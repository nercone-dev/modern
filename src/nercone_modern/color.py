class ModernColor:
    @staticmethod
    def ansi_color_by_code(color_code: int | str = 0):
        return f"\033[{color_code}m"

    @staticmethod
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

ModernColor.CYAN = ModernColor.ansi_color("cyan")
ModernColor.MAGENTA = ModernColor.ansi_color("magenta")
ModernColor.YELLOW = ModernColor.ansi_color("yellow")
ModernColor.GREEN = ModernColor.ansi_color("green")
ModernColor.RED = ModernColor.ansi_color("red")
ModernColor.BLUE = ModernColor.ansi_color("blue")
ModernColor.WHITE = ModernColor.ansi_color("white")
ModernColor.BLACK = ModernColor.ansi_color("black")
ModernColor.GRAY = ModernColor.ansi_color("gray")
ModernColor.RESET = ModernColor.ansi_color("reset")
