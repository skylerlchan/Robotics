# Sourced by the *.sh wrappers. Resolves the conda env and both arm ports once.
# Bootstrapping note: arms.toml is parsed here with sed, not Python, because the
# system python3 on macOS is 3.9 and has no tomllib — and the 3.12 interpreter we
# want is the very thing this file is looking up.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREFIX="$(sed -n 's/^prefix *= *"\(.*\)".*/\1/p' "$HERE/arms.toml" | head -1)"
PREFIX="${PREFIX/#\~/$HOME}"
PY="$PREFIX/bin/python"
BIN="$PREFIX/bin"

[ -x "$PY" ] || { echo "no python at $PY — check [env].prefix in arms.toml" >&2; exit 1; }

# LEADER_PORT / FOLLOWER_PORT / *_ID / ROBOT_TYPE / TELEOP_TYPE / ARM_PROFILE / FPS
# / REPO_ID / SINGLE_TASK / EPISODE_TIME_S / RESET_TIME_S / NUM_EPISODES / CAMERAS
eval "$("$PY" "$HERE/ports.py" --export)"

echo "[env] python  $PY"
echo "[env] leader   $LEADER_PORT  (id $LEADER_ID)"
echo "[env] follower $FOLLOWER_PORT  (id $FOLLOWER_ID)"
