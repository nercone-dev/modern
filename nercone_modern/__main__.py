from nercone_modern import NerconeModern

if __name__ == "__main__":
    import time

    logger = NerconeModern().modernLogging("Main")
    logger.log("This is a debug message", "DEBUG")
    logger.log("This is a test message", "INFO")
    logger.log("This is a warning message", "WARNING")
    logger.log("This is an error message", "ERROR")
    logger.log("This is an error message", "CRITICAL")

    progress_bar1 = NerconeModern().modernProgressBar(total=100, process_name="Task 1", process_color=32, spinner_mode=False)
    progress_bar1.setMessage("WAITING")
    progress_bar2 = NerconeModern().modernProgressBar(total=200, process_name="Task 2", process_color=34, spinner_mode=True)
    progress_bar2.setMessage("WAITING")

    progress_bar1.start()
    progress_bar2.start()

    progress_bar1.setMessage("RUNNING")
    for i in range(100):
        time.sleep(0.05)
        progress_bar1.update()
    progress_bar1.setMessage("DONE")
    progress_bar1.finish()

    progress_bar2.spin_start()
    progress_bar2.setMessage("RUNNING (BACKGROUND)")
    for i in range(100):
        time.sleep(0.05)
        progress_bar2.update(2)
    progress_bar2.setMessage("DONE")
    progress_bar2.finish()
