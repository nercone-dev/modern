from typing import Optional, Any, Union, List, Dict
from strip_ansi import strip_ansi

from ..color import Color
from ..terminal import Terminal, TerminalRegion

progress_bars: List["ProgressBar"] = []

class ProgressBarPart:
    def __init__(self):
        pass

    def render(self, bar: "ProgressBar") -> str:
        return "DEFAULT"

    def render_once(self, bar: "ProgressBar") -> str:
        state = (bar.current, bar.total, bar.message, bar.completed)
        if getattr(self, "rendered_state", None) != state:
            self.rendered_cache = self.render(bar)
            self.rendered_state = state
        return self.rendered_cache

from .parts import NamePart, PercentagePart, ProgressPart, MessagePart

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
        self.frozen = False

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
        if self.frozen:
            return

        self.active = False
        self.current = self.total

        if self.frozen:
            return

        Terminal.redraw()

        live = [bar for bar in progress_bars if not bar.frozen]
        if all(bar.completed for bar in live):
            for bar in Terminal.freeze(*live):
                bar.frozen = True

    def render(self) -> str:
        global progress_bars

        def aligned(attribute: str) -> List[str]:
            result: List[str] = []

            for part in getattr(self, attribute):
                rendered = {bar: other.render_once(bar) for bar in progress_bars for other in getattr(bar, attribute) if type(other) is type(part)}

                if not any(strip_ansi(value).strip() for value in rendered.values()):
                    continue

                width = max(len(strip_ansi(value)) for value in rendered.values())
                result.append(rendered[self] + " " * (width - len(strip_ansi(rendered[self]))))

            return result

        prefix = aligned("prefix")
        suffix = aligned("suffix")

        return " ".join(prefix + [self.bar(self.bar_length or (Terminal.width() - (len(strip_ansi(" ".join(prefix + suffix))) + 1)))] + suffix)

    def bar(self, length: int):
        filled_length = int(length * (self.current / self.total))
        return f"{self.primary_color}{self.primary_bar * filled_length}{self.secondary_color}{self.secondary_bar * (length - filled_length)}{Color('reset')}"

    @property
    def completed(self) -> bool:
        return self.current >= self.total
