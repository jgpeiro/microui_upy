# MicroUI Web Renderer

A Flask-based web renderer for MicroUI that allows real-time interaction with the UI through a web browser.

## Architecture

### Server (Flask)
- **File**: `web_server.py`
- **Port**: 5000 (default)
- **Purpose**: Runs the MicroUI context and processes mouse events

The server:
1. Initializes a MicroUI context
2. Receives mouse events (down/move/up) from the web client via REST API
3. Updates the MicroUI state based on events
4. Generates drawing commands
5. Serializes and returns commands as JSON

### Client (HTML/JavaScript)
- **File**: `templates/index.html`
- **Purpose**: Renders the UI in a web browser canvas

The client:
1. Displays a canvas for rendering
2. Captures mouse events (move, down, up)
3. Sends events to the server via POST requests
4. Receives drawing commands as JSON
5. Renders primitives (rectangles, text, icons) on the canvas

## API Endpoints

### GET `/`
Returns the main HTML page with the canvas renderer.

### GET `/api/init`
Initializes the UI and returns the first frame.

**Response:**
```json
{
  "status": "ok",
  "commands": [...],
  "frame": 0,
  "width": 400,
  "height": 600
}
```

### POST `/api/render`
Processes a mouse event and returns updated drawing commands.

**Request:**
```json
{
  "type": "mousemove|mousedown|mouseup",
  "x": 100,
  "y": 150,
  "button": 0
}
```

**Response:**
```json
{
  "status": "ok",
  "commands": [...],
  "frame": 42
}
```

## Drawing Commands

The server returns a list of drawing commands that the client renders:

### Command Types

1. **CLIP** (type=2): Set clipping rectangle
   ```json
   {
     "type": 2,
     "rect": {"x": 0, "y": 0, "w": 400, "h": 600}
   }
   ```

2. **RECT** (type=3): Draw filled rectangle
   ```json
   {
     "type": 3,
     "rect": {"x": 20, "y": 20, "w": 100, "h": 50},
     "color": {"r": 255, "g": 0, "b": 0, "a": 255}
   }
   ```

3. **TEXT** (type=4): Draw text
   ```json
   {
     "type": 4,
     "pos": {"x": 30, "y": 40},
     "text": "Hello World",
     "color": {"r": 255, "g": 255, "b": 255, "a": 255}
   }
   ```

4. **ICON** (type=5): Draw icon
   ```json
   {
     "type": 5,
     "icon_id": 2,
     "rect": {"x": 10, "y": 10, "w": 16, "h": 16},
     "color": {"r": 255, "g": 255, "b": 255, "a": 255}
   }
   ```

## Installation

1. Install Python dependencies:
   ```bash
   pip install -r web_requirements.txt
   ```

2. Make sure the microui package is in the same directory.

## Usage

1. Start the server:
   ```bash
   python web_server.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Interact with the UI using your mouse. The server will:
   - Process your mouse events
   - Update the UI state
   - Send drawing commands back to the browser
   - The browser will render the updated UI

## Logging

The server uses Python's logging module to log:
- INFO: Button clicks, checkbox changes, slider updates
- DEBUG: Mouse events, frame processing
- ERROR: Any exceptions or errors

View logs in the console where you started the server.

## Features

The demo UI includes:
- **Button**: Click counter
- **Checkboxes**: Toggle options
- **Slider**: Adjustable value (0-100)
- **Tree node**: Collapsible section
- **Panel**: Info display with frame counter and mouse position

## Customization

To create your own UI, modify the `update_ui()` function in `web_server.py`:

```python
def update_ui(ctx):
    """Main UI update function"""
    if begin_window(ctx, "My Window", Rect(10, 10, 300, 400)):
        # Add your UI elements here
        if button(ctx, "My Button"):
            print("Button clicked!")
        
        label(ctx, "Hello from MicroUI!")
        
        end_window(ctx)
```

## Browser Compatibility

Tested with:
- Chrome/Chromium
- Firefox
- Safari
- Edge

Requires HTML5 Canvas support.

## Performance

- The client sends a request for every mouse move event
- The server processes a full frame for each event
- For production use, consider debouncing mouse move events
- Drawing commands are kept minimal by MicroUI's clipping system

## Troubleshooting

**Canvas not updating:**
- Check browser console for JavaScript errors
- Verify server is running and accessible
- Check network tab for failed requests

**Server errors:**
- Check server console for Python exceptions
- Ensure all dependencies are installed
- Verify microui package is accessible

**High CPU usage:**
- Mouse move events trigger full frame processing
- Consider throttling mouse move events in JavaScript
- Reduce update frequency if needed
