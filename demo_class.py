from kano_wand import WandScanner, Wand, PATTERN

if __name__ == "__main__":
    class MyWand(Wand):
        colors = ["#a333c8", "2185d0", "0x21ba45", "#fbbd08", "#f2711c", "#db2828"]

        # def on_position(self, roll, x, y, z):
        #     roll = f"Roll: {roll}".ljust(16)
        #     print(f"{roll}(x, y, z): ({x}, {y}, {z})")

        def on_button(self, value):
            if value:
                c = self.colors.pop()
                self.set_led(c)
                if len(self.colors) == 0:
                    self.disconnect()

    scanner = WandScanner(wand_class=MyWand)
    wands = []
    try:
        while len(wands) == 0:
            wands = scanner.scan(connect=True)
            for wand in wands:
                wand.vibrate(PATTERN.BURST)
                wand.set_led(wand.colors.pop())

    # Detect keyboard interrupt disconnect
    except KeyboardInterrupt as e:
        for wand in wands:
            wand.disconnect()
