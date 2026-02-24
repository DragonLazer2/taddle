"""Taddle — Passive Security Monitoring Library."""

from .config import TaddleConfig
from .core import Taddle
from .events import Event, Severity

__version__ = "0.1.0"
__all__ = ["Taddle", "Event", "Severity", "TaddleConfig"]
