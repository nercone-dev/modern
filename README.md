
<img width="1920" alt="nercone_modern" src="https://github.com/user-attachments/assets/58bbaeef-ad81-4105-a5ed-a64d29d91e2c" />

# nercone-modern
Modern CLI Library

## Installation

### uv
**Install to venv and Add to project dependencies:**
```
uv add nercone-modern
```

**Install to venv:**
```
uv pip install nercone-modern
```

### pip
```
pip3 install nercone-modern
```

## Usage

### Import

```python
from nercone_modern.color import ModernColor
from nercone_modern.text import ModernText
from nercone_modern.logging import ModernLogging
from nercone_modern.progressbar import ModernProgressBar
```

### Color
```python
from nercone_modern.color import ModernColor as Color
print(f"Build {Color.GREEN}Success{Color.RESET}")
```

**Supported colors:**
- `CYAN`
- `MAGENTA`
- `YELLOW`
- `GREEN`
- `RED`
- `BLUE`
- `WHITE`
- `BLACK`
- `GRAY`
- `RESET`

### Text
```python
from nercone_modern.text import ModernText as Text
from nercone_modern.color import ModernColor as Color
print("Build" + Text("Success", color="green"))
print("Build" + Text("Failed", color=Color.RED))
```

### Logging
```python
ModernLogging(
  process_name: str = "App",           # Process name to show in the log
  display_level: str = "INFO",         # The minimum level to show in the log
  filepath: str | None = None,         # Log file path
  show_proc: bool | None = None,       # Whether to show process names
  show_level: bool | None = None       # Whether to show level names
)
ModernLogging().log(
  message: str = "",                   # Log contents
  level_text: str = "INFO",            # Level from "DEBUG", "INFO", "WARN", "ERROR" and "CRITICAL"
  level_color: str                     # Custom color for Level (see ModernLogging.color.ModernColor)
)
ModernLogging().prompt(
  message: str = "",                   # Log contents
  level_text: str = "INFO",            # Level from "DEBUG", "INFO", "WARN", "ERROR" and "CRITICAL"
  level_color: str | None = None,      # Custom color for Level (see ModernColor)
  default: str | None = None,          # Default answer
  show_default: bool = False,          # Whether to show default answer
  choices: list[str] | None = None,    # List of possible answers
  show_choices: bool = True,           # Whether to show choices
  interrupt_ignore: bool = False,      # Whether to raise an exception on KeyboardInterrupt or continue using the default argument.
  interrupt_default: str | None = None # Value to use instead of the default argument when interrupt_ignore is True.
)
```

```python
from nercone_modern.logging import ModernLogging
logger = ModernLogging("Main", display_level="DEBUG")
logger.log("This is a test message", level_text="INFO", level_color="magenta")
answer = logger.prompt("What's your name?", level_text="INFO")
logger.log(f"Answer: {answer}", level_text="DEBUG")
answer2 = logger.prompt("Select mode", default="A", choices=["A", "b", "c", "d"], level_text="INFO")
logger.log(f"Mode: {answer2}", level_text="DEBUG")
```

**Supported levels:**
- `DEBUG`
- `INFO`
- `WARN`
- `ERROR`
- `CRITICAL`

### Progress Bar
```python
ModernProgressBar(
  total: int,                          # Total number of steps (max progress value)
  process_name: str,                   # Name of the process shown next to the bar
  spinner_mode: bool = False,          # Whether to start in spinner mode instead of progress (spinner-only) mode
  primary_color: str = "blue",         # Color used for filled bar and brackets (see ModernColor)
  secondary_color: str = "cyan",       # Color used for center marker / spinner (see ModernColor)
  box_left: str = "[",                 # Left bracket surrounding the bar and status
  box_right: str = "]"                 # Right bracket surrounding the bar and status
)
ModernProgressBar().spinner(
  enabled: bool = True                 # Enable or disable spinner mode dynamically
)
ModernProgressBar().spin_start()       # Start spinner animation immediately
ModernProgressBar().setMessage(
  message: str = ""                    # Message to show after the status (e.g. current step description)
)
ModernProgressBar().start()            # Initial rendering and start of spinner (if enabled)
ModernProgressBar().update(
  amount: int = 1                      # Increase current progress by the specified amount and re-render
)
ModernProgressBar().finish()           # Mark as complete, stop spinner and render final DONE state
ModernProgressBar().log(
  message: str = "",                   # Log contents printed above the progress bar
  level_text: str = "INFO",            # Level from "DEBUG", "INFO", "WARN", "ERROR" and "CRITICAL"
  level_color: str | None = None,      # Custom color for Level (see ModernColor)
  show_proc: bool | None = None,       # Whether to show process names (fallbacks to ModernLogging settings)
  show_level: bool | None = None,      # Whether to show level names (fallbacks to ModernLogging settings)
  modernLogging: ModernLogging = None  # Existing ModernLogging instance to reuse. If None, a new one is created.
)
```

```python
from nercone_modern.progressbar import ModernProgressBar
progress_bar = ModernProgressBar(total=100, process_name="Task 1", spinner_mode=True)

progress_bar.start()
time.sleep(5)

progress_bar.spinner(False)

progress_bar.setMessage("Step 1")

for i in range(50):
  time.sleep(0.05)
  progress_bar.update(amount=1)

progress_bar.setMessage("Step 2")

for i in range(25):
  time.sleep(0.03)
  progress_bar.update(amount=1)

progress_bar.setMessage("Step 3")

for i in range(5):
  time.sleep(1)
  progress_bar.update(amount=5)

progress_bar.finish()
```

---

![PyPI - Version](https://img.shields.io/pypi/v/nercone-modern)
