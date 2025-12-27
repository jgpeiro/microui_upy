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

