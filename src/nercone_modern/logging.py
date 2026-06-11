import os
import sys
import tty
import fcntl
import termios
from enum import Enum
from strip_ansi import strip_ansi
from datetime import datetime, timezone

from .color import Color

last_process = None
last_level = None

max_prefix_width = 0
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
    def __init__(self, process_name: str, display_level: LoggingLevel = LoggingLevel.INFO, filepath: str | os.PathLike | None = None):
        self.process_name = process_name
        self.display_level = display_level
        self.filepath = filepath

        global max_process_width
        max_process_width = max(max_process_width, len(process_name))

    def log(self, content: str = "", level: LoggingLevel = LoggingLevel.INFO):
        global last_process, last_level

        if not level >= self.display_level:
            return

        line = self.format(content=content, level=level)
        print(line)

        last_process = self.process_name
        last_level = level

        if self.filepath:
            with open(self.filepath, "a") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(f"{strip_ansi(line)}\n")

    def prompt(self, content: str = "", level: LoggingLevel = LoggingLevel.INFO, default: str | None = None, choices: list[str] | None = None, show_choices: bool = True, interrupt_ignore: bool = False, interrupt_default: str | None = None) -> str:
        global last_process, last_level

        original_content = content
        display_content = content
        if choices and show_choices:
            display_content += f" [{'/'.join(choices)}]"
        if not display_content.endswith(" "):
            display_content += " "

        prefix_line = self.format(content=display_content, level=level)
        last_process = self.process_name
        last_level = level

        buffer: list[str] = []

        def render() -> None:
            sys.stdout.write("\r\033[K")
            sys.stdout.write(prefix_line)
            if not buffer and default is not None:
                sys.stdout.write(f"{Color.from_name('gray')}{default}{Color.from_name('reset')}")
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

        final_content = original_content
        if not final_content.endswith(" "):
            final_content += " "
        final_line = self.format(content=final_content, level=level)

        sys.stdout.write("\r\033[K")
        sys.stdout.write(f"{final_line}{value}\n")
        sys.stdout.flush()

        if self.filepath:
            with open(self.filepath, "a") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(f"{strip_ansi(final_line)}{value}\n")

        return value

    def format(self, content: str = "", level: LoggingLevel = LoggingLevel.INFO):
        global max_process_width

        if level == LoggingLevel.DEBUG:
            color = Color.from_name("gray")
        elif level == LoggingLevel.INFO:
            color = Color.from_name("blue")
        elif level == LoggingLevel.WARNING:
            color = Color.from_name("yellow")
        elif level == LoggingLevel.ERROR:
            color = Color.from_name("red")
        elif level == LoggingLevel.CRITICAL:
            color = Color.from_name("red", background=True) + Color.from_name("white")
        else:
            color = Color.from_name("gray")

        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        prefix = f"[{timestamp} {color}{level.value.ljust(LoggingLevel.max_width())}{Color.from_name('reset')} {self.process_name.ljust(max_process_width)}]"

        global max_prefix_width
        max_prefix_width = max(max_prefix_width, len(strip_ansi(prefix)))

        return f"{prefix} {content}"
