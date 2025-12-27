# microui/context.py
"""
Context methods for microui
"""
import logging
from .core import *

logger = logging.getLogger(__name__)


def begin(ctx):
    """Begin frame"""
    logger.debug(f"Begin frame {ctx.frame + 1}")
    
    if not ctx.text_width or not ctx.text_height:
        raise RuntimeError("text_width and text_height callbacks must be set")
    
    ctx.command_list.clear()
    ctx.root_list.clear()
    ctx.scroll_target = None
    ctx.hover_root = ctx.next_hover_root
    ctx.next_hover_root = None
    ctx.mouse_delta.x = ctx.mouse_pos.x - ctx.last_mouse_pos.x
    ctx.mouse_delta.y = ctx.mouse_pos.y - ctx.last_mouse_pos.y
    ctx.frame += 1


def end(ctx):
    """End frame"""
    logger.debug(f"End frame {ctx.frame}")
    
    # Check stacks are empty
    if ctx.container_stack.idx != 0:
        logger.error("Container stack not empty at end of frame")
    if ctx.clip_stack.idx != 0:
        logger.error("Clip stack not empty at end of frame")
    if ctx.id_stack.idx != 0:
        logger.error("ID stack not empty at end of frame")
    if ctx.layout_stack.idx != 0:
        logger.error("Layout stack not empty at end of frame")
    
    # Handle scroll input
    if ctx.scroll_target:
        ctx.scroll_target.scroll.x += ctx.scroll_delta.x
        ctx.scroll_target.scroll.y += ctx.scroll_delta.y
    
    # Unset focus if not touched this frame
    if not ctx.updated_focus:
        ctx.focus = 0
    ctx.updated_focus = 0
    
    # Bring hover root to front if mouse pressed
    if (ctx.mouse_pressed and ctx.next_hover_root and
        ctx.next_hover_root.zindex < ctx.last_zindex and
        ctx.next_hover_root.zindex >= 0):
        bring_to_front(ctx, ctx.next_hover_root)
    
    # Reset input state
    ctx.key_pressed = 0
    ctx.input_text = ""
    ctx.mouse_pressed = 0
    ctx.scroll_delta = Vec2(0, 0)
    ctx.last_mouse_pos = Vec2(ctx.mouse_pos.x, ctx.mouse_pos.y)
    
    # Sort root containers by zindex
    n = ctx.root_list.idx
    if n > 0:
        sorted_roots = sorted(
            ctx.root_list.items[:n],
            key=lambda c: c.zindex
        )
        ctx.root_list.items[:n] = sorted_roots
    
    # Set root container jump commands
    for i in range(n):
        cnt = ctx.root_list.items[i]
        if i == 0:
            if len(ctx.command_list) > 0:
                cmd = ctx.command_list[0]
                if isinstance(cmd, JumpCommand):
                    cmd.dst = cnt.head
        else:
            prev = ctx.root_list.items[i - 1]
            if prev.tail:
                prev.tail.dst = cnt.head
        
        if i == n - 1 and cnt.tail:
            cnt.tail.dst = None


def set_focus(ctx, id_val):
    """Set focused control"""
    logger.debug(f"Set focus to {id_val}")
    ctx.focus = id_val
    ctx.updated_focus = 1


def get_id(ctx, data):
    """Get ID from data"""
    idx = ctx.id_stack.idx
    res = ctx.id_stack.items[idx - 1] if idx > 0 else HASH_INITIAL
    res = hash_data(res, data)
    ctx.last_id = res
    return res


def push_id(ctx, data):
    """Push ID onto stack"""
    ctx.id_stack.push(get_id(ctx, data))


def pop_id(ctx):
    """Pop ID from stack"""
    ctx.id_stack.pop()


def push_clip_rect(ctx, rect):
    """Push clip rectangle"""
    last = get_clip_rect(ctx)
    ctx.clip_stack.push(intersect_rects(rect, last))


def pop_clip_rect(ctx):
    """Pop clip rectangle"""
    ctx.clip_stack.pop()


def get_clip_rect(ctx):
    """Get current clip rectangle"""
    if ctx.clip_stack.idx <= 0:
        raise RuntimeError("Clip stack empty")
    return ctx.clip_stack.items[ctx.clip_stack.idx - 1]


def check_clip(ctx, r):
    """Check if rectangle is clipped"""
    cr = get_clip_rect(ctx)
    if (r.x > cr.x + cr.w or r.x + r.w < cr.x or
        r.y > cr.y + cr.h or r.y + r.h < cr.y):
        return MU_CLIP_ALL
    if (r.x >= cr.x and r.x + r.w <= cr.x + cr.w and
        r.y >= cr.y and r.y + r.h <= cr.y + cr.h):
        return 0
    return MU_CLIP_PART


def get_current_container(ctx):
    """Get current container"""
    if ctx.container_stack.idx <= 0:
        raise RuntimeError("Container stack empty")
    return ctx.container_stack.items[ctx.container_stack.idx - 1]


def get_container(ctx, name):
    """Get container by name"""
    id_val = get_id(ctx, name)
    return _get_container(ctx, id_val, 0)


def _get_container(ctx, id_val, opt):
    """Internal get container"""
    # Try to get existing container from pool
    idx = pool_get(ctx, ctx.container_pool, id_val)
    if idx >= 0:
        if ctx.containers[idx].open or not (opt & MU_OPT_CLOSED):
            pool_update(ctx, ctx.container_pool, idx)
        return ctx.containers[idx]
    
    if opt & MU_OPT_CLOSED:
        return None
    
    # Container not found: init new
    idx = pool_init(ctx, ctx.container_pool, id_val)
    cnt = ctx.containers[idx]
    cnt.__init__()  # Reset
    cnt.open = 1
    bring_to_front(ctx, cnt)
    return cnt


def bring_to_front(ctx, cnt):
    """Bring container to front"""
    ctx.last_zindex += 1
    cnt.zindex = ctx.last_zindex
    logger.debug(f"Brought container to front with zindex {cnt.zindex}")


# Pool functions
def pool_init(ctx, items, id_val):
    """Initialize pool item"""
    n = -1
    f = ctx.frame
    for i in range(len(items)):
        if items[i].last_update < f:
            f = items[i].last_update
            n = i
    
    if n < 0:
        raise RuntimeError("Pool full")
    
    items[n].id = id_val
    pool_update(ctx, items, n)
    return n


def pool_get(ctx, items, id_val):
    """Get pool item by ID"""
    for i in range(len(items)):
        if items[i].id == id_val:
            return i
    return -1


def pool_update(ctx, items, idx):
    """Update pool item"""
    items[idx].last_update = ctx.frame


# Input handlers
def input_mousemove(ctx, x, y):
    """Handle mouse move"""
    ctx.mouse_pos.x = x
    ctx.mouse_pos.y = y


def input_mousedown(ctx, x, y, btn):
    """Handle mouse down"""
    input_mousemove(ctx, x, y)
    ctx.mouse_down |= btn
    ctx.mouse_pressed |= btn
    logger.debug(f"Mouse down at ({x}, {y}), btn={btn}")


def input_mouseup(ctx, x, y, btn):
    """Handle mouse up"""
    input_mousemove(ctx, x, y)
    ctx.mouse_down &= ~btn
    logger.debug(f"Mouse up at ({x}, {y}), btn={btn}")


def input_scroll(ctx, x, y):
    """Handle scroll"""
    ctx.scroll_delta.x += x
    ctx.scroll_delta.y += y


def input_keydown(ctx, key):
    """Handle key down"""
    ctx.key_pressed |= key
    ctx.key_down |= key


def input_keyup(ctx, key):
    """Handle key up"""
    ctx.key_down &= ~key


def input_text(ctx, text):
    """Handle text input"""
    ctx.input_text += text
