# TODO - Minecraft Status Effects Website

This file tracks upcoming features and improvements for the Minecraft Status Effects website. These are written in JIRA ticket format for clear task definition and progress tracking. While working on task in this file, mark it as [WIP], after finishing the task completely, and geeting my confirmation after I test it, mark it as done with this emoji: ✅.

## Table Functionality & UI Improvements

### MSE-001: Multi-Column Sorting ✅
**Priority:** High  
**Labels:** table, sorting, ui  
**Story:** As a user, I want to sort the effects table by any column in ascending or descending order, with support for multi-column sorting using Shift+click, so I can organize data according to my needs.

**Acceptance Criteria:**
- Each column header becomes clickable and shows sort indicators (arrows)
- Single click toggles between asc/desc for that column
- Shift+click adds additional sort columns (e.g., sort by Mod, then by Effect name)
- Visual indicators show sort direction and order priority
- Sorting works with current pagination and filtering

**Implementation Notes:**
- Add sorting state management to track multiple sort criteria
- Implement stable sorting algorithm to maintain consistent results
- Add visual cues for sort direction and priority

---

### MSE-002: Horizontal Scrolling ✅
**Priority:** High  
**Labels:** table, ui  
**Story:** As a user, I want the table to support horizontal scrolling so I can see all columns including new one (Source) without truncated descriptions or generally anything breaking into two lines.

**Acceptance Criteria:**
- Horizontal scroll is only enabled and horizontal scrollbar only appears if the table doesn't fit onto the screen
    - With our current setting, the horizontal scroll and scrollbar shouldn't appear on FHD maximized browser window, since it fits without breaking text into 2 lines
    - But it should appear i.e. on 1680x1050 resolution, since that would break a lot of descriptions into 2 lines as of now, but after this implementation, the horizontal scroll and scrollbar should appear instead
- Table container allows horizontal scrolling when content exceeds viewport width
    - Important note: the scroll must be within the table, not within the whole page
- Headers remain aligned with data columns during horizontal scroll
- Don't care about responsiveness for now, but the table should be scrollable on phones in the future
    - The table size won't be much smaller on phones, that's also reason why we need to horizontal scroll
- Smooth scrolling experience across browsers

**Implementation Notes:**
- Increase "Descriptipn" character limit to 200.
- As mentioned, add new column "Source":
    - Add "source" to effects.json after "description", and make it empty string for every existing effect
    - Create new table column "Source", but keep it hidden for now and tell me how to un-hide it in chat and also write it somewhere in comment
    - If the column couldn't be hidden from the table for any reason, do not add it then, and only add the "source" key to effects.json
- Ensure proper header/body alignment during horizontal scroll
    - Must also work properly with sticky header, or generally vertical and horizontal scroll must work together perfectly, vertical scroll must not break the horizontal scroll and vice versa
- Test across different viewport sizes

---

### MSE-003: Theme-aware Export Functionality ✅
**Priority:** Medium  
**Labels:** export, data, ui  
**Story:** As a user, I want to export the effects table data as CSV, Excel, or JSON files so I can use the data in other applications or for offline reference.

**Acceptance Criteria:**
- Dropdown menu positioned at top-right of table area (opposite corner from search)
    - Will have background and text color theme-aware, same as the "page-length" dropdown
- Export options: CSV, Excel (.xlsx), JSON
- All export related files/folders will be in ./export/ folder that will be in root
- Export includes currently applied filters (quick filters, search)
- Next to the dropdown (left side) will be text "Ignore filters" with checkbox, default will be not checked
    - If checked, it will download everything, no matter the filters.
    - State of this checkbox will be cached using localStorage.
- We can have pre-generated files with all results to be ready to download instantly, but filtered result must be generated via Python and then downloaded, as we can't have pre-generated every filter scenario
    - If you think have pre-generated full results is worth it, make a Python script that creates those file
    - Store them into ./export/files/ or similar, including the JSON file, even though it will be the same as ./data/effect.json
- Use appropriate, modern Python libraries, ideally one that can handle both XLSX and CSV (maybe OpenPYXL)
- The XLSX/CSV files will be stylized in Python, theme-aware (**use hexes from theme.css**)
    - If user downloads while on light-mode (it's exactly like on the web table): 
        - Header will have blue background and header text will be white
        - Data rows will switch between white and light blue background and data text will be black
        - Bold text in Description will be bold in the file too, and will be colored blue
    - If user downloads while on dark-mode (it's exactly like on the web table):
        - Header will have gold background and header text will be dark grey
        - Data rows will switch between grey and darker grey background and data text will be white
        - Bold text in Description will be bold in the file too, and will be colored gold
- For both themes (again XLSX/CSV only): 
    - Column widths should be equal or slightly bigger than the fixed width set in table.css (description column has width 100%; that is ~914px on FHD)
    - Rows height should be a bit bigger than default, ut not as big as in the web table
    - Header text will be uppercase and bold, there will be 1px border between header cells, and 2px between header row and data
    - Also there will be 2px border on the right and bottom edge (so it's like outlined by the border)
    - Data rows will also have 1px border between them (note combining 1px border-bottom with 1px border-top will create 2px, which we don't want)
- I believe this styling shouldn't be a performance issue, but if it is, we can get rid of some styles
- Filename format: `status-effects-{timestamp}.{extension}`
    - This also applies to the pre-generated files (if we will have them), they will be saved as `status-effects.{extension}`, but timestamp will be added to them during export, so the final filename will be different
- Do not put everything into one .py file, unless it's really short and sepearting doesn't make sense, otherwise separate it into 2+ files

**Implementation Notes:**
- Create Python scripts for the export
- (optional) Create script that will pre-generate full results from ./data/effects.json
- Create download endpoint in Bottle server
- Add UI dropdown component matching current design theme
- Style XLSX/CSV output files matching current design them

---

### MSE-004: Help/Legend Modals
- Start by deleting everything about current legend (it's hidden now, but I want it gone)
    - That is whole div class="note table-note legend" id="legend", then these sups: "sup class="fn-ref" data-target="legend-3", and all other stuff in `index.html` tied to the legend/help. Then all CSS and JS tied to that as well, all mentions, everything.
- "?" icon buttons similar to the theme swapping icons
- 1st will be next to the description (to the right side) text in header of the table
- 2nd will be next to the source (to the right side) text in header of the table
- Button opens modal dialog that covers entire window with grey overlay
- Modal contains current legend content plus additional explanations
- Clicking overlay or "OK" button closes the modal
- Modal is keyboard accessible (ESC key closes, focus management)
- Repurpose existing hidden #legend content
- Create modal component with proper a11y attributes
- Add smooth open/close animations matching theme
- Ensure modal works on mobile devices

---

### MSE-005: Navigation Update ✅
- Disable "Vanilla" quick filter by default (currently enabled by default)
- Make navigation mods scrollable, instead of the whole navigation panel.
    - The breakpoint when the navigation becames scrollable is >15 mod names (including group names, more about that below), and that is >364px on FHD
    - There is a placeholder object of the mod nav block, which's height needs to be the exact height of the nav after it's loaded, that is exactly 363.98px on FHD
    - If you would find a way to make this height dynamical, in i.e. rem or combination of px and rem, that would keep it precise still, it would be awesome, but the nav height is based on several factors and oen of them is font-size of our specific font Monstserrat, and also by the design of how rem works, this would be hard to hit exactly the 363.98px, but again, its some kinda big flaw we currently have, so if you fix that in this task, it would be great
- Group left menu (navigation) mods by common name (i.e. "The Ather Mods", "Delight Mods"), and only show the group name until expanded
    - Logic is either simple like this:
        - mod name contains "Aether" -> goes into "The Ather Mods" group, mod name contains "Delight" -> goes into "Delight Mods" group
    - Or a bit more complex. i.e. Ars Noveau, Blood Magic, Iron Spells'n'Spellbooks and T.O Magic 'n Extras are all magic mods, so we will group them under "Magic Mods"
    - Same can apply for combat mods, boss/dungeons mods, new dimension mods, etc., but for now, only add these: "The Ather Mods", "Delight Mods, "Magic Mods"
- Alphabeticall order will apply to the mod names inside the group, same as for the 1st layer mod names
- Add arrow down symbol (same as we have for col orders) to the of the group name, aligned to the very right of the box inside which the group name is
    - Wll change to arrow up when expanded (classic expand/collapse switch)
    - Add short animation to it, slideDown, slideUp
- These groups will do the expand/collapse when clicked, it wont find first effect of first mod or anything like that
- Group naems will be same as 1st layer mod names, except that the color will be brighter on dark mode, and darker on light mode, to be visually telling that it is a group (lighter on dark and darker on light will make the groups a bit highlighted)
- Grouped mod names (shown when expanded) will have "font-size: 0.8rem" instead of 0.85rem and "text-align: right" (within the group)
- Other than that, they will behave exactly the same like 1st layer effects: hover, find 1st effect on click, greyed out when not in the filtered table
- Additionally, use group "Other" for mods with <3 effects, but ONLY if they are not in other group already, i.e. "My Nether's Delight" mod only adds 2 effects, but it will be under the "Delight Mods", because it contains the word "Delight", so to summarize; grouping by common thing > grouping by not enough effects.
- The whoule group expand/collapse add functionality will be basically better and fancier dropdown, with animation that pushes elements below down on expand, and up on collapse

---

### MSE-NEXT: 
- Search term in URL and saved in localStorage
- Clickable logo and Minecraft version at the bottom right
- Update index.html description, to something like: "{big} library of modded Minecraft status effects. {something about features usage maybe}"
- Responsiveness

---

### Possible Future Upgrades
- Add something like [show more]/[show less] or [expand]/[collapse] to 2-lines long description/source texts, so it's all rendered on single line initially
- Add "guide" on first visit OR add >>> gif as a table overlay when page is loaded, to hint user the table is horinzotally scrolalble

---

### MSE-00X: Automated Testing Suite
**Priority:** Medium  
**Labels:** testing, quality-assurance, ci-cd  
**Story:** As a developer, I want comprehensive automated tests so I can maintain code quality and prevent regressions.

**Test Categories to Implement:**
- **Data validation tests**: effects.json schema compliance, description length limits, tag validity
- **Frontend unit tests**: filtering logic, sorting algorithms, pagination calculations
- **Integration tests**: search functionality, theme switching, localStorage persistence
- **UI/UX tests**: modal accessibility, responsive design breakpoints
- **Performance tests**: large dataset rendering, scroll performance
- **Cross-browser compatibility tests**: theme switching, table functionality

**Acceptance Criteria:**
- Test suite runs in CI/CD pipeline
- Minimum 80% code coverage for critical functionality
- Tests prevent deployment of breaking changes
- Performance benchmarks for table operations
- Accessibility compliance testing

**Implementation Notes:**
- Choose testing framework (Jest, Mocha, or similar)
- Set up test data fixtures
- Integrate with existing GitHub Actions workflow
- Add pre-commit hooks for critical tests

