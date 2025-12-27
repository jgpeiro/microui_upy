# MicroUI for MicroPython

A port of the microui immediate-mode UI library to MicroPython with hardware support.

## Features

- Immediate-mode UI paradigm
- Lightweight and efficient
- Asyncio support for non-blocking operation
- I2C touch screen support (FT6236/FT6206)
- SPI display support
- Comprehensive unit tests
- Logging support

## Installation

Copy the `microui` directory to your MicroPython device:

```
/microui
    /__init__.py
    /core.py
    /context.py
    /drawing.py
    /layout.py
    /controls.py
    /windows.py
    /hardware.py
```

## Basic Usage

```python
import framebuf
from microui import *

# Create framebuffer
buffer = bytearray(240 * 320 * 2)
fb = framebuf.FrameBuffer(buffer, 240, 320, framebuf.RGB565)

# Text callbacks
def text_width(font, text):
    return len(text) * 8

def text_height(font):
    return 10

# Create context
ctx = Context(text_width, text_height, fb)

# UI loop
def update_ui(ctx):
    begin(ctx)
    
    if begin_window(ctx, "Window", Rect(10, 10, 200, 150)):
        if button(ctx, "Click"):
            print("Clicked!")
        end_window(ctx)
    
    end(ctx)
    render_commands(ctx)

# Run
while True:
    update_ui(ctx)
```

## Hardware Setup

```python
from microui.hardware import setup_hardware, DisplayManager, ui_task
import asyncio

# Configure hardware
i2c_params = {'scl': 22, 'sda': 21}
spi_params = {'sck': 18, 'mosi': 23, 'dc': 2, 'cs': 15, 'rst': 4}

touch, display, fb = setup_hardware(i2c_params, spi_params)

# Create context and display manager
ctx = Context(text_width, text_height, fb)
display_mgr = DisplayManager(display, fb, fps=30)

# Run with asyncio
async def main():
    await asyncio.gather(
        touch.poll_async(ctx),
        display_mgr.run_async(ctx),
        ui_task(ctx, display_mgr, your_ui_function)
    )

asyncio.run(main())
```

## Controls

- `button(ctx, label)` - Button
- `checkbox(ctx, label, state)` - Checkbox
- `slider(ctx, value, min, max)` - Slider
- `label(ctx, text)` - Label
- `text(ctx, text)` - Word-wrapped text
- `begin_treenode(ctx, label)` - Collapsible tree node
- `begin_window(ctx, title, rect)` - Window
- `begin_panel(ctx, name)` - Panel

## Testing

Run unit tests:

```python
from tests.test_microui import run_tests
run_tests()
```

## File Structure

```
microui/
├── __init__.py       - Package exports
├── core.py           - Core data structures
├── context.py        - Context management
├── drawing.py        - Drawing functions
├── layout.py         - Layout system
├── controls.py       - UI controls
├── windows.py        - Windows and panels
└── hardware.py       - Hardware integration

tests/
└── test_microui.py   - Unit tests

example.py            - Usage examples
```

## License

MIT License - See original microui library by rxi

## Credits

Original microui library: https://github.com/rxi/microui
MicroPython port with hardware support and async