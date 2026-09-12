#!/usr/bin/env bash
# AlohaMini host install for Raspberry Pi 4 (64-bit Raspberry Pi OS).
# Run ON THE PI as the normal user (not root):   bash install_pi4.sh
# Idempotent: safe to re-run.
set -euo pipefail

ENV_NAME=lerobot_alohamini
REPO_URL=https://github.com/liyiteng/lerobot_alohamini.git
REPO_DIR="$HOME/lerobot_alohamini"

echo "== [1/6] apt packages"
sudo apt-get update
sudo apt-get install -y git wget curl v4l-utils ffmpeg libgl1 libglib2.0-0 iperf3 htop

echo "== [2/6] serial port permission (dialout group) — needs a reboot/re-login to apply"
sudo usermod -aG dialout "$USER"

echo "== [3/6] Miniforge (ARM64 conda)"
if [ ! -x "$HOME/miniforge3/bin/conda" ]; then
  wget -O /tmp/miniforge.sh \
    https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh
  bash /tmp/miniforge.sh -b -p "$HOME/miniforge3"
  rm -f /tmp/miniforge.sh
  "$HOME/miniforge3/bin/conda" init bash
fi
# shellcheck disable=SC1091
source "$HOME/miniforge3/etc/profile.d/conda.sh"

echo "== [4/6] conda env '$ENV_NAME' (python 3.12 — the repo now requires >=3.12)"
if ! conda env list | grep -qE "^$ENV_NAME\s"; then
  conda create -y -n "$ENV_NAME" python=3.12
fi
conda activate "$ENV_NAME"

echo "== [5/6] clone + install lerobot_alohamini (host needs only lekiwi+hardware extras)"
if [ ! -d "$REPO_DIR/.git" ]; then
  git clone "$REPO_URL" "$REPO_DIR"
fi
cd "$REPO_DIR"
git pull --ff-only || true
# --no-cache-dir keeps RAM/SD usage down on a Pi 4. Torch (CPU, aarch64) is a core dep: ~15-30 min on a Pi 4.
pip install --no-cache-dir -e ".[lekiwi,hardware]"
pip install --no-cache-dir pyzmq feetech-servo-sdk

echo "== [5b] torch import check (Pi 4 = Cortex-A72, no LSE atomics; some torch aarch64 wheels die with 'Illegal instruction')"
if [ -n "${TORCH_SPEC:-}" ]; then
  # e.g.  TORCH_SPEC='torch==2.7.1 torchvision==0.22.1' bash install_pi4.sh
  # shellcheck disable=SC2086
  pip install --no-cache-dir --force-reinstall $TORCH_SPEC
fi
if ! python -c "import torch; print('torch', torch.__version__, 'imports OK')"; then
  cat <<'MSG'
!! torch failed to import. Exit code 132 / 'Illegal instruction' means this wheel uses CPU instructions the Pi 4 lacks
   (pytorch/pytorch#132032, huggingface/lerobot#1738). Re-run with a different pinned CPU build, e.g.:
     TORCH_SPEC='torch==2.7.1 torchvision==0.22.1' bash ~/pi4/install_pi4.sh
   and if that also fails try 2.8.x or 2.9.x.
MSG
  exit 1
fi

echo "== [6/6] sanity check"
python - <<'PY'
import lerobot, zmq, cv2, scservo_sdk, serial
from lerobot.robots.alohamini import AlohaMiniConfig
print("lerobot:", lerobot.__file__)
print("pyzmq:", zmq.__version__, "| opencv:", cv2.__version__)
print("OK — host imports work. robot_model default:", AlohaMiniConfig().robot_model)
PY

cat <<MSG

DONE. Next:
  1. sudo reboot            (applies the dialout group)
  2. Plug in the two Waveshare boards + cameras, then run:  bash ~/pi4/make_udev_rules.sh
  3. conda activate $ENV_NAME && cd ~/lerobot_alohamini
     python -m lerobot.robots.alohamini.alohamini_calibrate --robot_model alohamini1
  4. python -m lerobot.robots.alohamini.alohamini_host --robot_model alohamini1
MSG
