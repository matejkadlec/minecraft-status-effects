/*------------------------------*
 * Theme toggle & persistence  *
 *------------------------------*/
(function (MCSE) {
  MCSE.root = document.documentElement;
  MCSE.btnDark = document.getElementById("btn-dark");
  MCSE.btnLight = document.getElementById("btn-light");

  MCSE.applyTheme = function applyTheme(theme) {
    const isDark = theme === "dark";
    MCSE.root.classList.toggle("dark", isDark);
    MCSE.btnDark.classList.toggle("active", isDark);
    MCSE.btnLight.classList.toggle("active", !isDark);
    localStorage.setItem("mcse-theme", isDark ? "dark" : "light");
  };

  // Apply stored theme (defaults to light) without causing flicker
  const storedTheme =
    localStorage.getItem("mcse-theme") === "dark" ? "dark" : "light";
  MCSE.applyTheme(storedTheme);

  MCSE.btnLight?.addEventListener("click", () => MCSE.applyTheme("light"));
  MCSE.btnDark?.addEventListener("click", () => MCSE.applyTheme("dark"));
})(window.MCSE);
