"""
MRU-MRUA Physics Teaching Application (320x240)
Educational tool for learning uniform and uniformly accelerated motion
Features: Theory screens, interactive experiments, graphs, formulas
Screen Size: 320x240 for compact display
"""
from microui import *
import math

# UI state for Physics Teaching App
ui_state = {
    # Navigation
    'current_screen': 'menu',  # menu, mru_theory, mru_experiment, mrua_theory, mrua_experiment, comparison, exercises
    
    # MRU (Uniform Rectilinear Motion) - Simulation parameters
    'mru_position_0': 0.0,      # Initial position (m)
    'mru_velocity': 5.0,        # Velocity (m/s)
    'mru_time': 0.0,            # Current time (s)
    'mru_running': False,       # Animation running
    
    # MRUA (Uniformly Accelerated Rectilinear Motion) - Simulation parameters
    'mrua_position_0': 0.0,     # Initial position (m)
    'mrua_velocity_0': 0.0,     # Initial velocity (m/s)
    'mrua_acceleration': 2.0,   # Acceleration (m/s²)
    'mrua_time': 0.0,           # Current time (s)
    'mrua_running': False,      # Animation running
    
    # Path history for visualization
    'mru_path_history': [],     # [(time, position)]
    'mrua_path_history': [],    # [(time, position, velocity)]
    
    # Animation speed
    'time_scale': 0.05,         # Time increment per frame
    
    # Frame counter
    'frame': 0,
}


def update_ui(ctx):
    """Main UI update function"""
    
    ui_state['frame'] += 1
    
    # Main window - full screen 320x240
    if begin_window_ex(ctx, "Physics: MRU-MRUA", Rect(0, 0, 320, 240), 
                       MU_OPT_NOCLOSE|MU_OPT_NORESIZE):
        
        # Navigation bar
        render_navigation(ctx)
        
        # Render current screen
        if ui_state['current_screen'] == 'menu':
            render_menu(ctx)
        elif ui_state['current_screen'] == 'mru_theory':
            render_mru_theory(ctx)
        elif ui_state['current_screen'] == 'mru_experiment':
            render_mru_experiment(ctx)
        elif ui_state['current_screen'] == 'mrua_theory':
            render_mrua_theory(ctx)
        elif ui_state['current_screen'] == 'mrua_experiment':
            render_mrua_experiment(ctx)
        elif ui_state['current_screen'] == 'comparison':
            render_comparison(ctx)
        elif ui_state['current_screen'] == 'exercises':
            render_exercises(ctx)
        
        end_window(ctx)


def render_navigation(ctx):
    """Navigation bar with screen selection"""
    
    # Main navigation buttons
    layout_row(ctx, 5, [60, 60, 60, 60, -1], 0)
    
    if button(ctx, "Menu"):
        ui_state['current_screen'] = 'menu'
    
    if button(ctx, "MRU"):
        if ui_state['current_screen'] == 'mru_theory':
            ui_state['current_screen'] = 'mru_experiment'
        else:
            ui_state['current_screen'] = 'mru_theory'
    
    if button(ctx, "MRUA"):
        if ui_state['current_screen'] == 'mrua_theory':
            ui_state['current_screen'] = 'mrua_experiment'
        else:
            ui_state['current_screen'] = 'mrua_theory'
    
    if button(ctx, "Comp"):
        ui_state['current_screen'] = 'comparison'
    
    if button(ctx, "Test"):
        ui_state['current_screen'] = 'exercises'


def render_menu(ctx):
    """Main menu screen"""
    
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "PHYSICS: MOTION TUTORIAL")
    label(ctx, "")
    
    # MRU Section
    layout_row(ctx, 1, [-1], 55)
    begin_panel(ctx, "MRU - Uniform Motion")
    label(ctx, "Constant Velocity")
    label(ctx, "- Position-time: x=x0+v*t")
    label(ctx, "- Straight line graph")
    label(ctx, "- No acceleration")
    end_panel(ctx)
    
    layout_row(ctx, 2, [155, -1], 0)
    if button(ctx, "MRU Theory"):
        ui_state['current_screen'] = 'mru_theory'
    if button(ctx, "MRU Lab"):
        ui_state['current_screen'] = 'mru_experiment'
    
    # MRUA Section
    layout_row(ctx, 1, [-1], 55)
    begin_panel(ctx, "MRUA - Accelerated")
    label(ctx, "Constant Acceleration")
    label(ctx, "- x=x0+v0*t+0.5*a*t^2")
    label(ctx, "- Parabolic graph")
    label(ctx, "- Velocity changes")
    end_panel(ctx)
    
    layout_row(ctx, 2, [155, -1], 0)
    if button(ctx, "MRUA Theory"):
        ui_state['current_screen'] = 'mrua_theory'
    if button(ctx, "MRUA Lab"):
        ui_state['current_screen'] = 'mrua_experiment'
    
    # Other sections
    layout_row(ctx, 2, [155, -1], 0)
    if button(ctx, "Compare Both"):
        ui_state['current_screen'] = 'comparison'
    if button(ctx, "Exercises"):
        ui_state['current_screen'] = 'exercises'


def render_mru_theory(ctx):
    """MRU Theory screen with formulas"""
    
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "MRU: Uniform Motion")
    label(ctx, "")
    
    # Definition
    layout_row(ctx, 1, [-1], 40)
    begin_panel(ctx, "Definition")
    label(ctx, "Motion with CONSTANT velocity")
    label(ctx, "Acceleration = 0")
    label(ctx, "Speed never changes")
    end_panel(ctx)
    
    # Formula
    layout_row(ctx, 1, [-1], 30)
    begin_panel(ctx, "Main Formula")
    label(ctx, "x(t) = x0 + v * t")
    label(ctx, "x0=start, v=velocity")
    end_panel(ctx)
    
    # Graph
    layout_row(ctx, 1, [-1], 30)
    begin_panel(ctx, "Graph")
    label(ctx, "Position-Time: STRAIGHT LINE")
    label(ctx, "Slope = velocity")
    end_panel(ctx)
    
    # Example
    layout_row(ctx, 1, [-1], 50)
    begin_panel(ctx, "Example")
    label(ctx, "Car: x0=10m, v=5m/s")
    label(ctx, "At t=3s:")
    label(ctx, "x(3) = 10+5*3 = 25m")
    label(ctx, "Traveled: 15m")
    end_panel(ctx)
    
    # Navigation
    layout_row(ctx, 1, [-1], 0)
    if button(ctx, "Go to Experiment >>"):
        ui_state['current_screen'] = 'mru_experiment'


def render_mru_experiment(ctx):
    """MRU Interactive experiment screen"""
    
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "MRU Experiment")
    
    # Parameter controls
    label(ctx, f"x0: {ui_state['mru_position_0']:.1f}m")
    layout_row(ctx, 1, [-1], 0)
    res, ui_state['mru_position_0'] = slider(ctx, ui_state['mru_position_0'], -10.0, 10.0)
    
    label(ctx, f"v: {ui_state['mru_velocity']:.1f}m/s")
    layout_row(ctx, 1, [-1], 0)
    res, ui_state['mru_velocity'] = slider(ctx, ui_state['mru_velocity'], -10.0, 10.0)
    
    # Controls
    layout_row(ctx, 3, [100, 100, -1], 0)
    
    if button(ctx, "Start" if not ui_state['mru_running'] else "Pause"):
        ui_state['mru_running'] = not ui_state['mru_running']
    
    if button(ctx, "Reset"):
        ui_state['mru_time'] = 0.0
        ui_state['mru_running'] = False
        ui_state['mru_path_history'].clear()
    
    if button(ctx, "Theory"):
        ui_state['current_screen'] = 'mru_theory'
    
    # Update simulation
    if ui_state['mru_running']:
        ui_state['mru_time'] += ui_state['time_scale']
        position = ui_state['mru_position_0'] + ui_state['mru_velocity'] * ui_state['mru_time']
        ui_state['mru_path_history'].append((ui_state['mru_time'], position))
        if len(ui_state['mru_path_history']) > 100:
            ui_state['mru_path_history'].pop(0)
    
    # Calculate current values
    current_position = ui_state['mru_position_0'] + ui_state['mru_velocity'] * ui_state['mru_time']
    
    # Display values
    layout_row(ctx, 1, [-1], 0)
    label(ctx, f"t:{ui_state['mru_time']:.1f}s x:{current_position:.1f}m")
    
    # Animation
    layout_row(ctx, 1, [-1], 50)
    cv = canvas(ctx, 300, 45)
    draw_mru_animation(cv, current_position, ui_state['mru_velocity'])
    
    # Graph
    layout_row(ctx, 1, [-1], 80)
    cv = canvas(ctx, 300, 75)
    draw_mru_position_graph(cv)


def draw_mru_animation(cv, position, velocity):
    """Draw MRU motion animation"""
    
    # Background
    cv.rectangle(0, 0, 300, 45, (30, 30, 40, 255), filled=True)
    
    # Ground line
    cv.line(5, 35, 295, 35, (100, 100, 100, 255))
    
    # Scale markers
    for i in range(0, 291, 29):
        x = 5 + i
        cv.line(x, 33, x, 37, (150, 150, 150, 255))
    
    # Object position
    screen_x = 150 + int(position * 2.9)
    screen_x = max(15, min(285, screen_x))
    
    # Draw object
    cv.circle(screen_x, 25, 8, (100, 200, 255, 255), filled=True)
    
    # Velocity vector
    if abs(velocity) > 0.1:
        vector_length = int(velocity * 4)
        arrow_x = screen_x + vector_length
        arrow_x = max(20, min(280, arrow_x))
        
        cv.line(screen_x, 25, arrow_x, 25, (255, 100, 100, 255))
        if velocity > 0:
            cv.line(arrow_x, 25, arrow_x - 4, 21, (255, 100, 100, 255))
            cv.line(arrow_x, 25, arrow_x - 4, 29, (255, 100, 100, 255))
        else:
            cv.line(arrow_x, 25, arrow_x + 4, 21, (255, 100, 100, 255))
            cv.line(arrow_x, 25, arrow_x + 4, 29, (255, 100, 100, 255))
        
        cv.text(screen_x + 10, 10, f"v={velocity:.1f}", (255, 100, 100, 255))


def draw_mru_position_graph(cv):
    """Draw position-time graph for MRU"""
    
    # Background
    cv.rectangle(0, 0, 300, 75, (25, 25, 35, 255), filled=True)
    
    # Title
    cv.text(5, 3, "x vs t", (200, 200, 200, 255))
    
    # Axes
    cv.line(30, 15, 30, 65, (150, 150, 150, 255))
    cv.line(30, 65, 290, 65, (150, 150, 150, 255))
    
    # Grid
    for i in range(0, 261, 52):
        cv.line(30 + i, 65, 30 + i, 15, (60, 60, 80, 255))
    for i in range(0, 51, 10):
        cv.line(30, 65 - i, 290, 65 - i, (60, 60, 80, 255))
    
    # Plot theoretical line
    x0 = ui_state['mru_position_0']
    v = ui_state['mru_velocity']
    
    for t in range(0, 10):
        x1 = x0 + v * t
        x2 = x0 + v * (t + 1)
        
        screen_t1 = 30 + t * 26
        screen_t2 = 30 + (t + 1) * 26
        screen_x1 = 65 - int(x1 * 1.2)
        screen_x2 = 65 - int(x2 * 1.2)
        
        if 15 <= screen_x1 <= 65 and 15 <= screen_x2 <= 65:
            cv.line(screen_t1, screen_x1, screen_t2, screen_x2, (100, 100, 120, 255))
    
    # Plot actual path
    if len(ui_state['mru_path_history']) > 1:
        for i in range(len(ui_state['mru_path_history']) - 1):
            t1, pos1 = ui_state['mru_path_history'][i]
            t2, pos2 = ui_state['mru_path_history'][i + 1]
            
            screen_t1 = 30 + int(t1 * 26)
            screen_t2 = 30 + int(t2 * 26)
            screen_pos1 = 65 - int(pos1 * 1.2)
            screen_pos2 = 65 - int(pos2 * 1.2)
            
            if screen_t1 < 290 and 15 <= screen_pos1 <= 65 and 15 <= screen_pos2 <= 65:
                cv.line(screen_t1, screen_pos1, screen_t2, screen_pos2, (0, 255, 100, 255))
    
    # Current point
    if ui_state['mru_time'] > 0:
        current_pos = x0 + v * ui_state['mru_time']
        screen_t = 30 + int(ui_state['mru_time'] * 26)
        screen_pos = 65 - int(current_pos * 1.2)
        
        if screen_t < 290 and 15 <= screen_pos <= 65:
            cv.circle(screen_t, screen_pos, 2, (255, 255, 0, 255), filled=True)


def render_mrua_theory(ctx):
    """MRUA Theory screen"""
    
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "MRUA: Accelerated Motion")
    label(ctx, "")
    
    # Definition
    layout_row(ctx, 1, [-1], 40)
    begin_panel(ctx, "Definition")
    label(ctx, "CONSTANT acceleration")
    label(ctx, "Velocity CHANGES")
    label(ctx, "Parabolic motion")
    end_panel(ctx)
    
    # Formulas
    layout_row(ctx, 1, [-1], 50)
    begin_panel(ctx, "Formulas")
    label(ctx, "v(t) = v0 + a*t")
    label(ctx, "x(t) = x0+v0*t+0.5*a*t^2")
    label(ctx, "v^2 = v0^2 + 2*a*(x-x0)")
    end_panel(ctx)
    
    # Graph
    layout_row(ctx, 1, [-1], 30)
    begin_panel(ctx, "Graphs")
    label(ctx, "x-t: PARABOLA (curved)")
    label(ctx, "v-t: STRAIGHT LINE")
    end_panel(ctx)
    
    # Example
    layout_row(ctx, 1, [-1], 50)
    begin_panel(ctx, "Example")
    label(ctx, "v0=0, a=2m/s^2, t=3s")
    label(ctx, "v(3) = 0+2*3 = 6m/s")
    label(ctx, "x(3) = 0+0+0.5*2*9 = 9m")
    label(ctx, "Speed increased!")
    end_panel(ctx)
    
    # Navigation
    layout_row(ctx, 1, [-1], 0)
    if button(ctx, "Go to Experiment >>"):
        ui_state['current_screen'] = 'mrua_experiment'


def render_mrua_experiment(ctx):
    """MRUA Interactive experiment"""
    
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "MRUA Experiment")
    
    # Parameters
    label(ctx, f"x0: {ui_state['mrua_position_0']:.1f}m")
    layout_row(ctx, 1, [-1], 0)
    res, ui_state['mrua_position_0'] = slider(ctx, ui_state['mrua_position_0'], -10.0, 10.0)
    
    label(ctx, f"v0: {ui_state['mrua_velocity_0']:.1f}m/s")
    layout_row(ctx, 1, [-1], 0)
    res, ui_state['mrua_velocity_0'] = slider(ctx, ui_state['mrua_velocity_0'], -10.0, 10.0)
    
    label(ctx, f"a: {ui_state['mrua_acceleration']:.1f}m/s^2")
    layout_row(ctx, 1, [-1], 0)
    res, ui_state['mrua_acceleration'] = slider(ctx, ui_state['mrua_acceleration'], -5.0, 5.0)
    
    # Controls
    layout_row(ctx, 3, [100, 100, -1], 0)
    
    if button(ctx, "Start" if not ui_state['mrua_running'] else "Pause"):
        ui_state['mrua_running'] = not ui_state['mrua_running']
    
    if button(ctx, "Reset"):
        ui_state['mrua_time'] = 0.0
        ui_state['mrua_running'] = False
        ui_state['mrua_path_history'].clear()
    
    if button(ctx, "Theory"):
        ui_state['current_screen'] = 'mrua_theory'
    
    # Update
    if ui_state['mrua_running']:
        ui_state['mrua_time'] += ui_state['time_scale']
        x0 = ui_state['mrua_position_0']
        v0 = ui_state['mrua_velocity_0']
        a = ui_state['mrua_acceleration']
        t = ui_state['mrua_time']
        
        position = x0 + v0 * t + 0.5 * a * t * t
        velocity = v0 + a * t
        
        ui_state['mrua_path_history'].append((t, position, velocity))
        if len(ui_state['mrua_path_history']) > 100:
            ui_state['mrua_path_history'].pop(0)
    
    # Current values
    x0 = ui_state['mrua_position_0']
    v0 = ui_state['mrua_velocity_0']
    a = ui_state['mrua_acceleration']
    t = ui_state['mrua_time']
    
    current_position = x0 + v0 * t + 0.5 * a * t * t
    current_velocity = v0 + a * t
    
    layout_row(ctx, 1, [-1], 0)
    label(ctx, f"t:{t:.1f}s x:{current_position:.1f}m v:{current_velocity:.1f}m/s")
    
    # Animation
    layout_row(ctx, 1, [-1], 40)
    cv = canvas(ctx, 300, 35)
    draw_mrua_animation(cv, current_position, current_velocity, a)
    
    # Graph
    layout_row(ctx, 1, [-1], 50)
    cv = canvas(ctx, 300, 45)
    draw_mrua_position_graph(cv)


def draw_mrua_animation(cv, position, velocity, acceleration):
    """Draw MRUA animation"""
    
    cv.rectangle(0, 0, 300, 35, (30, 30, 40, 255), filled=True)
    
    # Ground
    cv.line(5, 28, 295, 28, (100, 100, 100, 255))
    
    # Object
    screen_x = 150 + int(position * 2.9)
    screen_x = max(15, min(285, screen_x))
    
    cv.circle(screen_x, 18, 7, (255, 150, 100, 255), filled=True)
    
    # Velocity vector
    if abs(velocity) > 0.1:
        vector_length = int(velocity * 3)
        arrow_x = screen_x + vector_length
        arrow_x = max(20, min(280, arrow_x))
        
        cv.line(screen_x, 18, arrow_x, 18, (100, 255, 100, 255))
        if velocity > 0:
            cv.line(arrow_x, 18, arrow_x - 3, 15, (100, 255, 100, 255))
            cv.line(arrow_x, 18, arrow_x - 3, 21, (100, 255, 100, 255))
        
        cv.text(screen_x + 8, 5, f"v={velocity:.1f}", (100, 255, 100, 255))


def draw_mrua_position_graph(cv):
    """Draw MRUA position graph (parabola)"""
    
    cv.rectangle(0, 0, 300, 45, (25, 25, 35, 255), filled=True)
    
    cv.text(5, 2, "x vs t", (200, 200, 200, 255))
    
    # Axes
    cv.line(30, 10, 30, 40, (150, 150, 150, 255))
    cv.line(30, 40, 290, 40, (150, 150, 150, 255))
    
    # Theoretical parabola
    x0 = ui_state['mrua_position_0']
    v0 = ui_state['mrua_velocity_0']
    a = ui_state['mrua_acceleration']
    
    points = []
    for i in range(260):
        t = i / 26.0
        x = x0 + v0 * t + 0.5 * a * t * t
        
        screen_t = 30 + i
        screen_x = 40 - int(x * 0.6)
        
        if 10 <= screen_x <= 40:
            points.append((screen_t, screen_x))
    
    for i in range(len(points) - 1):
        cv.line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], (100, 100, 120, 255))
    
    # Actual path
    if len(ui_state['mrua_path_history']) > 1:
        for i in range(len(ui_state['mrua_path_history']) - 1):
            t1, pos1, _ = ui_state['mrua_path_history'][i]
            t2, pos2, _ = ui_state['mrua_path_history'][i + 1]
            
            screen_t1 = 30 + int(t1 * 26)
            screen_t2 = 30 + int(t2 * 26)
            screen_pos1 = 40 - int(pos1 * 0.6)
            screen_pos2 = 40 - int(pos2 * 0.6)
            
            if screen_t1 < 290 and 10 <= screen_pos1 <= 40 and 10 <= screen_pos2 <= 40:
                cv.line(screen_t1, screen_pos1, screen_t2, screen_pos2, (255, 150, 100, 255))


def render_comparison(ctx):
    """Comparison screen"""
    
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "MRU vs MRUA")
    label(ctx, "")
    
    # Table
    layout_row(ctx, 3, [90, 90, -1], 0)
    label(ctx, "Property")
    label(ctx, "MRU")
    label(ctx, "MRUA")
    
    layout_row(ctx, 3, [90, 90, -1], 0)
    label(ctx, "Velocity:")
    label(ctx, "CONSTANT")
    label(ctx, "CHANGES")
    
    layout_row(ctx, 3, [90, 90, -1], 0)
    label(ctx, "Accel:")
    label(ctx, "ZERO")
    label(ctx, "CONSTANT")
    
    layout_row(ctx, 3, [90, 90, -1], 0)
    label(ctx, "x-t graph:")
    label(ctx, "LINE")
    label(ctx, "PARABOLA")
    
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    
    # Formulas
    layout_row(ctx, 2, [155, -1], 40)
    
    begin_panel(ctx, "MRU")
    label(ctx, "x = x0 + v*t")
    label(ctx, "v = constant")
    end_panel(ctx)
    
    begin_panel(ctx, "MRUA")
    label(ctx, "x = x0+v0*t+0.5*a*t^2")
    label(ctx, "v = v0 + a*t")
    end_panel(ctx)
    
    # Examples
    layout_row(ctx, 2, [155, -1], 40)
    
    begin_panel(ctx, "Examples")
    label(ctx, "- Cruise control")
    label(ctx, "- Conveyor belt")
    end_panel(ctx)
    
    begin_panel(ctx, "Examples")
    label(ctx, "- Free fall")
    label(ctx, "- Car speeding up")
    end_panel(ctx)
    
    # Visual
    layout_row(ctx, 1, [-1], 60)
    cv = canvas(ctx, 300, 55)
    draw_comparison_graphs(cv)


def draw_comparison_graphs(cv):
    """Draw comparison graphs"""
    
    cv.rectangle(0, 0, 300, 55, (20, 20, 30, 255), filled=True)
    
    # MRU
    cv.text(30, 3, "MRU:x-t", (150, 200, 150, 255))
    cv.line(15, 12, 15, 50, (100, 100, 100, 255))
    cv.line(15, 50, 130, 50, (100, 100, 100, 255))
    cv.line(15, 50, 130, 15, (150, 200, 150, 255))
    cv.text(50, 28, "Linear", (150, 200, 150, 255))
    
    # MRUA
    cv.text(180, 3, "MRUA:x-t", (255, 150, 100, 255))
    cv.line(165, 12, 165, 50, (100, 100, 100, 255))
    cv.line(165, 50, 280, 50, (100, 100, 100, 255))
    
    # Parabola
    for i in range(115):
        t1 = i / 11.5
        t2 = (i + 1) / 11.5
        y1 = 50 - int(t1 * t1 * 0.4)
        y2 = 50 - int(t2 * t2 * 0.4)
        if y1 >= 12 and y2 >= 12:
            cv.line(165 + i, y1, 166 + i, y2, (255, 150, 100, 255))
    
    cv.text(195, 28, "Parabola", (255, 150, 100, 255))


def render_exercises(ctx):
    """Practice exercises"""
    
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "Practice Problems")
    label(ctx, "")
    
    # MRU Problem
    layout_row(ctx, 1, [-1], 70)
    begin_panel(ctx, "MRU Problem")
    label(ctx, "Car at v=20m/s, x0=50m")
    label(ctx, "Where at t=5s?")
    label(ctx, "")
    label(ctx, "Solution:")
    label(ctx, "x = 50 + 20*5 = 150m")
    label(ctx, "Distance: 100m")
    end_panel(ctx)
    
    layout_row(ctx, 1, [-1], 0)
    if button(ctx, "Try in MRU Lab"):
        ui_state['current_screen'] = 'mru_experiment'
        ui_state['mru_position_0'] = 5.0
        ui_state['mru_velocity'] = 2.0
    
    # MRUA Problem
    layout_row(ctx, 1, [-1], 80)
    begin_panel(ctx, "MRUA Problem")
    label(ctx, "v0=0, a=3m/s^2, t=4s")
    label(ctx, "Find v and x:")
    label(ctx, "")
    label(ctx, "v = 0 + 3*4 = 12m/s")
    label(ctx, "x = 0+0+0.5*3*16=24m")
    label(ctx, "")
    label(ctx, "Check: avg_v*t=6*4=24✓")
    end_panel(ctx)
    
    layout_row(ctx, 1, [-1], 0)
    if button(ctx, "Try in MRUA Lab"):
        ui_state['current_screen'] = 'mrua_experiment'
        ui_state['mrua_position_0'] = 0.0
        ui_state['mrua_velocity_0'] = 0.0
        ui_state['mrua_acceleration'] = 3.0