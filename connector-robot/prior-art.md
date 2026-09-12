# Prior Art: "Robot-Compatibility Home / OS for the Physical World"

**Created:** May 31, 2026

Scope: prior approaches to the central bet in [the design doc](../../../../.gstack/projects/Robotics/skyler-main-design-20260530-152518.md) — *make the environment legible to simple robots/agents instead of building a robot smart enough for an unstructured world*, plus a universal connector and a self-maintaining control loop.

## Verdict

Yes — heavily. The inversion itself is a named research lineage going back to the late 1990s, and the "structure the world, simplify the robot" bet is already commercially proven in warehouses and one purpose-built office tower. None of the four pillars (inversion, universal connector, shared world model, self-maintenance loop) is new on its own. Where the project can still be original is in the *combination* and the *home* domain — see [What's actually less-trodden](#whats-actually-less-trodden).

## Pillar-by-pillar map

### 1. The inversion: intelligence in the environment, simple robots

- **Intelligent Space (iSpace)** — Hashimoto Lab, University of Tokyo, late 1990s–2000s. "An area (room, public space) that has networked distributed sensors" observing the space; the mobile robot is explicitly the *"physical agent of the Intelligent Space"* — the brains live in the room, the robot is dumb hands ([IntechOpen](https://www.intechopen.com/books/advances-in-human-robot-interaction/human-system-interaction-through-distributed-devices-in-intelligent-space), [ResearchGate — Mobile Robot as Physical Agent of iSpace](https://www.researchgate.net/publication/220066190_Mobile_Robot_as_Physical_Agent_of_Intelligent_Space)). This is the design's core inversion, ~25 years old.
- **Ambient Intelligence (AmI)** — the broader umbrella the above sits inside: environments saturated with sensing/compute that respond to agents.

### 2. The universal connector + an ecology of devices/robots cooperating over a standard interface

- **PEIS-Ecology** (Physically Embedded Intelligent Systems) — Saffiotti et al., Örebro University, ~2004. Tagline "ambient intelligence meets autonomous robotics." Defines *robotic ecologies* = "networks of heterogeneous robotic devices pervasively embedded in everyday environments, where they cooperate to perform tasks," and states the need for "a common communication and cooperation model that allows dynamically assembled ad-hoc networks of robotic devices" — i.e. exactly the universal connector + plug-in ecology ([ResearchGate — PEIS Ecology](https://www.researchgate.net/publication/4246531_PEIS_Ecology_integrating_robots_into_smart_environments), [Springer — Robotic Ubiquitous Cognitive Ecology for Smart Homes, 2015](https://link.springer.com/article/10.1007/s10846-015-0178-2)).
- **Network Robot Systems (NRS) / Ubiquitous Robotics** — EU+Japan research programs, Sanfeliu et al., "ubiquitous networking robotics in urban settings" ([ACM — Network Robot Systems](https://dl.acm.org/doi/10.1016/j.robot.2008.06.007)). Korea pushed the same idea commercially as "ubiquitous robotics / ubibot."
- **Commercial home equivalent today:** the connector standard already exists for *devices* — **Matter** + **Google Home APIs** ("access any Matter or Works-with-Google-Home device," 750M+ devices) ([Google Home Developers](https://developers.home.google.com/apis), [The Verge](https://www.theverge.com/2024/5/15/24157154/google-home-api-matter-smart-home-chromecast-google-tv)). What these lack is the *robot-legible world model + self-maintenance loop* on top.

### 3. The shared, machine-readable world model (the "K" in MAPE-K)

- **RoboEarth** — "A World Wide Web for Robots," EU project ~2011 (ETH Zürich / TUM / Eindhoven). A cloud knowledge base where robots "encode, exchange, and reuse knowledge" in machine-readable form ([IEEE Spectrum](https://spectrum.ieee.org/roboearth-a-world-wide-web-for-robots), [Cloud robotics — Wikipedia](https://en.wikipedia.org/wiki/Cloud_robotics)).
- **3D scene graphs** — Kimera and Hydra, MIT SPARK Lab (Carlone). Real-time layered graph of a space (objects, places, rooms, relations) "used as an aid for planning tasks requiring semantic knowledge" ([Hydra — GitHub](https://github.com/MIT-SPARK/Hydra), [Kimera — SAGE](https://journals.sagepub.com/doi/abs/10.1177/02783649211056674)). This is directly the "scene graph the brain consumes" assumption in the design doc — and the active research front for *producing* such a graph from real sensors, which is the load-bearing perception dependency.

### 4. The self-maintaining loop

- **Autonomic Computing / MAPE-K** — IBM, 2001; Kephart & Chess, "The Vision of Autonomic Computing," 2003. Systems that self-configure, self-heal, self-optimize, self-protect under high-level policy ([Autonomic computing — Wikipedia](https://en.wikipedia.org/wiki/Autonomic_computing), [The Vision of Autonomic Computing — IEEE Computer](https://dl.acm.org/doi/10.1109/mc.2003.1160055)). The design doc already names this correctly; it is a mature, prior-art-rich discipline to mine for loop shape.

## Commercial proof that "structure the world → simplify the robot" works at scale

- **Ocado Smart Platform** — hundreds of simple, near-identical bots on an engineered grid, coordinated by a central computer, developed with digital twins. The environment is engineered precisely so the robots can be dumb and cheap ([Ocado OSRS](https://ocadointelligentautomation.com/systems/robot), [The Verge — inside Ocado](https://www.theverge.com/robot/719880/ocado-online-grocery-automation-krogers-luton-ogrp-robot-grid)).
- **Amazon Robotics (ex-Kiva)** — structured warehouse with fiducial-marked floors; same bet.
- **Naver 1784** — billed as the world's first "robot-friendly building": robot infrastructure designed in from the start, a robot-only elevator ("Roboport"), and a cloud multi-robot brain (ARC) ([Freethink](https://www.freethink.com/robots-ai/1784-naver-labs), [1784 testbed](https://1784.navercorp.com/en/)). This is the closest existing instance of a *clean-sheet, robot-compatible built environment* — just an office tower, not a self-maintaining home.

## What's actually less-trodden

The idea is not new; the *specific fusion* is where any contribution lives:

1. **Self-maintenance as the headline.** iSpace / PEIS / NRS focus on localization, navigation, and task cooperation — not "the home runs itself, self-heals, and auto-restocks" as the central deliverable. Bolting MAPE-K *autonomic* behavior onto the robot-compatibility-home framing is the less-explored seam.
2. **Home (not warehouse/office), clean-sheet, sim-first.** The proven commercial cases are industrial and economically rebuildable. Homes are heterogeneous and legacy-bound — which is exactly why the doc's "clean-sheet is free in simulation" move is the right venue, and exactly the wall real-world deployment hits.
3. **As an embodiment substrate for AI agents.** Framing the legible home as the clean interface that lets a modern LLM/agent act in the physical world is a current angle the 2000s-era work predates.

## Cautionary signal

iSpace and PEIS-Ecology were intellectually influential but did **not** become the dominant commercial home paradigm. The reason isn't that the bet is wrong (warehouses prove it works) — it's that homes are heterogeneous, legacy-bound, and hard to rebuild clean-sheet economically. The pattern wins where someone *owns and controls the whole environment* (a warehouse, a single new building). That is the real lesson for where this could go in the physical world later, and it strengthens the sim-first / clean-sheet choice for v1.

## Worth reading next

- Saffiotti & Broxvall, "PEIS Ecologies: Ambient Intelligence meets Autonomous Robotics" (2005) — the manifesto closest to this design.
- Kephart & Chess, "The Vision of Autonomic Computing" (2003) — the MAPE-K source.
- Hashimoto et al. on Intelligent Space — the inversion, concretely built.
- Hughes/Chang/Carlone, Hydra (2022) — modern robot-legible scene-graph representation.
