from typing import TYPE_CHECKING
from datetime import datetime, timezone

from ..color import Color
from . import main

if TYPE_CHECKING:
    from .main import Logger

class TextPart(main.LoggerPart):
    def __init__(self, text: str, color: Color = Color("default")):
        self.text = text
        self.color = color

    def render(self, logger: "Logger") -> str:
        return str(self.color) + self.text + str(Color("reset"))

class TimestampPart(main.LoggerPart):
    def __init__(self, format: str = "%Y-%m-%dT%H:%M:%SZ", color: Color = Color("gray")):
        self.format = format
        self.color = color

    def render(self, logger: "Logger") -> str:
        return str(self.color) + datetime.now(timezone.utc).strftime(self.format) + str(Color("reset"))

class NamePart(main.LoggerPart):
    def render(self, logger: "Logger") -> str:
        return str(logger.primary_color) + logger.process_name + str(Color("reset"))

class LevelPart(main.LoggerPart):
    def render(self, logger: "Logger") -> str:
        return str(logger.level.color()) + logger.level.value.ljust(main.LogLevel.max_width()) + str(Color("reset"))
