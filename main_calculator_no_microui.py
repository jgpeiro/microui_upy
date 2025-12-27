# calculator_standalone.py
"""
Standalone calculator for ILI9341 display with FT6x36 touch
Includes minimal UI framework inline for easy deployment
"""
import time

import asyncio
import logging
from machine import I2C, SPI, Pin

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

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Hardware pins
PIN_LCD_CS = 10
PIN_LCD_DC = 46
PIN_LCD_BL = 45
PIN_LCD_CLK = 12
PIN_LCD_MOSI = 11
PIN_LCD_MISO = 13
PIN_TOUCH_SDA = 16
PIN_TOUCH_SCL = 15

LCD_WIDTH = 320
LCD_HEIGHT = 240


class Button:
    """Simple button widget"""
    def __init__(self, x, y, w, h, text, bg=0x4444, fg=0xFFFF):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.bg = bg
        self.fg = fg
        self.pressed = False
        
    def contains(self, px, py):
        """Check if point is inside button"""
        return (self.x <= px < self.x + self.w and 
                self.y <= py < self.y + self.h)
    
    def draw(self, fb, highlight=False):
        """Draw button to framebuffer"""
        # Background
        color = 0x6666 if highlight else self.bg
        fb.fill_rect(self.x, self.y, self.w, self.h, color)
        
        # Border
        fb.rect(self.x, self.y, self.w, self.h, 0x8888)
        
        # Text (centered)
        text_w = len(self.text) * 8
        text_x = self.x + (self.w - text_w) // 2
        text_y = self.y + (self.h - 8) // 2
        fb.text(self.text, text_x, text_y, self.fg)


class Calculator:
    """Calculator logic"""
    def __init__(self):
        self.display = "0"
        self.value = 0.0
        self.operation = None
        self.new_number = True
        self.error = False
        
    def clear(self):
        self.display = "0"
        self.value = 0.0
        self.operation = None
        self.new_number = True
        self.error = False
        
    def clear_entry(self):
        self.display = "0"
        self.new_number = True
        
    def digit(self, d):
        if self.error:
            self.clear()
        if self.new_number:
            self.display = str(d)
            self.new_number = False
        else:
            if len(self.display) < 12:
                self.display = self.display + str(d) if self.display != "0" else str(d)
    
    def decimal(self):
        if self.error:
            self.clear()
        if self.new_number:
            self.display = "0."
            self.new_number = False
        elif "." not in self.display:
            self.display += "."
    
    def negate(self):
        if self.error:
            return
        try:
            val = -float(self.display)
            self.display = self._fmt(val)
        except:
            pass
    
    def percent(self):
        if self.error:
            return
        try:
            val = float(self.display) / 100.0
            self.display = self._fmt(val)
        except:
            pass
    
    def op(self, operation):
        if self.error:
            self.clear()
        try:
            if self.operation and not self.new_number:
                self.equals()
            self.value = float(self.display)
            self.operation = operation
            self.new_number = True
        except:
            self.display = "Error"
            self.error = True
    
    def equals(self):
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
            
            self.display = self._fmt(result)
            self.value = result
            self.operation = None
            self.new_number = True
        except:
            self.display = "Error"
            self.error = True
    
    def _fmt(self, num):
        """Format number"""
        if abs(num) > 999999999 or (abs(num) < 0.00001 and num != 0):
            return f"{num:.6e}"
        if num == int(num):
            return str(int(num))
        return f"{num:.8f}".rstrip('0').rstrip('.')


class CalculatorUI:
    """Calculator UI manager"""
    def __init__(self, display):
        self.display = display
        self.fb = display.get_framebuffer()
        self.calc = Calculator()
        self.buttons = []
        self.last_pressed = None
        self._create_buttons()
        
    def _create_buttons(self):
        """Create button layout"""
        # Display area at top: y=10, height=50
        # Buttons start at y=70
        
        btn_w = 75
        btn_h = 32
        x_start = 5
        y_start = 70
        gap = 3
        
        # Button layout
        layout = [
            ["C", "CE", "%", "/"],
            ["7", "8", "9", "*"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["+/-", "0", ".", "="]
        ]
        
        for row_idx, row in enumerate(layout):
            y = y_start + row_idx * (btn_h + gap)
            for col_idx, text in enumerate(row):
                x = x_start + col_idx * (btn_w + gap)
                
                # Special color for equals
                if text == "=":
                    btn = Button(x, y, btn_w, btn_h, text, bg=0x001F, fg=0xFFFF)
                else:
                    btn = Button(x, y, btn_w, btn_h, text)
                
                self.buttons.append(btn)
    
    def handle_touch(self, x, y):
        """Handle touch event"""
        for btn in self.buttons:
            if btn.contains(x, y):
                self.last_pressed = btn
                self._handle_button(btn.text)
                return True
        return False
    
    def _handle_button(self, text):
        """Handle button press"""
        if text.isdigit():
            self.calc.digit(int(text))
        elif text == ".":
            self.calc.decimal()
        elif text == "C":
            self.calc.clear()
        elif text == "CE":
            self.calc.clear_entry()
        elif text == "+/-":
            self.calc.negate()
        elif text == "%":
            self.calc.percent()
        elif text in "+-*/":
            self.calc.op(text)
        elif text == "=":
            self.calc.equals()
    
    def draw(self):
        """Draw calculator UI"""
        # Clear screen
        self.fb.fill(0x0000)
        
        # Draw display area
        display_x = 5
        display_y = 10
        display_w = 310
        display_h = 50
        
        # Display background
        self.fb.fill_rect(display_x, display_y, display_w, display_h, 0x2222)
        self.fb.rect(display_x, display_y, display_w, display_h, 0x8888)
        
        # Display text (right-aligned, larger)
        text = self.calc.display
        # Draw text 2x2 for larger appearance
        char_w = 8
        char_h = 8
        text_w = len(text) * char_w * 2
        text_x = display_x + display_w - text_w - 10
        text_y = display_y + (display_h - char_h * 2) // 2
        
        # Draw each character twice for 2x size effect
        for i, char in enumerate(text):
            x = text_x + i * char_w * 2
            # Draw 4 times with offset for 2x2
            for dy in range(2):
                for dx in range(2):
                    self.fb.text(char, x + dx, text_y + dy, 0xFFFF)
        
        # Draw buttons
        for btn in self.buttons:
            highlight = (btn == self.last_pressed)
            btn.draw(self.fb, highlight)
        
        # Update display
        self.display.show()
        
        # Clear last pressed after drawing
        self.last_pressed = None


async def touch_task(touch, ui):
    """Touch polling task"""
    last_count = 0
    debounce_time = 150
    last_touch_time = 0
    
    while True:
        count, x, y = touch.read()
        current_time = time.ticks_ms()
        
        if count > 0 and last_count == 0:
            # New touch
            if asyncio.ticks_diff(current_time, last_touch_time) > debounce_time:
                if ui.handle_touch(x, y):
                    log.info(f"Touch at ({x}, {y})")
                    last_touch_time = current_time
        
        last_count = count
        await asyncio.sleep_ms(20)


async def display_task(ui):
    """Display update task"""
    while True:
        ui.draw()
        await asyncio.sleep_ms(33)  # ~30 FPS


async def main():
    """Main application"""
    log.info("=== Calculator Demo ===")
    
    # Initialize I2C
    i2c = I2C(
        0,
        freq=400_000,
        scl=Pin(PIN_TOUCH_SCL),
        sda=Pin(PIN_TOUCH_SDA)
    )
    log.info("I2C initialized")
    
    # Initialize SPI
    spi = SPI(
        1,
        baudrate=40_000_000,
        polarity=0,
        phase=0,
        sck=Pin(PIN_LCD_CLK),
        mosi=Pin(PIN_LCD_MOSI),
        miso=Pin(PIN_LCD_MISO)
    )
    log.info("SPI initialized")
    
    # Initialize display
    display = Ili9341v(
        spi=spi,
        dc=Pin(PIN_LCD_DC, Pin.OUT, value=0),
        cs=Pin(PIN_LCD_CS, Pin.OUT, value=1),
        bl=Pin(PIN_LCD_BL, Pin.OUT, value=0),
        rst=None,
        rotation=1  # Landscape
    )
    log.info(f"Display: {display.width}x{display.height}")
    
    # Initialize touch
    touch = Ft6x36(i2c, swap_xy=True)
    log.info("Touch initialized")
    
    # Create UI
    ui = CalculatorUI(display)
    log.info("UI created")
    
    # Initial draw
    ui.draw()
    
    log.info("Starting event loop...")
    
    # Run tasks
    try:
        await asyncio.gather(
            touch_task(touch, ui),
            display_task(ui)
        )
    except KeyboardInterrupt:
        log.info("Stopped")
    except Exception as e:
        log.error(f"Error: {e}")
        import sys
        sys.print_exception(e)


# Run
if __name__ == '__main__':
    asyncio.run(main())