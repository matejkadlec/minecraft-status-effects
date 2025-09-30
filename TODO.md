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

### MSE-004: Help/Legend Modal
**Priority:** Medium  
**Labels:** ui, help, modal  
**Story:** As a user, I want to access explanatory information about the effects table through a help button so I understand what the data means and how to use the website.

**Acceptance Criteria:**
- "?" icon button positioned near searchbar or top-right of table
- Button opens modal dialog that covers entire window with grey overlay
- Modal contains current legend content plus additional explanations
- Clicking overlay or "OK" button closes the modal
- Modal is keyboard accessible (ESC key closes, focus management)

**Implementation Notes:**
- Repurpose existing hidden #legend content
- Create modal component with proper a11y attributes
- Add smooth open/close animations matching theme
- Ensure modal works on mobile devices

---

### MSE-005: Enhanced Tags and Filters
**Priority:** Medium  
**Labels:** tags, filters, categorization  
**Story:** As a user, I want more detailed categorization of effects through additional tags and filters so I can find specific types of effects more easily.

**New Tags to Add:**
- **DRAFT** - Effects lacking crucial information in descriptions
- **NEUTRAL** - Effects that can be positive or negative depending on situation
- **MOVEMENT** - Movement-impairing effects
- **COMBAT** - Combat-related effects  
- **SPELL** - Spell-related effects
- **WEAK/MEDIUM/STRONG** - Effect strength classification (or as separate column)

**Acceptance Criteria:**
- Update effects.json with new tag categories
- Add corresponding quick filter checkboxes to sidebar
- Filter state persists in localStorage
- All existing filters continue to work correctly
- Update validation script to recognize new tags

**Implementation Notes:**
- Decision needed: strength as tags vs. separate column
- Review all effects to assign appropriate new tags
- Update CSS for new badge styles if needed

---

### MSE-006: Missing Formula Warning Icon
**Priority:** Low  
**Labels:** ui, data-quality, tooltip  
**Story:** As a user, I want to know when effect formulas are incomplete so I understand data limitations.

**Acceptance Criteria:**
- Warning icon (⚠️) appears at end of description for effects with unknown formulas
- Cursor changes to help pointer on hover
- Tooltip shows "Exact formula is missing."
- Icon styling matches current design theme
- No impact on table layout or performance

**Implementation Notes:**
- Define criteria for "missing formula" (e.g., descriptions without `<b>` formula tags)
- Add icon during table rendering in render.js
- Implement lightweight tooltip functionality

---

### MSE-007: Wiki Scraping Tools
**Priority:** Low  
**Labels:** automation, scraping, data-collection  
**Story:** As a developer, I want automated tools to scrape Fandom wiki pages for effect information so I can efficiently collect data from multiple sources.

**Acceptance Criteria:**
- Python script to scrape Fandom wiki effects list pages
- Python script to scrape individual effect detail pages  
- Scripts handle common wiki template formats
- Error handling for network failures and parsing issues
- Output format compatible with existing effects.json structure

**Alternative Implementation:**
- Add informational text below intro: "Before you start browsing, read important info here" (with "here" as link to help modal)
- Emphasizes importance of understanding mod-pack dependent max levels and other caveats

**Implementation Notes:**
- Research common Fandom wiki structures across different mod wikis
- Implement respectful scraping with rate limiting
- Consider legal/ethical implications of automated scraping

---

### MSE-008: Automated Testing Suite
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
