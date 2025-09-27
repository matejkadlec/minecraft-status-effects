/*--------------------------*
 * Table sorting functionality *
 *--------------------------*/
(function (MCSE) {
  // Default sort order: [[columnIndex, direction], ...]
  // 0: Mod, 1: Effect, 2: Max, 3: Description, 4: Tags
  MCSE.sortState = [
    [0, "asc"], // Mod A-Z
    [1, "asc"], // Effect A-Z
    [4, "asc"], // Tags (positive first)
  ];

  /**
   * Initialize sorting - add click handlers to existing table headers
   */
  MCSE.initSorting = function initSorting() {
    const headers = document.querySelectorAll("#effects-table thead th");

    headers.forEach((header, index) => {
      // Make header clickable
      header.style.cursor = "pointer";
      header.style.userSelect = "none";

      // Add click handler to existing structure
      header.addEventListener("click", (e) => {
        e.preventDefault();
        if (e.shiftKey) {
          MCSE.handleShiftClick(index);
        } else {
          MCSE.handleClick(index);
        }
      });
    });

    // Enable sorting functionality and update arrow visibility
    document
      .querySelector("#effects-table thead")
      .classList.add("sorting-enabled");
    MCSE.updateSortArrows();
  };

  /**
   * Handle regular click - set this column as primary sort
   */
  MCSE.handleClick = function handleClick(columnIndex) {
    const existingSortIndex = MCSE.sortState.findIndex(
      ([col]) => col === columnIndex
    );
    let newDirection = "asc";

    if (existingSortIndex >= 0) {
      // This column is already in sort state - toggle direction
      newDirection =
        MCSE.sortState[existingSortIndex][1] === "asc" ? "desc" : "asc";
    }

    // Set this column as the only sort criteria
    MCSE.sortState = [[columnIndex, newDirection]];

    MCSE.applySorting();
  };

  /**
   * Handle shift+click - add/modify this column in sort order
   */
  MCSE.handleShiftClick = function handleShiftClick(columnIndex) {
    const existingIndex = MCSE.sortState.findIndex(
      ([col]) => col === columnIndex
    );

    if (existingIndex >= 0) {
      // Column already in sort state - toggle its direction
      const currentDirection = MCSE.sortState[existingIndex][1];
      const newDirection = currentDirection === "asc" ? "desc" : "asc";

      // Update direction in place (maintain priority order)
      MCSE.sortState[existingIndex][1] = newDirection;
    } else {
      // Column not in sort state - add to end with ascending order (lowest priority)
      MCSE.sortState.push([columnIndex, "asc"]);
    }

    MCSE.applySorting();
  };

  /**
   * Apply current sort state to the table
   */
  MCSE.applySorting = function applySorting() {
    // Store the current effects data before sorting
    const currentEffects = [...MCSE.effects];

    // Sort the effects based on current sort state
    currentEffects.sort((a, b) => {
      for (const [columnIndex, direction] of MCSE.sortState) {
        const compareResult = MCSE.compareValues(a, b, columnIndex);
        if (compareResult !== 0) {
          return direction === "asc" ? compareResult : -compareResult;
        }
      }
      return 0;
    });

    // Re-render table with sorted data
    MCSE.renderTable(currentEffects);

    // Apply any active filters after sorting
    if (typeof MCSE.applyTypeFilters === "function") {
      MCSE.applyTypeFilters();
    }
    if (typeof MCSE.updateNoResults === "function") {
      MCSE.updateNoResults();
    }

    // Update arrow visibility
    MCSE.updateSortArrows();
  };

  /**
   * Compare two effect objects by column index
   */
  MCSE.compareValues = function compareValues(a, b, columnIndex) {
    let valA, valB;

    switch (columnIndex) {
      case 0: // Mod
        valA = MCSE.getModSortValue(a.mod);
        valB = MCSE.getModSortValue(b.mod);
        break;
      case 1: // Effect
        valA = (a.effect || "").toLowerCase();
        valB = (b.effect || "").toLowerCase();
        break;
      case 2: // Max Level
        valA = MCSE.parseMaxLevel(a.maxLevel);
        valB = MCSE.parseMaxLevel(b.maxLevel);
        break;
      case 3: // Description
        valA = (a.description || "").toLowerCase();
        valB = (b.description || "").toLowerCase();
        break;
      case 4: // Tags
        valA = MCSE.getTagsSortValue(a.tags);
        valB = MCSE.getTagsSortValue(b.tags);
        break;
      default:
        return 0;
    }

    if (valA < valB) return -1;
    if (valA > valB) return 1;
    return 0;
  };

  /**
   * Get sort value for mod name (prioritize Minecraft)
   */
  MCSE.getModSortValue = function getModSortValue(mod) {
    if (!mod) return "zzz"; // Empty mods go last
    if (mod === "Minecraft") return "_minecraft"; // Prioritize Minecraft
    return mod.toLowerCase();
  };

  /**
   * Parse max level for numeric sorting
   */
  MCSE.parseMaxLevel = function parseMaxLevel(maxLevel) {
    if (!maxLevel) return 0;
    if (typeof maxLevel === "number") return maxLevel;

    const romanNumerals = {
      I: 1,
      II: 2,
      III: 3,
      IV: 4,
      V: 5,
      VI: 6,
      VII: 7,
      VIII: 8,
      IX: 9,
      X: 10,
    };
    if (romanNumerals[maxLevel]) return romanNumerals[maxLevel];

    const parsed = parseInt(maxLevel, 10);
    return isNaN(parsed) ? 0 : parsed;
  };

  /**
   * Get sort value for tags (positive < negative)
   */
  MCSE.getTagsSortValue = function getTagsSortValue(tags) {
    if (!tags || !Array.isArray(tags)) return "zzz";

    // Check for positive/negative tags first
    if (tags.includes("positive")) return "aaa_positive";
    if (tags.includes("negative")) return "zzz_negative";

    // Fall back to alphabetical by first tag
    return tags.length > 0 ? tags[0].toLowerCase() : "zzz";
  };

  /**
   * Update visual state of sort arrows
   */
  MCSE.updateSortArrows = function updateSortArrows() {
    const headers = document.querySelectorAll("#effects-table thead th");

    headers.forEach((header, index) => {
      const upArrow = header.querySelector(".sort-up");
      const downArrow = header.querySelector(".sort-down");

      if (!upArrow || !downArrow) return;

      // Reset all arrows to inactive state
      upArrow.classList.remove("active");
      downArrow.classList.remove("active");

      // Find if this column is in the sort state
      const sortEntry = MCSE.sortState.find(([col]) => col === index);

      if (sortEntry) {
        const [, direction] = sortEntry;
        if (direction === "asc") {
          upArrow.classList.add("active");
        } else {
          downArrow.classList.add("active");
        }
      }
    });
  };
})(window.MCSE);
