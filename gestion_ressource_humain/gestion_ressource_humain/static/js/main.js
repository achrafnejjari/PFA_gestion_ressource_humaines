// Start navbar
document.addEventListener("DOMContentLoaded", function () {
  // Gestion des boutons login/signup
  const loginBtn = document.getElementById("loginBtn");
  const signupBtn = document.getElementById("signupBtn");

  if (loginBtn) {
    loginBtn.addEventListener("click", () => {
      window.location.href = "../login";
    });
  }

  if (signupBtn) {
    signupBtn.addEventListener("click", () => {
      window.location.href = "../signup";
    });
  }

  // Ajout de la classe active à la bonne nav-link
  const currentPath = window.location.pathname.replace(/\/$/, "");
  const navLinks = document.querySelectorAll(".navbar-nav .nav-link");

  navLinks.forEach((link) => {
    const linkPath = new URL(link.href).pathname.replace(/\/$/, "");
    if (linkPath.endsWith(currentPath)) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });
});

// start faq
document.addEventListener("DOMContentLoaded", function () {
  const questions = document.querySelectorAll(".faq-question");
  const answers = document.querySelectorAll(".faq-answer");

  questions.forEach((question) => {
    question.addEventListener("click", function () {
      const targetAnswerId = this.getAttribute("data-target");
      const targetAnswer = document.getElementById(targetAnswerId);
      const toggleIcon = this.querySelector(".faq-toggle");

      // Si la question est déjà active, on la désactive
      if (this.classList.contains("active")) {
        this.classList.remove("active");
        targetAnswer.classList.remove("active");
        toggleIcon.textContent = "+";
      } else {
        // Retirer la classe "active" de toutes les questions et réponses
        questions.forEach((q) => {
          q.classList.remove("active");
          q.querySelector(".faq-toggle").textContent = "+";
        });
        answers.forEach((a) => a.classList.remove("active"));

        // Activer la question et la réponse cliquée
        this.classList.add("active");
        targetAnswer.classList.add("active");
        toggleIcon.textContent = "-";
      }
    });
  });
});
