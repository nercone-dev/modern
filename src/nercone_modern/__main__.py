#!/usr/bin/env python3

# -- nercone-modern --------------------------------------------- #
# __main__.py on nercone-modern                                   #
# Made by DiamondGotCat, Licensed under MIT License               #
# Copyright (c) 2025 DiamondGotCat                                #
# ---------------------------------------------- DiamondGotCat -- #

import time
from nercone_modern.logging import ModernLogging
from nercone_modern.progressbar import ModernProgressBar

logger0 = ModernLogging("Demo", display_level="DEBUG", show_proc=False, show_level=False)
show_proc = logger0.prompt("Show process name?", default="N", choices=["y", "N"], interrupt_ignore=True, level_color="magenta") == "y"
show_level = logger0.prompt("Show level name?", default="N", choices=["y", "N"], interrupt_ignore=True, level_color="magenta") == "y"
logger1 = ModernLogging("Main", display_level="DEBUG", show_proc=show_proc, show_level=show_level)
logger2 = ModernLogging("Sub", display_level="DEBUG", show_proc=show_proc, show_level=show_level)

try:
    logger1.log("This is a debug message", "DEBUG")
    logger1.log("This is a info message", "INFO")
    logger1.log("This is a info message", "INFO")
    logger1.log("This is a info message", "INFO")
    logger2.log("This is a info message", "INFO")
    logger1.log("This is a warning message", "WARNING")
    logger1.log("This is a error message", "ERROR")
    logger1.log("This is a critical error message", "CRITICAL")
    prompt_result = logger1.prompt("Continue demo?", default="Y", choices=["Y", "n"], interrupt_ignore=True, interrupt_default="n")
    if prompt_result == "n":
        logger1.log("Exiting demo. See you!", "INFO")
        raise SystemExit(0)

    progress_bar1 = ModernProgressBar(total=100, process_name="Task 1", spinner_mode=False)
    progress_bar1.setMessage("Waiting...")
    progress_bar2 = ModernProgressBar(total=1, process_name="Task 2", spinner_mode=True)
    progress_bar2.setMessage("Waiting...")

    progress_bar1.start()
    progress_bar2.start()

    progress_bar1.setMessage("Running...")
    for i in range(100):
        time.sleep(0.05)
        progress_bar1.update()
    progress_bar1.setMessage("Done!")
    progress_bar1.finish()

    progress_bar2.spin_start()
    progress_bar2.setMessage("Running with Spinner Mode...")
    time.sleep(10)
    progress_bar2.setMessage("Done!")
    progress_bar2.finish()
except KeyboardInterrupt:
    print()
    logger1.log("Aborted.", "INFO")
