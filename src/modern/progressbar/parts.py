import time
from typing import Optional, List, TYPE_CHECKING

from ..color import Color
from . import main

if TYPE_CHECKING:
    from .main import ProgressBar

class TextPart(main.ProgressBarPart):
    def __init__(self, text: str, color: Color = Color("default")):
        self.text = text
        self.color = color

    def render(self, bar: "ProgressBar") -> str:
        return str(self.color) + self.text + str(Color("reset"))

class NamePart(main.ProgressBarPart):
    def render(self, bar: "ProgressBar") -> str:
        return str(bar.primary_color) + bar.name + str(Color("reset"))

class PercentagePart(main.ProgressBarPart):
    def render(self, bar: "ProgressBar") -> str:
        if bar.completed:
            return str(bar.secondary_color) + "DONE" + str(Color("reset"))
        else:
            return str(bar.secondary_color) + str(int((bar.current / bar.total) * 100)).rjust(3) + "%" + str(Color("reset"))

class ProgressPart(main.ProgressBarPart):
    def render(self, bar: "ProgressBar") -> str:
        if bar.completed:
            return ""
        else:
            return str(bar.secondary_color) + "(" + str(bar.current).rjust(max(len(str(bar.total)) for bar in main.progress_bars)) + "/" + str(bar.total).rjust(max(len(str(bar.total)) for bar in main.progress_bars)) + ")" + str(Color("reset"))

class MessagePart(main.ProgressBarPart):
    def render(self, bar: "ProgressBar") -> str:
        return bar.message

class RateSample:
    def __init__(self, time: float, current: int):
        self.time = time
        self.current = current

class RateWindow:
    def __init__(self, window_size: int, outlier_threshold: float):
        self.window_size = window_size
        self.outlier_threshold = outlier_threshold
        self.samples: List[RateSample] = []

    def add(self, time: float, current: int):
        if self.samples and self.samples[-1].time == time:
            return
        self.samples.append(RateSample(time, current))
        if len(self.samples) > self.window_size:
            self.samples.pop(0)

    def outliers_removed(self) -> List[RateSample]:
        if len(self.samples) < 3:
            return self.samples

        rates = []
        for previous, sample in zip(self.samples, self.samples[1:]):
            dt = sample.time - previous.time
            if dt > 0:
                rates.append((sample.current - previous.current) / dt)

        if not rates:
            return self.samples

        rates.sort()
        median_rate = rates[len(rates) // 2]
        deviations = sorted(abs(rate - median_rate) for rate in rates)
        median_deviation = deviations[len(deviations) // 2] or 1e-9

        filtered = [self.samples[0]]
        for previous, sample in zip(self.samples, self.samples[1:]):
            dt = sample.time - previous.time
            if dt <= 0:
                continue
            rate = (sample.current - previous.current) / dt
            if abs(rate - median_rate) <= self.outlier_threshold * median_deviation:
                filtered.append(sample)
        return filtered

    def rate(self) -> Optional[float]:
        samples = self.outliers_removed()
        if len(samples) < 2:
            return None

        mean_time = sum(sample.time for sample in samples) / len(samples)
        mean_current = sum(sample.current for sample in samples) / len(samples)

        covariance = sum((sample.time - mean_time) * (sample.current - mean_current) for sample in samples)
        variance = sum((sample.time - mean_time) ** 2 for sample in samples)
        if variance == 0:
            return None

        return covariance / variance

class ETAPart(main.ProgressBarPart):
    def __init__(self, window_size: int = 20, outlier_threshold: float = 3.0):
        self.window_size = window_size
        self.outlier_threshold = outlier_threshold

    def render(self, bar: "ProgressBar") -> str:
        window: RateWindow = bar.scope.setdefault("eta", RateWindow(self.window_size, self.outlier_threshold))
        window.add(time.monotonic(), bar.current)

        if bar.completed or bar.current <= 0:
            return ""

        rate = window.rate()
        if not rate or rate <= 0:
            return ""

        remaining = bar.total - bar.current
        eta = remaining / rate

        return str(bar.secondary_color) + ETAPart.format(eta) + str(Color("reset"))

    @staticmethod
    def format(seconds: float) -> str:
        seconds = max(0, int(seconds))
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02}:{seconds:02}"
