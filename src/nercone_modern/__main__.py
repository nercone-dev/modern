import time

from .text import Text
from .logging import Logging, LoggingLevel
from .progressbar import ProgressBar

def demo_color():
    print("── Color ──")
    line = Text()
    for name in ["red", "green", "yellow", "blue", "magenta", "cyan"]:
        line += Text(f" {name} ", forground_color=name)
    print(line)

    line = Text()
    for name in ["red", "green", "yellow", "blue", "magenta", "cyan"]:
        line += Text(f" {name} ", background_color=name)
    print(line)

def demo_text():
    print("\n── Text ──")
    a = Text("Hello, ", "cyan")
    b = Text("world!", "yellow")
    print(str(a))
    print(str(b))
    print(str(a + b))

def demo_logging():
    print("\n── Logging ──")
    main = Logging("Main", primary_color="cyan",  display_level=LoggingLevel.DEBUG)
    sub  = Logging("Sub",  primary_color="green", display_level=LoggingLevel.DEBUG)
    main.log("Main #0", LoggingLevel.INFO)
    time.sleep(1)
    main.log("Main #1", LoggingLevel.WARNING)
    sub.log("Sub #0", LoggingLevel.INFO)
    time.sleep(2)
    main.log("Main #2", LoggingLevel.INFO)
    time.sleep(1)
    main.log("Main #3", LoggingLevel.ERROR)
    sub.log("Sub #1", LoggingLevel.CRITICAL)
    time.sleep(2)
    main.log("Main #4", LoggingLevel.CRITICAL)
    time.sleep(1)

def demo_progressbar():
    print("\n── ProgressBar ──")

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
