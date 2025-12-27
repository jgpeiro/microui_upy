# microui/core.py
"""
MicroPython port of microui library
Core context and data structures
"""
import framebuf
import logging
from micropython import const

logger = logging.getLogger(__name__)

# Version
MU_VERSION = "2.02-mp"

# Constants
MU_COMMANDLIST_SIZE = const(256 * 1024)
MU_ROOTLIST_SIZE = const(32)
MU_CONTAINERSTACK_SIZE = const(32)
MU_CLIPSTACK_SIZE = const(32)
MU_IDSTACK_SIZE = const(32)
MU_LAYOUTSTACK_SIZE = const(16)
MU_CONTAINERPOOL_SIZE = const(48)
MU_TREENODEPOOL_SIZE = const(48)
MU_MAX_WIDTHS = const(16)
MU_MAX_FMT = const(127)

# Clip flags
MU_CLIP_PART = const(1)
MU_CLIP_ALL = const(2)

# Command types
MU_COMMAND_JUMP = const(1)
MU_COMMAND_CLIP = const(2)
MU_COMMAND_RECT = const(3)
MU_COMMAND_TEXT = const(4)
MU_COMMAND_ICON = const(5)

# Color IDs
MU_COLOR_TEXT = const(0)
MU_COLOR_BORDER = const(1)
MU_COLOR_WINDOWBG = const(2)
MU_COLOR_TITLEBG = const(3)
MU_COLOR_TITLETEXT = const(4)
MU_COLOR_PANELBG = const(5)
MU_COLOR_BUTTON = const(6)
MU_COLOR_BUTTONHOVER = const(7)
MU_COLOR_BUTTONFOCUS = const(8)
MU_COLOR_BASE = const(9)
MU_COLOR_BASEHOVER = const(10)
MU_COLOR_BASEFOCUS = const(11)
MU_COLOR_SCROLLBASE = const(12)
MU_COLOR_SCROLLTHUMB = const(13)
MU_COLOR_MAX = const(14)

# Icon IDs
MU_ICON_CLOSE = const(1)
MU_ICON_CHECK = const(2)
MU_ICON_COLLAPSED = const(3)
MU_ICON_EXPANDED = const(4)

# Result flags
MU_RES_ACTIVE = const(1 << 0)
MU_RES_SUBMIT = const(1 << 1)
MU_RES_CHANGE = const(1 << 2)

# Option flags
MU_OPT_ALIGNCENTER = const(1 << 0)
MU_OPT_ALIGNRIGHT = const(1 << 1)
MU_OPT_NOINTERACT = const(1 << 2)
MU_OPT_NOFRAME = const(1 << 3)
MU_OPT_NORESIZE = const(1 << 4)
MU_OPT_NOSCROLL = const(1 << 5)
MU_OPT_NOCLOSE = const(1 << 6)
MU_OPT_NOTITLE = const(1 << 7)
MU_OPT_HOLDFOCUS = const(1 << 8)
MU_OPT_AUTOSIZE = const(1 << 9)
MU_OPT_POPUP = const(1 << 10)
MU_OPT_CLOSED = const(1 << 11)
MU_OPT_EXPANDED = const(1 << 12)

# Mouse buttons
MU_MOUSE_LEFT = const(1 << 0)
MU_MOUSE_RIGHT = const(1 << 1)
MU_MOUSE_MIDDLE = const(1 << 2)

# Keys
MU_KEY_SHIFT = const(1 << 0)
MU_KEY_CTRL = const(1 << 1)
MU_KEY_ALT = const(1 << 2)
MU_KEY_BACKSPACE = const(1 << 3)
MU_KEY_RETURN = const(1 << 4)

# Hash initial value
HASH_INITIAL = const(2166136261)


class Vec2:
    """2D Vector"""
    __slots__ = ('x', 'y')
    
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Vec2({self.x}, {self.y})"


class Rect:
    """Rectangle"""
    __slots__ = ('x', 'y', 'w', 'h')
    
    def __init__(self, x=0, y=0, w=0, h=0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    
    def __repr__(self):
        return f"Rect({self.x}, {self.y}, {self.w}, {self.h})"


class Color:
    """RGBA Color"""
    __slots__ = ('r', 'g', 'b', 'a')
    
    def __init__(self, r=0, g=0, b=0, a=255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
    
    def to_rgb565(self):
        """Convert to RGB565 format (swap bytes for SPI LCD)"""
        x = ((self.r & 0xF8) << 8) | ((self.g & 0xFC) << 3) | (self.b >> 3)
        l = (x>>0)&0xFF
        h = (x>>8)&0xFF
        return (l<<8)|(h<<0)
    
    def __repr__(self):
        return f"Color({self.r}, {self.g}, {self.b}, {self.a})"


class PoolItem:
    """Pool item for retained state"""
    __slots__ = ('id', 'last_update')
    
    def __init__(self):
        self.id = 0
        self.last_update = 0


class Command:
    """Base command class"""
    def __init__(self, cmd_type, size):
        self.type = cmd_type
        self.size = size


class JumpCommand(Command):
    """Jump command"""
    def __init__(self):
        super().__init__(MU_COMMAND_JUMP, 0)
        self.dst = None


class ClipCommand(Command):
    """Clip command"""
    def __init__(self, rect):
        super().__init__(MU_COMMAND_CLIP, 0)
        self.rect = rect


class RectCommand(Command):
    """Rectangle command"""
    def __init__(self, rect, color):
        super().__init__(MU_COMMAND_RECT, 0)
        self.rect = rect
        self.color = color


class TextCommand(Command):
    """Text command"""
    def __init__(self, font, pos, color, text):
        super().__init__(MU_COMMAND_TEXT, 0)
        self.font = font
        self.pos = pos
        self.color = color
        self.text = text


class IconCommand(Command):
    """Icon command"""
    def __init__(self, icon_id, rect, color):
        super().__init__(MU_COMMAND_ICON, 0)
        self.id = icon_id
        self.rect = rect
        self.color = color


class Layout:
    """Layout structure"""
    def __init__(self):
        self.body = Rect()
        self.next = Rect()
        self.position = Vec2()
        self.size = Vec2()
        self.max = Vec2()
        self.widths = [0] * MU_MAX_WIDTHS
        self.items = 0
        self.item_index = 0
        self.next_row = 0
        self.next_type = 0
        self.indent = 0


class Container:
    """Container structure"""
    def __init__(self):
        self.head = None
        self.tail = None
        self.rect = Rect()
        self.body = Rect()
        self.content_size = Vec2()
        self.scroll = Vec2()
        self.zindex = 0
        self.open = 0


class Style:
    """UI Style"""
    def __init__(self):
        self.font = None
        self.size = Vec2(68, 10)
        self.padding = 5
        self.spacing = 4
        self.indent = 24
        self.title_height = 24
        self.scrollbar_size = 12
        self.thumb_size = 8
        
        # Default colors
        self.colors = [
            Color(230, 230, 230, 255),  # TEXT
            Color(25, 25, 25, 255),      # BORDER
            Color(50, 50, 50, 255),      # WINDOWBG
            Color(25, 25, 25, 255),      # TITLEBG
            Color(240, 240, 240, 255),   # TITLETEXT
            Color(0, 0, 0, 0),           # PANELBG
            Color(75, 75, 75, 255),      # BUTTON
            Color(95, 95, 95, 255),      # BUTTONHOVER
            Color(115, 115, 115, 255),   # BUTTONFOCUS
            Color(30, 30, 30, 255),      # BASE
            Color(35, 35, 35, 255),      # BASEHOVER
            Color(40, 40, 40, 255),      # BASEFOCUS
            Color(43, 43, 43, 255),      # SCROLLBASE
            Color(30, 30, 30, 255),      # SCROLLTHUMB
        ]


class Stack:
    """Generic stack implementation"""
    def __init__(self, max_size):
        self.items = []
        self.idx = 0
        self.max_size = max_size
    
    def push(self, item):
        if self.idx >= self.max_size:
            raise RuntimeError(f"Stack overflow (max: {self.max_size})")
        if self.idx >= len(self.items):
            self.items.append(item)
        else:
            self.items[self.idx] = item
        self.idx += 1
    
    def pop(self):
        if self.idx <= 0:
            raise RuntimeError("Stack underflow")
        self.idx -= 1
        return self.items[self.idx]
    
    def top(self):
        if self.idx <= 0:
            raise RuntimeError("Stack empty")
        return self.items[self.idx - 1]
    
    def clear(self):
        self.idx = 0


# Utility functions
def clamp(x, a, b):
    """Clamp value between a and b"""
    return max(a, min(b, x))


def expand_rect(rect, n):
    """Expand rectangle by n pixels"""
    return Rect(rect.x - n, rect.y - n, rect.w + n * 2, rect.h + n * 2)


def intersect_rects(r1, r2):
    """Get intersection of two rectangles"""
    x1 = max(r1.x, r2.x)
    y1 = max(r1.y, r2.y)
    x2 = min(r1.x + r1.w, r2.x + r2.w)
    y2 = min(r1.y + r1.h, r2.y + r2.h)
    if x2 < x1:
        x2 = x1
    if y2 < y1:
        y2 = y1
    return Rect(x1, y1, x2 - x1, y2 - y1)


def rect_overlaps_vec2(r, p):
    """Check if point is inside rectangle"""
    return p.x >= r.x and p.x < r.x + r.w and p.y >= r.y and p.y < r.y + r.h


def hash_data(hash_val, data):
    """32-bit FNV-1a hash"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    elif isinstance(data, int):
        data = data.to_bytes(4, 'little')
    
    for byte in data:
        hash_val = ((hash_val ^ byte) * 16777619) & 0xFFFFFFFF
    return hash_val


class Context:
    """Main UI Context"""
    def __init__(self, text_width_fn, text_height_fn, framebuffer):
        logger.info("Initializing microui context")
        
        # Callbacks
        self.text_width = text_width_fn
        self.text_height = text_height_fn
        self.framebuffer = framebuffer
        
        # Style
        self.style = Style()
        
        # Core state
        self.hover = 0
        self.focus = 0
        self.last_id = 0
        self.last_rect = Rect()
        self.last_zindex = 0
        self.updated_focus = 0
        self.frame = 0
        self.hover_root = None
        self.next_hover_root = None
        self.scroll_target = None
        self.number_edit_buf = ""
        self.number_edit = 0
        
        # Stacks
        self.command_list = []
        self.root_list = Stack(MU_ROOTLIST_SIZE)
        self.container_stack = Stack(MU_CONTAINERSTACK_SIZE)
        self.clip_stack = Stack(MU_CLIPSTACK_SIZE)
        self.id_stack = Stack(MU_IDSTACK_SIZE)
        self.layout_stack = Stack(MU_LAYOUTSTACK_SIZE)
        
        # Pools
        self.container_pool = [PoolItem() for _ in range(MU_CONTAINERPOOL_SIZE)]
        self.containers = [Container() for _ in range(MU_CONTAINERPOOL_SIZE)]
        self.treenode_pool = [PoolItem() for _ in range(MU_TREENODEPOOL_SIZE)]
        
        # Input state
        self.mouse_pos = Vec2()
        self.last_mouse_pos = Vec2()
        self.mouse_delta = Vec2()
        self.scroll_delta = Vec2()
        self.mouse_down = 0
        self.mouse_pressed = 0
        self.key_down = 0
        self.key_pressed = 0
        self.input_text = ""
        
        # Unclipped rect
        self.unclipped_rect = Rect(0, 0, 0x1000000, 0x1000000)
        
        logger.debug("Context initialized successfully")
