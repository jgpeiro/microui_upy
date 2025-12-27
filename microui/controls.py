# microui/controls.py
"""
UI controls for microui
"""
import logging
from .core import *
from .context import get_id, set_focus, get_clip_rect, pool_get, pool_update, pool_init
from .drawing import draw_rect, draw_text, draw_icon, draw_frame
from .layout import get_layout, layout_next, layout_row, layout_begin_column, layout_end_column

logger = logging.getLogger(__name__)


def in_hover_root(ctx):
    """Check if in hover root"""
    # If no containers, allow interaction (for testing without windows)
    if ctx.container_stack.idx == 0:
        return True
    
    i = ctx.container_stack.idx
    while i > 0:
        i -= 1
        if ctx.container_stack.items[i] == ctx.hover_root:
            return True
        if ctx.container_stack.items[i].head:
            break
    return False


def mouse_over(ctx, rect):
    """Check if mouse is over rect"""
    return (rect_overlaps_vec2(rect, ctx.mouse_pos) and
            rect_overlaps_vec2(get_clip_rect(ctx), ctx.mouse_pos) and
            in_hover_root(ctx))


def update_control(ctx, id_val, rect, opt):
    """Update control state"""
    mouseover = mouse_over(ctx, rect)
    
    if ctx.focus == id_val:
        ctx.updated_focus = 1
    
    if opt & MU_OPT_NOINTERACT:
        return
    
    if mouseover and not ctx.mouse_down:
        ctx.hover = id_val
    
    if ctx.focus == id_val:
        if ctx.mouse_pressed and not mouseover:
            set_focus(ctx, 0)
        if not ctx.mouse_down and not (opt & MU_OPT_HOLDFOCUS):
            set_focus(ctx, 0)
    
    if ctx.hover == id_val:
        if ctx.mouse_pressed:
            set_focus(ctx, id_val)
        elif not mouseover:
            ctx.hover = 0


def draw_control_frame(ctx, id_val, rect, colorid, opt):
    """Draw control frame"""
    if opt & MU_OPT_NOFRAME:
        return
    
    if ctx.focus == id_val:
        colorid += 2
    elif ctx.hover == id_val:
        colorid += 1
    
    draw_frame(ctx, rect, colorid)


def draw_control_text(ctx, text, rect, colorid, opt):
    """Draw control text"""
    font = ctx.style.font
    tw = ctx.text_width(font, text)
    th = ctx.text_height(font)
    
    from .context import push_clip_rect, pop_clip_rect
    push_clip_rect(ctx, rect)
    
    pos = Vec2()
    pos.y = rect.y + (rect.h - th) // 2
    
    if opt & MU_OPT_ALIGNCENTER:
        pos.x = rect.x + (rect.w - tw) // 2
    elif opt & MU_OPT_ALIGNRIGHT:
        pos.x = rect.x + rect.w - tw - ctx.style.padding
    else:
        pos.x = rect.x + ctx.style.padding
    
    draw_text(ctx, font, text, pos, ctx.style.colors[colorid])
    pop_clip_rect(ctx)


def text(ctx, text_str):
    """Display text with word wrap"""
    font = ctx.style.font
    color = ctx.style.colors[MU_COLOR_TEXT]
    width = -1
    
    layout_begin_column(ctx)
    layout_row(ctx, 1, [width], ctx.text_height(font))
    
    # Simple word wrapping
    words = text_str.split()
    line = ""
    
    for word in words:
        test_line = line + (" " if line else "") + word
        if ctx.text_width(font, test_line) > get_layout(ctx).body.w:
            if line:
                r = layout_next(ctx)
                draw_text(ctx, font, line, Vec2(r.x, r.y), color)
                line = word
            else:
                r = layout_next(ctx)
                draw_text(ctx, font, word, Vec2(r.x, r.y), color)
        else:
            line = test_line
    
    if line:
        r = layout_next(ctx)
        draw_text(ctx, font, line, Vec2(r.x, r.y), color)
    
    layout_end_column(ctx)


def label(ctx, text_str):
    """Display label"""
    draw_control_text(ctx, text_str, layout_next(ctx), MU_COLOR_TEXT, 0)


def button_ex(ctx, label_str, icon, opt):
    """Button control"""
    res = 0
    
    if label_str:
        id_val = get_id(ctx, label_str)
    else:
        id_val = get_id(ctx, str(icon))
    
    r = layout_next(ctx)
    update_control(ctx, id_val, r, opt)
    
    # Handle click
    if ctx.mouse_pressed == MU_MOUSE_LEFT and ctx.focus == id_val:
        res |= MU_RES_SUBMIT
    
    # Draw
    draw_control_frame(ctx, id_val, r, MU_COLOR_BUTTON, opt)
    
    if label_str:
        draw_control_text(ctx, label_str, r, MU_COLOR_TEXT, opt)
    
    if icon:
        draw_icon(ctx, icon, r, ctx.style.colors[MU_COLOR_TEXT])
    
    return res


def button(ctx, label_str):
    """Simple button"""
    return button_ex(ctx, label_str, 0, MU_OPT_ALIGNCENTER)


def checkbox(ctx, label_str, state):
    """Checkbox control - returns (result, new_state)"""
    res = 0
    
    id_val = get_id(ctx, label_str)
    r = layout_next(ctx)
    box = Rect(r.x, r.y, r.h, r.h)
    
    update_control(ctx, id_val, r, 0)
    
    # Handle click
    if ctx.mouse_pressed == MU_MOUSE_LEFT and ctx.focus == id_val:
        res |= MU_RES_CHANGE
        state = not state
    
    # Draw
    draw_control_frame(ctx, id_val, box, MU_COLOR_BASE, 0)
    
    if state:
        draw_icon(ctx, MU_ICON_CHECK, box, ctx.style.colors[MU_COLOR_TEXT])
    
    r = Rect(r.x + box.w, r.y, r.w - box.w, r.h)
    draw_control_text(ctx, label_str, r, MU_COLOR_TEXT, 0)
    
    return res, state


def slider_ex(ctx, value, low, high, step, fmt, opt):
    """Slider control - returns (result, new_value)"""
    res = 0
    last = value
    v = last
    
    id_val = get_id(ctx, str(id(value)))
    base = layout_next(ctx)
    
    # Handle normal mode
    update_control(ctx, id_val, base, opt)
    
    # Handle input
    if (ctx.focus == id_val and 
        (ctx.mouse_down | ctx.mouse_pressed) == MU_MOUSE_LEFT):
        v = low + (ctx.mouse_pos.x - base.x) * (high - low) / base.w
        if step:
            v = round(v / step) * step
    
    # Clamp value
    value = v = clamp(v, low, high)
    if last != v:
        res |= MU_RES_CHANGE
    
    # Draw base
    draw_control_frame(ctx, id_val, base, MU_COLOR_BASE, opt)
    
    # Draw thumb
    w = ctx.style.thumb_size
    x = int((v - low) * (base.w - w) / (high - low)) if high != low else 0
    thumb = Rect(base.x + x, base.y, w, base.h)
    draw_control_frame(ctx, id_val, thumb, MU_COLOR_BUTTON, opt)
    
    # Draw text
    buf = fmt % v
    draw_control_text(ctx, buf, base, MU_COLOR_TEXT, opt)
    
    return res, value


def slider(ctx, value, low, high):
    """Simple slider"""
    return slider_ex(ctx, value, low, high, 0, "%.2f", MU_OPT_ALIGNCENTER)


def header_ex(ctx, label_str, opt):
    """Header control"""
    return _header(ctx, label_str, False, opt)


def header(ctx, label_str):
    """Simple header"""
    return header_ex(ctx, label_str, 0)


def begin_treenode_ex(ctx, label_str, opt):
    """Begin tree node"""
    res = _header(ctx, label_str, True, opt)
    if res & MU_RES_ACTIVE:
        get_layout(ctx).indent += ctx.style.indent
        from .context import push_id
        push_id(ctx, ctx.last_id)
    return res


def begin_treenode(ctx, label_str):
    """Simple tree node"""
    return begin_treenode_ex(ctx, label_str, 0)


def end_treenode(ctx):
    """End tree node"""
    get_layout(ctx).indent -= ctx.style.indent
    from .context import pop_id
    pop_id(ctx)


def _header(ctx, label_str, is_treenode, opt):
    """Internal header implementation"""
    id_val = get_id(ctx, label_str)
    idx = pool_get(ctx, ctx.treenode_pool, id_val)
    
    width = -1
    layout_row(ctx, 1, [width], 0)
    
    active = (idx >= 0)
    expanded = (not active) if (opt & MU_OPT_EXPANDED) else active
    
    r = layout_next(ctx)
    update_control(ctx, id_val, r, 0)
    
    # Handle click
    if ctx.mouse_pressed == MU_MOUSE_LEFT and ctx.focus == id_val:
        active = not active
    
    # Update pool
    if idx >= 0:
        if active:
            pool_update(ctx, ctx.treenode_pool, idx)
        else:
            ctx.treenode_pool[idx] = PoolItem()
    elif active:
        pool_init(ctx, ctx.treenode_pool, id_val)
    
    # Draw
    if is_treenode:
        if ctx.hover == id_val:
            draw_frame(ctx, r, MU_COLOR_BUTTONHOVER)
    else:
        draw_control_frame(ctx, id_val, r, MU_COLOR_BUTTON, 0)
    
    icon = MU_ICON_EXPANDED if expanded else MU_ICON_COLLAPSED
    draw_icon(ctx, icon, Rect(r.x, r.y, r.h, r.h), 
              ctx.style.colors[MU_COLOR_TEXT])
    
    r.x += r.h - ctx.style.padding
    r.w -= r.h - ctx.style.padding
    draw_control_text(ctx, label_str, r, MU_COLOR_TEXT, 0)
    
    return MU_RES_ACTIVE if expanded else 0
