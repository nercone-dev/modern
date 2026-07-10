import os
import sys
import shutil
import threading
from typing import Dict, List, Optional, TextIO

lock = threading.RLock()
regions: List["TerminalRegion"] = []
heights: Dict["TerminalRegion", int] = {}

proxy: Optional["StdoutProxy"] = None
stdout: Optional[TextIO] = None

class TerminalRegion:
    def render(self) -> str:
        raise NotImplementedError

class StdoutProxy:
    def __init__(self, stream: TextIO):
        self.stream = stream
        self.buffer = ""

    def __getattr__(self, name):
        return getattr(self.stream, name)

    def write(self, content: str) -> int:
        self.buffer += content
        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            Terminal.write_line(line)
        return len(content)

    def flush(self):
        self.stream.flush()

class Terminal:
    @staticmethod
    def size() -> os.terminal_size:
        return shutil.get_terminal_size()

    @staticmethod
    def width() -> int:
        return Terminal.size().columns

    @staticmethod
    def height() -> int:
        return Terminal.size().lines

    @staticmethod
    def stream() -> TextIO:
        global stdout
        if stdout is None:
            stdout = sys.stdout
        return stdout

    @staticmethod
    def attach(region: TerminalRegion) -> TerminalRegion:
        with lock:
            global proxy
            stream = Terminal.stream()
            if not regions and sys.stdout is stream:
                proxy = StdoutProxy(stream)
                sys.stdout = proxy
            regions.append(region)
            lines = region.render().split("\n")
            for line in lines:
                stream.write(line + "\n")
            heights[region] = len(lines)
            stream.flush()
        return region

    @staticmethod
    def detach(region: TerminalRegion):
        with lock:
            if region not in regions:
                return

            erased = sum(heights.values())
            regions.remove(region)
            del heights[region]
            Terminal.erase(erased)
            Terminal.paint()
            Terminal.stream().flush()

            global proxy
            if not regions and proxy is not None:
                if proxy.buffer:
                    Terminal.stream().write(proxy.buffer)
                    proxy.buffer = ""
                    Terminal.stream().flush()
                sys.stdout = Terminal.stream()
                proxy = None

    @staticmethod
    def redraw(region: Optional[TerminalRegion] = None):
        with lock:
            if region is None:
                Terminal.erase(sum(heights.values()))
                Terminal.paint()
                Terminal.stream().flush()
                return

            if region not in regions:
                return

            lines = region.render().split("\n")

            if len(lines) != heights[region]:
                Terminal.redraw()
                return

            stream = Terminal.stream()
            idx = regions.index(region)
            below = sum(heights[sibling] for sibling in regions[idx + 1:])

            stream.write(f"\033[{heights[region] + below}A\r")
            for line in lines:
                stream.write(f"\033[K{line}\n")
            if below:
                stream.write(f"\033[{below}B\r")
            stream.flush()

    @staticmethod
    def write(content: str = ""):
        with lock:
            Terminal.erase(sum(heights.values()))
            Terminal.stream().write(content)
            Terminal.paint()
            Terminal.stream().flush()

    @staticmethod
    def write_line(content: str = ""):
        with lock:
            Terminal.erase(sum(heights.values()))
            stream = Terminal.stream()
            for line in content.split("\n"):
                stream.write(line + "\n")
            Terminal.paint()
            Terminal.stream().flush()

    @staticmethod
    def paint():
        stream = Terminal.stream()
        for region in regions:
            lines = region.render().split("\n")
            for line in lines:
                stream.write(line + "\n")
            heights[region] = len(lines)

    @staticmethod
    def erase(count: int):
        if not count:
            return
        Terminal.stream().write(f"\033[{count}A\r\033[J")
