import time

from .color import Color
from .text import Text
from .logging import Logging, LoggingLevel
from .progressbar import ProgressBar

def demo_color():
    print(f"── Color ──")
    line = ""
    for name in ["red", "green", "yellow", "blue", "magenta", "cyan", "white", "gray", "bright_red", "bright_green", "bright_yellow", "bright_blue", "bright_magenta", "bright_cyan", "bright_white"]:
        line += f"{Color.from_name(name)}{name}{Color.from_name('reset')}  "
    print(line)

    line = ""
    for name in ["red", "green", "yellow", "blue", "magenta", "cyan"]:
        line += f"{Color.from_name(name, background=True)}{Color.from_name('white')} {name} {Color.from_name('reset')}  "
    print(line)

def demo_text():
    print(f"\n── Text ──")
    a = Text("Hello, ", Color.from_name("cyan"))
    b = Text("world!", Color.from_name("yellow"))
    print(str(a))
    print(str(b))
    print(str(a + b))

def demo_logging():
    print(f"\n── Logging ──")
    main = Logging("Main", display_level=LoggingLevel.DEBUG)
    sub  = Logging("Sub",  display_level=LoggingLevel.DEBUG)
    main.log("Main #1", LoggingLevel.INFO)
    sub.log("Sub #1", LoggingLevel.WARNING)
    main.log("Main #2", LoggingLevel.ERROR)
    sub.log("Sub #2", LoggingLevel.CRITICAL)

def demo_progressbar():
    print(f"\n── ProgressBar ──")

    def run(bar: ProgressBar, step_ms: int):
        for _ in range(bar.total):
            time.sleep(step_ms / 1000)
            bar.update(1)
        bar.finish()

    bar0 = ProgressBar("Download", total=30, primary_color="blue")
    bar1 = ProgressBar("Extract",  total=20, primary_color="cyan")
    bar2 = ProgressBar("Install",  total=15, primary_color="green")

    run(bar0, 50)
    run(bar1, 50)
    run(bar2, 100)

if __name__ == "__main__":
    demo_color()
    demo_text()
    demo_logging()
    demo_progressbar()
