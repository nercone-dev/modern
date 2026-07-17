import time

from .text import Text
from .logger import Logger, LogLevel
from .progressbar import ProgressBar

def demo_color():
    print("── Color ──")
    line = Text()
    for name in ["red", "green", "yellow", "blue", "magenta", "cyan"]:
        line += Text(f" {name} ", forground=name) + " "
    print(line)

    line = Text()
    for name in ["red", "green", "yellow", "blue", "magenta", "cyan"]:
        line += Text(f" {name} ", forground="white", background=name) + " "
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
    main = Logger("Main", primary_color="cyan",  display_level=LogLevel.DEBUG)
    sub  = Logger("Sub",  primary_color="green", display_level=LogLevel.DEBUG)

    main.info("Main #0")
    time.sleep(1)

    main.warning("Main #1")
    sub.info("Sub #0")
    time.sleep(2)

    main.info("Main #2")
    time.sleep(1)

    main.error("Main #3")
    sub.critical("Sub #1")
    time.sleep(2)

    main.critical("Main #4")
    time.sleep(1)

    if main.prompt("Continue?", default="Y", choices=["Y", "n"]) == "n":
        exit(0)

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
