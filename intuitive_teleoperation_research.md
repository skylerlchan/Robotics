# Making Robot Teleoperation Intuitive: A Research Survey

*April 20, 2026*

## Executive Summary

Teleoperation for dexterous manipulation remains one of the hardest unsolved problems in robotics. Despite decades of research, operators struggle with latency, kinematic mismatch, absence of haptic feedback, and poor depth perception. This document surveys the academic literature on why teleoperation is so difficult and what solutions have been proposed to make it feel natural -- like an extension of the operator's own body.

The research converges on several key insights:
1. **Embodiment is the gold standard** -- when operators feel the robot as part of themselves (not as an external tool), cognitive load drops and performance rises dramatically
2. **No single modality wins** -- the optimal interface depends on the task, but leader-follower systems consistently produce the highest quality demonstration data
3. **Shared autonomy is the most promising frontier** -- AI co-pilots that handle fine-grained control while humans provide high-level intent dramatically reduce operator burden
4. **Cloth and deformable objects represent the hardest class** -- they break every assumption in rigid-body robotics and push teleoperation systems to their limits

---

## 1. Why Teleoperation Is So Hard

### 1.1 Latency and Communication Delays

Latency is arguably the single most damaging factor in teleoperation. The problem compounds because the loop includes: operator sends command --> network transmission --> robot executes --> camera captures result --> video transmitted back --> rendered on display. Each step adds delay.

Key findings:
- Delays above 200ms force operators into a disjointed "move-and-wait" strategy that destroys task flow ([Frontiers in Robotics and AI](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2020.578805/full))
- Even delays of a few milliseconds in haptic feedback can destabilize the system, causing oscillation and over-correction ([ACM Transactions on Human-Robot Interaction](https://dl.acm.org/doi/10.1145/3651993))
- Brain functional connectivity measurably changes under teleoperation latency, with operators recruiting additional cognitive resources to compensate ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11599268/))
- Sensory manipulation (artificially slowing visual feedback to mask delays) has been proposed as a countermeasure ([Nature Scientific Reports](https://www.nature.com/articles/s41598-024-54734-1))
- A NASA study found operator performance degrades after approximately 3 hours of continuous teleoperation, with fatigue and latency compounding ([NASA Technical Reports](https://ntrs.nasa.gov/citations/20205008229))

### 1.2 Kinematic Mismatch

Humans and robots have fundamentally different bodies. This creates a mapping problem that is never fully solvable.

- Different joint configurations, workspace limits, and degrees of freedom mean human motions cannot map 1:1 to robot motions ([Nature Scientific Reports on exoskeletons](https://www.nature.com/articles/s41598-026-37205-7))
- For dexterous hands specifically, retargeting errors arise from structural differences in finger length, joint limits, and actuation topology -- these become more pronounced under fast motions ([AnyTeleop, arXiv:2307.04577](https://arxiv.org/html/2307.04577v3))
- The mismatch creates "intersensory conflict" -- the operator sees and intends one thing but the robot does something slightly different, causing nausea, frustration, and instability ([MIT Press PRESENCE](https://direct.mit.edu/pvar/article/27/2/226/96073/Effects-of-Throughput-Delay-on-Perception-of-Robot))

### 1.3 Lack of Haptic Feedback

Without force feedback, operators are essentially "numb" -- they cannot feel contact, texture, stiffness, or slip.

- In unilateral (no-feedback) teleoperation, operators apply excessive force, break objects, and cannot perform fine manipulation ([Springer Nature](https://link.springer.com/article/10.1007/s00542-022-05382-w))
- Adding force reflection significantly reduces position error, applied force, and task completion time in peg-in-hole assembly tasks ([NSF/PAR](https://par.nsf.gov/servlets/purl/10359277))
- Haptic feedback in surgical telerobots has been shown to reduce cognitive load, boost self-confidence, and minimize frustration, but delay in the feedback loop can cause instability ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12024826/))
- Operators can discriminate object stiffness through haptic teleoperation alone (without vision), but this requires well-calibrated bilateral systems ([arXiv:2412.02613](https://arxiv.org/html/2412.02613))

### 1.4 Depth Perception and Visual Limitations

- Single-camera setups drastically reduce spatial awareness, making contact-based tasks nearly impossible ([Frontiers in Robotics and AI](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2016.00047/full))
- Monocular vision with limited field-of-view forces operators to build mental models of 3D space from 2D images -- a massive cognitive burden
- Stereoscopic vision (as in VR headsets) significantly improves depth estimation and task performance, but introduces latency in the rendering pipeline
- Head-coupled stereoscopic displays (where the view tracks operator head movement) provide the strongest depth cues and spatial awareness ([Open-TeleVision](https://robot-tv.github.io/))

### 1.5 High Dimensionality

Dexterous manipulation requires controlling many degrees of freedom simultaneously:
- A bimanual system with two 7-DOF arms + two 16-DOF hands = 46 DOF to control simultaneously
- Human attention cannot effectively manage more than a few DOF consciously -- the rest must become "automatic" through practice or be offloaded to autonomy
- This creates an inherent tension: the more dexterous the robot, the harder it is to teleoperate

---

## 2. The Embodiment Framework: Making Robots Feel Like Extensions of Self

### 2.1 What Is Embodiment in Teleoperation?

The research identifies embodiment as the critical psychological construct that makes teleoperation feel natural. When embodiment is strong, the operator perceives the robot as an extension of their own body and sensorimotor system, which minimizes cognitive load and enhances fluidity of task execution ([Frontiers in Robotics and AI](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2020.00014/full)).

Embodiment comprises three components:
1. **Body ownership** -- feeling the robot as part of oneself
2. **Self-location** -- strong spatial telepresence at the remote site
3. **Agency** -- confidence that one's intentions directly produce corresponding robot actions

A transparent telerobotic system appears imperceptible and almost non-existent to the operator -- performance is not influenced by the mediation ([MDPI Applied Sciences](https://www.mdpi.com/2076-3417/10/18/6232)).

### 2.2 Factors That Enhance Embodiment

Research identifies several design principles:
- **Visuomotor congruence**: the robot must move exactly when and how the operator moves, with minimal delay
- **Anthropomorphic mapping**: the closer the robot's form matches the human body, the stronger the ownership illusion
- **Active perception**: operators who control the viewpoint (head-coupled cameras) report stronger embodiment than those with fixed views
- **Multisensory integration**: combining visual, haptic, and proprioceptive feedback creates stronger illusion than any single channel

### 2.3 The Role of Embodiment in Data Collection Quality

A 2025 study directly examined this question for mobile manipulation, finding that a strong sense of embodiment combined with minimal physical and cognitive demands enhances user experience during large-scale data collection and helps maintain data quality over extended periods. However, VR as a feedback modality actually *increases* task completion time, cognitive workload, and perceived effort -- suggesting embodiment through physical interfaces may be superior to virtual ones ([arXiv:2509.03222](https://arxiv.org/abs/2509.03222)).

---

## 3. Teleoperation Modalities Compared

### 3.1 Leader-Follower (Puppet-Style)

**How it works**: A kinematically identical (or similar) replica of the robot serves as the input device. The operator directly manipulates the leader, and the follower robot mirrors the motion.

**Key systems**:
- **ALOHA** (Stanford, 2023): Two consumer-grade robot arms in leader-follower configuration. Enabled 80-90% success on fine-grained bimanual tasks with only 10 minutes of demonstrations. Total system cost ~$20K. Paired with ACT (Action Chunking with Transformers) for policy learning ([Zhao et al., RSS 2023](https://tonyzhaozh.github.io/aloha/))
- **Mobile ALOHA** (2024): Extended ALOHA with a mobile base for whole-body teleoperation at $32K total cost ([arXiv:2401.02117](https://arxiv.org/abs/2401.02117))
- **GELLO** (2023): A $300 3D-printed leader device with the same kinematic structure as the target arm. User study with 12 participants across 5 tasks showed GELLO enables more reliable and efficient demonstration collection compared to VR controllers and 3D spacemouses ([arXiv:2309.13037](https://arxiv.org/html/2309.13037v2))

**Advantages**: Most intuitive mapping (1:1 joint correspondence), minimal cognitive load, highest demonstration quality, immediate proprioceptive feedback from the physical leader device.

**Disadvantages**: Requires building/buying a physical replica for each robot; limited workspace; cannot scale to very different morphologies.

### 3.2 VR / Head-Mounted Display

**How it works**: Operator wears VR headset for stereoscopic vision and uses hand/controller tracking for arm/hand control.

**Key systems**:
- **Open-TeleVision** (UCSD/MIT, 2024): Streams stereoscopic video from robot head camera to VR headset, with head-coupled active camera. Operates at 60Hz. Demonstrated cross-country teleoperation (MIT operator controlling robot at UCSD) ([Robot-TV](https://robot-tv.github.io/))
- **Bunny-VisionPro** (2024): Uses Apple Vision Pro's hand tracking for bimanual dexterous teleoperation. Matches or surpasses baselines in 9/10 tasks. Achieves 11% higher success rate with 45% less task completion time than AnyTeleop+ ([arXiv:2407.03162](https://arxiv.org/html/2407.03162v1))
- **LeVR** (2025): Modular VR teleoperation framework with seamless integration into LeRobot policy training ecosystem ([arXiv:2509.14349](https://arxiv.org/html/2509.14349v1))

**Advantages**: Immersive stereoscopic vision, intuitive hand tracking, active head-coupled perception, no physical replica needed, scalable across different robots.

**Disadvantages**: VR can increase cognitive load and fatigue; latency in rendering; no physical haptic feedback from the environment; can cause nausea with prolonged use.

### 3.3 Exoskeletons and Wearable Systems

**How it works**: Operator wears a mechanical structure that tracks arm/hand pose and optionally provides force feedback.

**Key systems**:
- **NuExo** (2025): Lightweight backpack-style exoskeleton covering full upper-limb ROM. Enables using the human arm directly as the controller for humanoid robots ([arXiv:2503.10554](https://arxiv.org/html/2503.10554v1))
- **DexCap** (RSS 2024): Wearable hand mocap system (not a full exoskeleton). Approximately 3x faster than teleoperation in data collection throughput. Policy learned from 30-minute human mocap data without any teleoperation needed ([arXiv:2403.07788](https://arxiv.org/html/2403.07788v1))
- **DexUMI** (2025): Uses the human hand itself as the universal manipulation interface via a wearable exoskeleton optimized per target robot hand ([arXiv:2505.21864](https://arxiv.org/html/2505.21864v3))

**Advantages**: Natural proprioceptive feedback, full arm workspace, can provide bilateral force reflection, closest to natural human motion.

**Disadvantages**: Expensive, bulky, requires calibration, limited portability, fatigue from wearing hardware.

### 3.4 Vision-Based (Camera-Only, No Wearables)

**How it works**: Cameras observe operator hand pose and retarget it to the robot.

**Key systems**:
- **AnyTeleop** (2023): General vision-based system using RGB cameras to estimate hand pose and retarget to any robot arm-hand system ([arXiv:2307.04577](https://arxiv.org/html/2307.04577v3))
- Vision-based systems with intuitive hand recognition interfaces for multi-robot teleoperation ([Nature Scientific Reports](https://www.nature.com/articles/s41598-024-80898-x))

**Advantages**: Zero wearable cost, most natural (bare hands), scalable.

**Disadvantages**: Occlusion problems, depth ambiguity, no haptic feedback, lower tracking accuracy, relies on kinematic retargeting without force/contact awareness.

### 3.5 Comparative Findings

The 2025 ICRA paper "How to Train Your Robots?" provides the most direct comparison ([arXiv:2503.07017](https://arxiv.org/abs/2503.07017)):
- **Kinesthetic teaching** is rated most intuitive and produces cleanest data for best downstream learning, but causes physical fatigue
- **VR teleoperation** offers high state diversity but lower action consistency
- **Spacemouse teleoperation** is least intuitive
- **Hybrid approach** (small amount of kinesthetic + larger VR data) achieves 20% higher performance than any single modality alone

The **TeleOpBench** benchmark (2025) provides unified evaluation across MoCap, VR, exoskeletons, and vision tracking across 30 tasks. MoCap pipelines (Xsens + Metagloves) delivered highest precision in shortest time ([arXiv:2505.12748](https://arxiv.org/html/2505.12748v1)).

---

## 4. Shared Autonomy: AI Co-Pilots for Teleoperation

Shared autonomy is emerging as the most promising solution to make teleoperation tractable. The core idea: let the human provide high-level intent while AI handles low-level execution details.

### 4.1 Key Systems

**Real-to-Sim-to-Real Shared Autonomy** (March 2026): Augments human teleoperation with a learned "copilot" trained from less than 5 minutes of real-world data. Uses a k-nearest-neighbor human surrogate to enable stable training of a residual correction policy ([arXiv:2603.17016](https://arxiv.org/abs/2603.17016)).

**End-to-End Dexterous Arm-Hand VLA via Shared Autonomy** (2025): Human provides arm guidance via VR while an autonomous VLA (Vision-Language-Action) policy handles fine-grained grasping. Reduces operator cognitive load by offloading the hardest part -- dexterous finger control ([arXiv:2511.00139](https://arxiv.org/html/2511.00139)).

**SPIRIT** (2026): Perceptive shared autonomy that dynamically transitions between semi-autonomous manipulation (when AI is confident) and haptic teleoperation (when uncertainty is high). Models uncertainty of deep learning perception to decide when humans should take over ([arXiv:2603.05111](https://arxiv.org/html/2603.05111)).

**TASC: Task-Aware Shared Control** (2025): Allows users to complete everyday tasks with reduced input burden while generalizing across multiple tasks and object configurations without task-specific training ([arXiv:2509.10416](https://arxiv.org/html/2509.10416v1)).

**Zero-Shot Intent Recognition** (2025): Vision-only framework that estimates human intent in real-time using end-effector cameras, enabling blended human-robot control without requiring prior training on specific objects ([arXiv:2501.08389](https://arxiv.org/html/2501.08389)).

**Sampling-Based Grasp and Collision Prediction** (2025): Assists teleoperators by predicting likely grasps and upcoming collisions, allowing preemptive correction ([arXiv:2504.18186](https://arxiv.org/abs/2504.18186)).

### 4.2 Human-Agent Joint Learning

A paradigm where the human and AI learn together during teleoperation. As the AI improves, the human can provide less precise input, reducing fatigue and cognitive load over time. The assistive agent gradually takes over routine parts of the task while the human focuses on novel situations ([arXiv:2407.00299](https://arxiv.org/html/2407.00299v2)).

### 4.3 TypeTele: Manipulation Type-Guided Teleoperation

Rather than forcing human hand motions onto the robot, TypeTele introduces a library of 30 "dexterous manipulation types" (grasps, non-grasps, bimanual symmetric/asymmetric). A multimodal large language model selects the appropriate type based on the task, enabling complex actions previously unachievable through direct retargeting (e.g., using scissors, spraying water, operating a kettle) ([arXiv:2507.01857](https://arxiv.org/abs/2507.01857)).

---

## 5. Solutions for Reducing Cognitive Load

### 5.1 Multi-Modal Feedback Design

Research shows that single-channel (vision-only) feedback overloads the visual system. Multi-modal interfaces distribute information across channels:
- Visual: stereoscopic 3D, AR overlays, predictive displays
- Haptic: force reflection, vibrotactile cues, stiffness rendering
- Auditory: contact sounds, proximity warnings, status cues

A study on multi-modal cognitive interfaces for manufacturing found that structured feedback channel design significantly reduces cognitive load compared to vision-only displays ([Springer, Journal of Intelligent Manufacturing](https://link.springer.com/article/10.1007/s10845-024-02451-x)).

### 5.2 Augmented Reality Overlays

AR enhances teleoperation by overlaying actionable information directly in the operator's field of view:
- Object highlighting and trajectory visualization
- Force magnitude displays
- Collision proximity warnings
- Grasp quality indicators

Studies demonstrate that dynamic AR overlays lead to fewer control mode switches, reduced errors and collisions, heightened confidence, and improved situational awareness ([ACM THRI 2024](https://dl.acm.org/doi/10.1145/3648536.3648544); [Cyborg and Bionic Systems](https://spj.science.org/doi/10.34133/cbsystems.0098)).

### 5.3 Predictive Displays

Predictive displays compensate for latency by showing the operator a model-based prediction of what the robot will do *now*, rather than waiting for delayed camera images:
- Significantly improve performance under delays >200ms
- Reduce subjective workload as measured by NASA-TLX
- Can use generative AI (GANs, diffusion models) for pixel-level prediction
- Intention-reflected predictive displays combine XR prediction with time-delay-aware shared control ([Springer ROBOMECH Journal](https://link.springer.com/article/10.1186/s40648-023-00258-8); [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1071581920301385))

### 5.4 Eye-Tracking Based Control

Eye-movement-based control can predict operator intent and reduce workload:
- Predicted trajectory guidance based on gaze significantly reduces workload across multiple NASA-TLX dimensions
- Particularly effective under high-delay conditions where manual control becomes impractical ([MDPI Machines](https://www.mdpi.com/2075-1702/13/8/735))

---

## 6. Cloth Manipulation: The Hardest Teleoperation Problem

### 6.1 Why Cloth Is Exceptionally Difficult

Cloth manipulation breaks fundamental assumptions in robotics ([arXiv:2407.01361](https://arxiv.org/html/2407.01361v1)):
- **Infinite-dimensional state space**: a cloth has effectively infinite configurations
- **No rigid-body dynamics**: standard physics engines struggle with accurate cloth simulation
- **Self-occlusion**: the cloth hides its own state from cameras
- **Complex contact**: cloth-cloth and cloth-object contacts are discontinuous and hard to model
- **Requires bimanual coordination**: most cloth tasks need two hands working in concert
- **Tactile is critical**: operators need to feel tension, slip, and thickness

### 6.2 Current Approaches to Cloth Teleoperation

**Click-based interfaces**: Users select pick-and-place points on cloth images, then preview simulated outcomes before execution. Reduces real-time control demands but loses dexterity ([arXiv:2104.02968](https://arxiv.org/pdf/2104.02968)).

**Reinforcement learning in simulation**: Neural networks trained to flatten/fold towels using tactile sensor data integrated into the textile itself, then transferred to real hardware ([ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0921889023001458)).

**Tactile sensing + edge tracing**: Vision-based tactile systems (like GelSight) enable cloth edge tracing and corner detection for unfolding -- emulating human dexterous strategies ([arXiv:2603.10609](https://arxiv.org/html/2603.10609)).

**GarmentLab** (NeurIPS 2024): Unified simulation benchmark for garment manipulation integrating modern physics engines with teleoperation pipelines for data collection ([NeurIPS 2024 Proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/file/15f80ec0fed53885d2ca6272edb96ede-Paper-Conference.pdf)).

### 6.3 The Data Bottleneck

Data remains the core bottleneck for cloth manipulation, calling for more realistic simulators and real-world pipelines that use modern teleoperation, motion capture, or multimodal sensing ([Frontiers in Robotics and AI, 2026](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2026.1752914/full)). Teleoperation of cloth is uniquely taxing on operators because:
- Constant contact management requires sustained attention
- Bimanual coordination demands are high
- Visual feedback alone is insufficient (operators cannot see tension in the cloth)
- Tasks are long-horizon (many sequential steps to fold a garment)

---

## 7. Operator Training and Learning Curves

### 7.1 The Skill Acquisition Problem

Teleoperation is a learned skill with significant learning curves:
- Human demonstrations are not always consistent -- fatigue, focus, and skill changes affect performance over time ([Labellerr](https://www.labellerr.com/blog/teleoperation-datasets-for-robot-learning/))
- High dimensionality of dexterous manipulation creates an inherent learning barrier
- Each teleoperation modality has its own learning curve -- VR controllers, spacemouses, leader-followers all require practice

### 7.2 Interface Intuitiveness Hierarchy

Based on the literature, interfaces rank approximately as follows (most to least intuitive):
1. Kinesthetic teaching (most natural -- direct physical guidance)
2. Leader-follower with matched kinematics (ALOHA, GELLO)
3. VR with hand tracking (Bunny-VisionPro, Open-TeleVision)
4. Exoskeleton with force feedback
5. VR controllers (Meta Quest controllers)
6. 3D spacemouse
7. Keyboard/gamepad (least intuitive)

### 7.3 Reducing Training Requirements

**Action Chunking with Transformers (ACT)** addresses the operator quality problem from the learning side: by predicting actions in chunks (sequences of k future timesteps), the policy is more forgiving of imperfect demonstrations. A task of 500 timesteps (10 seconds at 50Hz) with k=100 chunking reduces the effective decision horizon to just 5 steps. This means operators do not need to be perfectly consistent -- the policy smooths over small errors ([arXiv:2304.13705](https://arxiv.org/abs/2304.13705)).

**Human-Agent Joint Learning** reduces operator burden over time: as the AI assistive agent learns from accumulated data, less human effort and attention are required, creating a positive feedback loop where operation gets easier with practice ([arXiv:2407.00299](https://arxiv.org/abs/2407.00299)).

**DexCap's approach** sidesteps teleoperation entirely for data collection: operators simply perform tasks with their own hands wearing motion capture gloves, which is approximately 3x faster than teleoperation and close to natural human motion speed. The data is then retargeted to the robot embodiment offline ([arXiv:2403.07788](https://arxiv.org/html/2403.07788v1)).

---

## 8. Emerging Design Principles

Based on this survey, the following design principles emerge for building intuitive teleoperation systems:

### 8.1 Match the Control Interface to the Task
- Use leader-follower for precision tasks where data quality matters most
- Use VR for tasks requiring diverse viewpoints and spatial awareness
- Use shared autonomy for high-DOF dexterous tasks where operators cannot manage all joints

### 8.2 Provide Multi-Modal Feedback
- Never rely on vision alone
- Add haptic cues even if imperfect (vibrotactile is better than nothing)
- Use spatial audio for situational awareness
- Layer AR overlays for guidance without occluding the workspace

### 8.3 Embrace Shared Autonomy
- Let humans do what humans do best (high-level planning, novel situations)
- Let AI do what AI does best (precise joint control, force regulation, repetitive fine motor)
- Dynamic handoff based on confidence/uncertainty is the most promising paradigm

### 8.4 Design for the Data Collection Use Case
- If the goal is imitation learning, prioritize *demonstration quality* over operator comfort
- Hybrid data strategies (mixing modalities) outperform single-modality collection
- Account for operator fatigue in long collection sessions -- embodiment and low cognitive load help maintain quality

### 8.5 Minimize the "Mediation Gap"
- Reduce latency to below 50ms wherever possible
- Use predictive displays when latency is unavoidable
- Match kinematics as closely as feasible (GELLO principle)
- Provide active, head-coupled vision (not fixed cameras)
- Make the interface disappear psychologically -- the operator should forget they are controlling a robot

---

## 9. Key Papers Reference List

| Paper | Authors/Venue | Key Contribution |
|-------|---------------|------------------|
| [ALOHA: Learning Fine-Grained Bimanual Manipulation](https://tonyzhaozh.github.io/aloha/) | Zhao et al., RSS 2023 | Low-cost leader-follower + ACT policy, 80-90% success with 10min demos |
| [Mobile ALOHA](https://arxiv.org/abs/2401.02117) | Fu, Zhao et al., 2024 | Whole-body mobile manipulation teleoperation |
| [GELLO](https://arxiv.org/html/2309.13037v2) | Wu et al., 2023 | $300 matched-kinematics leader, outperforms VR/spacemouse |
| [Open-TeleVision](https://robot-tv.github.io/) | Yang et al., 2024 | Immersive stereoscopic VR teleoperation at 60Hz |
| [Bunny-VisionPro](https://arxiv.org/html/2407.03162v1) | Ding et al., 2024 | Vision Pro hand tracking for bimanual dexterous teleop |
| [DexCap](https://arxiv.org/html/2403.07788v1) | Wang et al., RSS 2024 | 3x faster than teleop, mocap-based data collection |
| [How to Train Your Robots?](https://arxiv.org/abs/2503.07017) | ICRA 2025 | Modality comparison: kinesthetic best quality, hybrid 20% better |
| [TeleOpBench](https://arxiv.org/html/2505.12748v1) | 2025 | Unified benchmark: MoCap > VR > Vision for precision |
| [TypeTele](https://arxiv.org/abs/2507.01857) | Lin et al., 2025 | MLLM-guided manipulation types, enables previously impossible tasks |
| [Toward Enhanced Teleoperation Through Embodiment](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2020.00014/full) | Frontiers 2020 | Framework: ownership + self-location + agency = embodiment |
| [Real-to-Sim-to-Real Shared Autonomy](https://arxiv.org/abs/2603.17016) | 2026 | Copilot trained from 5min data, corrects human errors |
| [SPIRIT](https://arxiv.org/html/2603.05111) | 2026 | Uncertainty-aware autonomy handoff |
| [TASC](https://arxiv.org/html/2509.10416v1) | 2025 | Task-aware shared control, generalizes without task-specific training |
| [Human-Agent Joint Learning](https://arxiv.org/abs/2407.00299) | 2024 | Co-learning reduces operator effort over time |
| [UniBiDex](https://arxiv.org/html/2601.04629v1) | 2026 | Unified framework supporting VR + leader-follower modalities |
| [NuExo](https://arxiv.org/html/2503.10554v1) | 2025 | Full upper-limb exoskeleton for humanoid teleoperation |
| [Robotic Cloth Manipulation Review](https://arxiv.org/html/2407.01361v1) | 2024 | Comprehensive review of cloth manipulation challenges |
| [Role of Embodiment in Whole-Body Teleoperation](https://arxiv.org/abs/2509.03222) | Humanoids 2025 | VR increases workload; coupled embodiment improves learning |
| [Predictive Display for Teleoperation](https://www.sciencedirect.com/science/article/pii/S1071581920301385) | ScienceDirect | Low-cost predictive display reduces workload under delay |
| [ACT: Action Chunking with Transformers](https://arxiv.org/abs/2304.13705) | Zhao et al., RSS 2023 | Chunked action prediction forgives imperfect demos |

---

## 10. Implications for Building a Teleoperation System for Cloth Folding

Based on this research, a teleoperation system optimized for cloth folding demonstrations should:

1. **Use a leader-follower interface** (ALOHA-style) for maximum data quality and operator intuitiveness -- the matched kinematics eliminate the biggest source of cognitive load
2. **Add tactile sensing on the robot fingers** -- operators need to feel cloth tension and slip, even if only through vibrotactile proxy feedback
3. **Implement shared autonomy for grasp stabilization** -- AI handles maintaining grasp force while human provides trajectory; this offloads the hardest continuous-attention subtask
4. **Provide stereoscopic overhead + wrist cameras** -- depth perception is critical for understanding cloth configuration
5. **Keep latency below 20ms** -- cloth tasks require continuous, flowing motions that break down under delay
6. **Use action chunking (ACT or Diffusion Policy)** for learning -- these approaches are specifically designed to handle the multimodal action distributions and temporal consistency requirements of dexterous tasks
7. **Plan for operator fatigue** -- cloth folding demos are long and attention-demanding; limit collection sessions and track data quality metrics
8. **Consider DexCap-style bare-hand collection** as an alternative pipeline -- if teleoperation proves too burdensome, capturing natural human cloth folding and retargeting offline may be more practical

---

## Sources

- [Frontiers: Survey of Telerobotic Time Delay Mitigation](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2020.578805/full)
- [Nature Scientific Reports: Sensory Manipulation as Latency Countermeasure](https://www.nature.com/articles/s41598-024-54734-1)
- [MIT Press PRESENCE: Effects of Delay on Perception](https://direct.mit.edu/pvar/article/27/2/226/96073/Effects-of-Throughput-Delay-on-Perception-of-Robot)
- [ACM: Impact of Haptic Feedback in High Latency Teleoperation](https://dl.acm.org/doi/10.1145/3651993)
- [PMC: Brain Functional Connectivity Under Teleoperation Latency](https://pmc.ncbi.nlm.nih.gov/articles/PMC11599268/)
- [Frontiers: Toward Enhanced Teleoperation Through Embodiment](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2020.00014/full)
- [MDPI: Interface Transparency Issues in Teleoperation](https://www.mdpi.com/2076-3417/10/18/6232)
- [ACM: Embodiment, Presence, and Their Intersections](https://dl.acm.org/doi/fullHtml/10.1145/3389210)
- [ALOHA Project Page](https://tonyzhaozh.github.io/aloha/)
- [Mobile ALOHA](https://arxiv.org/abs/2401.02117)
- [GELLO Paper](https://arxiv.org/html/2309.13037v2)
- [Open-TeleVision](https://robot-tv.github.io/)
- [Bunny-VisionPro](https://arxiv.org/html/2407.03162v1)
- [DexCap](https://arxiv.org/html/2403.07788v1)
- [How to Train Your Robots?](https://arxiv.org/abs/2503.07017)
- [TeleOpBench](https://arxiv.org/html/2505.12748v1)
- [TypeTele](https://arxiv.org/abs/2507.01857)
- [Real-to-Sim-to-Real Shared Autonomy](https://arxiv.org/abs/2603.17016)
- [SPIRIT Shared Autonomy](https://arxiv.org/html/2603.05111)
- [TASC: Task-Aware Shared Control](https://arxiv.org/html/2509.10416v1)
- [Human-Agent Joint Learning](https://arxiv.org/abs/2407.00299)
- [Springer: Multi-Modal Cognitive Interface](https://link.springer.com/article/10.1007/s10845-024-02451-x)
- [Cyborg and Bionic Systems: AR-Enhanced Teleoperation](https://spj.science.org/doi/10.34133/cbsystems.0098)
- [ACM: Dynamic Task-Based Overlays](https://dl.acm.org/doi/10.1145/3648536.3648544)
- [Springer: Predictive Display for Teleoperation](https://link.springer.com/article/10.1186/s40648-023-00258-8)
- [ScienceDirect: Low-Cost Predictive Display](https://www.sciencedirect.com/science/article/pii/S1071581920301385)
- [arXiv: Robotic Cloth Manipulation Review](https://arxiv.org/html/2407.01361v1)
- [Frontiers: Deep Learning Robotic Cloth Manipulation](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2026.1752914/full)
- [NeurIPS 2024: GarmentLab](https://proceedings.neurips.cc/paper_files/paper/2024/file/15f80ec0fed53885d2ca6272edb96ede-Paper-Conference.pdf)
- [NSF: Haptic Feedback in Surgical Teleoperation](https://par.nsf.gov/servlets/purl/10359277)
- [arXiv: Haptic Stiffness Perception](https://arxiv.org/html/2412.02613)
- [NASA: Telerobotic Mission Control Performance](https://ntrs.nasa.gov/citations/20205008229)
- [arXiv: Role of Embodiment in Whole-Body Teleoperation](https://arxiv.org/abs/2509.03222)
- [NuExo Exoskeleton](https://arxiv.org/html/2503.10554v1)
- [DexUMI](https://arxiv.org/html/2505.21864v3)
- [AnyTeleop](https://arxiv.org/html/2307.04577v3)
- [UniBiDex](https://arxiv.org/html/2601.04629v1)
- [ACT Policy](https://arxiv.org/abs/2304.13705)
