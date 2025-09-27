# TODO - Minecraft Status Effects Website

This file tracks upcoming features and improvements for the Minecraft Status Effects website. These are written in JIRA ticket format for clear task definition and progress tracking. While working on task in this file, mark it as [WIP], after finishing the task completely, mark it as done with this emoji: ✅.

## Table Functionality & UI Improvements

### MSE-001: Multi-Column Sorting
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

### MSE-002: Horizontal Scrolling
**Priority:** High  
**Labels:** table, ui, responsive  
**Story:** As a user, I want the table to support horizontal scrolling so I can see all columns including new ones (Source, Notes) without truncated descriptions.

**Acceptance Criteria:**
- Table container allows horizontal scrolling when content exceeds viewport width
- Headers remain aligned with data columns during horizontal scroll
- Responsive design maintains usability on mobile devices
- Smooth scrolling experience across browsers

**Implementation Notes:**
- Update CSS table layout to support wider content
- Ensure proper header/body alignment during horizontal scroll
- Test across different viewport sizes

---

### MSE-003: Export Functionality
**Priority:** Medium  
**Labels:** export, data, ui  
**Story:** As a user, I want to export the effects table data as CSV, Excel, or JSON files so I can use the data in other applications or for offline reference.

**Acceptance Criteria:**
- Dropdown menu positioned at top-right of table area (opposite corner from search)
- Export options: CSV, Excel (.xlsx), JSON
- Files are pre-generated server-side and ready for download
- Export includes currently applied filters (optional: checkbox to export all data)
- Filename format: `minecraft-effects-{timestamp}.{extension}`

**Implementation Notes:**
- Add Python scripts to generate export files from effects.json
- Create download endpoint in Bottle server
- Add UI dropdown component matching current design theme

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

---

## Development Notes

**Framework Decision Required:** Before implementing table features (MSE-001, MSE-002), evaluate whether to:
1. Continue with pure JavaScript implementation
2. Adopt a lightweight table library (DataTables, Tabulator, etc.)
3. Introduce a frontend framework (React, Vue, etc.)

Current codebase is well-structured vanilla JS with modular architecture. Consider maintenance overhead, bundle size, and learning curve when making this decision.

**Update Instructions:**
- When working on these tickets, update AGENTS.md with any new patterns or conventions
- Add completed features to this file's completion log
- Update sitemap.xml lastmod date when deploying user-facing changes
