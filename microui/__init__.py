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


