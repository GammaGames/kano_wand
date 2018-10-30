from bluepy.btle import *
import traceback
import sys

BLE_UUID_INFORMATION_SERVICE              = '64A70010-F691-4B93-A6F4-0968F5B648F8'
BLE_UUID_INFORMATION_ORGANIZATION_CHAR    = '64A7000B-F691-4B93-A6F4-0968F5B648F8'
BLE_UUID_INFORMATION_SW_CHAR              = '64A70013-F691-4B93-A6F4-0968F5B648F8'
BLE_UUID_INFORMATION_HW_CHAR              = '64A70001-F691-4B93-A6F4-0968F5B648F8'

BLE_UUID_IO_SERVICE                       = '64A70012-F691-4B93-A6F4-0968F5B648F8'
BLE_UUID_IO_BATTERY_CHAR                  = '64A70007-F691-4B93-A6F4-0968F5B648F8'
BLE_UUID_IO_USER_BUTTON_CHAR              = '64A7000D-F691-4B93-A6F4-0968F5B648F8'
BLE_UUID_IO_VIBRATOR_CHAR                 = '64A70008-F691-4B93-A6F4-0968F5B648F8'
BLE_UUID_IO_LED_CHAR                      = '64A70009-F691-4B93-A6F4-0968F5B648F8'
BLE_UUID_IO_KEEP_ALIVE_CHAR               = '64A7000F-F691-4B93-A6F4-0968F5B648F8'

BLE_UUID_SENSOR_SERVICE                   = '64A70011-F691-4B93-A6F4-0968F5B648F8'
BLE_UUID_SENSOR_TEMP_CHAR                 = '64A70014-F691-4B93-A6F4-0968F5B648F8'
BLE_UUID_SENSOR_QUATERNIONS_CHAR          = '64A70002-F691-4B93-A6F4-0968F5B648F8'
BLE_UUID_SENSOR_RAW_CHAR                  = '64A7000A-F691-4B93-A6F4-0968F5B648F8'
BLE_UUID_SENSOR_MOTION_CHAR               = '64A7000C-F691-4B93-A6F4-0968F5B648F8'
BLE_UUID_SENSOR_MAGN_CALIBRATE_CHAR       = '64A70021-F691-4B93-A6F4-0968F5B648F8'
BLE_UUID_SENSOR_QUATERNIONS_RESET_CHAR = '64A70004-F691-4B93-A6F4-0968F5B648F8'

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

class Wand(Peripheral):
    def __init__(self, device):
        super().__init__(None)
        self._mac = device.addr.upper()
        self._addrType = device.addrType
        self._connected = False

    def connect(self):
        super().connect(self._mac, self._addrType)
        self._info_service = self.getServiceByUUID(BLE_UUID_INFORMATION_SERVICE)
        self._io_service = self.getServiceByUUID(BLE_UUID_IO_SERVICE)
        self._sensor_service = self.getServiceByUUID(BLE_UUID_SENSOR_SERVICE)

    def set_led(self, on=True, color="0x2185d0"):
        color = int(color, 16)

        message = []
        message.append(1)

        r = (color >> 16) & 255
        g = (color >> 8) & 255
        b = color & 255
        rgb = (((r & 248) << 8) + ((g & 252) << 3) + ((b & 248) >> 3))
        message.append(rgb >> 8)
        message.append(rgb & 0xff)

        char = self._io_service.getCharacteristics(BLE_UUID_IO_LED_CHAR)[0]
        return char.write(bytes(message), withResponse=True)


class WandScanner(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        self._name = None
        self._prefix = None
        self._mac = None
        self._scanner = Scanner().withDelegate(self)

    def scan(self, name=None, prefix="Kano-Wand", mac=None, timeout=10.0, connect=False):
        wands = []

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
        self._scanner.scan(1.0)
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
                self.wands.append(Wand(device))

class ScanDelegate(DefaultDelegate):
    def __init__(self, prefix="Kano-Wand"):
        self.prefix = prefix
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            name = dev.getValueText(9)
            if (str(name).startswith(self.prefix)):
                print(name)
                device = Peripheral(dev.addr.upper(), dev.addrType)
                print("test")
                serv = device.getServiceByUUID(BLE_UUID_IO_SERVICE)
                chs = serv.getCharacteristics(BLE_UUID_IO_LED_CHAR)
                # for ch in chs:
                #     ch.write(bytes(message))
                # device.disconnect()

    def handleNotification(self, cHandle, data):
        print(data)

if __name__ == "__main__":
    scanner = WandScanner()
    wands = []
    try:
        wands = scanner.scan(connect=True)
        for wand in wands:
            wand.set_led()
            wand.disconnect()
        # except BTLEException as e:
            # print("Disconnected!")

    except KeyboardInterrupt as e:
        # Detect keyboard interrupt and close down
        # bleClient gracefully
        for wand in wands:
            wand.disconnect()
        print("Keyboard interrupt")
