// SAUVEGARDE / RESTAURATION SCROLL DE LA SIDEBAR
window.addEventListener("beforeunload", () => {
  const sidebar = document.getElementById("sidebar");
  if (sidebar) {
    localStorage.setItem("sidebarScroll", sidebar.scrollTop);
  }
});

window.addEventListener("load", () => {
  const sidebar = document.getElementById("sidebar");
  const saved = localStorage.getItem("sidebarScroll");
  if (sidebar && saved !== null) {
    sidebar.scrollTop = parseInt(saved);
  }
});

// METTRE LE LIEN ACTIF
window.addEventListener("DOMContentLoaded", () => {
  const links = document.querySelectorAll(".sidebar .nav-link");
  links.forEach((link) => {
    if (link.href === window.location.href) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });
});

// LOGIQUE DU REDIMENSIONNEMENT DE LA SIDEBAR
const sidebar = document.getElementById("sidebar");
const handle = document.getElementById("resizeHandle");

let isResizing = false;

if (handle) {
  handle.addEventListener("mousedown", (e) => {
    isResizing = true;
    document.body.style.cursor = "ew-resize";
    e.preventDefault();
  });

  document.addEventListener("mousemove", (e) => {
    if (!isResizing || !sidebar) return;

    let newWidth = e.clientX;
    if (newWidth < 100) {
      newWidth = 60;
      sidebar.classList.add("collapsed");
    } else {
      sidebar.classList.remove("collapsed");
    }

    if (newWidth > 400) newWidth = 400;
    sidebar.style.width = `${newWidth}px`;
  });

  document.addEventListener("mouseup", () => {
    isResizing = false;
    document.body.style.cursor = "default";
  });
}

// FONCTION POUR ACTIVER MANUELLEMENT UN LIEN
function setActive(el) {
  document
    .querySelectorAll(".sidebar .nav-link")
    .forEach((link) => link.classList.remove("active"));
  el.classList.add("active");
}
