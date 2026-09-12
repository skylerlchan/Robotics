# Best Practices for Organizing Computer Files and Folders

**Research compiled:** April 20, 2026

---

## Table of Contents

1. [File and Folder Naming Conventions](#1-file-and-folder-naming-conventions)
2. [Directory Structure Patterns](#2-directory-structure-patterns)
3. [Software Project Organization](#3-software-project-organization)
4. [Digital Decluttering Methodologies](#4-digital-decluttering-methodologies)
5. [Automated Organization Tools](#5-automated-organization-tools)
6. [Cognitive Load and Findability Research](#6-cognitive-load-and-findability-research)
7. [Anti-Patterns](#7-anti-patterns-common-mistakes)

---

## 1. File and Folder Naming Conventions

### The Core Principles

Good file names are **human-readable, machine-sortable, and search-friendly** ([MIT Communication Lab](https://mitcommlab.mit.edu/broad/commkit/file-structure/)). Every naming convention should satisfy three questions: What is this? When was it created/modified? What version is it?

### Casing Conventions

| Convention | Example | Best For |
|---|---|---|
| **kebab-case** | `project-proposal-draft.md` | URLs, web assets, general files. Most OS-friendly since it avoids spaces and special chars. Widely used in frontend development (React, Angular, Vue component files). |
| **snake_case** | `project_proposal_draft.md` | Python files, data science, academic work. Required by Python's PEP 8 for module names. Common in Linux environments. |
| **PascalCase** | `ProjectProposalDraft.md` | React/TypeScript component files, C#/.NET classes. Convention in many codebases for class-level files. |
| **camelCase** | `projectProposalDraft.md` | JavaScript/TypeScript variable-style naming. Less common for files outside of Java. |
| **UPPER_CASE** | `PROJECT_PROPOSAL.md` | Constants, environment files, config that should stand out (`.env`, `Makefile`, `README`). |
| **lowercase flat** | `projectproposal.md` | Avoid -- hard to read without delimiters. |

**Key rule:** Pick one convention and use it consistently across an entire project or file system ([Stack Overflow discussion](https://stackoverflow.com/questions/43973199/file-naming-conventions-in-reactjs)). Mixing conventions within the same directory creates cognitive friction.

### Date Prefixes

Using **ISO 8601 format (YYYY-MM-DD)** as a prefix is the single most universally recommended naming practice across all sources ([Reddit r/YouShouldKnow](https://www.reddit.com/r/YouShouldKnow/comments/xs1q86/ysk_when_naming_filesfolders_by_date_naming_them/)):

```
2026-04-20_meeting-notes-client-kickoff.md
2026-04-18_quarterly-report-q1.pdf
2026-03-15_invoice-acme-corp.pdf
```

Why YYYY-MM-DD:
- **Auto-sorts chronologically** in any file explorer when sorting alphabetically
- **Unambiguous internationally** -- no confusion between MM/DD and DD/MM
- **Is the actual ISO 8601 standard** for date representation in international data exchange
- The `YYYYMMDD` variant (no hyphens) also works but is less readable

### Versioning in File Names

Avoid the `_final`, `_final_v2`, `_FINAL_REAL` trap. Instead:

**Sequential numbering with zero-padding:**
```
report-v01.pdf
report-v02.pdf
report-v10.pdf    # zero-padding ensures v02 sorts before v10
```

**Date-based versioning for documents:**
```
budget-2026-04-20.xlsx
budget-2026-04-15.xlsx
```

**Semantic versioning for software:**
```
app-v2.1.0.tar.gz   # major.minor.patch
```

For collaborative documents, use version control (Git) or cloud-native versioning (Google Docs, OneDrive version history) instead of filename-based versioning whenever possible.

### Characters to Avoid

- **Spaces** -- use hyphens or underscores instead. Spaces cause issues in URLs, command-line tools, and many programming environments.
- **Special characters** -- avoid `# % & { } \ < > * ? / ! ' " : @ + ` | =`. These have special meanings in shells, URLs, or file systems.
- **Leading dots** -- `.hidden-file` is treated as hidden on Unix/macOS.
- **Trailing dots or spaces** -- Windows silently strips these, causing cross-platform issues.
- **Overly long names** -- Windows has a 260-character path limit (including directory path). Keep individual file names under 50-60 characters.

### Naming Conventions Summary

A good file name template:
```
[YYYY-MM-DD]_[category]-[descriptive-name]-[version].[ext]
```

Examples:
```
2026-04-20_notes-team-standup.md
2026-04-18_design-homepage-mockup-v02.fig
2026-03-01_finance-quarterly-report-q1.xlsx
```

---

## 2. Directory Structure Patterns

### Flat vs. Nested: The Fundamental Tradeoff

**Flat structures** (few levels, many items per level):
- Pros: Easy to scan, fast access, no need to remember hierarchy
- Cons: Becomes overwhelming past ~20-30 items per folder
- Best for: Small projects, reference collections, media libraries

**Nested structures** (many levels, few items per level):
- Pros: Logical grouping, scales to large collections
- Cons: Deep nesting (5+ levels) makes navigation painful, hard to remember paths
- Best for: Large organizations, multi-team projects

The research consensus is to **aim for 2-4 levels of depth maximum** ([UX Stack Exchange](https://ux.stackexchange.com/questions/131399/what-are-good-principles-for-organizing-files)), with Cooper et al.'s *About Face* recommending that "deeply nested hierarchies are at odds with people's mental models."

### By-Type vs. By-Feature Organization

**Group by type** (what it is):
```
project/
  components/
    Button.tsx
    Modal.tsx
    Sidebar.tsx
  styles/
    button.css
    modal.css
    sidebar.css
  tests/
    button.test.ts
    modal.test.ts
    sidebar.test.ts
```

**Group by feature** (what it does):
```
project/
  button/
    Button.tsx
    button.css
    button.test.ts
  modal/
    Modal.tsx
    modal.css
    modal.test.ts
  sidebar/
    Sidebar.tsx
    sidebar.css
    sidebar.test.ts
```

Modern consensus **strongly favors group-by-feature** (also called "colocation") for software projects ([Reddit r/reactjs](https://www.reddit.com/r/reactjs/comments/18qkhgi/folder_structure_group_by_feature_vs_group_by/)). The reasoning:
- Related code changes together -- a new feature means touching one folder, not three
- Easier to delete a feature cleanly
- Reduces long-distance imports
- Matches how developers think about the codebase

For non-software file systems (personal documents, work files), group-by-type tends to work better at the top level (e.g., `Documents/`, `Photos/`, `Projects/`), with by-feature organization within each.

### The Hybrid Approach

Most real-world systems use a hybrid. Top levels are by broad type or area, inner levels are by feature or project:

```
work/
  clients/
    acme-corp/
      contracts/
      deliverables/
      correspondence/
    globex/
      contracts/
      deliverables/
  internal/
    templates/
    policies/
  admin/
    invoices/
    expenses/
```

### Monorepo Patterns

For software teams managing multiple packages in a single repository, the standard monorepo layout (used by tools like Turborepo and Nx) follows this structure ([Reddit r/reactjs, r/devops](https://www.reddit.com/r/reactjs/comments/yhzf3f/nx_vs_turborepo_concerned_about_betting_on_either/)):

```
monorepo/
  apps/
    web/
    mobile/
    api/
  packages/
    ui/            # shared UI components
    config/        # shared configs (eslint, tsconfig)
    utils/         # shared utilities
  tools/           # build scripts, dev tooling
  package.json
  turbo.json
```

Key principles:
- `apps/` contains deployable applications
- `packages/` contains shared libraries consumed by apps
- Each package has its own `package.json` and can be independently versioned
- A root config orchestrates builds and dependencies

---

## 3. Software Project Organization

### Universal Conventions Across Languages

Nearly every well-maintained open source project includes these top-level items ([Software Engineering Stack Exchange](https://softwareengineering.stackexchange.com/questions/86914/whats-the-best-structure-for-a-repository)):

```
project/
  README.md          # what this project is and how to use it
  LICENSE            # legal terms
  .gitignore         # files to exclude from version control
  CHANGELOG.md       # version history
  CONTRIBUTING.md    # how to contribute
  docs/              # documentation
  tests/             # test suite
  src/               # source code (or language-specific variant)
  scripts/           # build/deploy/utility scripts
  .github/           # CI/CD workflows (GitHub Actions)
```

### Python (src layout)

The Python Packaging Authority recommends the **src layout** to prevent accidental imports of uninstalled code ([Python Packaging Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/), [Reddit r/Python](https://www.reddit.com/r/Python/comments/18qkivr/what_is_the_optimal_structure_for_a_python_project/)):

```
my-project/
  src/
    my_package/
      __init__.py
      core.py
      utils.py
      models/
        __init__.py
        user.py
  tests/
    test_core.py
    test_utils.py
  pyproject.toml
  README.md
```

Key conventions:
- Package directories use `snake_case`
- Top-level project directory uses `kebab-case`
- `src/` layout prevents the "it works on my machine" import problem
- Tests mirror the source structure

### Go (Standard Project Layout)

The widely-referenced Go project layout (55.8k GitHub stars) defines these directories ([golang-standards/project-layout](https://github.com/golang-standards/project-layout)):

```
my-project/
  cmd/               # main applications (entry points)
    myapp/
      main.go
  internal/          # private application code (compiler-enforced)
    auth/
    database/
  pkg/               # public library code safe for external use
  api/               # API definitions (OpenAPI, protobuf)
  configs/           # configuration templates
  deployments/       # docker-compose, k8s manifests
  build/             # packaging and CI scripts
  scripts/           # helper scripts
  docs/
  test/              # integration/e2e tests
  tools/             # supporting tools
```

Note: While this layout is popular, Go core team member Russ Cox has noted it is "not official" -- Go itself recommends a simpler layout at [go.dev/doc/modules/layout](https://go.dev/doc/modules/layout), starting minimal and growing as needed ([Reddit r/golang](https://www.reddit.com/r/golang/comments/1fafjdy/project_layout/)).

### React / Next.js (Colocation-First)

Modern React projects favor **colocation** -- keeping related files together by route or feature ([Reddit r/nextjs](https://www.reddit.com/r/nextjs/comments/1kkpqtm/sharing_my_goto_project_structure_for_nextjs/)):

```
my-app/
  src/
    app/                    # Next.js App Router
      (auth)/
        login/
          page.tsx
          login-form.tsx
          login-form.test.tsx
        register/
          page.tsx
      dashboard/
        page.tsx
        dashboard-stats.tsx
        use-dashboard-data.ts
      layout.tsx
    components/             # truly shared/global components
      ui/
        button.tsx
        modal.tsx
    lib/                    # shared utilities
      api-client.ts
      format-date.ts
    hooks/                  # shared hooks
    types/                  # shared type definitions
  public/
  next.config.js
```

Key principle: Components used by only one route live *in that route's folder*. Only truly shared items go in top-level `components/`, `lib/`, `hooks/`.

### Rust (Cargo Convention)

```
my-project/
  src/
    main.rs           # binary entry point
    lib.rs            # library entry point
    config.rs
    models/
      mod.rs
      user.rs
  tests/              # integration tests
  benches/            # benchmarks
  examples/           # example programs
  Cargo.toml
```

### Common Pattern: The "Screaming Architecture"

Robert C. Martin (Uncle Bob) advocates that a project's top-level directory structure should **scream what the application does**, not what framework it uses. Looking at the folder names should tell you "this is a healthcare system" not "this is a Rails app" ([Clean Architecture, Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2011/09/30/Screaming-Architecture.html)):

```
# Bad -- screams "Rails"          # Good -- screams "Healthcare"
app/                              patients/
  controllers/                    appointments/
  models/                         prescriptions/
  views/                          billing/
  helpers/                        medical-records/
```

---

## 4. Digital Decluttering Methodologies

### PARA Method (Tiago Forte)

The PARA method, developed by Tiago Forte and described in his book *Building a Second Brain*, organizes all digital information into exactly four top-level categories ([Forte Labs](https://fortelabs.com/blog/para/)):

```
1-Projects/       # short-term efforts with a defined goal and deadline
2-Areas/          # ongoing responsibilities with standards to maintain
3-Resources/      # topics of ongoing interest for future reference
4-Archive/        # inactive items from the other three categories
```

**Projects** have a finish line: "Launch website redesign," "Complete tax filing," "Plan vacation to Japan."

**Areas** are ongoing: "Health," "Finances," "Career Development," "Home Maintenance." They don't have an end date.

**Resources** are reference material by topic: "Machine Learning," "Cooking Recipes," "Photography Techniques."

**Archive** is where completed projects, retired areas, and outdated resources go. Nothing is deleted -- just moved out of active view.

Key insight from Forte: Most people organize by subject (like school), but should organize **by actionability** -- "What do I need to move forward on my current projects?" should be the primary organizing question. Organizing by broad academic categories ("Psychology," "Marketing") creates folders you'll never actually open when doing real work.

**PARA in practice:**
```
1-Projects/
  website-redesign/
  q2-marketing-campaign/
  apartment-search/
2-Areas/
  health/
  finances/
  career/
  home/
3-Resources/
  design-inspiration/
  industry-research/
  cooking/
4-Archive/
  2025-projects/
  old-client-work/
```

The numbered prefixes force a specific sort order, keeping Projects (the most actionable items) at the top.

### Johnny Decimal System

Johnny Decimal imposes a strict numerical taxonomy on your file system with a maximum of three levels ([johnnydecimal.com](https://johnnydecimal.com/)):

**Structure: Area > Category > ID**

```
10-19 Life Admin/
  11 Me/
    11.01 Birth certificate
    11.02 Passport
    11.03 Resume
  12 House/
    12.01 Lease agreement
    12.02 Insurance policy
  13 Money/
    13.01 Tax return 2025
    13.02 Investment accounts
  14 Online/
  15 Travel/
    15.01 Frequent flyer accounts
    15.02 Trip to NYC

20-29 Home Business/
  21 Clients/
  22 Invoicing/
  23 Marketing/

30-39 Tennis Club/
  31 Membership/
  32 Events/
```

**Rules:**
- Maximum 10 **areas** (numbered 10-19, 20-29, ... 90-99)
- Maximum 10 **categories** per area (numbered x1, x2, ... x9, x0)
- Maximum 100 **IDs** per category (numbered xx.01 through xx.99)
- **Never** go deeper than the ID level -- files go *inside* ID folders
- IDs are globally unique -- `15.02` means one specific thing in your entire system

**Strengths:** Extremely findable. You can tell someone "it's in 15.02" over the phone. Numbers don't rearrange alphabetically when you add new folders. The 10-item limit per level keeps cognitive load low.

**Limitations:** The rigid cap of 10 areas and 10 categories per area can feel constraining for some use cases. Items that logically belong in multiple categories have to be assigned one location (though you can use shortcuts/symlinks). Community discussion on Hacker News notes this is a common challenge with any strict hierarchy ([Hacker News](https://news.ycombinator.com/item?id=36308366)).

### GTD (Getting Things Done) by David Allen

David Allen's GTD system treats the file system as a **reference filing system** -- not a task manager. The folder structure supports quick retrieval, not organization for its own sake ([GTD Forum](https://forum.gettingthingsdone.com/threads/how-to-structure-your-reference-material.17239/)):

**Core GTD filing principles:**
- **Alphabetical by topic** is the default. Don't over-categorize. A single A-Z filing cabinet (physical or digital) with one folder per topic.
- **Create folders on demand** -- only when you have something to file, not speculatively.
- **Use the "less than 60 seconds" rule** -- if it takes more than 60 seconds to decide where to file something, your system is too complicated.
- **Purge regularly** -- review and archive quarterly.

**GTD digital structure:**
```
reference/
  accounting/
  car-maintenance/
  health-records/
  insurance/
  legal/
  recipes/
  travel/
  warranties/
```

GTD is intentionally simple -- the philosophy is that your *filing system* should not require mental energy. The work happens in your task management system (inbox, next actions, waiting for, someday/maybe), not in how you organize reference files.

### Comparison of Methodologies

| Aspect | PARA | Johnny Decimal | GTD |
|---|---|---|---|
| **Primary axis** | Actionability | Numerical taxonomy | Alphabetical simplicity |
| **Max depth** | 2-3 levels | 3 levels (strict) | 1-2 levels |
| **Best for** | Knowledge workers, creatives | People who need strict order and findability | People who want minimal filing overhead |
| **Weakness** | Project/Area boundary can be fuzzy | Rigid caps can feel constraining | Too flat for large collections |
| **Philosophy** | Organize by what you're working on now | Everything has one address | Filing should take zero thought |

---

## 5. Automated Organization Tools

### Hazel (macOS) -- $42

The gold standard for Mac file automation ([Noodlesoft](https://www.noodlesoft.com/)). Hazel watches designated folders and automatically processes files based on rules you define.

**How it works:**
- You select folders to watch (e.g., Downloads, Desktop)
- You create rules with conditions (file name contains, date is, file type is, etc.)
- You define actions (move, rename, tag, archive, trash, run script)

**Common Hazel rules** ([Reddit r/macapps](https://www.reddit.com/r/macapps/comments/1go0ytk/hazel_automations/)):
- **Auto-file downloads:** If file extension is `.pdf` and name contains "invoice" -> move to `~/Documents/Finances/Invoices/`
- **Unzip and clean:** If file is `.zip` -> extract, then trash the archive
- **Date-stamp screenshots:** If file matches `Screenshot*.png` -> rename to `YYYY-MM-DD_screenshot-[counter].png`
- **Trash old files:** If file in Downloads is older than 30 days and not tagged "keep" -> move to Trash
- **Install apps from DMGs:** If file is `.dmg` -> mount, copy `.app` to Applications, unmount, trash DMG
- **Import photos:** If image file appears in designated folder -> import to Photos app

**Power features:** Pattern matching in file contents (e.g., scan PDFs for an account number), Spotlight integration, AppleScript/Shortcuts support, tag management.

### organize (Python, open source) -- Free

A cross-platform, YAML-configured file organizer ([GitHub: tfeldmann/organize](https://github.com/tfeldmann/organize), [Reddit r/selfhosted](https://www.reddit.com/r/selfhosted/comments/12sv535/organize_file_management_automation_tool/)):

```yaml
rules:
  - name: "Sort downloads by type"
    locations: ~/Downloads
    filters:
      - extension:
          - pdf
          - docx
    actions:
      - move: ~/Documents/PDFs/

  - name: "Date-prefix photos"
    locations: ~/Photos/Unsorted
    filters:
      - extension:
          - jpg
          - png
      - created
    actions:
      - rename: "{created.strftime('%Y-%m-%d')}_{filename}"
      - move: ~/Photos/Sorted/

  - name: "Clean old downloads"
    locations: ~/Downloads
    filters:
      - lastmodified:
          days: 30
    actions:
      - trash
```

Runs on macOS, Linux, and Windows. Can be scheduled via cron or launchd. Supports filters by file size, creation date, regex on filename, file content, EXIF data, and more.

### Other Notable Tools

| Tool | Platform | Type | Key Feature |
|---|---|---|---|
| **File Juggler** | Windows | GUI, paid ($40) | Visual rule builder, content-aware filing |
| **DropIt** | Windows | Free, open source | Drag-and-drop processing with customizable rules |
| **Automator / Shortcuts** | macOS | Built-in | Folder Actions can trigger scripts when files appear |
| **watchdog** (Python) | Cross-platform | Library | Build custom file watchers programmatically |
| **AI-based organizers** | Various | Emerging | Projects like [naztech-automated-data-sorting](https://github.com/nazpins/naztech-automated-data-sorting-tools) use local LLMs to categorize files by content ([Reddit r/opensource](https://www.reddit.com/r/opensource/comments/1fmglr7/i_built_a_python_script_uses_ai_to_organize_files/)) |

### Common Automation Rules to Implement

1. **Downloads triage:** Auto-sort files from Downloads into type-based folders (PDFs, images, installers, archives)
2. **Screenshot management:** Auto-rename with dates, move to a screenshots folder
3. **Invoice/receipt filing:** Pattern-match on content (account numbers, vendor names) and file accordingly
4. **Desktop cleaner:** Sweep files older than X days from Desktop to an inbox folder
5. **Duplicate detection:** Flag or remove duplicate files based on hash comparison
6. **Archive compression:** Auto-compress folders older than a threshold

---

## 6. Cognitive Load and Findability Research

### Miller's Law: The Magic Number 7 +/- 2

George Miller's seminal 1956 paper demonstrated that human working memory can hold approximately 7 +/- 2 items (5-9 chunks) at a time ([Miller, 1956](https://pubmed.ncbi.nlm.nih.gov/13310704/)). This has direct implications for folder design:

- **Folders with more than ~10 items** start requiring scanning rather than recognition
- **7 items per level** is a practical upper bound for folders that users need to navigate without reading every label
- This doesn't mean limiting to 7 items everywhere -- it means that at each *decision point*, users should face a manageable number of choices

### Hick's Law: More Choices = Slower Decisions

Hick's Law (Hick & Hyman, 1952) states that **decision time increases logarithmically with the number of choices**: RT = a + b*log2(N+1) ([Interaction Design Foundation](https://ixdf.org/literature/topics/hick-s-law), [Laws of UX](https://lawsofux.com/hicks-law/), [Nielsen Norman Group](https://www.nngroup.com/videos/hicks-law-long-menus/)).

Applied to file systems:
- A folder with 5 subfolders takes measurably less time to navigate than one with 20
- However, **very shallow hierarchies** (2 items per level, 10 levels deep) are worse than moderate-width hierarchies (7-10 items per level, 3 levels deep), because each click yields little progress toward the goal
- **Optimal: 7-10 items per level, 2-4 levels deep** -- each decision meaningfully narrows the search space

UX research from the Interaction Design Foundation notes: "If the decision making is so simple that users make little progress towards their objectives each time they make a decision, they'll be as likely to leave as users who find a decision-making process impossibly confusing because they've seen too many options at once." ([IxDF](https://ixdf.org/literature/article/hick-s-law-making-the-choice-easier-for-users))

### Information Scent Theory

Developed by Peter Pirolli and Stuart Card at Xerox PARC, **information scent** describes how people assess whether a path will lead them to what they're looking for. Strong scent = clear, descriptive labels. Weak scent = vague, ambiguous names.

Applied to folders:
- `misc/`, `stuff/`, `new-folder/` have zero information scent -- users must open them to discover contents
- `2026-q1-financial-reports/` has strong scent -- users know immediately if this is relevant
- Folder names should **predict contents** at a glance

### The Cost of Disorganization

Research on context switching and information retrieval time supports the case for intentional organization:

- A McKinsey study found knowledge workers spend **19% of their time searching for and gathering information** -- nearly a full day per week ([McKinsey Global Institute, 2012](https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/the-social-economy))
- IDC research estimated the cost of an information worker being unable to find information at **$14,000 per worker per year** in lost productivity
- Context switching itself has a measurable cost: Gloria Mark's research at UC Irvine found it takes an average of **23 minutes and 15 seconds** to return to full focus after an interruption -- and searching for a misplaced file is a form of interruption ([Mark, Gonzalez & Harris, 2005](https://ics.uci.edu/~gmark/CHI2005.pdf))
- Enterprise research from Moveworks found that rising "Where do I find...?" questions are an early indicator of organizational knowledge fragmentation ([Moveworks](https://www.moveworks.com/us/en/resources/blog/the-real-cost-of-context-switching-in-the-enterprise))

### The "Retrieve vs. Remember" Framework

Cognitive psychology distinguishes between **recall** (generating from memory) and **recognition** (identifying from options). File system design should favor recognition:

- **Good:** Browsable, well-labeled folders with predictable locations (recognition)
- **Bad:** Requiring users to remember exact file names to search for (recall)
- **Best:** Designing for both -- browsable hierarchy *and* searchable metadata (tags, consistent naming)

The MIT Communication Lab makes this point well: "Knowing where files are, when to use certain code for certain operations, and how to find associated results, data, and figures can not only streamline productivity, but also allow for consistency and shareability." ([MIT CommLab](https://mitcommlab.mit.edu/broad/commkit/file-structure/))

---

## 7. Anti-Patterns: Common Mistakes

### 1. The "Miscellaneous" Junk Drawer

Creating folders named `misc/`, `stuff/`, `temp/`, `unsorted/`, `other/`, or `new-folder/`. These become black holes that grow indefinitely because nothing has an exit criterion. If a file doesn't fit anywhere, the system needs a new category -- not a catch-all.

### 2. Infinite Nesting (The Matryoshka Problem)

```
Documents/
  Work/
    Projects/
      2026/
        Q1/
          Client/
            Acme/
              Deliverables/
                Final/
                  v2/
                    approved/
                      report.pdf    # 10 levels deep
```

Every additional level of nesting adds a decision point and a click. Research supports staying at **3-4 levels maximum** ([Cooper et al., *About Face*](https://ux.stackexchange.com/questions/131399/what-are-good-principles-for-organizing-files)). If you need more depth, your categories are too granular.

### 3. The "Final" Version Spiral

```
report.docx
report-final.docx
report-FINAL.docx
report-FINAL-v2.docx
report-FINAL-v2-reviewed.docx
report-FINAL-v2-reviewed-ACTUAL.docx
```

This is the most universally mocked anti-pattern. Solutions: use version control (Git), use cloud document versioning (Google Docs, Office 365), or use strict `v01`/`v02` numbering with dates.

### 4. Organizing by Date Only

```
2026/
  04/
    20/
      file1.pdf
      file2.xlsx
      file3.jpg
```

Pure date-based hierarchies force users to remember *when* they created something rather than *what* it is. Dates are useful as **prefixes within meaningful categories**, not as the primary organizational axis (unless the content is inherently temporal, like daily logs or journal entries).

### 5. Duplicate Copies Everywhere

Keeping copies of the same file in multiple locations "just in case." This leads to version divergence (which copy is current?), wasted storage, and confusion. Instead: use shortcuts/symlinks/aliases, or organize by the file's *primary* context and search when you need it elsewhere.

### 6. Empty Speculative Folders

Pre-creating elaborate folder structures before having files to put in them. Empty folders add visual clutter and create decision paralysis ("should this go in Q3 or is it a project?"). GTD's principle applies: **create folders on demand**, not in advance.

### 7. Inconsistent Naming Within the Same Directory

```
project-alpha/
  Meeting Notes Jan 2026.docx
  2026-02_meeting-notes.md
  meetingNotes_March.txt
  NOTES april.pdf
```

Mixing date formats, casing conventions, delimiters, and file types within the same folder makes scanning and sorting impossible.

### 8. Over-Categorization

Creating 50 top-level folders, each with 2-3 files. This forces users to remember or navigate a sprawling taxonomy. Better to have 5-10 well-populated categories than 50 near-empty ones. The PARA method's four-folder top level is an intentional response to this.

### 9. Using Folder Structure as a Substitute for Search

Some people create deeply hierarchical folders because they distrust search. Modern OS search (Spotlight, Windows Search) and file managers are effective if files have good names. The best approach is to **design for both browsing and searching** -- descriptive names that work in a search bar *and* in a folder tree.

### 10. Ignoring Cross-Platform Compatibility

- Using characters valid on macOS but invalid on Windows (`:`, `\`)
- Creating case-sensitive duplicate names (`readme.md` vs `README.md`) that collide on case-insensitive file systems
- Exceeding Windows' 260-character path limit with deeply nested structures
- Using extended Unicode characters that some tools can't handle

---

## Appendix: Quick Reference

### The 10 Rules of Good File Organization

1. **Be consistent** -- pick conventions and stick to them everywhere
2. **Be descriptive** -- folder and file names should predict their contents
3. **Use ISO dates** -- YYYY-MM-DD prefix when dates matter
4. **Stay shallow** -- 3-4 levels of depth maximum
5. **Limit breadth** -- 7-10 items per folder at decision points
6. **Group by action** -- organize by what you're working on, not abstract categories
7. **Use version control** -- never `_final_v2_REAL`
8. **Create on demand** -- don't pre-build empty hierarchies
9. **Archive, don't delete** -- move inactive items out of sight, keep them findable
10. **Automate the boring parts** -- let tools handle Downloads triage and cleanup

### Example: Complete Personal File System

```
~/
  1-projects/                          # PARA: active work
    apartment-search/
    freelance-client-acme/
    learn-rust/
  2-areas/                             # PARA: ongoing responsibilities
    career/
      resume-2026.pdf
      portfolio/
    finances/
      2026-tax/
      banking/
    health/
  3-resources/                         # PARA: reference material
    design-inspiration/
    recipes/
    reading-notes/
  4-archive/                           # PARA: completed/inactive
    2025-projects/
    old-client-work/
  code/                                # software projects (separate tree)
    personal/
      my-website/
      dotfiles/
    work/
      company-app/
    open-source/
      contributions/
  media/                               # large files (separate tree)
    photos/
      2026/
      2025/
    music/
    videos/
```

### Example: Software Project Template

```
my-project/
  .github/
    workflows/
      ci.yml
  docs/
    architecture.md
    api.md
  src/
    features/
      auth/
      dashboard/
      settings/
    shared/
      components/
      hooks/
      utils/
    types/
  tests/
    unit/
    integration/
    e2e/
  scripts/
    build.sh
    seed-db.sh
  .gitignore
  .env.example
  README.md
  LICENSE
  CHANGELOG.md
  package.json
```

---

## Sources

- [Forte Labs - The PARA Method](https://fortelabs.com/blog/para/)
- [Johnny Decimal](https://johnnydecimal.com/)
- [MIT Communication Lab - File Structure](https://mitcommlab.mit.edu/broad/commkit/file-structure/)
- [Noodlesoft Hazel](https://www.noodlesoft.com/)
- [golang-standards/project-layout (GitHub)](https://github.com/golang-standards/project-layout)
- [Go Module Layout (Official)](https://go.dev/doc/modules/layout)
- [Interaction Design Foundation - Hick's Law](https://ixdf.org/literature/article/hick-s-law-making-the-choice-easier-for-users)
- [Laws of UX - Hick's Law](https://lawsofux.com/hicks-law/)
- [Nielsen Norman Group - Hick's Law and Menus](https://www.nngroup.com/videos/hicks-law-long-menus/)
- [Miller, G.A. (1956) "The Magical Number Seven"](https://pubmed.ncbi.nlm.nih.gov/13310704/)
- [Mark, Gonzalez & Harris (2005) - Cost of Interrupted Work](https://ics.uci.edu/~gmark/CHI2005.pdf)
- [Moveworks - Cost of Context Switching](https://www.moveworks.com/us/en/resources/blog/the-real-cost-of-context-switching-in-the-enterprise)
- [GTD Forum - Reference Filing](https://forum.gettingthingsdone.com/threads/how-to-structure-your-reference-material.17239/)
- [Cooper et al., *About Face* - Hierarchy Design](https://ux.stackexchange.com/questions/131399/what-are-good-principles-for-organizing-files)
- [UX StackExchange - Organizing Files](https://ux.stackexchange.com/questions/131399/what-are-good-principles-for-organizing-files)
- [Reddit r/datacurator - File System Organization](https://www.reddit.com/r/datacurator/comments/1gjk6tp/how_do_you_organize_your_file_system/)
- [Reddit r/YouShouldKnow - ISO Date Naming](https://www.reddit.com/r/YouShouldKnow/comments/xs1q86/ysk_when_naming_filesfolders_by_date_naming_them/)
- [Reddit r/reactjs - Feature vs Type Grouping](https://www.reddit.com/r/reactjs/comments/18qkhgi/folder_structure_group_by_feature_vs_group_by/)
- [Reddit r/nextjs - Colocation-First Structure](https://www.reddit.com/r/nextjs/comments/1kkpqtm/sharing_my_goto_project_structure_for_nextjs/)
- [Reddit r/selfhosted - Organize Tool](https://www.reddit.com/r/selfhosted/comments/12sv535/organize_file_management_automation_tool/)
- [Robert C. Martin - Screaming Architecture](https://blog.cleancoder.com/uncle-bob/2011/09/30/Screaming-Architecture.html)
- [Hacker News - Johnny Decimal Discussion](https://news.ycombinator.com/item?id=36308366)
- [Stack Overflow - File Naming in React](https://stackoverflow.com/questions/43973199/file-naming-conventions-in-reactjs)
- [Software Engineering SE - Repository Structure](https://softwareengineering.stackexchange.com/questions/86914/whats-the-best-structure-for-a-repository)
