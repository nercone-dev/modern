#!/usr/bin/env python3

# -- nercone-modern --------------------------------------------- #
# progressbar.py on nercone-modern                                #
# Made by DiamondGotCat, Licensed under MIT License               #
# Copyright (c) 2025 DiamondGotCat                                #
# ---------------------------------------------- DiamondGotCat -- #

import sys
import threading
from .color import ModernColor
from .logging import ModernLogging

class ModernProgressBar:
    _active_bars = []
    _last_rendered = False
    _lock = threading.RLock()

    def __init__(self, total: int, process_name: str, spinner_mode: bool = False, primary_color: str = "blue", secondary_color: str = "white", box_color: str = "white", box_left: str = "[", box_right: str = "]", show_bar: bool = True, bar_color: str = "blue"):
        self.total = total
        self.process_name = process_name.strip()
        self.spinner_mode = spinner_mode
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.box_color = box_color
        self.box_left = box_left
        self.box_right = box_right
        self.show_bar = show_bar
        self.bar_color = bar_color
        self.current = 0
        self.index = len(ModernProgressBar._active_bars)
        ModernProgressBar._active_bars.append(self)
        self.log_lines = 0
        self.step = 0
        self.spinner_step = 0
        self.message = "No message"
        self._spinner_thread = None
        self._spinner_stop_event = threading.Event()
        self._spinner_ready = False
        self._initial_render()

    def _initial_render(self):
        print()

    def spinner(self, enabled: bool = True):
        if self.spinner_mode == enabled:
            return
        self.spinner_mode = enabled
        if not self._spinner_ready:
            self._render(advance_spinner=False)
            return
        if enabled:
            self._start_spinner_thread_if_needed()
        else:
            self._stop_spinner_thread()
            self._render(advance_spinner=False)

    def spin_start(self):
        if self._spinner_ready and self.spinner_mode:
            return
        self._spinner_ready = True
        self.spinner_mode = True
        self.spinner_step = 0
        self._start_spinner_thread_if_needed()
        self._render(advance_spinner=False)

    def setMessage(self, message: str = ""):
        self.message = message

    def start(self):
        self._render(advance_spinner=False)
        self._start_spinner_thread_if_needed()

    def update(self, amount: int = 1):
        if self._should_spin():
            self._render(advance_spinner=False)
            return
        self.current += amount
        if self.current > self.total:
            self.current = self.total
        self._render(advance_spinner=False)

    def finish(self):
        self.current = self.total
        self.spinner_mode = False
        self._spinner_ready = False
        self._stop_spinner_thread()
        self._render(final=True, advance_spinner=False)

    def log(self, message: str = "", level_text: str = "INFO", level_color: str | None = None, show_proc: bool | None = None, show_level: bool | None = None, modernLogging: ModernLogging = None):
        with ModernProgressBar._lock:
            self.log_lines = 0
            if modernLogging is None:
                modernLogging = ModernLogging(self.process_name)
            result = modernLogging.make(message=message, level_text=level_text, level_color=level_color, show_proc=show_proc, show_level=show_level)
            if self.log_lines > 0:
                move_up = self.log_lines
            else:
                move_up = len(ModernProgressBar._active_bars) - self.index
            sys.stdout.write(f"\033[{move_up}A")
            sys.stdout.write("\033[K")
            print(result)
            self.log_lines += 1
            self._render(advance_spinner=False)

    def _start_spinner_thread_if_needed(self):
        if not self._should_spin():
            return
        if self._spinner_thread and self._spinner_thread.is_alive():
            return
        self._spinner_stop_event = threading.Event()
        self._spinner_thread = threading.Thread(target=self._spinner_worker, daemon=True)
        self._spinner_thread.start()

    def _stop_spinner_thread(self):
        if self._spinner_thread and self._spinner_thread.is_alive():
            self._spinner_stop_event.set()
            self._spinner_thread.join()
        self._spinner_thread = None

    def _spinner_worker(self):
        while not self._spinner_stop_event.wait(0.05):
            if not self._should_spin():
                continue
            self._render()

    def _render(self, final: bool = False, advance_spinner: bool = True):
        with ModernProgressBar._lock:
            progress = self.current / self.total if self.total else 0
            bar = self._progress_bar(progress, advance_spinner=advance_spinner and self._should_spin())
            percentage_value = int(round(min(max(progress, 0), 1) * 100))
            percentage = f"{percentage_value:3d}%"
            if self.current == self.total:
                percentage = "DONE"
            percentage_alt = "    "
            if self.spinner_mode:
                if self._should_spin():
                    percentage_alt = "RUNN"
                else:
                    percentage_alt = "WAIT"
            name_width = max(len(bar.process_name) for bar in ModernProgressBar._active_bars) if ModernProgressBar._active_bars else len(self.process_name)
            proc_name = f"{self.process_name:<{name_width}}"
            total_width = max(len(str(bar.total)) for bar in ModernProgressBar._active_bars) if ModernProgressBar._active_bars else max(len(str(self.total)), 1)
            status = ""
            if not (final or (self.spinner_mode and self._spinner_ready)):
                if self.spinner_mode:
                    status = f"{self.box_left}{' ' * total_width}/{' ' * total_width}{self.box_right} "
                else:
                    status = f"{self.box_left}{self.current:>{total_width}}/{self.total}{self.box_right} "
            line = f"{ModernColor.color(self.bar_color)}{'| ' if self.show_bar else ''}{ModernColor.color('reset')}{ModernColor.color(self.box_color)}{self.box_left}{ModernColor.color('reset')}{ModernColor.color('gray')}{bar}{ModernColor.color('reset')}{ModernColor.color(self.box_color)}{self.box_right}{ModernColor.color('reset')} {ModernColor.color(self.primary_color)}{proc_name}{ModernColor.color('reset')} {percentage_alt if self.spinner_mode else percentage} {status}{ModernColor.color(self.primary_color)}|{ModernColor.color('reset')} {self.message}"
            total_move_up = self.log_lines + (len(ModernProgressBar._active_bars) - self.index)
            if total_move_up > 0:
                sys.stdout.write(f"\033[{total_move_up}A")
            sys.stdout.write("\r")
            sys.stdout.write("\033[K")
            sys.stdout.write(line)
            sys.stdout.write("\n")
            down_lines = max(total_move_up - 1, 0)
            if down_lines > 0:
                sys.stdout.write(f"\033[{down_lines}B")
            sys.stdout.flush()

    def _progress_bar(self, progress: int, advance_spinner: bool = True):
        bar_length = 20
        if not self._should_spin():
            empty_bar = "-"
            if self.current == self.total:
                center_bar = ""
            else:
                center_bar = "-"
            filled_bar = "-"
            if self.current <= 0 and not self._spinner_ready:
                return f"{ModernColor.color('gray')}{empty_bar * (bar_length + 1)}"
            filled_length = int(progress * bar_length) + 1
            return f"{ModernColor.color(self.primary_color)}{filled_bar * filled_length}{ModernColor.color(self.secondary_color)}{center_bar}{ModernColor.color('gray')}{empty_bar * (bar_length - filled_length)}"
        else:
            if self.current <= 0 and not self._spinner_ready:
                return f"{ModernColor.color('gray')}{'-' * (bar_length + 1)}"
            spinner_symbol_length = 1
            spinner_end_bar_length = bar_length - self.spinner_step
            spinner_start_bar_length = bar_length - spinner_end_bar_length
            if advance_spinner:
                self.spinner_step = (self.spinner_step + 1) % (bar_length + 1)
            return f"{ModernColor.color('gray')}{'-' * spinner_start_bar_length}{ModernColor.color(self.secondary_color)}{'-' * spinner_symbol_length}{ModernColor.color('gray')}{'-' * spinner_end_bar_length}"

    def _should_spin(self):
        return self.spinner_mode and self._spinner_ready
