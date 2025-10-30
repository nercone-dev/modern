import sys

ModernLoggingLevels = ["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]
MAX_LOG_LEVEL_WIDTH = max(len(level) for level in ModernLoggingLevels)

class ModernLogging:
    def __init__(self, process_name):
        self.process_name = process_name

    def log(self, message, level="INFO"):
        level_text = level.strip().upper()
        if level_text in ["D", "DEBUG"]:
            print(self._make(message, level="DEBUG", color=35))
        elif level_text in ["I", "INFO", "INFORMATION"]:
            print(self._make(message, level="INFO", color=34))
        elif level_text in ["W", "WARN", "WARNING"]:
            print(self._make(message, level="WARN", color=33))
        elif level_text in ["E", "ERROR"]:
            print(self._make(message, level="ERROR", color=31))
        elif level_text in ["C", "CRITICAL"]:
            print(self._make(message, level="CRITICAL", color=31))
        else:
            print(self._make(message, level=level, color=34))

    def _make(self, message, level="INFO", color=34):
        padded_level = level.ljust(max(MAX_LOG_LEVEL_WIDTH, len(level)))
        return f"{self.process_name} {self._color(color)}{padded_level} | {self._color(0)}{message}"

    def _color(self, color_code):
        return f"\033[{color_code}m"
