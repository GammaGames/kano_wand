from kano_wand import Shoppe, Wand, PATTERN

if __name__ == "__main__":
    class MyWand(Wand):
    # Custom wand class extending the default wand
        colors = ["#a333c8", "2185d0", "0x21ba45", "#fbbd08", "#f2711c", "#db2828"]

        def post_connect(self):
            print(f"Connected to {self.name}")
            # Vibrate the wand and set its color to red
            self.set_led(self.colors.pop())
            # Subscribe to notifications
            self.subscribe_button()

        # Button callback, automatically called after connecting to wand
        def on_button(self, value):
            # If the button was pressed
            if value:
                # Update the led
                self.set_led(self.colors.pop())
                # Disconnect if we run out of colors
                if len(self.colors) == 0:
                    self.disconnect()

    # Create a new wand scanner
    scanner = Shoppe(wand_class=MyWand)
    wands = []
    try:
        # While we don't have any wands
        while len(wands) == 0:
            # Scan for wands and automatically connect
            print("Scanning...")
            wands = scanner.scan(connect=True)
            for wand in wands:
                # Vibrate the wand and set its color to red
                wand.vibrate(PATTERN.BURST)

                # Callback for position
                def onPos(roll, x, y, z):
                    roll = f"Roll: {roll}".ljust(16)
                    print(f"{roll}(x, y, z): ({x}, {y}, {z})")

                # Add the event callback to the wand
                wand.on("position", onPos)

    # Detect keyboard interrupt disconnect
    except KeyboardInterrupt as e:
        for wand in wands:
            wand.disconnect()
