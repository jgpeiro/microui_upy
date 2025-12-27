# microui/__init__.py
"""
MicroPython port of microui library
A tiny immediate-mode UI library
"""
from .core import *
from .context import *
from .drawing import *
from .layout import *
from .controls import *
from .windows import *

__version__ = MU_VERSION
__all__ = [
    # Core
    'Context', 'Vec2', 'Rect', 'Color', 'Style',
    
    # Constants
    'MU_CLIP_PART', 'MU_CLIP_ALL',
    'MU_COLOR_TEXT', 'MU_COLOR_BORDER', 'MU_COLOR_WINDOWBG',
    'MU_COLOR_TITLEBG', 'MU_COLOR_TITLETEXT', 'MU_COLOR_PANELBG',
    'MU_COLOR_BUTTON', 'MU_COLOR_BUTTONHOVER', 'MU_COLOR_BUTTONFOCUS',
    'MU_COLOR_BASE', 'MU_COLOR_BASEHOVER', 'MU_COLOR_BASEFOCUS',
    'MU_COLOR_SCROLLBASE', 'MU_COLOR_SCROLLTHUMB',
    'MU_ICON_CLOSE', 'MU_ICON_CHECK', 'MU_ICON_COLLAPSED', 'MU_ICON_EXPANDED',
    'MU_RES_ACTIVE', 'MU_RES_SUBMIT', 'MU_RES_CHANGE',
    'MU_OPT_ALIGNCENTER', 'MU_OPT_ALIGNRIGHT', 'MU_OPT_NOINTERACT',
    'MU_OPT_NOFRAME', 'MU_OPT_NORESIZE', 'MU_OPT_NOSCROLL',
    'MU_OPT_NOCLOSE', 'MU_OPT_NOTITLE', 'MU_OPT_HOLDFOCUS',
    'MU_OPT_AUTOSIZE', 'MU_OPT_POPUP', 'MU_OPT_CLOSED', 'MU_OPT_EXPANDED',
    'MU_MOUSE_LEFT', 'MU_MOUSE_RIGHT', 'MU_MOUSE_MIDDLE',
    'MU_KEY_SHIFT', 'MU_KEY_CTRL', 'MU_KEY_ALT', 'MU_KEY_BACKSPACE', 'MU_KEY_RETURN',
    
    # Context functions
    'begin', 'end', 'set_focus', 'get_id', 'push_id', 'pop_id',
    'push_clip_rect', 'pop_clip_rect', 'get_clip_rect',
    'get_current_container', 'get_container', 'bring_to_front',
    'input_mousemove', 'input_mousedown', 'input_mouseup',
    'input_scroll', 'input_keydown', 'input_keyup', 'input_text',
    
    # Drawing functions
    'push_command', 'set_clip', 'draw_rect', 'draw_box',
    'draw_text', 'draw_icon', 'draw_frame', 'render_commands',
    
    # Layout functions
    'layout_row', 'layout_width', 'layout_height',
    'layout_begin_column', 'layout_end_column',
    'layout_set_next', 'layout_next',
    
    # Controls
    'text', 'label', 'button', 'button_ex', 'checkbox',
    'slider', 'slider_ex', 'header', 'header_ex',
    'begin_treenode', 'begin_treenode_ex', 'end_treenode',
    
    # Windows
    'begin_window', 'begin_window_ex', 'end_window',
    'open_popup', 'begin_popup', 'end_popup',
    'begin_panel', 'begin_panel_ex', 'end_panel',
]


# example.py
"""
Example usage of microui for MicroPython
"""
import asyncio
import framebuf
import logging
from microui import *
from microui.hardware import setup_hardware, DisplayManager, ui_task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Mock hardware setup for testing
def create_mock_framebuffer(width=240, height=320):
    """Create mock framebuffer for testing"""
    buffer = bytearray(width * height * 2)
    return framebuf.FrameBuffer(buffer, width, height, framebuf.RGB565)


# Text measurement functions
def text_width(font, text):
    """Calculate text width (8px per char)"""
    return len(text) * 8


def text_height(font):
    """Get text height"""
    return 10


# UI state
ui_state = {
    'checkbox1': False,
    'checkbox2': True,
    'slider_value': 50.0,
    'counter': 0,
}


def update_ui(ctx):
    """Main UI update function"""
    global ui_state
    
    # Main window
    if begin_window(ctx, "Demo Window", Rect(10, 10, 220, 300)):
        
        # Title
        text(ctx, "MicroUI Demo")
        
        # Button
        layout_row(ctx, 1, [-1], 0)
        if button(ctx, "Click Me"):
            ui_state['counter'] += 1
            logger.info(f"Button clicked! Count: {ui_state['counter']}")
        
        # Counter display
        label(ctx, f"Clicks: {ui_state['counter']}")
        
        # Checkboxes
        layout_row(ctx, 1, [-1], 0)
        res, ui_state['checkbox1'] = checkbox(ctx, "Option 1", ui_state['checkbox1'])
        if res & MU_RES_CHANGE:
            logger.info(f"Checkbox 1: {ui_state['checkbox1']}")
        
        res, ui_state['checkbox2'] = checkbox(ctx, "Option 2", ui_state['checkbox2'])
        if res & MU_RES_CHANGE:
            logger.info(f"Checkbox 2: {ui_state['checkbox2']}")
        
        # Slider
        layout_row(ctx, 1, [-1], 0)
        label(ctx, "Volume:")
        res, ui_state['slider_value'] = slider(ctx, ui_state['slider_value'], 0.0, 100.0)
        if res & MU_RES_CHANGE:
            logger.info(f"Slider: {ui_state['slider_value']:.1f}")
        
        # Tree node
        layout_row(ctx, 1, [-1], 0)
        if begin_treenode(ctx, "Advanced Options"):
            label(ctx, "Option A")
            label(ctx, "Option B")
            label(ctx, "Option C")
            end_treenode(ctx)
        
        # Panel
        layout_row(ctx, 1, [-1], 100)
        begin_panel(ctx, "Info Panel")
        label(ctx, "Status: Running")
        label(ctx, f"Frame: {ctx.frame}")
        end_panel(ctx)
        
        end_window(ctx)


async def main():
    """Main async entry point"""
    logger.info("Starting microui example")
    
    # Create framebuffer
    fb = create_mock_framebuffer()
    
    # Create context
    ctx = Context(text_width, text_height, fb)
    logger.info("Context created")
    
    # Create display manager (mock)
    class MockDisplay:
        async def update_async(self, fb):
            await asyncio.sleep_ms(1)
    
    display = MockDisplay()
    display_mgr = DisplayManager(display, fb, fps=30)
    
    # Create tasks
    ui_coroutine = ui_task(ctx, display_mgr, update_ui)
    display_coroutine = display_mgr.run_async(ctx)
    
    # Run tasks
    await asyncio.gather(ui_coroutine, display_coroutine)


# Hardware example
def hardware_example():
    """
    Example with real hardware
    
    Hardware connections:
    - I2C Touch: SCL=22, SDA=21
    - SPI Display: SCK=18, MOSI=23, DC=2, CS=15, RST=4
    """
    import asyncio
    from microui.hardware import setup_hardware, DisplayManager, ui_task
    
    # Setup hardware
    i2c_params = {'scl': 22, 'sda': 21, 'freq': 400000}
    spi_params = {
        'sck': 18, 'mosi': 23, 'dc': 2, 'cs': 15, 'rst': 4,
        'baudrate': 40000000
    }
    
    touch, display, fb = setup_hardware(i2c_params, spi_params, (240, 320))
    
    # Create context
    ctx = Context(text_width, text_height, fb)
    
    # Create display manager
    display_mgr = DisplayManager(display, fb, fps=30)
    
    # Create tasks
    async def run_all():
        await asyncio.gather(
            touch.poll_async(ctx, interval_ms=50),
            display_mgr.run_async(ctx),
            ui_task(ctx, display_mgr, update_ui)
        )
    
    # Run
    asyncio.run(run_all())


if __name__ == '__main__':
    # Run mock example
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped by user")


# README.md content
README = """
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
"""
