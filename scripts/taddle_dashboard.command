#!/bin/bash
# Double-clickable fallback: opens Taddle Dashboard in Terminal
# To use: chmod +x scripts/taddle_dashboard.command, then double-click in Finder

cd "$(dirname "$0")/.." || exit 1
python3 -m taddle.dashboard
