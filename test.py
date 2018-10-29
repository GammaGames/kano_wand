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
BLE_UUID_SENSOR_QUATERNIONS_RESET_CHAR    = '64A70004-F691-4B93-A6F4-0968F5B648F8'

class Wand(Peripheral):
    def __init__(self, device):
        super().__init__(device.addr.upper(), device.addrType)
        self._info_service = self.getServiceByUUID(BLE_UUID_INFORMATION_SERVICE)
        self._io_service = self.getServiceByUUID(BLE_UUID_IO_SERVICE)
        self._sensor_service = self.getServiceByUUID(BLE_UUID_SENSOR_SERVICE)

    def set_led(self, on=True, color="0x2185d0"):
        color = int(f"0x{sys.argv[1]}", 16)

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

    def scan(self, name=None, prefix="Kano-Wand", mac=None, timeout=10.0):
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

# scanner = ble.Scanner().withDelegate(ScanDelegate())

# try:
#     devices = scanner.scan(1.0)
# except ble.BTLEException as e:
#     print("Disconnected!")

if __name__ == "__main__":
    scanner = WandScanner()
    try:
        wands = scanner.scan()
        for wand in wands:
            print(wand)
            wand.set_led()
            wand.disconnect()
    except BTLEException as e:
        print("Disconnected!")
