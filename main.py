import framebuf
from microui import *

# Create framebuffer
buffer = bytearray(240 * 320 * 2)
fb = framebuf.FrameBuffer(buffer, 240, 320, framebuf.RGB565)

# Text callbacks
def text_width(font, text):
    return len(text) * 8

def text_height(font):
    return 10

# Create context
ctx = Context(text_width, text_height, fb)

# UI loop
def update_ui(ctx):
    print("update_ui")
    begin(ctx)
    
    if begin_window(ctx, "Window", Rect(10, 10, 200, 150)):
        if button(ctx, "Click"):
            print("Clicked!")
        end_window(ctx)
    
    end(ctx)
    render_commands(ctx)

# Run
while True:
    update_ui(ctx)