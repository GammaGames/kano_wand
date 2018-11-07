from enum import Enum
from bluepy.btle import *
import inspect
import numpy
import threading
import uuid
import os

if os.getenv("SUDO_USER") is None:
    print("This program must be run with sudo")
    exit()

from time import sleep

class INFO(Enum):
    """Enum containing info UUIDs"""
    SERVICE = '64A70010-F691-4B93-A6F4-0968F5B648F8'
    ORGANIZATION_CHAR = '64A7000B-F691-4B93-A6F4-0968F5B648F8'
    SOFTWARE_CHAR = '64A70013-F691-4B93-A6F4-0968F5B648F8'
    HARDWARE_CHAR = '64A70001-F691-4B93-A6F4-0968F5B648F8'

class IO(Enum):
    """Enum containing IO UUIDs"""
    SERVICE = '64A70012-F691-4B93-A6F4-0968F5B648F8'
    BATTERY_CHAR = '64A70007-F691-4B93-A6F4-0968F5B648F8'
    USER_BUTTON_CHAR = '64A7000D-F691-4B93-A6F4-0968F5B648F8'
    VIBRATOR_CHAR = '64A70008-F691-4B93-A6F4-0968F5B648F8'
    LED_CHAR = '64A70009-F691-4B93-A6F4-0968F5B648F8'
    KEEP_ALIVE_CHAR = '64A7000F-F691-4B93-A6F4-0968F5B648F8'

class SENSOR(Enum):
    """Enum containing sensor UUIDs"""
    SERVICE = '64A70011-F691-4B93-A6F4-0968F5B648F8'
    TEMP_CHAR = '64A70014-F691-4B93-A6F4-0968F5B648F8'
    QUATERNIONS_CHAR = '64A70002-F691-4B93-A6F4-0968F5B648F8'
    # RAW_CHAR = '64A7000A-F691-4B93-A6F4-0968F5B648F8'
    # MOTION_CHAR = '64A7000C-F691-4B93-A6F4-0968F5B648F8'
    MAGN_CALIBRATE_CHAR = '64A70021-F691-4B93-A6F4-0968F5B648F8'
    QUATERNIONS_RESET_CHAR = '64A70004-F691-4B93-A6F4-0968F5B648F8'

class PATTERN(Enum):
    """Enum for wand vibration patterns"""
    REGULAR = 1
    SHORT = 2
    BURST = 3
    LONG = 4
    SHORT_LONG = 5
    SHORT_SHORT = 6
    BIG_PAUSE = 7

class Wand(Peripheral, DefaultDelegate):
    """A wand class to interact with the Kano wand
    """
    _position_notification_handle = 41
    _button_notification_handle = 33
    _temp_notification_handle = 56
    _battery_notification_handle = 23
    _notification_thread = None

    def __init__(self, device, debug=False):
        """Create a new wand

        Arguments:
            device {bluepy.ScanEntry} -- Device information

        Keyword Arguments:
            debug {bool} -- Print debug messages (default: {False})
        """
        super().__init__(None)
        self.debug = debug
        self._dev = device
        self.name = device.getValueText(9)

        if debug:
            print(f"Wand: {self.name}\n\rWand Mac: {device.addr}")

        self._connected = False
        self._position_callbacks = {}
        self._position_subscribed = False
        self._button_callbacks = {}
        self._button_subscribed = False
        self._temperature_callbacks = {}
        self._temperature_subscribed = False
        self._battery_callbacks = {}
        self._battery_subscribed = False

    def connect(self):
        if self.debug:
            print(f"Connecting to {self.name}...")

        super(Wand, self).connect(self._dev)
        self._connected = True
        self.setDelegate(self)
        self._info_service = self.getServiceByUUID(INFO.SERVICE.value)
        self._io_service = self.getServiceByUUID(IO.SERVICE.value)
        self._sensor_service = self.getServiceByUUID(SENSOR.SERVICE.value)

        self.post_connect()

        if self.debug:
            print(f"Connected to {self.name}")

    def post_connect(self):
        """Do anything necessary after connecting
        """
        pass

    def disconnect(self):
        super().disconnect()
        self._connected = False

        self.post_disconnect()

        if self.debug:
            print(f"Disconnected from {self.name}")

    def post_disconnect(self):
        """Do anything necessary after disconnecting
        """
        pass

    # INFO
    def get_organization(self):
        """Get organization of device

        Returns:
            string -- Organization name
        """
        if not hasattr(self, "_organization_handle"):
            handle = self._info_service.getCharacteristics(INFO.ORGANIZATION_CHAR.value)[0]
            self._organization_handle = handle.getHandle()
        return self.readCharacteristic(self._organization_handle).decode("utf-8")

    def get_software_version(self):
        """Get software version

        Returns:
            string -- Version number
        """
        if not hasattr(self, "_software_handle"):
            handle = self._info_service.getCharacteristics(INFO.SOFTWARE_CHAR.value)[0]
            self._software_handle = handle.getHandle()
        return self.readCharacteristic(self._software_handle).decode("utf-8")

    def get_hardware_version(self):
        """Get hardware version

        Returns:
            string -- Hardware version
        """
        if not hasattr(self, "_hardware_handle"):
            handle = self._info_service.getCharacteristics(INFO.HARDWARE_CHAR.value)[0]
            self._hardware_handle = handle.getHandle()
        return self.readCharacteristic(self._hardware_handle).decode("utf-8")

    # IO
    def get_battery(self):
        """Get battery level (currently only returns 0)

        Returns:
            string -- Battery level
        """
        if not hasattr(self, "_battery_handle"):
            handle = self._io_service.getCharacteristics(IO.BATTERY_CHAR.value)[0]
            self._battery_handle = handle.getHandle()
        return self.readCharacteristic(self._battery_handle).decode("utf-8")

    def get_button(self):
        """Get current button status

        Returns:
            bool -- Button status
        """
        if not hasattr(self, "_button_handle"):
            handle = self._io_service.getCharacteristics(IO.USER_BUTTON_CHAR.value)[0]
            self._button_handle = handle.getHandle()

        data = self.readCharacteristic(self._button_handle)
        return data[0] == 1

    def get_temperature(self):
        """Get temperature

        Returns:
            string -- Battery level
        """
        if not hasattr(self, "_temperature_handle"):
            handle = self._sensor_service.getCharacteristics(SENSOR.TEMP_CHAR.value)[0]
            self._temperature_handle = handle.getHandle()
        return self.readCharacteristic(self._temperature_handle).decode("utf-8")

    def vibrate(self, pattern=PATTERN.REGULAR):
        """Vibrate wand with pattern

        Keyword Arguments:
            pattern {kano_wand.PATTERN} -- Vibration pattern (default: {PATTERN.REGULAR})

        Returns:
            bytes -- Status
        """
        if isinstance(pattern, PATTERN):
            message = [pattern.value]
        else:
            message = [pattern]

        if not hasattr(self, "_vibrator_handle"):
            handle = self._io_service.getCharacteristics(IO.VIBRATOR_CHAR.value)[0]
            self._vibrator_handle = handle.getHandle()
        return self.writeCharacteristic(self._vibrator_handle, bytes(message), withResponse=True)

    def set_led(self, color="0x2185d0", on=True):
        """Set the LED's color

        Keyword Arguments:
            color {string} -- Color hex code (default: {"0x2185d0"})
            on {bool} -- Whether light is on or off (default: {True})

        Returns:
            bytes -- Status
        """
        message = []
        if on:
            message.append(1)
        else:
            message.append(0)

        # I got this from Kano's node module
        color = int(color.replace("#", ""), 16)
        r = (color >> 16) & 255
        g = (color >> 8) & 255
        b = color & 255
        rgb = (((r & 248) << 8) + ((g & 252) << 3) + ((b & 248) >> 3))
        message.append(rgb >> 8)
        message.append(rgb & 0xff)

        if not hasattr(self, "_led_handle"):
            handle = self._io_service.getCharacteristics(IO.LED_CHAR.value)[0]
            self._led_handle = handle.getHandle()

        return self.writeCharacteristic(self._led_handle, bytes(message), withResponse=True)

    # SENSORS
    def on(self, event, callback):
        """Add an event listener

        Arguments:
            event {string} -- Event type, "position" or "button"
            callback {function} -- Callback function

        Returns:
            string -- ID of the callback for removal later
        """
        if self.debug:
            print(f"Adding callback for {event} notification...")

        id = None
        if event == "position":
            id = uuid.uuid4()
            self._position_callbacks[id] = callback
            self.subscribe_position()
        elif event == "button":
            id = uuid.uuid4()
            self._button_callbacks[id] = callback
            self.subscribe_button()
        elif event == "temp":
            id = uuid.uuid4()
            self._temperature_callbacks[id] = callback
            self.subscribe_temperature()
        elif event == "battery":
            id = uuid.uuid4()
            self._battery_callbacks[id] = callback
            self.subscribe_battery()

        return id

    def off(self, uuid):
        """Remove a callback

        Arguments:
            uuid {string} -- Remove a callback with its id

        Returns:
            bool -- If removal was successful or not
        """
        removed = False
        if self._position_callbacks.get(uuid) != None:
            self._position_callbacks.pop(uuid)
            removed = True
        elif self._button_callbacks.get(uuid) != None:
            self._button_callbacks.pop(uuid)
            removed = True

        if len(self._position_callbacks.values()) == 0:
            self.unsubscribe_position()
        if len(self._button_callbacks.values()) == 0:
            self.unsubscribe_button()
        if len(self._temperature_callbacks.values()) == 0:
            self.unsubscribe_temperature()
        if len(self._battery_callbacks.values()) == 0:
            self.unsubscribe_battery()

        return removed

    def subscribe_position(self):
        """Subscribe to position notifications and start thread if necessary
        """
        if not hasattr(self, "_position_handle"):
            handle = self._sensor_service.getCharacteristics(SENSOR.QUATERNIONS_CHAR.value)[0]
            self._position_handle = handle.getHandle()

        self.writeCharacteristic(self._position_handle + 1, bytes([1, 0]))

        if self._notification_thread == None:
            self._start_notification_thread()

    def unsubscribe_position(self):
        pass

    def subscribe_button(self):
        """Subscribe to button notifications and start thread if necessary
        """
        if not hasattr(self, "_button_handle"):
            handle = self._io_service.getCharacteristics(IO.USER_BUTTON_CHAR.value)[0]
            self._button_handle = handle.getHandle()

        self.writeCharacteristic(self._button_handle + 1, bytes([1, 0]))

        if self._notification_thread == None:
            self._start_notification_thread()

    def unsubscribe_button(self):
        pass

    def subscribe_temperature(self):
        """Subscribe to temperature notifications and start thread if necessary
        """
        if not hasattr(self, "_temp_handle"):
            handle = self._sensor_service.getCharacteristics(SENSOR.TEMP_CHAR.value)[0]
            self._temp_handle = handle.getHandle()

        self.writeCharacteristic(self._temp_handle + 1, bytes([1, 0]))

        if self._notification_thread == None:
            self._start_notification_thread()

    def unsubscribe_temperature(self):
        pass

    def subscribe_battery(self):
        """Subscribe to battery notifications and start thread if necessary
        """
        if not hasattr(self, "_battery_handle"):
            handle = self._io_service.getCharacteristics(IO.BATTERY_CHAR .value)[0]
            self._battery_handle = handle.getHandle()

        self.writeCharacteristic(self._battery_handle + 1, bytes([1, 0]))

        if self._notification_thread == None:
            self._start_notification_thread()

    def unsubscribe_battery(self):
        pass

    def _start_notification_thread(self):
        try:
            self.reset_position()
            self._notification_thread = threading.Thread(target=self._run)
            self._notification_thread.start()
        except:
            pass

    def _run(self):
        while self._connected:
            try:
                if super().waitForNotifications(1):
                    continue
            except:
                continue

    def _on_position(self, data):
        """Private function for position notification

        Arguments:
            data {bytes} -- Data from device
        """
        # I got part of this from Kano's node module and modified it
        y = numpy.int16(numpy.uint16(int.from_bytes(data[0:2], byteorder='little')))
        x = numpy.int16(numpy.uint16(int.from_bytes(data[2:4], byteorder='little')))
        w = numpy.int16(numpy.uint16(int.from_bytes(data[4:6], byteorder='little')))
        z = numpy.int16(numpy.uint16(int.from_bytes(data[6:8], byteorder = 'little')))

        if self.debug:
            roll = f"Roll: {w}".ljust(16)
            print(f"{roll}(x, y, z): ({x}, {y}, {z})")

        self.on_position(w, x, y, z)
        for callback in self._position_callbacks.values():
            callback(w, x, y, z)

    def on_position(self, roll, x, y, z):
        """Function called on position notification

        Arguments:
            roll {int} -- Roll of wand
            x {int} -- X position of wand
            y {int} -- Y position of wand
            z {int} -- Z position of wand
        """
        pass

    def reset_position(self):
        """Reset the quaternains of the wand
        """
        handle = self._sensor_service.getCharacteristics(SENSOR.QUATERNIONS_RESET_CHAR.value)[0].getHandle()
        self.writeCharacteristic(handle, bytes([1]))

    def _on_button(self, data):
        """Private function for button notification

        Arguments:
            data {bytes} -- Data from device
        """
        val = data[0] == 1

        if self.debug:
            print(f"Button: {val}")

        self.on_button(val)
        for callback in self._button_callbacks.values():
            callback(val)

    def on_button(self, value):
        """Function called on button notification

        Arguments:
            value {bool} -- If button is pressed
        """
        pass

    def _on_temperature(self, data):
        """Private function for temperature notification

        Arguments:
            data {bytes} -- Data from device
        """
        val = numpy.int16(numpy.uint16(int.from_bytes(data[0:2], byteorder='little')))

        if self.debug:
            print(f"Temperature: {val}")

        self.on_temperature(val)
        for callback in self._temperature_callbacks.values():
            callback(val)

    def on_temperature(self, value):
        """Function called on temperature notification

        Arguments:
            value {int} -- Temperature of the wand
        """
        pass

    def _on_battery(self, data):
        """Private function for temperature notification

        Arguments:
            data {bytes} -- Data from device
        """
        val = data[0]

        if self.debug:
            print(f"Battery: {val}")

        self.on_battery(val)
        for callback in self._battery_callbacks.values():
            callback(val)

    def on_battery(self, value):
        """Function called on temperature notification

        Arguments:
            value {int} -- Temperature of the wand
        """

    def handleNotification(self, cHandle, data):
        """Handle notifications subscribed to

        Arguments:
            cHandle {int} -- Handle of notification
            data {bytes} -- Data from device
        """
        if cHandle == self._position_notification_handle:
            self._on_position(data)
        elif cHandle == self._button_notification_handle:
            self._on_button(data)
        elif cHandle == self._temp_notification_handle:
            self._on_temperature(data)
        elif cHandle == self._battery_notification_handle:
            self._on_battery(data)

class Shoppe(DefaultDelegate):
    """A scanner class to connect to wands
    """
    def __init__(self, wand_class=Wand, debug=False):
        """Create a new scanner

        Keyword Arguments:
            wand_class {class} -- Class to use when connecting to wand (default: {Wand})
            debug {bool} -- Print debug messages (default: {False})
        """
        super().__init__()
        self.wand_class = wand_class
        self.debug = debug
        self._name = None
        self._prefix = None
        self._mac = None
        self._scanner = Scanner().withDelegate(self)

    def scan(self, name=None, prefix="Kano-Wand", mac=None, timeout=1.0, connect=False):
        """Scan for devices

        Keyword Arguments:
            name {str} -- Name of the device to scan for (default: {None})
            prefix {str} -- Prefix of name of device to scan for (default: {"Kano-Wand"})
            mac {str} -- MAC Address of the device to scan for (default: {None})
            timeout {float} -- Timeout before returning from scan (default: {1.0})
            connect {bool} -- Connect to the wands automatically (default: {False})

        Returns:
            Wand[] -- Array of wand objects
        """

        if self.debug:
            print(f"Scanning for {timeout} seconds...")
        try:
            name_check = not (name is None)
            prefix_check = not (prefix is None)
            mac_check = not (mac is None)
            assert name_check or prefix_check or mac_check
        except AssertionError as e:
            print("Either a name, prefix, or mac address must be provided to find a wand")
            raise e

        if name is not None:
            self._name = name
        elif prefix is not None:
            self._prefix = prefix
        elif mac is not None:
            self._mac = mac

        self.wands = []
        self._scanner.scan(timeout)
        if connect:
            for wand in self.wands:
                wand.connect()
        return self.wands

    def handleDiscovery(self, device, isNewDev, isNewData):
        """Check if the device matches

        Arguments:
            device {bluepy.ScanEntry} -- Device data
            isNewDev {bool} -- Whether the device is new
            isNewData {bool} -- Whether the device has already been seen
        """

        if isNewDev:
            mode = 0
            if(self._name is not None):
                mode += 1
            if (self._prefix is not None):
                mode += 1
            if(self._mac is not None):
                mode += 1
            # Perform initial detection attempt
            found = 0
            if device.addr == self._mac:
                found += 1
            name = device.getValueText(9)
            if name == self._name:
                found += 1
            elif name.startswith(self._prefix):
                found += 1
            if found >= mode:
                self.wands.append(self.wand_class(device, debug=self.debug))
            elif self.debug:
                if name != "None":
                    print(f"Mac: {device.addr}\tCommon Name: {name}")
                else:
                    print(f"Mac: {device.addr}")
