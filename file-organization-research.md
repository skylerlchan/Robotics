# Automated File/Folder Organization: Algorithms, Heuristics, and Tools

*Research compiled 2026-04-20 09:47*

---

## 1. File Classification Approaches

How tools decide where a file belongs falls into four main strategies, used alone or in combination.

### By Extension (Simplest)

The most basic approach maps file extensions to categories. Every tool supports this as a baseline.

```yaml
# organize-cli example
rules:
  - name: "Sort by extension"
    locations: ~/Downloads
    filters:
      - extension:
          - pdf
          - docx
    actions:
      - move: "~/Documents/{extension | upper}/"
```

Limitations: A bank statement and a D&D character sheet are both `.pdf` files. Extension-only classification is "useless" for meaningful organization ([Medium - Using Local LLMs to Organize Files](https://medium.com/data-science-collective/using-local-llms-to-organize-messy-files-a-technical-deep-dive-79433165f4fb)).

### By Filename Patterns

More useful than extension alone. Matching filenames against known patterns (invoices, screenshots, date strings, project prefixes) provides a cheap heuristic with surprisingly high accuracy.

```yaml
# organize-cli: match invoices by name
rules:
  - name: "Sort invoices and receipts"
    locations: ~/Downloads
    subfolders: true
    filters:
      - extension: pdf
      - name:
          contains:
            - Invoice
            - Order
            - Purchase
          case_sensitive: false
    actions:
      - move: ~/Documents/Shopping/
```

Hazel supports the same concept through its GUI: "If name contains 'Screenshot', move to ~/Screenshots" ([Noodlesoft - About Folders & Rules](https://www.noodlesoft.com/manual/hazel/hazel-basics/about-folders-rules/)).

### By Content Analysis

Reading file content to determine what a document actually is. This is the approach that separates intelligent tools from basic sorters.

**Text extraction pipeline** ([Medium - Using Local LLMs to Organize Files](https://medium.com/data-science-collective/using-local-llms-to-organize-messy-files-a-technical-deep-dive-79433165f4fb)):
1. Check extension to determine extraction method
2. Use PyPDF2 for PDFs, python-docx for DOCX, openpyxl for XLSX, python-pptx for PPTX
3. Extract first N pages/chars as preview (typically 2000-3000 chars)
4. Feed preview to classifier (rule-based or LLM)

organize-cli's `filecontent` filter does regex matching on extracted text:
```yaml
# Match files containing specific text
rules:
  - name: "Sort by content"
    locations: ~/Documents
    filters:
      - filecontent: "EARNINGS REPORT"
    actions:
      - move: ~/Documents/Finance/
```

Hazel can also read content: "When a Word file in your Research folder contains the text 'earnings report,' apply the Finder tag 'Finances'" ([Make Tech Easier](https://www.maketecheasier.com/hazel-rules-automate-file-management/)).

### By Metadata

EXIF data for images, creation/modification dates, file size, macOS-specific attributes (date added, date last used).

```yaml
# organize-cli: sort photos by EXIF date
rules:
  - name: "Sort photos by EXIF year/month"
    locations: ~/Photos
    subfolders: true
    filters:
      - extension:
          - jpg
          - png
          - heic
      - exif
    actions:
      - move: "~/Photos/{exif.image_datetime.year}/{exif.image_datetime.month:02}/"
```

Enterprise document classification goes further, combining content sensitivity detection (PII, PCI, HIPAA markers) with metadata to determine classification levels: public, internal, confidential, restricted ([Concentric AI](https://concentric.ai/data-classification-reviewing-challenges-methodologies-and-best-practices/)).

---

## 2. Rule-Based Systems

### organize-cli (Cross-Platform, Open Source)

The most capable open-source file automation tool. Configuration is YAML-based with a `rules` structure containing `locations`, `filters`, and `actions` ([organize docs](https://organize.readthedocs.io/en/latest/)).

**Available Filters:**
| Filter | What It Does |
|--------|-------------|
| `extension` | Match by file extension |
| `name` | Match filename (startswith, endswith, contains) |
| `regex` | Regex with named capture groups |
| `filecontent` | Regex on extracted file text (PDF, DOCX, TXT, etc.) |
| `created` | Created date (older/newer than N days/hours/etc.) |
| `lastmodified` | Last modified date |
| `date_added` | Date added to folder (macOS only) |
| `date_lastused` | Last used date (macOS only) |
| `size` | File size comparison |
| `extension` | File extension matching |
| `duplicate` | Fast byte-by-byte duplicate detection |
| `empty` | Empty files or directories |
| `exif` | EXIF metadata from images |
| `hash` | File hash calculation |
| `mimetype` | MIME type matching |
| `python` | Arbitrary Python code as filter |

Source: [organize filters docs](https://tfeldmann.github.io/organize/filters/)

**Available Actions:**
| Action | What It Does |
|--------|-------------|
| `move` | Move file/dir with conflict resolution (skip, overwrite, trash, rename_new, rename_existing) |
| `copy` | Copy with same conflict options |
| `rename` | Rename in place |
| `trash` | Send to system trash |
| `delete` | Permanent delete |
| `echo` | Print message (useful in sim mode) |
| `confirm` | Interactive confirmation prompt |
| `shell` | Run arbitrary shell commands |
| `python` | Run arbitrary Python code |
| `macos_tags` | Set macOS Finder tags |
| `symlink` | Create symbolic links |
| `write` | Write content to a file |

Source: [organize actions docs](https://tfeldmann.github.io/organize/actions/)

**Key design features:**
- `organize sim` runs a full dry-run simulation before touching files
- Filters can be negated with `not` prefix: `not extension: jpg`
- `filter_mode: "none"` to exclude all filters
- Named regex groups flow into action templates: `{regex.group_name}`
- Supports `subfolders: true` for recursive scanning

**Advanced example -- regex extraction + rename:**
```yaml
rules:
  - name: "Rename invoices by date"
    locations: ~/Downloads
    filters:
      - regex: '^(?P<year>\d{4})-(?P<month>\d{2})-(?P<vendor>\w+)-invoice\.pdf$'
    actions:
      - move: "~/Documents/Invoices/{regex.vendor}/{regex.year}/"
```

**Duplicate detection + cleanup:**
```yaml
rules:
  - name: "Delete duplicates with confirmation"
    locations:
      - ~/Downloads
      - ~/Documents
    filters:
      - not empty
      - duplicate
      - name
    actions:
      - confirm: "Delete {name}?"
      - trash
```

### Hazel (macOS, Commercial)

Hazel watches designated folders and runs rules when files match conditions. It operates on an "if this, then that" structure ([Noodlesoft - Hazel Overview](https://www.noodlesoft.com/manual/hazel/hazel-overview/)):

**Conditions can test:**
- File name, extension, kind
- File contents (searches inside documents)
- Dates: created, modified, added, last opened
- Size, color label, tags
- Nested conditions with AND/OR/NOT logic

**Actions include:**
- Move, copy, rename, archive (zip)
- Add/remove Finder tags, color labels
- Run shell scripts, Automator workflows, AppleScripts
- Upload to server
- Import into apps (Photos, iTunes, etc.)

**Concrete Hazel rule examples** ([Automators Talk](https://talk.automators.fm/t/must-have-hazel-rules/3160)):
- Downloads folder: If file extension is PDF and name contains "invoice" -> move to ~/Documents/Invoices and tag "Finances"
- Desktop: If file kind is Image and date added is not in the last 1 day -> move to ~/Pictures/Desktop-Captures
- Downloads: If file is incomplete (.crdownload, .part) and date modified is not in the last 1 hour -> delete

**Key advantage:** No programming knowledge required. GUI-based rule builder with visual condition/action selection. Ships with starter rules to learn from ([OWC Blog](https://eshop.macsales.com/blog/86195-app-star-of-the-week-hazel-for-mac-is-file-automation-for-the-rest-of-us/)).

### File Juggler (Windows, Commercial)

Windows equivalent of Hazel. Monitors folders and applies rules with conditions and actions ([File Juggler docs](https://www.filejuggler.com/documentation/creating-rules/)).

**Condition types:**
- File path components (name, extension, full path)
- File content (reads PDF and DOCX)
- Creation and modification dates
- File size
- Logical grouping: all-of (AND), any-of (OR)

**Actions:**
- Move, copy, rename, delete, recycle
- Extract zip/rar archives
- Run command-line commands

Source: [File Juggler - Conditions](https://www.filejuggler.com/documentation/conditions/), [File Juggler - Actions](https://www.filejuggler.com/documentation/actions/)

---

## 3. AI-Powered Organization

### LlamaFS (Open Source)

A self-organizing file system using Llama 3. Two operating modes ([GitHub - iyaja/llama-fs](https://github.com/iyaja/llama-fs)):

**Batch mode:** Send a directory, get back a proposed new structure, review and accept.

**Watch mode:** A daemon watches your directory, intercepts filesystem operations, learns from your recent renames to proactively suggest organization.

**Architecture:**
- Python backend with Groq (cloud) or Ollama (local/private) for LLM inference
- Electron frontend for reviewing proposed changes before applying
- Moondream for image understanding, Whisper for audio transcription
- ~500ms per file processing with smart caching
- "Stealth Mode" for fully local processing with no cloud uploads

### Local LLM File Organizer Pattern

The most detailed technical approach comes from Muhammad Karim's deep dive on building a local LLM file organizer ([Medium - Using Local LLMs to Organize Files](https://medium.com/data-science-collective/using-local-llms-to-organize-messy-files-a-technical-deep-dive-79433165f4fb)):

**Three-component architecture:**

1. **Content Extractor** -- reads actual file content using format-specific libraries (PyPDF2, python-docx, openpyxl, python-pptx), producing a 2000-3000 char preview

2. **AI Classifier** -- sends the preview to a local LLM (Gemma 3:4b via Ollama) with a carefully engineered prompt:
```python
prompt = """You are an expert file organization AI.
Analyze this file based on its ACTUAL CONTENT (not just filename).

FILENAME: {filename}
EXTENSION: {extension}

=== FILE CONTENT (MOST IMPORTANT) ===
{content_preview}
=== END CONTENT ===

CRITICAL ANALYSIS GUIDELINES:
1. READ THE CONTENT CAREFULLY - most important factor
2. Look for: invoice numbers, contract terms, project names,
   personal vs business language
3. Use ONLY ONE subcategory level

Respond in JSON:
{
  "category": "Main category (e.g., Work, Personal, Projects)",
  "subcategory": "ONE specific subcategory",
  "reasoning": "Brief explanation based on CONTENT analysis"
}"""
```

3. **Undo Manager** -- logs every file operation to a JSON file before execution, enabling full reversal of any session

**Design principles:**
- Read anything: go beyond filenames
- See images: use vision models (multimodal LLMs)
- 100% private: all processing local
- Reversible: every operation logged for undo
- Accessible: GUI option alongside CLI

### Dropbox Smart Move (Production ML)

Dropbox's production ML system for suggesting where to move files, detailed in their engineering blog ([Dropbox Tech Blog](https://dropbox.tech/machine-learning/smart-move-ml-ai-file-organization-automation)):

**Training data generation:** Treat already-organized folders as the "labeled end state" of a theoretical successful move. Deconstruct existing folder structures into (file, candidate_folder, correct/incorrect) training pairs.

**Signals used:**
- Name of the file being moved (including extension)
- Name of each candidate folder
- Names of files/folders already within each candidate folder ("potential siblings")

**Model architecture:**
- Character-level and GloVE word-level embeddings via custom encoder
- Similarity matrices: context-to-candidate and context-to-siblings
- Deep neural network with <20 hidden layers and dropout
- Score-based ranking with confidence tiers (top 20% = high confidence)

**Key finding:** Sibling files in a folder give more organizational signal than the folder name itself. A folder named "finance" is ambiguous, but seeing `w-2.pdf`, `taxreturn_2020.pdf`, `charitable.img` inside it tells you exactly what belongs there.

**Results:** High-confidence suggestions accepted 94% of the time (heuristic) and 90% (trained model). The simpler filename similarity heuristic actually outperformed the trained model in production alpha testing, likely because the model overfit on internal Dropbox usage patterns.

**Critical design lesson:** "Organization is very personal. Multiple users said they were wary of allowing other people to organize their Dropbox contents." This drove their human-in-the-loop design where users always approve before files move.

### AI FileSorter (Desktop App)

Cross-platform desktop app supporting both local (Llama, Mistral via Ollama) and cloud (OpenAI, Gemini) LLMs. Can analyze images with LLaVA and documents with standard extractors. Suggests filenames and categories. Fully offline-capable ([GitHub - hyperfield/ai-file-sorter](https://github.com/hyperfield/ai-file-sorter)).

---

## 4. Deduplication Strategies

### Hash-Based (Exact Duplicates)

The standard approach: compute a cryptographic hash (MD5, SHA-256) of each file and compare. Identical hashes = identical files.

**Optimization layers** (as used by organize-cli and similar tools):
1. **Size pre-filter:** Files of different sizes cannot be duplicates. Group by size first.
2. **Partial hash:** Hash only the first N bytes. Eliminates most non-duplicates cheaply.
3. **Full hash:** Only compute full hash for files that match on size and partial hash.
4. **Byte-by-byte comparison:** Final verification for hash collisions.

organize-cli's `duplicate` filter implements this as a fast pipeline:
```yaml
rules:
  - name: "Find duplicates"
    locations:
      - ~/Downloads
      - ~/Documents
    filters:
      - not empty
      - duplicate
    actions:
      - echo: "Duplicate: {name} (size: {size})"
```

### Fuzzy Matching (Near-Duplicates)

For files that are similar but not identical -- different versions, slightly cropped images, reformatted documents ([Fuzzy Deduplication Techniques](https://www.emergentmind.com/topics/fuzzy-deduplication)):

**Common algorithms:**
| Algorithm | Best For | How It Works |
|-----------|----------|-------------|
| Levenshtein Distance | Filenames, short strings | Count edits to transform one string to another |
| Jaro-Winkler | Names, titles | Weighted by prefix similarity |
| MinHash + LSH | Large document sets | Estimate Jaccard similarity via locality-sensitive hashing |
| Perceptual Hashing | Images | Hash visual appearance, not bytes (similar images = similar hashes) |
| TF-IDF + Cosine | Document content | Compare term frequency vectors |

**Hybrid pipeline** (modern best practice):
1. Coarse filter with efficient indices (Bloom filters, MinHash-LSH, KNN)
2. Fine-grained matching with domain-informed similarity scoring
3. Human review for borderline cases

Source: [Airbyte - Data Deduplication Methods](https://airbyte.com/data-engineering-resources/data-deduplication)

### Block-Level Deduplication

Divides files into fixed or variable-sized blocks, stores only unique blocks. Finds partial duplicates and shared content across files. More common in backup/storage systems than user-facing tools ([LatentView](https://www.latentview.com/glossary/data-deduplication/)).

---

## 5. Archive/Cleanup Heuristics

### Identifying Stale Files

The naive approach (checking `lastmodifieddate`) is unreliable because automated processes -- search indexers, backup tools, antivirus -- update this attribute without any human involvement ([Varonis](https://www.varonis.com/blog/4-secrets-for-archiving-stale-data-efficiently)).

**Better approach -- four criteria** (from Varonis):

1. **The right metadata:** Correlate multiple metadata streams -- not just modification date, but who touched it last, who has access, whether it contains sensitive data

2. **Audit trail of human user activity:** Track actual user access events, not filesystem timestamps. An audit trail gives you known changes by human users vs. automated process touches

3. **Granular data selection:** Different data sets need different archiving rules. HR data vs. Finance data vs. Legal data all have different retention requirements. Pivot on: last access date, content sensitivity (PII, PCI, HIPAA), user profile (C-level vs. help desk)

4. **Automation:** Stale data identification must not consume more IT resources than it saves. Automated policies that flag/archive/delete based on metadata are essential

**Practical age thresholds** (common defaults):
- Downloads folder: 30-90 days untouched
- Temp files (.tmp, .crdownload, .part): 24 hours
- Desktop clutter: 7-30 days
- Project archives: 6-12 months after last access
- Temporary project files: 2 years
- Old email attachments: 3 years

Source: [Microsoft TechCommunity](https://techcommunity.microsoft.com/t5/storage-at-microsoft/dealing-with-stale-data-on-file-servers/ba-p/423837)

**Key statistic:** ~70% of unstructured data becomes stale within 90 days of creation ([Varonis](https://www.varonis.com/blog/4-secrets-for-archiving-stale-data-efficiently)).

### Archive vs. Delete Decision Tree

```
Is the file a known temp type (.tmp, .crdownload, .part, .DS_Store)?
  YES -> Delete after 24 hours
  NO  -> Continue

Has any human accessed this file in the last N days?
  YES -> Keep active
  NO  -> Continue

Does the file contain sensitive/regulated data (PII, financial, legal)?
  YES -> Archive with retention policy
  NO  -> Continue

Is it a duplicate of another file?
  YES -> Delete the duplicate (keep the original in the better location)
  NO  -> Continue

Is it in a project that has a clear end date?
  PAST END DATE -> Archive the whole project folder
  NO  -> Continue

Default: Archive if untouched >6 months, flag for review if >1 year
```

---

## 6. Safe Reorganization

### Principles for Not Breaking Things

The fundamental rule: **move first, edit second** ([TheLinuxCode](https://thelinuxcode.com/git-move-files-practical-renames-refactors-and-history-preservation-in-2026/)).

1. Move file(s) only -- commit the move
2. Update imports/paths/references -- commit those edits separately
3. Two commits, not one. Git detects renames based on content similarity; mixing moves with edits degrades rename detection

### Git History Preservation

`git mv` is preferred over manual `mv` + `git add` because it explicitly stages deletion and addition as a single rename, making it easier for Git to detect the relationship between old and new paths.

```bash
git mv services/billing apps/billing
git commit -m "Move billing service to apps/"
# Then update import paths in a second commit
```

Verify history follows with:
```bash
git log --follow path/to/new/file
git blame -C -M path/to/new/file
```

Source: [TheLinuxCode](https://thelinuxcode.com/git-move-files-practical-renames-refactors-and-history-preservation-in-2026/)

### Symlinks as Safety Net

Create symlinks at old locations pointing to new locations during transition periods. This prevents broken references while gradually updating consumers.

```bash
# After moving, leave a breadcrumb
ln -s /new/path/to/module /old/path/to/module
```

Git stores symlinks as special files containing the target path. Use relative paths for portability across machines.

### Simulation/Dry-Run Pattern

Every serious file organization tool implements this:
- **organize-cli:** `organize sim` runs the full rule engine without touching any files
- **Hazel:** Preview mode shows what would happen
- **rsync:** `-n` (dry-run) flag
- **Git:** `--dry-run` flag on many commands

### Undo/Rollback Logging

The local LLM file organizer pattern records every `shutil.move` to a JSON log before execution:

```python
class UndoManager:
    def start_session(self):
        session = {
            "id": str(uuid4()),
            "timestamp": datetime.now().isoformat(),
            "operations": []
        }
        # ...

    def record_move(self, source, destination):
        operation = {
            "type": "move",
            "source": str(source),
            "destination": str(destination),
            "timestamp": datetime.now().isoformat()
        }
        # Written to disk BEFORE the actual move
```

Source: [Medium - Using Local LLMs to Organize Files](https://medium.com/data-science-collective/using-local-llms-to-organize-messy-files-a-technical-deep-dive-79433165f4fb)

### Conflict Resolution Strategies

organize-cli implements five conflict modes when a destination already exists:
| Mode | Behavior |
|------|----------|
| `skip` | Do nothing, keep existing file |
| `overwrite` | Replace existing file |
| `trash` | Move existing file to trash, then place new file |
| `rename_new` | Rename the incoming file (e.g., `file 2.pdf`) |
| `rename_existing` | Rename the existing file, place new file at destination |

Source: [organize actions docs](https://tfeldmann.github.io/organize/actions/)

---

## 7. "Zero Inbox" Applied to Folders

The GTD (Getting Things Done) methodology adapted to file organization. The core principle: the inbox stores files only TEMPORARILY; they must be processed and moved to their permanent home ([Getting Things Done](https://gettingthingsdone.com/wp-content/uploads/2014/10/GettingYourInboxToZero.pdf)).

### The Folder Structure

```
~/
  Inbox/           # Landing zone (Downloads, email attachments, etc.)
  Action/          # Files you need to work on
  Waiting/         # Files blocked on someone else
  Reference/       # Permanent storage, organized by topic
  Archive/         # Completed projects, old references
  Trash/           # Staging for deletion (review before purge)
```

### The Processing Workflow

Applied to files the same way as email ([GTD Inbox Zero](https://www.gtd.be/en/what-is-gtd/core-principles/inbox-zero)):

1. **Pick up a file from Inbox**
2. **Can you delete it?** -> Delete
3. **Does it require action?**
   - Takes <2 minutes? -> Do it now
   - Takes longer? -> Move to `Action/`
   - Waiting on someone? -> Move to `Waiting/`
4. **Is it reference material?** -> File in `Reference/` under the right category
5. **Is it from a completed project?** -> Move to `Archive/`

### Key Practices

- **Process inbox at least once per week** to prevent buildup
- **Use search over folders:** With modern OS search (Spotlight, Everything), a flat archive with good filenames is often faster than deep folder hierarchies
- **2-minute rule:** If classifying a file takes less than 2 minutes, do it immediately rather than leaving it in the inbox
- **Archive liberally:** When in doubt, archive rather than delete. Storage is cheap; lost files are expensive.

Source: [Bill Zipp](https://billzipp.com/5-folders-the-simple-system-for-getting-your-email-inbox-to-zero/), [GTD](https://gettingthingsdone.com/wp-content/uploads/2014/10/2017-Getting-Your-Inbox-to-Zero.pdf)

---

## 8. Incremental vs. Big-Bang Organization

### Big-Bang Reorganization

Everything changes at once. One afternoon, you restructure your entire file system.

**When it works:**
- Small total file volume
- Fresh start (new machine, new project)
- You have robust undo/rollback capability
- Everything is backed up

**Risks:**
- If something goes wrong, the blast radius is total
- Hard to verify correctness across thousands of files
- High cognitive load -- you are making every decision at once
- Breaks muscle memory for existing paths

Source: [WalkMe - Incremental vs Big Bang](https://change.walkme.com/incremental-change/), [XB Software](https://xbsoftware.com/blog/big-bang-or-gradual-data-migration/)

### Incremental (Gradual) Organization

Changes happen in phases, one folder or category at a time.

**Strategy:**
1. Set up the target structure (empty folders for the new organization)
2. Route all NEW files through the new system immediately
3. Migrate existing files category-by-category over days/weeks
4. Leave symlinks at old locations during transition
5. Remove old structure only after confirming nothing still references it

**Advantages:**
- Lower risk -- problems are caught early and affect only one category
- Allows learning and adjustment of the organizational scheme
- Less disruptive to daily workflow
- Can be paused and resumed

**Best practice pattern:**
- Week 1: Set up new folder structure, configure rules for ~/Downloads only
- Week 2: Process ~/Desktop (highest visibility folder)
- Week 3: Tackle ~/Documents one subfolder at a time
- Week 4+: Handle deeper archives, old project directories

Source: [Migration Center](https://migration-center.com/blog/large-content-migration-strategies-big-bang-vs-phased-approach/)

### Hybrid Approach (Recommended)

Use big-bang for the structural skeleton and incremental for the actual file migration:

1. **Big-bang:** Create the new folder hierarchy, set up automation rules, configure watchers
2. **Incremental:** Files flow through the new system one at a time as they arrive or as you touch them
3. **Background sweep:** Periodically run batch rules against old directories to migrate untouched files

This matches what Dropbox found in production: "Because most users consider file organization a very personal and custom task, we focused on assisting rather than replacing manual organization patterns" ([Dropbox Tech Blog](https://dropbox.tech/machine-learning/smart-move-ml-ai-file-organization-automation)).

---

## Tool Comparison Summary

| Tool | Platform | Approach | Strengths | Limitations |
|------|----------|----------|-----------|-------------|
| [organize-cli](https://organize.readthedocs.io/) | Cross-platform | YAML rules | Most flexible open-source option, simulation mode, Python extensibility, duplicate detection | Requires CLI comfort |
| [Hazel](https://www.noodlesoft.com/manual/hazel/hazel-overview/) | macOS | GUI rules | User-friendly, deep macOS integration, watches folders in real-time | macOS only, commercial |
| [File Juggler](https://www.filejuggler.com/) | Windows | GUI rules | Reads PDF/DOCX content, good condition builder | Windows only, commercial |
| [LlamaFS](https://github.com/iyaja/llama-fs) | Cross-platform | LLM (Llama 3) | Content-aware, image/audio understanding, batch + watch modes | Requires Ollama/Groq setup |
| [AI FileSorter](https://github.com/hyperfield/ai-file-sorter) | Cross-platform | Local/cloud LLM | GUI, preview before apply, multiple LLM backends | Newer, less battle-tested |
| [Dropbox Smart Move](https://dropbox.tech/machine-learning/smart-move-ml-ai-file-organization-automation) | Dropbox web | Production ML | Trained on millions of examples, human-in-the-loop | Dropbox ecosystem only |

---

## Key Takeaways for Building an Organizer

1. **Extension is just the first pass.** Content analysis is where real value lives, but it is 10-100x more expensive computationally.

2. **Filename patterns catch 60-70% of cases cheaply.** Dropbox found their simple filename similarity heuristic had 94% accuracy for high-confidence suggestions vs. 90% for their trained ML model.

3. **Human-in-the-loop is essential.** Organization is deeply personal. Always preview before applying, never auto-execute without explicit approval.

4. **Simulation mode is non-negotiable.** Every tool of consequence has it. Build it first.

5. **Undo logging must be written before the operation.** Same principle as write-ahead logging in databases.

6. **Siblings reveal intent better than parents.** What files are already in a folder tells you more about what belongs there than the folder name alone.

7. **Stale data detection requires human-access auditing**, not just modification timestamps.

8. **Incremental beats big-bang** for real-world adoption. Set up the rules, then let files flow through organically.
