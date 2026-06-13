from typing import Union

class Color:
    def __init__(self, color: Union[str, "Color"] = "default", background: bool = False):
        if isinstance(color, str):
            if color.startswith("\033"):
                self.color = color
            elif color.isdecimal():
                self.color = Color.from_code(color).color
            else:
                self.color = Color.from_name(color, background=background).color
        elif isinstance(color, Color):
            self.color = color.color

    def __str__(self):
        return self.color

    def __add__(self, other: Union[str, "Color"]) -> "Color":
        return Color(str(self) + str(other))

    @staticmethod
    def from_code(color_code: int | str = 0) -> "Color":
        return Color(f"\033[{color_code}m")

    @staticmethod
    def from_name(name: str = "default", background: bool = False) -> "Color":
        name = name.strip().lower()
        if name == "reset":
            return Color.from_code(0)
        elif name == "default":
            return Color.from_code(49 if background else 39)
        elif name == "bold":
            return Color.from_code(1)
        elif name == "underline":
            return Color.from_code(4)
        elif not background:
            if name == "black":
                return Color.from_code(30)
            elif name == "red":
                return Color.from_code(31)
            elif name == "green":
                return Color.from_code(32)
            elif name == "yellow":
                return Color.from_code(33)
            elif name == "blue":
                return Color.from_code(34)
            elif name == "magenta":
                return Color.from_code(35)
            elif name == "cyan":
                return Color.from_code(36)
            elif name in ("white", "bright_gray", "light_gray"):
                return Color.from_code(37)
            elif name in ("bright_black", "gray", "grey"):
                return Color.from_code(90)
            elif name == "bright_red":
                return Color.from_code(91)
            elif name == "bright_green":
                return Color.from_code(92)
            elif name == "bright_yellow":
                return Color.from_code(93)
            elif name == "bright_blue":
                return Color.from_code(94)
            elif name == "bright_magenta":
                return Color.from_code(95)
            elif name == "bright_cyan":
                return Color.from_code(96)
            elif name == "bright_white":
                return Color.from_code(97)
            else:
                return Color()
        elif background:
            if name == "black":
                return Color.from_code(40)
            elif name == "red":
                return Color.from_code(41)
            elif name == "green":
                return Color.from_code(42)
            elif name == "yellow":
                return Color.from_code(43)
            elif name == "blue":
                return Color.from_code(44)
            elif name == "magenta":
                return Color.from_code(45)
            elif name == "cyan":
                return Color.from_code(46)
            elif name in ("white", "bright_gray", "bright_grey", "light_gray", "light_grey"):
                return Color.from_code(47)
            elif name in ("bright_black", "gray", "grey"):
                return Color.from_code(100)
            elif name == "bright_red":
                return Color.from_code(101)
            elif name == "bright_green":
                return Color.from_code(102)
            elif name == "bright_yellow":
                return Color.from_code(103)
            elif name == "bright_blue":
                return Color.from_code(104)
            elif name == "bright_magenta":
                return Color.from_code(105)
            elif name == "bright_cyan":
                return Color.from_code(106)
            elif name == "bright_white":
                return Color.from_code(107)
            else:
                return Color()
