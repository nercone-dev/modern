import math
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
    def update(self, time: float, current: int):
        raise NotImplementedError

    def rate(self) -> Optional[float]:
        raise NotImplementedError

    def estimate(self, current: int, total: int) -> Optional[float]:
        rate = self.rate()
        if rate is None or not math.isfinite(rate) or rate <= 0:
            return None
        return max(0.0, (total - current) / rate)

class RateSample:
    def __init__(self, time: float, current: int):
        self.time = time
        self.current = current

class InstantaneousRateETABackend(ETABackend):
    def __init__(self, minimum_interval: float = 0.05):
        self.minimum_interval = minimum_interval
        self.anchor: Optional[RateSample] = None
        self.measured: Optional[float] = None

    def update(self, time: float, current: int):
        sample = RateSample(time, current)
        if self.anchor is None:
            self.anchor = sample
            return

        interval = sample.time - self.anchor.time
        if interval <= 0 or interval < self.minimum_interval:
            return

        self.measured = (sample.current - self.anchor.current) / interval
        self.anchor = sample

    def rate(self) -> Optional[float]:
        return self.measured

class EMAETABackend(ETABackend):
    def __init__(self, half_life: float = 2.0, minimum_interval: float = 0.05):
        self.half_life = half_life
        self.minimum_interval = minimum_interval
        self.anchor: Optional[RateSample] = None
        self.smoothed: Optional[float] = None

    def update(self, time: float, current: int):
        sample = RateSample(time, current)
        if self.anchor is None:
            self.anchor = sample
            return

        interval = sample.time - self.anchor.time
        if interval <= 0 or interval < self.minimum_interval:
            return

        measured = (sample.current - self.anchor.current) / interval
        self.anchor = sample

        if self.smoothed is None or self.half_life <= 0:
            self.smoothed = measured
            return

        weight = 1 - 0.5 ** (interval / self.half_life)
        self.smoothed = weight * measured + (1 - weight) * self.smoothed

    def rate(self) -> Optional[float]:
        return self.smoothed

class LinearRegressionETABackend(ETABackend):
    def __init__(self, window: float = 2.0, minimum_samples: int = 16, maximum_samples: int = 128, minimum_interval: float = 0.05):
        self.window = window
        self.minimum_samples = minimum_samples
        self.maximum_samples = maximum_samples
        self.minimum_interval = minimum_interval
        self.samples: List[RateSample] = []

    def update(self, time: float, current: int):
        if self.samples:
            interval = time - self.samples[-1].time
            if interval <= 0 or interval < self.minimum_interval:
                return

        self.samples.append(RateSample(time, current))

        horizon = time - self.window
        while len(self.samples) > self.minimum_samples and self.samples[0].time < horizon:
            self.samples.pop(0)
        while len(self.samples) > self.maximum_samples:
            self.samples.pop(0)

    def rate(self) -> Optional[float]:
        if len(self.samples) < 2:
            return None

        mean_time = sum(sample.time for sample in self.samples) / len(self.samples)
        mean_current = sum(sample.current for sample in self.samples) / len(self.samples)

        covariance = sum((sample.time - mean_time) * (sample.current - mean_current) for sample in self.samples)
        variance = sum((sample.time - mean_time) ** 2 for sample in self.samples)
        if variance == 0:
            return None

        return covariance / variance

class HoltLinearETABackend(ETABackend):
    def __init__(self, level_half_life: float = 0.01, trend_half_life: float = 1.0, minimum_interval: float = 0.05):
        self.level_half_life = level_half_life
        self.trend_half_life = trend_half_life
        self.minimum_interval = minimum_interval
        self.level: Optional[float] = None
        self.trend: Optional[float] = None
        self.started: Optional[float] = None
        self.previous_time: Optional[float] = None

    def update(self, time: float, current: int):
        if self.level is None:
            self.level = float(current)
            self.trend = 0.0
            self.started = time
            self.previous_time = time
            return

        interval = time - self.previous_time
        if interval <= 0 or interval < self.minimum_interval:
            return
        self.previous_time = time

        level_weight = 1 - 0.5 ** (interval / self.level_half_life) if self.level_half_life > 0 else 1.0
        trend_weight = 1 - 0.5 ** (interval / self.trend_half_life) if self.trend_half_life > 0 else 1.0

        previous_level = self.level
        forecast = self.level + self.trend * interval
        self.level = level_weight * current + (1 - level_weight) * forecast
        self.trend = trend_weight * ((self.level - previous_level) / interval) + (1 - trend_weight) * self.trend

    def rate(self) -> Optional[float]:
        if self.trend is None or self.started is None:
            return None
        if self.trend_half_life <= 0:
            return self.trend

        settled = 1 - 0.5 ** ((self.previous_time - self.started) / self.trend_half_life)
        if settled <= 0:
            return None
        return self.trend / settled

class KalmanFilterETABackend(ETABackend):
    def __init__(self, drift: float = 0.15, jitter: float = 0.5, minimum_interval: float = 0.05):
        self.drift = drift
        self.jitter = jitter
        self.minimum_interval = minimum_interval
        self.first: Optional[RateSample] = None
        self.position: Optional[float] = None
        self.velocity = 0.0
        self.previous_time: Optional[float] = None
        self.position_variance = 0.0
        self.cross_variance = 0.0
        self.velocity_variance = 0.0

    def reset(self, time: float, current: int):
        self.first = RateSample(time, current)
        self.position = float(current)
        self.velocity = 0.0
        self.previous_time = time
        self.position_variance = 0.0
        self.cross_variance = 0.0
        self.velocity_variance = 0.0

    def seed(self, current: int):
        elapsed = self.previous_time - self.first.time
        if elapsed <= 0:
            return

        velocity = (current - self.first.current) / elapsed
        if velocity <= 0:
            return

        self.position = float(current)
        self.velocity = velocity
        self.position_variance = (self.jitter * velocity) ** 2
        self.cross_variance = 0.0
        self.velocity_variance = (self.drift * velocity) ** 2

    def update(self, time: float, current: int):
        if self.position is None or not math.isfinite(self.position) or not math.isfinite(self.velocity):
            self.reset(time, current)
            return

        interval = time - self.previous_time
        if interval <= 0 or interval < self.minimum_interval:
            return
        self.previous_time = time

        if self.velocity <= 0:
            self.seed(current)
            return

        process_variance = (self.drift * self.velocity) ** 2
        measurement_variance = (self.jitter * self.velocity) ** 2

        predicted_position = self.position + self.velocity * interval
        predicted_velocity = self.velocity

        predicted_position_variance = self.position_variance + 2 * interval * self.cross_variance + interval * interval * self.velocity_variance + process_variance * interval ** 3 / 3
        predicted_cross_variance = self.cross_variance + interval * self.velocity_variance + process_variance * interval ** 2 / 2
        predicted_velocity_variance = self.velocity_variance + process_variance * interval

        innovation = current - predicted_position
        innovation_variance = predicted_position_variance + measurement_variance
        if innovation_variance <= 0:
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

    def rate(self) -> Optional[float]:
        return self.velocity

class EnsembleETABackend(ETABackend):
    def __init__(self, backends: Optional[List[ETABackend]] = None, quantile: float = 0.5):
        self.backends = backends or [LinearRegressionETABackend(), EMAETABackend(), HoltLinearETABackend(), KalmanFilterETABackend()]
        self.quantile = quantile

    def update(self, time: float, current: int):
        for backend in self.backends:
            backend.update(time, current)

    def estimate(self, current: int, total: int) -> Optional[float]:
        return EnsembleETABackend.combined([backend.estimate(current, total) for backend in self.backends], self.quantile)

    @staticmethod
    def combined(estimates: List[Optional[float]], quantile: float = 0.5) -> Optional[float]:
        values = sorted(estimate for estimate in estimates if estimate is not None and math.isfinite(estimate))
        if not values:
            return None

        position = min(max(quantile, 0.0), 1.0) * (len(values) - 1)
        lower = math.floor(position)
        upper = min(lower + 1, len(values) - 1)
        return values[lower] * (1 - (position - lower)) + values[upper] * (position - lower)

class Prediction:
    def __init__(self, time: float, target: int, estimates: List[Optional[float]]):
        self.time = time
        self.target = target
        self.estimates = estimates

class AutoETABackend(ETABackend):
    def __init__(self, backends: Optional[List[ETABackend]] = None, horizon: float = 5.0, patience: float = 4.0, decay: float = 0.9, hysteresis: float = 0.25):
        self.backends = backends or [InstantaneousRateETABackend(), EMAETABackend(), LinearRegressionETABackend(), HoltLinearETABackend(), KalmanFilterETABackend()]
        self.horizon = horizon
        self.patience = patience
        self.decay = decay
        self.hysteresis = hysteresis
        self.errors = [0.0] * len(self.backends)
        self.counts = [0.0] * len(self.backends)
        self.pending: Optional[Prediction] = None
        self.leader: Optional[int] = None

    def target(self, current: int) -> Optional[int]:
        pace = EnsembleETABackend.combined([backend.estimate(current, current + 1) for backend in self.backends])
        if pace is None or pace <= 0:
            return None
        return current + max(1, round(self.horizon / pace))

    def score(self, time: float, current: int):
        if self.pending is None:
            return

        if current < self.pending.target:
            if time - self.pending.time > self.horizon * self.patience:
                self.pending = None
            return

        elapsed = time - self.pending.time
        for index, estimate in enumerate(self.pending.estimates):
            if estimate is None:
                continue
            self.errors[index] = self.decay * self.errors[index] + abs(estimate - elapsed)
            self.counts[index] = self.decay * self.counts[index] + 1
        self.pending = None

    def elect(self):
        scored = [index for index in range(len(self.backends)) if self.counts[index] > 0]
        if not scored:
            return

        best = min(scored, key=lambda index: self.errors[index] / self.counts[index])
        if self.leader is None or self.leader not in scored:
            self.leader = best
        elif best != self.leader and self.errors[best] / self.counts[best] < (self.errors[self.leader] / self.counts[self.leader]) * (1 - self.hysteresis):
            self.leader = best

    def update(self, time: float, current: int):
        self.score(time, current)

        for backend in self.backends:
            backend.update(time, current)

        if self.pending is None:
            target = self.target(current)
            if target is not None:
                self.pending = Prediction(time, target, [backend.estimate(current, target) for backend in self.backends])

        self.elect()

    def estimate(self, current: int, total: int) -> Optional[float]:
        if self.leader is not None:
            estimate = self.backends[self.leader].estimate(current, total)
            if estimate is not None and math.isfinite(estimate):
                return estimate
        return EnsembleETABackend.combined([backend.estimate(current, total) for backend in self.backends])

class ETAPart(main.ProgressBarPart):
    def __init__(self, backend: Optional[ETABackend] = None):
        self.backend = backend or AutoETABackend()
        self.latest: Optional[RateSample] = None

    def text(self, bar: "ProgressBar") -> str:
        if bar.completed or bar.current <= 0:
            return ""

        eta = self.backend.estimate(bar.current, bar.total)
        if eta is None or not math.isfinite(eta):
            return ""

        if self.latest is not None:
            eta = max(eta, time.monotonic() - self.latest.time)

        return ETAPart.format(eta)

    def render(self, bar: "ProgressBar") -> str:
        text = self.text(bar)
        if not text:
            return ""

        width = max((len(other.text(other_bar)) for other_bar in main.progress_bars for other in other_bar.prefix + other_bar.suffix if type(other) is ETAPart), default=0)
        return str(bar.secondary_color) + text.rjust(width) + str(Color("reset"))

    def on_update(self, bar: "ProgressBar"):
        now = time.monotonic()
        if self.latest is None or bar.current != self.latest.current:
            self.latest = RateSample(now, bar.current)
        self.backend.update(now, bar.current)

    @staticmethod
    def format(seconds: float) -> str:
        seconds = max(0, round(seconds))
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)

        if hours:
            return f"{hours}:{minutes:02}:{seconds:02}"
        else:
            return f"{minutes:02}:{seconds:02}"
