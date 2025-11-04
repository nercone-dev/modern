class ModernColor:
    def ansi_color(self, color_name: str = "reset"):
        if color_name == "cyan":
            return self.ansi_color_by_code(36)
        elif color_name == "magenta":
            return self.ansi_color_by_code(35)
        elif color_name == "yellow":
            return self.ansi_color_by_code(33)
        elif color_name == "green":
            return self.ansi_color_by_code(32)
        elif color_name == "red":
            return self.ansi_color_by_code(31)
        elif color_name == "blue":
            return self.ansi_color_by_code(34)
        elif color_name == "white":
            return self.ansi_color_by_code(37)
        elif color_name == "black":
            return self.ansi_color_by_code(30)
        elif color_name in ("gray", "grey"):
            return self.ansi_color_by_code(90)
        elif color_name == "reset":
            return self.ansi_color_by_code(0)
        else:
            return ""

    def ansi_color_by_code(self, color_code: int | str = 0):
        return f"\033[{color_code}m"

    CYAN = ansi_color("cyan")
    MAGENTA = ansi_color("magenta")
    YELLOW = ansi_color("yellow")
    GREEN = ansi_color("green")
    RED = ansi_color("red")
    BLUE = ansi_color("blue")
    WHITE = ansi_color("white")
    BLACK = ansi_color("black")
    GRAY = ansi_color("gray")
    RESET = ansi_color("reset")
