"""
Demo 2: Sliders & Tree Nodes
Demonstrates slider controls, tree nodes, headers, and nested layouts
"""
from microui import *

# UI state for Demo 2
ui_state = {
    'volume': 75.0,
    'brightness': 50.0,
    'contrast': 60.0,
    'temperature': 22.0,
    'speed': 100.0,
}


def update_ui(ctx):
    """Demo 2: Sliders & Tree Nodes"""
    
    # Main window - full screen for 320x240
    if begin_window_ex(ctx, "Demo 2: Advanced Controls", Rect(10, 10, 300, 220), MU_OPT_NOCLOSE|MU_OPT_NORESIZE|MU_OPT_NOINTERACT):
        
        # Title label
        label(ctx, "=== SLIDERS & TREES ===")
        
        # Section 1: Sliders
        layout_row(ctx, 1, [-1], 0)
        label(ctx, "--- Slider Controls ---")
        
        label(ctx, f"Volume: {ui_state['volume']:.1f}%")
        layout_row(ctx, 1, [-1], 0)
        res, ui_state['volume'] = slider(ctx, ui_state['volume'], 0.0, 100.0)
        
        label(ctx, f"Brightness: {ui_state['brightness']:.1f}%")
        layout_row(ctx, 1, [-1], 0)
        res, ui_state['brightness'] = slider(ctx, ui_state['brightness'], 0.0, 100.0)
        
        # Tree node 1: Audio Settings
        layout_row(ctx, 1, [-1], 0)
        if begin_treenode(ctx, "Audio Settings"):
            label(ctx, "Sample Rate: 44.1kHz")
            label(ctx, "Channels: Stereo")
            label(ctx, "Bitrate: 320kbps")
            
            if begin_treenode(ctx, "Effects"):
                label(ctx, "Reverb: ON")
                label(ctx, "Echo: OFF")
                label(ctx, "Bass Boost: ON")
                end_treenode(ctx)
            
            end_treenode(ctx)
        
        # Tree node 2: Video Settings
        layout_row(ctx, 1, [-1], 0)
        if begin_treenode(ctx, "Video Settings"):
            label(ctx, f"Contrast: {ui_state['contrast']:.0f}%")
            layout_row(ctx, 1, [-1], 0)
            res, ui_state['contrast'] = slider(ctx, ui_state['contrast'], 0.0, 100.0)
            
            label(ctx, "Resolution: 320x240")
            label(ctx, "FPS: 60")
            end_treenode(ctx)
        
        # Section 2: Temperature Control
        layout_row(ctx, 1, [-1], 0)
        if begin_treenode(ctx, "Climate Control"):
            label(ctx, f"Temp: {ui_state['temperature']:.1f}C")
            layout_row(ctx, 1, [-1], 0)
            res, ui_state['temperature'] = slider(ctx, ui_state['temperature'], 15.0, 30.0)
            
            label(ctx, f"Speed: {ui_state['speed']:.0f}%")
            layout_row(ctx, 1, [-1], 0)
            res, ui_state['speed'] = slider(ctx, ui_state['speed'], 0.0, 100.0)
            end_treenode(ctx)
        
        end_window(ctx)
