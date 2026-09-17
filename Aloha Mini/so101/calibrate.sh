#!/usr/bin/env bash
# Full lerobot calibration — DESTRUCTIVE, and usually the wrong tool here.
#
# lerobot-calibrate runs set_half_turn_homings(), which OVERWRITES each servo's
# Homing_Offset and Min/Max_Position_Limit. Both of these arms are already
# calibrated in-servo, and the raw-tick path (teleop.py) depends on exactly those
# values — so running this re-zeroes both arms and you have to re-teach the range
# of motion by hand.
#
# To get lerobot calibration JSONs without touching the arms, use instead:
#     ./snapshot.py --install
#
# Run this only if an arm's stored calibration is actually wrong (a servo was
# replaced, a horn was re-seated, the range is visibly off). A backup is written
# to so101/calibration/backup/ first and can be put back with:
#     ./snapshot.py --restore calibration/backup/<role>-<stamp>.json --role <role>
#
#   ./calibrate.sh leader
#   ./calibrate.sh follower
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_env.sh"

ROLE="${1:-}"
case "$ROLE" in
  leader|follower) ;;
  *) echo "usage: $0 leader|follower" >&2; exit 1 ;;
esac

echo
echo "!! This rewrites the ${ROLE}'s in-servo Homing_Offset and position limits."
echo "!! The raw-tick path (teleop.py) is calibrated against the current values."
echo "!! If you only need lerobot's JSON files, press Ctrl-C and run ./snapshot.py --install"
echo
read -r -p "type the word REWRITE to continue: " confirm
[ "$confirm" = "REWRITE" ] || { echo "aborted"; exit 1; }

"$PY" "$HERE/snapshot.py" --backup

if [ "$ROLE" = "leader" ]; then
  exec "$BIN/lerobot-calibrate" \
    --teleop.type="$TELEOP_TYPE" \
    --teleop.port="$LEADER_PORT" \
    --teleop.id="$LEADER_ID" \
    --teleop.arm_profile="$ARM_PROFILE"
else
  exec "$BIN/lerobot-calibrate" \
    --robot.type="$ROBOT_TYPE" \
    --robot.port="$FOLLOWER_PORT" \
    --robot.id="$FOLLOWER_ID" \
    --robot.arm_profile="$ARM_PROFILE"
fi
