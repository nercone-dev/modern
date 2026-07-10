from typing import Optional, Union, List
from strip_ansi import strip_ansi

from .color import Color
from .terminal import Terminal, TerminalRegion

progress_bars: List["ProgressBar"] = []
max_total_width = 0

class ProgressBar(TerminalRegion):
    def __init__(self, name: str, total: int, current: int = 0, start: bool = True, bar_length: Optional[int] = None, primary_bar: str = "━", secondary_bar: str = "━", primary_color: Union[str, Color] = "blue", secondary_color: Union[str, Color] = "grey"):
        self.name = name
        self.total = total
        self.current = current
        self.bar_length = bar_length
        self.primary_bar = primary_bar
        self.secondary_bar = secondary_bar
        self.primary_color = Color(primary_color)
        self.secondary_color = Color(secondary_color)

        self.active = False
        self.step = 0
        self.message = ""

        global max_total_width
        max_total_width = max(max_total_width, len(str(total)))

        if start:
            self.start()

    def set_message(self, message: str = ""):
        self.message = message
        Terminal.redraw(self)

    def start(self):
        global progress_bars
        if self.active:
            return
        self.active = True
        progress_bars.append(self)
        Terminal.attach(self)

    def update(self, amount: int = 1):
        self.current += amount
        if self.current > self.total:
            self.current = self.total
        Terminal.redraw(self)

    def finish(self):
        self.active = False
        self.current = self.total
        Terminal.redraw()

    def render(self) -> str:
        suffix = self.suffix()
        bar = self.bar(self.bar_length or (Terminal.width() - len(strip_ansi(suffix)) - 1))
        return f"{bar} {suffix}{Color('reset')}"

    def bar(self, length: int):
        filled_length = int(length * (self.current / self.total))
        return f"{self.primary_color}{self.primary_bar * filled_length}{self.secondary_color}{self.secondary_bar * (length - filled_length)}{Color('reset')}"

    def suffix(self):
        global progress_bars

        def build_parts(bar: ProgressBar) -> List[str]:
            return [
                f"{bar.primary_color}{bar.name}{Color('reset')}",
                f"{bar.secondary_color}{'DONE' if bar.completed else f'{int((bar.current / bar.total) * 100)}%':>4}{Color('reset')}",
                f"{bar.secondary_color}({bar.current:>{max_total_width}}/{bar.total:>{max_total_width}}){Color('reset')}" if not bar.completed else '',
                bar.message
            ]

        parts = [v + " " * (max(len(strip_ansi(build_parts(bar)[i])) for bar in progress_bars) - len(strip_ansi(v))) for i, v in enumerate(build_parts(self)) if not all(strip_ansi(build_parts(bar)[i]).strip() == "" for bar in progress_bars)]
        return " ".join(parts)

    @property
    def completed(self) -> bool:
        return self.current >= self.total
