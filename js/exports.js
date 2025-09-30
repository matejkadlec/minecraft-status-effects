/**
 * Export functionality for status effects table
 */

class ExportManager {
  constructor() {
    this.exportSelect = document.getElementById("export-format");
    this.ignoreFiltersCheckbox = document.getElementById("ignore-filters");

    this.init();
  }

  init() {
    // Load saved ignore filters preference
    const savedIgnoreFilters = localStorage.getItem("export-ignore-filters");
    if (savedIgnoreFilters !== null) {
      this.ignoreFiltersCheckbox.checked = JSON.parse(savedIgnoreFilters);
    }

    // Event listeners
    this.exportSelect.addEventListener("change", this.handleExport.bind(this));
    this.ignoreFiltersCheckbox.addEventListener(
      "change",
      this.saveIgnoreFiltersPreference.bind(this)
    );
  }

  saveIgnoreFiltersPreference() {
    localStorage.setItem(
      "export-ignore-filters",
      JSON.stringify(this.ignoreFiltersCheckbox.checked)
    );
  }

  async handleExport() {
    const format = this.exportSelect.value;
    if (!format) return;

    try {
      // Build export URL with current filters and theme
      const url = this.buildExportURL(format);

      // Create invisible download link and trigger it
      const link = document.createElement("a");
      link.href = url;
      link.style.display = "none";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Reset dropdown
      this.exportSelect.value = "";
    } catch (error) {
      console.error("Export failed:", error);
      alert("Export failed. Please try again.");
    }
  }

  buildExportURL(format) {
    const params = new URLSearchParams();

    // Add theme
    const currentTheme = document.documentElement.classList.contains("dark")
      ? "dark"
      : "light";
    params.set("theme", currentTheme);

    // Add ignore filters setting
    params.set("ignore_filters", this.ignoreFiltersCheckbox.checked.toString());

    // If not ignoring filters, add current filter state
    if (!this.ignoreFiltersCheckbox.checked) {
      // Search filter
      const searchValue = document.getElementById("search").value.trim();
      if (searchValue) {
        params.set("search", searchValue);
      }

      // Type filters - use correct IDs
      const positiveFilter = document.getElementById("filterPositive");
      const negativeFilter = document.getElementById("filterNegative");
      const scalingFilter = document.getElementById("filterScaling");
      const vanillaFilter = document.getElementById("filterVanilla");

      if (positiveFilter)
        params.set("positive", positiveFilter.checked.toString());
      if (negativeFilter)
        params.set("negative", negativeFilter.checked.toString());
      if (scalingFilter)
        params.set("scaling", scalingFilter.checked.toString());
      if (vanillaFilter)
        params.set("vanilla", vanillaFilter.checked.toString());
    }

    return `/export/${format}?${params.toString()}`;
  }
}

// Initialize export manager when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  window.exportManager = new ExportManager();
});
