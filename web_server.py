#!/usr/bin/env python3
"""
Flask web server for microui rendering
Receives mouse events from web client and returns drawing commands
"""
import logging
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from microui import *
from microui.core import (
    MU_COMMAND_JUMP, MU_COMMAND_CLIP, MU_COMMAND_RECT, 
    MU_COMMAND_TEXT, MU_COMMAND_ICON
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
CORS(app)

# UI state
ui_state = {
    'checkbox1': False,
    'checkbox2': True,
    'slider_value': 50.0,
    'counter': 0,
}

# MicroUI context
ctx = None
WIDTH = 400
HEIGHT = 600


def text_width(font, text):
    """Calculate text width (8px per char)"""
    return len(text) * 8


def text_height(font):
    """Get text height"""
    return 10


def init_context():
    """Initialize MicroUI context"""
    global ctx
    # For web rendering, we don't need a real framebuffer
    ctx = Context(text_width, text_height, None)
    logger.info(f"Context initialized: {WIDTH}x{HEIGHT}")


def update_ui(ctx):
    """Main UI update function"""
    global ui_state
    
    # Main window
    if begin_window(ctx, "Demo Window", Rect(20, 20, 360, 560)):
        
        # Title
        text(ctx, "MicroUI Web Demo")
        
        # Button
        layout_row(ctx, 1, [-1], 0)
        if button(ctx, "Click Me"):
            ui_state['counter'] += 1
            logger.info(f"Button clicked! Count: {ui_state['counter']}")
        
        # Counter display
        label(ctx, f"Clicks: {ui_state['counter']}")
        
        # Checkboxes
        layout_row(ctx, 1, [-1], 0)
        res, ui_state['checkbox1'] = checkbox(ctx, "Option 1", ui_state['checkbox1'])
        if res & MU_RES_CHANGE:
            logger.info(f"Checkbox 1: {ui_state['checkbox1']}")
        
        res, ui_state['checkbox2'] = checkbox(ctx, "Option 2", ui_state['checkbox2'])
        if res & MU_RES_CHANGE:
            logger.info(f"Checkbox 2: {ui_state['checkbox2']}")
        
        # Slider
        layout_row(ctx, 1, [-1], 0)
        label(ctx, "Volume:")
        res, ui_state['slider_value'] = slider(ctx, ui_state['slider_value'], 0.0, 100.0)
        if res & MU_RES_CHANGE:
            logger.info(f"Slider: {ui_state['slider_value']:.1f}")
        
        # Tree node
        layout_row(ctx, 1, [-1], 0)
        if begin_treenode(ctx, "Advanced Options"):
            label(ctx, "Option A")
            label(ctx, "Option B")
            label(ctx, "Option C")
            end_treenode(ctx)
        
        # Panel
        layout_row(ctx, 1, [-1], 120)
        begin_panel(ctx, "Info Panel")
        label(ctx, "Status: Running")
        label(ctx, f"Frame: {ctx.frame}")
        label(ctx, f"Mouse: ({ctx.mouse_pos.x}, {ctx.mouse_pos.y})")
        end_panel(ctx)
        
        end_window(ctx)


def serialize_commands(ctx):
    """Convert command list to JSON-serializable format"""
    commands = []
    
    for cmd in ctx.command_list:
        cmd_data = {
            'type': cmd.type,
        }
        
        if cmd.type == MU_COMMAND_CLIP:
            cmd_data['rect'] = {
                'x': cmd.rect.x,
                'y': cmd.rect.y,
                'w': cmd.rect.w,
                'h': cmd.rect.h
            }
        elif cmd.type == MU_COMMAND_RECT:
            cmd_data['rect'] = {
                'x': cmd.rect.x,
                'y': cmd.rect.y,
                'w': cmd.rect.w,
                'h': cmd.rect.h
            }
            cmd_data['color'] = {
                'r': cmd.color.r,
                'g': cmd.color.g,
                'b': cmd.color.b,
                'a': cmd.color.a
            }
        elif cmd.type == MU_COMMAND_TEXT:
            cmd_data['pos'] = {
                'x': cmd.pos.x,
                'y': cmd.pos.y
            }
            cmd_data['text'] = cmd.text
            cmd_data['color'] = {
                'r': cmd.color.r,
                'g': cmd.color.g,
                'b': cmd.color.b,
                'a': cmd.color.a
            }
        elif cmd.type == MU_COMMAND_ICON:
            cmd_data['icon_id'] = cmd.id
            cmd_data['rect'] = {
                'x': cmd.rect.x,
                'y': cmd.rect.y,
                'w': cmd.rect.w,
                'h': cmd.rect.h
            }
            cmd_data['color'] = {
                'r': cmd.color.r,
                'g': cmd.color.g,
                'b': cmd.color.b,
                'a': cmd.color.a
            }
        
        commands.append(cmd_data)
    
    return commands


@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html', width=WIDTH, height=HEIGHT)


@app.route('/api/render', methods=['POST'])
def render():
    """Process mouse event and return drawing commands"""
    try:
        data = request.json
        event_type = data.get('type')
        x = data.get('x', 0)
        y = data.get('y', 0)
        button = data.get('button', 0)
        
        logger.debug(f"Event: {event_type} at ({x}, {y}) button={button}")
        
        # Update mouse state
        if event_type == 'mousemove':
            input_mousemove(ctx, x, y)
        elif event_type == 'mousedown':
            input_mousemove(ctx, x, y)
            if button == 0:  # Left button
                input_mousedown(ctx, x, y, MU_MOUSE_LEFT)
        elif event_type == 'mouseup':
            input_mousemove(ctx, x, y)
            if button == 0:  # Left button
                input_mouseup(ctx, x, y, MU_MOUSE_LEFT)
        
        # Process frame
        begin(ctx)
        update_ui(ctx)
        end(ctx)
        
        # Serialize commands
        commands = serialize_commands(ctx)
        
        return jsonify({
            'status': 'ok',
            'commands': commands,
            'frame': ctx.frame
        })
        
    except Exception as e:
        logger.error(f"Error processing render: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/init', methods=['GET'])
def init():
    """Initialize and return first frame"""
    try:
        # Process initial frame
        begin(ctx)
        update_ui(ctx)
        end(ctx)
        
        commands = serialize_commands(ctx)
        
        return jsonify({
            'status': 'ok',
            'commands': commands,
            'frame': ctx.frame,
            'width': WIDTH,
            'height': HEIGHT
        })
        
    except Exception as e:
        logger.error(f"Error in init: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


def main():
    """Main entry point"""
    logger.info("Starting MicroUI Web Server")
    init_context()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    main()
