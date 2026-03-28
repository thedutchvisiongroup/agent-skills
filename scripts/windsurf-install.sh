#!/usr/bin/env bash
set -euo pipefail

# Determine the repository root (one level above this script's directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_DIR="$REPO_ROOT/skills"
TARGET_DIR="$HOME/.codeium/windsurf/skills"

echo "Windsurf Skills Installer"
echo "  Source: $SOURCE_DIR"
echo "  Target: $TARGET_DIR"
echo ""

# Verify source directory exists
if [[ ! -d "$SOURCE_DIR" ]]; then
    echo "Error: source directory not found: $SOURCE_DIR"
    exit 1
fi

# Create parent directory if it does not exist
PARENT_DIR="$(dirname "$TARGET_DIR")"
if [[ ! -d "$PARENT_DIR" ]]; then
    echo "Creating parent directory: $PARENT_DIR"
    mkdir -p "$PARENT_DIR"
fi

# Clear existing target directory if present
if [[ -L "$TARGET_DIR" ]]; then
    echo "Removing existing symlink at $TARGET_DIR"
    rm "$TARGET_DIR"
elif [[ -d "$TARGET_DIR" ]]; then
    echo "Removing existing directory at $TARGET_DIR"
    rm -rf "$TARGET_DIR"
fi

# Copy skills to target directory
cp -r "$SOURCE_DIR" "$TARGET_DIR"
echo "Done. Skills copied to $TARGET_DIR"
