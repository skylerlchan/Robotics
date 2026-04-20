# Research Survey: Effective Tools and Skills for LLM Agents

*Compiled: April 20, 2026*

---

## Table of Contents

1. [Tool-Use in LLMs: What Makes Tools Effective](#1-tool-use-in-llms-what-makes-tools-effective)
2. [Prompt Engineering Best Practices for Agent Systems](#2-prompt-engineering-best-practices-for-agent-systems)
3. [Agent Architectures and Skill/Capability Design](#3-agent-architectures-and-skillcapability-design)
4. [Reliability of LLM Tool-Calling and How to Improve It](#4-reliability-of-llm-tool-calling-and-how-to-improve-it)
5. [Structured Prompting, Chain-of-Thought, and Instruction Following](#5-structured-prompting-chain-of-thought-and-instruction-following)
6. [Key Takeaways and Design Principles](#6-key-takeaways-and-design-principles)

---

## 1. Tool-Use in LLMs: What Makes Tools Effective

### Foundational Papers

**Toolformer: Language Models Can Teach Themselves to Use Tools**
- Authors: Timo Schick, Jane Dwivedi-Yu et al. (Meta AI)
- Published: NeurIPS 2023
- Link: [arxiv.org/abs/2302.04761](https://arxiv.org/abs/2302.04761)
- Key finding: LLMs can learn to decide *which* APIs to call, *when* to call them, *what arguments* to pass, and *how* to incorporate results -- all in a self-supervised manner requiring only a handful of demonstrations per API. Toolformer achieved zero-shot performance competitive with much larger models while retaining core language abilities. This established that tool use is fundamentally about teaching models the meta-skill of knowing when a tool would help, not just how to format a call.

**Gorilla: Large Language Model Connected with Massive APIs**
- Authors: Shishir G. Patil, Sheng Zhang, Xin Wang, Joseph E. Gonzalez (UC Berkeley)
- Published: NeurIPS 2024
- Link: [arxiv.org/abs/2305.15334](https://arxiv.org/abs/2305.15334)
- Key finding: A fine-tuned LLaMA model that surpassed GPT-4 on writing API calls. Introduced Retriever Aware Training (RAT), which substantially mitigated hallucination when generating API calls. Demonstrated that combining retrieval with generation is critical for accurate tool use, especially as tool sets grow large and frequently update. Also introduced APIBench (HuggingFace, TorchHub, TensorHub APIs) and the Berkeley Function-Calling Leaderboard (BFCL).

**Tool Learning with Large Language Models: A Survey**
- Link: [arxiv.org/abs/2405.17935](https://arxiv.org/abs/2405.17935)
- Key finding: Comprehensive survey organizing tool learning into four key stages: (1) task planning, (2) tool selection, (3) parameter extraction, and (4) response generation. Argues that models must learn to decompose complex tasks into subtasks, dynamically adjust plans through reasoning, and select appropriate tools for each sub-task. Iterative interactions with tools -- adjusting sub-tasks progressively based on tool feedback -- is critical for complex problem-solving.

**Tool Learning with Foundation Models**
- Link: [arxiv.org/abs/2304.08354](https://arxiv.org/abs/2304.08354)
- Published: ACM Computing Surveys, 2024
- Key finding: Systematic investigation establishing that effective tool learning requires models to (1) understand available tools, (2) plan multi-step usage, and (3) adapt based on tool output. Tools must have clear descriptions, predictable behaviors, and composable interfaces.

### What Makes a Tool Effective: Synthesized Principles

The research converges on several properties of effective tools for LLM agents:

1. **Clear, contract-like descriptions**: Tool documentation should read like contracts -- a purpose line, crisp examples, and argument types that leave no room for guessing ([Anthropic Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use)).
2. **Predictable input/output behavior**: Tools with well-defined schemas and deterministic outputs are called more reliably.
3. **Composability**: Tools should be designed so they can be chained together. The four-stage pipeline (plan -> select -> parameterize -> integrate response) works best when tools have clean, narrow interfaces.
4. **Retrieval over enumeration**: When tool sets grow beyond ~20 tools, intelligent retrieval (Tool RAG) triples invocation accuracy while halving prompt length. Feeding all tools into a single prompt overwhelms the model ([Red Hat Emerging Tech](https://next.redhat.com/2025/11/26/tool-rag-the-next-breakthrough-in-scalable-ai-agents/)).
5. **Concrete usage examples**: Showing the model concrete usage patterns with input examples dramatically improves call accuracy beyond schema alone ([Anthropic Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use)).

---

## 2. Prompt Engineering Best Practices for Agent Systems

### Comprehensive Surveys

**The Prompt Report: A Systematic Survey of Prompt Engineering Techniques**
- Authors: Sander Schulhoff et al. (co-authored with OpenAI, Microsoft, Google, Princeton, Stanford)
- Published: June 2024
- Link: [arxiv.org/abs/2406.06608](https://arxiv.org/abs/2406.06608)
- Key finding: The most comprehensive survey on prompt engineering to date -- 76 pages analyzing 1,500+ academic papers. Establishes a vocabulary of 33 terms, a taxonomy of 58 text-based prompting techniques and 40 techniques for other modalities. Found that prompt engineering suffers from conflicting terminology and fragmented understanding, making standardization critical.

**A Systematic Survey of Prompt Engineering in Large Language Models: Techniques and Applications**
- Link: [arxiv.org/abs/2402.07927](https://arxiv.org/abs/2402.07927)
- Published: February 2024
- Key finding: Emphasizes that prompt engineering extends LLM capabilities *without modifying core model parameters*. The most impactful techniques are task-specific instructions combined with structured output specifications.

**Prompt Engineering and the Effectiveness of LLMs in Enhancing Human Productivity**
- Link: [arxiv.org/abs/2507.18638](https://arxiv.org/abs/2507.18638)
- Key finding: Users who employ clear, structured, and context-aware prompts report higher task efficiency and better outcomes. Structure and clarity of prompts directly impact LLM effectiveness.

### Anthropic: Building Effective Agents
- Published: December 2024
- Link: [anthropic.com/research/building-effective-agents](https://www.anthropic.com/research/building-effective-agents)
- Key finding: The most successful agent implementations use simple, composable patterns rather than complex frameworks. Identifies five workflow patterns:
  1. **Prompt chaining** -- sequential LLM calls where output feeds into the next
  2. **Routing** -- an initial call decides which downstream path to take
  3. **Parallelization** -- tasks split and run in parallel or via voting
  4. **Orchestrator-workers** -- one LLM triggers multiple calls that are synthesized
  5. **Evaluator-optimizer** -- one model checks another's work in a loop
- Core insight: "Start by using LLM APIs directly: many patterns can be implemented in a few lines of code." The foundational building block is an LLM augmented with retrieval, tools, and memory.

### Best Practices Synthesized from Research

1. **Specificity over vagueness**: Precise, goal-oriented phrasing with desired format, scope, tone, and length specified.
2. **Prompt scaffolding**: Wrap user inputs in structured templates that constrain model behavior and define how to think, respond, and decline.
3. **Structured output format**: Always specify output format (JSON, markdown, etc.) to avoid ambiguity and enable machine-readability.
4. **Iterative refinement**: Prompts should be refined through multiple rounds of testing with real feedback.
5. **ReAct pattern**: Combine internal reasoning with external tool calls for tasks requiring real-time information ([Prompting Guide](https://www.promptingguide.ai/)).

---

## 3. Agent Architectures and Skill/Capability Design

### Architecture Frameworks

**Cognitive Architectures for Language Agents (CoALA)**
- Authors: Theodore R. Sumers, Shunyu Yao, Karthik Narasimhan, Thomas L. Griffiths (Princeton)
- Published: Transactions on Machine Learning Research, 2024
- Link: [arxiv.org/abs/2309.02427](https://arxiv.org/abs/2309.02427)
- Key finding: Proposes a theoretical framework organizing language agents along three dimensions: (1) information storage (working + long-term memory), (2) action space (internal + external actions), and (3) decision-making (interactive loop with planning and execution). Grounded in cognitive science research on cognitive architectures. Used to retrospectively survey existing agent work and prospectively identify design directions.

**ReAct: Synergizing Reasoning and Acting in Language Models**
- Authors: Shunyu Yao, Jeffrey Zhao et al. (Princeton/Google)
- Published: ICLR 2023
- Link: [arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)
- Key finding: The seminal paper on interleaving reasoning traces with task-specific actions. Reasoning traces help the model induce, track, and update action plans and handle exceptions, while actions allow interfacing with external tools and knowledge bases. Tested on HotPotQA, Fever, ALFWorld, and WebShop. The ReAct pattern has become the de facto standard for agentic LLM systems.

**Agentic AI: Architectures, Taxonomies, and Evaluation of Large Language Model Agents**
- Link: [arxiv.org/html/2601.12560v1](https://arxiv.org/html/2601.12560v1)
- Published: January 2025
- Key finding: Comprehensive taxonomy of agent architectures, evaluation methods, and deployment patterns across the emerging agentic AI landscape.

**Fundamentals of Building Autonomous LLM Agents**
- Link: [arxiv.org/html/2510.09244v1](https://arxiv.org/html/2510.09244v1)
- Published: October 2025 (TUM seminar report)
- Scope: Technical survey of reasoning-enhanced, tool-augmented, multi-agent, and memory-augmented agent categories, analyzing 100+ papers from 2020-2024.

### Skill Design and Acquisition

**Agent Skills for Large Language Models: Architecture, Acquisition, Security, and the Path Forward**
- Link: [arxiv.org/abs/2602.12430](https://arxiv.org/abs/2602.12430)
- Published: February 2025
- Key finding: Defines "skill engineering" as a higher-order abstraction where a skill is a bundle including instructions, workflow guidance, executable scripts, reference documentation, and metadata -- all dynamically loaded when relevant. Distinguishes skills from raw tools: skills include applicability logic, multi-step sequencing, and explicit termination criteria. Direct human authoring is the most immediately impactful skill acquisition modality. Reports that Anthropic formalized agent skills in October 2025, with their skills repository accumulating 62,000+ GitHub stars within four months. A 30B parameter solver using dynamic skill composition achieved 91.6% on AIME 2025, demonstrating that skill composition can yield capabilities exceeding any individual skill.

**SoK: Agentic Skills -- Beyond Tool Use in LLM Agents**
- Authors: Yanna Jiang et al.
- Link: [arxiv.org/abs/2602.20867](https://arxiv.org/abs/2602.20867)
- Published: February 2026
- Key finding: Systematization of knowledge paper establishing that agentic skills are callable modules packaging procedural knowledge with explicit applicability conditions, execution policies, termination criteria, and reusable interfaces. Unlike tools (atomic primitives with fixed interfaces and no internal decision-making), skills invoke tools but extend them with applicability logic, multi-step sequencing, and termination criteria. Maps the skill lifecycle: discovery, practice, distillation, storage, composition, evaluation, and update. Introduces seven design patterns for how skills are packaged and executed.

**Agent Skill Acquisition for Large Language Models via CycleQD**
- Link: [arxiv.org/abs/2410.14735](https://arxiv.org/abs/2410.14735)
- Published: ICLR 2025
- Key finding: Uses Quality Diversity (QD) framework through MAP-Elites to train LLMs to acquire specific skills. Applied to LLaMA3-8B, the approach surpassed traditional fine-tuning and matched GPT-3.5-Turbo across coding, OS, and database tasks. Key innovations include model merging-based crossover for transferring skills between specialized experts, and SVD-based mutation to prevent overfitting.

**Voyager: An Open-Ended Embodied Agent with Large Language Models**
- Authors: Guanzhi Wang, Yuqi Xie et al. (NVIDIA/Caltech)
- Link: [arxiv.org/abs/2305.16291](https://arxiv.org/abs/2305.16291)
- Published: Transactions on Machine Learning Research, 2023
- Key finding: First LLM-powered embodied lifelong learning agent. Three key components: (1) automatic curriculum for exploration, (2) ever-growing skill library of executable code for storing/retrieving complex behaviors, and (3) iterative prompting with environment feedback and self-verification. Skills are temporally extended, interpretable, and compositional, compounding the agent's abilities while preventing catastrophic forgetting. Established the paradigm that skill libraries should grow over time and be retrieved contextually.

### Multi-Agent Systems

**MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework**
- Link: [arxiv.org/abs/2308.00352](https://arxiv.org/abs/2308.00352)
- Key finding: Integrates human workflows (Standardized Operating Procedures/SOPs) into LLM-based multi-agent collaboration. Uses an assembly line paradigm with role assignment and task decomposition. Demonstrates that encoding structured human workflows into prompt sequences improves multi-agent coordination.

**AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation**
- Authors: Microsoft Research
- Link: [arxiv.org/abs/2308.08155](https://arxiv.org/abs/2308.08155)
- Key finding: Framework for multi-agent conversation where agents communicate to solve tasks. Adopted an actor model for orchestration in 2024. Architecture provides flexibility through layered design including extensions like Magentic-One (generalist agent team).

**System Architecture for Agentic Large Language Models**
- Authors: Tianjun Zhang (UC Berkeley)
- Link: [www2.eecs.berkeley.edu/Pubs/TechRpts/2025/EECS-2025-5.pdf](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2025/EECS-2025-5.pdf)
- Published: Berkeley EECS Technical Report, 2025
- Scope: Comprehensive treatment of system-level architecture decisions for building agentic LLM systems.

---

## 4. Reliability of LLM Tool-Calling and How to Improve It

### Benchmarks and Evaluation

**Berkeley Function Calling Leaderboard (BFCL)**
- Link: [gorilla.cs.berkeley.edu/leaderboard.html](https://gorilla.cs.berkeley.edu/leaderboard.html)
- Paper: [proceedings.mlr.press/v267/patil25a.html](https://proceedings.mlr.press/v267/patil25a.html) (ICML 2025)
- Key finding: The standard benchmark for evaluating function-calling capabilities. Uses Abstract Syntax Tree (AST) evaluation across 2,000+ question-function-answer pairs in multiple languages (Python, Java, JavaScript, REST). BFCL V2 (Aug 2024) added enterprise-contributed data for real-world scenarios. BFCL V3 (Sep 2024) introduced multi-turn, multi-step evaluation. BFCL V4 added holistic agentic evaluation. Finding: While SOTA models excel at single-turn calls, memory, dynamic decision-making, and long-horizon reasoning remain open challenges.

**ToolSandbox: A Stateful, Conversational, Interactive Evaluation Benchmark for LLM Tool Use Capabilities**
- Authors: Apple Research
- Link: [arxiv.org/abs/2408.04682](https://arxiv.org/abs/2408.04682)
- Published: NAACL 2025 Findings
- Key finding: Introduces stateful tool execution with implicit state dependencies between tools, a built-in user simulator, and dynamic evaluation for intermediate milestones. Found significant performance gaps between open-source and proprietary models. Complex tasks involving state dependency, canonicalization, and insufficient information challenge even the most capable models.

**ToolACE: Winning the Points of LLM Function Calling**
- Published: ICLR 2025
- Link: [arxiv.org/abs/2409.00920](https://arxiv.org/abs/2409.00920)
- Key finding: Automatic agentic pipeline generating accurate, complex, diverse tool-learning data. Uses self-evolution synthesis to curate 26,507 diverse APIs, multi-agent dialog generation, and a dual-layer verification system (rule-based + model-based). With only 8B parameters, ToolACE significantly outperformed existing open-source models and was competitive with GPT-4. Demonstrates that data quality and diversity are paramount for tool-calling reliability.

### Methods for Improving Reliability

**Improving Large Language Models Function Calling and Interpretability via Guided-Structured Templates**
- Link: [arxiv.org/html/2509.18076v1](https://arxiv.org/html/2509.18076v1)
- Published: EMNLP 2025
- Key finding: Pre-execution structured reasoning (akin to extended CoT) before making function calls enhances both interpretability and performance. Guided-structured templates force the model through a reasoning step before committing to a tool call, reducing errors.

**ToolFlow: Boosting LLM Tool-Calling Through Natural and Coherent Dialogue Synthesis**
- Link: [aclanthology.org/2025.naacl-long.214](https://aclanthology.org/2025.naacl-long.214/)
- Published: NAACL 2025
- Key finding: Uses Graph-based Sampling for relevant tool combinations and Planned-generation for coherent dialogue synthesis. Fine-tuning LLaMA-3.1-8B on just 8,000 synthetic dialogues from ToolFlow achieved tool-calling performance comparable to or surpassing GPT-4. Naturalness and coherence of training data directly impact downstream reliability.

**Enhancing Function-Calling Capabilities in LLMs: Strategies for Prompt Formats, Data Integration, and Multilingual Translation**
- Link: [aclanthology.org/2025.naacl-industry.9](https://aclanthology.org/2025.naacl-industry.9/)
- Published: NAACL 2025 Industry Track
- Key finding: Explores prompt format design for function descriptions, blending function-calling and instruction-following data, introducing a "Decision Token" for conditional prompts, leveraging chain-of-thought reasoning, and multilingual translation pipelines.

**OpenAI Structured Outputs**
- Link: [openai.com/index/introducing-structured-outputs-in-the-api](https://openai.com/index/introducing-structured-outputs-in-the-api/)
- Key finding: Combining model training improvements with deterministic engineering constraints achieves 100% reliability in structured output generation. Setting `strict: true` in function definitions guarantees model arguments exactly match JSON Schema. This engineering approach (constraining output space via grammar/schema) is a crucial complement to model-level improvements.

**Model Context Protocol (MCP)**
- Authors: Anthropic
- Published: November 2024
- Link: [anthropic.com/news/model-context-protocol](https://www.anthropic.com/news/model-context-protocol)
- Key finding: Open standard for connecting AI assistants to data systems. Uses JSON-RPC 2.0 message flow (inspired by LSP). Defines three server primitives (Prompts, Resources, Tools) and two client primitives (Roots, Sampling). Over 1,000 community-built MCP servers within months. Donated to Linux Foundation's Agentic AI Foundation in December 2025. Standardization of tool interfaces across the ecosystem reduces ambiguity and improves reliability at the protocol level.

### Synthesized Reliability Principles

1. **Strict schemas**: Enforce JSON Schema validation on tool calls (strict mode) to eliminate malformed calls.
2. **Structured pre-reasoning**: Have the model reason about which tool to use and why before generating the call.
3. **High-quality training data**: Data quality matters more than quantity for tool-calling fine-tuning. Dual-layer verification (rule + model-based) catches errors.
4. **Stateful testing**: Evaluate tool use in stateful, multi-turn scenarios, not just single-call benchmarks.
5. **Tool retrieval over enumeration**: Use semantic search to surface only relevant tools per query.
6. **Standardized protocols**: MCP-style standards reduce ambiguity across the tool ecosystem.

---

## 5. Structured Prompting, Chain-of-Thought, and Instruction Following

### Foundational and Updated Research

**Chain-of-Thought Prompting Elicits Reasoning in Large Language Models**
- Authors: Jason Wei, Xuezhi Wang et al. (Google Brain)
- Published: NeurIPS 2022
- Link: [arxiv.org/abs/2201.11903](https://arxiv.org/abs/2201.11903)
- Key finding: The seminal paper showing that providing a few chain-of-thought examples enables LLMs to perform complex reasoning. CoT prompting is an emergent ability of model scale -- it substantially improves performance on arithmetic, commonsense, and symbolic reasoning benchmarks.

**The Decreasing Value of Chain of Thought in Prompting**
- Authors: Lennart Meincke, Ethan R. Mollick, Lilach Mollick, Dan Shapiro (Wharton)
- Published: June 2025
- Link: [papers.ssrn.com/sol3/papers.cfm?abstract_id=5285532](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5285532)
- Key finding: Critical reassessment showing CoT effectiveness varies significantly by model type and task. Non-reasoning models show modest average improvements but *increased variability*. Reasoning models (like o1) gain only marginal benefits from explicit CoT despite substantial time costs, because they already incorporate internal chain-of-thought. Implication: as models evolve built-in reasoning capabilities, explicit CoT prompting may become less necessary.

**Structured Chain-of-Thought Prompting for Code Generation (SCoT)**
- Published: ACM Transactions on Software Engineering and Methodology, January 2025
- Link: [ligechina.github.io/...SCoT](https://ligechina.github.io/My%20Papers/2025%20-%20TOSEM%20-%20Structured%20Chain-of-Thought%20Prompting%20for%20Code%20Generation.pdf)
- Key finding: Uses programming structures (if-else, loops) to build structured chain-of-thought reasoning, enabling nested structures for more complex solutions. Demonstrates that structuring the *format* of reasoning (not just asking "think step by step") yields better code generation.

### Instruction Following Research

**Instruction Tuning for Large Language Models: A Survey**
- Link: [arxiv.org/abs/2308.10792](https://arxiv.org/abs/2308.10792)
- Key finding: Comprehensive survey establishing that instruction tuning is the primary method for aligning LLMs to follow user instructions. Quality matters more than quantity -- high-quality instruction data consistently improves performance across different base models.

**A Survey on Data Selection for LLM Instruction Tuning**
- Link: [arxiv.org/abs/2402.05123](https://arxiv.org/abs/2402.05123)
- Published: February 2024
- Key finding: Explores methods for selecting high-quality subsets from instruction datasets. Mismatches between training data distribution and target model distribution can hurt performance. The GRAPE framework (NeurIPS 2025 Spotlight) tailors supervision by gathering responses aligned to the model's pretrained distribution.

**Enhancing LLM Tool Use with High-quality Instruction Data from Knowledge Graph**
- Link: [arxiv.org/html/2506.21071v1](https://arxiv.org/html/2506.21071v1)
- Key finding: Demonstrates that knowledge graph-derived instruction data improves tool use capabilities, bridging the gap between instruction following and tool calling.

---

## 6. Key Takeaways and Design Principles

### What Makes an Effective Tool for an LLM Agent

Based on synthesis of the above research:

| Principle | Evidence | Source |
|-----------|----------|--------|
| **Narrow, well-defined scope** | Tools with single, clear purposes are called more accurately than multi-function tools | Gorilla, BFCL benchmarks |
| **Contract-like documentation** | Purpose line, typed parameters, examples, and return format descriptions drastically improve call accuracy | Anthropic Advanced Tool Use |
| **Concrete usage examples** | Showing 2-3 input/output examples outperforms schema-only descriptions | Anthropic, ToolFlow |
| **Strict schema enforcement** | `strict: true` mode achieves 100% structural reliability | OpenAI Structured Outputs |
| **Composable design** | Tools should have clean interfaces enabling chaining; skill bundles compose tools into multi-step workflows | Voyager, Agent Skills survey |
| **Dynamic retrieval** | Use Tool RAG to surface only relevant tools per query (triples accuracy, halves prompt length) | Red Hat Tool RAG |
| **Standardized protocols** | MCP-style standards eliminate ambiguity across tool ecosystems | Anthropic MCP |
| **Stateful awareness** | Tools operating on shared state need explicit dependency documentation | Apple ToolSandbox |

### What Makes an Effective Skill/Capability Bundle

| Principle | Evidence | Source |
|-----------|----------|--------|
| **Beyond tool calls** | Skills package applicability conditions, execution policies, termination criteria, and reusable interfaces | SoK: Agentic Skills |
| **Lifecycle management** | Skills need discovery, practice, distillation, storage, composition, evaluation, and update phases | SoK: Agentic Skills |
| **Human-authored instructions** | Direct human authoring is the most immediately impactful skill acquisition method | Agent Skills survey |
| **Growing skill libraries** | Skill libraries that grow over time and are retrieved contextually compound agent capabilities | Voyager |
| **Composability yields emergence** | Skill composition can yield capabilities exceeding any individual skill (91.6% AIME 2025) | Agent Skills survey |

### Agent Architecture Principles

| Principle | Evidence | Source |
|-----------|----------|--------|
| **Start simple, add complexity as needed** | The most successful implementations use simple, composable patterns | Anthropic Building Effective Agents |
| **Interleave reasoning and acting** | ReAct pattern is the de facto standard | ReAct (ICLR 2023) |
| **Modular memory** | Separate working memory and long-term memory | CoALA |
| **Structured pre-reasoning before tool calls** | Forces better tool selection and parameter extraction | EMNLP 2025 Guided Templates |
| **Quality training data over quantity** | 8K high-quality dialogues can match GPT-4 tool-calling | ToolFlow (NAACL 2025) |
| **CoT is model-dependent** | Explicit CoT helps non-reasoning models but adds overhead for reasoning models with built-in CoT | Wharton 2025 report |

---

## Key Papers Quick Reference

| Paper | Venue/Year | Focus |
|-------|-----------|-------|
| [Toolformer](https://arxiv.org/abs/2302.04761) | NeurIPS 2023 | Self-supervised tool learning |
| [Gorilla](https://arxiv.org/abs/2305.15334) | NeurIPS 2024 | API calling with retrieval |
| [ReAct](https://arxiv.org/abs/2210.03629) | ICLR 2023 | Reasoning + acting interleaving |
| [Voyager](https://arxiv.org/abs/2305.16291) | TMLR 2023 | Embodied skill library |
| [CoALA](https://arxiv.org/abs/2309.02427) | TMLR 2024 | Cognitive architecture framework |
| [The Prompt Report](https://arxiv.org/abs/2406.06608) | arXiv 2024 | 58-technique prompting taxonomy |
| [ToolACE](https://arxiv.org/abs/2409.00920) | ICLR 2025 | Tool-calling data synthesis |
| [ToolFlow](https://aclanthology.org/2025.naacl-long.214/) | NAACL 2025 | Coherent dialogue synthesis for tool-calling |
| [ToolSandbox](https://arxiv.org/abs/2408.04682) | NAACL 2025 Findings | Stateful tool-use evaluation |
| [BFCL](https://gorilla.cs.berkeley.edu/leaderboard.html) | ICML 2025 | Function-calling benchmark |
| [Agent Skills](https://arxiv.org/abs/2602.12430) | arXiv 2025 | Skill architecture and acquisition |
| [SoK: Agentic Skills](https://arxiv.org/abs/2602.20867) | arXiv 2026 | Skill lifecycle and design patterns |
| [CycleQD](https://arxiv.org/abs/2410.14735) | ICLR 2025 | Quality-diversity skill acquisition |
| [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) | Anthropic 2024 | Agent design patterns |
| [MCP](https://www.anthropic.com/news/model-context-protocol) | Anthropic 2024 | Tool protocol standard |
| [Structured Outputs](https://openai.com/index/introducing-structured-outputs-in-the-api/) | OpenAI 2024 | Schema-enforced reliability |
| [CoT Decreasing Value](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5285532) | Wharton 2025 | CoT effectiveness by model type |
| [MetaGPT](https://arxiv.org/abs/2308.00352) | arXiv 2023 | Multi-agent SOP framework |
| [AutoGen](https://arxiv.org/abs/2308.08155) | arXiv 2023 | Multi-agent conversation |
| [Guided-Structured Templates](https://arxiv.org/html/2509.18076v1) | EMNLP 2025 | Pre-reasoning for function calling |
