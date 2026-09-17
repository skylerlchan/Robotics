#!/usr/bin/env bash
# Record a teleop dataset with the SO-101 pair. Dataset settings live in
# [lerobot.record] in arms.toml; anything here can be overridden on the CLI.
#
#   ./record.sh
#   ./record.sh --dataset.num_episodes=3 --dataset.single_task="fold the cloth"
#
# During recording: right arrow = end episode early, left arrow = redo it,
# ESC = stop the session. Add a camera in arms.toml before recording for real —
# a dataset with no images trains nothing useful.
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_env.sh"

if ! "$PY" -c "import datasets" >/dev/null 2>&1; then
  echo "[deps] lerobot-record needs the 'dataset' extra, which this env does not have." >&2
  echo "[deps] install it with:" >&2
  echo "         cd '$HERE/../lerobot_alohamini' && '$PY' -m pip install -e '.[dataset]'" >&2
  echo "[deps] it pulls datasets/pyarrow/torchcodec — teleop_lerobot.sh works without it." >&2
  exit 1
fi

eval "$("$PY" "$HERE/snapshot.py" --print-paths)"
for pair in "leader:$CAL_LEADER" "follower:$CAL_FOLLOWER"; do
  if [ ! -f "${pair#*:}" ]; then
    echo "[calib] missing ${pair%%:*} calibration: ${pair#*:}" >&2
    echo "[calib] run  $HERE/snapshot.py --install  first." >&2
    exit 1
  fi
done

args=(
  --robot.type="$ROBOT_TYPE"
  --robot.port="$FOLLOWER_PORT"
  --robot.id="$FOLLOWER_ID"
  --robot.arm_profile="$ARM_PROFILE"
  --teleop.type="$TELEOP_TYPE"
  --teleop.port="$LEADER_PORT"
  --teleop.id="$LEADER_ID"
  --teleop.arm_profile="$ARM_PROFILE"
  --dataset.repo_id="$REPO_ID"
  --dataset.single_task="$SINGLE_TASK"
  --dataset.num_episodes="$NUM_EPISODES"
  --dataset.episode_time_s="$EPISODE_TIME_S"
  --dataset.reset_time_s="$RESET_TIME_S"
  --dataset.fps="$FPS"
  --dataset.push_to_hub=false
)
[ -n "$CAMERAS" ] && args+=(--robot.cameras="$CAMERAS")

exec "$BIN/lerobot-record" "${args[@]}" "$@"
