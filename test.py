import bluepy.btle as ble
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

# return this.write(
#     BLE_UUID_IO_SERVICE,
#     BLE_UUID_IO_LED_CHAR,
#     message,
# );

# write(sId, cId, value) {
#     this.manager.log.trace(`[${this.getAdvertisementName()}]: Write: ${sId}:${cId} => ${value}`);
#     return this.setup()
#         .then(() => {
#             const char = this.getCharacteristic(sId, cId);
#             return BLEDevice.write(char, value);
#         });
# }

if(len(sys.argv) < 2):
    color = 0xFF0000
else:
    color = int(f"0x{sys.argv[1]}", 16)

message = []
message.append(1)

r = (color >> 16) & 255
g = (color >> 8) & 255
b = color & 255
rgb = (((r & 248) << 8) + ((g & 252) << 3) + ((b & 248) >> 3))
message.append(rgb >> 8)
message.append(rgb & 0xff)

class ScanDelegate(ble.DefaultDelegate):
    def __init__(self, prefix="Kano-Wand"):
        self.prefix = prefix
        ble.DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            name = dev.getValueText(9)
            if (str(name).startswith(self.prefix)):
                print(name)
                device = ble.Peripheral(dev.addr.upper(), dev.addrType)
                print("test")
                serv = device.getServiceByUUID(BLE_UUID_IO_SERVICE)
                chs = serv.getCharacteristics(BLE_UUID_IO_LED_CHAR)
                for ch in chs:
                    ch.write(bytes(message))
                # device.disconnect()

    def handleNotification(self, cHandle, data):
        print(data)

scanner = ble.Scanner().withDelegate(ScanDelegate())

try:
    devices = scanner.scan(1.0)
except ble.BTLEException as e:
    print("Disconnected!")
