from __future__ import annotations

# Color scheme
BG_DARK = "#1e1e2e"
BG_SIDEBAR = "#181825"
BG_CONTENT = "#1e1e2e"
BG_CARD = "#313244"
BG_TABLE_ROW = "#2a2a3c"

FG_PRIMARY = "#cdd6f4"
FG_SECONDARY = "#a6adc8"
FG_DIM = "#6c7086"

ACCENT = "#89b4fa"
ACCENT_HOVER = "#74c7ec"

# Status dot colors
STATUS_COLORS = {
    "monitoring": "#a6e3a1",  # green
    "attached": "#f9e2af",   # yellow
    "stopped": "#fab387",    # peach
    "detached": "#6c7086",   # gray
}

# Severity colors for event rows
SEVERITY_ROW_COLORS = {
    "INFO": "#cdd6f4",       # white/normal
    "WARNING": "#f9e2af",    # yellow
    "ALERT": "#fab387",      # orange
    "CRITICAL": "#f38ba8",   # red
}

SEVERITY_BG_COLORS = {
    "INFO": "#1e1e2e",
    "WARNING": "#2d2a1e",
    "ALERT": "#2d241e",
    "CRITICAL": "#2d1e1e",
}

# Fonts
FONT_FAMILY = "Helvetica"
FONT_TITLE = (FONT_FAMILY, 16, "bold")
FONT_HEADING = (FONT_FAMILY, 13, "bold")
FONT_BODY = (FONT_FAMILY, 11)
FONT_SMALL = (FONT_FAMILY, 10)
FONT_MONO = ("Menlo", 11)
FONT_BADGE = (FONT_FAMILY, 9, "bold")

# Sidebar
SIDEBAR_WIDTH = 200

# Event table
MAX_EVENT_ROWS = 1000

# Polling intervals (ms)
REGISTRY_POLL_MS = 5000
LOG_POLL_MS = 1000
