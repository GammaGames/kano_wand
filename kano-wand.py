#!/usr/bin/python3

from enum import Enum
from bluepy.btle import *
# import traceback
import inspect
import numpy

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

class OPERATIONS(Enum):
    BUTTON_COMMAND = [0x01]
    SET_DFU_NAME = [0x02]
    CREATE_COMMAND = [0x01, 0x01]
    CREATE_DATA = [0x01, 0x02]
    RECEIPT_NOTIFICATIONS = [0x02]
    CALCULATE_CHECKSUM = [0x03]
    EXECUTE = [0x04]
    SELECT_COMMAND = [0x06, 0x01]
    SELECT_DATA = [0x06, 0x02]
    RESPONSE = [0x60, 0x20]


# [CA:DE:F8:06:AB:D4][LE]> primary
# attr handle: 0x0001, end grp handle: 0x0009 uuid: 00001800-0000-1000-8000-00805f9b34fb
# attr handle: 0x000a, end grp handle: 0x000d uuid: 00001801-0000-1000-8000-00805f9b34fb
# attr handle: 0x000e, end grp handle: 0x0014 uuid: 64a70010-f691-4b93-a6f4-0968f5b648f8
# attr handle: 0x0015, end grp handle: 0x0026 uuid: 64a70012-f691-4b93-a6f4-0968f5b648f8
# attr handle: 0x0027, end grp handle: 0x003e uuid: 64a70011-f691-4b93-a6f4-0968f5b648f8
# attr handle: 0x003f, end grp handle: 0xffff uuid: 0000fe59-0000-1000-8000-00805f9b34fb
# [CA:DE:F8:06:AB:D4][LE]> char-desc
# handle: 0x0001, uuid: 00002800-0000-1000-8000-00805f9b34fb
# handle: 0x0002, uuid: 00002803-0000-1000-8000-00805f9b34fb
# handle: 0x0003, uuid: 00002a00-0000-1000-8000-00805f9b34fb
# handle: 0x0004, uuid: 00002803-0000-1000-8000-00805f9b34fb
# handle: 0x0005, uuid: 00002a01-0000-1000-8000-00805f9b34fb
# handle: 0x0006, uuid: 00002803-0000-1000-8000-00805f9b34fb
# handle: 0x0007, uuid: 00002a04-0000-1000-8000-00805f9b34fb
# handle: 0x0008, uuid: 00002803-0000-1000-8000-00805f9b34fb
# handle: 0x0009, uuid: 00002aa6-0000-1000-8000-00805f9b34fb
# handle: 0x000a, uuid: 00002800-0000-1000-8000-00805f9b34fb
# handle: 0x000b, uuid: 00002803-0000-1000-8000-00805f9b34fb
# handle: 0x000c, uuid: 00002a05-0000-1000-8000-00805f9b34fb
# handle: 0x000d, uuid: 00002902-0000-1000-8000-00805f9b34fb
# handle: 0x000e, uuid: 00002800-0000-1000-8000-00805f9b34fb
# handle: 0x000f, uuid: 00002803-0000-1000-8000-00805f9b34fb
# handle: 0x0010, uuid: 64a7000b-f691-4b93-a6f4-0968f5b648f8
# handle: 0x0011, uuid: 00002803-0000-1000-8000-00805f9b34fb
# handle: 0x0012, uuid: 64a70013-f691-4b93-a6f4-0968f5b648f8
# handle: 0x0013, uuid: 00002803-0000-1000-8000-00805f9b34fb
# handle: 0x0014, uuid: 64a70001-f691-4b93-a6f4-0968f5b648f8
# handle: 0x0015, uuid: 00002800-0000-1000-8000-00805f9b34fb
# handle: 0x0016, uuid: 00002803-0000-1000-8000-00805f9b34fb
# handle: 0x0017, uuid: 64a70007-f691-4b93-a6f4-0968f5b648f8
# handle: 0x0018, uuid: 00002902-0000-1000-8000-00805f9b34fb
# handle: 0x0019, uuid: 00002901-0000-1000-8000-00805f9b34fb
# handle: 0x001a, uuid: 00002803-0000-1000-8000-00805f9b34fb
# handle: 0x001b, uuid: 64a70008-f691-4b93-a6f4-0968f5b648f8
# handle: 0x001c, uuid: 00002901-0000-1000-8000-00805f9b34fb
# handle: 0x001d, uuid: 00002803-0000-1000-8000-00805f9b34fb
# handle: 0x001e, uuid: 64a70009-f691-4b93-a6f4-0968f5b648f8
# handle: 0x001f, uuid: 00002901-0000-1000-8000-00805f9b34fb
# handle: 0x0020, uuid: 00002803-0000-1000-8000-00805f9b34fb
# handle: 0x0021, uuid: 64a7000d-f691-4b93-a6f4-0968f5b648f8
# handle: 0x0022, uuid: 00002902-0000-1000-8000-00805f9b34fb
# handle: 0x0023, uuid: 00002901-0000-1000-8000-00805f9b34fb
# handle: 0x0024, uuid: 00002803-0000-1000-8000-00805f9b34fb
# handle: 0x0025, uuid: 64a7000f-f691-4b93-a6f4-0968f5b648f8
# handle: 0x0026, uuid: 00002901-0000-1000-8000-00805f9b34fb
# handle: 0x0027, uuid: 00002800-0000-1000-8000-00805f9b34fb
# handle: 0x0028, uuid: 00002803-0000-1000-8000-00805f9b34fb
# handle: 0x0029, uuid: 64a70002-f691-4b93-a6f4-0968f5b648f8
# handle: 0x002a, uuid: 00002902-0000-1000-8000-00805f9b34fb
# handle: 0x002b, uuid: 00002901-0000-1000-8000-00805f9b34fb
# handle: 0x002c, uuid: 00002803-0000-1000-8000-00805f9b34fb
# handle: 0x002d, uuid: 64a70004-f691-4b93-a6f4-0968f5b648f8
# handle: 0x002e, uuid: 00002901-0000-1000-8000-00805f9b34fb
# handle: 0x002f, uuid: 00002803-0000-1000-8000-00805f9b34fb
# handle: 0x0030, uuid: 64a7000a-f691-4b93-a6f4-0968f5b648f8
# handle: 0x0031, uuid: 00002902-0000-1000-8000-00805f9b34fb
# handle: 0x0032, uuid: 00002901-0000-1000-8000-00805f9b34fb
# handle: 0x0033, uuid: 00002803-0000-1000-8000-00805f9b34fb
# handle: 0x0034, uuid: 64a7000c-f691-4b93-a6f4-0968f5b648f8
# handle: 0x0035, uuid: 00002902-0000-1000-8000-00805f9b34fb
# handle: 0x0036, uuid: 00002901-0000-1000-8000-00805f9b34fb
# handle: 0x0037, uuid: 00002803-0000-1000-8000-00805f9b34fb
# handle: 0x0038, uuid: 64a70014-f691-4b93-a6f4-0968f5b648f8
# handle: 0x0039, uuid: 00002902-0000-1000-8000-00805f9b34fb
# handle: 0x003a, uuid: 00002901-0000-1000-8000-00805f9b34fb
# handle: 0x003b, uuid: 00002803-0000-1000-8000-00805f9b34fb
# handle: 0x003c, uuid: 64a70021-f691-4b93-a6f4-0968f5b648f8
# handle: 0x003d, uuid: 00002902-0000-1000-8000-00805f9b34fb
# handle: 0x003e, uuid: 00002901-0000-1000-8000-00805f9b34fb
# handle: 0x003f, uuid: 00002800-0000-1000-8000-00805f9b34fb
# handle: 0x0040, uuid: 00002803-0000-1000-8000-00805f9b34fb
# handle: 0x0041, uuid: 8ec90003-f315-4f60-9fb8-838830daea50
# handle: 0x0042, uuid: 00002902-0000-1000-8000-00805f9b34fb

class Wand(Peripheral, DefaultDelegate):
    _position_notification_handle = 41

    def __init__(self, device, name=None, debug=False):
        super().__init__(None)
        self.debug = debug
        self._dev = device
        self._name = device.getValueText(9)

        if debug:
            print(f"Wand: {self._name}\n\rWand Mac: {device.addr}")

        self._connected = False
        self._position_callbacks = []
        self._position_subscribed = False
        self._button_callbacks = []
        self._button_subscribed = False

        self._on_position_method = inspect.getsourcelines(self.on_position)[0][1].strip() == "pass"
        # TODO if has method, subscribe to position

    def connect(self):
        if self.debug:
            print(f"Connecting to {self._name}...")
        super(Wand, self).connect(self._dev)
        self._connected = True
        self.setDelegate(self)
        self._info_service = self.getServiceByUUID(INFO.SERVICE.value)
        self._io_service = self.getServiceByUUID(IO.SERVICE.value)
        self._sensor_service = self.getServiceByUUID(SENSOR.SERVICE.value)

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

    def on(self, event, callback):
        if self.debug:
            print(f"Adding callback to {event}...")

        if event == "position":
            self._position_callbacks.append(callback)

        # TODO return a hash based on the method

    def off(self, id):
        # TODO remove by id
        pass

    def subscribe_position(self):
        if not hasattr(self, "_position_handle"):
            handle = self._sensor_service.getCharacteristics(SENSOR.QUATERNIONS_CHAR.value)[0]
            self._position_handle = handle.getHandle()

        self.writeCharacteristic(self._position_handle + 1, b"\x01\x00")


        # self.writeCharacteristic(self._position_handle, bytes([1]), withResponse=True)
        # self.waitForNotifications(1)
        # svc = self.getServiceByUUID(SENSOR.SERVICE.value)
        # ch = svc.getCharacteristics(SENSOR.QUATERNIONS_CHAR.value)

        # ch.write(bytes([2, 0]))
        while True:
            if self.waitForNotifications(2):
                continue
            print("waiting...")

    def _on_position(self, data):
        w = numpy.int16(numpy.uint16(int.from_bytes(data[0:2], byteorder='little')))
        x = numpy.int16(numpy.uint16(int.from_bytes(data[2:4], byteorder='little')))
        y = numpy.int16(numpy.uint16(int.from_bytes(data[4:6], byteorder='little')))
        z = numpy.int16(numpy.uint16(int.from_bytes(data[6:8], byteorder='little')))
        if self.debug:
            roll = f"Roll: {w}".ljust(16)
            print(f"{roll}(x, y, z): ({x}, {y}, {z})")
        if self._on_position_method:
            self.on_position((w, x, y, z))
        for callback in self._position_callbacks:
            callback((w, x, y, z))

    def on_position(self, data):
        pass

    def handleNotification(self, cHandle, data):
        if cHandle == self._position_notification_handle:
            self._on_position(data)
        # TODO check event type
        # zope.event.notify(self.positionEvent())
        # subscribeButton() {
        #     if (this._buttonSubscribed) {
        #         return Promise.resolve();
        #     }
        #     // Synchronous state change. Multiple calls to subscribe will stop after the first
        #     this._buttonSubscribed = true;
        #     return this.subscribe(
        #         BLE_UUID_IO_SERVICE,
        #         BLE_UUID_IO_USER_BUTTON_CHAR,
        #         this.onUserButton,
        #     ).catch((e) => {
        #         // Revert state if failed to subscribe
        #         this._buttonSubscribed = false;
        #         throw e;
        #     });
        # }
        # unsubscribeButton() {
        #     if (!this._buttonSubscribed) {
        #         return Promise.resolve();
        #     }
        #     return this.unsubscribe(
        #         BLE_UUID_IO_SERVICE,
        #         BLE_UUID_IO_USER_BUTTON_CHAR,
        #     ).then(() => {
        #         // Stay subscribed until unsubscribe suceeds
        #         this._buttonSubscribed = false;
        #     });
        # }
        # getButtonStatus() {
        #     return this.read(BLE_UUID_IO_SERVICE, BLE_UUID_IO_USER_BUTTON_CHAR)
        #         .then(data => data[0]);
        # }

class WandScanner(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        self._name = None
        self._prefix = None
        self._mac = None
        self._scanner = Scanner().withDelegate(self)

    # TODO add debug
    # TODO pass in wand object
    def scan(self, name=None, prefix="Kano-Wand", mac=None, timeout=1.0, connect=False, debug=False):
        self.debug = debug
        if debug:
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
                self.wands.append(Wand(device, debug=self.debug))
            elif name != "None":
                print(f"Mac: {device.addr}\tCommon Name: {name}")
            else:
                print(f"Mac: {device.addr}")

if __name__ == "__main__":
    scanner = WandScanner()
    wands = []
    # try:
    wands = scanner.scan(connect=True, debug=True)
    for wand in wands:
        # colors = ["#db2828", "#f2711c", "#fbbd08", "#21ba45", "#2185d0", "#a333c8"]
        # for color in colors:
        #     wand.set_led(color)
        #     sleep(1)
        wand.vibrate(PATTERN.BURST)
        wand.subscribe_position()
        # wand.disconnect()

    # except KeyboardInterrupt as e:
    #     # Detect keyboard interrupt and close down
    #     # bleClient gracefully
    #     for wand in wands:
    #         wand.disconnect()
    #     print("Keyboard interrupt")
