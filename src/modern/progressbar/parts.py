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

class ETABackend:
    def add(self, time: float, current: int):
        raise NotImplementedError

    def estimate(self, current: int, total: int) -> Optional[float]:
        raise NotImplementedError

class RateSample:
    def __init__(self, time: float, current: int):
        self.time = time
        self.current = current

class InstantaneousRateETABackend(ETABackend):
    def __init__(self):
        self.previous: Optional[RateSample] = None
        self.rate: Optional[float] = None

    def add(self, time: float, current: int):
        sample = RateSample(time, current)
        if self.previous is not None:
            dt = sample.time - self.previous.time
            if dt > 0:
                self.rate = (sample.current - self.previous.current) / dt
        self.previous = sample

    def estimate(self, current: int, total: int) -> Optional[float]:
        if not self.rate or self.rate <= 0:
            return None
        return (total - current) / self.rate

class EMAETABackend(ETABackend):
    def __init__(self, smoothing: float = 0.3):
        self.smoothing = smoothing
        self.previous: Optional[RateSample] = None
        self.rate: Optional[float] = None

    def add(self, time: float, current: int):
        sample = RateSample(time, current)
        if self.previous is not None:
            dt = sample.time - self.previous.time
            if dt > 0:
                instant_rate = (sample.current - self.previous.current) / dt
                self.rate = instant_rate if self.rate is None else self.smoothing * instant_rate + (1 - self.smoothing) * self.rate
        self.previous = sample

    def estimate(self, current: int, total: int) -> Optional[float]:
        if not self.rate or self.rate <= 0:
            return None
        return (total - current) / self.rate

class LinearRegressionETABackend(ETABackend):
    def __init__(self, window_size: int = 20, outlier_threshold: float = 3.0):
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

    def estimate(self, current: int, total: int) -> Optional[float]:
        rate = self.rate()
        if not rate or rate <= 0:
            return None
        return (total - current) / rate

class HoltLinearETABackend(ETABackend):
    def __init__(self, level_smoothing: float = 0.3, trend_smoothing: float = 0.1):
        self.level_smoothing = level_smoothing
        self.trend_smoothing = trend_smoothing
        self.level: Optional[float] = None
        self.trend: Optional[float] = None
        self.previous_time: Optional[float] = None

    def add(self, time: float, current: int):
        if self.level is None:
            self.level = float(current)
            self.trend = 0.0
            self.previous_time = time
            return

        dt = time - self.previous_time
        if dt <= 0:
            return
        self.previous_time = time

        previous_level = self.level
        forecast = self.level + self.trend * dt
        self.level = self.level_smoothing * current + (1 - self.level_smoothing) * forecast
        self.trend = self.trend_smoothing * ((self.level - previous_level) / dt) + (1 - self.trend_smoothing) * self.trend

    def estimate(self, current: int, total: int) -> Optional[float]:
        if self.level is None or not self.trend or self.trend <= 0:
            return None
        return (total - self.level) / self.trend

class KalmanFilterETABackend(ETABackend):
    def __init__(self, process_variance: float = 1e-2, measurement_variance: float = 1.0):
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.position: Optional[float] = None
        self.velocity = 0.0
        self.previous_time: Optional[float] = None
        self.position_variance = 1.0
        self.cross_variance = 0.0
        self.velocity_variance = 1.0

    def add(self, time: float, current: int):
        if self.position is None:
            self.position = float(current)
            self.previous_time = time
            return

        dt = time - self.previous_time
        if dt <= 0:
            return
        self.previous_time = time

        predicted_position = self.position + self.velocity * dt
        predicted_velocity = self.velocity

        predicted_position_variance = self.position_variance + 2 * dt * self.cross_variance + dt * dt * self.velocity_variance + self.process_variance
        predicted_cross_variance = self.cross_variance + dt * self.velocity_variance
        predicted_velocity_variance = self.velocity_variance + self.process_variance

        innovation = current - predicted_position
        innovation_variance = predicted_position_variance + self.measurement_variance
        if innovation_variance == 0:
            self.position = predicted_position
            self.velocity = predicted_velocity
            self.position_variance = predicted_position_variance
            self.cross_variance = predicted_cross_variance
            self.velocity_variance = predicted_velocity_variance
            return

        position_gain = predicted_position_variance / innovation_variance
        velocity_gain = predicted_cross_variance / innovation_variance

        self.position = predicted_position + position_gain * innovation
        self.velocity = predicted_velocity + velocity_gain * innovation

        self.position_variance = (1 - position_gain) * predicted_position_variance
        self.cross_variance = (1 - position_gain) * predicted_cross_variance
        self.velocity_variance = predicted_velocity_variance - velocity_gain * predicted_cross_variance

    def estimate(self, current: int, total: int) -> Optional[float]:
        if self.position is None or self.velocity <= 0:
            return None
        return (total - self.position) / self.velocity

class EnsembleETABackend(ETABackend):
    def __init__(self, backends: Optional[List[ETABackend]] = None):
        self.backends = backends or [LinearRegressionETABackend(), EMAETABackend(), HoltLinearETABackend(), KalmanFilterETABackend()]

    def add(self, time: float, current: int):
        for backend in self.backends:
            backend.add(time, current)

    def estimate(self, current: int, total: int) -> Optional[float]:
        estimates = sorted(estimate for backend in self.backends if (estimate := backend.estimate(current, total)) is not None)
        if not estimates:
            return None

        middle = len(estimates) // 2
        if len(estimates) % 2 == 0:
            return (estimates[middle - 1] + estimates[middle]) / 2
        return estimates[middle]

class ETAPart(main.ProgressBarPart):
    def __init__(self, backend: Optional[ETABackend] = None):
        self.backend = backend or LinearRegressionETABackend()

    def render(self, bar: "ProgressBar") -> str:
        self.backend.add(time.monotonic(), bar.current)

        if bar.completed or bar.current <= 0:
            return ""

        eta = self.backend.estimate(bar.current, bar.total)
        if eta is None:
            return ""

        return str(bar.secondary_color) + ETAPart.format(eta) + str(Color("reset"))

    @staticmethod
    def format(seconds: float) -> str:
        seconds = max(0, int(seconds))
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02}:{seconds:02}"
