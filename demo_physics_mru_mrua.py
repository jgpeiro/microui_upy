"""
MRU-MRUA Physics Teaching Application
Educational tool for learning uniform and uniformly accelerated motion
Features: Theory screens, interactive experiments, graphs, formulas
Screen Size: 400x600 for comfortable viewing
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
    'mru_show_velocity': True,  # Show velocity vector
    'mru_show_path': True,      # Show path trace
    
    # MRUA (Uniformly Accelerated Rectilinear Motion) - Simulation parameters
    'mrua_position_0': 0.0,     # Initial position (m)
    'mrua_velocity_0': 0.0,     # Initial velocity (m/s)
    'mrua_acceleration': 2.0,   # Acceleration (m/s²)
    'mrua_time': 0.0,           # Current time (s)
    'mrua_running': False,      # Animation running
    'mrua_show_velocity': True, # Show velocity vector
    'mrua_show_accel': True,    # Show acceleration vector
    'mrua_show_path': True,     # Show path trace
    
    # Path history for visualization
    'mru_path_history': [],     # [(time, position)]
    'mrua_path_history': [],    # [(time, position, velocity)]
    
    # Exercise state
    'exercise_mode': 'mru',     # 'mru' or 'mrua'
    'exercise_answers': {'x0': '', 'v': '', 'a': '', 't': '', 'x': ''},
    'exercise_result': '',
    
    # Animation speed
    'time_scale': 0.05,         # Time increment per frame
    
    # Frame counter
    'frame': 0,
}


def update_ui(ctx):
    """Main UI update function"""
    
    ui_state['frame'] += 1
    
    # Main window
    if begin_window_ex(ctx, "MRU-MRUA Physics Teacher", Rect(0, 0, 400, 600), 
                       MU_OPT_NOCLOSE|MU_OPT_NORESIZE|MU_OPT_NOTITLE):
        
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
    
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "=== PHYSICS: MRU & MRUA ===")
    
    # Main navigation buttons
    layout_row(ctx, 4, [95, 95, 95, -1], 0)
    
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
    
    if button(ctx, "Compare"):
        ui_state['current_screen'] = 'comparison'
    
    layout_row(ctx, 1, [-1], 2)
    # Separator line (using label)
    label(ctx, "=" * 50)


def render_menu(ctx):
    """Main menu screen"""
    
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "WELCOME TO PHYSICS MOTION TUTORIAL")
    label(ctx, "")
    label(ctx, "Learn about rectilinear motion:")
    label(ctx, "")
    
    # MRU Section
    layout_row(ctx, 1, [-1], 80)
    begin_panel(ctx, "MRU - Uniform Motion")
    label(ctx, "Constant Velocity Motion")
    label(ctx, "")
    label(ctx, "Topics covered:")
    label(ctx, "- Position-time relationship")
    label(ctx, "- Velocity vectors")
    label(ctx, "- Distance calculations")
    label(ctx, "- Interactive simulations")
    end_panel(ctx)
    
    layout_row(ctx, 2, [190, -1], 0)
    if button(ctx, "Start MRU Theory"):
        ui_state['current_screen'] = 'mru_theory'
    if button(ctx, "Start MRU Lab"):
        ui_state['current_screen'] = 'mru_experiment'
    
    # MRUA Section
    layout_row(ctx, 1, [-1], 80)
    begin_panel(ctx, "MRUA - Accelerated Motion")
    label(ctx, "Constant Acceleration Motion")
    label(ctx, "")
    label(ctx, "Topics covered:")
    label(ctx, "- Acceleration concepts")
    label(ctx, "- Velocity changes")
    label(ctx, "- Parabolic trajectories")
    label(ctx, "- Free fall examples")
    end_panel(ctx)
    
    layout_row(ctx, 2, [190, -1], 0)
    if button(ctx, "Start MRUA Theory"):
        ui_state['current_screen'] = 'mrua_theory'
    if button(ctx, "Start MRUA Lab"):
        ui_state['current_screen'] = 'mrua_experiment'
    
    # Other sections
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    
    layout_row(ctx, 2, [190, -1], 0)
    if button(ctx, "Compare MRU vs MRUA"):
        ui_state['current_screen'] = 'comparison'
    if button(ctx, "Practice Exercises"):
        ui_state['current_screen'] = 'exercises'
    
    # Info
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "TIP: Use sliders to change parameters")
    label(ctx, "Watch real-time graphs and animations")


def render_mru_theory(ctx):
    """MRU Theory screen with formulas"""
    
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "--- MRU THEORY ---")
    label(ctx, "Uniform Rectilinear Motion")
    label(ctx, "")
    
    # Definition
    layout_row(ctx, 1, [-1], 50)
    begin_panel(ctx, "Definition")
    label(ctx, "Motion in a straight line with")
    label(ctx, "CONSTANT VELOCITY")
    label(ctx, "")
    label(ctx, "Characteristics:")
    label(ctx, "- Velocity does NOT change")
    label(ctx, "- Acceleration = 0")
    end_panel(ctx)
    
    # Main formula
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "POSITION EQUATION:")
    label(ctx, "")
    
    layout_row(ctx, 1, [-1], 30)
    begin_panel(ctx, "Formula")
    label(ctx, "x(t) = x0 + v * t")
    label(ctx, "")
    label(ctx, "where: x0=initial pos, v=velocity")
    end_panel(ctx)
    
    # Variables explanation
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "VARIABLES:")
    
    layout_row(ctx, 1, [-1], 80)
    begin_panel(ctx, "Variables")
    label(ctx, "x(t)  = Position at time t (m)")
    label(ctx, "x0    = Initial position (m)")
    label(ctx, "v     = Velocity (m/s)")
    label(ctx, "t     = Time (s)")
    label(ctx, "")
    label(ctx, "Note: v is CONSTANT")
    label(ctx, "      (same at all times)")
    end_panel(ctx)
    
    # Graph description
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "GRAPHS:")
    
    layout_row(ctx, 1, [-1], 70)
    begin_panel(ctx, "Graph Characteristics")
    label(ctx, "Position-Time: STRAIGHT LINE")
    label(ctx, "  - Slope = velocity")
    label(ctx, "  - Linear relationship")
    label(ctx, "")
    label(ctx, "Velocity-Time: HORIZONTAL LINE")
    label(ctx, "  - Constant value")
    end_panel(ctx)
    
    # Example
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "EXAMPLE:")
    
    layout_row(ctx, 1, [-1], 70)
    begin_panel(ctx, "Problem")
    label(ctx, "A car starts at x0 = 10m")
    label(ctx, "moving at v = 5 m/s")
    label(ctx, "")
    label(ctx, "Where is it at t = 3s?")
    label(ctx, "x(3) = 10 + 5*3 = 25m")
    label(ctx, "")
    label(ctx, "Distance traveled: 15m")
    end_panel(ctx)
    
    # Navigation
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    if button(ctx, "Go to MRU Experiment >>"):
        ui_state['current_screen'] = 'mru_experiment'


def render_mru_experiment(ctx):
    """MRU Interactive experiment screen"""
    
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "--- MRU EXPERIMENT ---")
    label(ctx, "Interactive Simulation")
    
    # Parameter controls
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "PARAMETERS:")
    
    label(ctx, f"Initial Position: {ui_state['mru_position_0']:.1f} m")
    layout_row(ctx, 1, [-1], 0)
    res, ui_state['mru_position_0'] = slider(ctx, ui_state['mru_position_0'], -10.0, 10.0)
    
    label(ctx, f"Velocity: {ui_state['mru_velocity']:.1f} m/s")
    layout_row(ctx, 1, [-1], 0)
    res, ui_state['mru_velocity'] = slider(ctx, ui_state['mru_velocity'], -10.0, 10.0)
    
    # Simulation controls
    layout_row(ctx, 4, [90, 90, 90, -1], 0)
    
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
        # Store path history
        position = ui_state['mru_position_0'] + ui_state['mru_velocity'] * ui_state['mru_time']
        ui_state['mru_path_history'].append((ui_state['mru_time'], position))
        # Keep only last 100 points
        if len(ui_state['mru_path_history']) > 100:
            ui_state['mru_path_history'].pop(0)
    
    # Calculate current values
    current_position = ui_state['mru_position_0'] + ui_state['mru_velocity'] * ui_state['mru_time']
    
    # Display current values
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, f"Time: {ui_state['mru_time']:.2f} s")
    label(ctx, f"Position: {current_position:.2f} m")
    label(ctx, f"Velocity: {ui_state['mru_velocity']:.2f} m/s")
    label(ctx, f"Distance: {abs(ui_state['mru_velocity'] * ui_state['mru_time']):.2f} m")
    
    # Animation canvas
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "MOTION ANIMATION:")
    
    layout_row(ctx, 1, [-1], 80)
    cv = canvas(ctx, 380, 70)
    draw_mru_animation(cv, current_position, ui_state['mru_velocity'])
    
    # Position-Time graph
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "POSITION-TIME GRAPH:")
    
    layout_row(ctx, 1, [-1], 120)
    cv = canvas(ctx, 380, 110)
    draw_mru_position_graph(cv)


def draw_mru_animation(cv, position, velocity):
    """Draw MRU motion animation"""
    
    # Background
    cv.rectangle(0, 0, 380, 70, (30, 30, 40, 255), filled=True)
    
    # Ground line
    cv.line(10, 50, 370, 50, (100, 100, 100, 255))
    
    # Scale markers (every 10m)
    for i in range(0, 361, 36):
        x = 10 + i
        cv.line(x, 48, x, 52, (150, 150, 150, 255))
        meter_value = (i - 180) // 36 * 10
        cv.text(x - 10, 55, f"{meter_value}", (150, 150, 150, 255))
    
    # Object position (map position to screen, center at 190 = 0m)
    screen_x = 190 + int(position * 3.6)  # 3.6 pixels per meter
    screen_x = max(20, min(360, screen_x))  # Clamp to screen
    
    # Draw object (circle)
    cv.circle(screen_x, 35, 10, (100, 200, 255, 255), filled=True)
    cv.text(screen_x - 5, 15, "O", (255, 255, 255, 255))
    
    # Draw velocity vector
    if abs(velocity) > 0.1:
        vector_length = int(velocity * 5)
        arrow_x = screen_x + vector_length
        arrow_x = max(30, min(350, arrow_x))
        
        cv.line(screen_x, 35, arrow_x, 35, (255, 100, 100, 255))
        # Arrow head
        if velocity > 0:
            cv.line(arrow_x, 35, arrow_x - 5, 30, (255, 100, 100, 255))
            cv.line(arrow_x, 35, arrow_x - 5, 40, (255, 100, 100, 255))
        else:
            cv.line(arrow_x, 35, arrow_x + 5, 30, (255, 100, 100, 255))
            cv.line(arrow_x, 35, arrow_x + 5, 40, (255, 100, 100, 255))
        
        cv.text(screen_x + 15, 20, f"v={velocity:.1f}", (255, 100, 100, 255))


def draw_mru_position_graph(cv):
    """Draw position-time graph for MRU"""
    
    # Background
    cv.rectangle(0, 0, 380, 110, (25, 25, 35, 255), filled=True)
    
    # Title
    cv.text(5, 5, "x vs t (Position vs Time)", (200, 200, 200, 255))
    
    # Axes
    cv.line(40, 20, 40, 95, (150, 150, 150, 255))  # Y-axis
    cv.line(40, 95, 370, 95, (150, 150, 150, 255))  # X-axis
    
    # Labels
    cv.text(5, 50, "x(m)", (150, 150, 150, 255))
    cv.text(350, 100, "t(s)", (150, 150, 150, 255))
    
    # Grid
    for i in range(0, 331, 66):
        cv.line(40 + i, 95, 40 + i, 20, (60, 60, 80, 255))
    for i in range(0, 76, 15):
        cv.line(40, 95 - i, 370, 95 - i, (60, 60, 80, 255))
    
    # Plot theoretical line (full range)
    x0 = ui_state['mru_position_0']
    v = ui_state['mru_velocity']
    
    # Draw theoretical line in gray
    for t in range(0, 10):
        x1 = x0 + v * t
        x2 = x0 + v * (t + 1)
        
        # Map to screen coordinates
        screen_t1 = 40 + t * 33
        screen_t2 = 40 + (t + 1) * 33
        screen_x1 = 95 - int(x1 * 1.5)
        screen_x2 = 95 - int(x2 * 1.5)
        
        # Clamp to visible area
        if 20 <= screen_x1 <= 95 and 20 <= screen_x2 <= 95:
            cv.line(screen_t1, screen_x1, screen_t2, screen_x2, (100, 100, 120, 255))
    
    # Plot actual path from history
    if len(ui_state['mru_path_history']) > 1:
        for i in range(len(ui_state['mru_path_history']) - 1):
            t1, pos1 = ui_state['mru_path_history'][i]
            t2, pos2 = ui_state['mru_path_history'][i + 1]
            
            # Map to screen
            screen_t1 = 40 + int(t1 * 33)
            screen_t2 = 40 + int(t2 * 33)
            screen_pos1 = 95 - int(pos1 * 1.5)
            screen_pos2 = 95 - int(pos2 * 1.5)
            
            # Clamp
            if screen_t1 < 370 and 20 <= screen_pos1 <= 95 and 20 <= screen_pos2 <= 95:
                cv.line(screen_t1, screen_pos1, screen_t2, screen_pos2, (0, 255, 100, 255))
    
    # Current point
    if ui_state['mru_time'] > 0:
        current_pos = x0 + v * ui_state['mru_time']
        screen_t = 40 + int(ui_state['mru_time'] * 33)
        screen_pos = 95 - int(current_pos * 1.5)
        
        if screen_t < 370 and 20 <= screen_pos <= 95:
            cv.circle(screen_t, screen_pos, 3, (255, 255, 0, 255), filled=True)


def render_mrua_theory(ctx):
    """MRUA Theory screen with formulas"""
    
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "--- MRUA THEORY ---")
    label(ctx, "Uniformly Accelerated Motion")
    label(ctx, "")
    
    # Definition
    layout_row(ctx, 1, [-1], 50)
    begin_panel(ctx, "Definition")
    label(ctx, "Motion in a straight line with")
    label(ctx, "CONSTANT ACCELERATION")
    label(ctx, "")
    label(ctx, "Characteristics:")
    label(ctx, "- Velocity CHANGES linearly")
    label(ctx, "- Acceleration is constant")
    end_panel(ctx)
    
    # Main formulas
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "FUNDAMENTAL EQUATIONS:")
    label(ctx, "")
    
    layout_row(ctx, 1, [-1], 80)
    begin_panel(ctx, "Formulas")
    label(ctx, "1) v(t) = v0 + a * t")
    label(ctx, "")
    label(ctx, "2) x(t) = x0 + v0*t + (1/2)*a*t^2")
    label(ctx, "")
    label(ctx, "3) v^2 = v0^2 + 2*a*(x - x0)")
    label(ctx, "")
    label(ctx, "(without time)")
    end_panel(ctx)
    
    # Variables explanation
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "VARIABLES:")
    
    layout_row(ctx, 1, [-1], 90)
    begin_panel(ctx, "Variables")
    label(ctx, "x(t)  = Position at time t (m)")
    label(ctx, "v(t)  = Velocity at time t (m/s)")
    label(ctx, "x0    = Initial position (m)")
    label(ctx, "v0    = Initial velocity (m/s)")
    label(ctx, "a     = Acceleration (m/s^2)")
    label(ctx, "t     = Time (s)")
    label(ctx, "")
    label(ctx, "Note: a is CONSTANT")
    end_panel(ctx)
    
    # Graph description
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "GRAPHS:")
    
    layout_row(ctx, 1, [-1], 80)
    begin_panel(ctx, "Graph Characteristics")
    label(ctx, "Position-Time: PARABOLA")
    label(ctx, "  - Curved (quadratic)")
    label(ctx, "  - Concave up/down")
    label(ctx, "")
    label(ctx, "Velocity-Time: STRAIGHT LINE")
    label(ctx, "  - Slope = acceleration")
    label(ctx, "")
    label(ctx, "Acceleration-Time: HORIZONTAL")
    end_panel(ctx)
    
    # Example
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "EXAMPLE:")
    
    layout_row(ctx, 1, [-1], 90)
    begin_panel(ctx, "Problem")
    label(ctx, "Car starts from rest (v0=0)")
    label(ctx, "at x0 = 0m with a = 2 m/s^2")
    label(ctx, "")
    label(ctx, "At t = 3s:")
    label(ctx, "v(3) = 0 + 2*3 = 6 m/s")
    label(ctx, "x(3) = 0 + 0 + 0.5*2*9 = 9m")
    label(ctx, "")
    label(ctx, "Velocity increased from 0 to 6!")
    end_panel(ctx)
    
    # Navigation
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    if button(ctx, "Go to MRUA Experiment >>"):
        ui_state['current_screen'] = 'mrua_experiment'


def render_mrua_experiment(ctx):
    """MRUA Interactive experiment screen"""
    
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "--- MRUA EXPERIMENT ---")
    label(ctx, "Interactive Simulation")
    
    # Parameter controls
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "PARAMETERS:")
    
    label(ctx, f"Initial Position: {ui_state['mrua_position_0']:.1f} m")
    layout_row(ctx, 1, [-1], 0)
    res, ui_state['mrua_position_0'] = slider(ctx, ui_state['mrua_position_0'], -10.0, 10.0)
    
    label(ctx, f"Initial Velocity: {ui_state['mrua_velocity_0']:.1f} m/s")
    layout_row(ctx, 1, [-1], 0)
    res, ui_state['mrua_velocity_0'] = slider(ctx, ui_state['mrua_velocity_0'], -10.0, 10.0)
    
    label(ctx, f"Acceleration: {ui_state['mrua_acceleration']:.1f} m/s^2")
    layout_row(ctx, 1, [-1], 0)
    res, ui_state['mrua_acceleration'] = slider(ctx, ui_state['mrua_acceleration'], -5.0, 5.0)
    
    # Simulation controls
    layout_row(ctx, 4, [90, 90, 90, -1], 0)
    
    if button(ctx, "Start" if not ui_state['mrua_running'] else "Pause"):
        ui_state['mrua_running'] = not ui_state['mrua_running']
    
    if button(ctx, "Reset"):
        ui_state['mrua_time'] = 0.0
        ui_state['mrua_running'] = False
        ui_state['mrua_path_history'].clear()
    
    if button(ctx, "Theory"):
        ui_state['current_screen'] = 'mrua_theory'
    
    # Update simulation
    if ui_state['mrua_running']:
        ui_state['mrua_time'] += ui_state['time_scale']
        # Calculate values
        x0 = ui_state['mrua_position_0']
        v0 = ui_state['mrua_velocity_0']
        a = ui_state['mrua_acceleration']
        t = ui_state['mrua_time']
        
        position = x0 + v0 * t + 0.5 * a * t * t
        velocity = v0 + a * t
        
        # Store path history
        ui_state['mrua_path_history'].append((t, position, velocity))
        # Keep only last 100 points
        if len(ui_state['mrua_path_history']) > 100:
            ui_state['mrua_path_history'].pop(0)
    
    # Calculate current values
    x0 = ui_state['mrua_position_0']
    v0 = ui_state['mrua_velocity_0']
    a = ui_state['mrua_acceleration']
    t = ui_state['mrua_time']
    
    current_position = x0 + v0 * t + 0.5 * a * t * t
    current_velocity = v0 + a * t
    
    # Display current values
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, f"Time: {t:.2f} s")
    label(ctx, f"Position: {current_position:.2f} m")
    label(ctx, f"Velocity: {current_velocity:.2f} m/s")
    label(ctx, f"Acceleration: {a:.2f} m/s^2")
    
    # Animation canvas
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "MOTION ANIMATION:")
    
    layout_row(ctx, 1, [-1], 80)
    cv = canvas(ctx, 380, 70)
    draw_mrua_animation(cv, current_position, current_velocity, a)
    
    # Position-Time graph
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "POSITION-TIME GRAPH:")
    
    layout_row(ctx, 1, [-1], 100)
    cv = canvas(ctx, 380, 90)
    draw_mrua_position_graph(cv)
    
    # Velocity-Time graph
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "VELOCITY-TIME GRAPH:")
    
    layout_row(ctx, 1, [-1], 100)
    cv = canvas(ctx, 380, 90)
    draw_mrua_velocity_graph(cv)


def draw_mrua_animation(cv, position, velocity, acceleration):
    """Draw MRUA motion animation"""
    
    # Background
    cv.rectangle(0, 0, 380, 70, (30, 30, 40, 255), filled=True)
    
    # Ground line
    cv.line(10, 50, 370, 50, (100, 100, 100, 255))
    
    # Scale markers
    for i in range(0, 361, 36):
        x = 10 + i
        cv.line(x, 48, x, 52, (150, 150, 150, 255))
        meter_value = (i - 180) // 36 * 10
        cv.text(x - 10, 55, f"{meter_value}", (150, 150, 150, 255))
    
    # Object position
    screen_x = 190 + int(position * 3.6)
    screen_x = max(20, min(360, screen_x))
    
    # Draw object
    cv.circle(screen_x, 35, 10, (255, 150, 100, 255), filled=True)
    cv.text(screen_x - 5, 15, "O", (255, 255, 255, 255))
    
    # Draw velocity vector
    if abs(velocity) > 0.1:
        vector_length = int(velocity * 5)
        arrow_x = screen_x + vector_length
        arrow_x = max(30, min(350, arrow_x))
        
        cv.line(screen_x, 35, arrow_x, 35, (100, 255, 100, 255))
        # Arrow head
        if velocity > 0:
            cv.line(arrow_x, 35, arrow_x - 5, 30, (100, 255, 100, 255))
            cv.line(arrow_x, 35, arrow_x - 5, 40, (100, 255, 100, 255))
        else:
            cv.line(arrow_x, 35, arrow_x + 5, 30, (100, 255, 100, 255))
            cv.line(arrow_x, 35, arrow_x + 5, 40, (100, 255, 100, 255))
        
        cv.text(screen_x + 15, 20, f"v={velocity:.1f}", (100, 255, 100, 255))
    
    # Draw acceleration vector (above object)
    if abs(acceleration) > 0.1:
        accel_length = int(acceleration * 8)
        arrow_x = screen_x + accel_length
        arrow_x = max(30, min(350, arrow_x))
        
        cv.line(screen_x, 25, arrow_x, 25, (255, 255, 100, 255))
        # Arrow head
        if acceleration > 0:
            cv.line(arrow_x, 25, arrow_x - 4, 21, (255, 255, 100, 255))
            cv.line(arrow_x, 25, arrow_x - 4, 29, (255, 255, 100, 255))
        else:
            cv.line(arrow_x, 25, arrow_x + 4, 21, (255, 255, 100, 255))
            cv.line(arrow_x, 25, arrow_x + 4, 29, (255, 255, 100, 255))
        
        cv.text(screen_x + 15, 10, f"a={acceleration:.1f}", (255, 255, 100, 255))


def draw_mrua_position_graph(cv):
    """Draw position-time graph for MRUA (parabolic)"""
    
    # Background
    cv.rectangle(0, 0, 380, 90, (25, 25, 35, 255), filled=True)
    
    # Title
    cv.text(5, 5, "x vs t (Parabolic)", (200, 200, 200, 255))
    
    # Axes
    cv.line(40, 15, 40, 80, (150, 150, 150, 255))
    cv.line(40, 80, 370, 80, (150, 150, 150, 255))
    
    # Labels
    cv.text(5, 42, "x(m)", (150, 150, 150, 255))
    cv.text(350, 85, "t(s)", (150, 150, 150, 255))
    
    # Grid
    for i in range(0, 331, 66):
        cv.line(40 + i, 80, 40 + i, 15, (60, 60, 80, 255))
    for i in range(0, 66, 13):
        cv.line(40, 80 - i, 370, 80 - i, (60, 60, 80, 255))
    
    # Plot theoretical parabola
    x0 = ui_state['mrua_position_0']
    v0 = ui_state['mrua_velocity_0']
    a = ui_state['mrua_acceleration']
    
    points = []
    for i in range(331):
        t = i / 33.0  # 0 to 10 seconds
        x = x0 + v0 * t + 0.5 * a * t * t
        
        screen_t = 40 + i
        screen_x = 80 - int(x * 1.3)
        
        if 15 <= screen_x <= 80:
            points.append((screen_t, screen_x))
    
    # Draw theoretical curve
    for i in range(len(points) - 1):
        cv.line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], (100, 100, 120, 255))
    
    # Plot actual path
    if len(ui_state['mrua_path_history']) > 1:
        for i in range(len(ui_state['mrua_path_history']) - 1):
            t1, pos1, _ = ui_state['mrua_path_history'][i]
            t2, pos2, _ = ui_state['mrua_path_history'][i + 1]
            
            screen_t1 = 40 + int(t1 * 33)
            screen_t2 = 40 + int(t2 * 33)
            screen_pos1 = 80 - int(pos1 * 1.3)
            screen_pos2 = 80 - int(pos2 * 1.3)
            
            if screen_t1 < 370 and 15 <= screen_pos1 <= 80 and 15 <= screen_pos2 <= 80:
                cv.line(screen_t1, screen_pos1, screen_t2, screen_pos2, (255, 150, 100, 255))
    
    # Current point
    if ui_state['mrua_time'] > 0:
        t = ui_state['mrua_time']
        pos = x0 + v0 * t + 0.5 * a * t * t
        screen_t = 40 + int(t * 33)
        screen_pos = 80 - int(pos * 1.3)
        
        if screen_t < 370 and 15 <= screen_pos <= 80:
            cv.circle(screen_t, screen_pos, 3, (255, 255, 0, 255), filled=True)


def draw_mrua_velocity_graph(cv):
    """Draw velocity-time graph for MRUA (linear)"""
    
    # Background
    cv.rectangle(0, 0, 380, 90, (25, 25, 35, 255), filled=True)
    
    # Title
    cv.text(5, 5, "v vs t (Linear)", (200, 200, 200, 255))
    
    # Axes
    cv.line(40, 15, 40, 80, (150, 150, 150, 255))
    cv.line(40, 45, 370, 45, (150, 150, 150, 255))  # Zero line
    cv.line(40, 80, 370, 80, (150, 150, 150, 255))
    
    # Labels
    cv.text(5, 42, "v(m/s)", (150, 150, 150, 255))
    cv.text(350, 85, "t(s)", (150, 150, 150, 255))
    cv.text(25, 43, "0", (150, 150, 150, 255))
    
    # Grid
    for i in range(0, 331, 66):
        cv.line(40 + i, 80, 40 + i, 15, (60, 60, 80, 255))
    
    # Plot theoretical line
    v0 = ui_state['mrua_velocity_0']
    a = ui_state['mrua_acceleration']
    
    for i in range(330):
        t1 = i / 33.0
        t2 = (i + 1) / 33.0
        v1 = v0 + a * t1
        v2 = v0 + a * t2
        
        screen_t1 = 40 + i
        screen_t2 = 40 + i + 1
        screen_v1 = 45 - int(v1 * 3)
        screen_v2 = 45 - int(v2 * 3)
        
        if 15 <= screen_v1 <= 80 and 15 <= screen_v2 <= 80:
            cv.line(screen_t1, screen_v1, screen_t2, screen_v2, (100, 100, 120, 255))
    
    # Plot actual path
    if len(ui_state['mrua_path_history']) > 1:
        for i in range(len(ui_state['mrua_path_history']) - 1):
            t1, _, vel1 = ui_state['mrua_path_history'][i]
            t2, _, vel2 = ui_state['mrua_path_history'][i + 1]
            
            screen_t1 = 40 + int(t1 * 33)
            screen_t2 = 40 + int(t2 * 33)
            screen_v1 = 45 - int(vel1 * 3)
            screen_v2 = 45 - int(vel2 * 3)
            
            if screen_t1 < 370 and 15 <= screen_v1 <= 80 and 15 <= screen_v2 <= 80:
                cv.line(screen_t1, screen_v1, screen_t2, screen_v2, (100, 255, 100, 255))
    
    # Current point
    if ui_state['mrua_time'] > 0:
        t = ui_state['mrua_time']
        vel = v0 + a * t
        screen_t = 40 + int(t * 33)
        screen_v = 45 - int(vel * 3)
        
        if screen_t < 370 and 15 <= screen_v <= 80:
            cv.circle(screen_t, screen_v, 3, (255, 255, 0, 255), filled=True)


def render_comparison(ctx):
    """Comparison screen showing MRU vs MRUA side by side"""
    
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "--- MRU vs MRUA COMPARISON ---")
    label(ctx, "")
    
    # Table header
    layout_row(ctx, 3, [120, 120, -1], 0)
    label(ctx, "PROPERTY")
    label(ctx, "MRU")
    label(ctx, "MRUA")
    
    layout_row(ctx, 1, [-1], 2)
    label(ctx, "-" * 50)
    
    # Comparison rows
    layout_row(ctx, 3, [120, 120, -1], 0)
    label(ctx, "Velocity:")
    label(ctx, "CONSTANT")
    label(ctx, "CHANGES")
    
    layout_row(ctx, 3, [120, 120, -1], 0)
    label(ctx, "Acceleration:")
    label(ctx, "ZERO (a=0)")
    label(ctx, "CONSTANT")
    
    layout_row(ctx, 3, [120, 120, -1], 0)
    label(ctx, "x-t Graph:")
    label(ctx, "STRAIGHT LINE")
    label(ctx, "PARABOLA")
    
    layout_row(ctx, 3, [120, 120, -1], 0)
    label(ctx, "v-t Graph:")
    label(ctx, "HORIZONTAL")
    label(ctx, "STRAIGHT LINE")
    
    layout_row(ctx, 1, [-1], 2)
    label(ctx, "-" * 50)
    
    # Formulas comparison
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "FORMULAS:")
    
    layout_row(ctx, 2, [190, -1], 70)
    
    begin_panel(ctx, "MRU Formulas")
    label(ctx, "Position:")
    label(ctx, "x = x0 + v*t")
    label(ctx, "")
    label(ctx, "Velocity:")
    label(ctx, "v = constant")
    label(ctx, "")
    label(ctx, "Distance:")
    label(ctx, "d = v*t")
    end_panel(ctx)
    
    begin_panel(ctx, "MRUA Formulas")
    label(ctx, "Position:")
    label(ctx, "x = x0+v0*t+0.5*a*t^2")
    label(ctx, "Velocity:")
    label(ctx, "v = v0 + a*t")
    label(ctx, "v^2 = v0^2 + 2*a*d")
    end_panel(ctx)
    
    # Examples comparison
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "REAL WORLD EXAMPLES:")
    
    layout_row(ctx, 2, [190, -1], 90)
    
    begin_panel(ctx, "MRU Examples")
    label(ctx, "- Car on cruise control")
    label(ctx, "- Train at constant speed")
    label(ctx, "- Light in vacuum")
    label(ctx, "- Conveyor belt")
    label(ctx, "- Escalator")
    label(ctx, "")
    label(ctx, "Key: Speed stays same")
    end_panel(ctx)
    
    begin_panel(ctx, "MRUA Examples")
    label(ctx, "- Free falling object")
    label(ctx, "- Car accelerating")
    label(ctx, "- Rocket launch")
    label(ctx, "- Braking vehicle")
    label(ctx, "- Ball rolling downhill")
    label(ctx, "")
    label(ctx, "Key: Speed changes")
    end_panel(ctx)
    
    # Visual comparison
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "VISUAL COMPARISON:")
    
    layout_row(ctx, 1, [-1], 120)
    cv = canvas(ctx, 380, 110)
    draw_comparison_graphs(cv)
    
    # Key differences
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "KEY INSIGHT:")
    
    layout_row(ctx, 1, [-1], 50)
    begin_panel(ctx, "Remember")
    label(ctx, "MRU: Same velocity = Straight path")
    label(ctx, "MRUA: Changing velocity = Curved path")
    label(ctx, "")
    label(ctx, "Both describe motion in ONE dimension")
    label(ctx, "(along a straight line)")
    end_panel(ctx)


def draw_comparison_graphs(cv):
    """Draw side-by-side comparison of MRU and MRUA graphs"""
    
    # Background
    cv.rectangle(0, 0, 380, 110, (20, 20, 30, 255), filled=True)
    
    # Left side - MRU
    cv.text(50, 5, "MRU: x-t", (150, 200, 150, 255))
    
    # MRU axes
    cv.line(20, 20, 20, 100, (100, 100, 100, 255))
    cv.line(20, 100, 170, 100, (100, 100, 100, 255))
    
    # MRU straight line (constant velocity)
    cv.line(20, 100, 170, 30, (150, 200, 150, 255))
    cv.text(80, 55, "Linear", (150, 200, 150, 255))
    
    # Right side - MRUA
    cv.text(240, 5, "MRUA: x-t", (255, 150, 100, 255))
    
    # MRUA axes
    cv.line(210, 20, 210, 100, (100, 100, 100, 255))
    cv.line(210, 100, 360, 100, (100, 100, 100, 255))
    
    # MRUA parabola (acceleration)
    for i in range(150):
        t1 = i / 15.0
        t2 = (i + 1) / 15.0
        
        # Parabolic function
        y1 = 100 - int(t1 * t1 * 0.8)
        y2 = 100 - int(t2 * t2 * 0.8)
        
        x1 = 210 + i
        x2 = 210 + i + 1
        
        if y1 >= 20 and y2 >= 20:
            cv.line(x1, y1, x2, y2, (255, 150, 100, 255))
    
    cv.text(260, 55, "Parabolic", (255, 150, 100, 255))


def render_exercises(ctx):
    """Practice exercises screen"""
    
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "--- PRACTICE EXERCISES ---")
    label(ctx, "")
    
    # Mode selection
    layout_row(ctx, 2, [190, -1], 0)
    if button(ctx, "MRU Problems"):
        ui_state['exercise_mode'] = 'mru'
        ui_state['exercise_result'] = ''
    if button(ctx, "MRUA Problems"):
        ui_state['exercise_mode'] = 'mrua'
        ui_state['exercise_result'] = ''
    
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    
    if ui_state['exercise_mode'] == 'mru':
        render_mru_exercise(ctx)
    else:
        render_mrua_exercise(ctx)


def render_mru_exercise(ctx):
    """MRU practice problem"""
    
    label(ctx, "MRU PROBLEM:")
    label(ctx, "")
    
    layout_row(ctx, 1, [-1], 80)
    begin_panel(ctx, "Problem Statement")
    label(ctx, "A car is moving at constant velocity")
    label(ctx, "of 20 m/s. It passes a point (x0=50m)")
    label(ctx, "at t=0.")
    label(ctx, "")
    label(ctx, "Question:")
    label(ctx, "Where will the car be at t=5s?")
    label(ctx, "What distance did it travel?")
    end_panel(ctx)
    
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "GIVEN DATA:")
    label(ctx, "x0 = 50 m")
    label(ctx, "v = 20 m/s")
    label(ctx, "t = 5 s")
    label(ctx, "")
    label(ctx, "FORMULA: x = x0 + v*t")
    label(ctx, "")
    
    layout_row(ctx, 1, [-1], 60)
    begin_panel(ctx, "Solution Steps")
    label(ctx, "1. Identify: x0=50m, v=20m/s, t=5s")
    label(ctx, "2. Apply formula: x = 50 + 20*5")
    label(ctx, "3. Calculate: x = 50 + 100 = 150m")
    label(ctx, "4. Distance: d = v*t = 20*5 = 100m")
    label(ctx, "")
    label(ctx, "ANSWER: Position = 150m, Distance = 100m")
    end_panel(ctx)
    
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "TRY IT: Modify values in MRU Experiment")
    label(ctx, "and verify the results!")
    
    layout_row(ctx, 1, [-1], 0)
    if button(ctx, "Go to MRU Experiment"):
        ui_state['current_screen'] = 'mru_experiment'
        ui_state['mru_position_0'] = 50.0
        ui_state['mru_velocity'] = 20.0 / 10.0  # Scale down
        ui_state['mru_time'] = 0.0
        ui_state['mru_running'] = False


def render_mrua_exercise(ctx):
    """MRUA practice problem"""
    
    label(ctx, "MRUA PROBLEM:")
    label(ctx, "")
    
    layout_row(ctx, 1, [-1], 90)
    begin_panel(ctx, "Problem Statement")
    label(ctx, "A car starts from rest (v0=0)")
    label(ctx, "and accelerates at a=3 m/s^2.")
    label(ctx, "It starts at position x0=0.")
    label(ctx, "")
    label(ctx, "Questions:")
    label(ctx, "1. What is velocity at t=4s?")
    label(ctx, "2. What is position at t=4s?")
    label(ctx, "3. What distance traveled?")
    end_panel(ctx)
    
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "GIVEN DATA:")
    label(ctx, "x0 = 0 m")
    label(ctx, "v0 = 0 m/s")
    label(ctx, "a = 3 m/s^2")
    label(ctx, "t = 4 s")
    label(ctx, "")
    
    layout_row(ctx, 1, [-1], 100)
    begin_panel(ctx, "Solution Steps")
    label(ctx, "1. Find velocity:")
    label(ctx, "   v = v0 + a*t = 0 + 3*4 = 12 m/s")
    label(ctx, "")
    label(ctx, "2. Find position:")
    label(ctx, "   x = x0+v0*t+0.5*a*t^2")
    label(ctx, "   x = 0 + 0 + 0.5*3*16 = 24 m")
    label(ctx, "")
    label(ctx, "3. Distance = |x - x0| = 24 m")
    label(ctx, "")
    label(ctx, "ANSWERS: v=12m/s, x=24m, d=24m")
    end_panel(ctx)
    
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "")
    label(ctx, "VERIFICATION:")
    label(ctx, "Average velocity = (0+12)/2 = 6 m/s")
    label(ctx, "Distance = avg_v * t = 6*4 = 24m ✓")
    label(ctx, "")
    
    layout_row(ctx, 1, [-1], 0)
    if button(ctx, "Go to MRUA Experiment"):
        ui_state['current_screen'] = 'mrua_experiment'
        ui_state['mrua_position_0'] = 0.0
        ui_state['mrua_velocity_0'] = 0.0
        ui_state['mrua_acceleration'] = 3.0
        ui_state['mrua_time'] = 0.0
        ui_state['mrua_running'] = False
