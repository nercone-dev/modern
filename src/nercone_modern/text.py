from typing import Union
from .color import Color

class Text:
    def __init__(self, content: str = "", color: str = "white"):
        self.content = content
        if color.startswith("\033"):
            self.color = color
        else:
            self.color = Color.from_name("white")

    def __add__(self, other: Union[str, "Text"]) -> "Text":
        if isinstance(other, Text):
            if self.color == other.color:
                return Text(self.content + other.content, self.color)
            else:
                return Text(f"{self.color}{self.content}{other.color}{other.content}", Color.from_name("reset"))
        elif isinstance(other, str):
            return Text(f"{self.color}{self.content}{other}", Color.from_name("reset"))

    def __str__(self):
        return f"{self.color}{self.content}{Color.from_name('reset')}"
