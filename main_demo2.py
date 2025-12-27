# calculator_demo.py
"""
Calculator application using microui with ILI9341 display and FT6x36 touch
"""
import asyncio
import logging
from machine import I2C, SPI, Pin
import framebuf

"""SPI LCD display driver for ILI9341 with RGB565 framebuffer."""
import time
import framebuf
import logging

logger = logging.getLogger("ili9341")


class Ili9341v:
    """ILI9341 display driver compatible with Display interface."""
    
    # Display dimensions
    WIDTH = 240
    HEIGHT = 320

    # Commands
    CASET = 0x2A
    RASET = 0x2B
    RAMWR = 0x2C
    
    X_OFFSET = 0
    Y_OFFSET = 0
    
    def __init__(self, spi, dc, cs, rst, bl=None, rotation=1, width=None, height=None):
        """
        Initialize ILI9341 display.
        
        Args:
            spi: SPI bus instance
            dc: Data/Command pin
            cs: Chip Select pin
            rst: Reset pin
            bl: Backlight pin (optional)
            rotation: Display rotation (0-3)
            width: Override width (for compatibility)
            height: Override height (for compatibility)
        """
        logger.debug("Initializing ILI9341 display driver...")
        
        self.spi = spi
        self.dc = dc
        self.cs = cs
        self.rst = rst
        self.bl = bl
        
        # Work buffers
        self.buf1 = bytearray(1)
        self.buf4 = bytearray(4)
        
        # Set initial dimensions
        self.width = width or self.WIDTH
        self.height = height or self.HEIGHT
        
        # Hardware initialization
        self._reset()
        self._config()
        self.set_rotation(rotation)
        
        # Create framebuffer after rotation is set
        self.buffer = bytearray(self.width * self.height * 2)  # RGB565
        self.fb = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.RGB565)
        
        # Clear and enable backlight
        self.clear()
        self.show()
        if self.bl:
            self.bl.value(1)
            print("bl ON")
            
        logger.info(f"Display initialized: {self.width}x{self.height} RGB565")
    
    def _reset(self):
        """Perform hardware reset sequence."""
        logger.debug("Performing hardware reset...")
        
        if not self.rst:
            return
        
        self.rst.value(1)
        time.sleep_ms(50)
        
        self.rst.value(0)
        time.sleep_ms(100)
        
        self.rst.value(1)
        time.sleep_ms(50)
        
        self.cs.value(1)
        self.dc.value(0)
        
        logger.debug("Hardware reset complete")
    
    def _write_cmd(self, cmd):
        """Write command byte to LCD."""
        self.buf1[0] = cmd
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(self.buf1)
        self.cs.value(1)
    
    def _write_data(self, data):
        """Write data to LCD."""
        if data is None or len(data) == 0:
            return
            
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(data)
        self.cs.value(1)
    
    def _write_reg(self, cmd, data=None):
        """Write register (command + optional data)."""
        self._write_cmd(cmd)
        if data is not None:
            self._write_data(data)
    
    def _config(self):
        """Configure display registers (ILI9341 initialization)."""
        logger.debug("Configuring display registers...")
        
        # Power control sequences
        self._write_reg(0xCF, b"\x00\xC1\x30")
        self._write_reg(0xED, b"\x64\x03\x12\x81")
        self._write_reg(0xE8, b"\x85\x00\x78")
        self._write_reg(0xCB, b"\x39\x2C\x00\x34\x02")
        self._write_reg(0xF7, b"\x20")
        self._write_reg(0xEA, b"\x00\x00")
        
        # Power control
        self._write_reg(0xC0, b"\x13")       # VRH[5:0]
        self._write_reg(0xC1, b"\x13")       # SAP[2:0];BT[3:0]
        self._write_reg(0xC5, b"\x22\x35")   # VCM control
        self._write_reg(0xC7, b"\xBD")       # VCM control2
        
        # Display inversion
        self._write_reg(0x21)                # Display Inversion ON
        
        # Memory Access Control (will be set by rotation)
        self._write_reg(0x36, b"\x08")
        
        # Display Function Control
        self._write_reg(0xB6, b"\x0A\xA2")
        
        # Pixel Format Set (16bit RGB565)
        self._write_reg(0x3A, b"\x55")
        
        # Interface Control & Frame Rate
        self._write_reg(0xF6, b"\x01\x30")
        self._write_reg(0xB1, b"\x00\x1B")
        
        # Gamma configuration
        self._write_reg(0xF2, b"\x00")       # 3Gamma Function Disable
        self._write_reg(0x26, b"\x01")       # Gamma curve selected
        
        # Positive Gamma Correction
        self._write_reg(0xE0, b"\x0F\x35\x31\x0B\x0E\x06\x49\xA7\x33\x07\x0F\x03\x0C\x0A\x00")
        
        # Negative Gamma Correction
        self._write_reg(0xE1, b"\x00\x0A\x0F\x04\x11\x08\x36\x58\x4D\x07\x10\x0C\x32\x34\x0F")
        
        # Sleep out and display on
        self._write_reg(0x11)                # Exit Sleep
        time.sleep_ms(120)
        
        self._write_reg(0x29)                # Display on
        
        logger.debug("Display configuration complete")
    
    def set_rotation(self, rotation):
        """
        Set display rotation.
        
        Args:
            rotation: 0-3 for different orientations
                0: Portrait
                1: Landscape
                2: Portrait inverted
                3: Landscape inverted
        """
        rotation = rotation % 4
        
        # BGR bit is always set (0x08)
        val = 0x08
        
        if rotation == 0:     # Portrait
            self.width = self.WIDTH
            self.height = self.HEIGHT
            # BGR only
            
        elif rotation == 1:   # Landscape
            self.width = self.HEIGHT
            self.height = self.WIDTH
            # BGR | MX | MV
            val |= (1 << 6) | (1 << 5)
            
        elif rotation == 2:   # Portrait inverted
            self.width = self.WIDTH
            self.height = self.HEIGHT
            # BGR | MX | MY
            val |= (1 << 6) | (1 << 7)
            
        elif rotation == 3:   # Landscape inverted
            self.width = self.HEIGHT
            self.height = self.WIDTH
            # BGR | MY | MV
            val |= (1 << 7) | (1 << 5)
        
        self._write_reg(0x36, bytes([val]))
    
    def _set_window(self, x, y, w, h):
        """Set drawing window."""
        x0 = x + self.X_OFFSET
        y0 = y + self.Y_OFFSET
        x1 = x0 + w - 1
        y1 = y0 + h - 1
        
        # Column Address Set
        self.buf4[0] = x0 >> 8
        self.buf4[1] = x0 & 0xFF
        self.buf4[2] = x1 >> 8
        self.buf4[3] = x1 & 0xFF
        self._write_reg(self.CASET, self.buf4)
        
        # Row Address Set
        self.buf4[0] = y0 >> 8
        self.buf4[1] = y0 & 0xFF
        self.buf4[2] = y1 >> 8
        self.buf4[3] = y1 & 0xFF
        self._write_reg(self.RASET, self.buf4)
    
    def show(self):
        """Transfer framebuffer to display."""
        self._set_window(0, 0, self.width, self.height)
        self._write_cmd(self.RAMWR)
        self._write_data(self.buffer)
        logger.debug("Display updated")
    
    def clear(self, color=0x0000):
        """Clear framebuffer to specified color."""
        self.fb.fill(color)
    
    def get_framebuffer(self):
        """Get framebuffer for direct rendering."""
        return self.fb
    
    # Legacy compatibility methods
    def draw(self, x, y, w, h, buf):
        """
        Draw raw buffer to display (legacy method).
        For direct hardware access without framebuffer.
        """
        self._set_window(x, y, w, h)
        self._write_reg(self.RAMWR, buf)

"""Touch input handling via I2C FT6x36 controller."""
import time
import asyncio
import logging

logger = logging.getLogger("ft6x36")


class Ft6x36:
    """FT6x36 touch screen controller interface."""
    
    SLAVE_ADDR = 0x38
    STATUS_REG = 0x02
    P1_XH_REG = 0x03
    
    def __init__(self, i2c, address=None, ax=1, bx=0, ay=1, by=0, swap_xy=False):
        """
        Initialize FT6x36 touch controller.
        
        Args:
            i2c: I2C bus instance
            address: I2C address (default: 0x38)
            ax, bx: X-axis calibration (x_final = ax * x_raw + bx)
            ay, by: Y-axis calibration (y_final = ay * y_raw + by)
            swap_xy: Swap X and Y coordinates before calibration
            
        For portrait mode (240x320):
            swap_xy=False, adjust ax, bx, ay, by as needed
            
        For landscape mode (320x240):
            swap_xy=True may be needed depending on orientation
        """
        logger.debug("Initializing FT6x36 touch controller...")
        
        self.i2c = i2c
        self.address = address or self.SLAVE_ADDR
        
        # Calibration parameters
        self.ax = ax
        self.bx = bx
        self.ay = ay
        self.by = by
        self.swap_xy = swap_xy
        
        # Current touch state
        self.x = 0
        self.y = 0
        self.pressed = False
        
        # Read buffers
        self.read_buffer1 = bytearray(1)
        self.read_buffer4 = bytearray(4)
        
        logger.info(f"FT6x36 initialized: addr=0x{self.address:02X}, swap_xy={swap_xy}")
        logger.debug(f"Calibration: ax={ax}, bx={bx}, ay={ay}, by={by}")
    
    def read(self):
        """
        Read touch data from sensor.
        
        Returns:
            tuple: (touch_count, x, y)
                - touch_count: 1 if touched, 0 otherwise
                - x, y: Calibrated coordinates
        """
        try:
            # Read touch status
            self.i2c.readfrom_mem_into(self.address, self.STATUS_REG, self.read_buffer1)
            points = self.read_buffer1[0] & 0x0F
            
            if points == 1:
                # Add small delay to avoid glitches
                time.sleep_ms(1)
                
                # Read again to confirm
                self.i2c.readfrom_mem_into(self.address, self.STATUS_REG, self.read_buffer1)
                points = self.read_buffer1[0] & 0x0F
                
                if points == 1:
                    # Read touch coordinates
                    self.i2c.readfrom_mem_into(self.address, self.P1_XH_REG, self.read_buffer4)
                    
                    # Parse coordinates (12-bit values)
                    x = ((self.read_buffer4[0] & 0x0F) << 8) | self.read_buffer4[1]
                    y = ((self.read_buffer4[2] & 0x0F) << 8) | self.read_buffer4[3]
                    
                    # Swap if needed
                    if self.swap_xy:
                        x, y = y, x
                    
                    # Apply calibration
                    x = int(self.ax * x + self.bx)
                    y = int(self.ay * y + self.by)
                    
                    # Update state
                    self.x = x
                    self.y = y
                    self.pressed = True
                    
                    return 1, x, y
            
            # No touch detected
            self.pressed = False
            return 0, 0, 0
            
        except OSError as e:
            logger.error(f"Touch read error: {e}")
            self.pressed = False
            return 0, 0, 0
    
    def get_touch(self):
        """
        Get current touch state without polling.
        
        Returns:
            tuple: (x, y, pressed)
        """
        return self.x, self.y, self.pressed
    
    def is_pressed(self):
        """Check if screen is currently being touched."""
        return self.pressed

# Import microui
from microui import *
from microui.core import Context, Rect, Color, Vec2
from microui.controls import draw_control_frame, draw_control_text, update_control
from microui.context import get_id, push_clip_rect, pop_clip_rect
from microui.drawing import draw_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pin definitions
PIN_LCD_CS = 10
PIN_LCD_DC = 46
PIN_LCD_BL = 45
PIN_LCD_CLK = 12
PIN_LCD_MOSI = 11
PIN_LCD_MISO = 13
PIN_TOUCH_SDA = 16
PIN_TOUCH_SCL = 15

# Display size
LCD_WIDTH = 320
LCD_HEIGHT = 240


class Calculator:
    """Calculator state and logic"""
    
    def __init__(self):
        self.display = "0"
        self.value = 0.0
        self.operation = None
        self.new_number = True
        self.memory = 0.0
        self.error = False
        
    def clear(self):
        """Clear calculator"""
        self.display = "0"
        self.value = 0.0
        self.operation = None
        self.new_number = True
        self.error = False
        
    def clear_entry(self):
        """Clear current entry"""
        self.display = "0"
        self.new_number = True
        
    def append_digit(self, digit):
        """Append digit to display"""
        if self.error:
            self.clear()
            
        if self.new_number:
            self.display = str(digit)
            self.new_number = False
        else:
            if len(self.display) < 12:  # Limit display length
                if self.display == "0":
                    self.display = str(digit)
                else:
                    self.display += str(digit)
    
    def append_decimal(self):
        """Append decimal point"""
        if self.error:
            self.clear()
            
        if self.new_number:
            self.display = "0."
            self.new_number = False
        elif "." not in self.display:
            self.display += "."
    
    def append_zero(self):
        """Append zero"""
        if self.error:
            self.clear()
            
        if self.new_number:
            self.display = "0"
            self.new_number = False
        elif self.display != "0" and len(self.display) < 12:
            self.display += "0"
    
    def negate(self):
        """Toggle sign"""
        if self.error:
            return
            
        try:
            val = float(self.display)
            val = -val
            self.display = self._format_number(val)
        except:
            pass
    
    def percent(self):
        """Convert to percentage"""
        if self.error:
            return
            
        try:
            val = float(self.display)
            val = val / 100.0
            self.display = self._format_number(val)
        except:
            pass
    
    def set_operation(self, op):
        """Set operation (+, -, *, /)"""
        if self.error:
            self.clear()
            
        try:
            if self.operation and not self.new_number:
                self.calculate()
            
            self.value = float(self.display)
            self.operation = op
            self.new_number = True
        except:
            self.display = "Error"
            self.error = True
    
    def calculate(self):
        """Perform calculation"""
        if self.error:
            return
            
        try:
            current = float(self.display)
            
            if self.operation == "+":
                result = self.value + current
            elif self.operation == "-":
                result = self.value - current
            elif self.operation == "*":
                result = self.value * current
            elif self.operation == "/":
                if current == 0:
                    self.display = "Error"
                    self.error = True
                    return
                result = self.value / current
            else:
                result = current
            
            self.display = self._format_number(result)
            self.value = result
            self.operation = None
            self.new_number = True
            
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            self.display = "Error"
            self.error = True
    
    def _format_number(self, num):
        """Format number for display"""
        # Handle scientific notation for very large/small numbers
        if abs(num) > 999999999 or (abs(num) < 0.00001 and num != 0):
            return f"{num:.6e}"
        
        # Format with appropriate precision
        if num == int(num):
            result = str(int(num))
        else:
            result = f"{num:.8f}".rstrip('0').rstrip('.')
        
        # Limit length
        if len(result) > 12:
            result = f"{num:.6e}"
        
        return result
    
    def get_display(self):
        """Get display string"""
        return self.display


# Text measurement functions
def text_width(font, text):
    """Calculate text width (8px per char for default font)"""
    return len(text) * 8


def text_height(font):
    """Get text height"""
    return 8


class TouchHandler:
    """Handle touch input for microui"""
    
    def __init__(self, touch_sensor, ctx):
        self.touch = touch_sensor
        self.ctx = ctx
        self.last_pressed = False
        self.debounce_time = 100  # ms
        self.last_touch_time = 0
        
    async def poll(self):
        """Poll touch sensor and update microui context"""
        while True:
            count, x, y = self.touch.read()
            current_time = time.ticks_ms()
            
            if count > 0:
                # Touch detected
                if not self.last_pressed:
                    # New touch
                    if asyncio.ticks_diff(current_time, self.last_touch_time) > self.debounce_time:
                        input_mousedown(self.ctx, x, y, MU_MOUSE_LEFT)
                        self.last_pressed = True
                        self.last_touch_time = current_time
                        logger.debug(f"Touch down: ({x}, {y})")
                else:
                    # Drag
                    input_mousemove(self.ctx, x, y)
            else:
                # No touch
                if self.last_pressed:
                    # Touch released
                    x, y, _ = self.touch.get_touch()
                    input_mouseup(self.ctx, x, y, MU_MOUSE_LEFT)
                    self.last_pressed = False
                    logger.debug(f"Touch up")
            
            await asyncio.sleep_ms(20)  # 50Hz polling


def draw_calculator_ui(ctx, calc):
    """Draw calculator UI"""
    
    # Main window (fullscreen)
    if begin_window_ex(ctx, "Calculator", Rect(0, 0, LCD_WIDTH, LCD_HEIGHT), 
                       MU_OPT_NOTITLE | MU_OPT_NOCLOSE | MU_OPT_NORESIZE | MU_OPT_NOSCROLL):
        
        # Display area
        layout_row(ctx, 1, [-1], 50)
        
        # Custom display with larger text
        r = layout_next(ctx)
        draw_control_frame(ctx, get_id(ctx, "display"), r, MU_COLOR_BASE, 0)
        
        # Draw display text (right-aligned)
        display_text = calc.get_display()
        text_w = text_width(None, display_text) * 2  # Scale up
        
        from microui.context import push_clip_rect, pop_clip_rect
        push_clip_rect(ctx, r)
        
        # Draw larger text by drawing multiple times with offset
        pos_x = r.x + r.w - text_w // 2 - 10
        pos_y = r.y + (r.h - 16) // 2
        
        for dy in range(0, 2):
            for dx in range(0, 2):
                draw_text(ctx, None, display_text, 
                         Vec2(pos_x + dx, pos_y + dy),
                         ctx.style.colors[MU_COLOR_TEXT])
        
        pop_clip_rect(ctx)
        
        # Button layout
        button_height = 35
        button_spacing = 2
        
        # Row 1: C, CE, %, /
        layout_row(ctx, 4, [75, 75, 75, 75], button_height)
        if button_ex(ctx, "C", 0, MU_OPT_ALIGNCENTER):
            calc.clear()
        if button_ex(ctx, "CE", 0, MU_OPT_ALIGNCENTER):
            calc.clear_entry()
        if button_ex(ctx, "%", 0, MU_OPT_ALIGNCENTER):
            calc.percent()
        if button_ex(ctx, "/", 0, MU_OPT_ALIGNCENTER):
            calc.set_operation("/")
        
        # Row 2: 7, 8, 9, *
        layout_row(ctx, 4, [75, 75, 75, 75], button_height)
        if button_ex(ctx, "7", 0, MU_OPT_ALIGNCENTER):
            calc.append_digit(7)
        if button_ex(ctx, "8", 0, MU_OPT_ALIGNCENTER):
            calc.append_digit(8)
        if button_ex(ctx, "9", 0, MU_OPT_ALIGNCENTER):
            calc.append_digit(9)
        if button_ex(ctx, "*", 0, MU_OPT_ALIGNCENTER):
            calc.set_operation("*")
        
        # Row 3: 4, 5, 6, -
        layout_row(ctx, 4, [75, 75, 75, 75], button_height)
        if button_ex(ctx, "4", 0, MU_OPT_ALIGNCENTER):
            calc.append_digit(4)
        if button_ex(ctx, "5", 0, MU_OPT_ALIGNCENTER):
            calc.append_digit(5)
        if button_ex(ctx, "6", 0, MU_OPT_ALIGNCENTER):
            calc.append_digit(6)
        if button_ex(ctx, "-", 0, MU_OPT_ALIGNCENTER):
            calc.set_operation("-")
        
        # Row 4: 1, 2, 3, +
        layout_row(ctx, 4, [75, 75, 75, 75], button_height)
        if button_ex(ctx, "1", 0, MU_OPT_ALIGNCENTER):
            calc.append_digit(1)
        if button_ex(ctx, "2", 0, MU_OPT_ALIGNCENTER):
            calc.append_digit(2)
        if button_ex(ctx, "3", 0, MU_OPT_ALIGNCENTER):
            calc.append_digit(3)
        if button_ex(ctx, "+", 0, MU_OPT_ALIGNCENTER):
            calc.set_operation("+")
        
        # Row 5: +/-, 0, ., =
        layout_row(ctx, 4, [75, 75, 75, 75], button_height)
        if button_ex(ctx, "+/-", 0, MU_OPT_ALIGNCENTER):
            calc.negate()
        if button_ex(ctx, "0", 0, MU_OPT_ALIGNCENTER):
            calc.append_zero()
        if button_ex(ctx, ".", 0, MU_OPT_ALIGNCENTER):
            calc.append_decimal()
        
        # Make equals button stand out
        r = layout_next(ctx)
        id_equals = get_id(ctx, "=")
        update_control(ctx, id_equals, r, 0)
        
        if ctx.mouse_pressed == MU_MOUSE_LEFT and ctx.focus == id_equals:
            calc.calculate()
        
        # Draw equals with different color
        draw_control_frame(ctx, id_equals, r, MU_COLOR_BUTTONFOCUS, 0)
        draw_control_text(ctx, "=", r, MU_COLOR_TEXT, MU_OPT_ALIGNCENTER)
        
        end_window(ctx)


async def ui_task(ctx, calc):
    """Main UI update task"""
    frame_time = 1000 // 30  # 30 FPS
    
    while True:
        print("ticks")
        start = time.ticks_ms()
        
        # Begin frame
        begin(ctx)
        
        # Draw UI
        draw_calculator_ui(ctx, calc)
        
        # End frame
        end(ctx)
        
        # Calculate frame time
        elapsed = asyncio.ticks_diff(time.ticks_ms(), start)
        delay = max(1, frame_time - elapsed)
        
        await asyncio.sleep_ms(delay)


async def display_task(ctx, display):
    """Display update task"""
    frame_time = 1000 // 30  # 30 FPS
    
    while True:
        start = time.ticks_ms()
        
        # Render commands to framebuffer
        render_commands(ctx)
        
        # Update display
        display.show()
        
        # Calculate frame time
        elapsed = asyncio.ticks_diff(time.ticks_ms(), start)
        delay = max(1, frame_time - elapsed)
        
        await asyncio.sleep_ms(delay)


def setup_hardware():
    """Initialize hardware"""
    logger.info("Initializing hardware...")
    
    # I2C for touch
    i2c = I2C(
        0,
        freq=400_000,
        scl=Pin(PIN_TOUCH_SCL),
        sda=Pin(PIN_TOUCH_SDA)
    )
    logger.info("I2C initialized")
    
    # SPI for LCD
    spi = SPI(
        1,
        baudrate=40_000_000,
        polarity=0,
        phase=0,
        sck=Pin(PIN_LCD_CLK),
        mosi=Pin(PIN_LCD_MOSI),
        miso=Pin(PIN_LCD_MISO)
    )
    logger.info("SPI initialized")
    
    # Display
    display = Ili9341v(
        spi=spi,
        dc=Pin(PIN_LCD_DC, Pin.OUT, value=0),
        cs=Pin(PIN_LCD_CS, Pin.OUT, value=1),
        bl=Pin(PIN_LCD_BL, Pin.OUT, value=0),
        rst=None,
        rotation=1  # Landscape mode
    )
    logger.info(f"Display initialized: {display.width}x{display.height}")
    
    # Touch sensor
    touch = Ft6x36(i2c, swap_xy=True)
    logger.info("Touch sensor initialized")
    
    return display, touch


async def main():
    """Main application entry point"""
    logger.info("Starting Calculator Demo")
    
    # Setup hardware
    display, touch = setup_hardware()
    
    # Get framebuffer from display
    fb = display.get_framebuffer()
    
    # Create microui context
    ctx = Context(text_width, text_height, fb)
    logger.info("MicroUI context created")
    
    # Configure colors for calculator theme
    ctx.style.colors[MU_COLOR_WINDOWBG] = Color(30, 30, 30)
    ctx.style.colors[MU_COLOR_BASE] = Color(50, 50, 50)
    ctx.style.colors[MU_COLOR_BUTTON] = Color(70, 70, 70)
    ctx.style.colors[MU_COLOR_BUTTONHOVER] = Color(90, 90, 90)
    ctx.style.colors[MU_COLOR_BUTTONFOCUS] = Color(0, 120, 215)  # Blue for equals
    ctx.style.colors[MU_COLOR_TEXT] = Color(255, 255, 255)
    
    # Create calculator
    calc = Calculator()
    
    # Create touch handler
    touch_handler = TouchHandler(touch, ctx)
    
    logger.info("Starting main loop...")
    
    # Run all tasks
    try:
        await asyncio.gather(
            touch_handler.poll(),
            ui_task(ctx, calc),
            display_task(ctx, display)
        )
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        import sys
        sys.print_exception(e)


if __name__ == '__main__':
    # Run the application
    asyncio.run(main())