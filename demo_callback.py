from kano_wand import Shoppe, PATTERN
import time
import sys

if __name__ == "__main__":
    # If we pass a -d flag, enable debugging
    debug = False
    if len(sys.argv) > 1:
        debug = sys.argv[1] == "-d"

    # Create a new wand scanner
    shoppe = Shoppe(debug=debug)
    wands = []
    try:
        # While we don't have any wands
        while len(wands) == 0:
            # Scan for wands and automatically connect
            print("Scanning...")
            wands = shoppe.scan(connect=True)
            # For each wand (Only tested with one)
            for wand in wands:
                print(f"Connected to {wand.name}")

                colors = ["#a333c8", "2185d0", "0x21ba45", "#fbbd08", "#f2711c", "#db2828"]
                # Vibrate the wand and set its color to red
                wand.vibrate(PATTERN.BURST)
                wand.set_led(colors.pop())

                # Callback for button presses
                def onButton(value):
                    global wand
                    global colors

                    # If the button was pressed
                    if value:
                        # Update the led
                        wand.set_led(colors.pop())
                        # Disconnect if we run out of colors
                        if len(colors) == 0:
                            wand.disconnect()

                # Callback for position
                def onPos(x, y, z, roll):
                    roll = f"Roll: {roll}".ljust(16)
                    print(f"{roll}(x, y, z): ({x}, {y}, {z})")

                # Add the event callbacks to the wand
                id = wand.on("button", onButton)
                wand.on("position", onPos)

    # Detect keyboard interrupt and disconnect wands
    except KeyboardInterrupt as e:
        for wand in wands:
            wand.disconnect()
