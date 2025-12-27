"""
Demo 4: Canvas Drawing
Demonstrates the canvas widget with various drawing primitives
"""
from microui import *
import math

# UI state for Demo 4
ui_state = {
    'animation_time': 0,
    'draw_mode': 'shapes',  # 'shapes', 'plot', 'art'
}


def update_ui(ctx):
    """Demo 4: Canvas Drawing"""
    
    # Main window - full screen for 320x240 or larger
    if begin_window_ex(ctx, "Demo 4: Canvas Drawing", Rect(10, 10, 380, 580), 
                       MU_OPT_NOCLOSE|MU_OPT_NORESIZE):
        
        # Title label
        label(ctx, "=== CANVAS DEMO ===")
        
        # Mode selection buttons
        layout_row(ctx, 3, [120, 120, -1], 0)
        if button(ctx, "Shapes"):
            ui_state['draw_mode'] = 'shapes'
        if button(ctx, "Plot"):
            ui_state['draw_mode'] = 'plot'
        if button(ctx, "Art"):
            ui_state['draw_mode'] = 'art'
        
        layout_row(ctx, 1, [-1], 0)
        label(ctx, f"Mode: {ui_state['draw_mode']}")
        
        # Canvas widget
        layout_row(ctx, 1, [-1], 300)
        cv = canvas(ctx, 360, 280)
        
        # Update animation time
        ui_state['animation_time'] += 1
        
        # Draw based on current mode
        if ui_state['draw_mode'] == 'shapes':
            draw_shapes_demo(cv, ui_state['animation_time'])
        elif ui_state['draw_mode'] == 'plot':
            draw_plot_demo(cv, ui_state['animation_time'])
        elif ui_state['draw_mode'] == 'art':
            draw_art_demo(cv, ui_state['animation_time'])
        
        # Info
        layout_row(ctx, 1, [-1], 0)
        label(ctx, f"Frame: {ui_state['animation_time']}")
        label(ctx, "Canvas supports: pixel, line, rect, circle, text")
        
        end_window(ctx)


def draw_shapes_demo(cv, t):
    """Draw basic shapes demonstration"""
    
    # Background
    cv.rectangle(0, 0, 360, 280, (40, 40, 60, 255), filled=True)
    
    # Title
    cv.text(10, 10, "Basic Shapes Demo", (255, 255, 255, 255))
    
    # Rectangles
    cv.text(10, 35, "Rectangles:", (200, 200, 200, 255))
    cv.rectangle(20, 50, 60, 40, (255, 100, 100, 255), filled=True)
    cv.rectangle(90, 50, 60, 40, (100, 255, 100, 255), filled=False)
    
    # Circles
    cv.text(10, 105, "Circles:", (200, 200, 200, 255))
    cv.circle(50, 140, 20, (100, 100, 255, 255), filled=True)
    cv.circle(120, 140, 20, (255, 255, 100, 255), filled=False)
    
    # Lines
    cv.text(10, 175, "Lines:", (200, 200, 200, 255))
    cv.line(20, 195, 80, 235, (255, 0, 0, 255))
    cv.line(80, 195, 20, 235, (0, 255, 0, 255))
    cv.line(90, 215, 150, 215, (0, 0, 255, 255))
    
    # Animated circle
    x = 250 + int(40 * math.sin(t * 0.05))
    y = 100 + int(30 * math.cos(t * 0.07))
    cv.circle(x, y, 15, (255, 200, 0, 255), filled=True)
    cv.text(200, 20, "Animated", (255, 200, 0, 255))
    
    # Pixel grid
    cv.text(200, 150, "Pixel Grid:", (200, 200, 200, 255))
    for i in range(10):
        for j in range(10):
            color_val = int(((i + j + t // 5) % 10) * 25)
            cv.pixel(210 + i * 3, 170 + j * 3, (color_val, 100, 255 - color_val, 255))


def draw_plot_demo(cv, t):
    """Draw a mathematical plot"""
    
    # Background
    cv.rectangle(0, 0, 360, 280, (30, 30, 40, 255), filled=True)
    
    # Title
    cv.text(10, 10, "Mathematical Plot", (255, 255, 255, 255))
    
    # Grid
    grid_color = (60, 60, 80, 255)
    for i in range(0, 360, 30):
        cv.line(i, 40, i, 270, grid_color)
    for i in range(40, 280, 30):
        cv.line(10, i, 350, i, grid_color)
    
    # Axes
    cv.line(10, 155, 350, 155, (150, 150, 150, 255))  # X-axis
    cv.line(180, 40, 180, 270, (150, 150, 150, 255))  # Y-axis
    
    # Plot sine wave
    for x in range(340):
        y1 = 155 - int(50 * math.sin((x + t) * 0.05))
        y2 = 155 - int(50 * math.sin((x + 1 + t) * 0.05))
        cv.line(10 + x, y1, 11 + x, y2, (0, 255, 100, 255))
    
    # Plot cosine wave
    for x in range(340):
        y1 = 155 - int(50 * math.cos((x + t) * 0.05))
        y2 = 155 - int(50 * math.cos((x + 1 + t) * 0.05))
        cv.line(10 + x, y1, 11 + x, y2, (255, 100, 100, 255))
    
    # Legend
    cv.text(260, 250, "sin(x)", (0, 255, 100, 255))
    cv.text(310, 250, "cos(x)", (255, 100, 100, 255))


def draw_art_demo(cv, t):
    """Draw generative art"""
    
    # Background
    cv.rectangle(0, 0, 360, 280, (0, 0, 0, 255), filled=True)
    
    # Title
    cv.text(10, 10, "Generative Art", (255, 255, 255, 255))
    
    # Spiral pattern
    center_x = 180
    center_y = 140
    
    for i in range(50):
        angle = (i + t * 0.1) * 0.3
        radius = i * 3
        x1 = int(center_x + radius * math.cos(angle))
        y1 = int(center_y + radius * math.sin(angle))
        
        # Color gradient
        r = int(128 + 127 * math.sin(i * 0.1))
        g = int(128 + 127 * math.sin(i * 0.1 + 2))
        b = int(128 + 127 * math.sin(i * 0.1 + 4))
        
        # Draw circle
        cv.circle(x1, y1, 5, (r, g, b, 255), filled=True)
    
    # Connecting lines
    for i in range(0, 360, 30):
        angle1 = math.radians(i + t)
        angle2 = math.radians(i + 180 + t)
        
        x1 = int(center_x + 80 * math.cos(angle1))
        y1 = int(center_y + 80 * math.sin(angle1))
        x2 = int(center_x + 80 * math.cos(angle2))
        y2 = int(center_y + 80 * math.sin(angle2))
        
        cv.line(x1, y1, x2, y2, (100, 200, 255, 128))
    
    # Rotating rectangles
    for i in range(5):
        size = 40 + i * 10
        angle = t * 0.02 * (i + 1)
        
        # Simple rotation (just move corners)
        x = int(center_x + size * math.cos(angle))
        y = int(center_y + size * math.sin(angle))
        
        r = int(255 * (i / 5))
        g = int(255 * (1 - i / 5))
        
        cv.rectangle(x - size//4, y - size//4, size//2, size//2, 
                    (r, g, 150, 200), filled=False)
