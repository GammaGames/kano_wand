from enum import Enum
from bluepy.btle import *
import inspect
import numpy
import threading
import uuid

from time import sleep

class INFO(Enum):
    SERVICE = '64A70010-F691-4B93-A6F4-0968F5B648F8'
    ORGANIZATION_CHAR = '64A7000B-F691-4B93-A6F4-0968F5B648F8'
    SOFTWARE_CHAR = '64A70013-F691-4B93-A6F4-0968F5B648F8'
    HARDWARE_CHAR = '64A70001-F691-4B93-A6F4-0968F5B648F8'

class IO(Enum):
    SERVICE = '64A70012-F691-4B93-A6F4-0968F5B648F8'
    BATTERY_CHAR = '64A70007-F691-4B93-A6F4-0968F5B648F8'
    USER_BUTTON_CHAR = '64A7000D-F691-4B93-A6F4-0968F5B648F8'
    VIBRATOR_CHAR = '64A70008-F691-4B93-A6F4-0968F5B648F8'
    LED_CHAR = '64A70009-F691-4B93-A6F4-0968F5B648F8'
    KEEP_ALIVE_CHAR = '64A7000F-F691-4B93-A6F4-0968F5B648F8'

class SENSOR(Enum):
    SERVICE = '64A70011-F691-4B93-A6F4-0968F5B648F8'
    TEMP_CHAR = '64A70014-F691-4B93-A6F4-0968F5B648F8'
    QUATERNIONS_CHAR = '64A70002-F691-4B93-A6F4-0968F5B648F8'
    # RAW_CHAR = '64A7000A-F691-4B93-A6F4-0968F5B648F8'
    # MOTION_CHAR = '64A7000C-F691-4B93-A6F4-0968F5B648F8'
    MAGN_CALIBRATE_CHAR = '64A70021-F691-4B93-A6F4-0968F5B648F8'
    QUATERNIONS_RESET_CHAR = '64A70004-F691-4B93-A6F4-0968F5B648F8'

class PATTERN(Enum):
    REGULAR = 1
    SHORT = 2
    BURST = 3
    LONG = 4
    SHORT_LONG = 5
    SHORT_SHORT = 6
    BIG_PAUSE = 7

class Wand(Peripheral, DefaultDelegate):
    _position_notification_handle = 41
    _button_notification_handle = 33
    _notification_thread = None

    def __init__(self, device, name=None, debug=False):
        super().__init__(None)
        self.debug = debug
        self._dev = device
        self._name = device.getValueText(9)

        if debug:
            print(f"Wand: {self._name}\n\rWand Mac: {device.addr}")

        self._connected = False
        self._position_callbacks = {}
        self._position_subscribed = False
        self._button_callbacks = {}
        self._button_subscribed = False

    def connect(self):
        if self.debug:
            print(f"Connecting to {self._name}...")

        super(Wand, self).connect(self._dev)
        self._connected = True
        self.setDelegate(self)
        self._info_service = self.getServiceByUUID(INFO.SERVICE.value)
        self._io_service = self.getServiceByUUID(IO.SERVICE.value)
        self._sensor_service = self.getServiceByUUID(SENSOR.SERVICE.value)

        # If the wand has a position method, then subscribe automatically
        self._on_position_method = inspect.getsourcelines(self.on_position)[0][1].strip().rstrip("\n\r").strip() != "pass"
        if self._on_position_method:
            self.subscribe_position()

        # If the wand has a button method, then subscribe automatically
        self._on_button_method = inspect.getsourcelines(self.on_button)[0][1].strip().rstrip("\n\r").strip() != "pass"
        if self._on_button_method:
            self.subscribe_button()

        if self.debug:
            print(f"Connected to {self._name}")

    def disconnect(self):
        super().disconnect()
        self._connected = False

        if self.debug:
            print(f"Disconnected from {self._name}")

    # INFO
    def get_organization(self):
        if not hasattr(self, "_organization_handle"):
            handle = self._info_service.getCharacteristics(INFO.ORGANIZATION_CHAR.value)[0]
            self._organization_handle = handle.getHandle()
        return self.readCharacteristic(self._organization_handle).decode("utf-8")

    def get_software_version(self):
        if not hasattr(self, "_software_handle"):
            handle = self._info_service.getCharacteristics(INFO.SOFTWARE_CHAR.value)[0]
            self._software_handle = handle.getHandle()
        return self.readCharacteristic(self._software_handle).decode("utf-8")

    def get_hardware_version(self):
        if not hasattr(self, "_hardware_handle"):
            handle = self._info_service.getCharacteristics(INFO.HARDWARE_CHAR.value)[0]
            self._hardware_handle = handle.getHandle()
        return self.readCharacteristic(self._hardware_handle).decode("utf-8")

    # IO
    def get_battery(self):
        if not hasattr(self, "_battery_handle"):
            handle = self._io_service.getCharacteristics(IO.BATTERY_CHAR.value)[0]
            self._battery_handle = handle.getHandle()
        return self.readCharacteristic(self._battery_handle).decode("utf-8")

    def get_button(self):
        if not hasattr(self, "_button_handle"):
            handle = self._io_service.getCharacteristics(IO.USER_BUTTON_CHAR.value)[0]
            self._button_handle = handle.getHandle()

        data = self.readCharacteristic(self._button_handle)
        return data[0] == 1

    def vibrate(self, pattern=PATTERN.REGULAR):
        if isinstance(pattern, PATTERN):
            message = [pattern.value]
        else:
            message = [pattern]

        if not hasattr(self, "_vibrator_handle"):
            handle = self._io_service.getCharacteristics(IO.VIBRATOR_CHAR.value)[0]
            self._vibrator_handle = handle.getHandle()
        return self.writeCharacteristic(self._vibrator_handle, bytes(message), withResponse=True)

    def set_led(self, color="0x2185d0", on=True):
        message = []
        if on:
            message.append(1)
        else:
            message.append(0)

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

        return id

    def off(self, uuid):
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

        return removed

    def subscribe_position(self):
        if not hasattr(self, "_position_handle"):
            handle = self._sensor_service.getCharacteristics(SENSOR.QUATERNIONS_CHAR.value)[0]
            self._position_handle = handle.getHandle()

        self.writeCharacteristic(self._position_handle + 1, bytes([1, 0]))

        if self._notification_thread == None:
            self._start_notification_thread()

    def unsubscribe_position(self):
        pass

    def subscribe_button(self):
        if not hasattr(self, "_button_handle"):
            handle = self._io_service.getCharacteristics(IO.USER_BUTTON_CHAR.value)[0]
            self._button_handle = handle.getHandle()

        self.writeCharacteristic(self._button_handle + 1, bytes([1, 0]))

        if self._notification_thread == None:
            self._start_notification_thread()

    def unsubscribe_button(self):
        pass

    def _start_notification_thread(self):
        self.reset_position()
        self._notification_thread = threading.Thread(target=self._run)
        self._notification_thread.start()

    def _run(self):
        while self._connected:
            try:
                if super().waitForNotifications(1):
                    continue
            except:
                continue

    def _on_position(self, data):
        w = numpy.int16(numpy.uint16(int.from_bytes(data[0:2], byteorder='little')))
        x = numpy.int16(numpy.uint16(int.from_bytes(data[2:4], byteorder='little')))
        y = numpy.int16(numpy.uint16(int.from_bytes(data[4:6], byteorder='little')))
        z = numpy.int16(numpy.uint16(int.from_bytes(data[6:8], byteorder='little')))
        if self.debug:
            roll = f"Roll: {w}".ljust(16)
            print(f"{roll}(x, y, z): ({x}, {y}, {z})")
        self.on_position(w, x, y, z)
        for callback in self._position_callbacks.values():
            callback(w, x, y, z)

    def on_position(self, roll, x, y, z):
        pass

    def reset_position(self):
        handle = self._sensor_service.getCharacteristics(SENSOR.QUATERNIONS_RESET_CHAR.value)[0].getHandle()
        self.writeCharacteristic(handle, bytes([1]))

    def _on_button(self, data):
        val = data[0]
        if self.debug:
            print(f"Button: {val}")
        self.on_button(val)
        for callback in self._button_callbacks.values():
            callback(val)

    def on_button(self, value):
        pass

    def handleNotification(self, cHandle, data):
        if cHandle == self._position_notification_handle:
            self._on_position(data)
        elif cHandle == self._button_notification_handle:
            self._on_button(data)

class WandScanner(DefaultDelegate):
    def __init__(self, wand_class=Wand, debug=False):
        DefaultDelegate.__init__(self)
        self.wand_class = wand_class
        self.debug = debug
        self._name = None
        self._prefix = None
        self._mac = None
        self._scanner = Scanner().withDelegate(self)

    def scan(self, name=None, prefix="Kano-Wand", mac=None, timeout=1.0, connect=False):
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
