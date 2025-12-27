# microui/layout.py
"""
Layout system for microui
"""
import logging
from .core import *

logger = logging.getLogger(__name__)

# Layout types
RELATIVE = const(1)
ABSOLUTE = const(2)


def push_layout(ctx, body, scroll):
    """Push new layout"""
    layout = Layout()
    layout.body = Rect(body.x - scroll.x, body.y - scroll.y, body.w, body.h)
    layout.max = Vec2(-0x1000000, -0x1000000)
    ctx.layout_stack.push(layout)
    
    width = 0
    layout_row(ctx, 1, [width], 0)


def get_layout(ctx):
    """Get current layout"""
    return ctx.layout_stack.top()


def layout_row(ctx, items, widths, height):
    """Setup layout row"""
    layout = get_layout(ctx)
    
    if widths:
        if items > MU_MAX_WIDTHS:
            raise ValueError(f"Too many items: {items} (max {MU_MAX_WIDTHS})")
        for i in range(items):
            layout.widths[i] = widths[i] if i < len(widths) else 0
    
    layout.items = items
    layout.position = Vec2(layout.indent, layout.next_row)
    layout.size.y = height
    layout.item_index = 0


def layout_width(ctx, width):
    """Set layout width"""
    get_layout(ctx).size.x = width


def layout_height(ctx, height):
    """Set layout height"""
    get_layout(ctx).size.y = height


def layout_begin_column(ctx):
    """Begin column layout"""
    push_layout(ctx, layout_next(ctx), Vec2(0, 0))


def layout_end_column(ctx):
    """End column layout"""
    b = get_layout(ctx)
    ctx.layout_stack.pop()
    
    # Inherit position/next_row/max from child
    a = get_layout(ctx)
    a.position.x = max(a.position.x, b.position.x + b.body.x - a.body.x)
    a.next_row = max(a.next_row, b.next_row + b.body.y - a.body.y)
    a.max.x = max(a.max.x, b.max.x)
    a.max.y = max(a.max.y, b.max.y)


def layout_set_next(ctx, r, relative):
    """Set next layout rect"""
    layout = get_layout(ctx)
    layout.next = r
    layout.next_type = RELATIVE if relative else ABSOLUTE


def layout_next(ctx):
    """Get next layout rect"""
    layout = get_layout(ctx)
    style = ctx.style
    
    if layout.next_type:
        # Handle rect set by layout_set_next
        type_val = layout.next_type
        layout.next_type = 0
        res = layout.next
        if type_val == ABSOLUTE:
            ctx.last_rect = res
            return res
    else:
        # Handle next row
        if layout.item_index == layout.items:
            layout_row(ctx, layout.items, None, layout.size.y)
        
        # Position
        res = Rect()
        res.x = layout.position.x
        res.y = layout.position.y
        
        # Size
        if layout.items > 0:
            res.w = layout.widths[layout.item_index]
        else:
            res.w = layout.size.x
        
        res.h = layout.size.y
        
        if res.w == 0:
            res.w = style.size.x + style.padding * 2
        if res.h == 0:
            res.h = style.size.y + style.padding * 2
        if res.w < 0:
            res.w += layout.body.w - res.x + 1
        if res.h < 0:
            res.h += layout.body.h - res.y + 1
        
        layout.item_index += 1
    
    # Update position
    layout.position.x += res.w + style.spacing
    layout.next_row = max(layout.next_row, res.y + res.h + style.spacing)
    
    # Apply body offset
    res.x += layout.body.x
    res.y += layout.body.y
    
    # Update max position
    layout.max.x = max(layout.max.x, res.x + res.w)
    layout.max.y = max(layout.max.y, res.y + res.h)
    
    ctx.last_rect = res
    return res
