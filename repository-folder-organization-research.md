# Repository & Codebase Folder Organization: Deep Research

Created: April 20, 2026 9:47 AM EDT

---

## Table of Contents

1. [Language-Specific Conventions](#1-language-specific-conventions)
2. [Monorepo vs Polyrepo](#2-monorepo-vs-polyrepo)
3. [README & Docs Placement](#3-readme--docs-placement)
4. [Config File Organization](#4-config-file-organization)
5. [Asset Organization](#5-asset-organization)
6. [Screaming Architecture](#6-screaming-architecture)
7. [Real Examples from Major Projects](#7-real-examples-from-major-projects)
8. [Automated Linting for Structure](#8-automated-linting-for-structure)

---

## 1. Language-Specific Conventions

### Python

The modern Python project structure has converged around the **src layout** with `pyproject.toml` as the single configuration file ([Python Packaging User Guide](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)).

**Canonical src layout:**

```
my-project/
├── src/
│   └── my_package/
│       ├── __init__.py
│       ├── __main__.py
│       ├── core.py
│       └── utils.py
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   └── test_utils.py
├── docs/
├── pyproject.toml
├── README.md
└── LICENSE
```

**Why src layout over flat layout:**

- Tests run against the *installed* version of your package, not the working directory copy. This catches packaging bugs that users would hit but you wouldn't during development ([pyOpenSci Python Package Guide](https://www.pyopensci.org/python-package-guide/package-structure-code/python-package-structure.html)).
- Prevents accidental imports of the local package, which is a common source of "works on my machine" bugs.
- The flat layout (package at root) is fine for scripts and small projects, but becomes fragile at scale.

**pyproject.toml is the norm:** By 2025, `setup.py` and `setup.cfg` are legacy. `pyproject.toml` centralizes build configuration, dependencies, and tool settings (for linters, formatters, etc.) in one file. Build backends like **Hatchling**, **Poetry-core**, **PDM-backend**, and **Flit-core** all read from it ([Python Packaging User Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/), [Poetry docs](https://python-poetry.org/docs/pyproject/)).

**Key conventions:**

- Use `tests/` at the top level mirroring your package structure ([Real Python](https://realpython.com/ref/best-practices/project-layout/))
- Put CLI entry points in `__main__.py`
- Use `docs/` for Sphinx/MkDocs documentation source
- Never put importable code at the repository root

---

### JavaScript / TypeScript

JS/TS projects have more variation, but dominant patterns have emerged ([DEV Community](https://dev.to/pramod_boda/recommended-folder-structure-for-nodets-2025-39jl), [DEV Community - React 2025](https://dev.to/pramod_boda/recommended-folder-structure-for-react-2025-48mc)).

**Node.js/Express (backend):**

```
my-api/
├── src/
│   ├── config/           # env vars, database config
│   ├── modules/          # feature-based (users/, auth/, orders/)
│   │   └── users/
│   │       ├── users.controller.ts
│   │       ├── users.service.ts
│   │       ├── users.model.ts
│   │       ├── users.routes.ts
│   │       └── users.test.ts
│   ├── middleware/
│   ├── utils/
│   └── index.ts
├── tests/                # integration / e2e tests
├── package.json
├── tsconfig.json
└── README.md
```

**React / Next.js (frontend):**

The [Bulletproof React](https://github.com/alan2207/bulletproof-react/blob/master/docs/project-structure.md) structure (34.9k GitHub stars) has become the de facto reference:

```
src/
├── app/              # routing, providers, entrypoint
│   ├── routes/
│   ├── app.tsx
│   └── provider.tsx
├── assets/           # images, fonts, static files
├── components/       # shared components
├── config/           # global config, exported env vars
├── features/         # feature-based modules (the core)
│   └── discussions/
│       ├── api/
│       ├── components/
│       ├── hooks/
│       ├── stores/
│       ├── types/
│       └── utils/
├── hooks/            # shared hooks
├── lib/              # preconfigured libraries (axios, etc.)
├── stores/           # global state
├── testing/          # test utilities and mocks
├── types/            # shared TypeScript types
└── utils/            # shared utility functions
```

**Key principle from Bulletproof React:** Features should NOT import from other features. Compose features at the app layer. Enforce this with ESLint `import/no-restricted-paths` rules.

**File naming:** Use **kebab-case** (`my-component.tsx`) to avoid cross-OS case-sensitivity issues ([DEV Community](https://dev.to/pramod_boda/recommended-folder-structure-for-nodets-2025-39jl)).

---

### Go

Go has the most opinionated community conventions, anchored by the [golang-standards/project-layout](https://github.com/golang-standards/project-layout) repo (55.8k stars) and the official [Go module layout guide](https://go.dev/doc/modules/layout).

**Standard Go project layout:**

```
my-service/
├── cmd/                  # application entry points
│   ├── api/
│   │   └── main.go
│   └── worker/
│       └── main.go
├── internal/             # private code (compiler-enforced)
│   ├── auth/
│   ├── storage/
│   └── transport/
├── pkg/                  # public reusable libraries
│   ├── logger/
│   └── crypto/
├── api/                  # API specs (OpenAPI, proto files)
├── configs/              # config file templates
├── deployments/          # docker-compose, k8s manifests
├── scripts/              # build/install/analysis scripts
├── build/                # packaging and CI configs
│   ├── ci/
│   └── package/
├── docs/
├── tools/                # supporting tools for the project
├── examples/
├── third_party/          # forked or imported external code
├── assets/
├── go.mod
├── go.sum
└── README.md
```

**Critical Go-specific rules:**

- **`internal/`** is enforced by the Go compiler -- code inside it can only be imported by the parent project. This is where all private business logic goes ([Go module layout guide](https://go.dev/doc/modules/layout)).
- **`cmd/`** each subdirectory is a separate binary. The directory name becomes the binary name.
- **Start small:** For simple projects, just `main.go` + `go.mod`. Add structure only as the project grows ([Alex Edwards](https://www.alexedwards.net/blog/11-tips-for-structuring-your-go-projects)).
- **`pkg/` is debated:** Some argue it adds unnecessary nesting. The Go team itself does not use `pkg/` in the standard library. Use it only if you genuinely have reusable public packages.

---

### Rust

Rust structure is governed by Cargo conventions and grows into workspaces for larger projects ([The Cargo Book](https://doc.rust-lang.org/cargo/guide/project-layout.html), [The Rust Programming Language](https://doc.rust-lang.org/book/ch14-03-cargo-workspaces.html)).

**Single crate (standard layout):**

```
my-crate/
├── Cargo.toml
├── Cargo.lock
├── src/
│   ├── lib.rs            # library root
│   ├── main.rs           # binary root
│   └── module_name/
│       └── mod.rs
├── benches/              # benchmarks
├── examples/             # example programs
├── tests/                # integration tests
└── README.md
```

**Workspace (multi-crate monorepo):**

```
my-workspace/
├── Cargo.toml            # [workspace] definition
├── Cargo.lock            # shared across all crates
├── crates/
│   ├── core/
│   │   ├── Cargo.toml
│   │   └── src/lib.rs
│   ├── api/
│   │   ├── Cargo.toml
│   │   └── src/main.rs
│   └── cli/
│       ├── Cargo.toml
│       └── src/main.rs
└── README.md
```

**Key Rust conventions:**

- Cargo enforces `src/lib.rs` for libraries and `src/main.rs` for binaries
- `tests/` is for integration tests; unit tests go *inside* the source files they test (using `#[cfg(test)]` modules)
- Workspaces share a single `Cargo.lock` and output directory, reducing duplicate compilation by 40-60% ([Leapcell](https://leapcell.io/blog/how-to-organize-a-large-scale-rust-project-effectively))
- Use `cargo-deny` for license checking across workspace dependencies

---

## 2. Monorepo vs Polyrepo

### When to use which

| Factor | Monorepo | Polyrepo |
|--------|----------|----------|
| Team structure | One team, or tightly coupled teams | Independent teams with separate release cycles |
| Code sharing | Heavy cross-project sharing | Minimal sharing, consumed via published packages |
| CI/CD | Unified pipeline, build affected packages only | Independent pipelines per repo |
| Dependency management | Single lockfile, deduplication | Each repo manages its own deps |
| Onboarding | One repo to clone, one set of tools | Need to understand which repos to clone |
| Scale risk | Repo size, slow git operations at extreme scale | Dependency hell, version drift across repos |

([DEV Community - Monorepo vs Polyrepo 2025](https://dev.to/md-afsar/monorepo-vs-polyrepo-which-one-should-you-choose-in-2025-g77))

### Tool Comparison: Nx vs Turborepo vs Lerna

**Turborepo** (by Vercel, written in Rust):
- Simplest setup, lowest learning curve
- `turbo.json` defines task pipeline (build, test, lint) with dependency graph
- Remote caching via Vercel out of the box
- Best for: JS/TS projects, especially Next.js/Vercel ecosystems

```
my-turborepo/
├── apps/
│   ├── web/               # Next.js frontend
│   ├── mobile/            # React Native
│   └── api/               # Express backend
├── packages/
│   ├── ui/                # shared component library
│   ├── config-eslint/     # shared ESLint config
│   ├── config-typescript/ # shared tsconfig
│   └── shared-types/      # shared TS types
├── turbo.json
├── package.json
└── pnpm-workspace.yaml
```

([Turborepo docs - Structuring a Repository](https://turborepo.dev/docs/crafting-your-repository/structuring-a-repository))

**Nx** (by Nrwl):
- Most feature-rich: code generators, dependency graph visualization, affected commands
- Plugin ecosystem for React, Angular, Node, Go, etc.
- Enforces module boundaries via tags and `@nx/enforce-module-boundaries` ESLint rule
- Best for: large enterprises, mixed-tech monorepos, teams wanting guardrails

```
my-nx-workspace/
├── apps/
│   ├── store/
│   └── admin/
├── libs/
│   ├── products/
│   │   ├── data-access/
│   │   ├── feature-list/
│   │   └── ui/
│   └── shared/
│       ├── ui/
│       └── utils/
├── tools/
├── nx.json
└── package.json
```

Nx recommends the **80/20 rule**: ~80% of code in `libs/`, ~20% in `apps/`. Apps are thin shells that compose libraries ([Nx docs - Folder Structure](https://nx.dev/docs/concepts/decisions/folder-structure)).

**Lerna** (v6+ delegates to Nx for task running):
- Now focused on **versioning and npm publishing**
- Best for: open-source library authors publishing multiple packages to npm
- Use Lerna for versioning + Nx for building/caching

([DEV Community - Monorepo Tools Comparison](https://dev.to/_d7eb1c1703182e3ce1782/monorepo-tools-comparison-turborepo-vs-nx-vs-lerna-in-2025-15a6), [Aviator Blog - Top 5 Monorepo Tools](https://www.aviator.co/blog/monorepo-tools/))

**The bottom line:** The difference between Turborepo and Nx is much smaller than the difference between either tool and having no monorepo tooling at all.

---

## 3. README & Docs Placement

### Universal conventions

Based on [Folder-Structure-Conventions](https://github.com/kriasoft/Folder-Structure-Conventions/blob/master/README.md) and widely adopted practices:

```
project-root/
├── README.md              # ALWAYS at root, entry point for the project
├── LICENSE                 # at root, standard naming (no extension or .md)
├── CHANGELOG.md            # at root (or auto-generated)
├── CONTRIBUTING.md         # at root
├── CODE_OF_CONDUCT.md      # at root
├── docs/                   # extended documentation
│   ├── architecture.md     # system design docs
│   ├── api.md              # API documentation
│   ├── deployment.md       # deployment guides
│   └── images/             # images used in docs
├── scripts/                # build, deploy, utility scripts
├── tests/ or __tests__/    # test files
└── src/                    # source code
```

### Key placement rules

**README.md:**
- Always at the repository root. GitHub/GitLab renders it as the landing page.
- Can also exist in subdirectories to explain that section (e.g., `src/README.md`, `docs/README.md`).
- Should include a "Repository Structure" section explaining the folder layout for contributors ([freeCodeCamp](https://www.freecodecamp.org/news/how-to-structure-your-readme-file/)).

**docs/:**
- For Sphinx/MkDocs/Docusaurus source files, use `docs/`
- GitHub Pages can serve directly from `docs/` on the main branch
- API reference docs often auto-generated into `docs/api/`

**scripts/:**
- Build scripts, CI helpers, migration scripts, dev utilities
- Use descriptive names: `scripts/setup-dev.sh`, `scripts/run-migrations.sh`

**tests/:**
- Top-level `tests/` for integration/e2e tests
- Unit tests either colocated with source (JS/TS convention) or in `tests/` mirroring `src/` (Python convention)
- Subtypes: `tests/unit/`, `tests/integration/`, `tests/e2e/`

---

## 4. Config File Organization

### The root directory problem

Modern JS projects in particular suffer from "config file explosion." A typical project root can contain 15+ config files:

```
.eslintrc.js
.prettierrc
.babelrc
.editorconfig
.env
.env.local
.gitignore
.gitattributes
.npmrc
.nvmrc
.husky/
jest.config.js
tsconfig.json
next.config.js
tailwind.config.js
postcss.config.js
commitlint.config.js
lint-staged.config.js
```

This problem is documented in the Node.js tooling group's issue [#79: "The creeping scourge of tooling config files in project root directories"](https://github.com/nodejs/tooling/issues/79), which received 600+ thumbs-up reactions.

### Strategies for taming config files

**1. Consolidate into `pyproject.toml` / `package.json` where possible:**
Many tools support embedding config in your main manifest. For Python, `pyproject.toml` can hold settings for `[tool.ruff]`, `[tool.pytest]`, `[tool.mypy]`, etc. For JS, `package.json` supports `"eslintConfig"`, `"prettier"`, `"jest"`, `"browserslist"`, etc.

**2. The `.config/` directory proposal:**
The Node.js tooling group proposed moving tool configs into a `.config/` subdirectory. Many tools now support this:
```
.config/
├── eslint.config.js
├── prettier.config.js
├── commitlint.config.js
└── lint-staged.config.js
```

**3. Categorize by purpose:**
```
config/                    # application config (runtime)
├── default.json
├── production.json
└── test.json
build/                     # build tool configs
├── webpack.config.js
└── babel.config.js
```

**4. Accept strategic root-level files:**
Some configs *must* be at root for tool discovery (`package.json`, `tsconfig.json`, `go.mod`, `Cargo.toml`). Others are good candidates for consolidation.

**5. Use `.gitattributes` to collapse in GitHub:**
Mark config files as "linguist-generated" so GitHub collapses them in PRs:
```gitattributes
*.config.js linguist-generated
```

---

## 5. Asset Organization

### Frontend assets

The dominant pattern is a dedicated `assets/` directory, either at the project root or within `src/` ([DEV Community - Clean Frontend Folder Structure](https://dev.to/yasirawan4831/a-clean-frontend-folder-structure-every-developer-should-know-4j81)):

```
src/assets/
├── images/
│   ├── logos/
│   ├── icons/
│   └── backgrounds/
├── fonts/
│   ├── inter/
│   └── fira-code/
├── styles/                # global CSS/SCSS
│   ├── variables.css
│   ├── reset.css
│   └── globals.css
└── videos/
```

### Static vs dynamic assets

| Type | Location | Reason |
|------|----------|--------|
| Build-processed assets (imports in code) | `src/assets/` | Bundler hashes filenames, tree-shakes unused |
| Directly served static files | `public/` or `static/` | Served as-is, no processing |
| User-uploaded content | External (S3, CDN) | Not in repo at all |

### Generated / build output

Generated files should NEVER be committed to the repository. Standard output directories:

| Language/Tool | Output Directory | gitignored |
|---------------|------------------|------------|
| Python | `dist/`, `build/`, `*.egg-info/` | Yes |
| JS (webpack/vite) | `dist/`, `build/`, `.next/` | Yes |
| Go | `bin/` | Yes |
| Rust | `target/` | Yes |
| General | `out/`, `output/` | Yes |

---

## 6. Screaming Architecture

### The concept

Coined by Robert "Uncle Bob" Martin, "screaming architecture" means your top-level folder structure should tell you what the system *does*, not what framework it uses ([Clean Coder Blog](https://blog.cleancoder.com/uncle-bob/2011/09/30/Screaming-Architecture.html)).

> "When you look at the top-level directory structure, and the source files in the highest level package, do they scream: Health Care System, or Accounting System, or Inventory Management System? Or do they scream: Rails, or Spring/Hibernate, or ASP?"

### Anti-pattern vs screaming pattern

**Technical-first (anti-pattern) -- screams "I am a web framework":**
```
src/
├── controllers/
├── models/
├── views/
├── services/
├── repositories/
├── middleware/
└── utils/
```

**Domain-first (screaming) -- screams "I am an e-commerce system":**
```
src/
├── orders/
│   ├── place-order.ts
│   ├── cancel-order.ts
│   └── order.model.ts
├── payments/
│   ├── process-payment.ts
│   └── payment.model.ts
├── shipping/
│   ├── calculate-rates.ts
│   └── tracking.ts
├── customers/
│   ├── register.ts
│   └── customer.model.ts
└── shared/
    ├── database.ts
    └── email.ts
```

### Feature-Sliced Design (FSD)

[Feature-Sliced Design](https://feature-sliced.design/docs/get-started/overview) is a formal methodology that operationalizes screaming architecture for frontends. It defines 7 strict layers:

```
app/          # routing, providers, global setup
pages/        # full pages (compose widgets/features)
widgets/      # self-contained UI chunks (e.g., Header, Sidebar)
features/     # user-facing actions (add-to-cart, login)
entities/     # business objects (user, product, order)
shared/       # detached reusable code (ui kit, api client)
```

**Rules:**

1. A layer can only import from layers strictly *below* it
2. Each slice (e.g., `features/add-to-cart/`) contains segments: `ui/`, `model/`, `api/`, `lib/`
3. Slices on the same layer cannot import from each other
4. FSD has its own linter: [Steiger](https://github.com/feature-sliced/steiger) for automated enforcement

**Practical benefit:** A new developer can look at the `features/` folder and immediately understand every user-facing capability the app provides.

---

## 7. Real Examples from Major Projects

### VS Code (TypeScript, 184k stars)

VS Code uses a deeply layered architecture under `src/vs/` with strict dependency rules ([VS Code Wiki - Source Code Organization](https://github.com/microsoft/vscode/wiki/source-code-organization)):

```
vscode/
├── src/
│   └── vs/
│       ├── base/              # general utilities, UI building blocks
│       ├── platform/          # service injection, base services
│       ├── editor/            # Monaco editor core
│       │   ├── common/
│       │   ├── browser/
│       │   ├── contrib/       # editor extensions (shipped in both VS Code and standalone)
│       │   └── standalone/    # standalone editor additions
│       ├── workbench/         # the full IDE experience
│       │   ├── api/           # extension host API
│       │   ├── browser/
│       │   ├── contrib/       # workbench features (search, git, debug, terminal)
│       │   ├── services/
│       │   └── common/
│       ├── code/              # Electron desktop app entry point
│       └── server/            # remote dev server entry point
├── extensions/                # built-in extensions (JS, TS, Python, etc.)
├── build/                     # build scripts
├── test/
└── resources/                 # icons, platform-specific resources
```

**Key design decisions:**

- Code within each layer is subdivided by **target environment**: `common/` (pure JS), `browser/` (Web APIs), `node/` (Node.js APIs), `electron-main/`, `electron-browser/`
- `workbench/contrib/` features have a strict rule: nothing outside `contrib/` may depend on anything inside `contrib/`
- Services use constructor-based dependency injection

### Linux Kernel (C, the canonical systems project)

The kernel source tree is the gold standard for systems-level organization ([DEV Community - Linux Kernel Source Tree](https://dev.to/darshan_rathod/anatomy-of-the-linux-kernel-source-tree-3hnb)):

```
linux/
├── arch/          # architecture-specific (x86/, arm/, riscv/)
├── block/         # block device layer
├── crypto/        # cryptographic API
├── drivers/       # hardware drivers (the LARGEST directory)
│   ├── usb/
│   ├── net/
│   ├── gpu/
│   └── ... (dozens more)
├── fs/            # file systems (ext4, xfs, btrfs, VFS)
├── include/       # kernel-wide headers
├── init/          # boot/initialization code (start_kernel())
├── ipc/           # inter-process communication
├── kernel/        # core (scheduler, interrupts, signals)
├── lib/           # utility functions (string, compression)
├── mm/            # memory management (paging, virtual memory)
├── net/           # networking stack (TCP, UDP, sockets)
├── scripts/       # build/config scripts
├── security/      # SELinux, AppArmor
├── sound/         # ALSA audio
└── tools/         # userspace tools (perf, bpf, selftests)
```

**Key design decisions:**

- Subsystem-first organization at the top level
- `arch/` isolates platform-dependent code cleanly
- `drivers/` organized by hardware type, not by manufacturer
- `include/` provides the "API surface" for cross-subsystem communication
- `Documentation/` (not shown) contains extensive docs organized by subsystem

### Next.js App Router (the modern JS framework structure)

The official Next.js project structure uses the filesystem for routing ([Next.js docs](https://nextjs.org/docs/app/getting-started/project-structure)):

```
my-next-app/
├── src/
│   ├── app/                     # App Router (filesystem routing)
│   │   ├── layout.tsx           # root layout
│   │   ├── page.tsx             # home page (/)
│   │   ├── dashboard/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx         # /dashboard
│   │   │   └── settings/
│   │   │       └── page.tsx     # /dashboard/settings
│   │   └── api/
│   │       └── users/
│   │           └── route.ts     # API route
│   ├── components/
│   ├── lib/
│   └── hooks/
├── public/                      # static assets served at /
├── next.config.js
├── package.json
└── tsconfig.json
```

### React (monorepo, library)

React itself uses a monorepo with `packages/`:

```
react/
├── packages/
│   ├── react/                # core React
│   ├── react-dom/            # DOM renderer
│   ├── react-reconciler/     # reconciliation algorithm
│   ├── react-server/         # server components
│   ├── scheduler/            # cooperative scheduling
│   └── shared/               # shared utilities
├── fixtures/                  # test apps
├── scripts/                   # build scripts
└── compiler/                  # React Compiler
```

---

## 8. Automated Linting for Structure

### eslint-plugin-project-structure

The most comprehensive tool for JS/TS projects ([GitHub](https://github.com/Igorkowalski94/eslint-plugin-project-structure), [npm](https://www.npmjs.com/package/eslint-plugin-project-structure)).

**Installation:**
```bash
npm i -D eslint-plugin-project-structure
```

**Configuration example (eslint.config.js):**
```js
import { projectStructurePlugin } from "eslint-plugin-project-structure";

export default [
  {
    plugins: { "project-structure": projectStructurePlugin },
    rules: {
      "project-structure/folder-structure": ["error", {
        structure: {
          children: [
            {
              name: "src",
              children: [
                { name: "features", children: [{ name: "{PascalCase}" }] },
                { name: "components", children: [{ name: "{PascalCase}" }] },
                { name: "hooks", children: [{ name: "{camelCase}.ts" }] },
                { name: "utils", children: [{ name: "{camelCase}.ts" }] },
              ]
            }
          ]
        }
      }],
      "project-structure/independent-modules": ["error", {
        modules: [
          { name: "src/features/*", allowImportsFrom: ["src/shared/**"] }
        ]
      }],
    }
  }
];
```

**Capabilities:**

- Define folder structure rules with recursion support
- Enforce naming conventions (PascalCase, camelCase, kebab-case)
- Create independent module boundaries (no cross-feature imports)
- File composition rules (what files a folder must/can contain)
- Support for path aliases via tsconfig

### FoldersLint

A simpler alternative focused on directory structure only ([GitHub](https://github.com/denisraslov/folderslint)):

```bash
npm i -D folderslint
```

**.folderslintrc:**
```json
{
  "root": "src",
  "rules": [
    "components/*",
    "components/*/index.ts",
    "components/*/styles.css",
    "features/*",
    "features/*/api/*",
    "features/*/components/*",
    "features/*/hooks/*"
  ]
}
```

Integrates with **lint-staged** to only check files changed in a commit.

### Steiger (Feature-Sliced Design)

The official FSD linter ([GitHub](https://github.com/feature-sliced/steiger)):

```bash
npx steiger src
```

Checks that your project follows FSD layer ordering, slice isolation, and segment conventions automatically.

### eslint-plugin-folders

Lighter-weight option that enforces file/folder naming conventions via regex ([npm](https://www.npmjs.com/package/eslint-plugin-folders)):

```json
{
  "plugins": ["folders"],
  "rules": {
    "folders/match-regex": [2, "^[a-z-]+$", "/src/"]
  }
}
```

### ESLint import/no-restricted-paths

Built into `eslint-plugin-import`, this is the most commonly used rule for enforcing architectural boundaries. From the Bulletproof React docs:

```js
// Prevent cross-feature imports
"import/no-restricted-paths": ["error", {
  zones: [
    {
      target: "./src/features/auth",
      from: "./src/features",
      except: ["./auth"]
    },
    // Enforce unidirectional flow: shared -> features -> app
    {
      target: "./src/features",
      from: "./src/app"
    },
    {
      target: "./src/shared",
      from: ["./src/features", "./src/app"]
    }
  ]
}]
```

### Beyond JavaScript: other ecosystems

| Language | Tool | Purpose |
|----------|------|---------|
| Rust | `cargo-deny` | License checking, dependency auditing |
| Go | `internal/` directory | Compiler-enforced visibility boundary |
| Python | `import-linter` | Enforce architectural layers via contracts |
| General | `.editorconfig` | Consistent formatting rules across editors |
| General | Pre-commit hooks | Run structure checks on every commit |

---

## Summary: Universal Principles

Regardless of language or project type, these principles recur across all well-structured codebases:

1. **Separate source from configuration.** Source code belongs in `src/` (or language-equivalent). Config lives at root or in a dedicated config directory.

2. **Group by domain, not by technical role.** Prefer `orders/`, `payments/`, `shipping/` over `controllers/`, `models/`, `services/`. Technical grouping should happen *within* domain folders.

3. **Enforce boundaries.** Whether it is Go's `internal/`, ESLint's `import/no-restricted-paths`, Nx's module boundary rules, or FSD's strict layering, the best projects use tooling to prevent architectural erosion.

4. **Keep generated output out of the repo.** Build artifacts, compiled files, and transpiler output go in gitignored directories (`dist/`, `build/`, `target/`, `bin/`).

5. **Tests live near what they test, or mirror the source tree.** JS/TS leans toward colocation (`Component.test.tsx` next to `Component.tsx`). Python and Go lean toward a separate `tests/` directory mirroring `src/`.

6. **README at root is mandatory.** Additional READMEs in subdirectories explain subsystems. Extended docs go in `docs/`.

7. **Start simple, add structure as you grow.** A single-file project does not need 15 directories. Add structure when the team or codebase demands it.

8. **Automate structure enforcement.** Use linting tools, pre-commit hooks, and CI checks to prevent structural drift. Documenting rules is necessary but not sufficient -- they must be machine-enforced.
