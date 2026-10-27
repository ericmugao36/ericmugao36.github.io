document.addEventListener("DOMContentLoaded", function () {
  const showcase = document.getElementById("portfolio-showcase");
  if (!showcase) {
    console.error("Portfolio showcase was not found.");
    return;
  }

  const label = document.getElementById("showcase-label");
  const title = document.getElementById("showcase-title");
  const description = document.getElementById("showcase-description");
  const symbol = document.getElementById("showcase-symbol");
  const secondary = document.getElementById("showcase-secondary");

  const previous = document.getElementById("showcase-prev");
  const next = document.getElementById("showcase-next");
  const primary = document.getElementById("showcase-primary");
  if (!label || !title || !description || !symbol ||     !primary || !secondary || !previous || !next) {   console.error("A portfolio showcase element is missing.");   return; }


const projectsData = [
  {
    id: "edutrack",
    name: "EduTrack Kenya â€” School Management Dashboard",
    icon: "",
    label: "EDUTRACK KENYA Â· SCHOOL TECHNOLOGY",
    title: "Every parent deserves to understand their child's progress.",
    description: "EduTrack Kenya helps teachers record assessment results and gives parents access to their children's reports and teachers' comments, making learning progress easier to follow.",
    cardDescription: "Helps schools record learner assessment results and gives parents access to reports and teachers' comments.",
    projectLink: "#project-edutrack",
    technologies: ["Python", "FastAPI", "SQLAlchemy", "SQLite", "PostgreSQL"],
    repository: "https://github.com/ericmugao36/jss-assessment-dashboard",
    demo: "https://jss-assessment-dashboard.onrender.com",
    screenshot: "https://raw.githubusercontent.com/ericmugao36/ericmugao36.github.io/main/images/image.png"
  },
  {
    id: "smp",
    name: "SMP Performance Coach",
    icon: "",
    label: "SMP PERFORMANCE COACH Â· MACHINE LEARNING",
    title: "Turn activity data into useful predictions.",
    description: "SMP Performance Coach is a Python machine-learning practice project exploring whether daily activity data can help predict achievement of a 10,000-step goal.",
    cardDescription: "A machine-learning practice project that explores step-goal predictions.",
    projectLink: "#project-smp",
    technologies: ["Python", "Pandas", "Scikit-learn"],
    repository: "",
    demo: "",
    screenshot: ""
  },
  {
    id: "tools",
    name: "Python Business Tools",
    icon: "",
    label: "PYTHON BUSINESS TOOLS Â· AUTOMATION",
    title: "Make everyday tasks simpler with Python.",
    description: "Python Business Tools is a collection of small scripts, reusable functions, and calculators designed to simplify routine tasks and explore practical business automation.",
    cardDescription: "Small Python calculators and scripts for everyday tasks and business automation.",
    projectLink: "#project-tools",
    technologies: ["Python", "Automation"],
    repository: "",
    demo: "",
    screenshot: ""
  }
];

  function renderProjectCards() {
  const container = document.getElementById("project-list");
  if (!container) return;

  container.innerHTML = projectsData.map(project => `
    <div class="project" data-project-id="${project.id}">
      <div class="project-icon">${project.icon}</div>
      <div class="project-info">
        <h3>${project.name}</h3>
        <p>${project.cardDescription}</p>
        ${project.screenshot ? `
  <div class="edutrack-screenshots">
    <img data-src="${project.screenshot}"
         alt="${project.name} screenshot"
         loading="lazy">
  </div>
` : ""}
        <div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:10px;font-size:12px;font-weight:750">
          ${project.repository ? `
            <a href="${project.repository}" target="_blank"
               rel="noopener noreferrer"
               style="color:var(--site-primary)">View Repository â†—</a>
          ` : ""}
          ${project.demo ? `
            <a href="${project.demo}" target="_blank"
               rel="noopener noreferrer"
               style="color:var(--site-primary)">Live Demo â†—</a>
          ` : ""}
          ${project.id === "edutrack" ? `
            <a href="mailto:ericmugao36@gmail.com?subject=EduTrack%20Kenya%20Demo%20Request"
               style="color:var(--site-primary)">Request a Demo â†—</a>
          ` : ""}
        </div>
      </div>
      <span class="open">â†—</span>
    </div>
  `).join("");

  container.querySelectorAll("[data-project-id]").forEach(card => {
    card.style.cursor = "pointer";
    card.addEventListener("click", event => {
      if (event.target.closest("a")) return;
      window.location.hash = "#project-" + card.dataset.projectId;
    });
  });
}

const slides = [
  {
    type: "about",
    label: "ABOUT ME Â· ERIC MUGAO",
    title: "I turn ideas into practical digital solutions.",
    description: "I am a Python programmer and AI enthusiast focused on building useful technology for real-world problems. My work includes school assessment systems, web applications, and automation tools designed to make everyday tasks easier.",
    symbol: "",
    linkText: "About Me",
    link: "#about"
  },
  ...projectsData.map(project => ({
  type: "project",
  id: project.id,
  label: project.label,
  title: project.title,
  description: project.description,
  symbol: "",
  linkText: "Explore " + project.name,
  link: project.projectLink,
  projectLink: project.projectLink
}))
  // Add future projects here.
  // Each project can appear in the slideshow automatically.
];


let current = 0;


  function showSlide(index) {
    current = (index + slides.length) % slides.length;
    const slide = slides[current];
showcase.classList.toggle("project-background", slide.type === "project");
showcase.dataset.slide = slide.id || "about";

    label.textContent = slide.label;
    title.textContent = slide.title;
    description.textContent = slide.description;

symbol.textContent = slide.symbol;

primary.href = slide.projectLink || "#projects";



primary.onclick = function (event) {
  event.preventDefault();

  const destination = slide.projectLink || slide.link || "#projects";
  window.location.hash = destination;
};

secondary.textContent = slide.linkText + " â†’";
secondary.href = slide.link;

  }


let rotationTimer;

function restartRotationTimer() {
  window.clearInterval(rotationTimer);

  rotationTimer = window.setInterval(function () {
    showSlide(current + 1);
  }, 7000);
}

previous.addEventListener("click", function () {
  showSlide(current - 1);
  restartRotationTimer();
});

next.addEventListener("click", function () {
  console.log("Next button clicked");
  showSlide(current + 1);
  restartRotationTimer();
});

renderProjectCards();
showSlide(0);
restartRotationTimer();

});

const app = document.getElementById('app');

document.querySelectorAll('.nav a').forEach(link => {
  link.addEventListener('click', () => {
    app?.classList.remove('mobile-open');
  });
});

const themeToggle=document.getElementById('themeToggle');const savedTheme=localStorage.getItem('eric-portfolio-theme');if(savedTheme==='dark'||savedTheme==='light'){document.documentElement.style.colorScheme=savedTheme}function updateThemeButton(){const dark=document.documentElement.style.colorScheme==='dark';themeToggle.textContent=dark?'â˜€ï¸':'ðŸŒ™';themeToggle.setAttribute('aria-label',dark?'Switch to light mode':'Switch to dark mode');themeToggle.setAttribute('aria-pressed',String(dark))}updateThemeButton();themeToggle.addEventListener('click',()=>{const dark=document.documentElement.style.colorScheme!=='dark';document.documentElement.style.colorScheme=dark?'dark':'light';localStorage.setItem('eric-portfolio-theme',dark?'dark':'light');updateThemeButton()});document.getElementById('year').textContent=new Date().getFullYear();
