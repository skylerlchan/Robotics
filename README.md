# Robotics

Working notes, code and experiments behind [Exahuman](https://exahuman.io), the robot
teleoperation lab I founded at the Princeton Robotics Club. The question the lab works on:
how does a remote operator stay in control of a manipulator when the link has latency?

Everything here is in motion. Guides carry dates, and a superseded guide says so at the top.

## What is here

| Folder | What it is |
|---|---|
| `Aloha Mini/` | Bring-up of a four-arm AlohaMini rig on LeRobot SO-101 arms: USB port mapping, calibration, leader/follower teleop, Raspberry Pi 4 setup. Start with `PI4_FULL_TELEOP_GUIDE.md`. |
| `Aloha Mini/so101/` | Scripted control of a follower arm with no leader (`arm.py`), plus probing, port and calibration tools. |
| `putaway/` | A benchmark for one job: put everything back where it lives. Marker-tracked objects and bins, a scorer that counts clean runs in a row. |
| `tendril-sim/` | MuJoCo studies of soft end effectors (the Bloom: an orb that opens into six petals) and task scenes, with generated catalog pages. |
| `personal-robot-concept/` | FORM 01, a Three.js design study of a compact mobile manipulator: stowed footprint, reach envelopes, a door interaction. |
| `connector-robot/` | Concept notes: a home robot as the physical API for every connector. |
| `docs/` | Analyses of Watney-style teleoperation (lag, haptics, mirror effect, physical setup) and a personal-robot engineering thesis. |
| `*_research.md` | Deep-research surveys: teleoperation latency, haptics and embodiment, shared autonomy, VR interfaces, cloth manipulation, ranked hardware, the teleop data landscape. |
| `kindergarden/` | Submodule: Princeton Robot Planning and Learning group's kindergarden. |

## Setup

```bash
git clone --recurse-submodules https://github.com/skylerlchan/Robotics.git
# or, after a plain clone:
git submodule update --init --recursive
```

Hardware work uses a LeRobot conda env; each guide names the interpreter it expects.
`lerobot/` is a local checkout and is not tracked here.
