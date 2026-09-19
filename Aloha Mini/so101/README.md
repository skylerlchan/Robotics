# SO-101 teleoperation

Leader → follower teleop for the Aloha Mini SO-101 arm pair, both plugged straight
into this Mac. Two layers over one shared config:

| Layer | Entry point | Uses | Good for |
|---|---|---|---|
| **raw ticks** | `teleop.py` | in-servo calibration only, no files | driving the arm now; lowest latency |
| **scripted** | `arm.py` | in-servo calibration only, no files | commanding the arm from code — no leader, no human |
| **stock lerobot** | `teleop_lerobot.sh`, `record.sh` | lerobot calibration JSONs | recording datasets, training policies |

Ports, tuning and dataset settings all live in **`arms.toml`** — edit there, not in
the code. Both layers resolve ports through `ports.py`, so neither has a hardcoded
`/dev/cu.*` path.

## The arms (identified 2026-09-17)

| Role | USB serial | Device | Bus | Servos |
|---|---|---|---|---|
| leader | `5AA9024340` | `/dev/cu.usbmodem5AA90243401` | 4.9 V (USB) | 1–6 |
| follower | `5AAF262710` | `/dev/cu.usbmodem5AAF2627101` | 12.0 V | 1–6 |

Only IDs 1–6 answer on the follower, so this is a plain SO-101 arm — no mobile
base (8/9/10) and no lift (11). These serials are **not** the four boards recorded
on 2026-09-12; if a board is swapped, update `arms.toml` or let `ports.py`
auto-detect by bus voltage.

Both arms are already calibrated **in the servos** (non-zero `Homing_Offset`,
custom `Min`/`Max_Position_Limit`). That is the whole reason the raw path works
with no files — and the reason not to run `lerobot-calibrate` (see below).

## Everyday use

```bash
cd "Aloha Mini/so101"
PY=~/miniforge3/envs/lerobot_alohamini/bin/python

$PY ports.py            # what's plugged in, and which role each board is
$PY probe.py            # full register dump of every board (never enables torque)
$PY teleop.py --dry-run # show the joint mapping and the soft-start travel, no torque
$PY teleop.py           # drive it
$PY teleop.py --fast    # 100 Hz, higher speed/accel caps
```

Before the first torque-on of a session: **turn the 12 V supply on**. On USB power
alone the follower's servos read ~5 V, cannot hold torque, and the arm slumps to
its hard stop — `teleop.py` refuses to start and prints why. `--wait-for-power`
polls until the supply appears instead of exiting.

## Scripted control (`arm.py`)

`teleop.py` needs a human holding the leader. `arm.py` drives the follower straight
from code, which is what lets a script — or Claude Code — run the robot.

```bash
$PY arm.py status                  # positions + limits + voltage, never torques
$PY arm.py relax                   # torque off, arm goes limp (support it first)
$PY arm.py teach rest              # pose it by hand, save where it is
$PY arm.py pose rest               # go back there
$PY arm.py move elbow_flex=-30 wrist_flex=15
$PY arm.py gripper open|close|40
$PY arm.py home                    # every joint to 0 deg
$PY arm.py play demo.json          # run a sequence
```

Angles are **degrees from centre** (tick 2048 = 0°), matching the SO-101
convention. The gripper is the exception: `0` = closed, `100` = open, mapped onto
whatever range that servo was actually calibrated to.

From Python:

```python
from arm import Arm
with Arm() as a:
    a.move({"shoulder_pan": 20}, secs=2)
    a.gripper(0)
    print(a.read_deg())
```

Two differences from teleop worth knowing:

- **Nothing holds the arm back.** With a leader in the loop a human feels the
  collision; a scripted target just drives into it. `--dry-run` prints the planned
  travel per joint and exits without energising anything — use it on a new move.
- **A move leaves the arm holding its goal.** Torque stays on when the command
  exits, because a limp arm falls. `arm.py relax` is the only thing that releases
  it (or `Arm(release_on_exit=True)` in a `with` block).

Same safety layer as `teleop.py`: under-voltage refusal, capped `Acceleration` and
`Goal_Velocity`, torque enabled one joint at a time with 150 ms gaps, every target
clamped to `arms.toml` **intersected with each servo's own `Min`/`Max_Position_Limit`**,
and all motion interpolated with a per-cycle step clamp so the arm never gets a
step change. Saved poses live in `poses.json`.

## The gripper mapping

The two grippers were calibrated to different ranges — leader `1686–2945`
(span 1259), follower `2024–3559` (span 1535). A plain tick copy would park the
follower at its closed stop, so the gripper uses `mode = "limits"` in `arms.toml`:
the leader's range is mapped linearly onto the follower's. Every other joint is a
direct tick copy, which is what was proven on 2026-09-12.

Any joint can switch to `mode = "limits"`, or take a `flip`, `scale` or `offset`,
without touching the code.

## Safety, unchanged from the proven script

- torque only on follower IDs 1–6, **one joint at a time with 150 ms gaps** — a
  simultaneous torque-on browned out the 12 V supply on 2026-09-12 and rebooted
  every servo
- `Acceleration` and `Goal_Velocity` capped before torque comes on
- soft start ramps from wherever the follower is to the leader pose over 6 s
- per-cycle step clamp, plus per-joint limits intersected with each follower
  servo's own `Min`/`Max_Position_Limit` — the tighter bound always wins
- Ctrl-C or any error disables follower torque before exiting
- auto-reconnect if the boards re-enumerate mid-session

`teleop.py --dry-run` prints the first move each joint would make before anything
is energised. Worth a look when the arms have been moved by hand.

## The stock lerobot path

`lerobot-calibrate` would run `set_half_turn_homings()`, which **overwrites the
in-servo `Homing_Offset` and limits** — re-zeroing both arms and breaking the raw
path. Don't. The same numbers can be read straight out of the servos instead:

```bash
$PY snapshot.py             # show what each arm has stored
$PY snapshot.py --install   # write lerobot's calibration JSONs from the servos
./teleop_lerobot.sh         # leader -> follower through lerobot
./teleop_lerobot.sh --display_data=true
```

`--install` writes exactly what `read_calibration()` reports, so lerobot's
`_is_calibrated()` check passes on connect and **nothing is written to the arms**.
Verified 2026-09-17: both files match the servos.

Files land in:
- `~/.cache/huggingface/lerobot/calibration/teleoperators/so101_leader/am_leader.json`
- `~/.cache/huggingface/lerobot/calibration/robots/so101_follower/am_follower.json`

`snapshot.py --backup` also drops a timestamped copy in `calibration/backup/`,
which `--restore` can write back into the servos if a calibration is ever lost.

`calibrate.sh leader|follower` does run the real destructive calibration — it
takes a backup and makes you type `REWRITE` first. Only for a replaced servo or a
re-seated horn.

## Recording datasets

```bash
./record.sh
./record.sh --dataset.num_episodes=3 --dataset.single_task="fold the cloth"
```

Two things first:

1. **The `dataset` extra is not installed** in `lerobot_alohamini` (it was built
   with `lekiwi,hardware,viz`). `record.sh` detects this and prints the install
   command. It pulls `datasets`/`pyarrow`/`torchcodec`, which can move `torch` —
   worth doing deliberately, not mid-session. `teleop_lerobot.sh` does not need it.
2. **There is no camera configured.** Set `cameras` in `[lerobot.record]` in
   `arms.toml` first; a dataset with no images trains nothing useful.
   `lerobot-find-cameras` lists what's available.

## Files

```
arms.toml            ports, tuning, joint maps, dataset settings — the one config
ports.py             board discovery; serial -> device, voltage -> role   (shared)
probe.py             read-only register dump of every board
snapshot.py          in-servo calibration <-> lerobot JSON (backup/install/restore)
teleop.py            raw-tick teleop (supersedes ../teleop_direct.py)
arm.py               scripted control — move/pose/teach/gripper/play, no leader
poses.json           poses saved by `arm.py teach` (created on first use)
demo.json            example `arm.py play` sequence
_env.sh              shell prelude: resolves the env and both ports once
teleop_lerobot.sh    stock lerobot-teleoperate
record.sh            stock lerobot-record
calibrate.sh         destructive lerobot-calibrate, with guardrails
calibration/backup/  timestamped in-servo calibration snapshots
```

`../teleop_direct.py` is left in place, frozen, as the known-good fallback — it
carries the same safety logic with hardcoded ports and no config file.
