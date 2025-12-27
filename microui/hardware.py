# microui/hardware.py
"""
Hardware integration for displays and touch sensors
"""
import asyncio
import logging
from machine import Pin, I2C, SPI
from micropython import const

logger = logging.getLogger(__name__)

# Touch sensor constants
FT6236_ADDR = const(0x38)
FT6236_REG_TOUCH_COUNT = const(0x02)
FT6236_REG_P1_XH = const(0x03)


class I2CTouchScreen:
    """I2C touch screen driver (FT6236/FT6206)"""
    
    def __init__(self, i2c, addr=FT6236_ADDR):
        """
        Initialize touch screen
        
        Args:
            i2c: I2C bus object
            addr: I2C address of touch controller
        """
        self.i2c = i2c
        self.addr = addr
        self.touch_points = []
        logger.info(f"I2C Touch initialized at addr 0x{addr:02x}")
    
    def read_touch(self):
        """
        Read touch points
        
        Returns:
            List of (x, y, pressed) tuples
        """
        try:
            # Read number of touch points
            count_data = self.i2c.readfrom_mem(self.addr, FT6236_REG_TOUCH_COUNT, 1)
            count = count_data[0] & 0x0F
            
            if count == 0:
                return []
            
            # Read touch data (6 bytes per point)
            data = self.i2c.readfrom_mem(self.addr, FT6236_REG_P1_XH, 6 * count)
            
            points = []
            for i in range(count):
                offset = i * 6
                
                # Parse coordinates
                x_high = data[offset] & 0x0F
                x_low = data[offset + 1]
                y_high = data[offset + 2] & 0x0F
                y_low = data[offset + 3]
                
                x = (x_high << 8) | x_low
                y = (y_high << 8) | y_low
                
                # Event type (0 = down, 1 = up, 2 = contact)
                event = (data[offset] >> 6) & 0x03
                pressed = event in (0, 2)
                
                points.append((x, y, pressed))
            
            return points
            
        except Exception as e:
            logger.error(f"Touch read error: {e}")
            return []
    
    async def poll_async(self, ctx, interval_ms=50):
        """
        Async polling loop for touch events
        
        Args:
            ctx: microui context
            interval_ms: Polling interval in milliseconds
        """
        logger.info(f"Starting touch polling (interval={interval_ms}ms)")
        last_pressed = False
        
        while True:
            points = self.read_touch()
            
            if points:
                x, y, pressed = points[0]  # Use first touch point
                
                from .context import input_mousemove, input_mousedown, input_mouseup
                
                if pressed and not last_pressed:
                    input_mousedown(ctx, x, y, 1)
                    logger.debug(f"Touch down: ({x}, {y})")
                elif not pressed and last_pressed:
                    input_mouseup(ctx, x, y, 1)
                    logger.debug(f"Touch up: ({x}, {y})")
                elif pressed:
                    input_mousemove(ctx, x, y)
                
                last_pressed = pressed
            else:
                if last_pressed:
                    # Touch released
                    from .context import input_mouseup
                    input_mouseup(ctx, ctx.mouse_pos.x, ctx.mouse_pos.y, 1)
                    last_pressed = False
            
            await asyncio.sleep_ms(interval_ms)


class SPIDisplay:
    """SPI display driver wrapper"""
    
    def __init__(self, spi, dc, cs, rst=None, width=240, height=320):
        """
        Initialize SPI display
        
        Args:
            spi: SPI bus object
            dc: Data/command pin
            cs: Chip select pin
            rst: Reset pin (optional)
            width: Display width
            height: Display height
        """
        self.spi = spi
        self.dc = Pin(dc, Pin.OUT)
        self.cs = Pin(cs, Pin.OUT)
        self.rst = Pin(rst, Pin.OUT) if rst else None
        self.width = width
        self.height = height
        
        logger.info(f"SPI Display initialized ({width}x{height})")
        
        # Initialize display
        self._init_display()
    
    def _init_display(self):
        """Initialize display (placeholder - implement for specific driver)"""
        if self.rst:
            self.rst.value(0)
            asyncio.sleep_ms(100)
            self.rst.value(1)
            asyncio.sleep_ms(100)
        
        logger.debug("Display initialized")
    
    def _write_cmd(self, cmd):
        """Write command byte"""
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(bytes([cmd]))
        self.cs.value(1)
    
    def _write_data(self, data):
        """Write data bytes"""
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(data)
        self.cs.value(1)
    
    def set_window(self, x0, y0, x1, y1):
        """Set drawing window (implement for specific driver)"""
        pass
    
    def write_pixels(self, data):
        """Write pixel data"""
        self._write_data(data)
    
    async def update_async(self, framebuffer):
        """
        Async update display from framebuffer
        
        Args:
            framebuffer: FrameBuffer object
        """
        # Convert framebuffer to display format and write
        # This is a placeholder - implement for specific display
        logger.debug("Display update")
        await asyncio.sleep_ms(1)


class DisplayManager:
    """Manages display updates with async support"""
    
    def __init__(self, display, framebuffer, fps=30):
        """
        Initialize display manager
        
        Args:
            display: Display driver object
            framebuffer: FrameBuffer object
            fps: Target frames per second
        """
        self.display = display
        self.framebuffer = framebuffer
        self.fps = fps
        self.frame_time_ms = 1000 // fps
        self.dirty = True
        
        logger.info(f"Display manager initialized (fps={fps})")
    
    def mark_dirty(self):
        """Mark display as needing update"""
        self.dirty = True
    
    async def run_async(self, ctx):
        """
        Async display update loop
        
        Args:
            ctx: microui context
        """
        logger.info("Starting display update loop")
        
        while True:
            start = asyncio.ticks_ms()
            
            if self.dirty:
                # Render UI commands to framebuffer
                from .drawing import render_commands
                render_commands(ctx)
                
                # Update display
                if hasattr(self.display, 'update_async'):
                    await self.display.update_async(self.framebuffer)
                
                self.dirty = False
            
            # Maintain frame rate
            elapsed = asyncio.ticks_diff(asyncio.ticks_ms(), start)
            delay = max(1, self.frame_time_ms - elapsed)
            await asyncio.sleep_ms(delay)


async def ui_task(ctx, display_mgr, update_fn):
    """
    Main UI task
    
    Args:
        ctx: microui context
        display_mgr: DisplayManager instance
        update_fn: Function that builds the UI each frame
    """
    logger.info("Starting UI task")
    
    while True:
        from .context import begin, end
        
        # Begin frame
        begin(ctx)
        
        # Call user update function
        update_fn(ctx)
        
        # End frame
        end(ctx)
        
        # Mark display for update
        display_mgr.mark_dirty()
        
        # Yield to other tasks
        await asyncio.sleep_ms(10)


def setup_hardware(i2c_params=None, spi_params=None, display_size=(240, 320)):
    """
    Setup hardware with default parameters
    
    Args:
        i2c_params: Dict with I2C parameters (scl, sda, freq)
        spi_params: Dict with SPI parameters (sck, mosi, miso, dc, cs, rst)
        display_size: Tuple of (width, height)
    
    Returns:
        Tuple of (touch_screen, display, framebuffer)
    """
    import framebuf
    
    touch = None
    display = None
    
    # Setup I2C touch
    if i2c_params:
        i2c = I2C(
            i2c_params.get('id', 0),
            scl=Pin(i2c_params['scl']),
            sda=Pin(i2c_params['sda']),
            freq=i2c_params.get('freq', 400000)
        )
        touch = I2CTouchScreen(i2c)
    
    # Setup SPI display
    if spi_params:
        spi = SPI(
            spi_params.get('id', 1),
            baudrate=spi_params.get('baudrate', 40000000),
            polarity=0,
            phase=0,
            sck=Pin(spi_params['sck']),
            mosi=Pin(spi_params['mosi']),
            miso=Pin(spi_params.get('miso')) if 'miso' in spi_params else None
        )
        
        display = SPIDisplay(
            spi,
            spi_params['dc'],
            spi_params['cs'],
            spi_params.get('rst'),
            display_size[0],
            display_size[1]
        )
    
    # Create framebuffer
    buffer = bytearray(display_size[0] * display_size[1] * 2)  # RGB565
    fb = framebuf.FrameBuffer(buffer, display_size[0], display_size[1], 
                               framebuf.RGB565)
    
    logger.info("Hardware setup complete")
    return touch, display, fb
