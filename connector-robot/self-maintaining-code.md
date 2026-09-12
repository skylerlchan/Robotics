# Self-Maintaining Code: Is It Real, Who Works On It, Where It's Going

**Created:** May 31, 2026

This is the "self-maintenance code, if that's a thing" idea from [the design doc](../../../../.gstack/projects/Robotics/skyler-main-design-20260530-152518.md), researched directly. Short answer: yes, it's real — but "self-maintaining codebase" means two different things, and conflating them hides where the hard part actually is.

## Two meanings

1. **Self-adaptive / self-managing software at *runtime*** — the running system keeps *itself* healthy (scales, recovers, reconfigures) without changing its source. This is autonomic computing applied to software, and it's mature.
2. **Self-maintaining *source code*** — the *code itself* gets fixed, updated, refactored, or improved with little/no human authoring. This is the more literal reading of "codebase," and it ranges from boringly-deployed (dependency bots) to frontier research (AI that rewrites its own code).

## Meaning 1: self-managing systems at runtime (mature)

This is the exact software-side twin of the home OS's MAPE-K loop.

- **Autonomic computing / MAPE-K** — IBM, 2003. The Monitor–Analyze–Plan–Execute over shared Knowledge loop for self-configuring/healing/optimizing/protecting systems ([The Vision of Autonomic Computing](https://dl.acm.org/doi/10.1109/mc.2003.1160055)).
- **Rainbow framework** — Garlan, Schmerl, Cheng et al., CMU, 2004. Architecture-based self-adaptation with reusable monitoring/decision/action infrastructure — the canonical academic system ([ResearchGate — Architecture-Based Self-Adaptation](https://www.researchgate.net/publication/227108020_Software_Architecture-Based_Self-Adaptation)).
- **The field & community** — "self-adaptive systems," organized around the SEAMS conference; recent survey [State of the Art on Self-adaptive Systems (arXiv 2025)](https://arxiv.org/html/2511.06352v1). Key names: David Garlan, Bradley Schmerl, Danny Weyns, Betty Cheng, Rogério de Lemos, Holger Giese.
- **In production today** — Kubernetes self-healing/auto-scaling, cloud auto-remediation, self-adaptive microservices. This part is solved and ordinary.

## Meaning 2: code that maintains/repairs/improves itself

### a. Automatic Program Repair (APR) — academic origin, deployed at scale

- **GenProg** — Le Goues, Nguyen, Forrest, Weimer (~2009–2012). Evolves patches to make a failing test suite pass, with no specs or annotations ([IEEE — GenProg](https://ieeexplore.ieee.org/document/6035728/)). The founding APR system.
- **SapFix + Getafix** — Facebook/Meta, 2018–2019. *The first deployment of automated end-to-end fault fixing, from test design to deployed production repairs* ([SapFix — ICSE-SEIP 2019](https://dl.acm.org/doi/10.1109/ICSE-SEIP.2019.00039)). Proof this leaves the lab.
- 15-year retrospective: Weimer et al., [The Evolution of Automated Software Repair (TSE 2025)](https://web.eecs.umich.edu/~weimerw/p/weimer-tse2025-genprog.pdf).
- Related: **genetic improvement** of software (Harman, Langdon, Petke, UCL CREST).

### b. Routine maintenance bots — the most "real today" form

Codebases already keep themselves current with near-zero human authoring:

- **Dependabot / Renovate** — automated dependency updates as PRs ([Renovate vs Dependabot](https://www.turbostarter.dev/blog/renovate-vs-dependabot-whats-the-best-tool-to-automate-your-dependency-updates)).
- **GitHub Copilot Autofix (for Dependabot/CodeQL)** — *not only keeps dependencies up to date, but also keeps CI green* and auto-patches flagged security issues ([Copilot Autofix discussion](https://github.com/orgs/community/discussions/141502)).

### c. AI coding agents — the current frontier (2024–2026)

Read an issue → locate root cause → write a fix → run tests → open a PR:

- **SWE-bench + SWE-agent** — Princeton (Yang, Jimenez, Press, Narasimhan). The benchmark and agent that defined the "resolve a real GitHub issue autonomously" task.
- **Devin** — Cognition. Markets the full fix cycle end-to-end; real-world success rates are still bounded (~60–80% on well-scoped tasks, much lower on open issues) ([ToolHalla 2026](https://toolhalla.ai/blog/devin-vs-openhands-vs-swe-agent-2026)).
- **OpenHands, DeepSWE** — open-source agents on the same task.
- **SWE-EVO (Dec 2025)** — benchmarks *long-horizon software evolution* specifically (multi-release feature work from release notes + commit history), not just single-issue fixes ([arXiv](https://arxiv.org/html/2512.18470v2)). This is the closest formalization of "maintain a codebase over time."
- **CodeMender** — Google DeepMind, Oct 2025. An autonomous agent that finds and patches security vulnerabilities across large codebases, with a *validation framework that checks the fix addresses root cause, is functionally correct, and breaks no tests*; submitted 72 fixes to open-source projects ([DeepMind — CodeMender](https://deepmind.google/blog/introducing-codemender-an-ai-agent-for-code-security/)).

### d. Code that rewrites *itself* — research stage

- **Gödel machine** — Schmidhuber (theoretical). A program that rewrites its own code once it can *prove* the rewrite improves it ([Sakana summary](https://sakana.ai/dgm/)).
- **Darwin Gödel Machine** — Sakana AI, May 2025. The empirical relaxation: a population of agents that edit their own code and keep what benchmarks better (open-ended evolution, validated on SWE-bench/Polyglot) ([arXiv 2505.22954](https://arxiv.org/abs/2505.22954)).
- **AlphaEvolve** — Google DeepMind, 2025. A Gemini-powered evolutionary coding agent that "evolves entire codebases." Already in production: a better data-center scheduling algorithm *recovering ~0.7% of Google's global compute*, plus chip-design wins ([DeepMind — AlphaEvolve](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/), [arXiv 2506.13131](https://arxiv.org/abs/2506.13131)).

## Can a fully self-maintaining codebase happen?

By layer, roughly where it stands in 2026:

- **Routine upkeep** (deps, lint, flaky tests, known-CVE patches): largely automated and deployed *now*.
- **Bug-fixing from an issue**: partial autonomy, climbing fast, but unreliable on messy real codebases without a human gate.
- **Open-ended self-evolution** (new features, architecture refactors, improving itself): research-stage and *narrow* — DGM and AlphaEvolve only work where there's a strong automatic objective to optimize against.

## The one constraint that governs all of it (and ties back to the home OS)

**You can only safely self-maintain what you can automatically verify.** Every working system above leans on a verification oracle: APR and SWE-agents need a *test suite*; AlphaEvolve needs a *measurable metric*; CodeMender built an explicit *validation framework*; the Gödel machine needs a *proof*. Remove the oracle and self-modification becomes unsafe guessing.

This is the same load-bearing dependency the home design already flagged — the MAPE-K "verify resolution" step, and "scene-graph fidelity." In code the oracle (tests/benchmarks) is comparatively cheap, which is *why* self-maintaining code is further along than self-maintaining homes. The home project's hardest problem isn't the loop shape (well-understood, prior-art-rich); it's manufacturing a trustworthy verification signal in the physical world. Whoever cracks cheap, reliable physical-world verification unlocks the same self-maintenance curve that software is already climbing.
