# microui/drawing.py
"""
Drawing functions for microui
"""
import logging
from .core import *

logger = logging.getLogger(__name__)


def push_command(ctx, cmd):
    """Push command to list"""
    ctx.command_list.append(cmd)
    return cmd


def next_command(ctx):
    """Iterator for commands - simplified version"""
    for cmd in ctx.command_list:
        # Skip jump commands, just yield regular commands
        if cmd.type != MU_COMMAND_JUMP:
            yield cmd


def push_jump(ctx, dst):
    """Push jump command"""
    cmd = JumpCommand()
    cmd.dst = dst
    return push_command(ctx, cmd)


def set_clip(ctx, rect):
    """Set clip rectangle"""
    cmd = ClipCommand(rect)
    push_command(ctx, cmd)


def draw_rect(ctx, rect, color):
    """Draw filled rectangle"""
    rect = intersect_rects(rect, get_clip_rect(ctx))
    if rect.w > 0 and rect.h > 0:
        cmd = RectCommand(rect, color)
        push_command(ctx, cmd)


def draw_box(ctx, rect, color):
    """Draw rectangle outline"""
    # Top
    draw_rect(ctx, Rect(rect.x + 1, rect.y, rect.w - 2, 1), color)
    # Bottom
    draw_rect(ctx, Rect(rect.x + 1, rect.y + rect.h - 1, rect.w - 2, 1), color)
    # Left
    draw_rect(ctx, Rect(rect.x, rect.y, 1, rect.h), color)
    # Right
    draw_rect(ctx, Rect(rect.x + rect.w - 1, rect.y, 1, rect.h), color)


def draw_text(ctx, font, text, pos, color):
    """Draw text"""
    text_w = ctx.text_width(font, text)
    text_h = ctx.text_height(font)
    rect = Rect(pos.x, pos.y, text_w, text_h)
    
    clipped = check_clip(ctx, rect)
    if clipped == MU_CLIP_ALL:
        return
    if clipped == MU_CLIP_PART:
        set_clip(ctx, get_clip_rect(ctx))
    
    cmd = TextCommand(font, pos, color, text)
    push_command(ctx, cmd)
    
    if clipped:
        set_clip(ctx, ctx.unclipped_rect)


def draw_icon(ctx, icon_id, rect, color):
    """Draw icon"""
    clipped = check_clip(ctx, rect)
    if clipped == MU_CLIP_ALL:
        return
    if clipped == MU_CLIP_PART:
        set_clip(ctx, get_clip_rect(ctx))
    
    cmd = IconCommand(icon_id, rect, color)
    push_command(ctx, cmd)
    
    if clipped:
        set_clip(ctx, ctx.unclipped_rect)


def draw_frame(ctx, rect, colorid):
    """Draw control frame"""
    draw_rect(ctx, rect, ctx.style.colors[colorid])
    
    # Skip border for certain elements
    if colorid in (MU_COLOR_SCROLLBASE, MU_COLOR_SCROLLTHUMB, MU_COLOR_TITLEBG):
        return
    
    # Draw border
    if ctx.style.colors[MU_COLOR_BORDER].a:
        draw_box(ctx, expand_rect(rect, 1), ctx.style.colors[MU_COLOR_BORDER])


# Rendering to framebuffer
def render_commands(ctx):
    """Render all commands to framebuffer"""
    logger.debug(f"Rendering {len(ctx.command_list)} commands")
    
    clip_rect = None
 
    for cmd in next_command(ctx):
        if cmd.type == MU_COMMAND_JUMP:
            logger.debug(f"Jump to command at {cmd.dst}")
            # In this simplified version, we just continue
            continue
        
        elif cmd.type == MU_COMMAND_CLIP:
            clip_rect = cmd.rect
            logger.debug(f"Set clip: {clip_rect}")
            
        elif cmd.type == MU_COMMAND_RECT:
            _render_rect(ctx, cmd.rect, cmd.color, clip_rect)
            
        elif cmd.type == MU_COMMAND_TEXT:
            _render_text(ctx, cmd, clip_rect)
            
        elif cmd.type == MU_COMMAND_ICON:
            _render_icon(ctx, cmd, clip_rect)
        
        elif cmd.type == MU_COMMAND_CANVAS_PIXEL:
            _render_pixel(ctx, cmd, clip_rect)
        
        elif cmd.type == MU_COMMAND_CANVAS_LINE:
            _render_line(ctx, cmd, clip_rect)
        
        elif cmd.type == MU_COMMAND_CANVAS_RECT:
            _render_canvas_rect(ctx, cmd, clip_rect)
        
        elif cmd.type == MU_COMMAND_CANVAS_CIRCLE:
            _render_canvas_circle(ctx, cmd, clip_rect)
        
        
def _render_pixel(ctx, cmd, clip_rect):
    """Render pixel to framebuffer"""
    #if clip_rect and not point_in_rect(cmd.pos, clip_rect):
    #    return
    
    rgb565 = cmd.color.to_rgb565()
    #ctx.framebuffer.pixel(cmd.pos.x, cmd.pos.y, rgb565)
    ctx.framebuffer.pixel(cmd.x, cmd.y, rgb565)

def _render_line(ctx, cmd, clip_rect):
    """Render line to framebuffer"""
    # Simple clipping: skip if both endpoints are outside clip rect
    #if clip_rect:
    #    if not (point_in_rect(cmd.start, clip_rect) or point_in_rect(cmd.end, clip_rect)):
    #        return
    
    rgb565 = cmd.color.to_rgb565()
    #ctx.framebuffer.line(cmd.start.x, cmd.start.y, cmd.end.x, cmd.end.y, rgb565)
    ctx.framebuffer.line(cmd.x1, cmd.y1, cmd.x2, cmd.y2, rgb565)

def _render_canvas_rect(ctx, cmd, clip_rect):
    """Render canvas rectangle to framebuffer"""
    rect = cmd.canvas_rect
    #if clip_rect:
    #    rect = intersect_rects(rect, clip_rect)
    
    if rect.w <= 0 or rect.h <= 0:
        return
    
    rgb565 = cmd.color.to_rgb565()
    
    # Draw rectangle outline
    #ctx.framebuffer.rect(rect.x, rect.y, rect.w, rect.h, rgb565)
    ctx.framebuffer.line(rect.x, rect.y, rect.x + rect.w - 1, rect.y, rgb565)
    # Bottom
    ctx.framebuffer.line(rect.x, rect.y + rect.h - 1, rect.x + rect.w - 1, rect.y + rect.h - 1, rgb565)
    # Left
    ctx.framebuffer.line(rect.x, rect.y, rect.x, rect.y + rect.h - 1, rgb565)
    # Right
    ctx.framebuffer.line(rect.x + rect.w - 1, rect.y, rect.x + rect.w - 1, rect.y + rect.h - 1, rgb565)


def _render_canvas_circle(ctx, cmd, clip_rect):
    """Render canvas circle to framebuffer"""
    #center = cmd.center
    center_x = cmd.x
    center_y = cmd.y
    
    radius = cmd.radius
    
    # Simple bounding box clipping
    bounding_rect = Rect(center_x - radius, center_y - radius, radius * 2, radius * 2)
    if clip_rect:
        bounding_rect = intersect_rects(bounding_rect, clip_rect)
    
    if bounding_rect.w <= 0 or bounding_rect.h <= 0:
        return
    
    rgb565 = cmd.color.to_rgb565()
    
    # Draw usin ellipse
    ctx.framebuffer.ellipse(center_x, center_y, radius, radius, rgb565)

def _render_rect(ctx, rect, color, clip_rect):
    """Render rectangle to framebuffer"""
    if clip_rect:
        rect = intersect_rects(rect, clip_rect)
    
    if rect.w <= 0 or rect.h <= 0:
        return
    
    # Convert color to RGB565
    rgb565 = color.to_rgb565()
    
    # Fill rectangle
    ctx.framebuffer.fill_rect(rect.x, rect.y, rect.w, rect.h, rgb565)


def _render_text(ctx, cmd, clip_rect):
    """Render text to framebuffer"""
    rect = Rect(cmd.pos.x, cmd.pos.y, 
                ctx.text_width(cmd.font, cmd.text),
                ctx.text_height(cmd.font))
    
    if clip_rect:
        rect = intersect_rects(rect, clip_rect)
    
    if rect.w <= 0 or rect.h <= 0:
        return
    
    # Convert color to RGB565
    rgb565 = cmd.color.to_rgb565()
    
    # Draw text
    ctx.framebuffer.text(cmd.text, cmd.pos.x, cmd.pos.y, rgb565)


def _render_icon(ctx, cmd, clip_rect):
    """Render icon to framebuffer"""
    if clip_rect:
        rect = intersect_rects(cmd.rect, clip_rect)
    else:
        rect = cmd.rect
    
    if rect.w <= 0 or rect.h <= 0:
        return
    
    rgb565 = cmd.color.to_rgb565()
    
    # Draw simple icon shapes
    if cmd.id == MU_ICON_CLOSE:
        # X shape
        x1, y1 = rect.x + 2, rect.y + 2
        x2, y2 = rect.x + rect.w - 2, rect.y + rect.h - 2
        ctx.framebuffer.line(x1, y1, x2, y2, rgb565)
        ctx.framebuffer.line(x2, y1, x1, y2, rgb565)
        
    elif cmd.id == MU_ICON_CHECK:
        # Checkmark
        x1 = rect.x + rect.w // 4
        y1 = rect.y + rect.h // 2
        x2 = rect.x + rect.w // 2
        y2 = rect.y + rect.h - 3
        x3 = rect.x + rect.w - 3
        y3 = rect.y + 3
        ctx.framebuffer.line(x1, y1, x2, y2, rgb565)
        ctx.framebuffer.line(x2, y2, x3, y3, rgb565)
        
    elif cmd.id == MU_ICON_COLLAPSED:
        # Right arrow
        x = rect.x + rect.w // 3
        y = rect.y + rect.h // 2
        for i in range(rect.h // 3):
            ctx.framebuffer.line(x, y - i, x + i, y, rgb565)
            ctx.framebuffer.line(x, y + i, x + i, y, rgb565)
            
    elif cmd.id == MU_ICON_EXPANDED:
        # Down arrow
        x = rect.x + rect.w // 2
        y = rect.y + rect.h // 3
        for i in range(rect.w // 3):
            ctx.framebuffer.line(x - i, y, x, y + i, rgb565)
            ctx.framebuffer.line(x + i, y, x, y + i, rgb565)


# Import get_clip_rect from context
from .context import get_clip_rect, check_clip
