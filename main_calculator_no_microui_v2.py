# calculator_working.py
"""
Working calculator with properly structured event loop
"""
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
                    y = 240-y
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

# Colors (RGB565)
COLOR_BG = 0x0000
COLOR_DISPLAY = 0x2104
COLOR_BUTTON = 0x4208
COLOR_BUTTON_HL = 0x6B4D
COLOR_EQUALS = 0x001F
COLOR_TEXT = 0xFFFF
COLOR_BORDER = 0x8410


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
            if len(self.display) < 10:
                if self.display == "0":
                    self.display = str(d)
                else:
                    self.display += str(d)
    
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
            self.display = self._format(val)
        except:
            pass
    
    def percent(self):
        if self.error:
            return
        try:
            val = float(self.display) / 100.0
            self.display = self._format(val)
        except:
            pass
    
    def operation_set(self, op):
        if self.error:
            self.clear()
        try:
            if self.operation and not self.new_number:
                self.equals()
            self.value = float(self.display)
            self.operation = op
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
            
            self.display = self._format(result)
            self.value = result
            self.operation = None
            self.new_number = True
        except:
            self.display = "Error"
            self.error = True
    
    def _format(self, num):
        if abs(num) > 999999999 or (abs(num) < 0.000001 and num != 0):
            s = f"{num:.4e}"
            return s[:10]
        if num == int(num):
            s = str(int(num))
        else:
            s = f"{num:.8f}".rstrip('0').rstrip('.')
        if len(s) > 10:
            s = f"{num:.4e}"[:10]
        return s


class Button:
    """Button widget"""
    
    def __init__(self, x, y, w, h, label, action, color=COLOR_BUTTON):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.label = label
        self.action = action
        self.color = color
        self.pressed = False
    
    def contains(self, px, py):
        return (self.x <= px < self.x + self.w and
                self.y <= py < self.y + self.h)
    
    def draw(self, fb):
        bg = COLOR_BUTTON_HL if self.pressed else self.color
        fb.fill_rect(self.x, self.y, self.w, self.h, bg)
        fb.rect(self.x, self.y, self.w, self.h, COLOR_BORDER)
        
        text_w = len(self.label) * 8
        text_h = 8
        tx = self.x + (self.w - text_w) // 2
        ty = self.y + (self.h - text_h) // 2
        fb.text(self.label, tx, ty, COLOR_TEXT)


class CalculatorUI:
    """Calculator UI"""
    
    def __init__(self, display):
        self.display = display
        self.fb = display.get_framebuffer()
        self.calc = Calculator()
        self.buttons = []
        self.active_button = None
        self.needs_redraw = True
        self._setup_ui()
    
    def _setup_ui(self):
        btn_w = 74
        btn_h = 30
        gap = 4
        x_start = 8
        y_start = 75
        
        layout = [
            [("C", self.calc.clear),
             ("CE", self.calc.clear_entry),
             ("%", self.calc.percent),
             ("/", lambda: self.calc.operation_set("/"))],
            
            [("7", lambda: self.calc.digit(7)),
             ("8", lambda: self.calc.digit(8)),
             ("9", lambda: self.calc.digit(9)),
             ("*", lambda: self.calc.operation_set("*"))],
            
            [("4", lambda: self.calc.digit(4)),
             ("5", lambda: self.calc.digit(5)),
             ("6", lambda: self.calc.digit(6)),
             ("-", lambda: self.calc.operation_set("-"))],
            
            [("1", lambda: self.calc.digit(1)),
             ("2", lambda: self.calc.digit(2)),
             ("3", lambda: self.calc.digit(3)),
             ("+", lambda: self.calc.operation_set("+"))],
            
            [("+/-", self.calc.negate),
             ("0", lambda: self.calc.digit(0)),
             (".", self.calc.decimal),
             ("=", self.calc.equals)]
        ]
        
        for row_idx, row in enumerate(layout):
            y = y_start + row_idx * (btn_h + gap)
            for col_idx, (label, action) in enumerate(row):
                x = x_start + col_idx * (btn_w + gap)
                color = COLOR_EQUALS if label == "=" else COLOR_BUTTON
                btn = Button(x, y, btn_w, btn_h, label, action, color)
                self.buttons.append(btn)
    
    def handle_touch(self, x, y):
        for btn in self.buttons:
            if btn.contains(x, y):
                self.active_button = btn
                btn.action()
                self.needs_redraw = True
                return True
        return False
    
    def draw(self):
        if not self.needs_redraw:
            return
        
        # Clear screen
        self.fb.fill(COLOR_BG)
        
        # Draw display
        dx, dy, dw, dh = 8, 10, 304, 55
        self.fb.fill_rect(dx, dy, dw, dh, COLOR_DISPLAY)
        self.fb.rect(dx, dy, dw, dh, COLOR_BORDER)
        
        # Display text (2x size, right-aligned)
        text = self.calc.display
        char_w = 8
        text_w = len(text) * char_w * 2
        text_x = dx + dw - text_w - 8
        text_y = dy + (dh - 16) // 2
        
        for i, c in enumerate(text):
            cx = text_x + i * char_w * 2
#             for dy_off in range(2):
#                 for dx_off in range(2):
#                     self.fb.text(c, cx + dx_off, text_y + dy_off, COLOR_TEXT)
            self.fb.text(c, cx, text_y, COLOR_TEXT)
        
        # Draw buttons
        for btn in self.buttons:
            btn.pressed = (btn == self.active_button)
            btn.draw(self.fb)
        
        # Update display
        self.display.show()
        
        # Clear state
        self.active_button = None
        self.needs_redraw = False


class App:
    """Main application"""
    
    def __init__(self):
        log.info("Initializing hardware...")
        
        # I2C
        self.i2c = I2C(0, freq=400_000,
                       scl=Pin(PIN_TOUCH_SCL),
                       sda=Pin(PIN_TOUCH_SDA))
        log.info("I2C OK")
        
        # SPI
        self.spi = SPI(1, baudrate=40_000_000,
                       polarity=0, phase=0,
                       sck=Pin(PIN_LCD_CLK),
                       mosi=Pin(PIN_LCD_MOSI),
                       miso=Pin(PIN_LCD_MISO))
        log.info("SPI OK")
        
        # Display
        self.display = Ili9341v(
            spi=self.spi,
            dc=Pin(PIN_LCD_DC, Pin.OUT, value=0),
            cs=Pin(PIN_LCD_CS, Pin.OUT, value=1),
            bl=Pin(PIN_LCD_BL, Pin.OUT, value=0),
            rst=None,
            rotation=1
        )
        log.info(f"Display OK: {self.display.width}x{self.display.height}")
        
        # Touch
        self.touch = Ft6x36(self.i2c, swap_xy=True)
        log.info("Touch OK")
        
        # UI
        self.ui = CalculatorUI(self.display)
        log.info("UI created")
        
        # Touch state
        self.last_pressed = False
        self.last_touch_time = 0
        self.debounce_ms = 200
        
        # Initial draw
        self.ui.needs_redraw = True
        self.ui.draw()
        log.info("Initial draw complete")
    
    async def run(self):
        """Main event loop"""
        log.info("Starting event loop...")
        
        frame_count = 0
        last_log = time.ticks_ms()
        
        while True:
            try:
                # Handle touch input
                count, x, y = self.touch.read()
                now = time.ticks_ms()
                
                if count > 0 and not self.last_pressed:
                    # New touch
                    if asyncio.ticks_diff(now, self.last_touch_time) > self.debounce_ms:
                        if self.ui.handle_touch(x, y):
                            log.debug(f"Touch: ({x}, {y})")
                            self.last_touch_time = now
                    self.last_pressed = True
                elif count == 0:
                    self.last_pressed = False
                
                # Redraw if needed
                if self.ui.needs_redraw:
                    self.ui.draw()
                
                # Log FPS occasionally
                frame_count += 1
                if asyncio.ticks_diff(now, last_log) > 5000:
                    fps = frame_count / 5.0
                    log.info(f"Running at {fps:.1f} FPS")
                    frame_count = 0
                    last_log = now
                
                # Yield to other tasks
                await asyncio.sleep_ms(30)
                
            except Exception as e:
                log.error(f"Loop error: {e}")
                import sys
                sys.print_exception(e)
                await asyncio.sleep_ms(100)


async def main():
    """Entry point"""
    log.info("=== Calculator Starting ===")
    
    try:
        app = App()
        await app.run()
    except KeyboardInterrupt:
        log.info("Stopped by user")
    except Exception as e:
        log.error(f"Fatal error: {e}")
        import sys
        sys.print_exception(e)


if __name__ == '__main__':
    asyncio.run(main())
