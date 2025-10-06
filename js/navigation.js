/*------------------------------*
 * Hash navigation & row focus *
 *------------------------------*/
(function (MCSE) {
  let suppressHashHighlight = false;

  window.addEventListener("hashchange", () => {
    if (suppressHashHighlight) return;
    MCSE.rows.forEach((r) => r.classList.remove("highlight"));
    const id = location.hash.slice(1);
    if (!id) return;
    const target = document.getElementById(id);
    if (!target) return;
    target.classList.remove("highlight");
    void target.offsetWidth;
    target.classList.add("highlight");
  });

  function scrollAndHighlight(targetRow) {
    function applyHighlight() {
      MCSE.rows.forEach((r) => r.classList.remove("highlight"));
      targetRow.classList.remove("highlight");
      void targetRow.offsetWidth;
      targetRow.classList.add("highlight");
    }

    const scrollWrap = document.querySelector(".table-scroll");
    if (scrollWrap) {
      scrollWrap.scrollLeft = 0;

      const header = scrollWrap.querySelector("thead th");
      const headerHeight = header ? header.getBoundingClientRect().height : 0;
      const targetOffset = targetRow.offsetTop;
      let desired = targetOffset - headerHeight;
      if (targetOffset === 0) desired = 0;
      const maxScroll = scrollWrap.scrollHeight - scrollWrap.clientHeight;
      if (desired < 0) desired = 0;
      if (desired > maxScroll) desired = maxScroll;

      const start = performance.now();
      const duration = 600;
      const delta = Math.abs(scrollWrap.scrollTop - desired);

      if (delta < 2) {
        setTimeout(() => {
          applyHighlight();
          suppressHashHighlight = false;
        }, 70);
        return;
      }

      scrollWrap.scrollTo({ top: desired, behavior: "smooth" });
      let done = false;
      const check = () => {
        const diff = Math.abs(scrollWrap.scrollTop - desired);
        const elapsed = performance.now() - start;
        if (diff < 2 || elapsed > duration + 150) {
          if (!done) {
            done = true;
            setTimeout(() => {
              applyHighlight();
              suppressHashHighlight = false;
            }, 70);
          }
          return;
        }
        requestAnimationFrame(check);
      };
      requestAnimationFrame(check);
    } else {
      targetRow.scrollIntoView({ behavior: "smooth", block: "start" });
      setTimeout(() => {
        applyHighlight();
        suppressHashHighlight = false;
      }, 650);
    }
  }

  MCSE.openNavGroups = MCSE.openNavGroups || new Set();
  const pendingAutoScrollTimers = new WeakMap();

  MCSE.buildNav = function buildNav() {
    const navList = MCSE.navList;
    if (!navList) return;

    const previousScrollTop = navList.scrollTop;

    // Get all unique mods from all rows (always show all mods)
    const allMods = [];
    const seenMods = new Set();

    MCSE.rows.forEach((r) => {
      if (r.id === "no-results-row") return;
      const mod = r.getAttribute("data-mod");
      if (!mod || seenMods.has(mod)) return;
      seenMods.add(mod);
      allMods.push({ mod, id: r.id });
    });

    // Get currently visible mods (considering filters and search)
    const visibleRows = MCSE.rows.filter((r) => {
      if (r.id === "no-results-row") return false;
      if (r.hasAttribute("data-hidden-search")) return false;
      return r.dataset.baseDisplay !== "none";
    });

    const availableMods = new Set();
    visibleRows.forEach((r) => {
      const mod = r.getAttribute("data-mod");
      if (mod) availableMods.add(mod);
    });

    // Count effects per mod
    const modEffectCounts = {};
    MCSE.rows.forEach((r) => {
      if (r.id === "no-results-row") return;
      const mod = r.getAttribute("data-mod");
      if (mod) {
        modEffectCounts[mod] = (modEffectCounts[mod] || 0) + 1;
      }
    });

    // Grouping logic
    const MOD_GROUPS = {
      "The Aether Mods": (mod) => mod.toLowerCase().includes("aether"),
      "Delight Mods": (mod) => mod.toLowerCase().includes("delight"),
      "Magic Mods": (mod) =>
        [
          "Ars Nouveau",
          "Blood Magic",
          "Iron Spells'n'Spellbooks",
          "T.O Magic 'n Extras",
        ].includes(mod),
    };

    function getModGroup(mod) {
      // Check named groups first
      for (const [groupName, matcher] of Object.entries(MOD_GROUPS)) {
        if (matcher(mod)) return groupName;
      }
      // "Other" group for mods with <3 effects (only if not in another group)
      if (modEffectCounts[mod] < 3) return "Other";
      return null; // Not in any group
    }

    // Organize mods into groups
    const grouped = {};
    const ungrouped = [];

    allMods.forEach(({ mod, id }) => {
      const group = getModGroup(mod);
      if (group) {
        if (!grouped[group]) grouped[group] = [];
        grouped[group].push({ mod, id });
      } else {
        ungrouped.push({ mod, id });
      }
    });

    // Helper function to determine mod order (Minecraft first, then alphabetical)
    const shouldComeBefore = (modA, modB) => {
      if (modA === "Minecraft" && modB !== "Minecraft") return true;
      if (modA !== "Minecraft" && modB === "Minecraft") return false;
      return modA < modB;
    };

    // Sort items within each group
    Object.keys(grouped).forEach((groupName) => {
      grouped[groupName].sort((a, b) =>
        shouldComeBefore(a.mod, b.mod) ? -1 : 1
      );
    });

    // Sort ungrouped mods
    ungrouped.sort((a, b) => (shouldComeBefore(a.mod, b.mod) ? -1 : 1));

    // Combine into final list: ungrouped first, then groups (alphabetically, but "Other" always last)
    const groupNames = Object.keys(grouped).sort((a, b) => {
      if (a === "Other") return 1;
      if (b === "Other") return -1;
      return a < b ? -1 : 1;
    });

    navList.innerHTML = "";

    function findFirstVisibleId(mod, fallbackId) {
      if (!availableMods.has(mod)) return fallbackId;
      const firstVisibleEffect = visibleRows.find(
        (r) => r.getAttribute("data-mod") === mod
      );
      return firstVisibleEffect ? firstVisibleEffect.id : fallbackId;
    }

    function decorateChildAnimations(container) {
      const links = Array.from(container.querySelectorAll("a"));
      container.style.setProperty("--child-count", links.length);
      links.forEach((link, index) => {
        link.style.setProperty("--child-index", index);
      });
    }

    function animateHeight(element, start, end, duration) {
      element.style.height = `${start}px`;
      element.style.overflow = "hidden";
      element.style.display = "block";
      requestAnimationFrame(() => {
        element.style.height = `${end}px`;
      });
      setTimeout(() => {
        element.style.height = "";
        element.style.overflow = "";
        if (end === 0) element.style.display = "";
      }, duration);
    }

    function easeInOutQuad(x) {
      return x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2;
    }

    function smoothScroll(container, target, duration) {
      const start = container.scrollTop;
      const diff = target - start;
      if (Math.abs(diff) < 1) return;
      let startTime = null;
      function step(timestamp) {
        if (!startTime) startTime = timestamp;
        const elapsed = timestamp - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = easeInOutQuad(progress);
        container.scrollTop = start + diff * eased;
        if (elapsed < duration) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    }

    function autoScrollGroupIntoView(li, duration) {
      const nav = MCSE.navList;
      if (!nav) return;
      const navRect = nav.getBoundingClientRect();
      const groupRect = li.getBoundingClientRect();
      let targetScroll = nav.scrollTop;

      if (groupRect.bottom > navRect.bottom) {
        targetScroll += groupRect.bottom - navRect.bottom;
      }
      if (groupRect.top < navRect.top) {
        targetScroll += groupRect.top - navRect.top;
      }

      const maxScroll = nav.scrollHeight - nav.clientHeight;
      if (targetScroll > maxScroll) targetScroll = maxScroll;
      if (targetScroll < 0) targetScroll = 0;

      smoothScroll(nav, targetScroll, duration);
    }

    function scheduleAutoScroll(li, duration) {
      const existing = pendingAutoScrollTimers.get(li);
      if (existing) {
        existing.cancel();
        pendingAutoScrollTimers.delete(li);
      }

      const upperBound = Math.min(duration, 520);
      const increment = 60;
      const timeouts = [];
      const handle = {
        cancelled: false,
        cancel() {
          handle.cancelled = true;
          timeouts.forEach((t) => clearTimeout(t));
        },
      };

      for (let delay = 160; delay <= upperBound; delay += increment) {
        const isLast = delay + increment > upperBound;
        const id = setTimeout(() => {
          if (handle.cancelled) return;
          if (!li.isConnected) return;
          if (!li.classList.contains("expanded")) return;
          autoScrollGroupIntoView(li, duration);
          if (isLast) {
            pendingAutoScrollTimers.delete(li);
          }
        }, delay);
        timeouts.push(id);
      }

      pendingAutoScrollTimers.set(li, handle);
    }

    function toggleGroup(li, groupName) {
      const children = li.querySelector(".group-children");
      if (!children) return;
      if (li.classList.contains("animating")) return;

      const expanding = !li.classList.contains("expanded");
      const duration = 500;
      li.classList.add("animating");

      if (expanding) {
        li.classList.add("expanding");
        li.classList.add("expanded");
        MCSE.openNavGroups.add(groupName);
        animateHeight(children, 0, children.scrollHeight, duration);
        scheduleAutoScroll(li, duration);
      } else {
        const currentHeight = children.scrollHeight;
        li.classList.remove("expanded");
        li.classList.add("collapsing");
        animateHeight(children, currentHeight, 0, duration);
        MCSE.openNavGroups.delete(groupName);
        const existing = pendingAutoScrollTimers.get(li);
        if (existing) {
          existing.cancel();
          pendingAutoScrollTimers.delete(li);
        }
      }

      setTimeout(() => {
        li.classList.remove("animating", "expanding", "collapsing");
      }, duration);
    }

    // Add ungrouped mods
    ungrouped.forEach(({ mod, id }) => {
      const li = document.createElement("li");
      const isAvailable = availableMods.has(mod);
      const targetId = findFirstVisibleId(mod, id);

      li.innerHTML = `<a href="#${targetId}" data-mod="${mod}" data-available="${isAvailable}">${mod}</a>`;
      navList.appendChild(li);
    });

    // Add grouped mods
    groupNames.forEach((groupName) => {
      const mods = grouped[groupName];
      const li = document.createElement("li");
      li.className = "mod-group";
      li.dataset.groupName = groupName;

      const groupHasAvailable = mods.some(({ mod }) => availableMods.has(mod));

      const header = document.createElement("div");
      header.className = "group-header";
      header.innerHTML = `<span class="group-arrow">▼</span><span class="group-name">${groupName}</span>`;
      header.setAttribute("data-available", groupHasAvailable);

      const children = document.createElement("div");
      children.className = "group-children";

      mods.forEach(({ mod, id }) => {
        const isAvailable = availableMods.has(mod);
        const targetId = findFirstVisibleId(mod, id);

        const link = document.createElement("a");
        link.href = `#${targetId}`;
        link.setAttribute("data-mod", mod);
        link.setAttribute("data-available", isAvailable);
        link.textContent = mod;
        children.appendChild(link);
      });

      decorateChildAnimations(children);

      if (!groupHasAvailable) {
        li.classList.add("group-disabled");
        MCSE.openNavGroups.delete(groupName);
      } else if (MCSE.openNavGroups.has(groupName)) {
        li.classList.add("expanded");
      }

      li.appendChild(header);
      li.appendChild(children);
      navList.appendChild(li);

      header.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (!groupHasAvailable) return;
        toggleGroup(li, groupName);
      });
    });

    requestAnimationFrame(() => {
      const maxScroll = navList.scrollHeight - navList.clientHeight;
      if (maxScroll <= 0) {
        navList.scrollTop = 0;
      } else {
        const clamped = Math.min(previousScrollTop, maxScroll);
        navList.scrollTop = clamped < 0 ? 0 : clamped;
      }
    });
  };

  if (MCSE.navList) {
    MCSE.navList.addEventListener("click", (e) => {
      const link = e.target.closest("a[href^='#']");
      if (!link) return;
      e.preventDefault();

      // Check if the mod is available (has visible effects)
      const isAvailable = link.getAttribute("data-available") === "true";
      if (!isAvailable) {
        return; // Do nothing if mod is not available
      }

      const targetMod = link.getAttribute("data-mod");
      if (!targetMod) return;

      // Find first visible effect for this mod (considering filters and search)
      const targetRow = MCSE.rows.find((r) => {
        if (r.id === "no-results-row") return false;
        if (r.getAttribute("data-mod") !== targetMod) return false;
        // Check if row is hidden by search filter
        if (r.hasAttribute("data-hidden-search")) return false;
        // Check if row is hidden by type filters
        return r.dataset.baseDisplay !== "none";
      });

      if (!targetRow) return;

      // Update hash in URL
      const hash = `#${targetRow.id}`;
      suppressHashHighlight = true;
      if (history.pushState) history.pushState(null, "", hash);
      else location.hash = hash;

      // Find which page contains this row
      if (MCSE.updatePagination && targetRow.dataset.page) {
        const targetPage = parseInt(targetRow.dataset.page, 10);
        if (targetPage && targetPage !== MCSE.pagination.page) {
          // Switch to the correct page first
          MCSE.pagination.page = targetPage;
          MCSE.updatePagination();
          // Small delay to ensure DOM updates
          setTimeout(() => scrollAndHighlight(targetRow), 50);
          return;
        }
      }

      // Row is on current page, scroll immediately
      scrollAndHighlight(targetRow);
    });
  }
})(window.MCSE);

document.addEventListener("click", (e) => {
  const ref = e.target.closest(".fn-ref");
  if (!ref) return;
  const id = ref.getAttribute("data-target");
  if (!id) return;
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.remove("flash");
  void el.offsetWidth;
  el.classList.add("flash");
});
