# Teleoperation Hardware Setups: Ranked by Ease & Naturalness

## Quick Reference: Every Setup Ranked

| Rank | System | Cost | Setup Time | Naturalness | Open Source? |
|------|--------|------|------------|-------------|-------------|
| 1 | SO-101 (LeRobot) | ~$110-275/arm pair | 2-4 hours | 6/10 | Yes |
| 2 | Koch v1.1 (LeRobot) | ~$430/arm pair | 2-4 hours | 6/10 | Yes |
| 3 | U-ARM | ~$50-57/leader arm | 1-3 hours | 5/10 | Yes |
| 4 | AlohaMini | ~$500-800 | ~1 hour assembly | 7/10 | Yes |
| 5 | UMI (Stanford) | ~$370/gripper | 3-5 hours | 8/10 | Yes |
| 6 | GELLO | ~$270-300/arm | 30 min + print time | 8/10 | Yes |
| 7 | reBot Arm B601-DM | ~$1,197/pair | 4-8 hours | 7/10 | Yes |
| 8 | Aloha Solo (Trossen) | ~$9,000 | 2-4 hours | 8/10 | Yes |
| 9 | Open-Teach (Quest 3) | ~$500 + robot | 4-8 hours | 7/10 | Yes |
| 10 | Open-TeleVision | ~$500-3,500 + robot | 8-16 hours | 9/10 | Yes |
| 11 | Bunny-VisionPro | ~$3,500 + robot | 8-16 hours | 9/10 | Yes |
| 12 | ALOHA 2 | ~$17,000-32,000 | 1-3 days | 8/10 | Yes |
| 13 | Mobile ALOHA | ~$32,000+ | 3-7 days | 8/10 | Yes |
| 14 | MANUS Gloves + Robot | ~$6,000 + robot | Days-weeks | 9/10 | Commercial |
| 15 | Shadow Robot Teleop | ~$100,000+ | Weeks | 10/10 | Commercial |

---

## Tier 1: Buy Parts, Build in an Afternoon (~$100-$500)

### SO-101 / SO-100 (LeRobot) -- EASIEST ENTRY POINT

The single easiest path into robot teleoperation today.

- **Cost:** ~$110/arm (Seeed Studio kit at $220/pair, 3D-printed parts ~$35 extra) ([Seeed Studio](https://www.seeedstudio.com/SO-ARM101-Low-Cost-AI-Arm-Kit-Pro-p-6427.html))
- **Setup time:** 2-4 hours
- **Skill level:** Beginner -- no soldering, screw-together, video guides
- **Naturalness:** 6/10 -- leader-follower direct mapping, small form factor
- **Works with:** LeRobot (ACT, Diffusion Policy training out of the box)
- **Open source:** Fully -- CAD, firmware, software ([GitHub](https://github.com/TheRobotStudio/SO-ARM100))
- **Where to buy:** [Seeed Studio](https://www.seeedstudio.com/SO-ARM100-Low-Cost-AI-Arm-Kit-Pro-p-6343.html), [PartaBot](https://partabot.com), [WowRobo](https://shop.wowrobo.com/products/so-arm100-diy-kit-assembled-version)
- **Limitation:** 5 DoF + gripper, small workspace, occasional servo drift

### Koch v1.1 (LeRobot)

Better servos, same concept.

- **Cost:** ~$430/pair ($180 leader, $250 follower) ([ROBOTIS](https://www.robotis.us/koch-v1-1-low-cost-robot-arm-leader/))
- **Setup time:** 2-4 hours
- **Naturalness:** 6/10 -- Dynamixel servos are smoother and more reliable
- **Open source:** Fully ([GitHub](https://github.com/jess-moss/koch-v1-1))

### U-ARM -- $50, Cheapest Leader Arm in Existence

- **Cost:** $50.50 for 6-DoF leader arm ([Paper](https://arxiv.org/abs/2509.02437))
- **Naturalness:** 5/10 -- functional but rough
- **Works with:** xArm6, UR5, Trossen ALOHA, Dobot, and more ([GitHub](https://github.com/MINT-SJTU/LeRobot-Anything-U-Arm))
- **Limitation:** Requires you to already own a follower robot arm

---

## Tier 2: A Weekend Project (~$400-$1,500)

### UMI (Universal Manipulation Interface) -- No Robot Needed

You literally pick things up with a handheld gripper. No robot kinematicsn to think about.

- **Cost:** ~$370/gripper ($73 printed parts + $298 GoPro) ([UMI](https://umi-gripper.github.io/))
- **Naturalness:** 8/10 -- closest to natural human motion
- **Key insight:** Decouples data collection from robot hardware. Collect demos anywhere, deploy on robot later.
- **Open source:** Fully ([GitHub](https://github.com/real-stanford/universal_manipulation_interface))
- **Limitation:** Data collection tool, not real-time teleoperation. Parallel-jaw only.

### GELLO -- Kinematic Twin

3D-printed leader arm with exact same joint structure as target robot. You "become" the robot.

- **Cost:** ~$270-300/arm ([Project Page](https://wuphilipp.github.io/gello_site/))
- **Naturalness:** 8/10 -- you feel joint limits and singularities as physical resistance
- **Works with:** Franka Panda, UR5, xArm7
- **Open source:** Fully ([GitHub](https://github.com/wuphilipp/gello_software))
- **Limitation:** Each GELLO is robot-specific. Needs a commercial arm ($5K-$30K).

### AlohaMini -- Bimanual on Wheels

- **Cost:** ~$500-800 DIY ([AlohaMini](https://www.alohamini.com/))
- **Setup:** ~60 minutes assembly, "unboxing to teleop in under 5 minutes" for Pro
- **Naturalness:** 7/10 -- bimanual with motorized lift
- **Open source:** Fully ([GitHub](https://github.com/liyiteng/AlohaMini))

### reBot Arm B601-DM -- New in 2026

- **Cost:** $1,197 complete ([Seeed Studio](https://www.seeedstudio.com/reBot-Arm-B601-DM-Bundle.html))
- **767mm reach, 1.5kg payload, 0.2mm repeatability**
- **LeRobot integration coming late April 2026**

---

## Tier 3: Serious Research (~$3,500-$32,000)

### Aloha Solo (Trossen) -- Closest to Plug-and-Play

- **Cost:** $8,999 ([Trossen](https://www.trossenrobotics.com/aloha-solo))
- **Naturalness:** 8/10 -- most battle-tested imitation learning platform
- **Includes:** Leader + follower + cameras + tripod

### Open-TeleVision -- Immersive VR Stereo

- **Cost:** ~$500-3,500 + robot ([GitHub](https://github.com/OpenTeleVision/TeleVision))
- **Naturalness:** 9/10 -- stereoscopic ego-centric view from robot's head. Camera moves with your head.
- **Key paper:** [arXiv:2407.01512](https://arxiv.org/abs/2407.01512)

### Bunny-VisionPro -- VR + Haptic Feedback

- **Cost:** ~$3,500 + robot ([GitHub](https://github.com/Dingry/BunnyVisionPro))
- **Naturalness:** 9/10 -- Apple hand tracking + low-cost haptic actuators ($1.20 each)
- **11% higher success rate, 45% faster than AnyTeleop+**
- Only open-source VR teleop with haptic feedback

### ALOHA 2 -- Gold Standard for Bimanual

- **Cost:** $17,000-32,000 ([Trossen Kits](https://www.trossenrobotics.com/aloha-kits))
- **Naturalness:** 8/10 -- dual arms, most validated platform
- **ACT was developed here.** Enormous community.

---

## What the Big Companies Use

| Company | Teleop System | Strategy |
|---------|--------------|----------|
| **1X Technologies** | VR headsets + haptic gloves ("Expert Mode") | Customers provide teleop data; AI learns from each intervention |
| **Figure AI** | Undisclosed (500 hours of teleop data) | Trained Helix model (7B params) |
| **Sanctuary AI** | HaptX Gloves for Phoenix humanoid | Teleop data trains Carbon AI |
| **Physical Intelligence** | Teleop + RECAP corrections | pi0 model open-sourced ([GitHub](https://github.com/Physical-Intelligence/openpi)) |

---

## Bottom Line Recommendations

**Absolute easiest:** SO-101 pair (~$275). Teleoperating within an afternoon.

**Best naturalness per dollar:** UMI gripper ($370). Pick things up with your hands. No robot needed.

**Best for an industrial arm:** GELLO ($300 + robot). Outperforms VR and spacemice in every study.

**Best plug-and-play purchase:** Trossen Aloha Solo ($9K). Arrives ready.

**Best immersive experience:** Open-TeleVision + Quest 3 ($500 + robot). Stereo robot eyes.

**The dream setup:** Apple Vision Pro + Bunny-VisionPro + dexterous hand. Best tracking, immersion, haptics, all open source.
