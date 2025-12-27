# tests/test_microui.py
"""
Unit tests for microui MicroPython port
"""
import unittest
import framebuf
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Mock font functions for testing
def mock_text_width(font, text):
    """Mock text width calculation"""
    return len(text) * 8

def mock_text_height(font):
    """Mock text height"""
    return 10


class TestCore(unittest.TestCase):
    """Test core data structures"""
    
    def test_vec2(self):
        from microui.core import Vec2
        v = Vec2(10, 20)
        self.assertEqual(v.x, 10)
        self.assertEqual(v.y, 20)
    
    def test_rect(self):
        from microui.core import Rect
        r = Rect(5, 10, 100, 50)
        self.assertEqual(r.x, 5)
        self.assertEqual(r.y, 10)
        self.assertEqual(r.w, 100)
        self.assertEqual(r.h, 50)
    
    def test_color(self):
        from microui.core import Color
        c = Color(255, 128, 64, 255)
        self.assertEqual(c.r, 255)
        self.assertEqual(c.g, 128)
        self.assertEqual(c.b, 64)
        self.assertEqual(c.a, 255)
        
        # Test RGB565 conversion
        rgb565 = c.to_rgb565()
        self.assertIsInstance(rgb565, int)
    
    def test_stack(self):
        from microui.core import Stack
        s = Stack(10)
        
        s.push(1)
        s.push(2)
        s.push(3)
        
        self.assertEqual(s.idx, 3)
        self.assertEqual(s.top(), 3)
        
        self.assertEqual(s.pop(), 3)
        self.assertEqual(s.pop(), 2)
        self.assertEqual(s.idx, 1)
    
    def test_stack_overflow(self):
        from microui.core import Stack
        s = Stack(2)
        s.push(1)
        s.push(2)
        
        with self.assertRaises(RuntimeError):
            s.push(3)
    
    def test_util_functions(self):
        from microui.core import clamp, expand_rect, intersect_rects, Rect
        
        # Test clamp
        self.assertEqual(clamp(5, 0, 10), 5)
        self.assertEqual(clamp(-5, 0, 10), 0)
        self.assertEqual(clamp(15, 0, 10), 10)
        
        # Test expand_rect
        r = expand_rect(Rect(10, 10, 20, 20), 5)
        self.assertEqual(r.x, 5)
        self.assertEqual(r.y, 5)
        self.assertEqual(r.w, 30)
        self.assertEqual(r.h, 30)
        
        # Test intersect_rects
        r1 = Rect(0, 0, 100, 100)
        r2 = Rect(50, 50, 100, 100)
        r3 = intersect_rects(r1, r2)
        self.assertEqual(r3.x, 50)
        self.assertEqual(r3.y, 50)
        self.assertEqual(r3.w, 50)
        self.assertEqual(r3.h, 50)


class TestContext(unittest.TestCase):
    """Test context functionality"""
    
    def setUp(self):
        """Setup test context"""
        from microui.core import Context
        
        buffer = bytearray(240 * 320 * 2)
        fb = framebuf.FrameBuffer(buffer, 240, 320, framebuf.RGB565)
        
        self.ctx = Context(mock_text_width, mock_text_height, fb)
    
    def test_context_init(self):
        """Test context initialization"""
        self.assertIsNotNone(self.ctx)
        self.assertEqual(self.ctx.frame, 0)
        self.assertEqual(self.ctx.hover, 0)
        self.assertEqual(self.ctx.focus, 0)
    
    def test_begin_end(self):
        """Test begin/end frame"""
        from microui.context import begin, end
        
        initial_frame = self.ctx.frame
        begin(self.ctx)
        self.assertEqual(self.ctx.frame, initial_frame + 1)
        
        end(self.ctx)
        self.assertEqual(self.ctx.mouse_pressed, 0)
    
    def test_id_generation(self):
        """Test ID generation"""
        from microui.context import get_id
        
        id1 = get_id(self.ctx, "test")
        id2 = get_id(self.ctx, "test")
        id3 = get_id(self.ctx, "other")
        
        self.assertEqual(id1, id2)
        self.assertNotEqual(id1, id3)
    
    def test_id_stack(self):
        """Test ID stack"""
        from microui.context import push_id, pop_id, get_id
        
        id1 = get_id(self.ctx, "base")
        
        push_id(self.ctx, "nested")
        id2 = get_id(self.ctx, "item")
        
        pop_id(self.ctx)
        id3 = get_id(self.ctx, "item")
        
        self.assertNotEqual(id2, id3)
    
    def test_clip_rect(self):
        """Test clip rectangle"""
        from microui.context import begin, push_clip_rect, pop_clip_rect, get_clip_rect
        from microui.core import Rect
        
        begin(self.ctx)
        
        r1 = Rect(0, 0, 100, 100)
        push_clip_rect(self.ctx, r1)
        
        r2 = get_clip_rect(self.ctx)
        self.assertEqual(r2.w, 100)
        self.assertEqual(r2.h, 100)
        
        pop_clip_rect(self.ctx)
    
    def test_input_mouse(self):
        """Test mouse input"""
        from microui.context import input_mousemove, input_mousedown, input_mouseup
        from microui.core import MU_MOUSE_LEFT
        
        input_mousemove(self.ctx, 100, 150)
        self.assertEqual(self.ctx.mouse_pos.x, 100)
        self.assertEqual(self.ctx.mouse_pos.y, 150)
        
        input_mousedown(self.ctx, 100, 150, MU_MOUSE_LEFT)
        self.assertEqual(self.ctx.mouse_down, MU_MOUSE_LEFT)
        self.assertEqual(self.ctx.mouse_pressed, MU_MOUSE_LEFT)
        
        input_mouseup(self.ctx, 100, 150, MU_MOUSE_LEFT)
        self.assertEqual(self.ctx.mouse_down, 0)


class TestLayout(unittest.TestCase):
    """Test layout system"""
    
    def setUp(self):
        """Setup test context"""
        from microui.core import Context, Rect
        from microui.context import begin
        
        buffer = bytearray(240 * 320 * 2)
        fb = framebuf.FrameBuffer(buffer, 240, 320, framebuf.RGB565)
        
        self.ctx = Context(mock_text_width, mock_text_height, fb)
        begin(self.ctx)
        
        # Push initial clip rect
        from microui.context import push_clip_rect
        push_clip_rect(self.ctx, Rect(0, 0, 240, 320))
    
    def test_layout_row(self):
        """Test layout row"""
        from microui.layout import layout_row, push_layout, get_layout
        from microui.core import Rect, Vec2
        
        body = Rect(0, 0, 200, 300)
        push_layout(self.ctx, body, Vec2(0, 0))
        
        layout_row(self.ctx, 3, [50, 100, 50], 30)
        
        layout = get_layout(self.ctx)
        self.assertEqual(layout.items, 3)
        self.assertEqual(layout.widths[0], 50)
        self.assertEqual(layout.widths[1], 100)
        self.assertEqual(layout.size.y, 30)
    
    def test_layout_next(self):
        """Test layout next"""
        from microui.layout import push_layout, layout_row, layout_next
        from microui.core import Rect, Vec2
        
        body = Rect(10, 10, 200, 300)
        push_layout(self.ctx, body, Vec2(0, 0))
        
        layout_row(self.ctx, 2, [100, 100], 40)
        
        r1 = layout_next(self.ctx)
        self.assertEqual(r1.w, 100)
        self.assertEqual(r1.h, 40)
        
        r2 = layout_next(self.ctx)
        self.assertGreater(r2.x, r1.x)


class TestControls(unittest.TestCase):
    """Test UI controls"""
    
    def setUp(self):
        """Setup test context"""
        from microui.core import Context, Rect
        from microui.context import begin
        
        buffer = bytearray(240 * 320 * 2)
        fb = framebuf.FrameBuffer(buffer, 240, 320, framebuf.RGB565)
        
        self.ctx = Context(mock_text_width, mock_text_height, fb)
        begin(self.ctx)
        
        # Setup initial layout
        from microui.context import push_clip_rect
        from microui.layout import push_layout
        from microui.core import Vec2
        
        push_clip_rect(self.ctx, Rect(0, 0, 240, 320))
        push_layout(self.ctx, Rect(0, 0, 240, 320), Vec2(0, 0))
    
    def test_button(self):
        """Test button control"""
        from microui.controls import button
        from microui.core import MU_RES_SUBMIT
        
        # Button not clicked
        res = button(self.ctx, "Test")
        self.assertEqual(res, 0)
        
        # Simulate button click
        from microui.context import input_mousedown
        from microui.core import MU_MOUSE_LEFT
        
        # Get button rect from last_rect
        rect = self.ctx.last_rect
        input_mousedown(self.ctx, rect.x + 5, rect.y + 5, MU_MOUSE_LEFT)
        
        # Re-create button and check if clicked
        from microui.layout import layout_row
        layout_row(self.ctx, 1, [-1], 0)
        res = button(self.ctx, "Test")
        self.assertTrue(res & MU_RES_SUBMIT)
    
    def test_checkbox(self):
        """Test checkbox control"""
        from microui.controls import checkbox
        from microui.core import MU_RES_CHANGE
        
        state = False
        res, new_state = checkbox(self.ctx, "Option", state)
        
        self.assertEqual(res, 0)
        self.assertEqual(new_state, False)
    
    def test_slider(self):
        """Test slider control"""
        from microui.controls import slider
        
        value = 50.0
        res, new_value = slider(self.ctx, value, 0.0, 100.0)
        
        self.assertEqual(res, 0)
        self.assertEqual(new_value, 50.0)
    
    def test_label(self):
        """Test label control"""
        from microui.controls import label
        
        # Should not raise exception
        label(self.ctx, "Test Label")
    
    def test_text(self):
        """Test text control"""
        from microui.controls import text
        
        # Should not raise exception
        text(self.ctx, "Multi-line text that should wrap properly")


class TestWindows(unittest.TestCase):
    """Test window management"""
    
    def setUp(self):
        """Setup test context"""
        from microui.core import Context
        from microui.context import begin
        
        buffer = bytearray(240 * 320 * 2)
        fb = framebuf.FrameBuffer(buffer, 240, 320, framebuf.RGB565)
        
        self.ctx = Context(mock_text_width, mock_text_height, fb)
        begin(self.ctx)
    
    def test_window_begin_end(self):
        """Test window creation"""
        from microui.windows import begin_window, end_window
        from microui.core import Rect
        
        opened = begin_window(self.ctx, "Test Window", Rect(10, 10, 200, 150))
        self.assertTrue(opened)
        
        end_window(self.ctx)
    
    def test_panel_begin_end(self):
        """Test panel creation"""
        from microui.windows import begin_window, end_window, begin_panel, end_panel
        from microui.core import Rect
        from microui.layout import layout_row
        
        begin_window(self.ctx, "Window", Rect(10, 10, 200, 150))
        
        layout_row(self.ctx, 1, [-1], -1)
        begin_panel(self.ctx, "Panel")
        end_panel(self.ctx)
        
        end_window(self.ctx)


class TestDrawing(unittest.TestCase):
    """Test drawing functions"""
    
    def setUp(self):
        """Setup test context"""
        from microui.core import Context
        
        buffer = bytearray(240 * 320 * 2)
        fb = framebuf.FrameBuffer(buffer, 240, 320, framebuf.RGB565)
        
        self.ctx = Context(mock_text_width, mock_text_height, fb)
    
    def test_draw_rect(self):
        """Test rectangle drawing"""
        from microui.drawing import draw_rect
        from microui.core import Rect, Color
        from microui.context import begin, push_clip_rect
        
        begin(self.ctx)
        push_clip_rect(self.ctx, Rect(0, 0, 240, 320))
        
        draw_rect(self.ctx, Rect(10, 10, 50, 30), Color(255, 0, 0))
        
        # Check command was added
        self.assertGreater(len(self.ctx.command_list), 0)
    
    def test_draw_text(self):
        """Test text drawing"""
        from microui.drawing import draw_text
        from microui.core import Vec2, Color
        from microui.context import begin, push_clip_rect
        from microui.core import Rect
        
        begin(self.ctx)
        push_clip_rect(self.ctx, Rect(0, 0, 240, 320))
        
        draw_text(self.ctx, None, "Hello", Vec2(10, 10), Color(255, 255, 255))
        
        # Check command was added
        self.assertGreater(len(self.ctx.command_list), 0)
    
    def test_render_commands(self):
        """Test command rendering"""
        from microui.drawing import draw_rect, render_commands
        from microui.core import Rect, Color
        from microui.context import begin, push_clip_rect
        
        begin(self.ctx)
        push_clip_rect(self.ctx, Rect(0, 0, 240, 320))
        
        draw_rect(self.ctx, Rect(10, 10, 50, 30), Color(255, 0, 0))
        
        # Should not raise exception
        render_commands(self.ctx)


class TestCanvas(unittest.TestCase):
    """Test canvas widget"""
    
    def setUp(self):
        from microui.core import Context
        import framebuf
        
        # Create a framebuffer for testing
        buffer = bytearray(240 * 320 * 2)
        fb = framebuf.FrameBuffer(buffer, 240, 320, framebuf.RGB565)
        
        self.ctx = Context(mock_text_width, mock_text_height, fb)
    
    def test_canvas_creation(self):
        """Test canvas widget creation"""
        from microui.controls import canvas
        from microui.context import begin, end
        from microui.windows import begin_window, end_window
        from microui.core import Rect
        
        begin(self.ctx)
        
        if begin_window(self.ctx, "Test", Rect(10, 10, 200, 200)):
            cv = canvas(self.ctx, 100, 100)
            self.assertIsNotNone(cv)
            self.assertEqual(cv.rect.w, 100)
            self.assertEqual(cv.rect.h, 100)
            end_window(self.ctx)
        
        end(self.ctx)
    
    def test_canvas_pixel(self):
        """Test canvas pixel drawing"""
        from microui.controls import canvas, CanvasContext
        from microui.context import begin, end
        from microui.windows import begin_window, end_window
        from microui.core import Rect, Color, MU_COMMAND_CANVAS_PIXEL
        
        begin(self.ctx)
        
        if begin_window(self.ctx, "Test", Rect(10, 10, 200, 200)):
            cv = canvas(self.ctx, 100, 100)
            cv.pixel(10, 20, (255, 0, 0, 255))
            end_window(self.ctx)
        
        end(self.ctx)
        
        # Check that pixel command was created
        found = False
        for cmd in self.ctx.command_list:
            if cmd.type == MU_COMMAND_CANVAS_PIXEL:
                self.assertEqual(cmd.x, 10)
                self.assertEqual(cmd.y, 20)
                self.assertEqual(cmd.color.r, 255)
                found = True
                break
        self.assertTrue(found, "Pixel command not found")
    
    def test_canvas_line(self):
        """Test canvas line drawing"""
        from microui.controls import canvas
        from microui.context import begin, end
        from microui.windows import begin_window, end_window
        from microui.core import Rect, MU_COMMAND_CANVAS_LINE
        
        begin(self.ctx)
        
        if begin_window(self.ctx, "Test", Rect(10, 10, 200, 200)):
            cv = canvas(self.ctx, 100, 100)
            cv.line(0, 0, 50, 50, (0, 255, 0, 255))
            end_window(self.ctx)
        
        end(self.ctx)
        
        # Check that line command was created
        found = False
        for cmd in self.ctx.command_list:
            if cmd.type == MU_COMMAND_CANVAS_LINE:
                self.assertEqual(cmd.x1, 0)
                self.assertEqual(cmd.y1, 0)
                self.assertEqual(cmd.x2, 50)
                self.assertEqual(cmd.y2, 50)
                found = True
                break
        self.assertTrue(found, "Line command not found")
    
    def test_canvas_rectangle(self):
        """Test canvas rectangle drawing"""
        from microui.controls import canvas
        from microui.context import begin, end
        from microui.windows import begin_window, end_window
        from microui.core import Rect, MU_COMMAND_CANVAS_RECT
        
        begin(self.ctx)
        
        if begin_window(self.ctx, "Test", Rect(10, 10, 200, 200)):
            cv = canvas(self.ctx, 100, 100)
            cv.rectangle(10, 10, 30, 20, (0, 0, 255, 255), filled=True)
            end_window(self.ctx)
        
        end(self.ctx)
        
        # Check that rectangle command was created
        found = False
        for cmd in self.ctx.command_list:
            if cmd.type == MU_COMMAND_CANVAS_RECT:
                self.assertEqual(cmd.x, 10)
                self.assertEqual(cmd.y, 10)
                self.assertEqual(cmd.w, 30)
                self.assertEqual(cmd.h, 20)
                self.assertTrue(cmd.filled)
                found = True
                break
        self.assertTrue(found, "Rectangle command not found")
    
    def test_canvas_circle(self):
        """Test canvas circle drawing"""
        from microui.controls import canvas
        from microui.context import begin, end
        from microui.windows import begin_window, end_window
        from microui.core import Rect, MU_COMMAND_CANVAS_CIRCLE
        
        begin(self.ctx)
        
        if begin_window(self.ctx, "Test", Rect(10, 10, 200, 200)):
            cv = canvas(self.ctx, 100, 100)
            cv.circle(50, 50, 25, (255, 255, 0, 255), filled=False)
            end_window(self.ctx)
        
        end(self.ctx)
        
        # Check that circle command was created
        found = False
        for cmd in self.ctx.command_list:
            if cmd.type == MU_COMMAND_CANVAS_CIRCLE:
                self.assertEqual(cmd.x, 50)
                self.assertEqual(cmd.y, 50)
                self.assertEqual(cmd.radius, 25)
                self.assertFalse(cmd.filled)
                found = True
                break
        self.assertTrue(found, "Circle command not found")
    
    def test_canvas_text(self):
        """Test canvas text drawing"""
        from microui.controls import canvas
        from microui.context import begin, end
        from microui.windows import begin_window, end_window
        from microui.core import Rect, MU_COMMAND_CANVAS_TEXT
        
        begin(self.ctx)
        
        if begin_window(self.ctx, "Test", Rect(10, 10, 200, 200)):
            cv = canvas(self.ctx, 100, 100)
            cv.text(5, 5, "Hello", (255, 255, 255, 255))
            end_window(self.ctx)
        
        end(self.ctx)
        
        # Check that text command was created
        found = False
        for cmd in self.ctx.command_list:
            if cmd.type == MU_COMMAND_CANVAS_TEXT:
                self.assertEqual(cmd.x, 5)
                self.assertEqual(cmd.y, 5)
                self.assertEqual(cmd.text, "Hello")
                found = True
                break
        self.assertTrue(found, "Canvas text command not found")


def add_test_case(suite, test_case_class):
    for attr in dir(test_case_class):
        if attr.startswith("test"):
            suite.addTest(test_case_class(attr))


def run_tests():
    suite = unittest.TestSuite()

    # Add all test classes
    add_test_case(suite, TestCore)
    add_test_case(suite, TestContext)
    add_test_case(suite, TestLayout)
    add_test_case(suite, TestControls)
    add_test_case(suite, TestWindows)
    add_test_case(suite, TestDrawing)
    add_test_case(suite, TestCanvas)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()

"""
def run_tests():
    suite = unittest.TestSuite()

    # Add test case instances (NOT methods)
    suite.addTest(TestCore())
    suite.addTest(TestContext())
    suite.addTest(TestLayout())
    suite.addTest(TestControls())
    suite.addTest(TestWindows())
    suite.addTest(TestDrawing())
    suite.addTest(TestCanvas())

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()
"""


if __name__ == '__main__':
    success = run_tests()
    print("\n" + "="*50)
    if success:
        print("All tests passed!")
    else:
        print("Some tests failed!")
