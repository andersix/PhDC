# vim: set ts=4 sw=4 sts=4 expandtab ai si ff=unix fileencoding=utf-8 textwidth=79:

from dataclasses import dataclass
from typing import Optional

@dataclass
class ButtonConfig:
    """Configuration settings for a button"""
    pin: int
    function: str
    pull_up: bool = True
    bounce_time: float = 0.05
    hold_time: Optional[float] = None
    hold_repeat: bool = False

