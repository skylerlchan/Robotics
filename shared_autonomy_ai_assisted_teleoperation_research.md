# Shared Autonomy, AI-Assisted Teleoperation, and Learning from Demonstration

**Research Date:** April 20, 2026

**Core Insight:** The solution to teleoperation difficulty is not making pure teleoperation easier, but having AI handle the hard parts while the human provides high-level guidance.

---

## Table of Contents

1. [Shared Autonomy Systems](#1-shared-autonomy-systems)
2. [AI-Assisted / Corrective Teleoperation](#2-ai-assisted--corrective-teleoperation)
3. [Action & Skill Primitives](#3-action--skill-primitives)
4. [Learning from Demonstration (LfD) - Data Requirements](#4-learning-from-demonstration-lfd---data-requirements)
5. [Diffusion Policies & ACT](#5-diffusion-policies--act)
6. [Keyframe vs. Continuous Teleoperation](#6-keyframe-vs-continuous-teleoperation)
7. [Levels of Abstraction in Teleoperation](#7-levels-of-abstraction-in-teleoperation)
8. [Google RT-2 & DeepMind's Approach](#8-google-rt-2--deepminds-approach)
9. [NVIDIA Sim-to-Real](#9-nvidia-sim-to-real)
10. [Mobile ALOHA & State-of-the-Art Data Collection](#10-mobile-aloha--state-of-the-art-data-collection)
11. [Click-Based & Point-and-Click Interfaces](#11-click-based--point-and-click-interfaces)
12. [Language, Gesture, and Alternative Interfaces](#12-language-gesture-and-alternative-interfaces)
13. [The Copilot Paradigm](#13-the-copilot-paradigm)
14. [Foundation Models for Robot Control](#14-foundation-models-for-robot-control)
15. [Key Takeaways & Implications](#15-key-takeaways--implications)

---

## 1. Shared Autonomy Systems

### Where Does Human Control End and AI Begin?

Shared autonomy occupies the space between full teleoperation and full autonomy. The fundamental question is how to blend human intent with robot capability in real-time.

**Core Framework:** Between teleoperation and full autonomy lies a continuum of shared control. Autonomy may vary from low to high for each of the robot primitives: sense, plan, and act ([Toward a Framework for Levels of Robot Autonomy](https://pmc.ncbi.nlm.nih.gov/articles/PMC5656240/)).

**How it works in practice:**
- The human provides coarse, high-level motion commands
- The AI copilot corrects local position and orientation errors
- The system infers operator intent and provides manipulation assistance
- Performance improves as control is gradually given to the robot's autonomy ([Frontiers | Editorial: Shared Control for Tele-Operation Systems](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2022.915187/full))

**Key Design Challenges:**
- When should the robot follow the human vs. override?
- What happens when human and AI intent conflict?
- How to maintain the operator's "sense of agency" while improving performance?
- How to dynamically adjust the level of autonomy based on task difficulty? ([The Sense of Agency in Assistive Robotics Using Shared Autonomy](https://arxiv.org/html/2501.07462v1))

**Variable Autonomy Approach:** In teleoperated scenarios, humans drive the base or move the arm, with autonomy serving in an assistive capacity. The main objective is lowering human cognitive load or reducing the operation completion time ([Frontiers | A Mini-Review on Mobile Manipulators with Variable Autonomy](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2025.1540476/full)).

---

## 2. AI-Assisted / Corrective Teleoperation

### AI Correcting or Stabilizing Operator Inputs

The most promising near-term approach: let the human provide rough intentions, and have AI clean up the execution.

**Task-Parameterized Models:** A hidden semi-Markov model learns manipulation skills from demonstrations, then predicts the manipulation target and estimates desired robotic motion given current operator input. The estimated motion corrects the operator's input and provides manipulation assistance ([Sage Journals - Robotic Shared Control via LfD](https://journals.sagepub.com/doi/10.1177/1729881419857428)).

**Residual Copilot Formulation:** Residual formulations naturally separate roles: the pilot provides high-level motion commands while the residual copilot applies low-level corrections for alignment, contact regulation, and robustness. This preserves human intent while improving performance ([Efficient and Reliable Teleoperation through Real-to-Sim-to-Real Shared Autonomy](https://arxiv.org/html/2603.17016v1)).

**Kinematic Correction:** A kinematic correction module can autonomously resolve kinematic constraints, reducing the operator's cognitive and physical load by shifting the burden of kinematic resolution from the human to the system ([User-customizable Shared Control for Robot Teleoperation via Virtual Reality](https://arxiv.org/html/2403.13177v2)).

**Real-to-Sim-to-Real Pipeline (2026):**
A key recent advance uses less than 5 minutes of real-world teleoperation data to create a human surrogate model in simulation, then trains a residual copilot policy with reinforcement learning that transfers back to the real world. This enables stable corrective policies with minimal real data ([Efficient and Reliable Teleoperation through Real-to-Sim-to-Real Shared Autonomy](https://arxiv.org/abs/2603.17016)).

---

## 3. Action & Skill Primitives

### "Grasp Corner" Instead of 6-DoF Joint Control

Skill-based teleoperation is a paradigm where the operator commands a robot through semantic, parameterized, or low-dimensional "skills" - such as grasp, move, pour, push, or manipulate - rather than issuing low-level joint or velocity commands ([Skill-Based Teleoperation](https://www.emergentmind.com/topics/skill-based-teleoperation)).

**Standard Primitive Library:**
A typical library includes five primitives:
1. **Reach** - move end-effector to a target pose
2. **Grasp** - close gripper with appropriate force
3. **Push** - apply force in a direction
4. **Release** - open gripper
5. **Atomic** - task-specific compound motions

([Movement Primitives in Robotics: A Comprehensive Survey](https://arxiv.org/html/2601.02379v1))

**Hierarchical Approach:**
- Movement primitives encode basic motions at the trajectory level (e.g., how to grasp a cup)
- These can be combined to achieve complex tasks
- Primitives generalize across environmental variations
- Policy improvement optimizes primitive parameters ([Robot Skill Learning via Compliant Movement Primitives](https://link.springer.com/article/10.1007/s10846-022-01605-4))

**Task-Level Authoring:** Operators specify shorter sequences of high-level commands, creating periods of variable robot autonomy. Instead of continuous control, the operator issues semantic commands like "pick up that object" and the robot handles trajectory planning and execution ([Task-Level Authoring for Remote Robot Teleoperation](https://pmc.ncbi.nlm.nih.gov/articles/PMC8502825/)).

**Key Insight:** The operator's role shifts from "puppet master" to "task director" - specifying WHAT to do rather than HOW to do it.

---

## 4. Learning from Demonstration (LfD) - Data Requirements

### How Much Teleoperation Data Do You Actually Need?

The answer varies dramatically based on the approach:

| Approach | Demonstrations Needed | Notes |
|----------|----------------------|-------|
| RoboCLIP | **1 video** | Zero-shot from single video/text description ([RoboCLIP](https://openreview.net/forum?id=DVlawv2rSI)) |
| Gaussian Process | **1-5 demos** | Non-parametric, good for subtasks |
| ACT (ALOHA) | **50 demos** | 80-90% success on fine manipulation tasks |
| Mobile ALOHA (with co-training) | **50 demos** | Complex mobile manipulation with 80%+ success |
| Diffusion Policy | **50-200 demos** | Consistent 46.9% improvement over baselines |
| Standard Behavior Cloning | **200-1000+ demos** | More data-hungry, less sample efficient |

**Key Finding from ACT/ALOHA:** Only 10 minutes of demonstration data is sufficient to learn 6 difficult tasks (opening condiment cups, slotting batteries) at 80-90% success rate ([Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware](https://arxiv.org/abs/2304.13705)).

**Co-training Effect:** Leveraging data from related tasks/robots can provide a 34% absolute improvement in success rate, meaning you can get away with far fewer task-specific demonstrations ([Mobile ALOHA](https://arxiv.org/abs/2401.02117)).

**Emerging Direction:** Learning from human videos (not teleoperation) as a demonstration source, which would eliminate the need for robot-specific data collection entirely ([Learning Generalizable Robot Policy with Human Demonstration Video as a Prompt](https://arxiv.org/abs/2505.20795)).

---

## 5. Diffusion Policies & ACT

### Modern Imitation Learning That Reduces Teleop Burden

#### Diffusion Policy

Diffusion Policy represents robot behavior as a conditional denoising diffusion process. It generates multi-step action sequences rather than single actions, which is critical for handling multi-modal action distributions (when there are multiple valid ways to accomplish a task).

**Performance:** Consistently outperforms existing state-of-the-art robot learning methods with an average improvement of 46.9% across 15 tasks from 4 benchmarks ([Diffusion Policy: Visuomotor Policy Learning via Action Diffusion](https://journals.sagepub.com/doi/full/10.1177/02783649241273668)).

**Why it matters for reducing teleop burden:**
- Handles multimodal distributions (imperfect demonstrations are OK)
- Predicts action sequences (chunks), not single steps
- Robust to demonstration noise and variability
- Works with visual inputs directly (no hand-engineered features)

**Trajectory-Guided Extensions:** The Diffusion Trajectory-guided Policy (DTP) framework generates task-relevant trajectories to guide policy learning for long-horizon tasks, outperforming baselines by 25% average success rate ([DTP](https://arxiv.org/abs/2502.10040)).

#### ACT (Action Chunking with Transformers)

ACT predicts a sequence of actions ("an action chunk") instead of a single action, which reduces the effective decision horizon and mitigates compounding errors.

**Architecture:**
- Trained as the decoder of a Conditional VAE (CVAE)
- Combines images from multiple viewpoints + joint positions
- Transformer encoder synthesizes multi-modal inputs
- Transformer decoder predicts action sequences
- ~80M parameters, trains in hours on a single GPU

**Key Innovation:** Action chunking fundamentally changes the problem from predicting 1000s of individual timesteps to predicting ~100 chunks, dramatically reducing error accumulation ([ACT - Hugging Face](https://huggingface.co/docs/lerobot/en/act)).

**One-Shot ACT:** Research demonstrates that a single demonstration can be sufficient for simpler tasks when combined with action chunking ([One ACT Play: Single Demonstration Behavior Cloning](https://arxiv.org/abs/2309.10175)).

---

## 6. Keyframe vs. Continuous Teleoperation

### Two Fundamentally Different Data Collection Paradigms

**Continuous Teleoperation:**
- Real-time, stream-based command input
- Operator controls every moment of the trajectory
- Higher cognitive load, more fatiguing
- Captures nuanced dynamic behaviors (force modulation, speed variation)
- Standard approach in most teleoperation systems

**Keyframe Teleoperation:**
- Operator specifies key poses/waypoints only
- Robot interpolates between keyframes
- Dramatically reduces operator burden
- Extracts only the essential "what happened" from demonstrations
- Reduces noise and redundancy in training data

**Keyframe Advantages for Learning:**
- A hierarchical imitation learning method incorporating keyframes trains robots to generate appropriate trajectories
- Keyframes focus on task goals rather than execution details
- Each keyframe records: end-effector pose, object poses, and object attributes
- This is essentially "task-level" rather than "trajectory-level" specification
([Teleoperation-Driven and Keyframe-Based Generalizable Imitation Learning](https://ascelibrary.org/doi/10.1061/JCCEE5.CPENG-5884))

**Semantic Keyframes:** Beyond just poses, semantic keyframes capture the meaning of key moments - "grasp here," "place there" - using object attribute constraints to generalize across scenarios ([Semantic Learning from Keyframe Demonstration](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2024.1340334/full)).

**Practical Implication:** Keyframe approaches let operators demonstrate the task structure without needing continuous fine motor control, which is exactly the kind of reduction in burden we're looking for.

---

## 7. Levels of Abstraction in Teleoperation

### The Spectrum from Joint-Level to Task-Level Control

| Level | What Operator Controls | AI Handles | Cognitive Load |
|-------|----------------------|------------|----------------|
| **Joint-level** | Individual joint angles | Nothing | Extreme |
| **End-effector (Cartesian)** | 6-DoF pose of gripper | IK solving, collision avoidance | High |
| **End-effector + constraints** | Position/orientation | Kinematic constraints, stability | Medium-High |
| **Skill-level** | Parameterized skills ("grasp at X") | Trajectory, approach angle, force | Medium |
| **Task-level** | Sequence of goals ("pick up cup") | Everything except what to do | Low |
| **Intent-level** | High-level goal ("clean the table") | Task decomposition, execution | Minimal |

**Key Insight:** Most current teleoperation operates at end-effector level. Moving even one level up to skill-level control would dramatically reduce operator burden while maintaining human oversight.

**Skill-Based Teleoperation Subsystems:**
1. Skill definition - what primitives are available
2. Intent estimation - predicting what the human wants
3. Shared autonomy - blending human and robot control
4. Learning from demonstration - improving over time
([Skill-Based Teleoperation](https://www.emergentmind.com/topics/skill-based-teleoperation))

**End-User Programming:** A system allowing non-expert operators to create task-level programs using a visual interface, with the robot executing each step semi-autonomously ([A System for Human-Robot Teaming through End-User Programming and Shared Autonomy](https://arxiv.org/html/2401.12380v1)).

---

## 8. Google RT-2 & DeepMind's Approach

### Vision-Language-Action Models - Reducing Teleoperation Through Knowledge Transfer

#### RT-2: Vision-Language-Action Model

RT-2 represents robot actions as another language, trained jointly on Internet-scale vision-language datasets and robot demonstration data. This means the robot inherits knowledge from billions of web images/text without needing explicit robot demonstrations for every concept.

**Key Results:**
- Functioned as well as RT-1 on training tasks
- Nearly doubled performance on novel, unseen scenarios (62% vs. RT-1's 32%)
- Demonstrated emergent capabilities: interpreting novel commands, rudimentary reasoning
- Can understand commands like "pick up the object that doesn't belong" without ever training on such instructions
([RT-2 - Google DeepMind](https://deepmind.google/blog/rt-2-new-model-translates-vision-and-language-into-action/))

**How it reduces teleoperation need:** By transferring knowledge from web data, the robot requires fewer task-specific demonstrations. Semantic understanding generalizes without per-task teleoperation.

#### AutoRT: Scalable Data Collection

AutoRT combines VLMs and LLMs with robot control models, orchestrating up to 20 robots simultaneously:
- Conducted 77,000 robotic trials across 6,650 unique tasks
- Uses language models to propose tasks and VLMs to understand environments
- Automates the data collection pipeline
([Shaping the Future of Advanced Robotics - DeepMind](https://deepmind.google/blog/shaping-the-future-of-advanced-robotics/))

#### SARA-RT: Efficiency

Self-Adaptive Robust Attention for Robotics Transformers makes RT models 14% faster and 10.6% more accurate - critical for real-time deployment ([Google DeepMind - SARA-RT](https://www.analyticsvidhya.com/blog/2024/01/google-deepmind-latest-robotics-advancements-autort-sara-rt-rt-trajectory/)).

#### RT-Trajectory: Visual Guidance

By overlaying 2D trajectory sketches on training videos, RT-Trajectory achieves 63% success rate on 41 unseen tasks - double the performance of existing RT models. This suggests that visual trajectory hints could be a much simpler interface than full teleoperation ([Google DeepMind - RT-Trajectory](https://www.analyticsvidhya.com/blog/2024/01/google-deepmind-latest-robotics-advancements-autort-sara-rt-rt-trajectory/)).

---

## 9. NVIDIA Sim-to-Real

### Eliminating Real-World Teleoperation Through Simulation

NVIDIA's approach: train extensively in simulation, transfer to reality with minimal or zero real-world demonstrations.

#### AutoMate (2024)
First framework demonstrating zero-shot sim-to-real transfer for assembly skills across geometrically diverse parts. No real-world demonstrations needed - skills learned purely in simulation work directly on physical robots ([NVIDIA - AutoMate](https://developer.nvidia.com/blog/training-sim-to-real-transferable-robotic-assembly-skills-over-diverse-geometries/)).

#### R2D2: Sim-and-Real Co-Training (2025)
Aligns simulated and real-world data through a shared latent space using optimal transport methods. Manipulation policies trained on both types of data generalize to real-world scenarios with fewer demonstrations ([NVIDIA - R2D2](https://developer.nvidia.com/blog/r2d2-improving-robot-manipulation-with-simulation-and-language-models/)).

#### Cosmos Transfer: Synthetic Data at Scale
NVIDIA Cosmos world foundation models generate exponentially large amounts of synthetic motion data from a small number of human demonstrations. This multiplies the effective dataset size without additional teleoperation ([NVIDIA Newsroom - GR00T N1](https://nvidianews.nvidia.com/news/nvidia-isaac-gr00t-n1-open-humanoid-robot-foundation-model-simulation-frameworks)).

#### GR00T N1.6 (2026)
The sim-to-real pipeline leverages whole-body reinforcement learning in Isaac Lab and synthetic-data-driven navigation, enabling zero-shot transfer and strong cross-embodiment performance with minimal finetuning ([NVIDIA - GR00T N1.6](https://developer.nvidia.com/blog/building-generalist-humanoid-capabilities-with-nvidia-isaac-gr00t-n1-6-using-a-sim-to-real-workflow/)).

**Practical Impact:** If simulation fidelity is sufficient, the teleoperation data collection bottleneck can be largely bypassed. The operator's role shifts from "data collector via teleoperation" to "verifier/corrector of autonomous behavior."

---

## 10. Mobile ALOHA & State-of-the-Art Data Collection

### Why ALOHA is Considered State-of-the-Art

**What makes ALOHA special:**

1. **Low cost ($32k total system)** - democratizes research
2. **Whole-body teleoperation** - captures bimanual + mobile data simultaneously
3. **Physical coupling** - operator is tethered to robot, providing natural kinesthetic feedback
4. **High-quality demonstrations** - the puppeteering interface produces cleaner data than VR/joystick methods
5. **Co-training recipe** - leverages existing datasets for massive efficiency gains

**The ALOHA Approach:**
- Two leader arms (controlled by human) mechanically coupled to two follower arms (on the robot)
- Human physically moves the leader arms, robot mirrors in real-time
- Three cameras (two wrist, one overhead) capture visual observations
- Base movement recorded via backdrive of wheels
([Mobile ALOHA](https://mobile-aloha.github.io/))

**Co-Training Innovation:**
The breakthrough insight is that training on data from different but related tasks (even from different robots) provides a powerful prior. With co-training:
- 50 demonstrations achieve 80%+ success on complex tasks
- 34% absolute improvement compared to no co-training
- Positive transfer observed across almost all mobile manipulation tasks
([Mobile ALOHA Paper](https://arxiv.org/abs/2401.02117))

**ALOHA 2:** Hardware improvements with better cameras, more robust mechanical design, and improved ergonomics for longer data collection sessions ([ALOHA 2](https://aloha-2.github.io/)).

**Why it's state-of-the-art for DATA COLLECTION specifically:**
- Intuitive physical interface (no learning curve for operators)
- High-frequency, high-fidelity demonstrations
- Captures the "feel" of manipulation (contact forces, compliance)
- Compatible with modern imitation learning methods (ACT, Diffusion Policy)
- Scalable - you can collect 50 demos in under an hour for most tasks

---

## 11. Click-Based & Point-and-Click Interfaces

### Minimal-Effort Teleoperation

**Georgia Tech Point-and-Click Grasping:**
Researchers developed a spectrum of teleoperation interfaces for grasping:
- Full 6-DoF manual control (hardest)
- 3-DoF constrained positioning (medium)
- **Single-click mostly automated grasping** (easiest)

The goal: getting rid of manual positioning entirely, using an interactive interface that handles everything with just one or two clicks ([IEEE Spectrum - Point-and-Click Robot Grasping](https://spectrum.ieee.org/point-and-click-method-robot-grasping-control)).

**How it works:**
1. Operator sees the scene through cameras
2. Operator clicks on the object to grasp
3. Robot autonomously plans approach, determines grasp pose, executes
4. Operator only intervenes if something goes wrong

**Laser-Based Interaction:** An intuitive tele-collaboration interface using laser pointing for indicating targets and behavior trees for structuring autonomous execution ([Laser-Based Interaction and Behavior Trees](https://www.sciencedirect.com/science/article/pii/S092188902500140X)).

**High-Level Goal Commands:** Frameworks that send commands like "move to this pose," leaving execution particulars up to the robot. The operator specifies WHERE, the robot figures out HOW ([Remote Robotic Teleoperation - Chris Paxton](https://itcanthink.substack.com/p/remote-robotic-teleoperation)).

---

## 12. Language, Gesture, and Alternative Interfaces

### Beyond Direct Physical Teleoperation

#### Natural Language Control

Language-conditioned robot manipulation combines language, vision, and control for end-to-end policy learning. The extracted policies provide a simple and intuitive interface for unstructured commands ([Language-Conditioned Imitation Learning](https://arxiv.org/abs/2010.12083)).

**DISCO:** Uses diffusion policies with language guidance and constrained inpainting for manipulation tasks specified in natural language ([DISCO](https://arxiv.org/html/2406.09767)).

**GEM:** Leverages pre-trained vision-language models with equivariant language mapping, demonstrating high sample efficiency and generalization across diverse tasks ([Learning Efficient Language-Conditioned Manipulation](https://arxiv.org/html/2406.15677)).

#### Gesture and Hand Tracking Control

**Apple Vision Pro for Teleoperation:**
- Streams hand tracking data over a network
- Records head, wrist, and finger movements in real-time
- Enables intuitive robot control through natural gestures
- Used with Unitree humanoid robots for full-body teleoperation
([VisionProTeleop - MIT](https://github.com/Improbable-AI/VisionProTeleop))

**Bunny-VisionPro:** Real-time bimanual dexterous teleoperation system using Vision Pro hand tracking for imitation learning data collection ([Bunny-VisionPro](https://arxiv.org/html/2407.03162v1)).

**NVIDIA MimicGen + Vision Pro:** Generates synthetic motion data from recorded teleoperated data, translating Vision Pro movements into robot actions and multiplying dataset size ([NVIDIA + Apple Vision Pro](https://appleinsider.com/articles/24/08/05/nvidia-using-apple-vision-pro-to-control-humanoid-robots)).

#### Mixed Reality Interfaces

Advanced systems combine:
- Natural hand gestures for manipulation commands
- Eye tracking for object selection
- Speech recognition for task-level commands
- AR overlays showing planned robot trajectories
([Immersive Robot Teleoperation Based on User Gestures in Mixed Reality](https://www.mdpi.com/1424-8220/24/15/5073))

---

## 13. The Copilot Paradigm

### Human + AI Working Together in Real-Time

The most promising emerging framework: the human as "pilot" with an AI "copilot" that provides corrections.

#### HACTS (Human-As-Copilot Teleoperation System)

Establishes bilateral, real-time joint synchronization between a robot arm and teleoperation hardware. Human copilots intervene seamlessly while collecting action-correction data for future learning. The key: the system improves over time from every human correction ([HACTS](https://arxiv.org/html/2503.24070v1)).

#### HIL-SERL (Human-in-the-Loop Sample-Efficient RL)

A vision-based RL system achieving:
- 100% success rate within 1-2.5 hours of real-world training
- Dynamic manipulation, precision assembly, and dual-arm coordination
- Human interventions provide demonstrations AND prevent undesirable behavior
- Binary reward classifier trained from positive/negative teleoperation samples
([HIL-SERL](https://hil-serl.github.io/))

**Training process:**
1. Brief teleoperation to collect positive and negative samples
2. Train binary reward classifier
3. Deploy with human oversight - human intervenes on failures
4. Robot learns from both successes and interventions
5. Intervention frequency decreases as robot improves

#### RoboCopilot: Interactive Imitation Learning

Alternates between model training and data collection with a learned policy:
1. Pre-train initial policy from human demonstrations
2. Deploy policy on robot
3. Human monitors and intervenes only on failures
4. Policy fine-tuned from all collected data (successes + corrections)
5. As performance improves, less human intervention needed

**Results:** Significantly outperformed traditional behavior cloning and batched DAgger approaches. Interactive data collection produces better quality data than passive demonstrations alone ([RoboCopilot](https://arxiv.org/html/2503.07771v1)).

#### TRANSIC: Online Correction for Sim-to-Real

When sim-trained policies make mistakes in the real world, humans interrupt and assist via teleoperation. The corrections are used to fine-tune the policy, closing sim-to-real gaps iteratively ([TRANSIC](https://transic-robot.github.io/)).

---

## 14. Foundation Models for Robot Control

### The Emerging Path to Zero-Shot Robot Manipulation

#### Physical Intelligence - pi0

The most capable generalist robot policy to date:
- Trained on data from 7 robotic platforms and 68 unique tasks
- Uses flow matching (a variant of diffusion) for high-frequency action output (50 Hz)
- Inherits semantic knowledge from Internet-scale VLM pretraining
- Demonstrates zero-shot performance on novel tasks
- Open-sourced for the community
([pi0 - Physical Intelligence](https://www.pi.website/blog/pi0))

**Why it matters:** pi0 shows that a single foundation model can control many different robots on many different tasks. This means the teleoperation burden is amortized across the entire community - your demonstrations contribute to a shared model.

#### LeRobot (Hugging Face)

The open-source ecosystem making all of this accessible:
- Implements ACT, Diffusion Policy, VQ-BeT, HIL-SERL, pi0, GR00T, SmolVLA
- Standardized dataset format for sharing demonstrations
- Supports Open X-Embodiment and DROID datasets
- v0.4.0 includes PI0.5 and GR00T N1.5 models
([LeRobot - Hugging Face](https://github.com/huggingface/lerobot))

**Practical Recommendation:** For anyone starting with robot learning today, LeRobot + ACT policy is the recommended starting point: fast training, low compute requirements, strong performance ([LeRobot v0.4.0](https://huggingface.co/blog/lerobot-release-v040)).

#### Open X-Embodiment

A massive shared dataset of robot demonstrations across many different robots and tasks, enabling cross-embodiment transfer learning. The key insight: demonstrations from ANY robot help ALL robots learn.

---

## 15. Key Takeaways & Implications

### The Landscape of Approaches to Reduce Operator Burden

**Immediate (can implement now):**
1. **Move from joint-level to end-effector control** - most basic improvement
2. **Add keyframe capture** - operator demonstrates key poses, robot interpolates
3. **Use ACT/Diffusion Policy** - only need ~50 demonstrations per task
4. **Co-train with existing datasets** - leverage LeRobot/Open X-Embodiment data

**Near-term (6-12 months of engineering):**
5. **Implement skill primitives** - operator selects "grasp object" rather than controlling gripper
6. **Add shared autonomy corrections** - AI smooths/corrects operator inputs in real-time
7. **Point-and-click grasping** - operator clicks target, robot figures out execution
8. **Language-conditioned control** - "pick up the red cup" as interface

**Medium-term (requires more research):**
9. **Full copilot paradigm** - human monitors, AI executes, human corrects failures only
10. **Foundation model deployment** - pi0/GR00T for zero-shot task generalization
11. **Real-to-sim-to-real** - minimal real data, train corrections in simulation
12. **Learning from human video** - no robot teleoperation needed at all

### Critical Numbers to Remember

| Metric | Value | Source |
|--------|-------|--------|
| Demos needed (ACT) | ~50 | ALOHA |
| Demos needed (with co-training) | ~50 (but much better performance) | Mobile ALOHA |
| Demos needed (single-shot methods) | 1 video | RoboCLIP |
| Time to train HIL-SERL policy | 1-2.5 hours real-world | Berkeley |
| ALOHA collection time per task | ~10 minutes for 50 demos | Stanford |
| Diffusion Policy improvement over baselines | 46.9% average | Columbia |
| RT-2 novel task generalization | 62% (vs 32% for RT-1) | DeepMind |
| AutoRT scale | 77,000 trials, 6,650 tasks | DeepMind |

### The Progression Path for a Robotics Product

**Phase 1 - Data Collection:**
Use ALOHA-style puppeteering to collect 50 demos per task. Train ACT policies via LeRobot. This gets you to 80%+ success with minimal infrastructure.

**Phase 2 - Shared Autonomy:**
Deploy learned policies with human oversight. Human monitors and intervenes on failures (copilot paradigm). Each intervention improves the policy. Failure rate drops over time.

**Phase 3 - Corrections-Based Learning:**
Implement residual copilot (AI handles most execution, human provides corrections). Corrections automatically improve the model. Operator burden drops dramatically.

**Phase 4 - Foundation Model Integration:**
Fine-tune pi0 or GR00T on your specific tasks. Leverage zero-shot generalization for new tasks. Teleoperation becomes the exception rather than the rule.

### The Core Insight Confirmed

The research overwhelmingly supports the thesis: **the future is NOT making pure teleoperation easier, but building systems where AI handles execution and humans provide oversight, corrections, and high-level guidance.** The most successful systems (HIL-SERL, HACTS, RoboCopilot, Mobile ALOHA + co-training) all follow this pattern:

1. Start with a small amount of human demonstration
2. Deploy a policy that's "good enough"
3. Human corrects failures (not controls every motion)
4. System improves from corrections
5. Human intervention decreases over time
6. Eventually the human role is supervisory, not operational

This is the path from teleoperation to autonomy, and the transition happens gradually through shared autonomy rather than as a binary switch.

---

## Key References

- [Mobile ALOHA - Stanford](https://mobile-aloha.github.io/)
- [ACT Policy - Hugging Face LeRobot](https://huggingface.co/docs/lerobot/en/act)
- [Diffusion Policy](https://journals.sagepub.com/doi/full/10.1177/02783649241273668)
- [HIL-SERL - Berkeley](https://hil-serl.github.io/)
- [pi0 - Physical Intelligence](https://www.pi.website/blog/pi0)
- [RT-2 - Google DeepMind](https://deepmind.google/blog/rt-2-new-model-translates-vision-and-language-into-action/)
- [NVIDIA GR00T N1](https://nvidianews.nvidia.com/news/nvidia-isaac-gr00t-n1-open-humanoid-robot-foundation-model-simulation-frameworks)
- [LeRobot - Hugging Face](https://github.com/huggingface/lerobot)
- [RoboCopilot](https://arxiv.org/html/2503.07771v1)
- [HACTS](https://arxiv.org/html/2503.24070v1)
- [Real-to-Sim-to-Real Shared Autonomy](https://arxiv.org/abs/2603.17016)
- [TRANSIC](https://transic-robot.github.io/)
- [Movement Primitives Survey](https://arxiv.org/html/2601.02379v1)
- [Skill-Based Teleoperation](https://www.emergentmind.com/topics/skill-based-teleoperation)
- [VisionProTeleop](https://github.com/Improbable-AI/VisionProTeleop)
