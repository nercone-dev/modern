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
from nercone_modern import NerconeModern
```

### Logging

```python
logger = NerconeModern().modernLogging(process_name="Main")
logger.log("This is a test message", level="INFO")
```

### Progress Bar

```python
progress_bar = NerconeModern().modernProgressBar(total=100, process_name="Task 1", process_color=32, spinner_mode=True)
progress_bar.start()

time.sleep(5)

progress_bar.spinner(False)

for i in range(100):
  time.sleep(0.05)
  progress_bar.update()

progress_bar.finish()
```
