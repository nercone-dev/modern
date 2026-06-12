import sys
import time
import shutil
import threading
from strip_ansi import strip_ansi

from . import logging
from .color import Color

lock = threading.Lock()
progress_bars: list["ProgressBar"] = []
max_total_width = 0

class ProgressBar:
    def __init__(self, process_name: str, total: int, current: int = 0, start: bool = True, bar_length: int | None = None, primary_bar: str = "━", secondary_bar: str = "━", primary_color: str = "blue", secondary_color: str = "grey"):
        self.process_name = process_name
        self.total = total
        self.current = current
        self.bar_length = bar_length
        self.primary_bar = primary_bar
        self.secondary_bar = secondary_bar
        self.primary_color = primary_color
        self.secondary_color = secondary_color

        self.active = False
        self.step = 0
        self.message = ""

        global max_total_width
        max_total_width = max(max_total_width, len(str(total)))

        if start:
            self.start()

    def set_message(self, message: str = ""):
        self.message = message

    def start(self):
        global progress_bars
        if self.active:
            return
        with lock:
            self.active = True
            progress_bars.append(self)
            sys.stdout.write(self.format() + "\n")
            sys.stdout.flush()

    def update(self, amount: int = 1):
        self.current += amount
        if self.current > self.total:
            self.current = self.total
        self.render()

    def finish(self):
        global progress_bars
        self.current = self.total
        self.active = False
        self.render()

        for bar in progress_bars:
            bar.render()

    def render(self):
        global progress_bars
        with lock:
            if self not in progress_bars:
                return

            idx = progress_bars.index(self)
            lines_up = len(progress_bars) - idx

            sys.stdout.write(f"\033[{lines_up}A")
            sys.stdout.write("\r\033[K")
            sys.stdout.write(self.format())
            sys.stdout.write(f"\033[{lines_up}B")
            sys.stdout.write("\r")
            sys.stdout.flush()

    def format(self):
        suffix = self.suffix()

        terminal_size = shutil.get_terminal_size((len(strip_ansi(suffix)) + 31, 1))
        bar_length = self.bar_length or (None if logging.max_prefix_width <= 1 else logging.max_prefix_width) or (terminal_size.columns - len(strip_ansi(suffix)) - 1)

        return f"{self.bar(bar_length)} {suffix}{Color.from_name('reset')}"

    def bar(self, bar_length: int):
        progress = self.current / self.total
        bar_filled_length = int(bar_length * progress)
        return f"{Color.from_name(self.primary_color)}{self.primary_bar * bar_filled_length}{Color.from_name(self.secondary_color)}{self.secondary_bar * (bar_length - bar_filled_length)}{Color.from_name('reset')}"

    def suffix(self):
        global progress_bars
        progress = self.current / self.total
        percentage = int(progress * 100)

        def build_parts(bar: ProgressBar) -> list[str]:
            return [
                f"{Color.from_name(bar.primary_color)}{bar.process_name}{Color.from_name('reset')}",
                f"{Color.from_name(bar.secondary_color)}{'DONE' if bar.completed else f'{percentage}%':>4}{Color.from_name('reset')}",
                f"{Color.from_name(bar.secondary_color)}({bar.current:>{max_total_width}}/{bar.total:>{max_total_width}}){Color.from_name('reset')}" if not bar.completed else '',
                bar.message
            ]

        parts = [v + " " * (max(len(strip_ansi(build_parts(bar)[i])) for bar in progress_bars) - len(strip_ansi(v))) for i, v in enumerate(build_parts(self)) if not all(strip_ansi(build_parts(bar)[i]).strip() == "" for bar in progress_bars)]
        return " ".join(parts)

    @property
    def completed(self) -> bool:
        return self.current >= self.total
