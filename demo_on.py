from kano_wand import WandScanner, Wand, PATTERN

if __name__ == "__main__":
    scanner = WandScanner()
    wands = []
    try:
        while len(wands) == 0:
            wands = scanner.scan(connect=True)
            for wand in wands:
                colors = ["#a333c8", "2185d0", "0x21ba45", "#fbbd08", "#f2711c", "#db2828"]
                wand.vibrate(PATTERN.BURST)
                wand.set_led(colors.pop())

                def onButton(value):
                    global wand
                    global colors

                    if value:
                        wand.set_led(colors.pop())
                        if len(colors) == 0:
                            wand.disconnect()

                def onPos(roll, x, y, z):
                    roll = f"Roll: {roll}".ljust(16)
                    print(f"{roll}(x, y, z): ({x}, {y}, {z})")

                wand.on("button", onButton)
                # wand.on("position", onPos)

    # Detect keyboard interrupt disconnect
    except KeyboardInterrupt as e:
        for wand in wands:
            wand.disconnect()
