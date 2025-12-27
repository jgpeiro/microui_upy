"""
Demo 4: Canvas Drawing (320x240)
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
    
    # Main window - full screen for 320x240
    if begin_window_ex(ctx, "Demo 4: Canvas Drawing", Rect(0, 0, 320, 240), 
                       MU_OPT_NOCLOSE|MU_OPT_NORESIZE):
        
        # Mode selection buttons
        layout_row(ctx, 3, [90, 90, -1], 0)
        if button(ctx, "Shapes"):
            ui_state['draw_mode'] = 'shapes'
        if button(ctx, "Plot"):
            ui_state['draw_mode'] = 'plot'
        if button(ctx, "Art"):
            ui_state['draw_mode'] = 'art'
        
        # Canvas widget - takes most of the space
        layout_row(ctx, 1, [-1], 180)
        cv = canvas(ctx, 300, 180)
        
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
        label(ctx, f"Frame: {ui_state['animation_time']} | Mode: {ui_state['draw_mode']}")
        
        end_window(ctx)


def draw_shapes_demo(cv, t):
    """Draw basic shapes demonstration"""
    
    # Background
    cv.rectangle(0, 0, 300, 180, (40, 40, 60, 255), filled=True)
    
    # Title
    cv.text(5, 5, "Basic Shapes Demo", (255, 255, 255, 255))
    
    # Rectangles
    cv.text(5, 25, "Rectangles:", (200, 200, 200, 255))
    cv.rectangle(10, 40, 50, 30, (255, 100, 100, 255), filled=True)
    cv.rectangle(70, 40, 50, 30, (100, 255, 100, 255), filled=False)
    
    # Circles
    cv.text(5, 80, "Circles:", (200, 200, 200, 255))
    cv.circle(35, 105, 15, (100, 100, 255, 255), filled=True)
    cv.circle(95, 105, 15, (255, 255, 100, 255), filled=False)
    
    # Lines
    cv.text(5, 130, "Lines:", (200, 200, 200, 255))
    cv.line(10, 145, 50, 170, (255, 0, 0, 255))
    cv.line(50, 145, 10, 170, (0, 255, 0, 255))
    cv.line(60, 157, 110, 157, (0, 0, 255, 255))
    
    # Animated circle
    x = 200 + int(35 * math.sin(t * 0.05))
    y = 60 + int(25 * math.cos(t * 0.07))
    cv.circle(x, y, 12, (255, 200, 0, 255), filled=True)
    cv.text(160, 15, "Animated", (255, 200, 0, 255))
    
    # Pixel grid
    cv.text(160, 95, "Pixel Grid:", (200, 200, 200, 255))
    for i in range(10):
        for j in range(10):
            color_val = int(((i + j + t // 5) % 10) * 25)
            cv.pixel(165 + i * 3, 115 + j * 3, (color_val, 100, 255 - color_val, 255))


def draw_plot_demo(cv, t):
    """Draw a mathematical plot"""
    
    # Background
    cv.rectangle(0, 0, 300, 180, (30, 30, 40, 255), filled=True)
    
    # Title
    cv.text(5, 5, "Mathematical Plot", (255, 255, 255, 255))
    
    # Grid
    grid_color = (60, 60, 80, 255)
    for i in range(0, 300, 30):
        cv.line(i, 25, i, 175, grid_color)
    for i in range(25, 180, 30):
        cv.line(5, i, 295, i, grid_color)
    
    # Axes
    cv.line(5, 100, 295, 100, (150, 150, 150, 255))  # X-axis
    cv.line(150, 25, 150, 175, (150, 150, 150, 255))  # Y-axis
    
    # Plot sine wave
    for x in range(285):
        y1 = 100 - int(40 * math.sin((x + t) * 0.05))
        y2 = 100 - int(40 * math.sin((x + 1 + t) * 0.05))
        cv.line(5 + x, y1, 6 + x, y2, (0, 255, 100, 255))
    
    # Plot cosine wave
    for x in range(285):
        y1 = 100 - int(40 * math.cos((x + t) * 0.05))
        y2 = 100 - int(40 * math.cos((x + 1 + t) * 0.05))
        cv.line(5 + x, y1, 6 + x, y2, (255, 100, 100, 255))
    
    # Legend
    cv.text(220, 165, "sin(x)", (0, 255, 100, 255))
    cv.text(260, 165, "cos(x)", (255, 100, 100, 255))


def draw_art_demo(cv, t):
    """Draw generative art"""
    
    # Background
    cv.rectangle(0, 0, 300, 180, (0, 0, 0, 255), filled=True)
    
    # Title
    cv.text(5, 5, "Generative Art", (255, 255, 255, 255))
    
    # Spiral pattern
    center_x = 150
    center_y = 90
    
    for i in range(40):
        angle = (i + t * 0.1) * 0.3
        radius = i * 2.5
        x1 = int(center_x + radius * math.cos(angle))
        y1 = int(center_y + radius * math.sin(angle))
        
        # Color gradient
        r = int(128 + 127 * math.sin(i * 0.1))
        g = int(128 + 127 * math.sin(i * 0.1 + 2))
        b = int(128 + 127 * math.sin(i * 0.1 + 4))
        
        # Draw circle
        cv.circle(x1, y1, 4, (r, g, b, 255), filled=True)
    
    # Connecting lines
    for i in range(0, 360, 30):
        angle1 = math.radians(i + t)
        angle2 = math.radians(i + 180 + t)
        
        x1 = int(center_x + 60 * math.cos(angle1))
        y1 = int(center_y + 60 * math.sin(angle1))
        x2 = int(center_x + 60 * math.cos(angle2))
        y2 = int(center_y + 60 * math.sin(angle2))
        
        cv.line(x1, y1, x2, y2, (100, 200, 255, 128))
    
    # Rotating rectangles
    for i in range(5):
        size = 30 + i * 8
        angle = t * 0.02 * (i + 1)
        
        # Simple rotation (just move corners)
        x = int(center_x + size * math.cos(angle))
        y = int(center_y + size * math.sin(angle))
        
        r = int(255 * (i / 5))
        g = int(255 * (1 - i / 5))
        
        cv.rectangle(x - size//4, y - size//4, size//2, size//2, 
                    (r, g, 150, 200), filled=False)