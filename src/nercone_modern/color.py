#!/usr/bin/env python3

# -- nercone-modern --------------------------------------------- #
# color.py on nercone-modern                                      #
# Made by DiamondGotCat, Licensed under MIT License               #
# Copyright (c) 2025 DiamondGotCat                                #
# ---------------------------------------------- DiamondGotCat -- #

from enum import Enum

class ModernColor:
    def from_code(color_code: int | str = 0):
        return f"\033[{color_code}m"

    def from_name(name: str = "default", background: bool = False):
        name = name.strip().lower()
        if name in ("default", "reset"):
            return ModernColor.from_code(0)
        elif name == "bold":
            return ModernColor.from_code(1)
        elif name == "underline":
            return ModernColor.from_code(4)
        elif not background:
            if name == "black":
                return ModernColor.from_code(30)
            elif name == "red":
                return ModernColor.from_code(31)
            elif name == "green":
                return ModernColor.from_code(32)
            elif name == "yellow":
                return ModernColor.from_code(33)
            elif name == "blue":
                return ModernColor.from_code(34)
            elif name == "magenta":
                return ModernColor.from_code(35)
            elif name == "cyan":
                return ModernColor.from_code(36)
            elif name == ("white", "bright_gray", "bright_gray", "light_gray", "light_gray"):
                return ModernColor.from_code(37)
            elif name in ("bright_black", "gray", "grey"):
                return ModernColor.from_code(90)
            elif name == "bright_red":
                return ModernColor.from_code(91)
            elif name == "bright_green":
                return ModernColor.from_code(92)
            elif name == "bright_yellow":
                return ModernColor.from_code(93)
            elif name == "bright_blue":
                return ModernColor.from_code(94)
            elif name == "bright_magenta":
                return ModernColor.from_code(95)
            elif name == "bright_cyan":
                return ModernColor.from_code(96)
            elif name == "bright_white":
                return ModernColor.from_code(97)
            else:
                return ""
        elif background:
            if name == "black":
                return ModernColor.from_code(40)
            elif name == "red":
                return ModernColor.from_code(41)
            elif name == "green":
                return ModernColor.from_code(42)
            elif name == "yellow":
                return ModernColor.from_code(43)
            elif name == "blue":
                return ModernColor.from_code(44)
            elif name == "magenta":
                return ModernColor.from_code(45)
            elif name == "cyan":
                return ModernColor.from_code(46)
            elif name == ("white", "bright_gray", "bright_gray", "light_gray", "light_gray"):
                return ModernColor.from_code(47)
            elif name in ("bright_black", "gray", "grey"):
                return ModernColor.from_code(100)
            elif name == "bright_red":
                return ModernColor.from_code(101)
            elif name == "bright_green":
                return ModernColor.from_code(102)
            elif name == "bright_yellow":
                return ModernColor.from_code(103)
            elif name == "bright_blue":
                return ModernColor.from_code(104)
            elif name == "bright_magenta":
                return ModernColor.from_code(105)
            elif name == "bright_cyan":
                return ModernColor.from_code(106)
            elif name == "bright_white":
                return ModernColor.from_code(107)
            else:
                return ""
