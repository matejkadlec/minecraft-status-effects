/*------------------------------*
 * Theme toggle & persistence  *
 *------------------------------*/
(function (MCSE) {
  MCSE.root = document.documentElement;
  MCSE.btnDark = document.getElementById("btn-dark");
  MCSE.btnLight = document.getElementById("btn-light");

  MCSE.applyTheme = function applyTheme(theme) {
    if (theme === "dark") {
      MCSE.root.classList.add("dark");
      MCSE.btnDark.classList.add("active");
      MCSE.btnLight.classList.remove("active");
    } else {
      MCSE.root.classList.remove("dark");
      MCSE.btnLight.classList.add("active");
      MCSE.btnDark.classList.remove("active");
    }
    // Swap loading spinner asset if placeholder still visible
    const navSpinner = document.getElementById("nav-spinner");
    if (navSpinner) {
      navSpinner.src =
        theme === "dark" ? "img/loading-dark.gif" : "img/loading-light.gif";
    }
    // Table spinner uses CSS background; force repaint by toggling a data attr (optional safeguard)
    const tableScroll = document.querySelector(".table-scroll.loading");
    if (tableScroll) {
      tableScroll.setAttribute(
        "data-theme-spin",
        theme === "dark" ? "dark" : "light"
      );
    }
    localStorage.setItem("mcse-theme", theme);
  };

  const storedTheme = localStorage.getItem("mcse-theme");
  MCSE.applyTheme(storedTheme === "dark" ? "dark" : "light");

  MCSE.btnLight?.addEventListener("click", () => MCSE.applyTheme("light"));
  MCSE.btnDark?.addEventListener("click", () => MCSE.applyTheme("dark"));
})(window.MCSE);
