
class Framebuffer:
    """Mock framebuffer for testing."""
    
    def __init__(self):
        self.operations = []
    
    def fill_rect(self, x, y, w, h, color):
        self.operations.append(('fill_rect', x, y, w, h, color))
    
    def rect(self, x, y, w, h, color):
        self.operations.append(('rect', x, y, w, h, color))
    
    def text(self, text, x, y, color):
        self.operations.append(('text', text, x, y, color))
    
    def line(self, x1, y1, x2, y2, color):
        self.operations.append(('line', x1, y1, x2, y2, color))
    
    def pixel(self, x, y, color):
        self.operations.append(('pixel', x, y, color))