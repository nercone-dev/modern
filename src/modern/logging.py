import os
import sys
import tty
import fcntl
import termios
from enum import Enum
from typing import Optional, Union, List
from datetime import datetime, timezone
from strip_ansi import strip_ansi

from .color import Color

last_process = None
last_timestamp = None

max_process_width = 0

class LoggingLevel(Enum):
    DEBUG    = "DEBUG"
    INFO     = "INFO"
    WARNING  = "WARNING"
    ERROR    = "ERROR"
    CRITICAL = "CRITICAL"

    @staticmethod
    def max_width() -> int:
        return max((len(level.value) for level in list(LoggingLevel)))

    def __ge__(a: "LoggingLevel", b: "LoggingLevel") -> bool:
        return list(LoggingLevel).index(a) >= list(LoggingLevel).index(b)

class Logging:
    def __init__(self, process_name: str, primary_color: Union[str, Color] = "cyan", display_level: LoggingLevel = LoggingLevel.INFO, filepath: Optional[Union[str, os.PathLike]] = None, show_process_name: bool = True, show_level: bool = True, show_timestamp: bool = True):
        self.process_name = process_name
        self.primary_color = Color(primary_color)
        self.display_level = display_level
        self.filepath = filepath

        self.show_process_name = show_process_name
        self.show_level = show_level
        self.show_timestamp = show_timestamp

        global max_process_width
        max_process_width = max(max_process_width, len(process_name))

    def log(self, content: str = "", *, level: LoggingLevel = LoggingLevel.INFO):
        global last_process

        if not level >= self.display_level:
            return

        line = self.format(content=content, level=level)
        print(line)

        last_process = self.process_name

        if self.filepath:
            with open(self.filepath, "a") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(f"{strip_ansi(line)}\n")

    def debug(self, content: str = ""):
        self.log(content, level=LoggingLevel.DEBUG)

    def info(self, content: str = ""):
        self.log(content, level=LoggingLevel.INFO)

    def warning(self, content: str = ""):
        self.log(content, level=LoggingLevel.WARNING)

    def error(self, content: str = ""):
        self.log(content, level=LoggingLevel.ERROR)

    def critical(self, content: str = ""):
        self.log(content, level=LoggingLevel.CRITICAL)

    def prompt(self, content: str = "", *, level: LoggingLevel = LoggingLevel.INFO, default: Optional[str] = None, choices: Optional[List[str]] = None, show_choices: bool = True, interrupt_ignore: bool = False, interrupt_default: Optional[str] = None) -> str:
        global last_process

        display_content = content
        if choices and show_choices:
            display_content += f" [{'/'.join(choices)}]"
        if not display_content.endswith(" "):
            display_content += " "

        line = self.format(content=display_content, level=level)

        buffer: List[str] = []

        def render():
            sys.stdout.write("\r\033[K")
            sys.stdout.write(line)
            if not buffer and default is not None:
                sys.stdout.write(f"{Color('gray')}{default}{Color('reset')}")
                if default:
                    sys.stdout.write(f"\033[{len(default)}D")
            else:
                sys.stdout.write("".join(buffer))
            sys.stdout.flush()

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        value = default or ""
        interrupted = False

        try:
            tty.setraw(fd)
            render()

            while True:
                ch = sys.stdin.read(1)

                if ch in ("\r", "\n"):
                    current = "".join(buffer) if buffer else (default or "")

                    if choices:
                        if current in choices:
                            value = current
                            break

                        if current:
                            lower_matches = [c for c in choices if c.lower() == current.lower()]
                            if lower_matches:
                                value = lower_matches[0]
                                break

                        continue

                    value = current
                    break

                elif ch == "\x03":
                    if interrupt_ignore:
                        value = interrupt_default if interrupt_default is not None else (default or "")
                        break
                    interrupted = True
                    break

                elif ch == "\x1b":
                    next_ch = sys.stdin.read(1)
                    if next_ch == "[":
                        sys.stdin.read(1)

                elif ch in ("\x7f", "\x08"):
                    if buffer:
                        buffer.pop()
                        render()

                elif " " <= ch <= "~" or ord(ch) > 127:
                    buffer.append(ch)
                    render()

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        if interrupted:
            sys.stdout.write("\n")
            sys.stdout.flush()
            raise KeyboardInterrupt

        if not content.endswith(" "):
            content += " "
        line = self.format(content=content, level=level)

        sys.stdout.write("\r\033[K")
        sys.stdout.write(f"{line}{value}\n")
        sys.stdout.flush()

        if self.filepath:
            with open(self.filepath, "a") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(f"{strip_ansi(line)}{value}\n")

        last_process = self.process_name

        return value

    def format(self, content: str = "", level: LoggingLevel = LoggingLevel.INFO) -> str:
        global max_process_width, last_process, last_timestamp

        if level == LoggingLevel.DEBUG:
            level_color = Color("gray")
        elif level == LoggingLevel.INFO:
            level_color = Color("blue")
        elif level == LoggingLevel.WARNING:
            level_color = Color("yellow")
        elif level == LoggingLevel.ERROR:
            level_color = Color("red")
        elif level == LoggingLevel.CRITICAL:
            level_color = Color("red", background=True) + Color("white")
        else:
            level_color = Color("gray")

        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        prefix_process_name = f"{self.primary_color}{' ' * max_process_width if self.process_name == last_process else self.process_name.ljust(max_process_width)}{Color('reset')}"
        prefix_level        = f"{level_color}{level.value.ljust(LoggingLevel.max_width())}{Color('reset')}"
        prefix_timestamp    = f"{Color('gray')}{' ' * len(timestamp) if timestamp == last_timestamp else timestamp}{Color('reset')}"
        prefix              = f"{prefix_timestamp + ' ' if self.show_timestamp else ''}{prefix_process_name + ' ' if self.show_process_name else ''}{prefix_level + ' ' if self.show_level else ''}"

        last_timestamp = timestamp

        return prefix + ('\n' + (' ' * len(strip_ansi(prefix)))).join(content.split('\n'))
