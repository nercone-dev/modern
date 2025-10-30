
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

```python
from nercone_modern.logging import ModernLogging
from nercone_modern.progressbar import ModernProgressBar
```

### Logging

```python
logger = ModernLogging("Main", display_level="DEBUG")
logger.log("This is a test message", level="INFO")
```

### Progress Bar

```python
progress_bar = ModernProgressBar(total=100, process_name="Task 1", spinner_mode=True)
progress_bar.start()

time.sleep(5)

progress_bar.spinner(False)

for i in range(100):
  time.sleep(0.05)
  progress_bar.update()

progress_bar.finish()
```
