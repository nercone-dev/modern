import sys
import threading

from .color import Color
from .logging import LoggingLevel, max_process_width as logging_max_process_width

max_total_width = 0
max_process_width = 0

lock = threading.Lock()
progress_bars: list["ProgressBar"] = []

class ProgressBar:
    def __init__(self, process_name: str, total: int, current: int = 0, primary_bar: str = "-", secondary_bar: str = "-", primary_color: str = "blue", secondary_color: str = "grey"):
        self.process_name = process_name
        self.total = total
        self.current = current
        self.primary_bar = primary_bar
        self.secondary_bar = secondary_bar
        self.primary_color = primary_color
        self.secondary_color = secondary_color

        self.active = False
        self.step = 0
        self.message = "No message"

        global max_total_width, max_process_width
        max_total_width = max(max_total_width, len(str(total)))
        max_process_width = max(max_process_width, len(process_name))

    def set_message(self, message: str = ""):
        self.message = message

    def start(self):
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
        self.current = self.total
        self.active = False
        self.render()

    def render(self):
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
        progress = self.current / self.total
        percentage = int(progress * 100)
        return f"[{self.bar()}] {Color.from_name(self.primary_color)}{self.process_name.ljust(max_process_width)}{Color.from_name('reset')} {Color.from_name(self.secondary_color)}{'DONE' if self.completed else f'{percentage}%':>4}{Color.from_name('reset')}{Color.from_name('gray')}{f' ({self.current:>{max_total_width}}/{self.total:>{max_total_width}})' if not self.completed else ''}{Color.from_name('reset')} {self.message}{Color.from_name('reset')}"

    def bar(self):
        progress = self.current / self.total
        bar_length = 20 + LoggingLevel.max_width() + logging_max_process_width
        bar_filled_length = int(bar_length * progress)
        return f"{Color.from_name(self.primary_color)}{self.primary_bar * bar_filled_length}{Color.from_name(self.secondary_color)}{self.secondary_bar * (bar_length - bar_filled_length)}{Color.from_name('reset')}"

    @property
    def completed(self) -> bool:
        return self.current >= self.total
