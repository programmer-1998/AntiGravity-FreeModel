#!/usr/bin/env bash
# ==============================================================================
# AntiGravity-FreeModel / Auto-Orchestrator Installer
# ==============================================================================
# Links or installs this repository into ~/.gemini/config/plugins/auto-orchestrator
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${HOME}/.gemini/config/plugins/auto-orchestrator"
MODE="symlink"

for arg in "$@"; do
    case "$arg" in
        --copy)
            MODE="copy"
            ;;
        --link|--symlink)
            MODE="symlink"
            ;;
        --help|-h)
            echo "Usage: ./install.sh [--symlink | --copy]"
            echo ""
            echo "Options:"
            echo "  --symlink (default)  Create a symbolic link from $TARGET_DIR to this repo"
            echo "  --copy               Copy files directly into $TARGET_DIR"
            exit 0
            ;;
        *)
            echo "Unknown argument: $arg"
            echo "Run ./install.sh --help for options."
            exit 1
            ;;
    esac
done

echo "=========================================================="
echo " AntiGravity-FreeModel / Auto-Orchestrator Plugin Setup"
echo "=========================================================="
echo "Source: $SCRIPT_DIR"
echo "Target: $TARGET_DIR"
echo "Mode:   $MODE"
echo "----------------------------------------------------------"

# 1. Verify Python 3
if ! command -v python3 &>/dev/null; then
    echo "[-] Error: python3 is not installed or not in PATH."
    exit 1
fi
echo "[+] Python 3 detected: $(python3 --version)"

# 2. Make router script executable
if [ -f "$SCRIPT_DIR/skills/auto-orchestrator/scripts/router.py" ]; then
    chmod +x "$SCRIPT_DIR/skills/auto-orchestrator/scripts/router.py"
    echo "[+] Ensured router.py is executable."
fi

# 3. Create parent directory if needed
mkdir -p "$(dirname "$TARGET_DIR")"

# 4. Handle existing target
if [ -L "$TARGET_DIR" ]; then
    CURRENT_LINK="$(readlink "$TARGET_DIR")"
    if [ "$CURRENT_LINK" = "$SCRIPT_DIR" ] && [ "$MODE" = "symlink" ]; then
        echo "[+] Plugin is already symlinked to this directory."
    else
        echo "[!] Updating existing symlink ($CURRENT_LINK -> $SCRIPT_DIR)..."
        rm -f "$TARGET_DIR"
    fi
elif [ -d "$TARGET_DIR" ]; then
    BACKUP_DIR="${TARGET_DIR}.backup.$(date +%Y%m%d%H%M%S)"
    echo "[!] Existing directory found at $TARGET_DIR. Backing up to $BACKUP_DIR..."
    mv "$TARGET_DIR" "$BACKUP_DIR"
fi

# 5. Perform installation
if [ ! -e "$TARGET_DIR" ]; then
    if [ "$MODE" = "symlink" ]; then
        ln -s "$SCRIPT_DIR" "$TARGET_DIR"
        echo "[+] Successfully created symlink: $TARGET_DIR -> $SCRIPT_DIR"
    else
        cp -r "$SCRIPT_DIR" "$TARGET_DIR"
        echo "[+] Successfully copied plugin to: $TARGET_DIR"
    fi
fi

# 6. Check configuration file
if [ ! -f "$SCRIPT_DIR/config.env" ] && [ ! -f "$TARGET_DIR/config.env" ]; then
    echo "----------------------------------------------------------"
    echo "[!] No config.env detected."
    if [ -f "$SCRIPT_DIR/config.env.example" ]; then
        cp "$SCRIPT_DIR/config.env.example" "$SCRIPT_DIR/config.env"
        echo "[+] Created $SCRIPT_DIR/config.env from config.env.example"
        echo "[*] Please edit '$SCRIPT_DIR/config.env' and add your GROQ_API_KEY and OPENROUTER_API_KEY."
    fi
else
    echo "[+] Configuration file found."
fi

echo "=========================================================="
echo " Installation completed successfully!"
echo " Restart or reload your Antigravity session to apply."
echo "=========================================================="
