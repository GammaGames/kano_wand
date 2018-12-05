# Kano Wand

Easily use the Kano Harry Potter Wand in Python

Demos available at the [**kano-wand-demos repo**](https://github.com/GammaGames/kano-wand-demos)

- [Kano Wand](#kano-wand)
    - [Usage](#usage)
    - [Classes](#classes)
        - [Shop](#shop)
        - [Wand](#wand)
        - [PATTERN](#pattern)
    - [FAQ](#faq)

## Usage

First, you'll want to create a `Shop`. It handles scanning for new wands and will return an array of wand objects. There are a few different ways to use the wands:

1. Use the wands returned by scanning
    * Create a shop and start to scan, returning an array of found wands
    * For each wand, call methods like `set_led` or `vibrate` on the wand object
    * Call the `on` method with an event type (`"position"`, `"button"`, etc) and a callback function to process events
    * Call the `off` method with a callback's id (returned from `on`) to remove a callback

2. Use a custom wand class
    * Create a class that inherits from `Wand`
    * Override the `post_connect` method in the new class to call methods and subscribe to events
    * Override methods (such as `on_position` or `on_button`) to use the data from the wand
    * Pass the class to the Shop using the `wand_class` argument on creation
    * Start scanning, and let the program run while it uses your custom wand class

3. Use a combination of the two
    * Create a custom class that inherits from wand
    * Add event callbacks with the `on` method
    * Override methods (such as `on_position` or `on_button`) to process events
    * Remove event callbacks with the `off` method, passing `continue_notifications=True` to prevent the notification thread from stopping

You can pass `debug=True` to the Shop or set `self.debug = True` in the wand to print debug messages, as well. When using the module, you should run it with sudo as it won't scan properly otherwise.

## Classes

### Shop

A scanner class to connect to wands

#### Instance variables

* `wand_class` {class} -- Class to use for new wand devices
* `debug` {bool} -- Print debug messages

#### Instance methods

* `Constructor` - Create a new scanner
    * Keyword Arguments:
        * `wand_class` {class} -- Class to use when connecting to wand (default: {Wand})
        * `debug` {bool} -- Print debug messages (default: {False})
* `scan` - Scan for devices. By default it will scan and connect to any Kano wands, but the behavior can be modified with the provided arguments
    * Keyword Arguments:
        * `name` {str} -- Name of the device to scan for (default: {None})
        * `prefix` {str} -- Prefix of name of device to scan for (default: {"Kano-Wand"})
        * `mac` {str} -- MAC Address of the device to scan for (default: {None})
        * `timeout` {float} -- Timeout before returning from scan (default: {1.0})
        * `connect` {bool} -- Connect to the wands automatically (default: {False})
    * Returns {Wand[]} -- Array of found wand objects

### Wand

A wand class to interact with the Kano wand. You shouldn't create this unless you know what you're doing, because you'll have to pass in a dictionary at construction so the wand knows where to connect to.

#### Instance variables

* `debug` {bool} -- Print debug messages
* `name` {str} -- Device name
* `connected {bool} -- Keeps track if wand is currently connected

#### Instance methods

* `Constructor` - Create a new wand
    * Arguments:
        * `device` {bluepy.ScanEntry} -- Device information obtained by the Shop
    * Keyword Arguments:
        * `debug` {bool} -- Print debug messages (default: {False})
* `connect` -- Connect to the wand
* `post_connect` -- Do anything necessary after connecting
* `disconnect` -- Disconnect from the wand and stop the notification thread
* `post_disconnect` -- Do anything necessary after disconnecting
* `get_organization` -- Get Get organization of device
    * Returns {str} -- Organization name
* `get_software_version` -- Get software version
    * Returns {str} -- Version number
* `get_hardware_version` -- Get hardware version
    * Returns {str} -- Hardware version
* `get_battery` -- Get battery level (currently only returns 0?)
    * Returns {str} -- Battery level
* `get_button` -- Get current button status
    * Returns {bool} -- Button pressed status
* `get_temperature` -- Get temperature
    * Returns {str} -- Battery level
* `vibrate` -- Vibrate wand with pattern
    * Keyword Arguments:
        * `pattern` {kano_wand.PATTERN} -- Vibration pattern (default: {PATTERN.REGULAR})
    * Returns {bytes} -- Status
* `Set` -- Set the LED's color
    * Keyword Arguments:
        * `color` {str} -- Color hex code (default: {"0x2185d0"})
        * `on` {bool} -- Whether light is on or off (default: {True})
    * Returns {bytes} -- Status
* `on` -- Add an event listener
    * Arguments:
        * `event` {str} -- Event type, "position", "button", "temp", or "battery"
        * `callback` {function} -- Callback function. The callback arguments match the format of the below `on_<event>` functions
    * Returns {str} -- ID of the callback for removal later
* `off` -- Remove a callback
    * Arguments:
        * `uuid` {str} -- Remove a callback with its id
    * Keyword Arguments:
        * `continue_notifications` {bool} -- Keep notification thread running (default: {False})
    * Returns {bool} -- If removal was successful or not
* `subscribe_position` -- Subscribe to position notifications and start thread if necessary
* `unsubscribe_position` -- Unsubscribe to position notifications
    * Keyword Arguments:
        * `continue_notifications` {bool} -- Keep notification thread running (default: {False})
subscribe_button(self):
        """Subscribe to button notifications and start thread if necessary
* `unsubscribe_button` -- Unsubscribe to button notifications
    * Keyword Arguments:
        * `continue_notifications` {bool} -- Keep notification thread running (default: {False})
* `subscribe_temperature` -- Subscribe to temperature notifications and start thread if necessary
* `unsubscribe_temperature` -- Unsubscribe to temperature notifications
    * Keyword Arguments:
        * `continue_notifications` {bool} -- Keep notification thread running (default: {False})
* `subscribe_battery` -- Subscribe to battery notifications and start thread if necessary
* `unsubscribe_battery` -- Unsubscribe to battery notifications
    * Keyword Arguments:
        * `continue_notifications` {bool} -- Keep notification thread running (default: {False})
* `reset_position` -- Reset the quaternains of the wand
* `on_position` -- Function called on position notification
    * Arguments:
        * `x` {int} -- X position of wand (Between -1000 and 1000)
        * `y` {int} -- Y position of wand (Between -1000 and 1000)
        * `pitch` {int} -- Pitch of wand (Between -1000 and 1000)
        * `roll` {int} -- Roll of wand (Between -1000 and 1000)
* `on_button` -- Function called on button notification
    * Arguments:
        * `pressed` {bool} -- If button is pressed
* `on_temperature` -- Function called on temperature notification
    * Arguments:
        * `value` {int} -- Temperature of the wand
* `on_battery` -- Function called on battery notification
    * Arguments:
        * `value` {int} -- Battery level of the wand

### PATTERN

An enum for vibration patterns. You can pass either an int or one of these values to `vibrate`:

* REGULAR
* SHORT
* BURST
* LONG
* SHORT_LONG
* SHORT_SHORT
* BIG_PAUSE

## FAQ

1. What operating systems will the module run on?
    * Currently it only runs on linux, as it is based on bluepy (which only supports linux). I would like to add support to Windows and Mac, but I would probably have to port it to another ble module.

2. I keep getting the error `bluepy.btle.BTLEException: Failed to execute mgmt cmd 'le on'`
    * The program must be run with sudo, as bluepy BLE doesn't work without elevation

3. How are notifications handled?
    * When subscribing to a notification the class will spawn a new thread that will listen to notifications, if necessary. The thread is automatically stopped when all notifications have been unsubscribed or the wand is disconnected.

4. When I connect to the wand and try to set the led immediately after turning it on the led doesn't actually change?
    * The wand does a boot animation with the led, I assume that the animation continues whether you set the led manually or not.

5. Kano's official app sometimes updates the wand's firmware, can I do that manually with this module?
    * Not at this point. I didn't want people bricking their wands and I didn't have any reason to write new firmware to the wand, so I left that feature out. For now the only way to update the wand's firmware is to use Kano's app.

6. Sometimes the program freezes and I have to Ctrl+C to end it. Why?
    * To help prevent nasty race conditions and bluetooth errors I use a lock when reading and writing to device characterstics. It did fix most errors with reading and writing, but occasionally the program isn't able to get the lock and will sit there frozen. I'm still new-ish to Python, but pull requests are welcome if you want to take a try at fixing it :)

7. There are a lot more instance variables and functions that aren't documented here, why aren't they?
    * Any variables or methods that start with an underscore are meant to be "private" and shouldn't be messed with directly. Methods like `handleNotification` and `handleDiscovery` are carried over from bluepy, and also should not be messed with.
