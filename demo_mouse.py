from kano_wand import Shoppe, Wand, PATTERN
import math
from pymouse import PyMouse

if __name__ == "__main__":
    class MouseWand(Wand):
        left_color = "#2185d0"
        right_color = "#f2711c"
        left = False

        def post_connect(self):
            print("Move the wand to move the mouse")
            print("Tilt the wand left and right and press the button to left and right click")
            # Create a mouse and get the screen dimensions
            self._m = PyMouse()
            self.x_dim, self.y_dim = self._m.screen_size()

        def on_position(self, roll, x, y, z):
            # Do some magic to get an adjusted x and y position
            x_pos = self.x_dim * (1.0 - (max(1, x * 4 + 1000) / 2000))
            y_pos = self.x_dim * (1.0 - (max(1, y * 3 + 1000) / 2000))
            # Move the mouse
            self._m.move(int(x_pos), int(y_pos))

            # Change left mouse button status and set LED when necessary
            if roll < 0 and self.left:
                self.left = False
                self.set_led(self.right_color)
            elif roll > 0 and not self.left:
                self.left = True
                self.set_led(self.left_color)

        def on_button(self, value):
            x_pos, y_pos = self._m.position()
            if value:
                self._m.press(x_pos, y_pos, 1 if self.left else 2)
            else:
                self._m.release(x_pos, y_pos, 1 if self.left else 2)

    # Create a new wand scanner
    shoppe = Shoppe(wand_class=MouseWand)
    wands = []
    try:
        # While we don't have any wands
        while len(wands) == 0:
            # Scan for wands and automatically connect
            wands = shoppe.scan(connect=True)

    # Detect keyboard interrupt and disconnect wands
    except KeyboardInterrupt as e:
        for wand in wands:
            wand.disconnect()
