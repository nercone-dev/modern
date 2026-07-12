import time
from typing import Optional, Any, Union, List, Dict
from strip_ansi import strip_ansi

from .color import Color
from .terminal import Terminal, TerminalRegion

progress_bars: List["ProgressBar"] = []

class ProgressBarPart:
    def __init__(self):
        pass

    def render(self, bar: "ProgressBar") -> str:
        return "DEFAULT"

class TextPart(ProgressBarPart):
    def __init__(self, text: str, color: Color = Color("default")):
        self.text = text
        self.color = color

    def render(self, bar: "ProgressBar") -> str:
        return str(self.color) + self.text + str(Color("reset"))

class NamePart(ProgressBarPart):
    def render(self, bar: "ProgressBar") -> str:
        return str(bar.primary_color) + bar.name + str(Color("reset"))

class PercentagePart(ProgressBarPart):
    def render(self, bar: "ProgressBar") -> str:
        if bar.completed:
            return str(bar.secondary_color) + "DONE" + str(Color("reset"))
        else:
            return str(bar.secondary_color) + str(int((bar.current / bar.total) * 100)).rjust(3) + "%" + str(Color("reset"))

class ProgressPart(ProgressBarPart):
    def render(self, bar: "ProgressBar") -> str:
        if bar.completed:
            return ""
        else:
            return str(bar.secondary_color) + "(" + str(bar.current).rjust(max(len(str(bar.total)) for bar in progress_bars)) + "/" + str(bar.total).rjust(max(len(str(bar.total)) for bar in progress_bars)) + ")" + str(Color("reset"))

class MessagePart(ProgressBarPart):
    def render(self, bar: "ProgressBar") -> str:
        return bar.message

class ETAPart(ProgressBarPart):
    def __init__(self, weight: float = 0.5, smoothing: float = 0.3):
        self.weight = weight
        self.smoothing = smoothing

    def render(self, bar: "ProgressBar") -> str:
        state = bar.scope.setdefault("eta", {"start_time": time.monotonic(), "last_time": None, "last_current": None, "ema_rate": None})

        now = time.monotonic()
        if state["last_time"] is not None and state["last_current"] is not None:
            delta_current = bar.current - state["last_current"]
            delta_time = now - state["last_time"]
            if delta_current > 0 and delta_time > 0:
                rate = delta_current / delta_time
                state["ema_rate"] = rate if state["ema_rate"] is None else self.smoothing * rate + (1 - self.smoothing) * state["ema_rate"]
        state["last_time"] = now
        state["last_current"] = bar.current

        if bar.completed or bar.current <= 0:
            return ""

        elapsed = now - state["start_time"]
        if elapsed <= 0:
            return ""

        remaining = bar.total - bar.current
        average_eta = remaining / (bar.current / elapsed)
        ema_eta = remaining / state["ema_rate"] if state["ema_rate"] else average_eta
        eta = average_eta * self.weight + ema_eta * (1 - self.weight)

        return str(bar.secondary_color) + self.format(eta) + str(Color("reset"))

    def format(self, seconds: float) -> str:
        seconds = max(0, int(seconds))
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02}:{seconds:02}"

class ProgressBar(TerminalRegion):
    def __init__(self, name: str, total: int, *, current: int = 0, start: bool = True, prefix: Optional[List[ProgressBarPart]] = None, suffix: Optional[List[ProgressBarPart]] = None, bar_length: Optional[int] = None, primary_bar: str = "━", secondary_bar: str = "━", primary_color: Union[str, Color] = "blue", secondary_color: Union[str, Color] = "grey"):
        self.name = name
        self.total = total
        self.current = current
        self.bar_length = bar_length
        self.primary_bar = primary_bar
        self.secondary_bar = secondary_bar
        self.primary_color = Color(primary_color)
        self.secondary_color = Color(secondary_color)

        self.scope: Dict[str, Any] = {}

        self.prefix = prefix or []
        self.suffix = suffix or [NamePart(), PercentagePart(), ProgressPart(), MessagePart()]

        self.active = False
        self.step = 0
        self.message = ""

        if start:
            self.start()

    def set_message(self, message: str = ""):
        self.message = message
        Terminal.redraw()

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
        Terminal.redraw()

    def finish(self):
        global progress_bars
        self.active = False
        self.current = self.total
        if self not in progress_bars:
            return
        Terminal.redraw()
        if all(bar.completed for bar in progress_bars):
            Terminal.freeze(*progress_bars)
            progress_bars = []

    def render(self) -> str:
        global progress_bars

        prefix: List[str] = []
        for part in self.prefix:
            if not any(strip_ansi(part.render(bar)).strip() for bar in progress_bars):
                continue
            width    = max(len(strip_ansi(part.render(bar))) for bar in progress_bars)
            rendered = part.render(self)
            prefix.append(rendered + " " * (width - len(strip_ansi(rendered))))

        suffix: List[str] = []
        for part in self.suffix:
            if not any(strip_ansi(part.render(bar)).strip() for bar in progress_bars):
                continue
            width    = max(len(strip_ansi(part.render(bar))) for bar in progress_bars)
            rendered = part.render(self)
            suffix.append(rendered + " " * (width - len(strip_ansi(rendered))))

        return " ".join(prefix + [self.bar(self.bar_length or (Terminal.width() - (len(strip_ansi(" ".join(prefix + suffix))) + 1)))] + suffix)

    def bar(self, length: int):
        filled_length = int(length * (self.current / self.total))
        return f"{self.primary_color}{self.primary_bar * filled_length}{self.secondary_color}{self.secondary_bar * (length - filled_length)}{Color('reset')}"

    @property
    def completed(self) -> bool:
        return self.current >= self.total
