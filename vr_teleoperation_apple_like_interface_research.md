# VR-Based Teleoperation: Designing an "Apple-Like" Interface

*Research compiled April 20, 2026*

---

## The Core Analogy: What Apple Did for Scrolling, We Must Do for Teleoperation

Apple made scrolling feel so natural that users never think about the interface -- they think about the content. The finger-to-screen relationship is 1:1, immediate, and physically intuitive. This is "direct manipulation" in HCI terminology, and it is the gold standard for what teleoperation should feel like.

The goal: **the operator should forget they are operating a robot. They should feel like they ARE the robot.**

---

## 1. The State of VR Teleoperation Systems (2024-2025)

### Open-TeleVision (UC San Diego / MIT, 2024)

The most significant recent open-source contribution to immersive teleoperation. Key insight: **stereoscopic ego-centric vision through a VR headset creates the feeling of inhabiting the robot's body** ([arXiv:2407.01512](https://arxiv.org/abs/2407.01512)).

Architecture:
- VR headset streams operator's hand, head, and wrist poses to the server
- Server retargets human poses to robot joints via inverse kinematics
- Active stereo camera on robot head mimics human head movement
- Real-time ego-centric 3D observations streamed back to VR headset

**Why it matters for "Apple-like" design:**
- The operator sees what the robot sees (ego-centric, stereoscopic)
- Head movement naturally controls camera -- no buttons, no menus
- The system "mirrors the operator's arm and hand movements on the robot, creating an immersive experience as if the operator's mind is transmitted to a robot embodiment"
- Validated on 4 long-horizon tasks across 2 humanoid platforms (Unitree H1, Fourier GR1)

**Critical perception insight:** Static third-person cameras cause occlusion problems and disconnect. First-person active stereo vision that moves with operator head motion is dramatically more intuitive because it matches how humans naturally perceive the world.

### NVIDIA GR00T / Teleop Services

NVIDIA has built teleoperation into its robotics stack, allowing Apple Vision Pro to control humanoid robots. Their approach uses the Vision Pro's hand and head tracking to send commands to humanoid platforms. This represents the "big tech" validation that VR-based teleoperation is the future of data collection for robot learning ([NVIDIA Isaac](https://developer.nvidia.com/isaac)).

### Unitree Embodied Avatar (2025)

Unitree released a full-body teleoperation platform for their humanoid robots, allowing head, arm, and hand tracking through VR to drive the G1 and H1 platforms. Described as enabling operators to have a "full-body avatar" in the robot.

### AnyTeleop (Stanford / UCSD)

A retargeting framework that maps between different human tracking modalities (VR controllers, hand tracking, gloves) and different robot embodiments. Key contribution: **decouples the human interface from the robot hardware**, meaning you can use whatever tracking is most natural and map it to whatever robot you have ([ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0957415824000485)).

### Arm Robot (2024)

An AR-enhanced embodied control system that uses augmented reality to visualize the robot's intended motion overlaid on the real world. Key finding: **"Embodied teleoperation has made robot control intuitive to non-technical users, but differences between humans' and robots' capabilities (ranges of motion, response time) remain challenging"** ([arXiv:2411.13851](https://arxiv.org/abs/2411.13851)).

---

## 2. Hand Tracking: The Controller-Free Paradigm

### Why Controllers Are the Anti-Apple Move

Controllers are training wheels. They add an abstraction layer between intent and action. The Apple analogy: imagine if the iPhone required a stylus to scroll (actually, that was the pre-iPhone PDA era). Apple removed the intermediary.

### Meta Quest Hand Tracking (2024-2025)

Meta's Quest 3 and Quest Pro feature advanced hand tracking that can detect individual finger poses without controllers. Key improvements in 2024-2025:
- Improved precision for fine-grained finger tracking
- Lower latency tracking updates
- Better occlusion handling when fingers overlap

Reddit community response (r/virtualreality, Dec 2025): "Meta's progress on hand tracking is truly the cutting edge, and the Quest's standalone software infrastructure is miles ahead of the competition."

### Apple Vision Pro Hand/Eye Tracking

Vision Pro uses hand and eye tracking as its *primary* input -- no controllers exist. This represents Apple's own bet on what "natural" means:
- Pinch gestures for selection
- Hand movement for spatial interaction
- Eye tracking for targeting
- No controllers, no learning curve for the basics

**Design principle for teleoperation:** If Apple believes hands + eyes are sufficient for all spatial computing interaction, then a teleoperation system should be controllable with hands + eyes + head pose alone.

### The Research Consensus

From the Open-TeleVision paper: Using VR hand tracking (not controllers) for robot teleoperation enables:
- Dexterous multi-finger hand control
- No specialized per-robot hardware needed
- Remote operation without being physically co-located with robot
- Natural grasp and release actions

---

## 3. Direct Manipulation and the Gulfs (HCI Theory Applied to Teleoperation)

### The Foundational Framework

Don Norman, Jim Hollan, and Ed Hutchins established the concept of "direct manipulation interfaces" and two critical gulfs ([Hutchins, Hollan, Norman, 1985](https://www.lri.fr/~mbl/ENS/FONDIHM/2013/papers/Hutchins-HCI-85.pdf)):

**Gulf of Execution:** The distance between the user's goal and the physical actions required to achieve it.

**Gulf of Evaluation:** The distance between the system's actual state and the user's understanding of that state.

### Applying This to Teleoperation

| Gulf | Traditional Teleop Problem | "Apple-Like" Solution |
|------|---------------------------|----------------------|
| Execution | I want the robot to grab the cup, but I must: understand coordinate frames, use a joystick, think about inverse kinematics | I reach out and grab. The robot's hand follows mine 1:1. |
| Evaluation | I can't tell if the robot is gripping tightly enough, I can't see what it sees | I feel haptic resistance when the robot grips. I see through its eyes in stereo 3D. |

### Properties of Direct Manipulation (from HCI literature)

1. **Continuous representation of objects of interest** -- the robot's state is always visible
2. **Physical actions rather than syntax** -- move your hand, don't type commands
3. **Rapid, incremental, reversible operations** -- small moves have small effects, can back up
4. **Immediate visibility of results** -- zero perceptual lag between action and feedback

### The "Invisible Interface" Principle

From Georgia Tech HCI course material: "Effective interfaces can disappear from the user's consciousness, allowing them to focus entirely on their tasks rather than the interface itself" ([Studocu/Georgia Tech](https://www.studocu.com/en-us/document/georgia-institute-of-technology/human-computer-interaction/exploring-direct-manipulation-in-hci-concepts-applications/136974762)).

**This is the Apple design principle distilled.** The iPhone disappears. You don't think "I am using a phone to scroll." You think "I am reading this article." The teleoperation interface must similarly disappear -- the operator should think "I am picking up this cup" not "I am teleopting a robot to pick up a cup."

### Teleoperation's HCI Lineage

"Teleoperation has two parents: direct manipulation in personal computers and process control in complex environments" -- HCI course materials referencing Shneiderman's foundational work.

---

## 4. Workspace Mapping and Kinematic Mismatch

### The Fundamental Problem

Human arms and robot arms are different:
- Different link lengths
- Different joint limits
- Different degrees of freedom
- Different workspace volumes (a human can reach behind their head; many robots cannot)

This is the equivalent of the iPhone's capacitive touchscreen problem: fingers are imprecise, fat, and block what you're touching. Apple solved it with clever algorithms. We must solve kinematic mismatch with clever retargeting.

### Research on Kinematic Mapping Methods

From [ScienceDirect 2024](https://www.sciencedirect.com/science/article/abs/pii/S0957415824000485): "A kinematic mapping method maps the end-effector motion of the human arm to the robotic arm according to scale and then adjusts the elbow rotation angle according to the mapping information to improve the similarity of arm posture."

Key approaches:
1. **End-effector mapping** -- only map where the hand goes, let the robot figure out joint angles via IK
2. **Joint-angle mapping** -- copy human joint angles to robot (requires similar kinematics)
3. **Hybrid approaches** -- map end-effector position + constrain elbow/shoulder orientation

### Scaling Strategies

- **1:1 mapping** -- human moves 10cm, robot moves 10cm (most natural but workspace-limited)
- **Scaled mapping** -- human moves 10cm, robot moves 30cm (useful for large workspaces but less intuitive)
- **Clutch-based remapping** -- press button to "pick up" control, reposition, "put down" (like lifting a mouse off a mousepad)
- **Workspace warping** -- non-linear mapping that gives 1:1 near the center and compressed at edges

**Apple-like insight:** iPhone scrolling is NOT 1:1. It has momentum, rubber-banding, and adaptive speed. The key is not literal 1:1 mapping -- it's that the mapping **feels** natural. Teleoperation should similarly use intelligent non-linear mappings that feel right even when they aren't geometrically exact.

### The ArmRobot Solution (2024)

"To make the mapping between humans and robots more intuitive, we embodied the robot gripper with the user's hand." -- using AR overlay to show where the robot gripper IS relative to where the user's hand IS, so the user can intuitively correct for any mismatch.

---

## 5. The Embodiment and Presence Problem

### What Makes Teleoperation Feel "Real"

Research on haptic feedback and presence identifies key factors for feeling "inside" the robot:

**Kinesthetic Feedback (Force Feedback):**
- If the robot hits something, the operator's hand physically resists
- Creates the sensation of touching real objects
- Hardware: Haption Virtuose 6D, Force Dimension Omega provide multi-axis force reflection
- ([IEEE](https://ieeexplore.ieee.org/document/10363664/), [Nature](https://www.nature.com/articles/s41598-023-38201-x))

**Cutaneous Feedback (Tactile Cues):**
- Vibrations, temperature, skin stretch
- Lighter-weight than force feedback
- Can be integrated into gloves worn during VR

**The Jitter Problem:** When feedback latency causes over-correction, creating oscillation that breaks immersion. This is equivalent to iOS scroll judder -- Apple invested enormously in 60fps+ rendering to prevent exactly this.

### Sense of Embodiment (SoE) Research

Three components that create the feeling of "being" the robot:
1. **Self-location** -- feeling physically present at the robot's location
2. **Agency** -- feeling that YOU are causing the robot's movements
3. **Body ownership** -- feeling that the robot's body IS your body

VR with stereoscopic vision + hand tracking maximizes all three. This is why Open-TeleVision's approach works: you see through the robot's eyes (self-location), your movements cause its movements (agency), and its hands move like yours (body ownership).

---

## 6. Low-Latency Streaming and Its Effect on Performance

### The Latency Thresholds

Research establishes critical latency boundaries for teleoperation:

| Latency | Effect |
|---------|--------|
| <50ms | Feels real-time; operator performs naturally |
| 50-150ms | Noticeable but workable; operators slow down slightly |
| 150-300ms | Significant performance degradation; move-and-wait strategy emerges |
| >300ms | Task failure rates spike; operators develop unnatural compensating behaviors |
| >1000ms | Teleoperation becomes essentially "move, wait, observe, move" |

**Apple parallel:** iOS touch response is <16ms (60fps). Apple pioneered predictive touch to make input feel instantaneous. For teleoperation, the equivalent investment is in:
- Low-latency video encoding (H.265 hardware encode)
- Predictive motion (the robot starts moving before the full command arrives)
- Visual prediction (render predicted robot state while waiting for confirmation)

### Reddit Discussion on Teleoperation Latency (r/singularity, 2024)

"Impressive latency and speed of teleoperation achieved" -- discussion of systems achieving sub-100ms round-trip, which enables the feeling of "real-time" control even over network connections.

### Digital Twins for Latency Masking

Reddit discussion (r/robotics, Oct 2025): Challenge of keeping a robot and its digital twin in accurate sync. The digital twin can:
- Show predicted robot state immediately (no latency)
- Highlight when actual state deviates from predicted
- Allow the operator to "plan" moves while the real robot catches up

---

## 7. Camera Views: First-Person vs. Third-Person

### The Research Question

Should the operator see from the robot's eyes (first-person/ego-centric) or from an external camera watching the robot (third-person)?

### First-Person Advantages
- Maximum immersion and presence
- Natural head movement controls camera
- Enables fine-grained close-up manipulation
- Aligns with how humans naturally perform tasks
- Best for policy learning (agent sees what operator saw)

### First-Person Disadvantages
- Can cause motion sickness if latency is high
- No awareness of robot's overall body position
- Occlusion by robot's own hands
- Limited peripheral awareness

### Third-Person Advantages
- Better spatial awareness
- Can see obstacles approaching from sides
- Easier for novice operators initially
- Less motion sickness

### Third-Person Disadvantages
- Mental rotation required (mapping "left on screen" to "robot's left")
- Less precise for manipulation
- Operator cannot freely look around
- Not how humans normally perform tasks

### The Hybrid Solution (Open-TeleVision's Insight)

**Active ego-centric stereo vision** -- first-person view that the operator controls with head movement. This gives:
- First-person immersion and precision
- Ability to "look around" for spatial awareness
- Natural attention mechanism (look at what you're working on)
- Stereo depth for manipulation

---

## 8. Gaming/VR UX Principles Applied to Teleoperation

### Flow State Design

From game design research, "flow" occurs when:
- Challenge matches skill level
- Clear goals exist
- Immediate feedback is provided
- Sense of control is maintained
- Self-consciousness disappears (the interface disappears)

**Teleoperation application:**
- Gradually increase task difficulty as operators improve
- Provide clear visual targets (AR overlays of where to place objects)
- Zero-latency visual feedback
- Precise, predictable control response
- The VR headset makes the outside world disappear -- operator IS the robot

### Affordances from VR Game Design

| VR Game Principle | Teleoperation Application |
|-------------------|--------------------------|
| Haptic "clicks" for confirming actions | Vibration pulse when gripper makes contact |
| Visual highlights on interactable objects | AR highlight objects that robot should grasp |
| Adaptive difficulty | Auto-assist for novice operators, raw control for experts |
| Tutorial levels | Progressive tasks: reach > grasp > lift > place > stack |
| Spatial audio | Auditory feedback from robot sensors (grinding = too much force) |
| Comfort vignetting | Darken periphery during fast robot movement to prevent nausea |
| Snap-to-grid / magnetism | Slight position assistance near target locations |

### Gamification for Engagement

For data collection at scale, operators need to enjoy the experience:
- Score/speed metrics create competitive motivation
- Progress bars and task completion tracking
- "Combo" scoring for smooth, efficient demonstrations
- Leaderboards across data collectors
- Sound design that makes manipulation satisfying

---

## 9. Open-Source Teleoperation Systems Landscape

### ALOHA / Mobile ALOHA (Stanford, 2023-2024)

- **Approach:** Physical leader-follower arm pairs ($20k total budget)
- **Key insight:** Direct kinematic mirroring -- you move a physical arm, the robot arm copies
- **Strengths:** High-bandwidth, zero latency, very precise
- **Weakness:** Must be physically co-located; single-purpose hardware
- **Apple analogy:** This is like the MacBook trackpad -- mechanical, precise, but physically attached
- ([ALOHA Project Page](https://tonyzhaozh.github.io/aloha/))

### GELLO (2024)

- **Approach:** 3D-printed leader arm that matches robot kinematics
- **Key insight:** Joint-angle copying with matched geometry
- **Strengths:** Cheap to build, direct tactile feedback through the leader arm
- **Weakness:** Custom per-robot, must be co-located

### Open-TeleVision (2024)

- **Approach:** VR headset + hand tracking + stereoscopic robot head camera
- **Key insight:** Immersive perception is as important as action mapping
- **Strengths:** Remote operation, natural hand control, scales to different robots
- **Weakness:** Requires VR headset, latency-dependent, no force feedback
- ([GitHub: robot-tv.github.io](https://robot-tv.github.io/))

### Bunny-VisionPro (2024)

- **Approach:** Apple Vision Pro hand tracking mapped to bimanual robot arms
- **Key insight:** Leveraging Apple's best-in-class hand tracking for teleoperation
- **Strengths:** Highest quality hand tracking available, no controllers needed
- **Weakness:** Expensive headset ($3,500), Apple ecosystem lock-in

### TeleMoMa (2024)

- **Approach:** Modular teleoperation for mobile manipulators
- **Key insight:** Unifies multiple human interfaces (cameras, VR controllers, keyboard, joystick)
- **Strengths:** Flexibility, works with any combination of inputs
- **Weakness:** Complexity of configuration

### MoMa-Teleop

- **Approach:** Delegates base motion to RL agent, operator only controls end-effector
- **Key insight:** Don't make the human control what AI can handle
- **Strengths:** Reduces cognitive load -- operator focuses only on manipulation
- **Weakness:** Requires pre-trained navigation policy

### MART (Multi-user)

- **Approach:** Multiple remote users simultaneously control multiple arms
- **Key insight:** Parallelizes data collection across multiple operators
- **Strengths:** Scalable data collection
- **Weakness:** Coordination challenges

---

## 10. Design Principles for "Apple-Like" Teleoperation

Drawing from all the research above, here are the principles that would make teleoperation feel as natural as using an iPhone:

### Principle 1: The Interface Must Disappear

Like the iPhone's glass -- you touch the content, not the device. In teleoperation:
- No buttons to press to "activate" control
- No mode switches between "looking" and "acting"
- The VR headset disappears from consciousness
- You ARE the robot; you don't CONTROL the robot

### Principle 2: 1:1 Spatial Mapping (or Feels Like It)

iPhone scrolling is actually non-linear (momentum, rubber-banding), but it FEELS 1:1. For teleoperation:
- Hand movements map spatially to robot hand movements
- Head movements map to robot head/camera movement
- Add intelligent scaling/damping that preserves the FEELING of directness
- Use predictive rendering to mask any latency

### Principle 3: Ego-Centric Stereoscopic Vision

You see through the robot's eyes, in 3D, with active head control. This is non-negotiable for presence:
- Stereo RGB from robot head cameras
- Head-tracked camera that follows operator gaze
- Low-latency streaming (<50ms ideal, <100ms acceptable)
- Resolution sufficient to see fine manipulation details

### Principle 4: Progressive Disclosure of Complexity

iPhone: basic features are obvious; advanced features are hidden but discoverable. For teleoperation:
- First time: just move your hands and the robot moves
- Over time: unlock precision modes, force scaling, workspace expansion
- Expert mode: raw unfiltered control, custom mappings
- Never force beginners through a training manual

### Principle 5: Graceful Degradation

iPhone still works if GPS is off, if bluetooth disconnects. For teleoperation:
- If latency spikes, switch to digital twin preview mode
- If hand tracking is lost momentarily, robot holds position (doesn't flail)
- If one arm disconnects, other arm still works
- Safety stops feel smooth, not jarring

### Principle 6: Sensory Feedback at Every Scale

iPhone: every touch produces a visual change and a haptic tap. For teleoperation:
- Visual: robot state always visible in real-time
- Audio: contact sounds, motor sounds, spatial audio
- Haptic: vibration for contact, resistance for force (if hardware supports it)
- Every action produces immediate, proportional feedback

### Principle 7: Error Prevention Over Error Correction

iPhone: it's hard to accidentally delete important things; undo is always available. For teleoperation:
- Soft limits prevent joint damage
- Collision prediction shows "ghost" of impending collision
- Speed limiting near obstacles
- One-button emergency stop + one-button resume from last position

### Principle 8: Delegate to AI What Humans Shouldn't Manage

iPhone: autocorrect, auto-brightness, auto-focus. For teleoperation:
- AI handles base navigation (operator just points "go there")
- AI handles grasp stability (operator initiates grasp, AI maintains force)
- AI handles collision avoidance (operator moves freely, robot routes around obstacles)
- AI handles repetitive sub-tasks (operator does it once, AI repeats)

### Principle 9: Instant On, Zero Configuration

iPhone: press button, it works. No BIOS, no login sequence. For teleoperation:
- Put on headset, see through robot's eyes immediately
- Move hands, robot moves
- No calibration step, no "connect" button, no coordinate frame alignment
- Auto-detect which robot, auto-load appropriate retargeting

### Principle 10: The Task, Not the Tool

iPhone: you think "I'll check my email" not "I'll open the Mail application and navigate to the inbox." For teleoperation:
- Operator thinks "pick up that cup" not "activate right arm, open gripper, move to position X,Y,Z, close gripper, verify force..."
- The system handles the HOW, the human provides the WHAT
- Intent-level control where possible, joint-level where needed

---

## 11. The Path Forward: Technical Architecture

Based on this research, the optimal "Apple-like" teleoperation system would combine:

### Hardware
- **Headset:** Meta Quest 3/Pro (cost-effective, best standalone hand tracking) or Apple Vision Pro (best hand/eye tracking, premium)
- **Robot:** Any arm with a wrist-mounted or head-mounted stereo camera pair
- **Audio:** Spatial audio from robot microphones
- **Haptic:** Wrist haptic bands for basic contact feedback (future: full hand haptic gloves)

### Software Stack
1. **Hand/Head tracking** -- from VR SDK (50Hz+)
2. **Retargeting** -- IK-based end-effector mapping with elbow constraint
3. **Video pipeline** -- Hardware H.265 encode on robot, WebRTC stream to headset (<50ms)
4. **Digital twin** -- Predictive robot state rendered in VR while waiting for real frame
5. **AI co-pilot** -- Collision avoidance, grasp assistance, navigation autonomy
6. **Data recording** -- Simultaneous capture of all modalities for imitation learning

### The "Day One" Experience
1. User puts on VR headset
2. Sees the robot's perspective in stereo 3D
3. Moves hands -- robot hands move
4. Turns head -- robot camera turns
5. Reaches for object -- robot reaches
6. Grasps -- feels vibration confirmation
7. Lifts and places -- task complete
8. Total training time: zero

---

## 12. Key Open Questions and Challenges

1. **Can we achieve <50ms glass-to-glass latency over WiFi?** This is the make-or-break for presence.

2. **How do we handle the workspace mismatch?** Human workspace is larger than most robot arms. Clutching feels unnatural. Workspace warping introduces non-linearity.

3. **Is force feedback necessary for the "Apple" feeling?** Or is visual + audio + vibration sufficient? (Apple's Taptic Engine proved that clever haptics beat brute force feedback.)

4. **How to handle robot safety?** The more "invisible" the interface, the less the operator thinks about the robot as a physical machine that can break things.

5. **Scaling data collection:** Can we make this fun enough that people WANT to teleoperate, enabling crowd-sourced data collection?

6. **Sim-to-real gap in the experience:** Can operators train in simulation and transfer skills to real robots without re-learning?

---

## Sources

- [Open-TeleVision: Teleoperation with Immersive Active Visual Feedback](https://arxiv.org/abs/2407.01512) -- Cheng et al., UC San Diego/MIT, 2024
- [Direct Manipulation Interfaces](https://www.lri.fr/~mbl/ENS/FONDIHM/2013/papers/Hutchins-HCI-85.pdf) -- Hutchins, Hollan, Norman, 1985
- [Gulf of Evaluation and Gulf of Execution](https://www.interaction-design.org/literature/book/the-glossary-of-human-computer-interaction/gulf-of-evaluation-and-gulf-of-execution) -- Interaction Design Foundation
- [Human-robot kinematic mapping method based on index constraint](https://www.sciencedirect.com/science/article/abs/pii/S0957415824000485) -- ScienceDirect, 2024
- [Arm Robot: AR-Enhanced Embodied Control and Visualization for Intuitive Robot Arm Manipulation](https://arxiv.org/abs/2411.13851) -- Pei et al., 2024
- [Haptic Feedback in Robotic Teleoperation: A Complete Guide](https://roboticsmeta.com/haptic-feedback-in-robotic-teleoperation-a-complete-guide/) -- RoboticsMeta
- [Towards the development of an intuitive teleoperation system for human support robot using a VR device](https://www.tandfonline.com/doi/full/10.1080/01691864.2020.1813623) -- Nakanishi et al., Advanced Robotics, 2020
- [ALOHA: A Low-cost Open-source Hardware System for Bimanual Teleoperation](https://tonyzhaozh.github.io/aloha/) -- Zhao et al., Stanford
- [Mobile ALOHA: Learning Bimanual Mobile Manipulation with Low-Cost Whole-Body Teleoperation](https://mobile-aloha.github.io/resources/mobile-aloha.pdf) -- Fu et al., 2024
- [Tool-as-Interface: Learning Robot Policies from Observing Human Tool Use](https://arxiv.org/abs/2504.04612) -- Chen et al., 2025
- [Interactive imitation learning for dexterous robotic manipulation](https://pmc.ncbi.nlm.nih.gov/articles/PMC12757213/) -- PMC/NIH, 2025
- [Building a data acquisition pipeline via teleoperation with NVIDIA Isaac Sim](https://www.x-humanoid.com/news-view-158.html) -- X-Humanoid, 2025
- [Training Robots with LeRobot: Teleoperation and AI for Pick-and-Place Tasks](https://techlabs-aachen.medium.com/training-robots-with-lerobot-teleoperation-and-ai-for-pick-and-place-tasks-d8a16a219af5) -- TechLabs Aachen, 2025
- [DATA SCALING LAWS IN IMITATION LEARNING FOR ROBOTIC MANIPULATION](https://proceedings.iclr.cc/paper_files/paper/2025/file/88b7b2c896506daabc8d3fd587055167-Paper-Conference.pdf) -- ICLR 2025
- [RoboCopilot: Human-in-the-loop Interactive Imitation Learning](https://arxiv.org/html/2503.07771v1) -- 2025
- [Learning more about direct manipulation and reducing the 'gulfs'](https://marcabraham.com/2014/02/20/learning-more-about-direct-manipulation-and-reducing-the-gulfs/) -- Marc Abraham
- [Exploring Direct Manipulation in HCI: Concepts and Applications](https://www.studocu.com/en-us/document/georgia-institute-of-technology/human-computer-interaction/exploring-direct-manipulation-in-hci-concepts-applications/136974762) -- Georgia Tech HCI
