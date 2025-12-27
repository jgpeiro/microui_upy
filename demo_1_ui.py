"""
Demo 1: Basic Controls & Layout
Demonstrates buttons, labels, checkboxes, and basic layout features
"""
from microui import *

# UI state for Demo 1
ui_state = {
    'button_clicks': 0,
    'checkbox_enabled': True,
    'checkbox_option1': False,
    'checkbox_option2': True,
    'checkbox_option3': False,
}


def update_ui(ctx):
    """Demo 1: Basic Controls & Layout"""
    
    # Main window - full screen for 320x240
    if begin_window_ex(ctx, "Demo 1: Basic Controls", Rect(10, 10, 300, 220), MU_OPT_NOCLOSE|MU_OPT_NORESIZE|MU_OPT_NOINTERACT):
        
        # Title label
        label(ctx, "=== BASIC CONTROLS DEMO ===")
        
        # Section 1: Buttons
        layout_row(ctx, 1, [-1], 0)
        label(ctx, "--- Buttons ---")
        
        layout_row(ctx, 2, [140, -1], 0)
        if button(ctx, "Click Me!"):
            ui_state['button_clicks'] += 1
        
        label(ctx, f"Clicks: {ui_state['button_clicks']}")
        
        layout_row(ctx, 3, [90, 90, -1], 0)
        if button(ctx, "Reset"):
            ui_state['button_clicks'] = 0
        if button(ctx, "Add 10"):
            ui_state['button_clicks'] += 10
        if button(ctx, "Clear"):
            ui_state['button_clicks'] = 0
            for key in ui_state:
                if key.startswith('checkbox_'):
                    ui_state[key] = False
        
        # Section 2: Checkboxes
        layout_row(ctx, 1, [-1], 0)
        label(ctx, "--- Checkboxes ---")
        
        res, ui_state['checkbox_enabled'] = checkbox(ctx, "Enable Features", ui_state['checkbox_enabled'])
        
        if ui_state['checkbox_enabled']:
            res, ui_state['checkbox_option1'] = checkbox(ctx, "Option Alpha", ui_state['checkbox_option1'])
            res, ui_state['checkbox_option2'] = checkbox(ctx, "Option Beta", ui_state['checkbox_option2'])
            res, ui_state['checkbox_option3'] = checkbox(ctx, "Option Gamma", ui_state['checkbox_option3'])
        
        # Section 3: Multi-column layout
        layout_row(ctx, 1, [-1], 0)
        label(ctx, "--- Status Display ---")
        
        layout_row(ctx, 2, [100, -1], 0)
        label(ctx, "Frame:")
        label(ctx, str(ctx.frame))
        
        layout_row(ctx, 2, [100, -1], 0)
        label(ctx, "Mouse:")
        label(ctx, f"{ctx.mouse_pos.x},{ctx.mouse_pos.y}")
        
        end_window(ctx)
