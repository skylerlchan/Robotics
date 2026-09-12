# Product Concept: Teleoperated Home Robot

**Created:** April 16, 2026

---

## Core Concept

A beautiful, minimal home robot that does your chores while you're away. No setup. No learning curve. You leave the house, it works, you come back to a clean home. Pay only for the labor it does.

---

## The Experience

### Unboxing
1. Box arrives at your door
2. Open the lid
3. Download the app, tap "Wake Up"
4. Robot drives itself out of the box onto the floor
5. It finds its own charging spot (against a wall, near an outlet)
6. Done. You never "set it up"

### Daily Use
1. You leave the house (detected via phone GPS / Bluetooth proximity)
2. App notifies: "Home is empty. Want me to tidy up?"
3. You tap "Go" (or it's set to auto)
4. Remote operator connects, sees the camera feed, starts working
5. Robot picks up floor clutter, clears table, sorts laundry into bins, etc.
6. Operator marks tasks complete in their dashboard
7. Robot returns to charger
8. You come home to a tidied space
9. App shows: "Picked up 14 items. Cleared dining table. Sorted darks/lights. $4.20"

### What the User Never Sees
- The teleoperator
- Any setup process
- Any technical interface
- The robot working (it only works when they're gone)
- Charging management (auto-docks)

---

## Why "Only When You're Gone" Is the Key Insight

| Problem | How this solves it |
|---------|-------------------|
| **Privacy / creepiness** | No one is watching you through the camera. Ever. Camera only active during work sessions when house is empty |
| **Robot in the way** | You never see it moving around. It's just sitting on its charger when you're home |
| **Social awkwardness** | No weird feeling of a robot staring at you or following you around |
| **Latency tolerance** | Operator can work at whatever pace they need. No one is watching |
| **Error tolerance** | If it drops something or takes 5 tries, nobody saw it. You just see the result |
| **Magic factor** | You leave a mess, you come back to clean. That's it. Like having an invisible housekeeper |
| **Safety** | No risk of tripping over it, no kids grabbing it, no pets interacting with it while active |

---

## Pricing Model

### Option A: Razor/Blade (Recommended)
- Robot: **$299** (subsidized, below BOM at first)
- Service: **Pay per task** — charged per item picked up, per surface cleared, per load sorted
- Example session: 20 minutes of work = $3-8 depending on tasks
- Typical household: $50-150/month

### Option B: Subscription
- Robot: **$0 upfront** (fully subsidized)
- Monthly: **$99/month** unlimited tidying
- Premium: **$149/month** includes folding, table clearing, dish staging

### Option C: Premium Purchase
- Robot: **$799-999** (full margin)
- Service: **$49/month** flat rate
- Per-task fees for overage

### Why Pay-Per-Task Wins
- Zero commitment barrier — try it with one session
- Scales with actual value delivered (big mess = more tasks = more revenue)
- Users feel fair — only pay for what gets done
- Operators only get paid when working (variable cost, not fixed)
- Aligns incentives: faster/better operators = more tasks/hour = more revenue

---

## Operator Side

### Who operates
- Remote workers globally (Philippines, India, Eastern Europe, Latin America)
- Paid per task completed, not per hour
- Gamified: speed ratings, quality scores, leveling up
- No specialized training needed — if you can use a game controller and see a camera feed, you can do it

### Operator interface
- Video feed from robot cameras
- Game controller (standard Xbox/PS layout)
- Task queue: "Pick up items from living room floor" → "Clear dining table" → "Sort laundry"
- One-tap task completion marking
- Quality verified by before/after photos (automatic)

### Operator economics
- Operator earns: $0.10-0.30 per item picked up
- Speed: ~3-4 items/minute for experienced operators
- Hourly equivalent: $18-72/hour depending on speed and task mix
- Attractive wage in global labor markets

---

## Hardware

### What's in the box
- Wheeled base (smooth, quiet motors)
- Telescoping vertical column (floor to counter height)
- Two chopstick arms (bimanual manipulation)
- Two cameras (wide-angle navigation + close-up gripper)
- Battery (4-6 hour runtime)
- Charging cable (pre-routed in box, robot drives to it)

### What's NOT in the box
- No instruction manual (there are no instructions)
- No remote control (user never drives it)
- No screen on the robot
- No speaker/microphone (no voice assistant, not Alexa)

### Industrial Design
- Matte white or matte black (two SKUs)
- Smooth, seamless shell — no visible screws, no exposed wiring
- Arms tuck flush against body when idle
- Roughly the footprint of a small side table or a Sonos speaker
- When idle on charger, looks like a piece of furniture, not a robot
- Quiet: <40dB during operation (quieter than a dishwasher)

---

## Technical Architecture

### Connectivity
- Bluetooth LE for phone pairing and presence detection
- WiFi for video streaming to operator
- Cellular backup (optional premium) for homes with bad WiFi

### Presence Detection (Is Everyone Gone?)
- Phone GPS geofence (primary)
- Bluetooth proximity (secondary — phone not detected nearby)
- Optional: door sensor integration, smart home API
- Conservative: if unsure, don't start. Never work when someone might be home

### Video Streaming
- WebRTC for low-latency operator video (<150ms target)
- 720p minimum, 1080p preferred
- End-to-end encrypted
- Video NEVER stored on company servers — stream only, no recording
- Before/after snapshots stored locally on device for task verification, auto-deleted after 24 hours

### Privacy Architecture
- Camera hardware kill switch (LED indicates active)
- Camera physically shuttered when not in work session
- No always-on microphone
- No data leaves the home unless work session is active
- User can review operator session logs (timestamps only, no video replay)
- Operator never knows the user's identity or exact address

---

## Data Flywheel (The Hidden Business)

Every teleoperation session generates:
- Observation-action pairs (what the camera sees + what the operator does)
- Task completion trajectories
- Edge case interventions
- Object recognition data across thousands of real homes

This data trains autonomous policies over time:
- **Year 1**: 100% teleoperated, collecting data
- **Year 2**: Robot handles navigation autonomously, operator focuses on manipulation
- **Year 3**: Robot handles simple pick-and-place autonomously, operator handles novel objects
- **Year 4+**: Robot handles 80%+ autonomously, operator supervises and handles edge cases
- **Endgame**: Fully autonomous, operators only needed for rare interventions

As autonomy increases:
- Operator cost per session drops
- Margin per session increases
- Price to user can stay flat or drop (competitive moat)
- Data advantage compounds (more homes = more data = better autonomy = more homes)

---

## Go-To-Market

### Target Customer
- Dual-income households with kids (biggest mess, least time)
- People who already pay for cleaning services ($150-300/month)
- Tech-forward but not technical (Apple customers, not Arduino tinkerers)

### Positioning
"Your home, always tidy. You never lift a finger."

### Launch Sequence
1. **Alpha**: 100 units, hand-selected homes, free service, validate the hardware + operator pipeline
2. **Beta**: 1,000 units, subsidized price, pay-per-task, tune pricing and operator economics
3. **Launch**: 10,000 units, full pricing, target one metro area for operator density

---

## Key Risks

| Risk | Mitigation |
|------|-----------|
| Robot damages something | Start with soft objects only (clothes, toys, paper). Insurance fund from service fees |
| Privacy backlash | Camera shutter, no recording, no audio, work-only-when-gone model |
| Operator quality variance | Before/after photo verification, rating system, task-specific certification |
| WiFi reliability | Cellular backup, graceful disconnect (robot stops and docks if connection drops) |
| Unit economics don't work | Pay-per-task keeps costs variable. Subsidize hardware only when LTV math works |
| Someone comes home mid-session | Bluetooth detection triggers immediate stop. Robot goes to charger. Operator disconnects |
| Pet safety | Pet detection via camera — operator avoids pets, or user marks "pets at home = don't operate" |
