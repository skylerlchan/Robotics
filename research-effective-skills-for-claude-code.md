# What Makes a Strong, Reliable Skill/Ability for Claude Code and AI Agents

**Research compiled: April 20, 2026 09:47 EDT**

Deep web research synthesizing Reddit community discussions from r/ClaudeAI, r/ClaudeCode, r/LocalLLaMA, r/ChatGPTCoding, r/AI_Agents, r/PromptEngineering, and r/MachineLearning on what makes agent skills reliable, how to structure them, and what to avoid.

---

## Table of Contents

1. [The Hierarchy: CLAUDE.md vs Skills vs Commands vs Hooks](#1-the-hierarchy)
2. [Skill Architecture Best Practices](#2-skill-architecture-best-practices)
3. [The Progressive Disclosure Pattern](#3-progressive-disclosure)
4. [CLAUDE.md Design Principles](#4-claudemd-design-principles)
5. [Hooks: The Deterministic Enforcement Layer](#5-hooks-deterministic-enforcement)
6. [Common Failure Modes and Prevention](#6-failure-modes)
7. [The AGENTS.md Research: What the Data Says](#7-agentsmd-research)
8. [Context Window Management and Compaction](#8-context-management)
9. [Instruction Design for Reliable Compliance](#9-instruction-design)
10. [Anti-Patterns to Avoid](#10-anti-patterns)

---

## 1. The Hierarchy: CLAUDE.md vs Skills vs Commands vs Hooks {#1-the-hierarchy}

The Claude Code ecosystem has distinct layers, and understanding when to use each is critical. A highly upvoted diagram from r/ClaudeAI lays it out ([Claude Code Extension Features Comparison](https://www.reddit.com/r/ClaudeAI/comments/1pvobog/claude_code_extension_features_commands_rules/)):

```
DISTRIBUTION:  Plugins (package & share)
EXTENSIONS:    Commands | Skills | Agents | Hooks | MCP
FOUNDATION:    Rules (CLAUDE.md) - passive context
```

**When to use what:**

- **CLAUDE.md (Rules)**: Always-loaded passive context. Use for things that apply to 80%+ of conversations -- project structure, coding conventions, hard rules. As one highly upvoted user put it: "Orientation (project identity, tech stack, conventions) belongs in CLAUDE.md. Enforcement belongs in hooks." ([What happens when you stop adding rules](https://www.reddit.com/r/ClaudeAI/comments/1rz2oo3/what_happens_when_you_stop_adding_rules_to/))

- **Skills**: Contextually-triggered expertise that loads on demand. Use for things that apply to less than 20% of conversations. "If instructions apply to <20% of conversations, make it a skill instead of putting it in CLAUDE.md." ([Complete Guide V4](https://www.reddit.com/r/ClaudeAI/comments/1qquxle/the_complete_guide_to_claude_code_v4_the/), 655 upvotes)

- **Commands**: Manually triggered shortcuts (invoked with /). Use for repeatable workflows you want to invoke explicitly. "With command you need to explicitly mention it." ([Introducing Claude Skills](https://www.reddit.com/r/ClaudeCode/comments/1o8e62n/claude_code_is_introducing_claude_skills/))

- **Hooks**: Deterministic programmatic enforcement that runs regardless of what the LLM decides. "CLAUDE.md rules are suggestions Claude can ignore under context pressure. Hooks are deterministic -- they always run." ([Complete Guide V3](https://www.reddit.com/r/ClaudeAI/comments/1qe239d/the_complete_guide_to_claude_code_v3_lsp_claudemd/), 366 upvotes)

A key distinction from a power user with 6 months of experience (2,292 upvotes): "Commands drop everything in context when called. Skills have progressive disclosure. I use commands to compose multiple more granular skills when their knowledge is needed for a particular, repeatable workflow." ([Claude Code is a Beast](https://www.reddit.com/r/ClaudeAI/comments/1oivjvm/claude_code_is_a_beast_tips_from_6_months_of/))

---

## 2. Skill Architecture Best Practices {#2-skill-architecture-best-practices}

### The 500-Line Rule

This is the most consistently cited rule across dozens of threads. Anthropic's own 32-page guide on building skills enforces it ([Anthropic Released 32 Page Detailed Guide](https://www.reddit.com/r/ClaudeAI/comments/1r3hr40/anthropic_released_32_page_detailed_guide_on/), 1,477 upvotes):

- **SKILL.md must stay under 500 lines**. Move detailed content to reference files.
- A user who tested this found: "4.8x token efficiency isn't marginal improvement. It's the difference between 'works sometimes' and 'works reliably.'" ([I was wrong about Agent Skills](https://www.reddit.com/r/ClaudeAI/comments/1opxgq4/i_was_wrong_about_agent_skills_and_how_i_refactor/))
- "SKILL.md under 500 lines. Move domain content to reference files." ([How to build a skill in 10 minutes](https://www.reddit.com/r/ClaudeCode/comments/1rqnk1k/how_you_can_build_a_claude_skill_in_10_minutes/), 158 upvotes)

### The 200-Line Entry Point

A more aggressive optimization discovered by community members:

- "Keep the entry point under ~200 lines... Total: 400-700 lines of highly relevant context instead of 1,131 lines of mixed relevance. This is context engineering 101." ([I was wrong about Agent Skills](https://www.reddit.com/r/ClaudeCode/comments/1opxf9f/i_was_wrong_about_agent_skills_and_how_i_refactor/))
- "The 200-line rule matters. It's not a suggestion."

### Skill Directory Structure

```
.claude/skills/
  └── my-skill/
      ├── SKILL.md        # Required: instructions + YAML frontmatter (under 500 lines)
      ├── references/      # Optional: detailed docs loaded on demand
      ├── scripts/         # Optional: executable code
      └── templates/       # Optional: reference material
```

### YAML Frontmatter is Critical

The frontmatter `name` and `description` are the only two fields that determine when and how Claude triggers skills ([Deep Dive: Anatomy of a Skill](https://www.reddit.com/r/ClaudeAI/comments/1pha74t/deep_dive_anatomy_of_a_skill_its_tokenomics_why/)):

- **Keep description under 1,024 characters** and make it specific about when to trigger
- "If the description is vague, the skill won't fire when you need it. Something like 'generates conventional commit messages from staged diffs' is way more reliable than a vague one-liner." ([Useful cheatsheet for understanding Skills](https://www.reddit.com/r/Anthropic/comments/1qbpc9x/a_useful_cheatsheet_for_understanding_claude/), 56 upvotes)
- "Writing a generic description like 'handles git commits' means Claude might never load it because dozens of things could match."

### Skill Content Principles

- "All text serves the executing model. No design rationale, maintainer commentary, or 'how to extend' guidance in SKILL.md -- that belongs in docs/." ([How to build a skill in 10 minutes](https://www.reddit.com/r/ClaudeCode/comments/1rqnk1k/how_you_can_build_a_claude_skill_in_10_minutes/))
- "If an instruction is mechanical (same input -> same output, no judgment needed), write a script in .claude/scripts/ and have the skill call it." ([116-Configuration Claude Code Setup](https://www.reddit.com/r/ClaudeCode/comments/1rltiv7/inside_a_116configuration_claude_code_setup/))
- Skills should contain "decision trees, tool chains, verification steps, failure modes, and learned patterns from actual use." ([What Exactly Are Skills](https://www.reddit.com/r/ClaudeAI/comments/1rxz863/what_exactly_are_claudes_skills/), 48 upvotes)
- "Each skill teaches Claude how to perform a specific development task, not what a tool does."

---

## 3. The Progressive Disclosure Pattern {#3-progressive-disclosure}

Progressive disclosure is the single most important architectural pattern for skills. It is referenced in nearly every high-quality thread about skill design.

**How it works:**

1. **Startup**: Only the skill name and description are loaded (~50-100 tokens)
2. **Trigger**: When the conversation matches, the full SKILL.md body is loaded
3. **On-demand**: Reference files and scripts are loaded only when the skill deems them necessary

"Skills use progressive disclosure for token efficiency: Startup: Only name/description loaded (~50 tokens)." ([Complete Guide V4](https://www.reddit.com/r/ClaudeAI/comments/1qquxle/the_complete_guide_to_claude_code_v4_the/))

The disclosure hierarchy is: **YAML frontmatter -> skill body -> examples & additional references** ([Claude Skills Vs Claude + MCP](https://www.reddit.com/r/ClaudeCode/comments/1q6j6e0/claude_skills_vs_claude_mcp/))

**Why it matters:**

- "Loading 5-7 skills meant 5,000-7,000 lines flooding the context window immediately. I thought this was just how it had to be." This is the pre-progressive-disclosure antipattern. ([I was wrong about Agent Skills](https://www.reddit.com/r/ClaudeCode/comments/1opxf9f/i_was_wrong_about_agent_skills_and_how_i_refactor/))
- "Same functionality, massive efficiency gain. Now only the skill name and description live in context (~500 tokens). When Claude needs it, it reads the skill.md." ([Agent Skills open standard](https://www.reddit.com/r/ClaudeAI/comments/1ppw38d/agent_skills_is_now_an_open_standard/), 557 upvotes)
- "SKILL.md is just the map. Test the cold start -- Clear your context, activate the skill, and measure. If it loads more than 500 lines on first activation, you're doing it wrong."

**The modularization approach for CLAUDE.md itself:**

"Point to files, don't inline everything. My CLAUDE.md links to separate docs (style guides, hook configs, etc.) with file paths. The agent reads them when it actually needs them instead of loading everything on every conversation." ([What to include in CLAUDE.md](https://www.reddit.com/r/ClaudeCode/comments/1rohbj0/what_to_include_in_claudemd_and_what_not/))

---

## 4. CLAUDE.md Design Principles {#4-claudemd-design-principles}

### Keep It Lean

The community consensus is overwhelmingly clear:

- **"Your claude.md should not exceed 200 lines."** ([Claude Code Hooks guide](https://www.reddit.com/r/ClaudeAI/comments/1rxu41b/claude_code_hooks_all_23_explained_and_implemented/), 262 upvotes, citing Anthropic best practices)
- "Keep CLAUDE.md lean: coding conventions, project structure overview, and hard rules only. Things like 'use TypeScript strict mode' or 'API routes go in src/routes.' Nothing that changes often." ([Claude.md best practices](https://www.reddit.com/r/ClaudeCode/comments/1riwy13/claudemd_best_practices/))
- "You want to keep it as minimal as possible. Don't put any code in it."
- Use directory-level CLAUDE.md files that "layer on top of the root one. So the root stays short and generic, each subdirectory adds its own context."

### What Belongs in CLAUDE.md

- Project architecture overview (brief)
- Coding conventions and style rules
- Hard constraints ("never do X")
- Build/test commands
- Key architectural decisions and their rationale
- Technology stack and versions

### What Does NOT Belong in CLAUDE.md

- Detailed implementation instructions (use skills)
- Code examples longer than a few lines (use reference files)
- Anything that applies to less than 20% of conversations (use skills)
- Things that change frequently
- Anything the model can deduce from the codebase itself

### The "Specific Beats Comprehensive" Principle

This finding emerged from the AGENTS.md research discussion: "We settled on keeping context files focused on anti-patterns and decision rationale rather than general guidelines. Specific beats comprehensive every time." ([AGENTS.md reduce success rates](https://www.reddit.com/r/ClaudeAI/comments/1r7mvja/new_research_agentsmd_files_reduce_coding_agent/))

Actionable version: "Instructing Claude to follow certain development principles saved me from a lot of trouble, like over-engineering: SRP, DRY, KISS, YAGNI." ([Code quality of Claude](https://www.reddit.com/r/ClaudeAI/comments/1ptcbm3/code_quality_of_claude_a_sad_realization/))

---

## 5. Hooks: The Deterministic Enforcement Layer {#5-hooks-deterministic-enforcement}

This is perhaps the strongest consensus finding across all threads: **for anything that must always happen, use hooks, not instructions.**

### The Core Insight

"The real fix is moving your critical rules out of the prompt entirely and into deterministic checks that fire before the action executes. Prompt says 'don't delete files.' Infrastructure actually blocks the delete. Only one of those works at 2am with nobody watching." ([What happens when you stop adding rules](https://www.reddit.com/r/ClaudeAI/comments/1rz2oo3/what_happens_when_you_stop_adding_rules_to/))

"The community's verdict is clear: your extensive guardrail system of .md files and memory prompts are just 'suggestions' that Claude is free to ignore. You can't trust the AI to police itself. Hooks are King. This is the top-voted advice. Stop writing process docs and start writing deterministic code." ([Claude ignores its own plans](https://www.reddit.com/r/ClaudeAI/comments/1se1olb/claude_ignores_its_own_plans_memory_and/))

### From the Claude Certified Architect Exam

"Three distractor patterns that repeat across all 5 domains: 'Improve the system prompt' vs 'Add a hook.' Whenever the scenario describes a reliability issue -- agent skipping steps, ignoring rules -- one answer says enhance the prompt and another says add programmatic enforcement." The correct answer is always: add the hook. ([Claude Certified Architect exam notes](https://www.reddit.com/r/ClaudeCode/comments/1s3hbv3/notes_from_studying_the_claude_certified/))

### Hook Types and Uses

- **PreToolUse**: Intercept and validate tool calls before execution. "PreToolUse hooks for the critical guardrails, text instructions for everything else." ([Hooks explained](https://www.reddit.com/r/ClaudeAI/comments/1rxu41b/claude_code_hooks_all_23_explained_and_implemented/))
- **PostToolUse**: Log, validate outputs, run linters after file edits
- **Stop hooks**: Run quality gates at end of turn
- **UserPromptSubmit**: Re-inject context on every prompt

Real-world examples:
- "I had a rule in CLAUDE.md that said 'always run typecheck after editing a file.' Claude followed it sometimes. Ignored it when it was deep in a task. So I replaced the rule with a lifecycle hook." ([What happens when you stop adding rules](https://www.reddit.com/r/ClaudeAI/comments/1rz2oo3/what_happens_when_you_stop_adding_rules_to/))
- "I built a fairly robust set of tools... but literally NOTHING in Claude.md could consistently enforce it. I gave up on my Max plan after spending most of a month swearing at it... I saw the hooks feature and gave the pre tool call hooks a try and it mostly does what I want." ([Claude ignores rules](https://www.reddit.com/r/ClaudeAI/comments/1q9y79q/claude_flat_out_ignores_rules_aka_how_can_i_get/))

### The Orientation vs Enforcement Split

This is a framework endorsed by multiple high-upvote threads:

| Layer | What It Does | Where It Lives |
|-------|-------------|----------------|
| **Orientation** | Project identity, tech stack, conventions | CLAUDE.md |
| **Guidance** | Best practices, patterns, workflow knowledge | Skills |
| **Enforcement** | Rules that must always be followed | Hooks + scripts |

"The split that helped me most: orientation vs. enforcement. Orientation belongs in CLAUDE.md." ([What happens when you stop adding rules](https://www.reddit.com/r/ClaudeAI/comments/1rz2oo3/what_happens_when_you_stop_adding_rules_to/))

---

## 6. Common Failure Modes and Prevention {#6-failure-modes}

### Failure Mode 1: Context Drift in Long Sessions

"The drift is real. Once the context window fills up, Claude starts losing track of earlier decisions and repeating work." ([Long Claude Code sessions](https://www.reddit.com/r/ClaudeCode/comments/1qzrao5/long_claude_code_sessions_start_drifting_what/))

"Claude Code injects CLAUDE.md into the very start of the conversation and never refreshes its own knowledge of this prompt. The longer the context window gets, the more it does what its training tells it, and the less it will obey your specific commands." ([What to do when Claude doesn't read CLAUDE.md](https://www.reddit.com/r/ClaudeAI/comments/1m8ao6f/what_do_you_do_when_claude_doesnt_read_claudemd/))

**Prevention:**
- Break work into small, self-contained tasks. "'Implement the login page' is better than 'build the auth system.'"
- Use /clear between phases
- "Long context doesn't mean good context"
- Use hooks to re-inject critical instructions via UserPromptSubmit

### Failure Mode 2: Skills Not Triggering

This was a major pain point reported by power users:

"We're talking thousands of lines of best practices, patterns, and examples. And then... nothing. Claude just wouldn't use them. I'd literally use the exact keywords from the skill descriptions. Nothing." ([Claude Code is a Beast](https://www.reddit.com/r/ClaudeAI/comments/1oivjvm/claude_code_is_a_beast_tips_from_6_months_of/), 2,292 upvotes)

"In tests, Skills didn't help 56% of the time because the AI didn't even realize it had them or needed to check them. Even at its best, it only hit a 79% success rate." (Vercel research, cited in [multiple threads](https://www.reddit.com/r/google_antigravity/comments/1qvz088/tip_why_agentsmd_beats_agent_skills_every_time/))

**Prevention:**
- Make descriptions extremely specific about trigger conditions
- Use hooks to force skill activation: "That's when I had the idea of using hooks [to auto-activate skills]."
- Create a skill-rules.json and wire it to hooks for deterministic activation
- Keep the description under 1,024 characters but highly specific

### Failure Mode 3: Claude Ignoring CLAUDE.md Rules

"I built a fairly robust set of tools invoked by shell scripts... but literally NOTHING in Claude.md could consistently enforce it not making direct calls to docker or npm. Whatever core patterns are baked in always overrode what I considered fairly simple instructions." ([Claude ignores rules](https://www.reddit.com/r/ClaudeAI/comments/1q9y79q/claude_flat_out_ignores_rules_aka_how_can_i_get/))

**Prevention:**
- "Use hooks to programmatically and consistently verify behavior you care about." ([When Claude doesn't read CLAUDE.md](https://www.reddit.com/r/ClaudeAI/comments/1m8ao6f/what_do_you_do_when_claude_doesnt_read_claudemd/))
- /clear and start again when drift is severe
- Keep CLAUDE.md short -- longer files get less attention

### Failure Mode 4: Over-Engineered Instructions

"Many of us have been in situation like: 'hey Claude - NEVER EVER DO THAT AGAIN!'... and boom! you get extra rows in instructions. And over time, it will be too long to be useful." ([Hooks guide](https://www.reddit.com/r/ClaudeAI/comments/1rxu41b/claude_code_hooks_all_23_explained_and_implemented/))

**Prevention:**
- Regularly audit and prune CLAUDE.md
- Move reactive rules into hooks instead of accumulating them in text
- "The doc over time also helps me to understand which things are not part of its training data" -- only document what Claude gets wrong natively

### Failure Mode 5: Compaction Destroying Context

"The compaction issue is real... When context gets compacted, the CLAUDE.md still gets loaded fresh. Think of it as persistent memory that survives compaction." ([Managing context in Claude Code](https://www.reddit.com/r/ClaudeAI/comments/1rrkv0h/how_are_you_guys_managing_context_in_claude_code/), 81 upvotes, 74-upvote comment)

**Prevention strategies (in order of community endorsement):**
1. Use CLAUDE.md as persistent memory that reloads after compaction
2. Break work into smaller sessions that stay within context limits
3. Use /compact proactively with instructions about what to preserve
4. Offload plans and state to actual files (PLAN.md, TODO.md) that Claude reads from disk
5. Create session-summary commands that write handoff docs
6. "Claude compresses prose aggressively but preserves structured data almost perfectly" -- use structured formats

---

## 7. The AGENTS.md Research: What the Data Says {#7-agentsmd-research}

An ETH Zurich paper (arxiv.org/abs/2602.11988) evaluated whether repo-level context files (AGENTS.md, CLAUDE.md equivalents) actually help coding agents. The findings were widely discussed across Reddit ([New research: AGENTS.md files reduce success rates](https://www.reddit.com/r/ClaudeAI/comments/1r7mvja/new_research_agentsmd_files_reduce_coding_agent/), [ETH Zurich study](https://www.reddit.com/r/machinelearningnews/comments/1rev9lc/new_eth_zurich_study_proves_your_ai_coding_agents/), [Research: repo-level MD files reduce quality](https://www.reddit.com/r/ClaudeCode/comments/1r95h0c/research_seems_to_show_that_repolevel_md_files/), 119 upvotes).

### Key Findings

1. **LLM-generated context files reduce task success rates by ~3%** while increasing inference costs by 20%+
2. **Human-written context files yield a marginal ~4% improvement**, but only for smaller models
3. Both types encourage "broader exploration (more thorough testing and file traversal)" and agents "tend to respect their instructions" -- but this doesn't translate to higher success
4. Auto-generated content "basically repeats what's already written in the code and yields no positive effects"

### Community Interpretation

"This paper argues that LLM generated .MD files hurt the most, because they basically repeat what's already written in the code and yield no positive effects. Human written .MD files that are kept to a minimum and only focus on things the model wouldn't deduce from the codebase itself seem at least to yield a minimal positive impact." ([Research discussion](https://www.reddit.com/r/ClaudeCode/comments/1r95h0c/research_seems_to_show_that_repolevel_md_files/))

"Poorly structured context files increase cost 20%+ and reduce success rates." ([AI Agents thread](https://www.reddit.com/r/AI_Agents/comments/1rs8f1v/ive_been_building_with_ai_agents_for_months_the/))

### Practical Takeaway

Context files work when they are:
- **Human-written** (not auto-generated)
- **Minimal** -- only covering what can't be inferred from code
- **Focused on anti-patterns and decision rationale** rather than general guidelines
- **Specific** rather than comprehensive
- Combined with distributed, directory-level files rather than one giant file

"The actual token-level context it provides matters less than the fact that writing it forces you to articulate things about your codebase that were previously just in your head." ([Programming thread](https://www.reddit.com/r/programming/comments/1r89c8e/evaluating_agentsmd_are_repositorylevel_context/))

---

## 8. Context Window Management and Compaction {#8-context-management}

The dominant strategy endorsed by the community ([Managing context](https://www.reddit.com/r/ClaudeAI/comments/1rrkv0h/how_are_you_guys_managing_context_in_claude_code/)):

> "Stop treating the context window as your primary memory and start using files instead."

### The File-as-Memory Pattern

1. **CLAUDE.md** as persistent rules that survive compaction
2. **PLAN.md / TODO.md** for current work state, updated by Claude as it works
3. **Session handoff docs** -- structured summaries written at end of session
4. "Claude compresses prose aggressively but preserves structured data almost perfectly" -- format critical info as structured data

### Advanced Compaction Strategies

- "Use /config to turn auto compact off. Then use remaining space to summarize into .md file. Then /config re-enable, and first command after compact is to review the MD file." ([Preventing focus loss](https://www.reddit.com/r/ClaudeAI/comments/1plgyff/how_to_prevent_claude_code_from_losing_its_focus/))
- A hook to intercept auto-compact, grab the todo list, /clear, then reinject context ([Context loss after compaction](https://www.reddit.com/r/ClaudeCode/comments/1lw5cjm/context_loss_on_claude_code_after_context/))
- "When compaction fires, Claude reads the latest handoff to rebuild context -- same as starting a new session." The handoff template has a "Files to Load Next Session" field. ([CLAUDE.md for compaction](https://www.reddit.com/r/ClaudeAI/comments/1r43dzl/new_claudemd_that_solves_the_compactioncontext/))
- The "materialized context graph on disk" approach -- better than in-conversation compaction ([Solving compaction](https://www.reddit.com/r/ClaudeAI/comments/1r06z4r/i_built_a_claudemd_that_solves_the/))

---

## 9. Instruction Design for Reliable Compliance {#9-instruction-design}

### Fundamental Prompt Structure

From high-engagement threads across r/ChatGPTPromptGenius and r/PromptEngineering ([Best Practices for Prompting 2025](https://www.reddit.com/r/ChatGPTPromptGenius/comments/1nytjzy/best_practices_for_ai_prompting_2025/)):

1. **Role/Persona** -- who the AI should act as
2. **Context** -- what background info it needs
3. **Task** -- what you want done explicitly
4. **Format** -- how you want output structured
5. **Constraints** -- what to avoid or limits to follow

### XML Tags for Structure

"Structuring your prompts using XML achieves better results because it helps Claude parse your prompt more accurately." ([The Only Prompt You Need](https://www.reddit.com/r/ClaudeAI/comments/1gds696/the_only_prompt_you_need/), 1,562 upvotes)

### Short and Specific Wins

"The biggest improvement for me was keeping prompts short and specific with one example. 'Rewrite this function to handle null values. Here's the current code:' beats a 500-word instruction every time." ([The Only Prompt You Need](https://www.reddit.com/r/ClaudeAI/comments/1gds696/the_only_prompt_you_need/))

### Planning Before Execution

"Slow and steady wins. Plan. Plan some more. Maybe a little more. Then let CC loose. It will save you time in the long run." (30-upvote answer to [Best Practices for Claude Code](https://www.reddit.com/r/ClaudeCode/comments/1nris9w/what_are_your_best_practices_for_claude_code/))

### TDD as a Guardrail

"I run prompts that instruct it to follow TDD. Write failing tests for the spec, verify failing, implement code, verify passing. Then verify that linting and the full test suite passes. The resulting code is then fed to another sub agent for review against the spec." (21-upvote answer on [guardrails](https://www.reddit.com/r/ClaudeCode/comments/1q19o4r/what_guardrails_are_you_using_in_the_claudecode/))

"Spec driven development where the specs become the guardrails." ([Making specs the guardrails](https://www.reddit.com/r/ClaudeAI/comments/1q6uhg8/a_better_way_to_develop_making_the_specs_the/))

---

## 10. Anti-Patterns to Avoid {#10-anti-patterns}

### Do NOT:

1. **Put everything in one giant CLAUDE.md** -- "The drift is real" and instructions at the top get ignored as context grows

2. **Auto-generate context files with LLMs** -- ETH Zurich research shows these actively hurt performance by repeating what's in the code ([Research](https://www.reddit.com/r/machinelearningnews/comments/1rev9lc/new_eth_zurich_study_proves_your_ai_coding_agents/))

3. **Rely on CLAUDE.md for enforcement** -- "Your extensive guardrail system of .md files and memory prompts are just 'suggestions' that Claude is free to ignore" ([Claude ignores plans](https://www.reddit.com/r/ClaudeAI/comments/1se1olb/claude_ignores_its_own_plans_memory_and/))

4. **Make skill descriptions vague** -- "Writing a generic description like 'handles git commits' means Claude might never load it"

5. **Stuff SKILL.md with everything upfront** -- "Put everything in one giant SKILL.md file so the agent has all the information upfront" is the anti-pattern that causes 5,000-7,000 line context floods

6. **Create skills for everything** -- "Don't try to overcomplicate it if you don't NEED anything. If you are happy with raw CC, just use that. When you come to a point where you're getting frustrated with the same thing over and over again, then try to address it with a skill." ([Struggling with Skills](https://www.reddit.com/r/ClaudeAI/comments/1qvvn04/struggling_to_see_the_value_of_claude_code_skills/))

7. **Use skills for complex, iterative work** -- "Anything where you need to iterate. Direct Claude Code with one continuous session beats 7 agents trying to coordinate." Skills work best for "simple, self-contained actions."

8. **Trust the model to self-enforce** -- "The only way to prevent slop is with hooks or external tools (pre-commit, linting, security scans); everything else is non-deterministic." ([Guardrails discussion](https://www.reddit.com/r/ClaudeCode/comments/1q19o4r/what_guardrails_are_you_using_in_the_claudecode/))

9. **Treat context length as the solution** -- "The 200K limit is workable once you stop treating context as your primary memory and start treating files as memory instead. Models that have 1M context have similar drift problems at that scale."

10. **Skip the hooks when the rule matters** -- From the Architect exam: the correct answer for reliability issues is always "add programmatic enforcement," never "improve the system prompt"

---

## Summary: The Reliable Skill Checklist

For any skill/ability you build:

- [ ] YAML frontmatter has specific, trigger-word-rich description under 1,024 chars
- [ ] SKILL.md body is under 500 lines (ideally under 200 for the entry point)
- [ ] Detailed content lives in references/ or scripts/ subdirectories
- [ ] Instructions serve the executing model -- no meta-commentary or maintainer notes
- [ ] Decision trees, verification steps, and failure modes are documented
- [ ] Mechanical tasks are scripts, not instructions
- [ ] Critical enforcement rules are hooks, not text instructions
- [ ] Content cannot be inferred from the codebase itself
- [ ] Focused on anti-patterns and decision rationale, not general guidelines
- [ ] Tested with a cold start to verify context load stays reasonable

---

## Source URLs

- [The Complete Guide to Claude Code V2 (508 upvotes)](https://www.reddit.com/r/ClaudeAI/comments/1qcwckg/the_complete_guide_to_claude_code_v2_claudemd_mcp/)
- [The Complete Guide to Claude Code V3 (366 upvotes)](https://www.reddit.com/r/ClaudeAI/comments/1qe239d/the_complete_guide_to_claude_code_v3_lsp_claudemd/)
- [The Complete Guide to Claude Code V4 (655 upvotes)](https://www.reddit.com/r/ClaudeAI/comments/1qquxle/the_complete_guide_to_claude_code_v4_the/)
- [Claude Code is a Beast - Tips from 6 Months (2,292 upvotes)](https://www.reddit.com/r/ClaudeAI/comments/1oivjvm/claude_code_is_a_beast_tips_from_6_months_of/)
- [Anthropic's 32-Page Guide on Skills (1,477 upvotes)](https://www.reddit.com/r/ClaudeAI/comments/1r3hr40/anthropic_released_32_page_detailed_guide_on/)
- [The Only Prompt You Need (1,562 upvotes)](https://www.reddit.com/r/ClaudeAI/comments/1gds696/the_only_prompt_you_need/)
- [The 5 Levels of Claude Code (1,043 upvotes)](https://www.reddit.com/r/ClaudeAI/comments/1s1ipep/the_5_levels_of_claude_code_and_how_to_know_when/)
- [Agent Skills Open Standard (557 upvotes)](https://www.reddit.com/r/ClaudeAI/comments/1ppw38d/agent_skills_is_now_an_open_standard/)
- [The Busy Person's Intro to Claude Skills (523 upvotes)](https://www.reddit.com/r/ClaudeAI/comments/1pq0ui4/the_busy_persons_intro_to_claude_skills_a_feature/)
- [Claude Code Hooks - All 23 Explained (262 upvotes)](https://www.reddit.com/r/ClaudeAI/comments/1rxu41b/claude_code_hooks_all_23_explained_and_implemented/)
- [Claude Code Beast Examples Repo (298 upvotes)](https://www.reddit.com/r/ClaudeAI/comments/1ojqxbg/claude_code_is_a_beast_examples_repo_by_popular/)
- [I Was Wrong About Agent Skills (refactoring)](https://www.reddit.com/r/ClaudeAI/comments/1opxgq4/i_was_wrong_about_agent_skills_and_how_i_refactor/)
- [Deep Dive: Anatomy of a Skill](https://www.reddit.com/r/ClaudeAI/comments/1pha74t/deep_dive_anatomy_of_a_skill_its_tokenomics_why/)
- [What to Include in CLAUDE.md](https://www.reddit.com/r/ClaudeCode/comments/1rohbj0/what_to_include_in_claudemd_and_what_not/)
- [CLAUDE.md Best Practices](https://www.reddit.com/r/ClaudeCode/comments/1riwy13/claudemd_best_practices/)
- [Stop Bloating Your CLAUDE.md: Progressive Disclosure](https://www.reddit.com/r/ClaudeCode/comments/1qgkxh0/stop_bloating_your_claudemd_progressive/)
- [What Happens When You Stop Adding Rules](https://www.reddit.com/r/ClaudeAI/comments/1rz2oo3/what_happens_when_you_stop_adding_rules_to/)
- [Claude Ignores Plans, Memory, and Guardrails](https://www.reddit.com/r/ClaudeAI/comments/1se1olb/claude_ignores_its_own_plans_memory_and/)
- [Claude Flat Out Ignores Rules](https://www.reddit.com/r/ClaudeAI/comments/1q9y79q/claude_flat_out_ignores_rules_aka_how_can_i_get/)
- [What Do You Do When Claude Doesn't Read CLAUDE.md](https://www.reddit.com/r/ClaudeAI/comments/1m8ao6f/what_do_you_do_when_claude_doesnt_read_claudemd/)
- [AGENTS.md Reduces Success Rates (research)](https://www.reddit.com/r/ClaudeAI/comments/1r7mvja/new_research_agentsmd_files_reduce_coding_agent/)
- [ETH Zurich Study on AGENTS.md](https://www.reddit.com/r/machinelearningnews/comments/1rev9lc/new_eth_zurich_study_proves_your_ai_coding_agents/)
- [Research: Repo-Level MD Files Reduce Quality (119 upvotes)](https://www.reddit.com/r/ClaudeCode/comments/1r95h0c/research_seems_to_show_that_repolevel_md_files/)
- [Managing Context in Claude Code (81 upvotes)](https://www.reddit.com/r/ClaudeAI/comments/1rrkv0h/how_are_you_guys_managing_context_in_claude_code/)
- [Long Sessions Start Drifting](https://www.reddit.com/r/ClaudeCode/comments/1qzrao5/long_claude_code_sessions_start_drifting_what/)
- [CLAUDE.md for Compaction Problem](https://www.reddit.com/r/ClaudeAI/comments/1r43dzl/new_claudemd_that_solves_the_compactioncontext/)
- [Guardrails for Claude Code Workflow](https://www.reddit.com/r/ClaudeCode/comments/1q19o4r/what_guardrails_are_you_using_in_the_claudecode/)
- [Struggling with Skills Value](https://www.reddit.com/r/ClaudeAI/comments/1qvvn04/struggling_to_see_the_value_of_claude_code_skills/)
- [Claude Certified Architect Exam Notes](https://www.reddit.com/r/ClaudeCode/comments/1s3hbv3/notes_from_studying_the_claude_certified/)
- [116-Configuration Claude Code Setup](https://www.reddit.com/r/ClaudeCode/comments/1rltiv7/inside_a_116configuration_claude_code_setup/)
- [Useful Cheatsheet for Understanding Skills](https://www.reddit.com/r/Anthropic/comments/1qbpc9x/a_useful_cheatsheet_for_understanding_claude/)
- [How to Build a Skill in 10 Minutes (158 upvotes)](https://www.reddit.com/r/ClaudeCode/comments/1rqnk1k/how_you_can_build_a_claude_skill_in_10_minutes/)
- [Claude Code Extension Features Comparison](https://www.reddit.com/r/ClaudeAI/comments/1pvobog/claude_code_extension_features_commands_rules/)
- [Making Specs the Guardrails](https://www.reddit.com/r/ClaudeAI/comments/1q6uhg8/a_better_way_to_develop_making_the_specs_the/)
- [Deterministic Guardrails Instead of Prompt Rules](https://www.reddit.com/r/ClaudeAI/comments/1r3np57/stop_trying_to_make_ai_guardrails_unbreakable_put/)
- [Reverse Engineered Claude's Skills System](https://www.reddit.com/r/AI_Agents/comments/1s9i8io/i_reverse_engineered_claudes_skills_system_to_see/)
- [Best Practices for Prompting 2025](https://www.reddit.com/r/ChatGPTPromptGenius/comments/1nytjzy/best_practices_for_ai_prompting_2025/)
- [Claude Skills Vs Claude + MCP](https://www.reddit.com/r/ClaudeCode/comments/1q6j6e0/claude_skills_vs_claude_mcp/)
- [Preventing Focus Loss After Compaction](https://www.reddit.com/r/ClaudeAI/comments/1plgyff/how_to_prevent_claude_code_from_losing_its_focus/)
- [Evaluating AGENTS.md (r/programming)](https://www.reddit.com/r/programming/comments/1r89c8e/evaluating_agentsmd_are_repositorylevel_context/)
