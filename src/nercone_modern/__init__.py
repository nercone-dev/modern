import sys

class NerconeModern:
    def __init__(self):
        pass

    def color(self, color_code):
        return f"\033[{color_code}m"
    
    def modernLogging(self, process_name):
        from .logging import ModernLogging
        return ModernLogging(process_name)
    
    def modernProgressBar(self, total: int, process_name: str, process_color: int = 32, spinner_mode: bool = False):
        from .progressbar import ModernProgressBar
        return ModernProgressBar(total, process_name, process_color, spinner_mode)

