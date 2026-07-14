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

class RateEstimator:
    def __init__(self, process_variance: float, measurement_variance: float):
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.rate: Optional[float] = None
        self.trend = 0.0
        self.rate_variance = measurement_variance
        self.trend_variance = 1.0
        self.covariance = 0.0

    def update(self, measured_rate: float, dt: float):
        if self.rate is None:
            self.rate = measured_rate
            return

        predicted_rate = self.rate + self.trend * dt
        predicted_trend = self.trend

        q = self.process_variance
        predicted_rate_variance = self.rate_variance + 2 * dt * self.covariance + dt * dt * self.trend_variance + (dt ** 4 / 4) * q
        predicted_covariance = self.covariance + dt * self.trend_variance + (dt ** 3 / 2) * q
        predicted_trend_variance = self.trend_variance + dt * dt * q

        innovation = measured_rate - predicted_rate
        innovation_variance = predicted_rate_variance + self.measurement_variance

        rate_gain = predicted_rate_variance / innovation_variance
        trend_gain = predicted_covariance / innovation_variance

        self.rate = predicted_rate + rate_gain * innovation
        self.trend = predicted_trend + trend_gain * innovation

        self.rate_variance = predicted_rate_variance * (1 - rate_gain)
        self.covariance = predicted_covariance * (1 - rate_gain)
        self.trend_variance = predicted_trend_variance - trend_gain * predicted_covariance

class ETAPart(ProgressBarPart):
    def __init__(self, process_variance: float = 0.01, measurement_variance: float = 1.0):
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance

    def render(self, bar: "ProgressBar") -> str:
        state = bar.scope.setdefault("eta", {"last_time": None, "last_current": None, "estimator": RateEstimator(self.process_variance, self.measurement_variance)})

        now = time.monotonic()
        if state["last_time"] is not None and state["last_current"] is not None:
            delta_current = bar.current - state["last_current"]
            delta_time = now - state["last_time"]
            if delta_current > 0 and delta_time > 0:
                measured_rate = delta_current / delta_time
                state["estimator"].update(measured_rate, delta_time)
        state["last_time"] = now
        state["last_current"] = bar.current

        if bar.completed or bar.current <= 0:
            return ""

        rate = state["estimator"].rate
        if not rate or rate <= 0:
            return ""

        remaining = bar.total - bar.current
        eta = remaining / rate

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
