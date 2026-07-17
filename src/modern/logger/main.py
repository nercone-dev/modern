import os
import sys
from enum import Enum
from typing import Optional, Any, Union, List, Dict
from strip_ansi import strip_ansi

if os.name == "nt":
    import msvcrt
else:
    import tty
    import fcntl
    import termios

from ..color import Color
from ..terminal import Terminal

loggers: List["Logger"] = []

class LogLevel(Enum):
    DEBUG    = "DEBUG"
    INFO     = "INFO"
    WARNING  = "WARNING"
    ERROR    = "ERROR"
    CRITICAL = "CRITICAL"

    def __ge__(a: "LogLevel", b: "LogLevel") -> bool:
        return list(LogLevel).index(a) >= list(LogLevel).index(b)

    def color(self) -> Color:
        if self is LogLevel.DEBUG:
            return Color("gray")
        elif self is LogLevel.INFO:
            return Color("blue")
        elif self is LogLevel.WARNING:
            return Color("yellow")
        elif self is LogLevel.ERROR:
            return Color("red")
        elif self is LogLevel.CRITICAL:
            return Color("red", background=True) + Color("white")
        else:
            return Color("gray")

    @staticmethod
    def max_width() -> int:
        return max((len(level.value) for level in list(LogLevel)))

class LoggerPart:
    def __init__(self):
        pass

    def render(self, logger: "Logger") -> str:
        return "DEFAULT"

    def on_log(self, logger: "Logger"):
        pass

    def on_prompt(self, logger: "Logger"):
        pass

from .parts import TimestampPart, NamePart, LevelPart

class Logger:
    def __init__(self, process_name: str, *, prefix: Optional[List[LoggerPart]] = None, suffix: Optional[List[LoggerPart]] = None, primary_color: Union[str, Color] = "cyan", display_level: LogLevel = LogLevel.INFO, filepath: Optional[Union[str, os.PathLike]] = None):
        global loggers

        self.process_name = process_name
        self.primary_color = Color(primary_color)
        self.display_level = display_level
        self.filepath = filepath

        self.scope: Dict[str, Any] = {}

        self.prefix = prefix or [TimestampPart(), NamePart(), LevelPart()]
        self.suffix = suffix or []

        self.level = display_level
        self.content = ""

        loggers.append(self)

    def log(self, content: str = "", *, level: LogLevel = LogLevel.INFO):
        if not level >= self.display_level:
            return

        for part in self.prefix + self.suffix:
            part.on_log(self)

        line = self.format(content=content, level=level)
        Terminal.write_line(line)

        if self.filepath:
            with open(self.filepath, "a") as f:
                if os.name == "nt":
                    f.seek(0)
                    msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
                    f.seek(0, os.SEEK_END)
                else:
                    fcntl.flock(f, fcntl.LOCK_EX)
                f.write(f"{strip_ansi(line)}\n")

    def debug(self, content: str = ""):
        self.log(content, level=LogLevel.DEBUG)

    def info(self, content: str = ""):
        self.log(content, level=LogLevel.INFO)

    def warning(self, content: str = ""):
        self.log(content, level=LogLevel.WARNING)

    def error(self, content: str = ""):
        self.log(content, level=LogLevel.ERROR)

    def critical(self, content: str = ""):
        self.log(content, level=LogLevel.CRITICAL)

    def prompt(self, content: str = "", *, level: LogLevel = LogLevel.INFO, default: Optional[str] = None, choices: Optional[List[str]] = None, show_choices: bool = True, interrupt_ignore: bool = False, interrupt_default: Optional[str] = None) -> str:
        display_content = content

        if choices and show_choices:
            display_content += f" [{'/'.join(choices)}]"

        if not display_content.endswith(" "):
            display_content += " "

        for part in self.prefix + self.suffix:
            part.on_prompt(self)

        buffer: List[str] = []

        def render():
            stream = Terminal.stream()

            if not buffer and default is not None:
                text = f"{Color('gray')}{default}{Color('reset')}"
            else:
                text = "".join(buffer)

            stream.write("\r\033[K")
            stream.write(self.format(content=display_content + text, level=level, back=True))

            if not buffer and default:
                stream.write(f"\033[{len(default)}D")

            stream.flush()

        if os.name != "nt":
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)

        value = default or ""
        interrupted = False

        try:
            if os.name != "nt":
                tty.setraw(fd)
            render()

            while True:
                ch = msvcrt.getwch() if os.name == "nt" else sys.stdin.read(1)

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

                elif ch == "\x1b" and os.name != "nt":
                    next_ch = sys.stdin.read(1)
                    if next_ch == "[":
                        sys.stdin.read(1)

                elif os.name == "nt" and ch in ("\x00", "\xe0"):
                    msvcrt.getwch()

                elif ch in ("\x7f", "\x08"):
                    if buffer:
                        buffer.pop()
                        render()

                elif " " <= ch <= "~" or ord(ch) > 127:
                    buffer.append(ch)
                    render()

        finally:
            if os.name != "nt":
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        if interrupted:
            Terminal.stream().write("\n")
            Terminal.stream().flush()
            raise KeyboardInterrupt

        if not content.endswith(" "):
            content += " "
        line = self.format(content=content + value, level=level)

        Terminal.stream().write("\r\033[K")
        Terminal.stream().write(f"{line}\n")
        Terminal.stream().flush()

        if self.filepath:
            with open(self.filepath, "a") as f:
                if os.name == "nt":
                    f.seek(0)
                    msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
                    f.seek(0, os.SEEK_END)
                else:
                    fcntl.flock(f, fcntl.LOCK_EX)
                f.write(f"{strip_ansi(line)}\n")

        return value

    def format(self, content: str = "", level: LogLevel = LogLevel.INFO, back: bool = False) -> str:
        global loggers

        self.content = content
        self.level = level

        def columns(attribute: str) -> List[type]:
            result: List[type] = []

            for logger in loggers:
                index = 0
                for part in getattr(logger, attribute):
                    if type(part) in result:
                        index = result.index(type(part)) + 1
                    else:
                        result.insert(index, type(part))
                        index += 1

            return result

        def aligned(attribute: str) -> List[str]:
            result: List[str] = []

            for column in columns(attribute):
                rendered = {logger: other.render(logger) for logger in loggers for other in getattr(logger, attribute) if type(other) is column}

                if not any(strip_ansi(value).strip() for value in rendered.values()):
                    continue

                own = rendered.get(self, "")
                width = max(len(strip_ansi(value)) for value in rendered.values())
                result.append(own + " " * (width - len(strip_ansi(own))))

            return result

        prefix = aligned("prefix")
        suffix = aligned("suffix")

        content = ('\n' + (' ' * len(strip_ansi(" ".join(prefix))))).join(content.split('\n'))
        padding = " " * (Terminal.width() - (len(strip_ansi(" ".join(prefix))) + len(strip_ansi(content.split('\n')[-1])) + len(strip_ansi(" ".join(suffix))) + 3))

        return " ".join(prefix + [content] + ([padding] if suffix else []) + suffix) + (f"\033[{len(strip_ansi(' '.join([padding] + suffix)))}D" if back and suffix else "")
