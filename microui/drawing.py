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
        
        elif cmd.type == MU_COMMAND_CANVAS_TEXT:
            _render_canvas_text(ctx, cmd, clip_rect)
        
        
def _render_pixel(ctx, cmd, clip_rect):
    """Render pixel to framebuffer"""
    # Translate canvas coordinates to screen coordinates
    screen_x = int(cmd.canvas_rect.x + cmd.x)
    screen_y = int(cmd.canvas_rect.y + cmd.y)
    
    rgb565 = int(cmd.color.to_rgb565())
    ctx.framebuffer.pixel(screen_x, screen_y, rgb565)


def _render_line(ctx, cmd, clip_rect):
    """Render line to framebuffer"""
    # Translate canvas coordinates to screen coordinates
    screen_x1 = int(cmd.canvas_rect.x + cmd.x1)
    screen_y1 = int(cmd.canvas_rect.y + cmd.y1)
    screen_x2 = int(cmd.canvas_rect.x + cmd.x2)
    screen_y2 = int(cmd.canvas_rect.y + cmd.y2)
    
    rgb565 = int(cmd.color.to_rgb565())
    ctx.framebuffer.line(screen_x1, screen_y1, screen_x2, screen_y2, rgb565)


def _render_canvas_rect(ctx, cmd, clip_rect):
    """Render canvas rectangle to framebuffer"""
    # Translate canvas coordinates to screen coordinates
    screen_x = int(cmd.canvas_rect.x + cmd.x)
    screen_y = int(cmd.canvas_rect.y + cmd.y)
    
    rgb565 = int(cmd.color.to_rgb565())
    
    if cmd.filled:
        # Draw filled rectangle
        ctx.framebuffer.fill_rect(screen_x, screen_y, int(cmd.w), int(cmd.h), rgb565)
    else:
        # Draw rectangle outline
        # Top
        ctx.framebuffer.line(screen_x, screen_y, int(screen_x + cmd.w - 1), screen_y, rgb565)
        # Bottom
        ctx.framebuffer.line(screen_x, int(screen_y + cmd.h - 1), int(screen_x + cmd.w - 1), int(screen_y + cmd.h - 1), rgb565)
        # Left
        ctx.framebuffer.line(screen_x, screen_y, screen_x, int(screen_y + cmd.h - 1), rgb565)
        # Right
        ctx.framebuffer.line(int(screen_x + cmd.w - 1), screen_y, int(screen_x + cmd.w - 1), int(screen_y + cmd.h - 1), rgb565)


def _render_canvas_circle(ctx, cmd, clip_rect):
    """Render canvas circle to framebuffer"""
    # Translate canvas coordinates to screen coordinates
    screen_x = int(cmd.canvas_rect.x + cmd.x)
    screen_y = int(cmd.canvas_rect.y + cmd.y)
    
    rgb565 = int(cmd.color.to_rgb565())
    
    if cmd.filled:
        # For filled circles, we need to draw multiple circles or use a fill algorithm
        # Since framebuf.ellipse only draws outline, we'll fill by drawing concentric circles
#         for r in range(cmd.radius, 0, -1):
        ctx.framebuffer.ellipse(screen_x, screen_y, int(cmd.radius), int(cmd.radius), rgb565, 1, 0x0F)
    else:
        # Draw circle outline using ellipse
        ctx.framebuffer.ellipse(screen_x, screen_y, int(cmd.radius), int(cmd.radius), rgb565, 0, 0x0F)


def _render_canvas_text(ctx, cmd, clip_rect):
    """Render canvas text to framebuffer"""
    # Translate canvas coordinates to screen coordinates
    screen_x = int(cmd.canvas_rect.x + cmd.x)
    screen_y = int(cmd.canvas_rect.y + cmd.y)
    
    rgb565 = int(cmd.color.to_rgb565())
    ctx.framebuffer.text(cmd.text, screen_x, screen_y, rgb565)


def _render_rect(ctx, rect, color, clip_rect):
    """Render rectangle to framebuffer"""
    if clip_rect:
        rect = intersect_rects(rect, clip_rect)
    
    if rect.w <= 0 or rect.h <= 0:
        return
    
    # Convert color to RGB565
    rgb565 = int(color.to_rgb565())
    
    # Fill rectangle
    ctx.framebuffer.fill_rect(int(rect.x), int(rect.y), int(rect.w), int(rect.h), rgb565)


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
    rgb565 = int(cmd.color.to_rgb565())
    
    # Draw text
    ctx.framebuffer.text(cmd.text, int(cmd.pos.x), int(cmd.pos.y), rgb565)


def _render_icon(ctx, cmd, clip_rect):
    """Render icon to framebuffer"""
    if clip_rect:
        rect = intersect_rects(cmd.rect, clip_rect)
    else:
        rect = cmd.rect
    
    if rect.w <= 0 or rect.h <= 0:
        return
    
    rgb565 = int(cmd.color.to_rgb565())
    
    # Draw simple icon shapes
    if cmd.id == MU_ICON_CLOSE:
        # X shape
        x1, y1 = int(rect.x + 2), int(rect.y + 2)
        x2, y2 = int(rect.x + rect.w - 2), int(rect.y + rect.h - 2)
        ctx.framebuffer.line(x1, y1, x2, y2, rgb565)
        ctx.framebuffer.line(x2, y1, x1, y2, rgb565)
        
    elif cmd.id == MU_ICON_CHECK:
        # Checkmark
        x1 = int(rect.x + rect.w // 4)
        y1 = int(rect.y + rect.h // 2)
        x2 = int(rect.x + rect.w // 2)
        y2 = int(rect.y + rect.h - 3)
        x3 = int(rect.x + rect.w - 3)
        y3 = int(rect.y + 3)
        ctx.framebuffer.line(x1, y1, x2, y2, rgb565)
        ctx.framebuffer.line(x2, y2, x3, y3, rgb565)
        
    elif cmd.id == MU_ICON_COLLAPSED:
        # Right arrow
        x = int(rect.x + rect.w // 3)
        y = int(rect.y + rect.h // 2)
        for i in range(int(rect.h // 3)):
            ctx.framebuffer.line(x, int(y - i), int(x + i), y, rgb565)
            ctx.framebuffer.line(x, int(y + i), int(x + i), y, rgb565)
            
    elif cmd.id == MU_ICON_EXPANDED:
        # Down arrow
        x = int(rect.x + rect.w // 2)
        y = int(rect.y + rect.h // 3)
        for i in range(int(rect.w // 3)):
            ctx.framebuffer.line(int(x - i), y, x, int(y + i), rgb565)
            ctx.framebuffer.line(int(x + i), y, x, int(y + i), rgb565)


# Import get_clip_rect from context
from .context import get_clip_rect, check_clip