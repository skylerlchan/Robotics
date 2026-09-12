#!/bin/bash
# AlohaMini Quick Installation Script for macOS

set -e  # Exit on error

echo "=========================================="
echo "AlohaMini Installation Script"
echo "=========================================="
echo ""

# Check if conda is installed
if command -v conda &> /dev/null; then
    echo "✅ Conda is already installed"
else
    echo "📦 Installing Miniforge (Conda)..."
    cd ~/Downloads

    # Detect architecture
    ARCH=$(uname -m)
    if [ "$ARCH" = "arm64" ]; then
        echo "   Detected Apple Silicon (M1/M2/M3)"
        INSTALLER="Miniforge3-MacOSX-arm64.sh"
    else
        echo "   Detected Intel Mac"
        INSTALLER="Miniforge3-MacOSX-x86_64.sh"
    fi

    # Download installer
    echo "   Downloading $INSTALLER..."
    curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/$INSTALLER"

    # Install
    echo "   Installing Miniforge..."
    bash "$INSTALLER" -b -p "$HOME/miniforge3"

    # Initialize
    echo "   Initializing conda..."
    "$HOME/miniforge3/bin/conda" init zsh
    "$HOME/miniforge3/bin/conda" init bash

    # Source the config
    if [ -f "$HOME/.zshrc" ]; then
        source "$HOME/.zshrc"
    fi

    echo "✅ Miniforge installed!"
fi

# Initialize conda for this script
eval "$($HOME/miniforge3/bin/conda shell.bash hook)" || eval "$(conda shell.bash hook)"

# Create environment
echo ""
echo "🐍 Creating Python environment..."
if conda env list | grep -q "^lerobot "; then
    echo "   Environment 'lerobot' already exists"
else
    conda create -y -n lerobot python=3.10
    echo "✅ Environment created!"
fi

# Activate environment
echo ""
echo "🔌 Activating environment..."
conda activate lerobot

# Install dependencies
echo ""
echo "📚 Installing dependencies..."
cd "/Users/skyler/Library/CloudStorage/OneDrive-Personal/Desktop/Current Project/Aloha Mini/lerobot_alohamini"

echo "   Installing lerobot..."
pip install -e .[all]

echo "   Installing additional packages..."
pip install pyzmq
pip install feetech-servo-sdk

echo "   Installing ffmpeg..."
conda install -y ffmpeg=7.1.1 -c conda-forge

echo ""
echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate the environment:"
echo "   conda activate lerobot"
echo ""
echo "2. Identify your arms:"
echo "   python identify_arms.py"
echo ""
echo "3. Follow QUICK_START.md for teleoperation"
echo ""
echo "=========================================="
