#!/usr/bin/env python3
"""
Build SEO-friendly static blog pages from Markdown files in _posts/.

Expected post format:

---
title: "Article title"
date: 2026-10-23T00:03:00+03:00
description: "A short summary for search and social previews."
image: https://example.com/cover.jpg
---

Markdown article body...

The script:
- keeps each Markdown file as the source of truth;
- creates /articles/<markdown-filename-without-extension>.html;
- inserts a server-rendered article list into blog.html between markers;
- adds generated article URLs to sitemap.xml;
- preserves existing blog.html content outside the generated region.

Dependencies:
    python -m pip install PyYAML Markdown bleach

Run from the repository root:
    python generate_blog.py
"""

from __future__ import annotations

import argparse
import html
import json
import logging
import os
import re
import tempfile
import unicodedata
import xml.etree.ElementTree as ET

from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import bleach
import markdown
import yaml


LOGGER = logging.getLogger("blog-generator")

SITE_NAME = "Eric Mugao"
SITE_URL = "https://ericmugao.co.ke"
BLOG_TITLE = "Never Stop Wondering"
BLOG_TAGLINE = "Culture -- Politics -- Technology -- Curiosity."
BLOG_DESCRIPTION = (
    "Essays and reflections on culture, politics, technology, humanity, "
    "and the questions that keep us curious."
)

POSTS_DIRECTORY = "_posts"
ARTICLES_DIRECTORY = "articles"
BLOG_FILE = "blog.html"
SITEMAP_FILE = "sitemap.xml"

BLOG_START_MARKER = "<!-- BLOG_POSTS_START -->"
BLOG_END_MARKER = "<!-- BLOG_POSTS_END -->"
LEGACY_LOADER_START = "let blogLibrariesPromise = null;"
LEGACY_LOADER_END = "loadPublishedBlogArticles();"

CHARCHA_EMBED_URL = (
    "https://charcha-comments.ericmugao36.workers.dev/embed.js"
)

# Markdown is converted to HTML and then sanitized. This list allows normal
# article formatting while preventing scripts, event handlers, and unsafe URLs.
ALLOWED_TAGS = set(bleach.sanitizer.ALLOWED_TAGS).union(
    {
        "p", "h1", "h2", "h3", "h4", "h5", "h6",
        "blockquote", "pre", "code", "hr", "br",
        "ul", "ol", "li", "table", "thead", "tbody",
        "tr", "th", "td", "del", "sup", "sub",
        "figure", "figcaption", "img", "div", "span",
    }
)
ALLOWED_ATTRIBUTES = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    "a": ["href", "title", "rel"],
    "img": ["src", "alt", "title"],
    "code": ["class"],
    "div": ["class"],
    "span": ["class"],
    "h1": ["id"], "h2": ["id"], "h3": ["id"],
    "h4": ["id"], "h5": ["id"], "h6": ["id"],
    "th": ["align"],
    "td": ["align"],
}
ALLOWED_PROTOCOLS = {"http", "https", "mailto"}


@dataclass(frozen=True)
class Post:
    slug: str
    title: str
    published: datetime
    description: str
    image: str
    body_html: str
    source_path: Path

    @property
    def published_iso(self) -> str:
        return self.published.isoformat()

    @property
    def published_date(self) -> str:
        return self.published.strftime("%B %d, %Y").replace(" 0", " ")

    @property
    def canonical_url(self) -> str:
        return f"{SITE_URL}/{ARTICLES_DIRECTORY}/{self.slug}.html"


def atomic_write(path: Path, content: str) -> None:
    """Write a UTF-8 file safely, avoiding half-written output."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
        text=True,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


def split_front_matter(raw_text: str, source: Path) -> tuple[dict[str, Any], str]:
    """Read YAML front matter delimited by the first pair of --- lines."""
    normalized = raw_text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.startswith("---\n"):
        raise ValueError(f"{source}: missing YAML front matter opening '---'.")

    closing_match = re.search(r"(?m)^---\s*$", normalized[4:])
    if not closing_match:
        raise ValueError(f"{source}: missing YAML front matter closing '---'.")

    closing_start = 4 + closing_match.start()
    closing_end = 4 + closing_match.end()
    metadata_text = normalized[4:closing_start].strip()
    body = normalized[closing_end:].lstrip("\n")

    try:
        metadata = yaml.safe_load(metadata_text) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"{source}: invalid YAML front matter: {exc}") from exc

    if not isinstance(metadata, dict):
        raise ValueError(f"{source}: front matter must be a YAML mapping.")

    return metadata, body


def parse_date(value: Any, source: Path) -> datetime:
    """Accept YAML dates/datetimes and common ISO date strings."""
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, date):
        parsed = datetime.combine(value, datetime.min.time())
    elif isinstance(value, str):
        candidate = value.strip()
        if not candidate:
            raise ValueError(f"{source}: 'date' cannot be empty.")
        try:
            parsed = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
        except ValueError:
            try:
                parsed = datetime.strptime(candidate, "%Y-%m-%d")
            except ValueError as exc:
                raise ValueError(
                    f"{source}: date must be YYYY-MM-DD or an ISO date/time."
                ) from exc
    else:
        raise ValueError(f"{source}: missing or invalid 'date' in front matter.")

    # Naive dates are interpreted in the site's local publishing timezone.
    # Existing article dates with +03:00 retain their original offset.
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def clean_metadata_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        raise ValueError("Metadata fields such as title/description must be text.")
    return re.sub(r"\s+", " ", str(value)).strip()


def normalize_image(value: Any, source: Path) -> str:
    image = clean_metadata_text(value)
    if not image:
        return ""

    # Reject data:, javascript:, file:, and other non-web schemes.
    parsed = urlparse(image)
    if parsed.scheme not in {"http", "https"}:
        # A relative image path is allowed and will be resolved from the site root.
        if image.startswith("//"):
            return "https:" + image
        if image.startswith(("/", "./", "../")):
            return image
        raise ValueError(
            f"{source}: image must be an http(s) URL or a site-relative path."
        )
    return image


def render_markdown(body: str) -> str:
    converter = markdown.Markdown(
        extensions=[
            "extra",
            "toc",
            "sane_lists",
            "smarty",
        ],
        output_format="html5",
    )
    rendered = converter.convert(body)
    return bleach.clean(
        rendered,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )


def load_post(path: Path) -> Post:
    raw_text = path.read_text(encoding="utf-8-sig")
    metadata, body = split_front_matter(raw_text, path)

    title = clean_metadata_text(metadata.get("title"))
    if not title:
        raise ValueError(f"{path}: missing required 'title' in front matter.")

    published = parse_date(metadata.get("date"), path)
    description = clean_metadata_text(metadata.get("description"))
    if not description:
        # A useful fallback for posts that do not yet have a description.
        plain_body = re.sub(r"[#>*_`\\[\\]()!~-]", " ", body)
        description = clean_metadata_text(plain_body)[:220]

    image = normalize_image(
        metadata.get("image") or metadata.get("cover_image"), path
    )

    # Convert the source filename into a URL-safe slug. This keeps existing
    # ASCII filenames unchanged while handling curly apostrophes, accented
    # characters, spaces, and other punctuation safely.
    original_stem = path.stem
    normalized_stem = unicodedata.normalize("NFKD", original_stem)
    ascii_stem = normalized_stem.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", ascii_stem)
    slug = re.sub(r"-+", "-", slug).strip("._-")

    if not slug or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", slug):
        raise ValueError(
            f"{path}: filename cannot be converted into a safe URL slug."
        )

    body_html = render_markdown(body)
    if not body_html.strip():
        raise ValueError(f"{path}: article body is empty.")

    return Post(
        slug=slug,
        title=title,
        published=published,
        description=description,
        image=image,
        body_html=body_html,
        source_path=path,
    )


def meta_description(description: str, limit: int = 160) -> str:
    compact = clean_metadata_text(description)
    if len(compact) <= limit:
        return compact

    shortened = compact[: limit - 1].rsplit(" ", 1)[0].rstrip(" ,;:-")
    if len(shortened) < 90:
        shortened = compact[: limit - 1].rstrip()
    return shortened + "…"


def json_for_script(value: Any) -> str:
    """JSON safe for embedding inside a script element."""
    return (
        json.dumps(value, ensure_ascii=False)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )


def render_blog_card(post: Post) -> str:
    title = html.escape(post.title)
    description = html.escape(meta_description(post.description, 220))
    date_label = html.escape(post.published_date)
    href = f"/{ARTICLES_DIRECTORY}/{post.slug}.html"

    image_html = ""
    if post.image:
        image_url = html.escape(post.image, quote=True)
        image_html = (
            f'<img class="blog-card-image" src="{image_url}" '
            f'alt="{title}" loading="lazy" decoding="async">'
        )

    return f"""
    <article class="milestone blog-card">
      <div class="milestone-mark" aria-hidden="true">✍</div>
      <div class="blog-card-content">
        {image_html}
        <h3><a href="{href}">{title}</a></h3>
        <p class="cv-note"><time datetime="{html.escape(post.published_iso, quote=True)}">{date_label}</time></p>
        <p>{description}</p>
        <p><a class="blog-read-more" href="{href}" aria-label="Read {title}">Read article →</a></p>
      </div>
    </article>""".strip()


def render_legacy_redirect(posts: list[Post]) -> str:
    routes = {post.slug: f"/{ARTICLES_DIRECTORY}/{post.slug}.html" for post in posts}
    routes_json = json_for_script(routes)
    return f"""
<script>
  // Keep old blog.html?post=... links working after static article pages are created.
  (() => {{
    const routes = {routes_json};
    const requestedPost = new URLSearchParams(window.location.search).get("post");
    if (requestedPost && routes[requestedPost]) {{
      window.location.replace(routes[requestedPost]);
    }}
  }})();
</script>""".strip()


def update_blog_index(blog_path: Path, posts: list[Post]) -> None:
    if not blog_path.exists():
        raise FileNotFoundError(f"Could not find {blog_path}.")

    current = blog_path.read_text(encoding="utf-8")
    if current.count(BLOG_START_MARKER) != 1 or current.count(BLOG_END_MARKER) != 1:
        raise ValueError(
            f"{blog_path} must contain exactly one BLOG_POSTS_START and "
            "one BLOG_POSTS_END marker."
        )

    start = current.index(BLOG_START_MARKER) + len(BLOG_START_MARKER)
    end = current.index(BLOG_END_MARKER)
    if end < start:
        raise ValueError(f"{blog_path}: blog post markers are in the wrong order.")

    cards = "\n\n".join(render_blog_card(post) for post in posts)
    if not cards:
        cards = '<p class="cv-note">No published articles yet.</p>'

    generated_region = (
        "\n\n"
        + cards
        + "\n\n"
        + render_legacy_redirect(posts)
        + "\n\n"
    )
    updated = current[:start] + generated_region + current[end:]

    # The old client-side loader fetches Markdown from GitHub and replaces this
    # server-rendered list. Remove that loader so the static HTML remains visible
    # to search engines and does not get overwritten after page load.
    if LEGACY_LOADER_START in updated:
        loader_start = updated.index(LEGACY_LOADER_START)
        loader_end_start = updated.find(LEGACY_LOADER_END, loader_start)
        if loader_end_start == -1:
            raise ValueError(
                f"{blog_path}: found the legacy blog loader start but not its end. "
                "Please review the inline blog JavaScript before generating."
            )
        loader_end = loader_end_start + len(LEGACY_LOADER_END)
        updated = (
            updated[:loader_start]
            + "// Article cards are generated as static HTML by generate_blog.py.\n"
            + updated[loader_end:]
        )
        LOGGER.info("Disabled the old client-side article loader in %s", blog_path)

    if updated != current:
        atomic_write(blog_path, updated)
        LOGGER.info("Updated server-rendered article list in %s", blog_path)
    else:
        LOGGER.info("Article list in %s is already up to date", blog_path)


def article_navigation() -> str:
    links = [
        ("index.html", "🏠", "Home"),
        ("projects.html", "💻", "Projects"),
        ("about.html", "👤", "About me"),
        ("skills.html", "🛠️", "Skills"),
        ("cv.html", "🛍️", "Shop"),
        ("learning.html", "🎨", "Graphic Design"),
        ("blog.html", "✍️", "Blog"),
        ("contact.html", "📞", "Contact"),
    ]
    rendered = []
    for href, icon, label in links:
        active = ' class="active"' if href == "blog.html" else ""
        rendered.append(
            f'<a{active} href="../{href}"><span class="ico">{icon}</span>'
            f'<span class="nav-label">{label}</span></a>'
        )
    return "\n".join(rendered)


def render_article_page(post: Post) -> str:
    title = html.escape(post.title)
    description = html.escape(meta_description(post.description), quote=True)
    canonical = html.escape(post.canonical_url, quote=True)
    published_iso = html.escape(post.published_iso, quote=True)
    published_label = html.escape(post.published_date)
    image_meta = (
        f'<meta property="og:image" content="{html.escape(post.image, quote=True)}">\n'
        if post.image else ""
    )
    image_html = ""
    if post.image:
        article_image = post.image
        if not urlparse(article_image).scheme and not article_image.startswith("/"):
            article_image = "../" + article_image.removeprefix("./")
        image_html = (
            f'<img class="article-featured-image" '
            f'src="{html.escape(article_image, quote=True)}" '
            f'alt="{title}" fetchpriority="high">'
        )

    social_image = post.image
    if social_image:
        if not urlparse(social_image).scheme:
            if social_image.startswith("/"):
                social_image = SITE_URL + social_image
            else:
                social_image = SITE_URL + "/" + social_image.removeprefix("./")

    article_schema = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post.title,
        "description": meta_description(post.description),
        "datePublished": post.published_iso,
        "dateModified": post.published_iso,
        "mainEntityOfPage": post.canonical_url,
        "author": {
            "@type": "Person",
            "name": SITE_NAME,
            "url": SITE_URL,
        },
        "publisher": {
            "@type": "Person",
            "name": SITE_NAME,
        },
    }
    if social_image:
        article_schema["image"] = [social_image]

    schema_json = json_for_script(article_schema)
    navigation = article_navigation()

    return f"""<!doctype html>
<!-- GENERATED_BY_GENERATE_BLOG_PY -->
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} | {SITE_NAME}</title>
  <meta name="description" content="{description}">
  <meta name="author" content="{SITE_NAME}">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <link rel="canonical" href="{canonical}">
  <link rel="stylesheet" href="../styles.css">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical}">
  {image_meta.rstrip()}
  <meta property="article:published_time" content="{published_iso}">
  <meta name="twitter:card" content="{'summary_large_image' if post.image else 'summary'}">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{description}">
  <script type="application/ld+json">{schema_json}</script>
  <style>
    .article-panel {{ max-width: 920px; }}
    .article-heading {{ margin: 8px 0 12px; line-height: 1.2; overflow-wrap: anywhere; }}
    .article-meta {{ margin: 0 0 22px; }}
    .article-featured-image {{
      display: block; width: 100%; max-height: 460px; object-fit: cover;
      border-radius: 12px; margin: 0 0 28px;
    }}
    .blog-article-body {{ line-height: 1.8; overflow-wrap: anywhere; }}
    .blog-article-body h2, .blog-article-body h3, .blog-article-body h4 {{
      line-height: 1.35; margin-top: 1.8em;
    }}
    .blog-article-body p {{ margin: 0 0 1.15em; }}
    .blog-article-body ul, .blog-article-body ol {{ padding-left: 1.5em; }}
    .blog-article-body blockquote {{
      margin: 1.5em 0; padding: 0.2em 1em;
      border-left: 3px solid var(--site-primary);
      opacity: .9;
    }}
    .blog-article-body pre {{
      overflow-x: auto; padding: 1em; border-radius: 10px;
      background: var(--site-panel, rgba(127,127,127,.10));
    }}
    .blog-article-body code {{ overflow-wrap: anywhere; }}
    .blog-article-body table {{ display: block; max-width: 100%; overflow-x: auto; }}
    .blog-article-body img {{ max-width: 100%; height: auto; border-radius: 10px; }}
    .article-back-link {{ display: inline-block; margin-bottom: 18px; }}
    .article-comments {{ margin-top: 42px; }}
    @media (max-width: 640px) {{
      .article-panel {{ padding: 18px; }}
      .article-heading {{ font-size: clamp(1.7rem, 8vw, 2.4rem); }}
    }}
  </style>
</head>
<body>
<div class="app" id="app">
  <aside class="sidebar" aria-label="Main navigation">
    <a class="brand" href="../index.html#dashboard" aria-label="{SITE_NAME} home">
      <img class="brand-mark"
           src="https://raw.githubusercontent.com/ericmugao36/ericmugao36.github.io/main/images/passport.jpg"
           alt="{SITE_NAME}">
      <div>
        <div class="brand-name">{SITE_NAME}</div>
        <div class="brand-sub">Communication - AI - Developer</div>
      </div>
    </a>
    <nav class="nav">
      {navigation}
    </nav>
    <div class="sidebar-bottom">Building a Block At a Time.</div>
  </aside>

  <main class="main" id="article">
    <header class="topbar">
      <div class="top-left">
        <button class="icon-btn theme-toggle" id="themeToggle"
                aria-label="Toggle theme" title="Toggle theme">🌙</button>
      </div>
    </header>

    <section class="section-head">
      <div>
        <div class="eyebrow">Blog article</div>
        <h1>{title}</h1>
        <p>Culture -- Politics -- Technology -- Curiosity.</p>
      </div>
    </section>

    <section class="panel article-panel">
      <a class="article-back-link" href="../blog.html">← Back to all articles</a>
      {image_html}
      <p class="cv-note article-meta">
        <time datetime="{published_iso}">{published_label}</time>
      </p>
      <article class="blog-article-body">
        {post.body_html}
      </article>
      <div class="article-comments">
        <h2>Join the conversation</h2>
        <div data-charcha data-thread="post-{html.escape(post.slug, quote=True)}"></div>
      </div>
      <p><a class="article-back-link" href="../blog.html">← Back to all articles</a></p>
    </section>

    <footer class="footer">
      <span>© <span id="year"></span> Yuri Solutions. All rights reserved.</span>
    </footer>
  </main>
</div>

<script>
  const themeToggle = document.getElementById('themeToggle');
  const savedTheme = localStorage.getItem('eric-portfolio-theme');

  if (savedTheme === 'dark' || savedTheme === 'light') {{
    document.documentElement.style.colorScheme = savedTheme;
  }}

  function updateThemeButton() {{
    const dark = document.documentElement.style.colorScheme === 'dark';
    themeToggle.textContent = dark ? '☀️' : '🌙';
    themeToggle.setAttribute('aria-label',
      dark ? 'Switch to light mode' : 'Switch to dark mode');
    themeToggle.setAttribute('aria-pressed', String(dark));
  }}

  updateThemeButton();

  themeToggle.addEventListener('click', () => {{
    const dark = document.documentElement.style.colorScheme !== 'dark';
    document.documentElement.style.colorScheme = dark ? 'dark' : 'light';
    localStorage.setItem('eric-portfolio-theme', dark ? 'dark' : 'light');
    updateThemeButton();
  }});

  document.getElementById('year').textContent = new Date().getFullYear();
</script>
<script src="{CHARCHA_EMBED_URL}" defer></script>
<script src="../scroll-reveal.js" defer></script>
</body>
</html>
"""


def update_sitemap(sitemap_path: Path, posts: list[Post]) -> None:
    if not sitemap_path.exists():
        LOGGER.warning("No sitemap.xml found; skipping sitemap update.")
        return

    try:
        tree = ET.parse(sitemap_path)
    except ET.ParseError as exc:
        raise ValueError(f"{sitemap_path} is not valid XML: {exc}") from exc

    root = tree.getroot()
    namespace_match = re.match(r"\{([^}]+)\}", root.tag)
    namespace = namespace_match.group(1) if namespace_match else ""
    ns = f"{{{namespace}}}" if namespace else ""
    loc_tag = f"{ns}loc"
    url_tag = f"{ns}url"

    existing_locations = {}
    for url_node in root.findall(url_tag):
        loc_node = url_node.find(loc_tag)
        if loc_node is not None and loc_node.text:
            existing_locations[loc_node.text.strip()] = url_node

    # Remove only URLs generated under this script's /articles/ path.
    article_prefix = f"{SITE_URL}/{ARTICLES_DIRECTORY}/"
    for location, node in list(existing_locations.items()):
        if location.startswith(article_prefix) and location.endswith(".html"):
            root.remove(node)

    for post in posts:
        url_node = ET.SubElement(root, url_tag)
        loc_node = ET.SubElement(url_node, loc_tag)
        loc_node.text = post.canonical_url

    ET.register_namespace("", namespace) if namespace else None
    xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    xml_text = xml_bytes.decode("utf-8") + "\n"
    atomic_write(sitemap_path, xml_text)
    LOGGER.info("Updated %s with %d article URLs", sitemap_path, len(posts))


def build(root: Path) -> int:
    posts_dir = root / POSTS_DIRECTORY
    blog_path = root / BLOG_FILE
    sitemap_path = root / SITEMAP_FILE
    articles_dir = root / ARTICLES_DIRECTORY

    if not posts_dir.is_dir():
        raise FileNotFoundError(f"Posts folder not found: {posts_dir}")

    markdown_files = sorted(
        (path for path in posts_dir.iterdir()
         if path.is_file() and path.suffix.lower() == ".md"),
        key=lambda path: path.name.lower(),
    )

    posts = [load_post(path) for path in markdown_files]
    posts.sort(key=lambda post: post.published, reverse=True)

    seen_slugs: set[str] = set()
    for post in posts:
        if post.slug in seen_slugs:
            raise ValueError(f"Duplicate article slug: {post.slug}")
        seen_slugs.add(post.slug)

    articles_dir.mkdir(parents=True, exist_ok=True)
    for post in posts:
        output_path = articles_dir / f"{post.slug}.html"
        atomic_write(output_path, render_article_page(post))
        LOGGER.info("Generated %s", output_path.relative_to(root))

    update_blog_index(blog_path, posts)
    update_sitemap(sitemap_path, posts)

    LOGGER.info("Build complete: %d Markdown article(s) processed.", len(posts))
    return len(posts)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate SEO-friendly static HTML pages from Markdown blog posts."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Website repository root (defaults to this script's directory).",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show detailed build messages."
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    root = args.root.resolve()
    try:
        count = build(root)
    except Exception as exc:
        LOGGER.error("%s", exc)
        return 1

    print(f"Generated {count} article page(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
