#!/usr/bin/env bash
# Stock lerobot teleoperation for the SO-101 pair — the path that feeds
# lerobot-record and policy training (normalised joint values, not raw ticks).
#
#   ./teleop_lerobot.sh                       # leader -> follower
#   ./teleop_lerobot.sh --display_data=true   # plus a rerun view
#
# Any extra arguments are passed straight through to lerobot-teleoperate.
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_env.sh"

eval "$("$PY" "$HERE/snapshot.py" --print-paths)"
for pair in "leader:$CAL_LEADER" "follower:$CAL_FOLLOWER"; do
  if [ ! -f "${pair#*:}" ]; then
    echo "[calib] missing ${pair%%:*} calibration: ${pair#*:}" >&2
    echo "[calib] run  $HERE/snapshot.py --install  — it reads the calibration the" >&2
    echo "[calib] servos already hold, so nothing on the arms changes." >&2
    exit 1
  fi
done

exec "$BIN/lerobot-teleoperate" \
  --robot.type="$ROBOT_TYPE" \
  --robot.port="$FOLLOWER_PORT" \
  --robot.id="$FOLLOWER_ID" \
  --robot.arm_profile="$ARM_PROFILE" \
  --teleop.type="$TELEOP_TYPE" \
  --teleop.port="$LEADER_PORT" \
  --teleop.id="$LEADER_ID" \
  --teleop.arm_profile="$ARM_PROFILE" \
  --fps="$FPS" \
  "$@"
