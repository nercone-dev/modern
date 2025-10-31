
<img width="1920" alt="Nercone Modern" src="https://github.com/user-attachments/assets/c92b0407-916f-46ec-9116-c3388b38c88c" />

# nercone-modern
Modern Logging and Progress Bar Library

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
from nercone_modern.logging import ModernLogging
from nercone_modern.progressbar import ModernProgressBar
```

### Logging

```python
logger = ModernLogging("Main", display_level="DEBUG")
logger.log("This is a test message", level="INFO")
answer = logger.prompt("What's your name?", level="INFO")
logger.log(f"Answer: {answer}", level="DEBUG")
```

**Supported levels:**
- `DEBUG`
- `INFO`
- `WARN`
- `ERROR`
- `CRITICAL`

### Progress Bar

```python
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
