# What Constitutes a Strong Skill for Claude

*Research compiled April 20, 2026 9:47 AM EDT*

Sources: X.com discourse, Reddit (r/ClaudeAI, r/ClaudeCode, r/AI_Agents), Anthropic official documentation, academic papers, and gstack architecture analysis.

---

## 1. The Core Thesis

A strong Claude skill is not a prompt template pasted into context. It is a **living methodology file** containing decision trees, tool chains, verification steps, failure modes, and learned patterns from actual use. Claude reads the SKILL.md, understands the workflow architecture, and executes step by step using real tools ([Reddit: r/ClaudeAI](https://www.reddit.com/r/ClaudeAI/comments/1rxz863/what_exactly_are_claudes_skills/)). The difference between "works sometimes" and "works reliably" comes down to disciplined context engineering, not more words.

---

## 2. Architecture: Progressive Disclosure is Non-Negotiable

The single most discussed and validated design principle across all sources is **progressive disclosure** — the idea that skills load information in stages, not all at once.

### The Three Tiers

| Tier | What Loads | When | Token Cost |
|------|-----------|------|------------|
| **Metadata** (YAML frontmatter) | `name` + `description` only | Always, at startup | ~100 tokens per skill |
| **Instructions** (SKILL.md body) | Step-by-step process | When skill is triggered | <500 lines recommended |
| **References** (scripts/, references/, assets/) | Domain docs, examples, templates | On-demand, only when needed | Zero until accessed |

This is the architecture that makes skills fundamentally different from stuffing everything into CLAUDE.md. As one X.com user put it: "agents load metadata first, then full instructions only when needed" ([Matteo Collina on X](https://x.com/matteocollina/status/2031053414671450189)). Google Developers endorsed this: "you can load domain expertise only when needed. This can reduce baseline context usage" ([Google Developers on X](https://x.com/googledevs/status/2039359112668950986)).

### Why This Matters: Token Economics

Reddit users who measured actual token usage found dramatic differences:

- Loading 5-7 skills without progressive disclosure = **5,000-7,000 lines flooding context immediately** ([Reddit: r/ClaudeCode](https://www.reddit.com/r/ClaudeCode/comments/1opxf9f/i_was_wrong_about_agent_skills_and_how_i_refactor/))
- With proper progressive disclosure = **400-700 lines of highly relevant context** instead of 1,131 lines of mixed relevance
- Measured improvement: **4.8x token efficiency** — the difference between "works sometimes" and "works reliably"

### The Hard Rules

1. **SKILL.md under 500 lines** ([Anthropic Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)). Many power users go further: keep the entry point under **~200 lines** ([Reddit](https://www.reddit.com/r/ClaudeCode/comments/1opxf9f/i_was_wrong_about_agent_skills_and_how_i_refactor/))
2. **SKILL.md is the map, not the territory.** It should contain process steps only. Domain content goes in reference files ([Reddit: r/ClaudeCode](https://www.reddit.com/r/ClaudeCode/comments/1rqnk1k/how_you_can_build_a_claude_skill_in_10_minutes/))
3. **References one level deep only.** Claude partially reads deeply nested files, using `head -100` previews rather than full reads ([Anthropic Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices))
4. **No maintainer commentary in SKILL.md.** "All text serves the executing model. No design rationale, maintainer commentary, or 'how to extend' guidance" ([Reddit](https://www.reddit.com/r/ClaudeCode/comments/1rqnk1k/how_you_can_build_a_claude_skill_in_10_minutes/))

---

## 3. The Description Field: Make or Break

The `description` field is how Claude decides whether to trigger a skill. This is the single most critical piece of text in the entire skill. Across all sources, the consensus is:

### What Works
- **Specific trigger words**: "generates conventional commit messages from staged diffs" ([Reddit: r/Anthropic](https://www.reddit.com/r/Anthropic/comments/1qbpc9x/a_useful_cheatsheet_for_understanding_claude/))
- **Dual purpose**: Describe both what the skill does AND when to use it
- **Third person**: "Processes Excel files and generates reports" — NOT "I can help you" or "You can use this" ([Anthropic Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices))
- **Front-load key use cases**: Combined description + when_to_use is truncated at 1,536 characters in skill listing

### What Fails
- **Vague descriptions**: "handles git commits" — Claude may never load it because dozens of things could match ([Reddit](https://www.reddit.com/r/Anthropic/comments/1qbpc9x/a_useful_cheatsheet_for_understanding_claude/))
- **Generic names**: `helper`, `utils`, `tools` — meaningless to the model
- **Missing trigger context**: Not specifying when to invoke means Claude guesses

---

## 4. Instruction Design: How to Write What Goes Inside

### Imperative Language Over Suggestions

Anthropic's official guidance and community consensus: **use direct commands, not suggestions**. "Always run tests before committing" reliably outperforms "You might want to consider running tests." Agents follow directives more reliably than suggestions ([Anthropic Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)).

### Degrees of Freedom: Match Specificity to Fragility

From [Anthropic's Skill Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices):

| Freedom Level | When to Use | Example |
|--------------|-------------|---------|
| **High** (text instructions) | Multiple valid approaches, decisions depend on context | Code review process |
| **Medium** (pseudocode/templates) | Preferred pattern exists, some variation OK | Report generation with format parameters |
| **Low** (exact scripts, no params) | Operations are fragile, consistency critical, specific sequence required | Database migrations |

The analogy from Anthropic: Think of Claude as a robot on a path. **Narrow bridge with cliffs** = exact instructions. **Open field** = general direction.

### XML Tags for Structure

Claude responds significantly better to prompts structured with XML tags. This is one of the most validated findings across all sources ([Anthropic Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)):

```xml
<instructions>Step-by-step process here</instructions>
<context>Background information here</context>
<examples>Input/output pairs here</examples>
```

### The Default Assumption: Claude is Already Smart

From [Anthropic Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices): "Only add context Claude doesn't already have." Challenge each piece:
- "Does Claude really need this explanation?"
- "Can I assume Claude knows this?"
- "Does this paragraph justify its token cost?"

A 50-token concise example reliably outperforms a 150-token verbose one that explains what PDFs are.

---

## 5. Reliability Patterns

### Pattern 1: Feedback Loops (Validate-Fix-Repeat)

The most impactful reliability pattern across all sources. Run a validator, fix errors, repeat. This pattern "greatly improves output quality" ([Anthropic Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

gstack implements this through atomic commits per concern: design fixes, code reviews, and QA work each generate single-purpose commits, making changes bisectable and reversible ([gstack architecture](https://github.com/garrytan/gstack/blob/main/docs/skills.md)).

### Pattern 2: Verifiable Intermediate Outputs

For complex tasks, create a plan file (e.g., `changes.json`) that gets validated before execution. This is the "plan-validate-execute" pattern:

1. Analyze the input
2. Create a structured plan file
3. Validate the plan with a script
4. Execute only after validation passes
5. Verify the output

This catches errors before they propagate. gstack's risk budgeting enforces hard caps (e.g., 30 fixes max) and calculates risk scores before proceeding ([gstack docs](https://github.com/garrytan/gstack/blob/main/docs/skills.md)).

### Pattern 3: Forcing Assumptions Into the Open

Multiple gstack skills use **diagrams and structured formats** to prevent hand-wavy planning. The `/plan-eng-review` skill emphasizes: "diagrams force hidden assumptions into the open. They make hand-wavy planning much harder" ([gstack architecture](https://github.com/garrytan/gstack/blob/main/docs/skills.md)).

### Pattern 4: Workflow Checklists

For complex multi-step processes, provide a checklist Claude can copy and track:

```
Task Progress:
- [ ] Step 1: Analyze input
- [ ] Step 2: Create mapping
- [ ] Step 3: Validate mapping
- [ ] Step 4: Execute changes
- [ ] Step 5: Verify output
```

This prevents Claude from skipping steps ([Anthropic Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

### Pattern 5: Error-Handling in Scripts, Not in Claude

"Solve, don't punt" — scripts should handle errors explicitly rather than failing and letting Claude figure it out. Configuration parameters should be justified and documented to avoid "voodoo constants" ([Anthropic Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

---

## 6. Structural Patterns from gstack

gstack achieves its reliability through several architectural decisions that apply to any skill system:

### Role-Based Specialization
Each skill embodies a specific professional role — CEO, engineer manager, designer, QA lead — rather than attempting multiple domains. This bounds the context and produces deeper reasoning within that domain ([gstack architecture](https://github.com/garrytan/gstack), [DEV Community analysis](https://dev.to/imaginex/a-claude-code-skills-stack-how-to-combine-superpowers-gstack-and-gsd-without-the-chaos-44b3)).

### Sequential Refinement Through Review Gates
Outputs from one phase feed into the next: `/plan-ceo-review` -> `/plan-eng-review` -> `/plan-design-review`. Decisions persist to disk so they survive beyond conversations ([gstack docs](https://github.com/garrytan/gstack/blob/main/docs/skills.md)).

### Three-Layer Architecture
The most effective skill stacks separate concerns into layers ([DEV Community](https://dev.to/imaginex/a-claude-code-skills-stack-how-to-combine-superpowers-gstack-and-gsd-without-the-chaos-44b3)):
1. **Decision layer**: What to do and whether it should be done
2. **Execution layer**: Disciplined workflow from planning through verification
3. **Context layer**: Maintaining stable specifications across long sessions

### The Selectivity Principle
"Skill counts spiral easily... Selective deployment beats volume." Focused scope over feature accumulation. The most stable implementations cherry-pick high-value flows rather than enabling everything simultaneously ([DEV Community](https://dev.to/imaginex/a-claude-code-skills-stack-how-to-combine-superpowers-gstack-and-gsd-without-the-chaos-44b3)).

---

## 7. Academic Research Findings

### Tool Description Quality Directly Impacts Performance

**ToolFlow** (NAACL 2025): Using a Graph-based Sampling strategy to sample relevant tool combinations and a Planned-generation strategy to create coherent dialogues, LLaMA-3.1-8B fine-tuned on just 8,000 synthetic dialogues achieved performance comparable to or surpassing GPT-4 in tool-calling. The key insight: **natural, coherent tool descriptions** matter more than volume of training data ([ACL Anthology](https://aclanthology.org/2025.naacl-long.214/)).

### Stateful Interactions Are the Hard Part

**ToolSandbox** (Apple, NAACL 2025 Findings): A benchmark showing that stateful tool execution, implicit state dependencies between tools, and conversational context are where even SOTA LLMs struggle significantly. Open-source models have a "significant performance gap" with proprietary models on complex state-dependent tasks ([arxiv: 2408.04682](https://arxiv.org/abs/2408.04682)).

Implication for skill design: **explicitly model state transitions and dependencies** rather than assuming Claude will track implicit state.

### Simple Composable Patterns Over Frameworks

**Anthropic's "Building Effective Agents"** (Dec 2024): The most successful implementations use five simple, composable patterns rather than complex frameworks ([Anthropic Research](https://www.anthropic.com/research/building-effective-agents)):
1. **Prompt chaining**: Sequential LLM calls
2. **Routing**: Initial call decides next step
3. **Parallelization**: Task split and run simultaneously
4. **Orchestrator-workers**: One orchestrator, multiple workers
5. **Evaluator-optimizer**: One model checks another in a loop

### Prompt Sensitivity Research

Options and parameters presented within prompts show **sensitivity scores of 6.37** compared to knowledge components at 2.56. This means the way choices are structured in system prompts has **2.5x more impact** on agent behavior than the factual knowledge provided ([Lakera Prompt Engineering Guide](https://www.lakera.ai/blog/prompt-engineering-guide)).

### Chain-of-Thought Still Works

Self-consistency with CoT achieves a **2-3x accuracy boost** over simple Chain-of-Thought alone by using an ensemble approach. For skills, this translates to: have Claude reason through its approach before executing, and verify against multiple criteria ([Prompting Guide](https://www.promptingguide.ai/research/llm-agents)).

### Context Engineering > Prompt Engineering

The emerging consensus in 2025-2026: "2023: prompt engineering. 2024: context engineering. 2025: tool use, memory, evals. 2026: delete waste tokens." Context engineering — what information the agent has access to and when — separates agents that demo well from agents that run in production ([X.com: @koylanai](https://x.com/koylanai/status/2003948029661893093)).

---

## 8. Community-Validated Anti-Patterns (What NOT to Do)

### 1. Giant SKILL.md Files
Loading everything into one massive SKILL.md file is the most common mistake. It floods context and degrades performance ([Reddit: r/ClaudeCode](https://www.reddit.com/r/ClaudeCode/comments/1opxf9f/i_was_wrong_about_agent_skills_and_how_i_refactor/)).

### 2. Embedding Skill Pointers in CLAUDE.md
"You should not need to embed semantic information and pointers to your Skills within the CLAUDE.md as the Skill's frontmatter is passed along with each message" ([Reddit: r/ClaudeAI](https://www.reddit.com/r/ClaudeAI/comments/1pha74t/deep_dive_anatomy_of_a_skill_its_tokenomics_why/)).

### 3. Time-Sensitive Information
Don't include "if you're doing this before August 2025, use old API." Use an "old patterns" section with `<details>` collapse instead ([Anthropic Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

### 4. Inconsistent Terminology
Mixing "API endpoint", "URL", "API route", "path" within a single skill confuses the model. Pick one term and use it throughout ([Anthropic Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

### 5. Too Many Options
Presenting multiple approaches unless necessary: "You can use pypdf, or pdfplumber, or PyMuPDF..." — instead, provide a default with an escape hatch ([Anthropic Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

### 6. Over-Prompting Tool Usage
"Tools that undertriggered in previous models are likely to trigger appropriately now. Instructions like 'If in doubt, use [tool]' will cause overtriggering" on Claude 4.x models ([Anthropic Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)).

### 7. Windows-Style Paths
Always use forward slashes, even on Windows. Unix-style paths work cross-platform ([Anthropic Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

---

## 9. The Iterative Development Process

Anthropic's official recommendation, validated across community sources:

### Build With Two Claudes
1. **Claude A** (architect): Helps design and refine the skill
2. **Claude B** (executor): Tests the skill on real tasks in a fresh context

This works because "Claude models understand both how to write effective agent instructions and what information agents need" ([Anthropic Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

### Evaluation-Driven Development
1. Run Claude on representative tasks WITHOUT a skill — document specific failures
2. Build 3 evaluation scenarios testing those gaps
3. Measure baseline performance
4. Write MINIMAL instructions addressing just the gaps
5. Iterate: evaluate -> compare -> refine

"This approach ensures you're solving actual problems rather than anticipating requirements that may never materialize" ([Anthropic Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)).

### The Observation Loop
- Watch for **unexpected exploration paths** — Claude reading files in unanticipated order
- Watch for **missed connections** — Claude failing to follow references
- Watch for **overreliance** — Claude repeatedly reading the same file (should be in SKILL.md instead)
- Watch for **ignored content** — file never accessed (might be unnecessary)

---

## 10. Synthesis: The Checklist for a Strong Skill

Based on convergent evidence across all sources:

**Architecture**
- [ ] SKILL.md under 200-500 lines (process steps only)
- [ ] Domain content in separate reference files
- [ ] Progressive disclosure: metadata -> instructions -> references
- [ ] References one level deep max
- [ ] Forward-slash paths everywhere

**Description**
- [ ] Specific trigger words that match natural language
- [ ] Third-person voice
- [ ] Describes WHAT it does AND WHEN to use it
- [ ] Key use case front-loaded (1,536 char cap)

**Instructions**
- [ ] Imperative language (commands, not suggestions)
- [ ] Freedom level matched to task fragility
- [ ] XML tags for structural clarity
- [ ] No redundant explanations Claude already knows
- [ ] Consistent terminology throughout

**Reliability**
- [ ] Feedback loops (validate -> fix -> repeat)
- [ ] Verifiable intermediate outputs for complex tasks
- [ ] Explicit error handling in scripts
- [ ] Workflow checklists for multi-step processes
- [ ] No voodoo constants

**Testing**
- [ ] At least 3 evaluation scenarios
- [ ] Tested with real usage (not synthetic)
- [ ] Tested across model sizes (Haiku/Sonnet/Opus)
- [ ] Iterated based on observed behavior, not assumptions

**Scope**
- [ ] One skill, one job
- [ ] Selective deployment over volume
- [ ] Addresses actual workflow gaps, not hypothetical ones
- [ ] Proportional process (not front-loading heavy process for small tasks)

---

## Sources

### Official Documentation
- [Anthropic Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
- [Anthropic Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Agent Skills Specification (agentskills.io)](https://agentskills.io/specification)
- [Anthropic: Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [Anthropic: Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)

### gstack
- [gstack GitHub Repository](https://github.com/garrytan/gstack)
- [gstack Skills Architecture](https://github.com/garrytan/gstack/blob/main/docs/skills.md)
- [DEV Community: Claude Code Skills Stack Analysis](https://dev.to/imaginex/a-claude-code-skills-stack-how-to-combine-superpowers-gstack-and-gsd-without-the-chaos-44b3)
- [SitePoint: gstack Tutorial](https://www.sitepoint.com/gstack-garry-tan-claude-code/)

### Academic Papers
- [ToolFlow: Boosting LLM Tool-Calling Through Natural and Coherent Dialogue Synthesis (NAACL 2025)](https://aclanthology.org/2025.naacl-long.214/)
- [ToolSandbox: A Stateful, Conversational, Interactive Evaluation Benchmark (Apple, NAACL 2025)](https://arxiv.org/abs/2408.04682)
- [Agent Skill Acquisition for Large Language Models via CycleQD](https://arxiv.org/abs/2410.14735)
- [Agent Skills for LLMs: Architecture, Acquisition, Security, and the Path Forward](https://arxiv.org/html/2602.12430v3)
- [LLM-Based Agents for Tool Learning: A Survey](https://link.springer.com/article/10.1007/s41019-025-00296-9)

### X.com Discourse
- [Matteo Collina on Progressive Disclosure in Agent Skills](https://x.com/matteocollina/status/2031053414671450189)
- [Google Developers on Agent Skills Specification](https://x.com/googledevs/status/2039359112668950986)
- [@koylanai on Context Engineering](https://x.com/koylanai/status/2003948029661893093)
- [@omarsar0 on Harness Engineering](https://x.com/omarsar0/status/2031426008285421933)
- [Elvis on Chaining Slash Commands](https://x.com/omarsar0/status/1970877712441995329)
- [Miles Deutscher: 50 Claude Code Tips](https://x.com/milesdeutscher/status/2014027971254952332)

### Reddit
- [r/ClaudeAI: Deep Dive into Skill Tokenomics](https://www.reddit.com/r/ClaudeAI/comments/1pha74t/deep_dive_anatomy_of_a_skill_its_tokenomics_why/)
- [r/ClaudeCode: I Was Wrong About Agent Skills (4.8x Token Efficiency)](https://www.reddit.com/r/ClaudeCode/comments/1opxf9f/i_was_wrong_about_agent_skills_and_how_i_refactor/)
- [r/ClaudeAI: Anthropic Released 32-Page Guide (1,477 upvotes)](https://www.reddit.com/r/ClaudeAI/comments/1r3hr40/anthropic_released_32_page_detailed_guide_on/)
- [r/ClaudeAI: What Are Claude Skills Really?](https://www.reddit.com/r/ClaudeAI/comments/1rxz863/what_exactly_are_claudes_skills/)
- [r/ClaudeAI: Agent Skills as Open Standard](https://www.reddit.com/r/ClaudeAI/comments/1ppw38d/agent_skills_is_now_an_open_standard/)
- [r/ClaudeCode: Build a Skill in 10 Minutes](https://www.reddit.com/r/ClaudeCode/comments/1rqnk1k/how_you_can_build_a_claude_skill_in_10_minutes/)
- [r/Anthropic: Cheatsheet for Understanding Skills](https://www.reddit.com/r/Anthropic/comments/1qbpc9x/a_useful_cheatsheet_for_understanding_claude/)
- [r/ClaudeCode: 116-Configuration Setup](https://www.reddit.com/r/ClaudeCode/comments/1rltiv7/inside_a_116configuration_claude_code_setup/)

### Guides & Analysis
- [Lakera: The Ultimate Guide to Prompt Engineering in 2026](https://www.lakera.ai/blog/prompt-engineering-guide)
- [Prompting Guide: LLM Agents](https://www.promptingguide.ai/research/llm-agents)
- [Smartscope: Anthropic's 33-Page Guide Distilled — 5 Design Patterns](https://smartscope.blog/en/generative-ai/claude/claude-skills-design-patterns-official-guide/)
- [Composio: Top 10 Claude Code Skills 2026](https://composio.dev/content/top-claude-skills)
