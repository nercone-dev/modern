from typing import Union
from .color import Color

class Text:
    def __init__(self, content: str = "", forground: Union[str, Color] = "default", background: Union[str, Color] = "default"):
        self.content = content
        self.forground = Color(forground)
        self.background = Color(background, background=True)

    def __add__(self, other: Union[str, "Text"]) -> "Text":
        if isinstance(other, Text):
            if self.forground == other.forground and self.background == other.background:
                return Text(self.content + other.content, self.forground, self.background)
            else:
                return Text(f"{self}{other}")
        elif isinstance(other, str):
            return Text(f"{self}{other}")

    def __str__(self):
        return f"{self.forground}{self.background}{self.content}{Color('reset')}"
