# microui/windows.py
"""
Window and panel management for microui
"""
import logging
from .core import *
from .context import (get_id, push_id, pop_id, get_current_container, 
                     _get_container, bring_to_front, push_clip_rect, 
                     pop_clip_rect, set_focus)
from .drawing import draw_frame, draw_icon, push_jump
from .layout import push_layout, get_layout, expand_rect, layout_next

logger = logging.getLogger(__name__)


def push_container_body(ctx, cnt, body, opt):
    """Push container body"""
    if not (opt & MU_OPT_NOSCROLL):
        _scrollbars(ctx, cnt, body)
    
    push_layout(ctx, expand_rect(body, -ctx.style.padding), cnt.scroll)
    cnt.body = body


def _scrollbars(ctx, cnt, body):
    """Add scrollbars to container"""
    sz = ctx.style.scrollbar_size
    cs = Vec2(cnt.content_size.x, cnt.content_size.y)
    cs.x += ctx.style.padding * 2
    cs.y += ctx.style.padding * 2
    
    push_clip_rect(ctx, body)
    
    # Resize body for scrollbars
    if cs.y > cnt.body.h:
        body.w -= sz
    if cs.x > cnt.body.w:
        body.h -= sz
    
    # Vertical scrollbar
    _scrollbar(ctx, cnt, body, cs, True)
    # Horizontal scrollbar
    _scrollbar(ctx, cnt, body, cs, False)
    
    pop_clip_rect(ctx)


def _scrollbar(ctx, cnt, body, cs, vertical):
    """Draw scrollbar"""
    from .controls import update_control, mouse_over
    
    if vertical:
        maxscroll = cs.y - body.h
        if maxscroll <= 0 or body.h <= 0:
            cnt.scroll.y = 0
            return
        
        id_val = get_id(ctx, "!scrollbary")
        
        base = Rect(body.x + body.w, body.y, ctx.style.scrollbar_size, body.h)
        
        update_control(ctx, id_val, base, 0)
        
        if ctx.focus == id_val and ctx.mouse_down == MU_MOUSE_LEFT:
            cnt.scroll.y += ctx.mouse_delta.y * cs.y / base.h
        
        cnt.scroll.y = clamp(cnt.scroll.y, 0, maxscroll)
        
        draw_frame(ctx, base, MU_COLOR_SCROLLBASE)
        
        thumb = Rect(base.x, base.y, base.w, 
                    max(ctx.style.thumb_size, base.h * body.h // cs.y))
        thumb.y += int(cnt.scroll.y * (base.h - thumb.h) / maxscroll) if maxscroll else 0
        
        draw_frame(ctx, thumb, MU_COLOR_SCROLLTHUMB)
        
        if mouse_over(ctx, body):
            ctx.scroll_target = cnt
    else:
        maxscroll = cs.x - body.w
        if maxscroll <= 0 or body.w <= 0:
            cnt.scroll.x = 0
            return
        
        id_val = get_id(ctx, "!scrollbarx")
        
        base = Rect(body.x, body.y + body.h, body.w, ctx.style.scrollbar_size)
        
        update_control(ctx, id_val, base, 0)
        
        if ctx.focus == id_val and ctx.mouse_down == MU_MOUSE_LEFT:
            cnt.scroll.x += ctx.mouse_delta.x * cs.x / base.w
        
        cnt.scroll.x = clamp(cnt.scroll.x, 0, maxscroll)
        
        draw_frame(ctx, base, MU_COLOR_SCROLLBASE)
        
        thumb = Rect(base.x, base.y, 
                    max(ctx.style.thumb_size, base.w * body.w // cs.x), base.h)
        thumb.x += int(cnt.scroll.x * (base.w - thumb.w) / maxscroll) if maxscroll else 0
        
        draw_frame(ctx, thumb, MU_COLOR_SCROLLTHUMB)
        
        if mouse_over(ctx, body):
            ctx.scroll_target = cnt


def begin_root_container(ctx, cnt):
    """Begin root container"""
    ctx.container_stack.push(cnt)
    
    # Push to roots list
    ctx.root_list.push(cnt)
    cnt.head = push_jump(ctx, None)
    
    # Set hover root
    if (rect_overlaps_vec2(cnt.rect, ctx.mouse_pos) and
        (not ctx.next_hover_root or cnt.zindex > ctx.next_hover_root.zindex)):
        ctx.next_hover_root = cnt
    
    # Reset clipping
    ctx.clip_stack.push(ctx.unclipped_rect)


def end_root_container(ctx):
    """End root container"""
    cnt = get_current_container(ctx)
    cnt.tail = push_jump(ctx, None)
    cnt.head.dst = len(ctx.command_list)
    
    pop_clip_rect(ctx)
    _pop_container(ctx)


def _pop_container(ctx):
    """Pop container from stack"""
    cnt = get_current_container(ctx)
    layout = get_layout(ctx)
    
    cnt.content_size.x = layout.max.x - layout.body.x
    cnt.content_size.y = layout.max.y - layout.body.y
    
    ctx.container_stack.pop()
    ctx.layout_stack.pop()
    pop_id(ctx)


def begin_window_ex(ctx, title, rect, opt):
    """Begin window"""
    id_val = get_id(ctx, title)
    cnt = _get_container(ctx, id_val, opt)
    
    if not cnt or not cnt.open:
        return False
    
    push_id(ctx, id_val)
    
    if cnt.rect.w == 0:
        cnt.rect = rect
    
    begin_root_container(ctx, cnt)
    rect = cnt.rect
    body = Rect(rect.x, rect.y, rect.w, rect.h)
    
    # Draw frame
    if not (opt & MU_OPT_NOFRAME):
        draw_frame(ctx, rect, MU_COLOR_WINDOWBG)
    
    # Do title bar
    if not (opt & MU_OPT_NOTITLE):
        from .controls import update_control, draw_control_text
        
        tr = Rect(rect.x, rect.y, rect.w, ctx.style.title_height)
        draw_frame(ctx, tr, MU_COLOR_TITLEBG)
        
        # Title text
        title_id = get_id(ctx, "!title")
        update_control(ctx, title_id, tr, opt)
        draw_control_text(ctx, title, tr, MU_COLOR_TITLETEXT, opt)
        
        if title_id == ctx.focus and ctx.mouse_down == MU_MOUSE_LEFT:
            cnt.rect.x += ctx.mouse_delta.x
            cnt.rect.y += ctx.mouse_delta.y
        
        body.y += tr.h
        body.h -= tr.h
        
        # Close button
        if not (opt & MU_OPT_NOCLOSE):
            close_id = get_id(ctx, "!close")
            r = Rect(tr.x + tr.w - tr.h, tr.y, tr.h, tr.h)
            tr.w -= r.w
            
            draw_icon(ctx, MU_ICON_CLOSE, r, ctx.style.colors[MU_COLOR_TITLETEXT])
            update_control(ctx, close_id, r, opt)
            
            if ctx.mouse_pressed == MU_MOUSE_LEFT and close_id == ctx.focus:
                cnt.open = 0
    
    push_container_body(ctx, cnt, body, opt)
    
    # Resize handle
    if not (opt & MU_OPT_NORESIZE):
        from .controls import update_control
        
        sz = ctx.style.title_height
        resize_id = get_id(ctx, "!resize")
        r = Rect(rect.x + rect.w - sz, rect.y + rect.h - sz, sz, sz)
        
        update_control(ctx, resize_id, r, opt)
        
        if resize_id == ctx.focus and ctx.mouse_down == MU_MOUSE_LEFT:
            cnt.rect.w = max(96, cnt.rect.w + ctx.mouse_delta.x)
            cnt.rect.h = max(64, cnt.rect.h + ctx.mouse_delta.y)
    
    # Auto size
    if opt & MU_OPT_AUTOSIZE:
        r = get_layout(ctx).body
        cnt.rect.w = cnt.content_size.x + (cnt.rect.w - r.w)
        cnt.rect.h = cnt.content_size.y + (cnt.rect.h - r.h)
    
    # Close popup if clicked elsewhere
    if opt & MU_OPT_POPUP and ctx.mouse_pressed and ctx.hover_root != cnt:
        cnt.open = 0
    
    push_clip_rect(ctx, cnt.body)
    return True


def begin_window(ctx, title, rect):
    """Simple window"""
    return begin_window_ex(ctx, title, rect, 0)


def end_window(ctx):
    """End window"""
    pop_clip_rect(ctx)
    end_root_container(ctx)


def open_popup(ctx, name):
    """Open popup window"""
    from .context import get_container
    
    cnt = get_container(ctx, name)
    ctx.hover_root = ctx.next_hover_root = cnt
    cnt.rect = Rect(ctx.mouse_pos.x, ctx.mouse_pos.y, 1, 1)
    cnt.open = 1
    bring_to_front(ctx, cnt)


def begin_popup(ctx, name):
    """Begin popup"""
    opt = (MU_OPT_POPUP | MU_OPT_AUTOSIZE | MU_OPT_NORESIZE |
           MU_OPT_NOSCROLL | MU_OPT_NOTITLE | MU_OPT_CLOSED)
    return begin_window_ex(ctx, name, Rect(0, 0, 0, 0), opt)


def end_popup(ctx):
    """End popup"""
    end_window(ctx)


def begin_panel_ex(ctx, name, opt):
    """Begin panel"""
    push_id(ctx, name)
    cnt = _get_container(ctx, ctx.last_id, opt)
    cnt.rect = layout_next(ctx)
    
    if not (opt & MU_OPT_NOFRAME):
        draw_frame(ctx, cnt.rect, MU_COLOR_PANELBG)
    
    ctx.container_stack.push(cnt)
    push_container_body(ctx, cnt, cnt.rect, opt)
    push_clip_rect(ctx, cnt.body)


def begin_panel(ctx, name):
    """Simple panel"""
    begin_panel_ex(ctx, name, 0)


def end_panel(ctx):
    """End panel"""
    pop_clip_rect(ctx)
    _pop_container(ctx)
