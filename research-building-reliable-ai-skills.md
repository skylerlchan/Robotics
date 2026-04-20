# Research: Building Strong, Reliable Skills/Abilities for Claude Code and AI Agents

**Date:** 2026-04-20

---

## 1. Official Anthropic Guidance: "The Complete Guide to Building Skills for Claude"

Anthropic published a 33-page guide that is the single most authoritative source on skill design. Key findings from the guide and from Thariq (Claude Code engineer) who wrote the companion blog post ([X post](https://x.com/trq212/status/2033949937936085378)):

### Skills Cluster Into Recurring Categories

The best skills fit cleanly into one category; the more confusing ones straddle several:

- **Knowledge Skills** -- encode domain expertise that pushes Claude outside its default behavior. The Anthropic frontend design skill is a good example: "it was built by iterating with customers on improving Claude's design taste, avoiding classic patterns like the Inter font and purple gradients" ([Thariq/X](https://x.com/trq212/status/2033949937936085378))
- **Workflow Skills** -- enforce a specific sequence of steps (plan, review, ship)
- **Code Style Skills** -- enforce code patterns Claude doesn't do well by default
- **Testing Practice Skills** -- instructions on how to write tests and what to test
- **Adversarial Review Skills** -- spawn a fresh-eyes subagent to critique, implement fixes, iterate until findings degrade to nitpicks

### Progressive Disclosure is the Core Architecture

This is the single most important design pattern for skills. Skills use a lazy-loading approach where Claude only loads what it needs when it needs it ([Thariq/X](https://x.com/trq212/status/2033949937936085378), [Google Devs/X](https://x.com/googledevs/status/2039359112668950986)):

1. **At startup:** Claude pre-loads only the name and description of every installed skill (~100 tokens each) ([Eyad/X](https://x.com/eyad_khrais/status/2010810802023141688))
2. **On demand:** When a task matches a skill, Claude reads the full SKILL.md
3. **Multi-level:** SKILL.md can reference other files (scripts/, references/, assets/), which Claude reads only if needed

This reduces baseline context usage by up to 90% compared to dumping everything into a system prompt ([Google Devs/X](https://x.com/googledevs/status/2039359112668950986)).

### Skill Structure Best Practices (from Anthropic's guide)

- **A skill is a folder, not just a file.** The SKILL.md is the entry point, but supporting files in `scripts/`, `references/`, or `assets/` directories provide depth
- **Frontmatter matters.** YAML frontmatter controls behavior: `name`, `description`, `allowed-tools`, `context: fork` (run in subagent), `user-invocable: false`, `disable-model-invocation: true`
- **Include troubleshooting sections** that capture common gotchas Claude runs into when using the skill. Update these over time ([Thariq/X](https://x.com/trq212/status/2033949937936085378))
- **Focus knowledge skills on information that pushes Claude out of its normal thinking patterns** rather than things Claude already knows well

**Source:** [Anthropic's Complete Guide to Building Skills](https://claude.com/blog/complete-guide-to-building-skills-for-claude), [PDF version](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)

---

## 2. Prompt Engineering Patterns That Make Skills Reliable

### 30 Techniques from Claude Code's Own System Prompt

An analysis of Claude Code's leaked/open-sourced codebase by XenZee identified 30 prompt engineering techniques ([X post](https://x.com/XenZeeCodes/status/2039166944314884250)):

1. **Multi-Level Security Redundancy** -- Repeat critical constraints at system prompt, tool descriptions, and task-specific prompt levels. "No single instruction is 100% reliable. By repeating security constraints at different levels, you create redundancy."

2. **Static/Dynamic Boundary** -- Separate static rules (which get cached) from dynamic data (which gets refreshed). This saves 60-80% on API tokens and is foundational to prompt caching ([RetroChainer/X](https://x.com/RetroChainer/status/2040779340560941562))

3. **Imperative Constraints** -- Use NEVER and MUST instead of "try to" and "consider." The model ignores soft suggestions but follows commands ([RetroChainer/X](https://x.com/RetroChainer/status/2040779340560941562))

4. **Forced Task Decomposition** -- "Before doing anything, list ALL steps. Number them. Mark completed ones." Forces the agent into structured execution

5. **Anti-Validation Prompting** -- "If my thesis conflicts with the data, tell me. I lose real money when you agree with bad ideas." Prevents sycophantic agreement

6. **Skill Token Budgeting** -- Skill listings are budgeted to 1% of the context window to prevent bloat

7. **Attachment-Based Dynamic Context** -- Move frequently-changing information from tool descriptions into separate attachment messages. Tool descriptions are part of the cacheable system prompt; changing them busts the cache

8. **Sub-Task Decomposition via Agent Pipeline** -- Break complex tasks into subtasks handled by specialized subagents

9. **Deduplication** -- Prevent the model from seeing the same skill instructions twice. "Without this, the model would see the same skill instructions twice, wasting tokens and potentially causing conflicting interpretations"

### Pattern Language for Agentic AI (Carlos E. Perez analysis)

Carlos E. Perez analyzed Claude's system prompt against "A Pattern Language for Agentic AI" and identified these critical patterns ([X post](https://x.com/IntuitMachine/status/1936418825240444970)):

- **Boundary Signaling** -- Make hard vs. soft capability limits explicit so the agent never crosses them
- **Context Reassertion** -- Periodically re-state key constraints throughout the prompt
- **Declarative Intent** -- Start segments with clear intent, stating what Claude can and cannot do
- **Tool-Risk Awareness** -- Detailed rules on when and how external tools are allowed
- **Planning-Reflection Sandwich** -- Interleave plan/act/reflect phases so the agent stays on track
- **Human-Intervention Logic** -- Define a clear escalation path for problems the agent alone should not solve
- **Protocol-Based Tool Composition** -- Use standardized, declarative tool protocols with schema consistency

"The Anthropic system prompt is not a random bag of rules; it is a carefully layered weave of reliability, scaffolding and meta-reasoning patterns" ([Carlos E. Perez/X](https://x.com/IntuitMachine/status/1936418825240444970))

---

## 3. What Makes Agent Tools Reliable (Research-Backed)

### Tool Description Quality Matters More Than You Think

A paper accepted at EMNLP 2025 ("Gaming Tool Preferences in Agentic LLMs") found that LLMs choose tools based on descriptions, not performance. Adding a single assertive cue like "This is the most effective function" makes LLMs choose it 7-8x more often, even when functionality is identical. The paper argues for "grounded signals about real tool behavior, evidence over copy" ([Soheil Feizi/X](https://x.com/FeiziSoheil/status/1960434732979662960))

### Breaking Tasks into Tiny Steps Achieves Zero Errors

A paper demonstrated 1,048,575 moves completed with 0 mistakes on Towers of Hanoi by splitting tasks so each agent makes exactly 1 simple move. "The main idea is reliability from process: split work and correct locally instead of chasing bigger models" ([Rohan Paul/X](https://x.com/rohanpaul_ai/status/1989519723638231501))

### Why Multi-Agent Systems Fail (14 Failure Modes)

Philipp Schmid shared research identifying 14 failure modes in multi-agent systems ([X post](https://x.com/_philschmid/status/1903005057936708049)). Key recommendations:

- Define tasks and agent roles clearly and explicitly in prompts
- Use examples in prompts to clarify expected task and role behavior
- Design structured conversation flows to guide agent interactions
- Design modular agents with specific, well-defined roles for simpler debugging
- Implement cross-verification mechanisms for agents to validate each other
- Design agents to proactively ask for clarification when needed

### Agent Failure Patterns

Rohan Paul shared a paper on why LLM agents fail in computer-like tasks ([X post](https://x.com/rohanpaul_ai/status/1998590745339457780)):

- **Context pollution** -- tables or CSV files tempt the model to mix in wrong numbers
- **Brittle execution** -- malformed tool calls, loops, or losing track of steps once traces are large
- Conclusion: "LLM agents become reliable only when they are trained to ground actions, verify data, and recover from errors, not just scaled up in size"

### Separate Reasoning from Execution

Paul Iusztin's agent engineering roadmap emphasizes: "Separate reasoning from execution so agents can handle multi-step, multi-tool problems reliably" using ReAct and plan-and-execute patterns. Context engineering, structured outputs, and tool calling are the foundational layers ([X post](https://x.com/pauliusztin_/status/2003827831155871791))

---

## 4. GStack: How Garry Tan's Skills Achieve Reliability

GStack (by Garry Tan, YC CEO) is one of the most discussed skill collections, with 15+ specialist skills for Claude Code ([GitHub](https://github.com/garrytan/gstack)). Key design patterns:

### Specialist Roles Over Generic Agents

The core idea: "instead of one generic AI assistant, you get specialists you can call on" ([Himanshu/X](https://x.com/Hxlfed14/status/2033213745460306133)). Each skill embodies a distinct persona:

- `/plan-ceo-review` -- Founder brain. Finds the real product before you build the wrong one
- `/plan-eng-review` -- Architect brain. Architecture gate: will this blow up later?
- `/review` -- Code review
- `/qa` -- Real browser, real clicks, real user testing on staging
- `/ship` -- Deploy workflow
- `/office-hours` -- YC-style product thinking ([Garry Tan/X](https://x.com/garrytan/status/2034304114574909681))

### ETHOS.md: Philosophical Guardrails

GStack includes an ETHOS.md file with meta-rules that govern all skills ([Garry Tan/X](https://x.com/garrytan/status/2037905125055033351)):

> **User Sovereignty:** AI models recommend. Users decide. This is the one rule that overrides all others. Two AI models agreeing on a change is a strong signal. It is not a mandate. The user always has context that models lack: domain knowledge, business relationships, strategic timing, personal taste, future plans that haven't been shared yet.

Referencing Andrej Karpathy's "Iron Man suit" philosophy and Simon Willison's warning that "agents are merchants of complexity," GStack keeps the human at the center.

### Opinionated Workflows Over Flexible Prompts

GStack skills are not loose suggestions; they enforce specific workflows. For example, `/qa` uses Playwright for real browser automation rather than just asking Claude to imagine testing. `/ship` follows a structured release workflow. This opinionated approach makes them reliable because they reduce the agent's decision space ([Marktechpost/X](https://x.com/Marktechpost/status/2032740337396101549)).

### Skills Can Be Chained

The workflow `/office-hours` (plan) -> `/review` (check code) -> `/qa` (test in real browser) -> `/ship` (deploy) shows how skills compose into a complete development pipeline ([Corey Ganim/X](https://x.com/coreyganim/status/2034717504505823728)).

---

## 5. Claude Code Best Practices (From Boris Cherny, Creator)

Boris Cherny, who created Claude Code, shared these key insights ([X posts](https://x.com/bcherny/status/2007179832300581177), [X](https://x.com/bcherny/status/2038454360418787764)):

### CLAUDE.md Design

- Keep the root CLAUDE.md lean -- under 200 lines per file ([Tech with Mak/X](https://x.com/techNmak/status/2037788648691884207))
- Every mistake becomes a rule added to CLAUDE.md
- Tag @.claude on coworker PRs to add learnings to CLAUDE.md as part of review
- CLAUDE.md should include: bash commands used frequently, important files, architectural decisions, coding style preferences

### Skills vs. Commands vs. Agents

- "Use commands for workflows instead of sub-agents"
- "Have feature-specific sub-agents with skills instead of general QA or backend"
- Use `--agent` to give Claude Code a custom system prompt and tools: "Custom agents are a powerful primitive that often gets overlooked" ([Boris Cherny/X](https://x.com/bcherny/status/2038454360418787764))
- Skills that run automatically as hooks or in GitHub Actions: `adversarial-review`, `code-style`, `testing-practices`

### Prompt Caching is Everything

Thariq (Claude Code engineer) wrote: "you fundamentally have to design agents for prompt caching first, almost every feature touches on it somehow" ([X post](https://x.com/trq212/status/2024638793719177291)):

- Keep all tools in every request (don't add/remove dynamically) -- toggling tools breaks cache
- Use EnterPlanMode/ExitPlanMode as tools themselves rather than changing the tool set
- If switching models, use subagents where Opus prepares a "handoff" message
- Use identical cache-safe parameters for side computations (compaction, summarization, skill execution)
- Fragile ordering: putting timestamps in static prompts, shuffling tool order, or updating tool parameters all break prompt cache hits

### Verification is Everything

"Give Claude verification. Browser tests, bash commands, test suites. 2-3x quality improvement" ([Boris Cherny via Aakash Gupta/X](https://x.com/aakashgupta/status/2007347705945944153))

---

## 6. Context Engineering: The Meta-Discipline

Multiple sources converge on "context engineering" as the discipline that separates agents that demo well from agents that run in production ([Koylan AI/X](https://x.com/koylanai/status/2003948029661893093)):

### Key Principles

- **Design how information flows into the model** -- context engineering is about the entire pipeline, not just the prompt ([Paul Iusztin/X](https://x.com/pauliusztin_/status/2003827831155871791))
- **Context degradation is real** -- lost-in-middle effects, context poisoning, and token bloat silently degrade performance
- **Context optimization** -- compaction, masking, and caching are essential techniques

### GSD (Get Sh*t Done) Framework

GSD is a meta-prompting and context engineering system for Claude Code that enforces spec-driven development. "It's the context engineering layer that makes Claude Code reliable. GSD is about describing your idea, let the system extract everything it needs to know as context, and let Claude Code get to work. Each action the agent takes becomes a mandatory, deliberate, auditable task tied to a plan" ([Uncle BigBay/X](https://x.com/unclebigbay143/status/2015535426472226992))

### Agent Skills for Context Engineering

A repo treating skills as a "Meta-Agent knowledge base" organizes context fundamentals, context degradation patterns, context optimization, and multi-agent patterns into learnable skills ([Koylan AI/X](https://x.com/koylanai/status/2003117995963424941))

---

## 7. Lessons from Building Background Agents

David Wilson shared hard-won lessons ([X post](https://x.com/daviddbwilson/status/2018358661283029293)):

- **Playbooks (skills) should focus on why and what, not how** -- give ever-smarter models room to make decisions, but this also gives them room to go off track
- "You can't prompt your way to reliable background agents" -- users who got the most value came in with a specific workflow already in mind
- **Text-based playbooks/skills are easier to create, understand, and edit than node-based flows**
- "The underlying AI models will keep improving. Some of this architecture will become less necessary. But right now, if you're building background agents, these patterns will help make them reliable"

---

## 8. Compound Engineering: Competing Framework

The "Compound Engineering" framework from Every is another major skill system discussed alongside GStack. Comparisons note ([Vox/X](https://x.com/Voxyz_ai/status/2038237755654783107)):

- **GStack's strength is in decisions and real-world QA**
- **Compound Engineering's strength is in accumulating project knowledge** -- "The longer you use it, the more your agent understands your project"
- Five subagents extract lessons and write them to docs/solutions/ -- making each cycle faster
- The recommendation: pick one main framework first and get comfortable before combining

---

## 9. Synthesis: The 12 Principles of Reliable Skill Design

Based on all findings, these are the core principles:

1. **Progressive Disclosure** -- Load only what's needed. Skill metadata at startup, full instructions on demand, supporting files only when referenced.

2. **Imperative Language** -- Use MUST/NEVER/ALWAYS, not "try to" or "consider." Models follow commands, not suggestions.

3. **Single Responsibility** -- Each skill should do one thing well. Specialist roles beat generic agents.

4. **Forced Decomposition** -- Require explicit step listing before execution. Number steps. Mark completed ones.

5. **Verification Loops** -- Build verification into every skill. Browser tests, bash commands, test suites produce 2-3x quality improvement.

6. **Iterative Refinement** -- Include troubleshooting sections. Update skills based on observed failures. Every mistake becomes a rule.

7. **Token Budget Awareness** -- Budget skill listings to ~1% of context window. Use prompt caching. Keep static/dynamic boundaries clean.

8. **Opinionated Workflows** -- Reduce the agent's decision space. Enforce specific sequences rather than offering flexible options.

9. **Multi-Level Redundancy** -- Repeat critical constraints at system prompt, tool descriptions, and task-specific levels.

10. **Human Sovereignty** -- AI recommends, users decide. Build in escalation paths and human intervention points.

11. **Context Hygiene** -- Use /compact at 60K tokens, /clear between unrelated tasks, subagents for exploration. Context pollution is a silent killer.

12. **Evidence Over Copy** -- Ground tool selection in observed performance, not assertive descriptions. Design skills based on what works in practice.

---

## Sources

- [Thariq - Lessons from Building Claude Code: How We Use Skills](https://x.com/trq212/status/2033949937936085378)
- [Thariq - Prompt Caching Is Everything](https://x.com/trq212/status/2024574133011673516)
- [Boris Cherny - My Claude Code Setup](https://x.com/bcherny/status/2007179832300581177)
- [Boris Cherny - Custom Agents](https://x.com/bcherny/status/2038454360418787764)
- [Boris Cherny - Skills Merged with Slash Commands](https://x.com/bcherny/status/2014839121659986316)
- [XenZee - 30 Prompt Engineering Techniques Behind Claude Code](https://x.com/XenZeeCodes/status/2039166944314884250)
- [Carlos E. Perez - Claude 4.0 System Prompt Pattern Analysis](https://x.com/IntuitMachine/status/1936418825240444970)
- [RetroChainer - 4 Techniques from Claude Code's System Prompt](https://x.com/RetroChainer/status/2040779340560941562)
- [Alex Prompter - Anthropic Complete Guide to Building Skills](https://x.com/alex_prompter/status/2022246638304313461)
- [Soheil Feizi - Gaming Tool Preferences in Agentic LLMs (EMNLP 2025)](https://x.com/FeiziSoheil/status/1960434732979662960)
- [Rohan Paul - Zero Error Million-Step LLM Tasks](https://x.com/rohanpaul_ai/status/1989519723638231501)
- [Rohan Paul - How LLMs Fail in Agentic Scenarios](https://x.com/rohanpaul_ai/status/1998590745339457780)
- [Philipp Schmid - Why Multi-Agent LLM Systems Fail](https://x.com/_philschmid/status/1903005057936708049)
- [Andrew Ng - Tool Use Design Patterns](https://x.com/AndrewYNg/status/1775951610059141147)
- [Paul Iusztin - Agent Engineering Roadmap](https://x.com/pauliusztin_/status/2003827831155871791)
- [Garry Tan - GStack ETHOS.md](https://x.com/garrytan/status/2037905125055033351)
- [Garry Tan - /office-hours Skill](https://x.com/garrytan/status/2034304114574909681)
- [Marktechpost - GStack Release](https://x.com/Marktechpost/status/2032740337396101549)
- [Vox - GStack vs Superpowers vs Compound Engineering](https://x.com/Voxyz_ai/status/2038237755654783107)
- [David Wilson - Lessons from Building Reliable Background Agents](https://x.com/daviddbwilson/status/2018358661283029293)
- [Uncle BigBay - GSD Framework](https://x.com/unclebigbay143/status/2015535426472226992)
- [Eyad - Claude Code Tutorial Level 2 (Skills Deep Dive)](https://x.com/eyad_khrais/status/2010810802023141688)
- [Tech with Mak - Claude Code Best Practices (22K stars)](https://x.com/techNmak/status/2037788648691884207)
- [Koylan AI - Agent Skills for Context Engineering](https://x.com/koylanai/status/2003117995963424941)
- [Google Devs - Agent Skills Specification](https://x.com/googledevs/status/2039359112668950986)
- [Augment Code - Prompting as Infrastructure](https://x.com/augmentcode/status/2033617142353170940)
- [Andrej Karpathy - 2025 LLM Year in Review](https://x.com/karpathy/status/2002118205729562949)
- [Cat Wu (Anthropic) - Official Best Practices Guide](https://x.com/_catwu/status/1913354716001739173)
- [Anthropic - Complete Guide to Building Skills for Claude](https://claude.com/blog/complete-guide-to-building-skills-for-claude)
- [Justin Schroeder - Claude Code Source Analysis](https://x.com/jpschroeder/status/2038960058499768427)
