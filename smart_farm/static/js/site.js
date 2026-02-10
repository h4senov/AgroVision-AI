// static/js/site.js
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    const navbar = document.querySelector("nav.navbar");
    if (!navbar) return;

    const navCollapse = navbar.querySelector(".navbar-collapse");
    const dropdowns = Array.from(navbar.querySelectorAll(".navbar-nav .dropdown"));
    const toggler = navbar.querySelector(".navbar-toggler");

    // -----------------------------
    // Helper: Bağla bütün dropdown-ları
    // -----------------------------
    function closeAllDropdowns() {
      dropdowns.forEach(d => {
        d.classList.remove("show");
        const menu = d.querySelector(".dropdown-menu");
        if (menu) menu.classList.remove("show");
        const toggle = d.querySelector(".dropdown-toggle");
        if (toggle) toggle.setAttribute("aria-expanded", "false");
      });
    }

    // -----------------------------
    // Dropdown-ları yalnız klikdə aç/qapa
    // -----------------------------
    dropdowns.forEach(dropdown => {
      const toggle = dropdown.querySelector(".dropdown-toggle");
      const menu = dropdown.querySelector(".dropdown-menu");

      if (!toggle || !menu) return;

      toggle.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();

        const isOpen = dropdown.classList.contains("show");

        // Digər dropdown-ları bağla
        closeAllDropdowns();

        // Yalnız klik ediləni aç
        if (!isOpen) {
          dropdown.classList.add("show");
          menu.classList.add("show");
          toggle.setAttribute("aria-expanded", "true");
        }
      });
    });

    // -----------------------------
    // Klik xaricdədirsə bağla
    // -----------------------------
    document.addEventListener("click", function (e) {
      if (!e.target.closest("nav.navbar")) {
        closeAllDropdowns();
        if (navCollapse) navCollapse.classList.remove("show");
      }
    });

    // -----------------------------
    // Burger klikində arxa fon
    // -----------------------------
    if (toggler && navCollapse) {
      toggler.addEventListener("click", function () {
        if (navCollapse.classList.contains("show")) {
          navCollapse.style.backgroundColor = "transparent";
        } else {
          navCollapse.style.backgroundColor = "#fff"; // Ağ fon
        }
      });
    }

    // -----------------------------
    // Escape düyməsi ilə dropdown və collapse bağla
    // -----------------------------
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" || e.key === "Esc") {
        closeAllDropdowns();
        if (navCollapse && navCollapse.classList.contains("show")) {
          navCollapse.classList.remove("show");
          navCollapse.style.backgroundColor = "transparent";
        }
      }
    });

    // -----------------------------
    // Mobil -> desktop resize
    // -----------------------------
    function handleResize() {
      if (window.innerWidth >= 993) {
        closeAllDropdowns();
        if (navCollapse) navCollapse.style.backgroundColor = "";
      }
    }
    window.addEventListener("resize", handleResize);
    handleResize();
  });
})();
