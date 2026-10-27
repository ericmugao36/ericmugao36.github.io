
document.addEventListener("DOMContentLoaded", () => {
  const selectors = [
    "main section",
    ".shop-card",
    ".project-card",
    ".skill-card",
    ".learning-card",
    ".contact-card",
    ".about-card",
    ".blog-card",
    "#published-blog-articles article",
    "#published-blog-articles > div"
  ];

  const selectorText = selectors.join(", ");
  const observedElements = new WeakSet();

  if (!("IntersectionObserver" in window)) {
    document.querySelectorAll(selectorText).forEach(element => {
      element.classList.add("is-visible");
    });
    return;
  }

  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.12,
    rootMargin: "0px 0px -35px 0px"
  });

  function observeRevealElements(root = document) {
    if (root.matches?.(selectorText)) {
      observeElement(root);
    }

    root.querySelectorAll?.(selectorText).forEach(observeElement);
  }

  function observeElement(element) {
    if (observedElements.has(element)) return;

    observedElements.add(element);
    element.classList.add("scroll-reveal");
    observer.observe(element);
  }

  observeRevealElements();

  // Detect blog articles and other content added after page load.
  const mutationObserver = new MutationObserver(mutations => {
    mutations.forEach(mutation => {
      mutation.addedNodes.forEach(node => {
        if (node.nodeType === Node.ELEMENT_NODE) {
          observeRevealElements(node);
        }
      });
    });
  });

  mutationObserver.observe(document.body, {
    childList: true,
    subtree: true
  });
});
