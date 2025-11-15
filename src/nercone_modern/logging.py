#!/usr/bin/env python3

# -- nercone-modern --------------------------------------------- #
# logging.py on nercone-modern                                    #
# Made by DiamondGotCat, Licensed under MIT License               #
# Copyright (c) 2025 DiamondGotCat                                #
# ---------------------------------------------- DiamondGotCat -- #

import sys
from .color import ModernColor

ModernLoggingLevels = ["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]
MAX_LOG_LEVEL_WIDTH = max(len(level) for level in ModernLoggingLevels)
LEVEL_ALIASES = {
    "D": "DEBUG",
    "DEBUG": "DEBUG",
    "I": "INFO",
    "INFO": "INFO",
    "INFORMATION": "INFO",
    "W": "WARN",
    "WARN": "WARN",
    "WARNING": "WARN",
    "E": "ERROR",
    "ERROR": "ERROR",
    "C": "CRITICAL",
    "CRITICAL": "CRITICAL"
}

_last_process = None
_last_level = None
_max_proc_width = 0

def normalize_level(level: str) -> str:
    level = level.strip().upper()
    return LEVEL_ALIASES.get(level, level)

def is_higher_priority(level_a: str, level_b: str) -> bool:
    a = normalize_level(level_a)
    b = normalize_level(level_b)
    try:
        return ModernLoggingLevels.index(a) >= ModernLoggingLevels.index(b)
    except ValueError:
        raise ValueError(f"Unknown log level: {level_a} or {level_b}")

class ModernLogging:
    def __init__(self, process_name: str = "App", display_level: str = "INFO", filepath: str | None = None, show_proc: bool | None = None, show_level: bool | None = None):
        self.process_name = process_name
        self.display_level = display_level
        self.filepath = filepath
        self.show_proc = show_proc
        self.show_level = show_level
        global _max_proc_width
        _max_proc_width = max(_max_proc_width, len(process_name))

    def log(self, message: str = "", level_text: str = "INFO", level_color: str | None = None):
        if not is_higher_priority(level_text, self.display_level):
            return
        global _last_process, _last_level
        log_line = self.make(message=message, level_text=level_text, level_color=level_color)
        print(log_line)
        _last_process = self.process_name
        _last_level = normalize_level(level_text.strip().upper())
        if self.filepath:
            with open(self.filepath, "a") as f:
                f.write(f"{log_line}\n")

    def prompt(self, message: str = "", level_text: str = "INFO", level_color: str | None = None, default: str | None = None, show_default: bool = False, choices: list[str] | None = None, show_choices: bool = True, interrupt_ignore: bool = False, interrupt_default: str | None = None) -> str:
        if not is_higher_priority(level_text, self.display_level):
            return
        global _last_process, _last_level
        if default and show_default:
            message += f" ({default})"
        if choices and show_choices:
            message += f" [{'/'.join(choices)}]"
        if not message.endswith(" "):
            message += " "
        log_line = self.make(message=message, level_text=level_text, level_color=level_color)
        print(log_line, end="")
        _last_process = self.process_name
        _last_level = normalize_level(level_text.strip().upper())
        answer = ""
        used_default = False
        try:
            answer = input()
        except KeyboardInterrupt:
            if interrupt_ignore:
                if interrupt_default:
                    answer = interrupt_default
                    used_default = True
                print()
            else:
                raise
        if answer.strip() == "" and default is not None:
            if choices:
                selected_default = self._select_choice(default, choices)
                if selected_default is not None:
                    answer = default
                    used_default = True
            else:
                answer = default
                used_default = True
        if used_default:
            self._rewrite_prompt_line_with_answer(log_line, answer)
        if self.filepath:
            with open(self.filepath, "a") as f:
                f.write(f"{log_line}{answer}\n")
        if choices:
            selected = self._select_choice(answer, choices)
            if selected is not None:
                return selected
            else:
                while True:
                    log_line = self.make(message=f"Invalid selection. Please select from: {'/'.join(choices)}", level_text=level_text, level_color=level_color)
                    print(log_line)
                    if self.filepath:
                        with open(self.filepath, "a") as f:
                            f.write(f"{log_line}{answer}\n")
                    log_line = self.make(message=message, level_text=level_text, level_color=level_color)
                    print(log_line, end="")
                    try:
                        answer = input()
                    except KeyboardInterrupt:
                        if interrupt_ignore:
                            if interrupt_default:
                                answer = interrupt_default
                                used_default = True
                            print()
                        else:
                            raise
                    used_default = False
                    if answer.strip() == "" and default is not None:
                        if choices:
                            selected_default = self._select_choice(default, choices)
                            if selected_default is not None:
                                answer = default
                                used_default = True
                        else:
                            answer = default
                            used_default = True
                    if used_default:
                        self._rewrite_prompt_line_with_answer(log_line, answer)
                    if self.filepath:
                        with open(self.filepath, "a") as f:
                            f.write(f"{log_line}{answer}\n")
                    if answer.strip() == "" and default is not None:
                        if choices:
                            selected_default = self._select_choice(default, choices)
                            if selected_default is not None:
                                return default
                        else:
                            return default
                    selected = self._select_choice(answer, choices)
                    if selected is not None:
                        return selected
        return answer

    def _rewrite_prompt_line_with_answer(self, log_line: str, answer: str) -> None:
        try:
            sys.stdout.write("\033[F\r")
            sys.stdout.write(f"{log_line}{answer}  \n")
            sys.stdout.flush()
        except Exception:
            print(f"{log_line}{answer}")

    def _select_choice(self, answer: str, choices: list[str]) -> str | None:
        if answer in choices:
            return answer
        stripped = answer.strip()
        if stripped in choices:
            return stripped
        lower_map = {c.lower(): c for c in choices}
        if answer.lower() in lower_map:
            return lower_map[answer.lower()]
        if stripped.lower() in lower_map:
            return lower_map[stripped.lower()]
        return None

    def make(self, message: str = "", level_text: str = "INFO", level_color: str | None = None, show_proc: bool | None = None, show_level: bool | None = None):
        level_text = normalize_level(level_text.strip().upper())
        system_show_proc = (self.process_name != _last_process)
        system_show_level = system_show_proc or (level_text != _last_level)

        if not level_color:
            if level_text == "DEBUG":
                level_color = 'gray'
            elif level_text == "INFO":
                level_color = 'blue'
            elif level_text == "WARN":
                level_color = 'yellow'
            elif level_text == "ERROR":
                level_color = 'red'
            elif level_text == "CRITICAL":
                level_color = 'red'
            else:
                level_color = 'blue'

        if show_proc is None:
            if self.show_proc is not None:
                show_proc = self.show_proc
            else:
                show_proc = True

        if show_level is None:
            if self.show_level is not None:
                show_level = self.show_level
            else:
                show_level = True

        return self._make(message=message, level_text=level_text, level_color=level_color, show_proc=show_proc, show_level=show_level, system_show_proc=system_show_proc, system_show_level=system_show_level)

    def _make(self, message: str = "", level_text: str = "INFO", level_color: str = "blue", show_proc: bool = False, show_level: bool = False, system_show_proc: bool = True, system_show_level: bool = True):
        global _max_proc_width
        level_width = max(MAX_LOG_LEVEL_WIDTH, len(level_text))
        color_bar = f"{ModernColor.color(level_color)}|{ModernColor.color('reset')}"

        if not show_proc and not show_level:
            prefix = ""
        else:
            prefix = ""
            if show_proc:
                if system_show_proc:
                    proc_part = self.process_name[:_max_proc_width].ljust(_max_proc_width)
                else:
                    proc_part = " " * _max_proc_width
                prefix += proc_part
                prefix += " "
            else:
                if show_level:
                    prefix += " " * (_max_proc_width + 1)
            if show_level:
                if system_show_level:
                    level_part = level_text.ljust(level_width)
                    level_part = f"{ModernColor.color(level_color)}{level_part}{ModernColor.color('reset')}"
                else:
                    level_part = " " * level_width
                prefix += level_part
                if show_proc:
                    prefix += " " * (_max_proc_width + 1)

        return f"{prefix}{color_bar} {str(message)}"
