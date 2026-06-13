from typing import Union
from .color import Color

class Text:
    def __init__(self, content: str = "", forground_color: str | Color = "default", background_color: str | Color = "default"):
        self.content = content
        self.forground_color = Color(forground_color)
        self.background_color = Color(background_color, background=True)

    def __add__(self, other: Union[str, "Text"]) -> "Text":
        if isinstance(other, Text):
            if self.forground_color == other.forground_color and self.background_color == other.background_color:
                return Text(self.content + other.content, self.forground_color, self.background_color)
            else:
                return Text(f"{self}{other}")
        elif isinstance(other, str):
            return Text(f"{self}{other}")

    def __str__(self):
        return f"{self.forground_color}{self.background_color}{self.content}{Color('reset')}"
