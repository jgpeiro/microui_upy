# calculator_microui_fixed.py
"""
Calculator using MicroUI library with fixed event loop
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
        self.last_pressed = False
    
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
                    self.last_pressed = 1
                    return 1, x, y
            elif self.last_pressed:
                self.last_pressed = 0
                return 0, self.x, self.y
            # No touch detected
            self.pressed = False
            return 0, self.x, self.y
            
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

# Import MicroUI components
from microui.core import (
    Context, Rect, Color, Vec2,
    MU_COLOR_TEXT, MU_COLOR_BORDER, MU_COLOR_WINDOWBG,
    MU_COLOR_BUTTON, MU_COLOR_BUTTONHOVER, MU_COLOR_BUTTONFOCUS,
    MU_COLOR_BASE, MU_COLOR_BASEHOVER, MU_MOUSE_LEFT,
    MU_OPT_NOTITLE, MU_OPT_NOCLOSE, MU_OPT_NORESIZE, 
    MU_OPT_NOSCROLL, MU_OPT_ALIGNCENTER, MU_RES_SUBMIT
)
from microui.context import (
    begin, end, get_id, push_clip_rect, pop_clip_rect,
    input_mousemove, input_mousedown, input_mouseup
)
from microui.drawing import draw_rect, draw_text, render_commands
from microui.layout import layout_row, layout_next
from microui.controls import button_ex, draw_control_frame, draw_control_text, update_control
from microui.windows import begin_window_ex, end_window

logging.basicConfig(level=logging.DEBUG)
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
        log.info("Clear")
    
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
            log.info(f"Result: {self.display}")
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
    
    def get_display(self):
        return self.display


# Text measurement functions for MicroUI
def text_width(font, text):
    return len(text) * 8

def text_height(font):
    return 8


def draw_calculator_ui(ctx, calc):
    """Draw calculator UI using MicroUI"""
    
    # Fullscreen window
    if begin_window_ex(ctx, "Calculator", Rect(0, 0, 320, 240),
                       MU_OPT_NOTITLE | MU_OPT_NOCLOSE | MU_OPT_NORESIZE | MU_OPT_NOSCROLL):
        
        # Display area (large)
        layout_row(ctx, 1, [-1], 50)
        r = layout_next(ctx)
        
        # Draw display background
        id_display = get_id(ctx, "display")
        draw_control_frame(ctx, id_display, r, MU_COLOR_BASE, 0)
        
        # Draw display text (right-aligned, scaled 2x)
        display_text = calc.get_display()
        push_clip_rect(ctx, r)
        
        char_w = 8
        text_w = len(display_text) * char_w * 2
        text_x = r.x + r.w - text_w - 10
        text_y = r.y + (r.h - 16) // 2
        
        # Draw 2x scaled text
        for i, c in enumerate(display_text):
            cx = text_x + i * char_w * 2
            #for dy in range(2):
            #    for dx in range(2):
            #        draw_text(ctx, None, c, Vec2(cx + dx, text_y + dy),
            #                 ctx.style.colors[MU_COLOR_TEXT])
            draw_text(ctx, None, c, Vec2(cx, text_y),
                 ctx.style.colors[MU_COLOR_TEXT])
        
        pop_clip_rect(ctx)
        
        # Button rows
        btn_h = 35
        
        # Row 1: C, CE, %, /
        layout_row(ctx, 4, [75, 75, 75, 75], btn_h)
        if button_ex(ctx, "C", 0, MU_OPT_ALIGNCENTER):
            calc.clear()
        if button_ex(ctx, "CE", 0, MU_OPT_ALIGNCENTER):
            calc.clear_entry()
        if button_ex(ctx, "%", 0, MU_OPT_ALIGNCENTER):
            calc.percent()
        if button_ex(ctx, "/", 0, MU_OPT_ALIGNCENTER):
            calc.operation_set("/")
        
        # Row 2: 7, 8, 9, *
        layout_row(ctx, 4, [75, 75, 75, 75], btn_h)
        if button_ex(ctx, "7", 0, MU_OPT_ALIGNCENTER):
            calc.digit(7)
        if button_ex(ctx, "8", 0, MU_OPT_ALIGNCENTER):
            calc.digit(8)
        if button_ex(ctx, "9", 0, MU_OPT_ALIGNCENTER):
            calc.digit(9)
        if button_ex(ctx, "*", 0, MU_OPT_ALIGNCENTER):
            calc.operation_set("*")
        
        # Row 3: 4, 5, 6, -
        layout_row(ctx, 4, [75, 75, 75, 75], btn_h)
        if button_ex(ctx, "4", 0, MU_OPT_ALIGNCENTER):
            calc.digit(4)
        if button_ex(ctx, "5", 0, MU_OPT_ALIGNCENTER):
            calc.digit(5)
        if button_ex(ctx, "6", 0, MU_OPT_ALIGNCENTER):
            calc.digit(6)
        if button_ex(ctx, "-", 0, MU_OPT_ALIGNCENTER):
            calc.operation_set("-")
        
        # Row 4: 1, 2, 3, +
        layout_row(ctx, 4, [75, 75, 75, 75], btn_h)
        if button_ex(ctx, "1", 0, MU_OPT_ALIGNCENTER):
            calc.digit(1)
        if button_ex(ctx, "2", 0, MU_OPT_ALIGNCENTER):
            calc.digit(2)
        if button_ex(ctx, "3", 0, MU_OPT_ALIGNCENTER):
            calc.digit(3)
        if button_ex(ctx, "+", 0, MU_OPT_ALIGNCENTER):
            calc.operation_set("+")
        
        # Row 5: +/-, 0, ., =
        layout_row(ctx, 4, [75, 75, 75, 75], btn_h)
        if button_ex(ctx, "+/-", 0, MU_OPT_ALIGNCENTER):
            calc.negate()
        if button_ex(ctx, "0", 0, MU_OPT_ALIGNCENTER):
            calc.digit(0)
        if button_ex(ctx, ".", 0, MU_OPT_ALIGNCENTER):
            calc.decimal()
        
        # Equals button with special handling
        r = layout_next(ctx)
        id_equals = get_id(ctx, "=")
        update_control(ctx, id_equals, r, 0)
        
        if ctx.mouse_pressed == MU_MOUSE_LEFT and ctx.focus == id_equals:
            calc.equals()
        
        # Draw equals with blue color
        draw_control_frame(ctx, id_equals, r, MU_COLOR_BUTTONFOCUS, 0)
        draw_control_text(ctx, "=", r, MU_COLOR_TEXT, MU_OPT_ALIGNCENTER)
        
        end_window(ctx)

# microui_demos.py
"""
Five reference UI demos showcasing MicroUI features
Gold standard examples for the library
"""

from microui.core import (
    Rect, Vec2, Color,
    MU_COLOR_TEXT, MU_COLOR_BUTTON, MU_COLOR_BASE,
    MU_OPT_ALIGNCENTER, MU_OPT_ALIGNRIGHT, MU_OPT_EXPANDED
)
from microui.context import get_id, push_clip_rect, pop_clip_rect
from microui.drawing import draw_text, draw_rect, draw_icon
from microui.layout import (
    layout_row, layout_next, layout_begin_column, 
    layout_end_column, layout_width
)
from microui.controls import (
    button_ex, checkbox, slider, label, text, header,
    begin_treenode, end_treenode, draw_control_frame, draw_control_text
)
from microui.windows import (
    begin_window_ex, end_window, begin_panel_ex, end_panel
)


# =============================================================================
# DEMO 1: Dashboard UI - Shows panels, labels, and basic layout
# =============================================================================

class DashboardState:
    """State for dashboard demo"""
    def __init__(self):
        self.cpu_temp = 42.5
        self.memory_used = 67
        self.disk_used = 45
        self.network_up = 1.2
        self.network_down = 5.8
state = DashboardState()
def draw_dashboard_ui(ctx, state):
    """
    Dashboard UI Demo
    Features: Multiple panels, labels, progress bars (sliders), text display
    """
    
    if begin_window_ex(ctx, "System Monitor", Rect(10, 10, 300, 220), 0):
        
        # Title section
        layout_row(ctx, 1, [-1], 0)
        label(ctx, "System Status Dashboard")
        
        # Two-column layout
        layout_row(ctx, 2, [145, 145], -1)
        
        # Left panel - System Info
        begin_panel_ex(ctx, "system_info", 0)
        layout_row(ctx, 1, [-1], 0)
        label(ctx, "CPU Temperature")
        layout_row(ctx, 1, [-1], 0)
        text(ctx, f"{state.cpu_temp:.1f} C")
        
        layout_row(ctx, 1, [-1], 10)  # Spacer
        
        layout_row(ctx, 1, [-1], 0)
        label(ctx, "Memory Usage")
        layout_row(ctx, 1, [-1], 20)
        _, state.memory_used = slider(ctx, state.memory_used, 0, 100)
        layout_row(ctx, 1, [-1], 0)
        label(ctx, f"{state.memory_used:.0f}%")
        
        layout_row(ctx, 1, [-1], 10)  # Spacer
        
        layout_row(ctx, 1, [-1], 0)
        label(ctx, "Disk Usage")
        layout_row(ctx, 1, [-1], 20)
        _, state.disk_used = slider(ctx, state.disk_used, 0, 100)
        layout_row(ctx, 1, [-1], 0)
        label(ctx, f"{state.disk_used:.0f}%")
        end_panel(ctx)
        
        # Right panel - Network Info
        begin_panel_ex(ctx, "network_info", 0)
        layout_row(ctx, 1, [-1], 0)
        label(ctx, "Network Activity")
        
        layout_row(ctx, 1, [-1], 10)
        
        layout_row(ctx, 1, [-1], 0)
        label(ctx, "Upload Speed")
        layout_row(ctx, 1, [-1], 0)
        text(ctx, f"{state.network_up:.1f} MB/s")
        
        layout_row(ctx, 1, [-1], 10)
        
        layout_row(ctx, 1, [-1], 0)
        label(ctx, "Download Speed")
        layout_row(ctx, 1, [-1], 0)
        text(ctx, f"{state.network_down:.1f} MB/s")
        
        layout_row(ctx, 1, [-1], 10)
        
        layout_row(ctx, 1, [-1], 0)
        if button_ex(ctx, "Refresh", 0, MU_OPT_ALIGNCENTER):
            state.cpu_temp += 0.5
            state.network_up = (state.network_up + 0.3) % 10
            state.network_down = (state.network_down + 0.5) % 15
        end_panel(ctx)
        
        end_window(ctx)



# =============================================================================
# DEMO 2: Settings UI - Shows checkboxes, sliders, tree nodes
# =============================================================================

class SettingsState:
    """State for settings demo"""
    def __init__(self):
        self.enable_sound = True
        self.enable_vibration = False
        self.enable_notifications = True
        self.volume = 75.0
        self.brightness = 80.0
        self.timeout = 30
state = SettingsState()
def draw_settings_ui(ctx, state):
    """
    Settings UI Demo
    Features: Checkboxes, sliders, tree nodes, nested layouts
    """
    
    if begin_window_ex(ctx, "Settings", Rect(10, 10, 300, 220), 0):
        
        # Audio settings (expandable tree node)
        if begin_treenode(ctx, "Audio Settings"):
            layout_row(ctx, 1, [-1], 0)
            _, state.enable_sound = checkbox(ctx, "Enable Sound", state.enable_sound)
            
            layout_row(ctx, 1, [-1], 0)
            _, state.enable_vibration = checkbox(ctx, "Enable Vibration", state.enable_vibration)
            
            layout_row(ctx, 1, [-1], 0)
            label(ctx, "Volume")
            layout_row(ctx, 1, [-1], 20)
            _, state.volume = slider(ctx, state.volume, 0, 100)
            
            end_treenode(ctx)
        
        # Display settings
        if begin_treenode(ctx, "Display Settings"):
            layout_row(ctx, 1, [-1], 0)
            label(ctx, "Brightness")
            layout_row(ctx, 1, [-1], 20)
            _, state.brightness = slider(ctx, state.brightness, 0, 100)
            
            layout_row(ctx, 1, [-1], 0)
            label(ctx, f"Screen Timeout: {state.timeout}s")
            layout_row(ctx, 1, [-1], 20)
            _, state.timeout = slider(ctx, float(state.timeout), 10, 120)
            state.timeout = int(state.timeout)
            
            end_treenode(ctx)
        
        # Notification settings
        if begin_treenode(ctx, "Notifications"):
            layout_row(ctx, 1, [-1], 0)
            _, state.enable_notifications = checkbox(ctx, "Enable Notifications", 
                                                     state.enable_notifications)
            
            layout_row(ctx, 1, [-1], 0)
            label(ctx, "Get alerts for:")
            layout_row(ctx, 1, [-1], 0)
            text(ctx, "Messages, Calls, Updates")
            
            end_treenode(ctx)
        
        # Action buttons
        layout_row(ctx, 2, [145, 145], 0)
        if button_ex(ctx, "Reset Defaults", 0, MU_OPT_ALIGNCENTER):
            state.volume = 75.0
            state.brightness = 80.0
            state.timeout = 30
            state.enable_sound = True
            state.enable_notifications = True
        
        if button_ex(ctx, "Apply", 0, MU_OPT_ALIGNCENTER):
            pass  # Apply settings
        
        end_window(ctx)


# =============================================================================
# DEMO 3: File Browser UI - Shows lists, panels, scrolling
# =============================================================================

class FileBrowserState:
    """State for file browser demo"""
    def __init__(self):
        self.current_path = "/home/user"
        self.files = [
            ("Documents", True),
            ("Downloads", True),
            ("Pictures", True),
            ("Music", True),
            ("Videos", True),
            ("readme.txt", False),
            ("notes.md", False),
            ("todo.txt", False),
        ]
        self.selected_idx = -1
state = FileBrowserState()
def draw_file_browser_ui(ctx, state):
    """
    File Browser UI Demo
    Features: Lists, selection, panels, text display
    """
    
    if begin_window_ex(ctx, "File Browser", Rect(10, 10, 300, 220), 0):
        
        # Path bar
        layout_row(ctx, 1, [-1], 0)
        label(ctx, f"Path: {state.current_path}")
        
        layout_row(ctx, 1, [-1], 5)  # Spacer
        
        # File list in panel
        layout_row(ctx, 1, [-1], 140)
        begin_panel_ex(ctx, "file_list", 0)
        
        for idx, (name, is_folder) in enumerate(state.files):
            layout_row(ctx, 1, [-1], 0)
            
            # Custom button for file/folder
            r = layout_next(ctx)
            id_item = get_id(ctx, f"file_{idx}")
            
            # Check if selected
            from microui.controls import update_control, mouse_over
            update_control(ctx, id_item, r, 0)
            
            # Highlight if selected
            if idx == state.selected_idx:
                draw_control_frame(ctx, id_item, r, MU_COLOR_BUTTON, 0)
            
            # Handle click
            if ctx.mouse_pressed == 1 and ctx.focus == id_item:
                state.selected_idx = idx
            
            # Draw icon and name
            icon_text = "[DIR]" if is_folder else "[   ]"
            full_text = f"{icon_text} {name}"
            draw_control_text(ctx, full_text, r, MU_COLOR_TEXT, 0)
        
        end_panel(ctx)
        
        # Action buttons
        layout_row(ctx, 3, [95, 95, 95], 0)
        if button_ex(ctx, "Open", 0, MU_OPT_ALIGNCENTER):
            if state.selected_idx >= 0:
                name, is_folder = state.files[state.selected_idx]
                if is_folder:
                    state.current_path += f"/{name}"
        
        if button_ex(ctx, "Back", 0, MU_OPT_ALIGNCENTER):
            if "/" in state.current_path:
                state.current_path = "/".join(state.current_path.split("/")[:-1])
                if not state.current_path:
                    state.current_path = "/"
        
        if button_ex(ctx, "Delete", 0, MU_OPT_ALIGNCENTER):
            if state.selected_idx >= 0:
                state.files.pop(state.selected_idx)
                state.selected_idx = -1
        
        end_window(ctx)






# =============================================================================
# DEMO 4: Media Player UI - Shows custom drawing, icons, progress
# =============================================================================

class MediaPlayerState:
    """State for media player demo"""
    def __init__(self):
        self.playing = False
        self.track_name = "Summer Vibes.mp3"
        self.artist = "Electronic Dreams"
        self.position = 45.0  # seconds
        self.duration = 180.0  # seconds
        self.volume = 70.0
state = MediaPlayerState()
def draw_media_player_ui(ctx, state):
    """
    Media Player UI Demo
    Features: Custom drawing, progress bars, icon buttons, time display
    """
    
    if begin_window_ex(ctx, "Music Player", Rect(10, 10, 300, 220), 0):
        
        # Album art area (simulated with colored rect)
        layout_row(ctx, 1, [-1], 80)
        r = layout_next(ctx)
        draw_rect(ctx, r, Color(60, 60, 100))
        
        # Draw album info overlay
        push_clip_rect(ctx, r)
        info_y = r.y + r.h - 30
        draw_text(ctx, None, state.track_name, 
                 Vec2(r.x + 5, info_y), ctx.style.colors[MU_COLOR_TEXT])
        draw_text(ctx, None, state.artist,
                 Vec2(r.x + 5, info_y + 10), Color(180, 180, 180))
        pop_clip_rect(ctx)
        
        # Progress bar
        layout_row(ctx, 1, [-1], 0)
        pos_min = int(state.position // 60)
        pos_sec = int(state.position % 60)
        dur_min = int(state.duration // 60)
        dur_sec = int(state.duration % 60)
        label(ctx, f"{pos_min:02d}:{pos_sec:02d} / {dur_min:02d}:{dur_sec:02d}")
        
        layout_row(ctx, 1, [-1], 20)
        _, new_pos = slider(ctx, state.position, 0, state.duration)
        if abs(new_pos - state.position) > 1.0:  # User seeked
            state.position = new_pos
        
        # Playback controls
        layout_row(ctx, 5, [55, 55, 55, 55, 55], 0)
        
        if button_ex(ctx, "<<", 0, MU_OPT_ALIGNCENTER):
            state.position = max(0, state.position - 10)
        
        play_label = "||" if state.playing else ">"
        if button_ex(ctx, play_label, 0, MU_OPT_ALIGNCENTER):
            state.playing = not state.playing
        
        if button_ex(ctx, ">>", 0, MU_OPT_ALIGNCENTER):
            state.position = min(state.duration, state.position + 10)
        
        if button_ex(ctx, "[]", 0, MU_OPT_ALIGNCENTER):
            state.position = 0
            state.playing = False
        
        if button_ex(ctx, "...", 0, MU_OPT_ALIGNCENTER):
            pass  # Options menu
        
        # Volume control
        layout_row(ctx, 1, [-1], 0)
        label(ctx, f"Volume: {state.volume:.0f}%")
        layout_row(ctx, 1, [-1], 20)
        _, state.volume = slider(ctx, state.volume, 0, 100)
        
        # Simulate playback
        if state.playing and state.position < state.duration:
            state.position += 0.1  # Advance by 0.1s per frame
        
        end_window(ctx)


# =============================================================================
# DEMO 5: Form UI - Shows text input simulation, mixed controls
# =============================================================================

class FormState:
    """State for form demo"""
    def __init__(self):
        self.name = "John Doe"
        self.email = "john@example.com"
        self.age = 25
        self.subscribe = True
        self.gender = 0  # 0=Male, 1=Female, 2=Other
        self.interests = [False, True, False, True]  # Tech, Sports, Music, Art
        self.submitted = False
state = FormState()
def draw_form_ui(ctx, state):
    """
    Form UI Demo
    Features: Mixed controls, radio buttons (simulated), form layout
    """
    
    if begin_window_ex(ctx, "User Registration", Rect(10, 10, 300, 220), 0):
        
        # Name field (simulated text input)
        layout_row(ctx, 1, [-1], 0)
        label(ctx, "Full Name:")
        layout_row(ctx, 1, [-1], 0)
        r = layout_next(ctx)
        draw_control_frame(ctx, get_id(ctx, "name"), r, MU_COLOR_BASE, 0)
        draw_control_text(ctx, state.name, r, MU_COLOR_TEXT, 0)
        
        # Email field
        layout_row(ctx, 1, [-1], 0)
        label(ctx, "Email:")
        layout_row(ctx, 1, [-1], 0)
        r = layout_next(ctx)
        draw_control_frame(ctx, get_id(ctx, "email"), r, MU_COLOR_BASE, 0)
        draw_control_text(ctx, state.email, r, MU_COLOR_TEXT, 0)
        
        # Age slider
        layout_row(ctx, 2, [100, 190], 0)
        label(ctx, f"Age: {state.age}")
        _, state.age = slider(ctx, float(state.age), 1, 100)
        state.age = int(state.age)
        
        # Gender (simulated radio buttons)
        layout_row(ctx, 1, [-1], 0)
        label(ctx, "Gender:")
        layout_row(ctx, 3, [90, 90, 90], 0)
        if button_ex(ctx, "Male", 0, MU_OPT_ALIGNCENTER if state.gender != 0 else 0):
            state.gender = 0
        if button_ex(ctx, "Female", 0, MU_OPT_ALIGNCENTER if state.gender != 1 else 0):
            state.gender = 1
        if button_ex(ctx, "Other", 0, MU_OPT_ALIGNCENTER if state.gender != 2 else 0):
            state.gender = 2
        
        # Interests checkboxes
        if begin_treenode(ctx, "Interests"):
            layout_row(ctx, 2, [140, 140], 0)
            _, state.interests[0] = checkbox(ctx, "Technology", state.interests[0])
            _, state.interests[1] = checkbox(ctx, "Sports", state.interests[1])
            
            layout_row(ctx, 2, [140, 140], 0)
            _, state.interests[2] = checkbox(ctx, "Music", state.interests[2])
            _, state.interests[3] = checkbox(ctx, "Art", state.interests[3])
            end_treenode(ctx)
        
        # Subscribe checkbox
        layout_row(ctx, 1, [-1], 0)
        _, state.subscribe = checkbox(ctx, "Subscribe to newsletter", state.subscribe)
        
        # Submit button
        layout_row(ctx, 1, [-1], 0)
        if button_ex(ctx, "Submit Registration", 0, MU_OPT_ALIGNCENTER):
            state.submitted = True
        
        if state.submitted:
            layout_row(ctx, 1, [-1], 0)
            label(ctx, "Form submitted successfully!")
        
        end_window(ctx)

class App:
    """Main application with MicroUI"""
    
    def __init__(self):
        log.info("Initializing hardware...")
        
        # I2C for touch
        self.i2c = I2C(0, freq=400_000,
                       scl=Pin(PIN_TOUCH_SCL),
                       sda=Pin(PIN_TOUCH_SDA))
        log.info("I2C OK")
        
        # SPI for display
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
        
        # MicroUI context
        fb = self.display.get_framebuffer()
        self.ctx = Context(text_width, text_height, fb)
        
        # Configure colors
        self.ctx.style.colors[MU_COLOR_WINDOWBG] = Color(30, 30, 30)
        self.ctx.style.colors[MU_COLOR_BASE] = Color(50, 50, 50)
        self.ctx.style.colors[MU_COLOR_BUTTON] = Color(70, 70, 70)
        self.ctx.style.colors[MU_COLOR_BUTTONHOVER] = Color(90, 90, 90)
        self.ctx.style.colors[MU_COLOR_BUTTONFOCUS] = Color(0, 120, 215)
        self.ctx.style.colors[MU_COLOR_TEXT] = Color(255, 255, 255)
        self.ctx.style.colors[MU_COLOR_BORDER] = Color(100, 100, 100)
        
        log.info("MicroUI context created")
        
        # Calculator
        self.calc = Calculator()
        
        # Touch state
        self.last_pressed = False
        self.last_touch_time = 0
        self.debounce_ms = 150
        
        # Initial draw
        log.info("Performing initial draw...")
        #self._update_ui()
        self._build_ui()
        self._draw_ui()
        log.info("Initial draw complete")
    
    def _build_ui(self):
        # Begin MicroUI frame
        begin(self.ctx)
        
        # Draw calculator UI
        #draw_calculator_ui(self.ctx, self.calc)
        global state
        #€draw_dashboard_ui(self.ctx, state)
        #draw_settings_ui(self.ctx, state)
        #draw_file_browser_ui(self.ctx, state)
        #draw_media_player_ui(self.ctx, state)
        draw_form_ui(self.ctx, state)
        
        
        # End MicroUI frame
        end(self.ctx)
        
    def _draw_ui(self):
        """Update UI - single frame"""
        # Render to framebuffer
        render_commands(self.ctx)
        
        # Update display
        self.display.show()
    
    async def run(self):
        """Main event loop"""
        log.info("Starting event loop...")
        
        frame_count = 0
        last_log = time.ticks_ms()

        last_pressed = False
        n = 0
        while( 1 ):
            pressed, x, y = self.touch.read()
            if( pressed and not last_pressed ):
                log.info(f"Touch down: ({x}, {y})")
                input_mousemove(self.ctx, x, y)
                self._build_ui()
                self._draw_ui()
                input_mousedown(self.ctx, x, y, MU_MOUSE_LEFT)
                n = 1
            elif( pressed and last_pressed ):
                #log.info(f"Touch move: ({x}, {y})")
                input_mousemove(self.ctx, x, y)
                #n = 1
            elif( not pressed and last_pressed ):
                log.info(f"Touch up: ({x}, {y})")
                input_mousemove(self.ctx, x, y)
                self._build_ui()
                self._draw_ui()
                input_mouseup(self.ctx, x, y, MU_MOUSE_LEFT)
                n = 1
                
            else:
                if( n ):
                    n = 0
                    self._build_ui()
                    self._draw_ui()
                pass
            
            last_pressed = pressed
            await asyncio.sleep_ms(10)
        
        while True:
            try:
                # Handle touch
                count, x, y = self.touch.read()
                now = time.ticks_ms()
                
                if count > 0 and not self.last_pressed:
                    # New touch
                    if asyncio.ticks_diff(now, self.last_touch_time) > self.debounce_ms:
                        input_mousedown(self.ctx, x, y, MU_MOUSE_LEFT)
                        self.last_touch_time = now
                        log.debug(f"Touch down: ({x}, {y})")
                        # Update UI immediately on touch
                        self._update_ui()
                    self.last_pressed = True
                    
                elif count == 0 and self.last_pressed:
                    # Touch released
                    x, y, _ = self.touch.get_touch()
                    input_mouseup(self.ctx, x, y, MU_MOUSE_LEFT)
                    self.last_pressed = False
                    log.debug("Touch up")
                    # Update UI on release
                    self._update_ui()
                
                elif count == 0:
                    self.last_pressed = False
                
                # Periodic redraw (for animations/hover)
                if frame_count % 10 == 0:  # Every 10th frame
                    self._update_ui()
                
                # Log FPS
                frame_count += 1
                if asyncio.ticks_diff(now, last_log) > 1000:
                    fps = frame_count / 1.0
                    log.info(f"Running at {fps:.1f} FPS")
                    frame_count = 0
                    last_log = now
                
                # Yield
                await asyncio.sleep_ms(0)
                
            except Exception as e:
                log.error(f"Loop error: {e}")
                import sys
                sys.print_exception(e)
                await asyncio.sleep_ms(100)


async def main():
    """Entry point"""
    log.info("=== MicroUI Calculator Starting ===")
    
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