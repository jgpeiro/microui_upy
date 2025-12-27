"""
Demo 3: Panels, Popups & Advanced Features
Demonstrates panels, popups, text wrapping, headers, and complex layouts
"""
from microui import *

# UI state for Demo 3
ui_state = {
    'counter': 0,
    'show_info': True,
    'notification_count': 3,
    'popup_opened': False,
    'log_messages': [
        "System started",
        "Connected to server",
        "Ready for input",
    ],
}


def update_ui(ctx):
    """Demo 3: Panels, Popups & Advanced"""
    
    # Main window - full screen for 320x240
    if begin_window_ex(ctx, "Demo 3: Panels & Popups", Rect(10, 10, 300, 220), MU_OPT_NOCLOSE|MU_OPT_NORESIZE|MU_OPT_NOINTERACT):
        
        # Title label
        label(ctx, "=== PANELS & ADVANCED ===")
        
        # Section 1: Button to open popup
        layout_row(ctx, 2, [140, -1], 0)
        if button(ctx, "Open Popup"):
            open_popup(ctx, "Test Popup")
            ui_state['popup_opened'] = True
        
        label(ctx, f"Count: {ui_state['counter']}")
        
        # Section 2: Panel with info
        layout_row(ctx, 1, [-1], 60)
        begin_panel(ctx, "Info Panel")
        label(ctx, "System Information:")
        label(ctx, f"Frame: {ctx.frame}")
        label(ctx, f"Notifications: {ui_state['notification_count']}")
        label(ctx, f"Status: RUNNING")
        end_panel(ctx)
        
        # Section 3: Header with content
        layout_row(ctx, 1, [-1], 0)
        if header(ctx, "Statistics"):
            pass  # Header clicked
        
        layout_row(ctx, 2, [120, -1], 0)
        label(ctx, "Total Events:")
        label(ctx, str(ui_state['counter'] * 10))
        
        # Section 4: Log panel with scrolling
        layout_row(ctx, 1, [-1], 70)
        begin_panel(ctx, "Activity Log")
        
        for i, msg in enumerate(ui_state['log_messages'][-5:]):
            label(ctx, f"[{i+1}] {msg}")
        
        end_panel(ctx)
        
        # Action buttons
        layout_row(ctx, 3, [85, 85, -1], 0)
        if button(ctx, "Add Log"):
            ui_state['counter'] += 1
            ui_state['log_messages'].append(f"Event #{ui_state['counter']}")
            if len(ui_state['log_messages']) > 10:
                ui_state['log_messages'].pop(0)
        
        if button(ctx, "Notify"):
            ui_state['notification_count'] += 1
        
        if button(ctx, "Clear"):
            ui_state['log_messages'].clear()
            ui_state['log_messages'].append("Log cleared")
            ui_state['counter'] = 0
        
        end_window(ctx)
    
    # Popup window
    if begin_popup(ctx, "Test Popup"):
        label(ctx, "This is a popup!")
        label(ctx, "Click outside to close")
        
        layout_row(ctx, 1, [-1], 0)
        if button(ctx, "Action 1"):
            ui_state['counter'] += 1
        
        if button(ctx, "Action 2"):
            ui_state['counter'] += 5
        
        if button(ctx, "Close"):
            # Close popup by ending it
            end_popup(ctx)
            # Re-open to force close
            ctx.next_hover_root = None
            return
        
        end_popup(ctx)
