import os

if os.name == "nt":
    import ctypes
    ctypes.windll.kernel32.SetConsoleMode(ctypes.windll.kernel32.GetStdHandle(-11), 7)

from .text import Text
from .color import Color
from .logger import Logger, LoggerPart, LogLevel
from .terminal import Terminal, TerminalRegion
from .progressbar import ProgressBar, ProgressBarPart

__all__ = ["Text", "Color", "Logger", "LoggerPart", "LogLevel", "Terminal", "TerminalRegion", "ProgressBar", "ProgressBarPart"]
