#!/bin/bash
# Build macOS .app bundle for Taddle Dashboard
# Usage: bash scripts/build_app.sh

set -euo pipefail

APP_NAME="Taddle Dashboard"
APP_DIR="$HOME/Applications/${APP_NAME}.app"
CONTENTS_DIR="${APP_DIR}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
RESOURCES_DIR="${CONTENTS_DIR}/Resources"

echo "Building ${APP_NAME}.app ..."

# Find Python
PYTHON=$(command -v python3 || command -v python)
if [ -z "$PYTHON" ]; then
    echo "Error: Python not found" >&2
    exit 1
fi

# Create bundle structure
mkdir -p "${MACOS_DIR}"
mkdir -p "${RESOURCES_DIR}"

# Info.plist
cat > "${CONTENTS_DIR}/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Taddle Dashboard</string>
    <key>CFBundleDisplayName</key>
    <string>Taddle Dashboard</string>
    <key>CFBundleIdentifier</key>
    <string>com.taddle.dashboard</string>
    <key>CFBundleVersion</key>
    <string>0.1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>0.1.0</string>
    <key>CFBundleExecutable</key>
    <string>taddle-dashboard</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

# Launcher script
cat > "${MACOS_DIR}/taddle-dashboard" << LAUNCHER
#!/bin/bash
exec "${PYTHON}" -m taddle.dashboard "\$@"
LAUNCHER

chmod +x "${MACOS_DIR}/taddle-dashboard"

echo "Created: ${APP_DIR}"
echo "You can now open '${APP_NAME}' from ~/Applications or Spotlight."
