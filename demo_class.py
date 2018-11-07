from kano_wand import Shoppe, Wand, PATTERN
import sys

if __name__ == "__main__":

    # Custom wand class extending the default wand
    class MyWand(Wand):
        colors = ["#a333c8", "2185d0", "0x21ba45", "#fbbd08", "#f2711c", "#db2828"]

        #
        def post_connect(self):
            print(f"Connected to {self.name}")
            # Vibrate the wand and set its color to red
            self.vibrate(PATTERN.BURST)
            self.set_led(self.colors.pop())
            # Subscribe to notifications
            self.subscribe_button()
            self.subscribe_position()

        # Position callback, automatically called after connecting to wand
        def on_position(self, x, y, z, roll):
            roll = f"Roll: {roll}".ljust(16)
            print(f"{roll}(x, y, z): ({x}, {y}, {z})")

        # Button callback, automatically called after connecting to wand
        def on_button(self, value):
            # If the button was pressed
            if value:
                # Update the led
                self.set_led(self.colors.pop())
                # Disconnect if we run out of colors
                if len(self.colors) == 0:
                    self.disconnect()

    # If we pass a -d flag, enable debugging
    debug = False
    if len(sys.argv) > 1:
        debug = sys.argv[1] == "-d"

    # Create a new wand scanner
    shoppe = Shoppe(wand_class=MyWand, debug=debug)
    wands = []
    try:
        # While we don't have any wands
        while len(wands) == 0:
            # Scan for wands and automatically connect
            print("Scanning...")
            wands = shoppe.scan(connect=True)

    # Detect keyboard interrupt and disconnect wands
    except KeyboardInterrupt as e:
        for wand in wands:
            wand.disconnect()
