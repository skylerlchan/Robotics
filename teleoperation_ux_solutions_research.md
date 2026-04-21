# Teleoperation UX Solutions: Industry Deep Dive

*Research compiled April 20, 2026*

The core problem: teleoperation for dexterous tasks (cloth folding, cable manipulation, object insertion) is extremely painful for operators, even experienced ones. This document maps out who has meaningfully improved the teleoperation UX and how they did it.

---

## Summary of Approaches

| Approach | Key Example | Fidelity | Operator Effort | Cost |
|----------|------------|----------|-----------------|------|
| Leader-follower arms (kinematic twin) | ALOHA, GELLO, LeRobot SO-100 | High | Moderate - physical matching | Low ($100-$20K) |
| VR headset + hand tracking | Open-TeleVision, 1X NEO | Medium-High | Low cognitive load | Medium ($3-5K) |
| Haptic gloves + dexterous hands | Shadow Robot + HaptX, DOGlove | Very High | Low (natural hand motion) | Very High ($100K+) or Low (open-source) |
| Exoskeleton/motion capture suit | Sanctuary AI, Telexistence | High | Low (whole body mapping) | High |
| Web browser / gamepad | Hello Robot Stretch | Low | Low but imprecise | Minimal |
| Shared autonomy (AI-assisted) | Real-to-Sim-to-Real, Skill-Assisted Teleop | Variable | Lowest | Software cost only |

---

## 1. ALOHA System (Stanford / Tony Zhao / Trossen Robotics)

**The gold standard for affordable bimanual teleoperation in research.**

### What It Is
ALOHA (A Low-cost Open-source HArdware system for bimanual teleoperation) is a leader-follower system where the operator physically moves a pair of "leader" robot arms, and the "follower" arms mirror those motions exactly. Total cost ~$20K for the full setup ([ALOHA project page](https://tonyzhaozh.github.io/aloha/)).

### Interface/Hardware
- **Leader arms:** Identical ViperX 300 6-DOF robot arms from Trossen Robotics (same kinematics as follower)
- **Follower arms:** Same ViperX 300 arms executing the task
- **No VR, no gloves, no headset** - pure kinematic matching
- **4 RGB cameras** (2 static overhead/side, 2 wrist-mounted on follower arms) streaming at 480x640
- Operator stands behind the leader arms and physically manipulates them

### Why It Works
- **Kinematic equivalence eliminates retargeting errors** - the leader IS the robot, just scaled
- The operator feels the workspace geometry directly through the leader arms
- **Zero training time** - if you can move the arms, you can teleoperate
- Joint positions recorded at 50Hz

### Key UX Insight
Tony Zhao's critical finding: even with this "easy" interface, collecting demonstrations for fine manipulation is HARD. Tasks like threading a zip tie or slotting a battery require extreme precision. The breakthrough was not in making teleoperation perfect but in developing **Action Chunking with Transformers (ACT)** - an algorithm that needs only 10 minutes of (imperfect) demonstration data to learn tasks at 80-90% success. The philosophy: make teleoperation good enough, then let the AI handle the rest ([Paper: arXiv:2304.13705](https://arxiv.org/abs/2304.13705)).

### Mobile ALOHA
Extended with a mobile base (AgileX Tracer). The operator walks behind the robot pushing it, while simultaneously controlling both arms. Cost: ~$32K total. Demonstrated cooking, cabinet manipulation, and elevator operation ([Mobile ALOHA project](https://mobile-aloha.github.io/)).

### Limitations
- Operator must be physically present next to the leader arms
- No force/haptic feedback - operator cannot feel what the robot grips
- Bimanual coordination while walking (Mobile ALOHA) is cognitively demanding
- Tasks requiring very fine finger dexterity (cloth folding) remain difficult because the gripper is a simple parallel jaw

---

## 2. GELLO (General, Low-cost, Lightweight teLeoperation)

**The most accessible and user-friendly leader-follower interface for research.**

### What It Is
A 3D-printed miniature leader arm that is kinematically equivalent to the target robot arm. Uses off-the-shelf Dynamixel servomotors. An open-source project designed to be universal across different robot arms ([Paper: arXiv:2309.13037](https://arxiv.org/abs/2309.13037)).

### Interface/Hardware
- 3D-printed joints that mirror the target robot's kinematics
- Off-the-shelf servomotors for joint position reading
- Gravity-compensated so operator doesn't fight the weight
- Costs ~$200-500 per arm

### Why It Works
- Kinematic equivalence means no retargeting math needed
- Extremely lightweight - reduces operator fatigue
- The "feel" of the workspace constraints transfers directly

### Key UX Insight
Research from 2025 shows GELLO can be **augmented with force feedback** (paper: "Improving Low-Cost Teleoperation: Augmenting GELLO with Force") - the servos provide resistance matching the forces the follower robot encounters. This dramatically improves operator precision for contact-rich tasks.

### Limitations
- Still requires physical presence
- One GELLO design per robot type (not universal across morphologies)
- No tactile/fingertip feedback

---

## 3. Open-TeleVision (CMU / UC San Diego)

**First open-source system using Apple Vision Pro for immersive robot teleoperation.**

### What It Is
A VR-based teleoperation system that streams stereoscopic 3D video from robot cameras to an Apple Vision Pro headset, while tracking the operator's hand and wrist poses to control robot arms ([Paper: arXiv:2407.01512](https://arxiv.org/html/2407.01512v2)).

### Interface/Hardware
- **Apple Vision Pro** (or Meta Quest) for stereoscopic viewing and hand tracking
- Robot-mounted stereo cameras for 3D visual feedback
- Hand pose streaming from VR device to robot end-effectors
- Works over WiFi - operator can be anywhere

### Why It Works
- **Immersive depth perception** - operators see the workspace in 3D, dramatically improving spatial reasoning
- **Natural hand/wrist tracking** eliminates the need for leader arms
- The operator can look around by moving their head (active vision)
- No physical hardware beyond the headset

### Key UX Insight
The paper specifically notes that "immersive active visual feedback" (stereoscopic + head-gaze controlled cameras) is the critical missing ingredient in most teleoperation systems. When operators can't perceive depth, they crash into things and misjudge grasp distances. Open-TeleVision demonstrated bimanual dexterous tasks including cloth folding.

### Limitations
- Hand tracking from VR headsets has limited precision for very fine manipulation
- No haptic/force feedback
- Latency-sensitive (requires good network)
- Apple Vision Pro is $3,500

---

## 4. 1X Technologies (NEO Robot)

**Commercial humanoid using VR teleoperation for data collection and "Expert Mode" deployment.**

### What It Is
1X Technologies builds the NEO humanoid robot for home use. They use VR-based teleoperation both for data collection to train AI and as a live service ("Expert Mode") where remote operators control the robot when it encounters tasks it cannot do autonomously ([1X NEO info](https://www.1x.tech/neo)).

### Interface/Hardware
- **VR headset + controllers** for remote operators
- Remote operators control NEO via VR when robot encounters unknown tasks
- AI watches the teleoperation and learns from the demonstrations
- Privacy: people in camera feed are blurred

### Key UX Insight
1X's model is the most commercially pragmatic: they acknowledged that full autonomy is not yet achievable, so they designed a hybrid system where teleoperation is a **product feature**, not just a data collection hack. When NEO doesn't know how to do something, a remote operator steps in seamlessly. The AI continually improves from these interventions.

### Limitations
- Details of their VR teleoperation rig are not fully public
- Unclear how they handle dexterous manipulation specifically (NEO's hands are relatively simple)

---

## 5. Sanctuary AI (Phoenix Robot)

**Full-body teleoperation using motion capture suit and haptic gloves.**

### What It Is
Sanctuary AI builds the Phoenix humanoid robot and uses their "Carbon" AI system. For data collection, they use full-body teleoperation with operators wearing motion capture equipment and haptic gloves ([Sanctuary AI](https://www.sanctuary.ai/technology)).

### Interface/Hardware
- Full-body motion capture suit
- Haptic gloves with force feedback
- VR headset for visual immersion
- Operators are trained professionals in dedicated teleoperation stations
- The Phoenix hand has 20+ DOF matching human hand dexterity

### Why It Works
- Full embodiment - the operator's entire body maps to the robot
- Haptic feedback enables contact-rich manipulation
- Professional operator workforce ensures consistency

### Key UX Insight
Sanctuary's approach is to invest heavily in both the robot hand fidelity AND the teleoperation interface quality. Their teleoperation system is reportedly the most immersive in the industry but also the most expensive and least accessible. They treat teleoperation as a serious engineering discipline, not an afterthought.

### Limitations
- Extremely expensive hardware (motion capture + haptics)
- Requires trained professional operators
- Not open-source or accessible to researchers
- Some skepticism exists about the level of autonomy vs. teleoperation in their demos

---

## 6. Shadow Robot Company (Teleoperation System)

**The highest-fidelity dexterous hand teleoperation commercially available.**

### What It Is
Shadow Robot makes the DEX-EE series of dexterous robotic hands (20 DOF, 24 movements, 120+ sensors) paired with a custom teleoperation system using lightweight gloves ([Shadow Robot Teleoperation](https://shadowrobot.com/teleoperation/)).

### Interface/Hardware
- **Shadow Glove**: Lightweight sensor glove that captures all finger/hand/wrist motions
- **HaptX Glove option**: Full haptic feedback including pressure, temperature, vibration
- **Shadow Tactile Fingertips**: Pressure sensors on robot fingertips feeding back to operator
- WiFi/5G for remote operation ("across the room or across continents")
- Bilateral setup available (two hands simultaneously)

### Why It Works
- 20 DOF hand with 120 sensors provides unprecedented accuracy
- Operator's natural hand movements are directly replicated
- Haptic feedback creates "telepresence" - operator feels what robot touches
- Modular system integrates into existing robot setups
- Very little training required (intuitive glove interface)

### Key UX Insight
Shadow Robot's whitepaper on "The State of Teleoperation in 2025" acknowledges that the key barrier is **not hardware fidelity but latency and situational awareness**. Even with perfect haptic feedback, operators struggle when visual feedback is delayed or when they lose spatial context. Their solution: minimizing latency and providing rich multi-sensory feedback simultaneously.

### Limitations
- Extremely expensive (Shadow Hands cost $100K+)
- Primarily for nuclear, pharmaceutical, and research sectors
- No mobile base - fixed workspace teleoperation
- Integration effort required for custom setups

---

## 7. Hello Robot (Stretch 3)

**The simplest teleoperation UX - web browser control.**

### What It Is
Hello Robot's Stretch 3 is a $24,950 mobile manipulator designed for homes and assistive applications. It supports multiple teleoperation modes ([Hello Robot Stretch 3](https://hello-robot.com/stretch-3)).

### Interface/Hardware
- **Web browser teleoperation**: Control from any device with a browser
- **Gamepad control**: Standard game controller
- **Dexterous teleoperation**: More advanced control mode
- Pan-tilt head camera with RGBD for operator viewpoint
- Gripper-mounted camera for close-up views
- 7 DOF manipulation (2 base, 1 lift, 1 telescoping, 3 wrist)

### Why It Works
- **Zero barrier to entry** - any device with a browser works
- The robot is simple enough (no dexterous hand) that a gamepad suffices
- Lightweight (24.5 kg) means safe around people
- Open-source software with ROS 2

### Key UX Insight
Hello Robot made a deliberate design choice: rather than building a human-like dexterous system requiring complex teleoperation, they designed a robot morphology that is EASY to teleoperate. The telescoping arm + compliant grabber gripper is not human-like but is incredibly simple to control remotely. The design philosophy is that **simpler robots need simpler teleoperation**.

### Limitations
- Not suitable for dexterous manipulation (cloth folding, etc.)
- Simple parallel jaw gripper limits task complexity
- Web teleoperation has latency issues
- Not designed for high-precision tasks

---

## 8. Telexistence (Japan)

**VR-first teleoperation deployed in real convenience stores.**

### What It Is
Telexistence builds robots specifically for retail/convenience store stock replenishment, teleoperated by remote workers wearing VR headsets. They deployed their TX SCARA and Model-T robots in FamilyMart convenience stores in Japan ([Telexistence](https://tx-inc.com/)).

### Interface/Hardware
- VR headset (custom) with stereoscopic cameras on robot
- Motion-tracked controllers for arm manipulation
- Operators work from remote control centers
- Target ratio: 1 operator controlling multiple robots

### Why It Works
- **Task-specific design**: The robot is optimized for shelf stocking, not general dexterity
- Remote operators can be lower-cost workers in different locations
- The VR interface provides sufficient immersion for the relatively simple pick-place tasks
- Deployed in real commercial operations (not just research)

### Key UX Insight
Telexistence discovered that for commercial viability, you need **one operator managing multiple robots** (target: 1:20 ratio). Their insight: robots handle 95% of tasks autonomously, and the human only intervenes for edge cases (product orientation, unfamiliar items). This "supervisor" model dramatically reduces per-robot teleoperation cost. The key is not making teleoperation easier per se, but making it RARER through autonomy.

### Limitations
- Limited to relatively simple pick-and-place tasks
- Not suitable for dexterous manipulation
- Commercial deployment has been challenging financially
- Latency issues with remote operation

---

## 9. GITAI (Space Teleoperation)

**Autonomous + teleoperated robots for space applications.**

### What It Is
GITAI builds robotic systems for space (ISS, lunar surface) that can switch between autonomous operation and ground-based teleoperation. They demonstrated successful operations aboard the ISS ([GITAI](https://gitai.tech/)).

### Interface/Hardware
- Ground control stations with joystick/controller interfaces
- Significant latency management (space communication delays)
- Autonomous capabilities for routine tasks
- Human teleoperation for complex/novel tasks

### Key UX Insight
GITAI's contribution to teleoperation UX is in **latency management** - space introduces 1-3 second delays. Their solution: predictive displays, command buffering, and significant autonomous sub-task execution. The operator gives high-level commands; the robot handles low-level execution. This approach has direct relevance to terrestrial teleoperation over imperfect networks.

---

## 10. DOGlove (Tsinghua University, 2025)

**Open-source haptic force feedback glove for $300.**

### What It Is
DOGlove is a low-cost, fully open-source haptic force feedback glove for dexterous manipulation teleoperation. Published at RSS 2025 ([Paper: arXiv:2502.07730](https://arxiv.org/abs/2502.07730), [GitHub](https://github.com/TEA-Lab/DOGlove)).

### Interface/Hardware
- Cable-driven mechanism provides force feedback to each finger
- Linear Resonant Actuators (LRA) on fingertips for haptic vibration feedback
- 21-DOF motion capture + 5-DOF haptic force feedback
- Total cost: ~$300 for materials
- Anthropomorphic structure matching human hand
- Works with AnyTeleop retargeting framework

### Why It Works
- **Dual feedback**: Both force (cable tension) and haptic (vibration) feedback
- User study shows operators can distinguish objects by touch alone while blindfolded
- Force feedback significantly improves success rate on contact-sensitive tasks (e.g., bottle slipping without dropping)
- Open-source and easy to manufacture

### Key UX Insight
DOGlove's paper demonstrates that **haptic force feedback dramatically improves operator performance** even without visual feedback. In their bottle-slipping experiment, adding force feedback significantly increased success rates, and adding haptic feedback on top further improved performance. The combination of knowing "how hard am I gripping" (force) and "am I touching something" (haptic vibration) is critical for dexterous tasks.

### Limitations
- Still a research prototype
- Requires calibration per operator
- Retargeting to robot hand morphology is non-trivial
- No off-the-shelf commercial version

---

## 11. Sarcos Robotics (Guardian XO / Guardian XT)

**Exoskeleton-based teleoperation for industrial strength tasks.**

### What It Is
Sarcos builds full-body powered exoskeletons (Guardian XO) and teleoperated upper-body robots (Guardian XT). The exoskeleton amplifies operator strength while preserving intuitive movement ([Sarcos/Paladin AI](https://www.paladinai.com/)).

### Interface/Hardware
- **Guardian XO**: Full-body powered exoskeleton - operator wears it and the robot amplifies force 20x
- **Guardian XT**: Upper-body teleoperated robot controlled from a remote station
- Force-feedback throughout the exoskeleton
- Operator feels load and resistance naturally

### Key UX Insight
The exoskeleton approach eliminates the "control abstraction" problem entirely - the operator just moves their body normally, and the robot follows. This is the most intuitive interface possible for gross motor tasks. However, Sarcos has struggled commercially (restructured as Paladin AI in 2024), suggesting that the exoskeleton approach may be too expensive/complex for the tasks it enables.

### Limitations
- Primarily for heavy-lifting tasks, not dexterous manipulation
- Very expensive hardware
- Operator must wear heavy equipment
- Company has faced financial difficulties

---

## 12. Astribot S1 (China, 2025)

**VR teleoperation optimized for ultra-efficient data collection.**

### What It Is
Astribot's S1 humanoid uses VR-based teleoperation specifically optimized for training data collection speed. Their "Teleoperation Series 1" focuses on collecting high-quality demonstrations as efficiently as possible ([Astribot](https://www.astribot.com/)).

### Interface/Hardware
- VR headset + controllers for full arm/hand teleoperation
- Emphasized "ultra-efficient data collection" workflows
- Eventually targets autonomous operation (demonstrated 1x speed autonomous tasks in late 2024)

### Key UX Insight
Astribot's contribution is in making the teleoperation-to-autonomy pipeline as fast as possible. They claim to have achieved autonomous operation at real-time speed (not sped up) for tasks initially taught via teleoperation, suggesting their teleoperation UX and data quality are good enough to train policies quickly.

---

## 13. LeRobot / Hugging Face Community

**Democratized teleoperation at $100-300 price points.**

### What It Is
LeRobot is Hugging Face's open-source robotics framework. The community builds affordable robots (SO-100 arm at ~$100-300) with leader-follower teleoperation for data collection ([LeRobot GitHub](https://github.com/huggingface/lerobot)).

### Interface/Hardware
- **SO-100 arm**: ~$100 leader-follower setup using Feetech servos
- **Leader arm** identical to follower arm (ALOHA-style approach)
- USB cameras for visual observation
- Python-based recording and playback
- Direct joint position mapping

### Known Teleoperation Difficulties (from community issues)
- Motor calibration issues (follower moves opposite direction to leader - [GitHub Issue #930](https://github.com/huggingface/lerobot/issues/930))
- Servo backlash and compliance makes precise control difficult
- No force feedback means operators can't tell when objects are being crushed
- Recording quality varies significantly between operators
- Low-cost servos have limited torque, creating "spongy" feel
- Camera placement critical but non-obvious for new users

### Key UX Insight
The LeRobot community reveals the **fundamental tension in affordable teleoperation**: cheap servos are imprecise and compliant, making the leader arm feel "mushy" and unpredictable. Users report that even simple pick-and-place becomes frustrating when you can't trust that the follower is doing exactly what the leader does. The community is actively exploring solutions like gravity compensation, better servo feedback, and higher-quality motors.

### Limitations
- Quality limited by servo precision
- No haptic feedback
- Assembly and calibration is non-trivial
- Limited to relatively simple tasks due to hardware constraints

---

## 14. Shared Autonomy / AI-Assisted Teleoperation

**The emerging frontier: AI that makes teleoperation easier in real-time.**

### Concept
Rather than improving the hardware interface, shared autonomy augments the human operator with AI assistance during teleoperation. The AI handles precision alignment, collision avoidance, and routine sub-tasks while the human provides high-level intent ([Paper: arXiv:2603.17016](https://arxiv.org/abs/2603.17016)).

### Key Approaches (2024-2026)

1. **Real-to-Sim-to-Real Shared Autonomy** (2026): Augments human teleoperation with learned corrective behaviors. Uses a kNN human surrogate to model operator actions in simulation, then provides real-time corrections during actual teleoperation.

2. **Skill-Assisted Teleoperation**: Operators select from libraries of parameterized skills rather than doing low-level control. E.g., "grasp this" rather than manually positioning fingers.

3. **Neural Shared Autonomy**: AI infers operator intent and provides automatic collision avoidance, pre-grasp alignment, or task-specific assistance.

4. **Bilateral Copilot Feedback**: Real-time synchronization where the robot "pushes back" against the operator to guide them toward better trajectories.

5. **Augmented Reality Overlays**: VR systems showing manipulability polytopes, constraint boundaries, and task state estimates to help operators understand the workspace.

### Key UX Insight
The central thesis of shared autonomy: **if the robot's strengths (local sensing, precise execution, speed) are fully utilized, the human's control effort can be reduced while simultaneously increasing task performance**. Studies show that even simple haptic augmentation during teleoperation makes operators perform tasks faster, more accurately, and with less cognitive load.

---

## 15. Universal Robots / Collaborative Robots

**Teaching by demonstration rather than teleoperation.**

### What It Is
Universal Robots and other cobot companies (Franka Emika/now Franka Robotics, Kinova) largely bypassed the teleoperation problem by using **direct physical guidance** - the operator grabs the robot arm directly and moves it through the desired trajectory.

### Interface/Hardware
- **Force/torque sensors** at joints detect when human is pushing
- Robot enters "zero gravity" mode (gravity-compensated, compliant)
- Teach pendant for fine adjustments and waypoint programming
- PolyScope software for visual programming

### Key UX Insight
The cobot approach reveals that for many industrial tasks, **the simplest "teleoperation" is just grabbing the robot and moving it**. No leader arm, no VR, no gloves. This works well for pick-place and simple assembly but breaks down for bimanual tasks or tasks requiring the robot to be in hard-to-reach locations.

---

## Key Findings and Patterns

### What Actually Solves the UX Problem

1. **Kinematic equivalence** (ALOHA, GELLO, LeRobot leader-follower): Eliminates retargeting confusion. The operator "is" the robot. Lowest cognitive load for arm control. The dominant approach for research data collection.

2. **Stereoscopic immersion** (Open-TeleVision, Telexistence, Sanctuary): Depth perception is THE critical missing piece in most teleop setups. When operators can't perceive depth, everything is harder.

3. **Haptic force feedback** (DOGlove, Shadow + HaptX, CDF-Glove): For contact-rich tasks (cloth, insertion, delicate objects), force feedback is not optional - it's essential. Without it, operators crush things or lose grip.

4. **Shared autonomy** (AI assistance): The most promising scalable direction. Rather than perfecting the human interface, augment the human with AI that handles precision and collision avoidance.

5. **Task-specific robot design** (Hello Robot, Telexistence): Sometimes the answer is not "better teleoperation" but "simpler robot that needs simpler control."

### What Doesn't Work Well

1. **Raw end-effector control** (joysticks, keyboard): Extremely unintuitive. Operators must mentally translate from input space to robot space.

2. **VR hand tracking alone** (without haptics): Precision is insufficient for fine manipulation. Operators overshoot and can't feel contact.

3. **High-DOF control without feedback**: Controlling a 20-DOF hand without haptic feedback is essentially impossible for dexterous tasks.

4. **Remote teleoperation over bad networks**: Even 50ms of additional latency destroys operator performance. Most "remote teleoperation" demos work over LAN.

### The Fundamental Insight

**No one has truly "solved" teleoperation for dexterous manipulation.** The field has converged on a pragmatic approach: make teleoperation *good enough* for data collection, then train AI policies from that data. The winners are not the companies with the best teleoperation interface, but those whose pipeline from teleoperation to autonomy is fastest (ALOHA/ACT, 1X, Astribot).

The real competitive advantage is:
- How few demonstrations do you need? (ACT needs 10-50)
- How quickly can the AI learn from imperfect demos?
- Can shared autonomy make the operator more precise in real-time?

---

## Companies/Projects Worth Watching

| Company/Project | Why | Status |
|----------------|-----|--------|
| ALOHA / ACT (Stanford) | Best-demonstrated pipeline from teleop to autonomy | Open-source, commercialized via Trossen |
| Open-TeleVision | First practical VR teleop for bimanual dexterity | Open-source |
| DOGlove | Open-source haptic glove at $300 | Research prototype, code available |
| GELLO + Force Augmentation | Best affordable leader-follower with feedback | Research, open-source |
| 1X Technologies (NEO) | Only company shipping teleoperation as a product feature | Pre-orders shipping |
| Shadow Robot | Highest-fidelity commercial solution | Available but expensive |
| Shared Autonomy research | Most promising scalable direction | Active research area |
| LeRobot community | Largest open community iterating on teleop UX | Active development |

---

## Implications for Cloth Folding

Cloth folding specifically requires:
- **Bimanual coordination** (both hands must work together)
- **Deformable object handling** (no rigid grasp points)
- **Precise force control** (too much force crumples; too little drops)
- **Visual feedback on deformation state** (did the fold land correctly?)

Best current approach for cloth folding teleoperation:
1. **ALOHA-style leader-follower** for bimanual coordination
2. **Stereoscopic cameras** (Open-TeleVision approach) for depth perception of deformable state
3. **Force-augmented interface** (GELLO + force or DOGlove-style haptics) for grip force control
4. **Shared autonomy** to assist with alignment and fold completion

No single commercial system currently combines all four. The closest is Open-TeleVision running on a bimanual setup with force feedback, which remains a research integration challenge.

---

## Sources

- [ALOHA Project Page](https://tonyzhaozh.github.io/aloha/)
- [Mobile ALOHA](https://mobile-aloha.github.io/)
- [Open-TeleVision Paper (arXiv:2407.01512)](https://arxiv.org/html/2407.01512v2)
- [DOGlove (arXiv:2502.07730)](https://arxiv.org/abs/2502.07730)
- [DOGlove GitHub](https://github.com/TEA-Lab/DOGlove)
- [GELLO + Force Augmentation (arXiv:2507.13602)](https://arxiv.org/html/2507.13602v1)
- [Shadow Robot Teleoperation](https://shadowrobot.com/teleoperation/)
- [Hello Robot Stretch 3](https://hello-robot.com/stretch-3)
- [Sanctuary AI Technology](https://www.sanctuary.ai/technology)
- [1X NEO](https://www.1x.tech/neo)
- [Real-to-Sim-to-Real Shared Autonomy (arXiv:2603.17016)](https://arxiv.org/abs/2603.17016)
- [Shared Control for Tele-Operation Systems (Frontiers)](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2022.915187/full)
- [Skill-Assisted Teleoperation Overview](https://www.emergentmind.com/topics/skill-assisted-teleoperation)
- [LeRobot GitHub](https://github.com/huggingface/lerobot)
- [Telexistence](https://tx-inc.com/)
- [GITAI](https://gitai.tech/)
- [Astribot](https://www.astribot.com/)
