# Deep Research: Robotic Cloth/Fabric Manipulation - Why It's One of the Hardest Problems in Robotics

**Date:** April 20, 2026

---

## 1. Why Cloth Manipulation Is Fundamentally Hard for Robots

Cloth manipulation is widely regarded as one of the most challenging problems in robotic manipulation. Unlike rigid objects with fixed geometry, cloth presents a unique combination of difficulties that compound upon each other:

### 1.1 Near-Infinite Degrees of Freedom

A piece of cloth is a continuous deformable surface that can take on essentially infinite configurations. Unlike a rigid body with 6 DOF (position + orientation), a cloth mesh might be modeled with thousands of particles, each with its own position state. This means:

- The configuration space is astronomically large
- There is no compact state representation that fully captures cloth shape
- Planning in this space is computationally intractable using traditional methods
- Every unique way a shirt crumples is a new challenge for the robot ([NPR](https://www.npr.org/2022/10/22/1130552239/robot-folding-laundry))

### 1.2 Complex, Nonlinear Dynamics

Cloth exhibits highly nonlinear dynamics including:

- **Non-rigid deformation** under gravity and contact forces
- **Friction interactions** between cloth layers and with surfaces
- **Inertial effects** during dynamic manipulation (flinging, shaking)
- **Hysteresis** - cloth does not return to previous states predictably
- **Material-dependent behavior** - different fabrics (silk vs. denim vs. cotton) behave completely differently under the same forces ([MDPI Sensors](https://www.mdpi.com/1424-8220/23/5/2389))

### 1.3 Self-Occlusion

Cloth's many degrees of freedom introduce severe self-occlusion, making state estimation extremely difficult ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10007406/)). When cloth folds over itself:

- Parts of the garment become invisible to cameras
- The robot cannot determine how many layers exist at a given point
- Folded/crumpled states are highly ambiguous from visual observation alone
- Even depth cameras struggle with thin overlapping layers

### 1.4 State Estimation is Unsolved

Because of self-occlusion and deformability, full state estimation of cloth remains an open problem. A robot cannot simply "look" at a crumpled shirt and know its complete 3D configuration. The fabric may be:

- Folded inside itself in ways invisible to any camera angle
- Wrinkled in ways that create ambiguous depth readings
- Partially attached to the surface via static friction in unknown locations

Research at CMU has specifically focused on "seeing the unseen" - closed-loop occlusion reasoning for cloth manipulation that attempts to infer hidden cloth geometry ([CMU Robotics Institute](https://www.ri.cmu.edu/publications/seeing-the-unseen-closed-loop-occlusion-reasoning-for-cloth-manipulation/)).

### 1.5 Contact-Rich Manipulation Challenges

Cloth manipulation is inherently contact-rich, and contact-rich manipulation has fundamental challenges because of the rapidly growing combinatorics inherent to the amount of contact involved ([Science Robotics](https://www.science.org/doi/10.1126/scirobotics.ads6790)):

- The discrete and multi-modal nature of contact makes trajectory generation extremely difficult
- Force/torque sensors cannot distinguish between different contact points on the cloth
- Sub-millimeter changes in grasp position can result in completely different outcomes
- Cloth-on-cloth friction creates stick-slip behavior that is hard to model

### 1.6 No Fixed Grasp Points

Unlike rigid objects with stable grasp affordances, cloth has no natural handles. The same garment can be grasped at any point, and the outcome of manipulation depends critically on:

- Exactly where the cloth is grasped
- How much material is pinched
- The angle and force of the grasp
- Whether multiple layers are captured

Vision is not sufficient to solve this task alone - fine touch abilities are needed, sensing weight, weight shifting, and fabric properties ([Knowable Magazine](https://knowablemagazine.org/content/article/technology/2025/why-robots-cant-fold-laundry)).

---

## 2. State of the Art in Robotic Cloth Folding

### 2.1 Key Systems and Their Performance

| System | Year | Speed | Success Rate | Method |
|--------|------|-------|--------------|--------|
| SpeedFolding (Berkeley) | 2022 | ~2 min/garment | 93% | Learned bimanual primitives |
| UniFolding (CoRL) | 2023 | N/A | Variable | VR-trained unified policy |
| SSFold | 2024 | N/A | 66-100% per task | Graph dynamics from demos |
| Figure AI Helix | 2025 | N/A | Demo-quality | End-to-end neural net |
| Weave Isaac 0 | 2026 | 30-90 min/load | Requires human backup | Autonomy + teleop assist |
| BiFold (ICRA) | 2025 | N/A | SOTA on benchmark | Vision-language model |

### 2.2 ICRA 2024 Cloth Competition Results

The ICRA 2024 Cloth Competition provided the first rigorous, independent benchmark for robotic cloth unfolding. Eleven teams competed in head-to-head evaluation focused on grasp pose selection for in-air robotic cloth unfolding ([AIRO IDLab](https://airo.ugent.be/cloth_competition/)):

- **Top score:** 0.60 coverage (AIR-JNU team)
- **Key insight:** Hand-engineered methods performed surprisingly well compared to learned approaches
- **Gap revealed:** Significant discrepancy between claimed performance in papers vs. independent evaluation
- Dataset of 679 unfolding demonstrations across 34 garments was released

### 2.3 Commercial Attempts

**Weave Robotics Isaac 0 (2026):** The first commercially available laundry-folding robot shipped to Bay Area customers. Key facts ([New Atlas](https://newatlas.com/robotics/weave-robotics-isaac-robot-fold-laundry-teleoperation/)):
- $7,999 up-front or $450/month subscription
- Takes 30-90 minutes to fold a load
- Still requires human teleoperator intervention for tricky garments
- When the robot encounters errors, a remote specialist takes control for 5-10 seconds

This is remarkable: even a production-grade, single-purpose robot dedicated exclusively to cloth folding still cannot do it fully autonomously in 2026.

---

## 3. SpeedFolding (UC Berkeley) - Deep Dive

SpeedFolding represents one of the most significant advances in robotic cloth folding, achieving the first sub-2-minute garment fold with high reliability ([SpeedFolding Project Page](https://pantor.github.io/speedfolding/)).

### 3.1 System Architecture

- **Robot:** ABB YuMi industrial dual-arm robot (~$58,000)
- **End-effectors:** Parallel grippers with 3D-printed teeth extensions for improved fabric grasping
- **Sensors:** Overhead RGB-D cameras
- **Software:** BiManual Manipulation Network (BiMaMa-Net)

### 3.2 BiMaMa-Net (Bimanual Manipulation Network)

The core neural network predicts two corresponding gripper poses to parameterize bimanual action primitives without spatial restrictions. The architecture:

- Takes RGB-D observation as input
- Predicts pick poses for multiple primitive types simultaneously
- Handles automated calibration for robot reachability constraints
- Outputs parameterized primitives: fling, drag, and pick-and-place

### 3.3 Manipulation Primitives

SpeedFolding decomposes cloth manipulation into learned primitives:

1. **Fling:** Both arms grasp the cloth and dynamically stretch it in the air - this is the key smoothing action
2. **Drag:** Both arms perform coordinated dragging motions to flatten cloth on the table
3. **Pick-and-Place:** Precise placement actions used for the actual folding step

### 3.4 Training Data

- 4,300 human-annotated or self-supervised actions
- Combination of human demonstrations and automated data collection
- User-defined folding lines specify the desired fold

### 3.5 Performance

- **Speed:** 30-40 garments/hour, most under 2 minutes per fold
- **Success rate:** 93%
- **Improvement:** 5-10x faster than prior work (which required 10-20 minutes per fold)
- **Generalization:** Can identify fold strategy based on color, shape, or stiffness

The key insight is that the two-phase approach (first smooth, then fold) dramatically simplifies the problem. Smoothing removes the exponential state complexity of crumpled cloth, reducing it to a nearly flat configuration where folding becomes tractable.

---

## 4. ClothFunnels and Other Key Research

### 4.1 ClothFunnels (Columbia University, 2022)

ClothFunnels introduces "canonicalized-alignment" - the idea of reducing arbitrary garment configurations into a standard form before downstream manipulation ([ClothFunnels Project](https://clothfunnels.cs.columbia.edu/)):

- **Insight:** Rather than learning to fold from arbitrary states, first learn to bring cloth into a canonical configuration
- **Method:** Multi-arm, multi-primitive policy that chooses between dynamic flings and quasi-static pick-and-place
- **Result:** Even simple hand-designed folding policies work well when cloth starts in a canonical pose
- **Impact:** Bridges the gap between rigid-object manufacturing and deformable manipulation

### 4.2 FlingBot (Columbia, CoRL 2021 Best System Paper)

FlingBot demonstrated "the unreasonable effectiveness of dynamic manipulation for cloth unfolding" ([FlingBot Project](https://flingbot.cs.columbia.edu/)):

- **Key insight:** High-velocity dynamic fling actions are dramatically more effective than quasi-static pick-and-place for unfolding
- **Performance:** Over 80% coverage within just 3 actions on novel cloths
- **Generalization:** Despite training on rectangular cloths only, directly generalizes to shirts
- **Why it works:** Flings exploit air resistance and inertia to spread cloth, effectively expanding the robot's reach beyond its workspace

### 4.3 FabricFlowNet (CoRL 2022, CMU/David Held's group)

FabricFlowNet uses optical flow as both input and action representation ([PMLR](https://proceedings.mlr.press/v164/weng22a.html)):

- **Innovation:** Optical flow between observation and goal images provides an effective cloth correspondence representation
- **Capability:** Elegantly switches between bimanual and single-arm actions
- **Generalization:** Trained on single square cloth, generalizes to T-shirts and rectangular cloths
- **Sim-to-real:** Demonstrated effective transfer from simulation to real bimanual robot

### 4.4 SSFold (2024, IEEE TASE)

SSFold learns to fold arbitrary crumpled cloth using graph dynamics from human demonstration ([arxiv](https://arxiv.org/abs/2411.02608)):

- **Data collection:** 800 human demonstration videos over 21 hours using YOLOv10 hand tracking
- **Architecture:** Two-stream (sequential + spatial) with a connectivity dynamics model
- **No expensive hardware:** Uses single monocular camera and YOLOv10 for hand/keypoint detection
- **Results:** 66.7-100% success rate across 6 different cloth folding tasks on UR5 robot
- **Generalization:** Works on unseen fabrics with diverse colors, shapes, and stiffness

### 4.5 AdaFold (2024, IEEE RA-L)

AdaFold introduces feedback-loop manipulation for cloth folding ([AdaFold Project](https://adafold.github.io/)):

- **Key innovation:** Re-plans the folding trajectory at every timestep using MPC
- **Method:** Extracts particle-based cloth representation from RGB-D, uses learned dynamics model
- **Semantic descriptors:** Distinguishes between ambiguous point clouds of differently-folded cloth
- **Result:** Adapts to cloth with varying physical properties; generalizes sim-to-real

### 4.6 BiFold (ICRA 2025)

BiFold combines language guidance with bimanual cloth folding ([arxiv](https://arxiv.org/abs/2501.16458)):

- **Innovation:** Uses pre-trained vision-language model to predict manipulation actions conditioned on text instructions
- **Addresses data scarcity:** Novel dataset with automatically parsed actions and language-aligned instructions
- **Performance:** State-of-the-art on language-conditioned folding benchmark
- **Generalization:** Strong generalization to new instructions, garments, and environments

### 4.7 UniFolding (CoRL 2023)

A unified system for garment unfolding and folding ([GitHub](https://github.com/xiaoxiaoxh/UniFolding)):

- **Training:** Human demonstrations via VR (offline) + human-in-the-loop fine-tuning (online)
- **Perception:** Based on garment's partial point cloud for generalization
- **Tested on:** 20 shirts with significant variations in textures, shapes, and materials
- **Architecture:** UFONet neural network integrating unfolding and folding into single adaptable policy

---

## 5. Teleoperation of Cloth Manipulation

### 5.1 Why Teleoperation of Cloth is Exceptionally Difficult

Your experience finding cloth folding "nearly impossible" to teleoperate aligns with the fundamental challenges:

1. **Lack of force feedback:** Most teleoperation systems provide only visual feedback. Without feeling the cloth, operators cannot sense:
   - How much fabric they have grasped
   - Whether they are pulling too hard (tearing risk)
   - Subtle slip of fabric between fingers
   - How many layers they are manipulating

2. **Latency amplifies errors:** Any delay between command and execution is catastrophic for cloth because:
   - Cloth continues deforming during the delay
   - By the time the operator sees the result, the cloth state has already changed
   - Corrections overshoot and create new deformation problems

3. **Precision requirements exceed most interfaces:** Cloth folding requires:
   - Sub-centimeter grasp positioning
   - Coordinated bimanual motions
   - Speed-dependent actions (flings need velocity; folds need precision)
   - Real-time trajectory adaptation as cloth deforms

4. **Occlusion during manipulation:** The operator's view is often blocked by:
   - The robot's own arms and grippers
   - The cloth itself as it is lifted or folded
   - Camera angles that cannot show both the top and underside of the cloth

### 5.2 Systems That Attempt Cloth Teleoperation

**VR Framework for Cloth Folding (2023):** A specific framework for human-robot collaboration in cloth folding data collection uses VR to leverage immersive experience for intuitively defining folding plans. Uses skeleton representations to help users define folding plans for garment classes ([arxiv](https://arxiv.org/html/2305.07493v2)).

**OPEN TEACH:** A unified teleoperation framework supporting multiple arms and hands, calibration-free operation, works across simulation and real-world ([Academia.edu](https://www.academia.edu/124580827/OPEN_TEACH_A_Versatile_Teleoperation_System_for_Robotic_Manipulation)).

**SoftMimicGen (2025):** Uses Apple Vision Pro to collect source human demonstrations, retargeting hand motions to either parallel-jaw gripper or dexterous robotic hand. Enables large-scale data generation from only a small number of human teleoperated demonstrations ([arxiv](https://arxiv.org/html/2603.25725v1)).

**Weave Robotics (2026):** The most telling commercial example - their production robot still requires human teleoperator intervention for "tricky garments," with specialists taking control for 5-10 second adjustments ([The Register](https://www.theregister.com/2026/02/12/laundry_folding_robot_8000_dollars_teleoperated/)).

### 5.3 The Consensus on Teleoperation for Cloth

The research community has largely concluded that:

- Pure teleoperation of cloth is impractical for production use
- Teleoperation is primarily useful as a **data collection method** for training autonomous policies
- The most effective approach is **shared autonomy** - the robot handles routine actions while humans intervene only for edge cases
- Contact-rich manipulation datasets (including cloth) are "the hardest to collect well because they require precise force/torque sensing, sub-millisecond synchronization across modalities, and teleoperators who understand contact dynamics" ([Claru](https://claru.ai/guides/how-to-build-a-contact-rich-manipulation-dataset))

---

## 6. Sensors and End-Effectors for Cloth

### 6.1 End-Effector Types

**Parallel Grippers (Most Common):**
- Simple, reliable, widely available
- SpeedFolding adds 3D-printed teeth for better fabric grasping
- Struggle with single-layer grasping and delicate fabrics
- Cannot perform in-hand manipulation of cloth

**Specialized Cloth Grippers:**
- **Microneedle grippers:** Embedded microneedles for delicate fabric handling without damage ([ResearchGate](https://www.researchgate.net/publication/342407645_Delicate_Fabric_Handling_Using_a_Soft_Robotic_Gripper_With_Embedded_Microneedles))
- **Pin/brush-based:** Good for initial grasping from flat surfaces
- **Vacuum/suction:** Works for flat configurations but fails on crumpled cloth
- **Electrostatic:** Can attract cloth without mechanical contact

**Gripper-on-Gripper (G.O.G, 2024):** A novel design enabling bimanual cloth manipulation with a single robot arm by mounting a secondary gripper system on the primary gripper ([arxiv](https://arxiv.org/html/2401.10702v1)).

**Dexterous Hands:**
- Figure AI's Helix uses multi-fingered hands for cloth folding
- Much more capable but dramatically more complex to control
- Enable edge tracing, corner pinching, surface smoothing
- GarmentLab benchmark supports dexterous hand evaluation ([NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/15f80ec0fed53885d2ca6272edb96ede-Abstract-Conference.html))

### 6.2 Tactile Sensing

Tactile sensing is increasingly recognized as critical for cloth manipulation:

- **Vision-based tactile sensors (GelSight-type):** Can detect cloth edges, corners, and layer boundaries
- **Learning to singulate layers of cloth using tactile feedback** is an active area ([ResearchGate](https://www.researchgate.net/publication/366618099_Learning_to_Singulate_Layers_of_Cloth_using_Tactile_Feedback))
- **Touch G.O.G.:** Combines visuotactile gripper with dedicated perception algorithms for bimanual cloth manipulation ([arxiv](https://arxiv.org/html/2603.10609))
- **Active tactile palms:** Integrate actuation and high-resolution sensing for adaptive grasping in contact-rich tasks ([Nature](https://www.nature.com/articles/s44182-026-00079-y))

### 6.3 The Sensing Gap

A fundamental challenge: force/torque sensing lacks spatial resolution. It measures aggregate load but cannot distinguish between different contact points or provide pressure distribution across a surface ([Claru](https://claru.ai/guides/how-to-build-a-contact-rich-manipulation-dataset)). This is precisely what cloth manipulation requires - knowing exactly where and how the fabric is contacting the fingers.

---

## 7. Dual-Arm Coordination in Cloth Tasks

### 7.1 Why Bimanual Is Essential

Almost all successful cloth folding systems use dual-arm (bimanual) robots. Single-arm approaches face severe limitations:

- Cannot perform fling actions (require stretching cloth between two grippers)
- Cannot hold one part of cloth stable while manipulating another
- Cannot perform simultaneous grasp-and-fold operations
- Reach range is limited - flings exploit dual-arm span to handle larger garments

### 7.2 Key Bimanual Systems

- **ABB YuMi:** Used in SpeedFolding - industrial dual-arm with high precision
- **Dual UR5:** Used in FlingBot - two universal robot arms with larger workspace
- **ALOHA/ACT systems:** Low-cost bimanual teleop platforms adapted for cloth
- **SmolVLA:** 450M-parameter VLA model fine-tuned on 50 teleoperated demonstrations for bimanual cloth folding ([Vizuara Newsletter](https://www.vizuaranewsletter.com/p/teaching-robots-to-fold-clothes-smolvla))

### 7.3 Coordination Strategies

Research shows effective coordination requires:

1. **Learned switching between bimanual and single-arm actions** - FabricFlowNet elegantly handles this
2. **Asymmetric roles** - one arm often holds while the other manipulates
3. **Dynamic primitives** - fling requires synchronized, high-velocity bimanual motion
4. **Independent planning** - some phases need independent arm control for smoothing

### 7.4 Alternative: Single-Arm Bimanual

The G.O.G. design demonstrates that creative gripper engineering can achieve bimanual-like capability with a single arm, reducing cost and complexity while maintaining cloth manipulation capability ([arxiv](https://arxiv.org/html/2401.10702v1)).

---

## 8. Simulation Environments for Cloth

### 8.1 SoftGym (2020, CoRL)

The foundational benchmark for deformable object manipulation RL ([SoftGym GitHub](https://github.com/Xingyu-Lin/softgym)):

- Built on **NVIDIA FleX** particle-based physics engine
- Models cloth as particles with position-based dynamics (PBD) constraints
- Standard OpenAI Gym API for RL agent interaction
- Runs ~4x real-time on NVIDIA 2080Ti GPU
- 1 million sim steps = 6 hours wall clock = 35+ hours of real robot time
- Includes tasks: ClothFold, ClothFlatten, ClothDrop

### 8.2 GarmentLab (NeurIPS 2024)

The most comprehensive recent benchmark ([GarmentLab GitHub](https://github.com/GarmentLab/GarmentLab)):

- Built on **NVIDIA Isaac Sim** (GPU-accelerated, ray-traced rendering)
- Supports both **PBD and FEM** simulation methods
- 11 categories of garments with realistic meshes
- 20 tasks across 5 groups including garment-garment and garment-avatar interactions
- Integrates teleoperation pipeline with ROS
- Supports grippers, suction, and dexterous hands
- Includes sim-to-real pipeline with designed transfer algorithms

### 8.3 Other Notable Simulators

- **NVIDIA PhysX 5.x:** Successor to FleX with improved cloth simulation
- **MuJoCo (with cloth extensions):** Some researchers have added cloth capabilities
- **Blender/SOFA:** Used for generating training data with realistic rendering
- **DiffClothSim:** Differentiable cloth simulation for gradient-based optimization

### 8.4 The Sim-to-Real Gap Problem

The sim-to-real gap remains the central challenge for cloth simulation ([IEEE Xplore](https://ieeexplore.ieee.org/abstract/document/10417136)):

- Most simulators originate from graphics and prioritize visual appearance over physical realism
- Dynamic interactions (fast flings, collisions) are particularly poorly modeled
- Material properties are difficult to calibrate to match real fabrics
- Contact and friction between cloth layers are oversimplified
- Real cloth has micro-scale properties (thread weave, fiber flexibility) not captured by particle systems

**SIM1 (2025)** attempts to address this with "physics-aligned simulation" that constrains strain evolution during contact, enabling zero-shot sim-to-real transfer for deformable manipulation ([arxiv](https://arxiv.org/html/2604.08544)).

---

## 9. Automation vs. Human Teleoperation for Cloth Folding

### 9.1 What Can Be Automated Today

| Sub-Task | Automation Level | Notes |
|----------|-----------------|-------|
| Unfolding (fling) | High | FlingBot achieves 80%+ coverage in 3 actions |
| Smoothing/flattening | High | Learned primitives work well |
| Simple folds (towels) | Medium-High | 93% success for SpeedFolding |
| Complex folds (shirts) | Medium | Requires multi-step sequencing |
| Handling novel garments | Low-Medium | Generalization remains limited |
| Recovery from errors | Low | Still requires human intervention |
| Multi-garment sorting | Low | Category recognition + planning |

### 9.2 Where Humans Are Still Needed

Weave Robotics' production experience is the best evidence: their robot folds autonomously most of the time, but requires human teleoperator intervention for:

- Tricky garments with unusual geometry
- Error states the robot cannot self-diagnose
- Garments with accessories (buttons, zippers, drawstrings)
- Extremely crumpled initial configurations
- Material types the system was not trained on

### 9.3 The Path Forward: Shared Autonomy

The consensus in the field is converging on a **shared autonomy** model:

1. Robot performs routine manipulation autonomously (smoothing, simple folds)
2. System detects uncertainty or failure conditions
3. Human teleoperator intervenes briefly for edge cases
4. Robot resumes autonomous operation
5. Human interventions become training data for future autonomy

This is exactly Weave's architecture: autonomy with 5-10 second human corrections when needed.

### 9.4 Data Collection Strategy

For training autonomous policies, teleoperation is used as a data collection tool rather than a production method:

- **SpeedFolding:** 4,300 human-annotated actions
- **SSFold:** 800 human demonstration videos (21 hours)
- **SmolVLA:** 50 teleoperated demonstrations
- **Figure AI Helix:** 80 hours of training footage
- **UniFolding:** VR-collected demonstrations + human-in-the-loop refinement

---

## 10. What Makes a Fold Successful?

### 10.1 Primary Metrics

There is no universally adopted metric for folding success, which is itself a challenge for the field. Common metrics include ([arxiv](https://arxiv.org/html/2407.01361v1)):

**Final Ratio (FR):** The ratio between the area covered by the top half and the total final area. FR = 1 means perfect alignment of the two halves after folding.

**Intersection over Union (IoU):** Comparing the achieved folded shape to a target shape template. AdaFold achieves IoU of 0.83.

**Coverage:** Percentage of target area covered by the cloth (primarily used for unfolding/flattening tasks).

**Success Rate:** Binary success/failure, but criteria vary wildly between papers.

### 10.2 What Makes Folding Physically Difficult

1. **Edge alignment:** The fold requires two edges to align precisely - any rotational or translational error accumulates
2. **Maintaining flatness during fold:** The cloth must remain relatively flat as one half is lifted and placed on the other
3. **Material stiffness interaction:** Bending coefficients significantly influence each fold, with errors potentially accumulating across multi-fold sequences
4. **Gravity effects:** As cloth is lifted for folding, gravity causes unpredictable draping
5. **Static friction uncertainty:** Whether the "base" half stays in place during folding depends on surface friction

### 10.3 The Standardization Problem

A critical finding from the ICRA 2024 competition: there is a significant discrepancy between performance claimed in papers vs. independent evaluation. This suggests that many published results benefit from favorable evaluation conditions that do not generalize ([AIRO IDLab Competition](https://airo.ugent.be/cloth_competition/)).

---

## 11. Cloth Manipulation Teleoperation Datasets

### 11.1 Available Datasets

| Dataset | Size | Method | Tasks |
|---------|------|--------|-------|
| SpeedFolding data | 4,300 actions | Human annotation + self-supervised | Smoothing + folding |
| SSFold demonstrations | 800 videos (21 hrs) | Monocular camera + YOLOv10 tracking | 6 folding tasks |
| ICRA 2024 Competition | 679 demonstrations | Real robot platform | Unfolding grasp selection |
| RoboTurk cloth | Part of larger dataset | Web-based teleoperation | Various manipulation |
| UniFolding VR data | Not specified | VR demonstrations | Unfolding + folding |
| SoftMimicGen | Small source set | Apple Vision Pro | Deformable objects |
| 111-hour dataset | 111 hrs, 54 operators | Large-scale teleoperation | 3 manipulation tasks |

### 11.2 Data Collection Challenges

Data collection for cloth manipulation teleoperation faces unique obstacles ([Frontiers in Robotics and AI](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2026.1752914/full)):

- **Operator skill variation:** Different teleoperators have vastly different success rates
- **Contact-rich sensing requirements:** Need precise force/torque, sub-millisecond synchronization
- **Demonstration quality:** Poor demonstrations actively harm policy learning
- **Scaling difficulty:** Complex setups limit number of operators and throughput
- **Labeling ambiguity:** Hard to define what constitutes "correct" manipulation

### 11.3 Methods for Collecting Demonstrations

1. **Kinesthetic teaching:** Physically guiding the robot (precise but slow, requires co-location)
2. **Motion capture:** Tracking human hands and mapping to robot (natural but imprecise mapping)
3. **Teleoperation systems:** Joystick, VR, or leader-follower robots (scalable but skill-dependent)
4. **Expert script policies:** Automated data collection using hand-coded routines (limited variety)
5. **Human video learning:** Extract manipulation strategies from watching human folding videos (newest approach, most scalable)

---

## 12. Contact-Rich Manipulation and Why It's Hard to Teleoperate

### 12.1 The Fundamental Problem

Contact-rich manipulation requires reasoning about forces, friction, and deformation simultaneously - information that is extremely difficult to transmit through a teleoperation interface:

- **The operator sees but cannot feel:** Visual information alone is insufficient for sensing fabric weight, stiffness, and slip
- **Force bandwidth mismatch:** Humans control forces at >100Hz; teleoperation loops typically run at 10-30Hz
- **Haptic feedback limitations:** Even with haptic devices, the fidelity of force reproduction is orders of magnitude below human tactile resolution
- **Compliance vs. precision tradeoff:** Cloth requires both gentle compliance (not tearing) and precise positioning (accurate folds)

### 12.2 Why Cloth Is the Worst Case for Teleop

Cloth represents perhaps the most challenging contact-rich manipulation scenario for teleoperation because:

1. **Continuous deformation:** Unlike rigid contact where discrete events happen, cloth deforms continuously requiring continuous force modulation
2. **Multi-point contact:** The entire surface of the cloth is potentially in contact with surfaces, other cloth layers, and the gripper
3. **No rigid reference frame:** With rigid objects, you can plan in workspace coordinates. With cloth, the "object frame" is meaningless
4. **History-dependent state:** The current cloth state depends on the entire history of manipulation, not just the current action
5. **Exploration sensitivity:** Slight differences in exploration (how you poke/lift the cloth to understand it) lead to entirely different states

### 12.3 ADAPT-Teleop (2025)

A notable recent advance: ADAPT-Teleop is a robotic hand with human-matched embodiment that enables dexterous teleoperated manipulation. The key insight is that matching the robot's kinematic structure to the human hand reduces the cognitive load of teleoperation for contact-rich tasks ([Nature npj Robotics](https://www.nature.com/articles/s44182-025-00034-3)).

### 12.4 Implications for Your Experience

Your finding that cloth folding via teleoperation is "nearly impossible" is entirely consistent with the research. The field has essentially concluded that:

- Direct teleoperation of cloth folding is not viable as a production method
- It is useful primarily for collecting small amounts of high-quality demonstration data
- The future is autonomous policies trained on demonstrations + human-in-the-loop for edge cases
- Even with the best interfaces (VR, haptic feedback), the information bandwidth between human and robot is too low for the information-rich task of cloth manipulation

---

## 13. Summary of Key Insights

### What Works

1. **Dynamic primitives (flings):** The single biggest unlock for cloth manipulation. Exploiting dynamics rather than quasi-static manipulation
2. **Smooth-then-fold decomposition:** Reducing crumpled cloth to flat cloth first makes folding tractable
3. **Learned policies from demonstrations:** 50-800 demonstrations can produce usable policies
4. **Bimanual coordination:** Essential for most cloth tasks, especially smoothing and folding
5. **Feedback-loop manipulation:** Re-planning at every step (AdaFold) handles material variation

### What Doesn't Work (Yet)

1. **Direct teleoperation for production:** Too slow, too error-prone, insufficient feedback
2. **Pure sim-to-real transfer:** Sim-to-real gap for cloth dynamics remains large
3. **Single general policy for all garments:** Generalization across garment types is limited
4. **Pure reinforcement learning:** Sample efficiency is too low for cloth's complexity
5. **Vision-only approaches:** Tactile/force sensing increasingly shown to be necessary

### The Research Frontier (2025-2026)

- **Vision-Language-Action models** (SmolVLA, BiFold) for language-conditioned folding
- **End-to-end neural policies** (Figure Helix) with multi-fingered dexterous hands
- **Shared autonomy** (Weave) as the practical deployment architecture
- **Real-to-sim-to-real** pipelines for closing the simulation gap
- **Foundation models** applied to cloth state estimation and planning
- **Temporal context in VLMs** for understanding folding progress over time

---

## 14. References and Key Labs

### Leading Research Groups

- **UC Berkeley AUTOLAB (Ken Goldberg):** SpeedFolding, data-driven manipulation
- **Columbia AI Robotics (Shuran Song):** FlingBot, ClothFunnels, DextAIRity
- **CMU Robotics Institute (David Held):** FabricFlowNet, SoftGym, DeformGS
- **KTH (Danica Kragic):** AdaFold, cloth dynamics modeling
- **AIRO Lab Ghent (Francis Wyffels):** ICRA Cloth Competition, competition-winning systems
- **Figure AI:** Helix end-to-end cloth folding with humanoid
- **Weave Robotics:** Commercial laundry folding

### Key Paper Links

- SpeedFolding: [arxiv.org/abs/2208.10552](https://arxiv.org/abs/2208.10552)
- ClothFunnels: [clothfunnels.cs.columbia.edu](https://clothfunnels.cs.columbia.edu/)
- FlingBot: [flingbot.cs.columbia.edu](https://flingbot.cs.columbia.edu/)
- FabricFlowNet: [arxiv.org/abs/2111.05623](https://arxiv.org/abs/2111.05623)
- SSFold: [arxiv.org/abs/2411.02608](https://arxiv.org/abs/2411.02608)
- AdaFold: [adafold.github.io](https://adafold.github.io/)
- BiFold: [arxiv.org/abs/2501.16458](https://arxiv.org/abs/2501.16458)
- UniFolding: [github.com/xiaoxiaoxh/UniFolding](https://github.com/xiaoxiaoxh/UniFolding)
- GarmentLab: [garmentlab.github.io](https://garmentlab.github.io/)
- SoftGym: [github.com/Xingyu-Lin/softgym](https://github.com/Xingyu-Lin/softgym)
- ICRA 2024 Cloth Competition: [airo.ugent.be/cloth_competition](https://airo.ugent.be/cloth_competition/)
- Unfolding the Literature (Survey): [arxiv.org/html/2407.01361v1](https://arxiv.org/html/2407.01361v1)
- Figure AI Helix: [figure.ai/news/helix-learns-to-fold-laundry](https://www.figure.ai/news/helix-learns-to-fold-laundry)
