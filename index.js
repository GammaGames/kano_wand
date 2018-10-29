'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

var events = require('events');

class Package {
    constructor(extractor, buffer) {
        this.extractor = extractor;
        this.buffer = buffer;
        this.zipFile = null;
        this.manifest = null;
    }
    load() {
        return this.extractor.loadAsync(this.buffer)
            .then((zipFile) => {
                this.zipFile = zipFile;
                try {
                    return this.zipFile.file('manifest.json').async('string');
                } catch (e) {
                    throw new Error('Unable to find manifest, is this a proper DFU package?');
                }
            })
            .then((content) => {
                this.manifest = JSON.parse(content).manifest;
                return this;
            });
    }
    getImage(types) {
        let type;
        for (let i = 0; i < types.length; i += 1) {
            type = types[i];
            if (this.manifest[type]) {
                const entry = this.manifest[type];
                const result = {
                    type,
                    initFile: entry.dat_file,
                    imageFile: entry.bin_file,
                };

                return this.zipFile.file(result.initFile).async('arraybuffer')
                    .then((data) => {
                        result.initData = data;
                        return this.zipFile.file(result.imageFile).async('arraybuffer');
                    })
                    .then((data) => {
                        result.imageData = data;
                        return result;
                    });
            }
        }
        return null;
    }
    getBaseImage() {
        return this.getImage(['softdevice', 'bootloader', 'softdevice_bootloader']);
    }
    getAppImage() {
        return this.getImage(['application']);
    }
}

let counter = 0;

class Device extends events.EventEmitter {
    constructor(manager, abstract = false) {
        super();
        this.manager = manager;
        this.abstract = abstract;
        this.type = 'device';
        // Abstract devices don't have an id, or increement the counter
        if (this.abstract) {
            return;
        }
        this.id = counter.toString();
        counter += 1;
    }
    terminate() {
        this.manager.removeDevice(this);
        return Promise.resolve(this.id);
    }
}

// Mixin extending a BLEDevice
const WandMixin = (BLEDevice) => {
    const BLE_UUID_INFORMATION_SERVICE              = BLEDevice.localUuid('64A70010-F691-4B93-A6F4-0968F5B648F8');
    const BLE_UUID_INFORMATION_ORGANISATION_CHAR    = BLEDevice.localUuid('64A7000B-F691-4B93-A6F4-0968F5B648F8');
    const BLE_UUID_INFORMATION_SW_CHAR              = BLEDevice.localUuid('64A70013-F691-4B93-A6F4-0968F5B648F8');
    const BLE_UUID_INFORMATION_HW_CHAR              = BLEDevice.localUuid('64A70001-F691-4B93-A6F4-0968F5B648F8');

    const BLE_UUID_IO_SERVICE                       = BLEDevice.localUuid('64A70012-F691-4B93-A6F4-0968F5B648F8');
    const BLE_UUID_IO_BATTERY_CHAR                  = BLEDevice.localUuid('64A70007-F691-4B93-A6F4-0968F5B648F8');
    const BLE_UUID_IO_USER_BUTTON_CHAR              = BLEDevice.localUuid('64A7000D-F691-4B93-A6F4-0968F5B648F8');
    const BLE_UUID_IO_VIBRATOR_CHAR                 = BLEDevice.localUuid('64A70008-F691-4B93-A6F4-0968F5B648F8');
    const BLE_UUID_IO_LED_CHAR                      = BLEDevice.localUuid('64A70009-F691-4B93-A6F4-0968F5B648F8');
    const BLE_UUID_IO_KEEP_ALIVE_CHAR               = BLEDevice.localUuid('64A7000F-F691-4B93-A6F4-0968F5B648F8');

    const BLE_UUID_SENSOR_SERVICE                   = BLEDevice.localUuid('64A70011-F691-4B93-A6F4-0968F5B648F8');
    const BLE_UUID_SENSOR_QUATERNIONS_CHAR          = BLEDevice.localUuid('64A70002-F691-4B93-A6F4-0968F5B648F8');
    const BLE_UUID_SENSOR_RAW_CHAR                  = BLEDevice.localUuid('64A7000A-F691-4B93-A6F4-0968F5B648F8');
    const BLE_UUID_SENSOR_MOTION_CHAR               = BLEDevice.localUuid('64A7000C-F691-4B93-A6F4-0968F5B648F8');
    const BLE_UUID_SENSOR_MAGN_CALIBRATE_CHAR       = BLEDevice.localUuid('64A70021-F691-4B93-A6F4-0968F5B648F8');
    const BLE_UUID_SENSOR_QUATERNIONS_RESET_CHAR    = BLEDevice.localUuid('64A70004-F691-4B93-A6F4-0968F5B648F8');
    const BLE_UUID_SENSOR_TEMP_CHAR                 = BLEDevice.localUuid('64A70014-F691-4B93-A6F4-0968F5B648F8');


    /**
     * Emits: position, temperature, battery-status, user-button, sleep
     */
    class Wand extends BLEDevice {
        constructor(...args) {
            super(...args);
            this.type = 'wand';
            this._eulerSubscribed = false;
            this._temperatureSubscribed = false;
            this._buttonSubscribed = false;
            this.onUserButton = this.onUserButton.bind(this);
            this.onPosition = this.onPosition.bind(this);
            this.onBatteryStatus = this.onBatteryStatus.bind(this);
        }
        static uInt8ToUInt16(byteA, byteB) {
            const number = (((byteB & 0xff) << 8) | byteA);
            const sign = byteB & (1 << 7);

            if (sign) {
                return 0xFFFF0000 | number;
            }

            return number;
        }
        // --- INFORMATION ---
        getOrganisation() {
            return this.read(BLE_UUID_INFORMATION_SERVICE, BLE_UUID_INFORMATION_ORGANISATION_CHAR)
                .then(data => BLEDevice.uInt8ArrayToString(data));
        }
        getSoftwareVersion() {
            return this.read(BLE_UUID_INFORMATION_SERVICE, BLE_UUID_INFORMATION_SW_CHAR)
                .then(data => BLEDevice.uInt8ArrayToString(data));
        }
        getHardwareBuild() {
            return this.read(BLE_UUID_INFORMATION_SERVICE, BLE_UUID_INFORMATION_HW_CHAR)
                .then(data => data[0]);
        }
        // --- IO ---
        getBatteryStatus() {
            return this.read(BLE_UUID_IO_SERVICE, BLE_UUID_IO_BATTERY_CHAR)
                .then(data => data[0]);
        }
        subscribeBatteryStatus() {
            return this.subscribe(
                BLE_UUID_IO_SERVICE,
                BLE_UUID_IO_BATTERY_CHAR,
                this.onBatteryStatus,
            );
        }
        unsubscribeBatteryStatus() {
            return this.unsubscribe(
                BLE_UUID_IO_SERVICE,
                BLE_UUID_IO_BATTERY_CHAR,
                this.onBatteryStatus,
            );
        }
        getVibratorStatus() {
            return this.read(BLE_UUID_IO_SERVICE, BLE_UUID_IO_VIBRATOR_CHAR)
                .then(data => data[0]);
        }
        vibrate(pattern) {
            return this.write(
                BLE_UUID_IO_SERVICE,
                BLE_UUID_IO_VIBRATOR_CHAR,
                [pattern],
            );
        }
        getLedStatus() {
            return this.read(BLE_UUID_IO_SERVICE, BLE_UUID_IO_LED_CHAR)
                .then(data => data[0]);
        }
        setLed(state, color = 0x000000) {
            /* eslint no-bitwise: "warn" */
            const message = new Uint8Array(3);
            message.set([state ? 1 : 0]);
            const r = (color >> 16) & 255;
            const g = (color >> 8) & 255;
            const b = color & 255;
            const rgb565 = (((r & 248) << 8) + ((g & 252) << 3) + ((b & 248) >> 3));
            message.set([rgb565 >> 8], 1);
            message.set([rgb565 & 0xff], 2);
            return this.write(
                BLE_UUID_IO_SERVICE,
                BLE_UUID_IO_LED_CHAR,
                message,
            );
        }
        subscribePosition() {
            if (this._eulerSubscribed) {
                return Promise.resolve();
            }
            // Synchronous state change. Multiple calls to subscribe will stop after the first
            this._eulerSubscribed = true;
            return this.subscribe(
                BLE_UUID_SENSOR_SERVICE,
                BLE_UUID_SENSOR_QUATERNIONS_CHAR,
                this.onPosition,
            ).catch((e) => {
                // Revert state if failed to subscribe
                this._eulerSubscribed = false;
                throw e;
            });
        }
        subscribeButton() {
            if (this._buttonSubscribed) {
                return Promise.resolve();
            }
            // Synchronous state change. Multiple calls to subscribe will stop after the first
            this._buttonSubscribed = true;
            return this.subscribe(
                BLE_UUID_IO_SERVICE,
                BLE_UUID_IO_USER_BUTTON_CHAR,
                this.onUserButton,
            ).catch((e) => {
                // Revert state if failed to subscribe
                this._buttonSubscribed = false;
                throw e;
            });
        }
        unsubscribeButton() {
            if (!this._buttonSubscribed) {
                return Promise.resolve();
            }
            return this.unsubscribe(
                BLE_UUID_IO_SERVICE,
                BLE_UUID_IO_USER_BUTTON_CHAR,
            ).then(() => {
                // Stay subscribed until unsubscribe suceeds
                this._buttonSubscribed = false;
            });
        }
        getButtonStatus() {
            return this.read(BLE_UUID_IO_SERVICE, BLE_UUID_IO_USER_BUTTON_CHAR)
                .then(data => data[0]);
        }
        keepAlive() {
            return this.write(
                BLE_UUID_IO_SERVICE,
                BLE_UUID_IO_KEEP_ALIVE_CHAR,
                [1],
            );
        }
        // --- Position ---
        subscribePosition() {
            if (this._eulerSubscribed) {
                return Promise.resolve();
            }
            // Synchronous state change. Multiple calls to subscribe will stop after the first
            this._eulerSubscribed = true;
            return this.subscribe(
                BLE_UUID_SENSOR_SERVICE,
                BLE_UUID_SENSOR_QUATERNIONS_CHAR,
                this.onPosition,
            ).catch((e) => {
                // Revert state if failed to subscribe
                this._eulerSubscribed = false;
                throw e;
            });
        }
        unsubscribePosition() {
            if (!this._eulerSubscribed) {
                return Promise.resolve();
            }
            return this.unsubscribe(
                BLE_UUID_SENSOR_SERVICE,
                BLE_UUID_SENSOR_QUATERNIONS_CHAR,
                this.onPosition,
            ).then(() => {
                // Stay subscribed until unsubscribe succeeds
                this._eulerSubscribed = false;
            });
        }
        subscribeTemperature() {
            if (this._temperatureSubscribed) {
                return Promise.resolve();
            }
            // Synchronous state change. Multiple calls to subscribe will stop after the first
            this._temperatureSubscribed = true;
            return this.subscribe(
                BLE_UUID_SENSOR_SERVICE,
                BLE_UUID_SENSOR_TEMP_CHAR,
                this.onTemperature,
            ).catch((e) => {
                // Revert state if failed to subscribe
                this._temperatureSubscribed = false;
                throw e;
            });
        }
        unsubscribeTemperature() {
            if (!this._temperatureSubscribed) {
                return Promise.resolve();
            }
            return this.unsubscribe(
                BLE_UUID_SENSOR_SERVICE,
                BLE_UUID_SENSOR_TEMP_CHAR,
                this.onTemperature,
            ).then(() => {
                // Stay subscribed until unsubscribe succeeds
                this._temperatureSubscribed = false;
            });
        }
        calibrateMagnetometer() {
            return this.calibrateChar(BLE_UUID_SENSOR_SERVICE, BLE_UUID_SENSOR_MAGN_CALIBRATE_CHAR);
        }
        resetQuaternions() {
            return this.write(BLE_UUID_SENSOR_SERVICE, BLE_UUID_SENSOR_QUATERNIONS_RESET_CHAR, [1]);
        }
        calibrateChar(sId, cId) {
            const wasSubscribed = this._eulerSubscribed;

            return this.unsubscribePosition()
                .then(() => {
                    // Promise that will resolve once the calibration is done
                    return new Promise((resolve, reject) => {
                        this.subscribe(
                            sId,
                            cId,
                            (data) => {
                                // Once the status means calibrated, resolve the promise
                                const status = data[0];
                                if (status === 2) {
                                    resolve();
                                } else if (status === 3) {
                                    reject(new Error('Calibration failed'));
                                }
                            },
                        ).then(() => this.write(sId, cId, [1]));
                    });
                })
                .then(() => {
                    if (wasSubscribed) {
                        return this.subscribePosition();
                    }
                    return null;
                });
        }
        update(buffer) {
            return this.manager.updateDFUDevice(this, buffer);
        }
        onUserButton(data) {
            this.emit('user-button', data[0]);
        }
        onPosition(r) {
            const w = Wand.uInt8ToUInt16(r[0], r[1]);
            const x = Wand.uInt8ToUInt16(r[2], r[3]);
            const y = Wand.uInt8ToUInt16(r[4], r[5]);
            const z = Wand.uInt8ToUInt16(r[6], r[7]);
            this.emit('position', [w, x, y, z]);
        }
        onTemperature(temperature) {
            let auxTemperature = Wand.uInt8ToUInt16(temperature[0], temperature[1]);
            this.emit('temperature', auxTemperature);
        }
        onBatteryStatus(data) {
            this.emit('battery-status', data[0]);
        }
    }

    return Wand;
};

const CRC32 = {};

CRC32.version = '1.2.0';
/* see perf/crc32table.js */
function signed_crc_table() {
	var c = 0, table = new Array(256);

	for(var n =0; n != 256; ++n){
		c = n;
		c = ((c&1) ? (-306674912 ^ (c >>> 1)) : (c >>> 1));
		c = ((c&1) ? (-306674912 ^ (c >>> 1)) : (c >>> 1));
		c = ((c&1) ? (-306674912 ^ (c >>> 1)) : (c >>> 1));
		c = ((c&1) ? (-306674912 ^ (c >>> 1)) : (c >>> 1));
		c = ((c&1) ? (-306674912 ^ (c >>> 1)) : (c >>> 1));
		c = ((c&1) ? (-306674912 ^ (c >>> 1)) : (c >>> 1));
		c = ((c&1) ? (-306674912 ^ (c >>> 1)) : (c >>> 1));
		c = ((c&1) ? (-306674912 ^ (c >>> 1)) : (c >>> 1));
		table[n] = c;
	}

	return typeof Int32Array !== 'undefined' ? new Int32Array(table) : table;
}

var T = signed_crc_table();
function crc32_bstr(bstr, seed) {
	var C = seed ^ -1, L = bstr.length - 1;
	for(var i = 0; i < L;) {
		C = (C>>>8) ^ T[(C^bstr.charCodeAt(i++))&0xFF];
		C = (C>>>8) ^ T[(C^bstr.charCodeAt(i++))&0xFF];
	}
	if(i === L) C = (C>>>8) ^ T[(C ^ bstr.charCodeAt(i))&0xFF];
	return C ^ -1;
}

function crc32_buf(buf, seed) {
	if(buf.length > 10000) return crc32_buf_8(buf, seed);
	var C = seed ^ -1, L = buf.length - 3;
	for(var i = 0; i < L;) {
		C = (C>>>8) ^ T[(C^buf[i++])&0xFF];
		C = (C>>>8) ^ T[(C^buf[i++])&0xFF];
		C = (C>>>8) ^ T[(C^buf[i++])&0xFF];
		C = (C>>>8) ^ T[(C^buf[i++])&0xFF];
	}
	while(i < L+3) C = (C>>>8) ^ T[(C^buf[i++])&0xFF];
	return C ^ -1;
}

function crc32_buf_8(buf, seed) {
	var C = seed ^ -1, L = buf.length - 7;
	for(var i = 0; i < L;) {
		C = (C>>>8) ^ T[(C^buf[i++])&0xFF];
		C = (C>>>8) ^ T[(C^buf[i++])&0xFF];
		C = (C>>>8) ^ T[(C^buf[i++])&0xFF];
		C = (C>>>8) ^ T[(C^buf[i++])&0xFF];
		C = (C>>>8) ^ T[(C^buf[i++])&0xFF];
		C = (C>>>8) ^ T[(C^buf[i++])&0xFF];
		C = (C>>>8) ^ T[(C^buf[i++])&0xFF];
		C = (C>>>8) ^ T[(C^buf[i++])&0xFF];
	}
	while(i < L+7) C = (C>>>8) ^ T[(C^buf[i++])&0xFF];
	return C ^ -1;
}

function crc32_str(str, seed) {
	var C = seed ^ -1;
	for(var i = 0, L=str.length, c, d; i < L;) {
		c = str.charCodeAt(i++);
		if(c < 0x80) {
			C = (C>>>8) ^ T[(C ^ c)&0xFF];
		} else if(c < 0x800) {
			C = (C>>>8) ^ T[(C ^ (192|((c>>6)&31)))&0xFF];
			C = (C>>>8) ^ T[(C ^ (128|(c&63)))&0xFF];
		} else if(c >= 0xD800 && c < 0xE000) {
			c = (c&1023)+64; d = str.charCodeAt(i++)&1023;
			C = (C>>>8) ^ T[(C ^ (240|((c>>8)&7)))&0xFF];
			C = (C>>>8) ^ T[(C ^ (128|((c>>2)&63)))&0xFF];
			C = (C>>>8) ^ T[(C ^ (128|((d>>6)&15)|((c&3)<<4)))&0xFF];
			C = (C>>>8) ^ T[(C ^ (128|(d&63)))&0xFF];
		} else {
			C = (C>>>8) ^ T[(C ^ (224|((c>>12)&15)))&0xFF];
			C = (C>>>8) ^ T[(C ^ (128|((c>>6)&63)))&0xFF];
			C = (C>>>8) ^ T[(C ^ (128|(c&63)))&0xFF];
		}
	}
	return C ^ -1;
}
CRC32.table = T;
// $FlowIgnore
CRC32.bstr = crc32_bstr;
// $FlowIgnore
CRC32.buf = crc32_buf;
// $FlowIgnore
CRC32.str = crc32_str;

const OPERATIONS = {
    BUTTON_COMMAND: [0x01],
    SET_DFU_NAME: [0x02],
    CREATE_COMMAND: [0x01, 0x01],
    CREATE_DATA: [0x01, 0x02],
    RECEIPT_NOTIFICATIONS: [0x02],
    CALCULATE_CHECKSUM: [0x03],
    EXECUTE: [0x04],
    SELECT_COMMAND: [0x06, 0x01],
    SELECT_DATA: [0x06, 0x02],
    RESPONSE: [0x60, 0x20],
};

const RESPONSE = {
    // Invalid code
    0x00: 'Invalid opcode',
    // Success
    0x01: 'Operation successful',
    // Opcode not supported
    0x02: 'Opcode not supported',
    // Invalid parameter
    0x03: 'Missing or invalid parameter value',
    // Insufficient resources
    0x04: 'Not enough memory for the data object',
    // Invalid object
    0x05: 'Data object does not match the firmware and hardware requirements, the signature is wrong, or parsing the command failed',
    // Unsupported type
    0x07: 'Not a valid object type for a Create request',
    // Operation not permitted
    0x08: 'The state of the DFU process does not allow this operation',
    // Operation failed
    0x0A: 'Operation failed',
    // Extended error
    0x0B: 'Extended error',
};

const EXTENDED_ERROR = {
    // No error
    0x00: 'No extended error code has been set. This error indicates an implementation problem',
    // Invalid error code
    0x01: 'Invalid error code. This error code should never be used outside of development',
    // Wrong command format
    0x02: 'The format of the command was incorrect',
    // Unknown command
    0x03: 'The command was successfully parsed, but it is not supported or unknown',
    // Init command invalid
    0x04: 'The init command is invalid. The init packet either has an invalid update type or it is missing required fields for the update type',
    // Firmware version failure
    0x05: 'The firmware version is too low. For an application, the version must be greater than the current application. For a bootloader, it must be greater than or equal to the current version',
    // Hardware version failure
    0x06: 'The hardware version of the device does not match the required hardware version for the update',
    // Softdevice version failure
    0x07: 'The array of supported SoftDevices for the update does not contain the FWID of the current SoftDevice',
    // Signature missing
    0x08: 'The init packet does not contain a signature',
    // Wrong hash type
    0x09: 'The hash type that is specified by the init packet is not supported by the DFU bootloader',
    // Hash failed
    0x0A: 'The hash of the firmware image cannot be calculated',
    // Wrong signature type
    0x0B: 'The type of the signature is unknown or not supported by the DFU bootloader',
    // Verification failed
    0x0C: 'The hash of the received firmware image does not match the hash in the init packet',
    // Insufficient space
    0x0D: 'The available space on the device is insufficient to hold the firmware',
};

const LITTLE_ENDIAN = true;
const PACKET_SIZE = 20;

const EVENT_PROGRESS = 'progress';


// Mixin extending a BLEDevice
const DFUMixin = (BLEDevice) => {
    const DFU_SERVICE = BLEDevice.localUuid('fe59');
    const CONTROL_UUID = BLEDevice.localUuid('8ec90001-f315-4f60-9fb8-838830daea50');
    const PACKET_UUID = BLEDevice.localUuid('8ec90002-f315-4f60-9fb8-838830daea50');
    const BUTTON_UUID = BLEDevice.localUuid('8ec90003-f315-4f60-9fb8-838830daea50');

    const RECEIPT_NOTIFICATION_PACKETS = 15;

    /**
     * Emits: position, battery-status, user-button, sleep
     */
    class DFU extends BLEDevice {
        constructor(...args) {
            super(...args);
            this.type = 'dfu';
            this._transfer = {
                type: 'none',
                totalBytes: 0,
            };

            this.packetsWritten = 0;
        }

        setDfuMode() {
            return new Promise((resolve, reject) => {
                this.on('disconnect', () => resolve());
                Promise.resolve()
                    .then(() => {
                        let auxAddress = this.device.address.substr(this.device.address.length - 5).replace(':', '-');
                        this.dfuName = `DFU-${auxAddress}`;

                        let dfuNameBuffer = new ArrayBuffer(this.dfuName.length);
                        let bufView = new Uint8Array(dfuNameBuffer);
                        this.dfuName.split('').forEach((el, index) => {
                            bufView[index] = el.charCodeAt();
                        });

                        return this.sendOperation(
                            BUTTON_UUID,
                            OPERATIONS.SET_DFU_NAME.concat(this.dfuName.length),
                            dfuNameBuffer
                        );
                    })
                    .then(() => new Promise(r => setTimeout(r, 100)))
                    .then(() => {
                        // Disable the reconnect try when the board will restart to go
                        // into DFU mode.
                        this._manuallyDisconnected = true;

                        return this.sendOperation(BUTTON_UUID, OPERATIONS.BUTTON_COMMAND);
                    })
                    .catch(reject);
            });
        }

        static handleResponse(buffer) {
            return new Promise((resolve, reject) => {
                const view = new DataView(buffer);
                let error;
                if (OPERATIONS.RESPONSE.indexOf(view.getUint8(0)) < 0) {
                    throw new Error('Unrecognised control characteristic response notification');
                }
                const result = view.getUint8(2);
                if (result === 0x01) {
                    const data = new DataView(view.buffer, 3);
                    return resolve(data);
                } else if (result === 0x0B) {
                    const code = view.getUint8(3);
                    error = `Error: ${EXTENDED_ERROR[code]}`;
                } else {
                    error = `Error: ${RESPONSE[result]}`;
                }
                return reject(new Error(error));
            });
        }

        static checkCrc(buffer, crc) {
            console.log('expected', crc);
            console.log('found', CRC32.buf(new Uint8Array(buffer)));
            return crc === CRC32.buf(new Uint8Array(buffer));
        }

        transferInit(buffer) {
            return this.transfer(buffer, 'init', OPERATIONS.SELECT_COMMAND, OPERATIONS.CREATE_COMMAND);
        }

        transferFirmware(buffer) {
            return this.transfer(buffer, 'firmware', OPERATIONS.SELECT_DATA, OPERATIONS.CREATE_DATA);
        }

        transfer(buffer, type, selectType, createType) {
            return this.sendControl(selectType)
                .then((response) => {
                    const maxSize = response.getUint32(0, LITTLE_ENDIAN);
                    const offset = response.getUint32(4, LITTLE_ENDIAN);
                    const crc = response.getInt32(8, LITTLE_ENDIAN);

                    if (type === 'init' && offset === buffer.byteLength && DFU.checkCrc(buffer, crc)) {
                        return Promise.resolve();
                    }

                    this.startTransfer(type, buffer.byteLength);

                    return this.transferObject(buffer, createType, maxSize, offset);
                });
        }

        startTransfer(type, totalBytes) {
            this._transfer.type = type;
            this._transfer.totalBytes = totalBytes;
            this._transfer.currentBytes = 0;
        }

        transferObject(buffer, createType, maxSize, o) {
            let offset = o;
            const start = offset - (offset % maxSize);
            const end = Math.min(start + maxSize, buffer.byteLength);

            const view = new DataView(new ArrayBuffer(4));
            view.setUint32(0, end - start, LITTLE_ENDIAN);

            return this.sendControl(createType, view.buffer)
                .then(() => {
                    const data = buffer.slice(start, end);

                    // Reset the packets written after you send the CREATE
                    this.packetsWritten = 0;

                    return this.transferData(data, start);
                })
                .then(() => {
                    this.ignoreReceipt = true;
                    return this.sendControl(OPERATIONS.CALCULATE_CHECKSUM)
                })
                .then((response) => {
                    const crc = response.getInt32(4, LITTLE_ENDIAN);
                    const transferred = response.getUint32(0, LITTLE_ENDIAN);
                    const data = buffer.slice(0, transferred);

                    this.ignoreReceipt = false;
                    if (DFU.checkCrc(data, crc)) {
                        offset = transferred;
                        return this.sendControl(OPERATIONS.EXECUTE);
                    }

                    return Promise.resolve();
                })
                .then(() => {
                    if (end < buffer.byteLength) {
                        return this.transferObject(buffer, createType, maxSize, offset);
                    }
                    return Promise.resolve();
                });
        }

        transferData(data, offset, s) {
            const start = s || 0;
            const end = Math.min(start + PACKET_SIZE, data.byteLength);
            const packet = data.slice(start, end);

            return this.writePacket(packet)
                .then(() => {
                    this.packetsWritten += 1;

                    this.progress(offset + end);

                    if (end < data.byteLength) {
                        return Promise.resolve()
                            .then(() => {
                                if (this.packetsWritten < RECEIPT_NOTIFICATION_PACKETS) {
                                    return Promise.resolve();
                                }

                                return new Promise((resolve, reject) => {
                                    // If we already received the CRC, we're safe to continue
                                    if (this.receivedCRC) {
                                        resolve();
                                    }

                                    let waitForCRC = setInterval(() => {
                                        if (this.receivedCRC) {
                                            resolve();
                                            clearInterval(waitForCRC);
                                        }
                                    }, 5);
                                })
                                .then(() => {
                                    this.receivedCRC = false;
                                    this.packetsWritten = 0;
                                });
                            })
                            .then(() => this.transferData(data, offset, end));
                    }
                });
        }

        writePacket(packet) {
            return this.write(DFU_SERVICE, PACKET_UUID, packet, true);
        }

        sendControl(operation, buffer) {
            return this.sendOperation(CONTROL_UUID, operation, buffer);
        }

        sendOperation(cId, operation, buffer) {
            let size = operation.length;
            if (buffer) size += buffer.byteLength;

            const value = new Uint8Array(size);
            value.set(operation);
            if (buffer) {
                const data = new Uint8Array(buffer);
                value.set(data, operation.length);
            }
            return new Promise((resolve, reject) => {
                const onResponse = (response) => {
                    this.unsubscribe(DFU_SERVICE, cId, onResponse);
                    DFU.handleResponse(response.buffer)
                        .then(resolve, reject);
                };
                this.subscribe(DFU_SERVICE, cId, onResponse)
                    .then(() => this.write(DFU_SERVICE, cId, value))
                    .catch(reject);
            });
        }

        progress(n) {
            this._transfer.currentBytes = n;
            this.emit(EVENT_PROGRESS, this._transfer);
        }

        update(init, firmware) {
            if (!init) {
                throw new Error('Init not specified');
            }
            if (!firmware) {
                throw new Error('Firmware not specified');
            }
            return this.subscribe(DFU_SERVICE, CONTROL_UUID, response => {
                // The receipt notification is a CRC response.
                if (response[0] == 96 && response[1] == 3) {
                    if (!this.ignoreReceipt) {
                        this.receivedCRC = true;
                    }
                }
            })
                .then(() => {
                    return new Promise((resolve, reject) => {
                        // Enable the receipt notification
                        let value = new Uint8Array(2);
                        value[0] = RECEIPT_NOTIFICATION_PACKETS;

                        this.sendControl(OPERATIONS.RECEIPT_NOTIFICATIONS, value)
                            .then(resolve);
                    })
                })
                .then(() => this.transferInit(init))
                .then(() => this.transferFirmware(firmware));
        }
    }

    return DFU;
};

class Logger {
    trace() {}
    debug() {}
    info(...args) {
        console.log(...args);
    }
    warn(...args) {
        console.log(...args);
    }
    error(...args) {
        console.log(...args);
    }
    log(...args) {
        console.log(...args);
    }
}

const WAND_PREFIX = 'Kano-Wand';

const WAND_ID = 'wand';

class Devices extends events.EventEmitter {
    constructor(opts) {
        super();
        // If no bluetooth configuration is provided, disable bluetooth devices
        if (!opts.bluetooth) {
            this.bluetoothDisabled = true;
        } else {
            if (!opts.bluetooth.watcher) {
                throw new Error('A bluetooth watcher must be provided');
            }
            if (!opts.bluetooth.deviceMixin) {
                throw new Error('A bluetooth device mixin must be provided');
            }
            this.dfuSupported = Boolean(opts.bluetooth.extractor);
            this.extractor = opts.bluetooth.extractor;
        }
        this.devices = new Map();
        if (!this.bluetoothDisabled) {
            this.watcher = opts.bluetooth.watcher;
            this.BLEDeviceMixin = opts.bluetooth.deviceMixin;
            // Bluetooth devices
            this.BLEDevice = this.BLEDeviceMixin(Device);
            this.Wand = WandMixin(this.BLEDevice);
            this.DFU = DFUMixin(this.BLEDevice);
        }

        this.deviceIDTestFunction = {};
        this.deviceIDTestFunction[WAND_ID] = this.wandTestFunction.bind(this);

        this.deviceIDClass = {};
        this.deviceIDClass[WAND_ID] = this.Wand;

        this.setLogger(new Logger());
        // Add here future devices
    }
    setLogger(logger) {
        this.log = logger;
        this.watcher.setLogger(logger);
    }
    wandTestFunction(devicePrefix = null) {
        devicePrefix = devicePrefix || this.wandPrefix || WAND_PREFIX;

        return (peripheral) => {
            const device = new this.BLEDevice(peripheral, this, true);
            const deviceData = device.toJSON();
            const bluetoothInfo = deviceData.bluetooth;
            // Never set internally, the wandPrefix property can help debugging a specific device
            return bluetoothInfo.name && bluetoothInfo.name.startsWith(devicePrefix);
        };
    }
    searchForClosestDevice(deviceID, timeout) {
        if (this.bluetoothDisabled) {
            return Promise.resolve();
        }

        if (!(deviceID in this.deviceIDTestFunction)) {
            return Promise.reject(new Error('Unrecognised deviceID'));
        }

        this.log.info(`Starting searchForClosestDevice with type ${deviceID}. Will stop after ${timeout}ms...`);

        return this.watcher.searchForClosestDevice(this.deviceIDTestFunction[deviceID](), timeout)
            .then((ble) => {
                let newDeviceClass = this.deviceIDClass[deviceID];
                let newDevice = new newDeviceClass(ble, this);
                this.addDevice(newDevice);
                return Promise.resolve(newDevice);
            });
    }
    getDeviceID(deviceName) {
        if (deviceName && deviceName.startsWith(WAND_PREFIX)) {
            return WAND_ID;
        }
        // Add more devices here
        return false;
    }
    searchForDevice(devicePrefix, timeout) {
        if (this.bluetoothDisabled) {
            return Promise.resolve();
        }

        let deviceID = this.getDeviceID(devicePrefix);
        if (!(deviceID in this.deviceIDTestFunction)) {
            return Promise.reject(new Error('Unrecognised device.'));
        }

        this.log.info(`Starting searchForClosestDevice with prefix ${devicePrefix}. Will stop after ${timeout}ms...`);

        return this.watcher.searchForDevice(this.deviceIDTestFunction[deviceID](devicePrefix), timeout)
            .then((ble) => {
                let newDeviceClass = this.deviceIDClass[deviceID];
                let newDevice = new newDeviceClass(ble, this);
                this.addDevice(newDevice);
                return Promise.resolve(newDevice);
            });
    }
    stopBluetoothScan() {
        if (this.bluetoothDisabled) {
            return Promise.resolve();
        }
        // Stop the scan
        return this.watcher.stopScan();
    }
    searchForDfuDevice(name) {
        if (this.bluetoothDisabled) {
            return Promise.resolve();
        }
        return this.watcher.searchForDevice((peripheral) => {
            const device = new this.BLEDevice(peripheral, this, true);
            const deviceData = device.toJSON();
            return deviceData.bluetooth.name === name;
        }).then(ble => new this.DFU(ble, this));
    }
    updateDFUDevice(device, buffer) {
        if (!this.dfuSupported) {
            throw new Error('Cannot update DFU device. Missing extractor');
        }
        const dfuDevice = this.createDFUDevice(device);
        const pck = new Package(this.extractor, buffer);
        this.log.trace('Loading update package...');
        return pck.load()
            .then(() => {
                this.log.trace('Update package loaded');
                this.log.trace('Enabling DFU mode...');
                // Flag as manually disconnected to prevent auto reconnect
                device._manuallyDisconnected = true;
                dfuDevice._manuallyDisconnected = true;
                return dfuDevice.setDfuMode();
            })
            .then(() => {
                this.log.trace('DFU mode enabled');
                return dfuDevice.dispose()
                    .catch((e) => {
                        this.log.error('Unable to close the dfuDevice...', e);
                    });
            })
            .then(() => {
                this.log.trace('Searching for DFU device...');
                return this.searchForDfuDevice(dfuDevice.dfuName);
            })
            .then((dfuTarget) => {
                this.log.trace('DFU found');
                this.log.trace('Starting update');
                dfuTarget.on('progress', (transfer) => {
                    device.emit('update-progress', transfer);
                });
                return pck.getAppImage()
                    .then(image => dfuTarget.update(image.initData, image.imageData))
                    .then(() => {
                        this.log.trace('Update finished, disconnecting...');
                    })
                    .then(() => dfuTarget.dispose());
            })
            .then(() => {
                this.log.trace('Reconnecting to device');
                return device.reconnect();
            });

    }
    addDevice(device) {
        this.log.info(`Adding/Updating device ${device.id}`);
        this.devices.set(device.id, device);
        this.emit('new-device', device);
    }
    createDFUDevice(device) {
        return new this.DFU(device.device, this);
    }
    getById(id) {
        return this.devices.get(id);
    }
    getAll() {
        return Array.from(this.devices.values());
    }
    removeDevice(device) {
        // Returns true if the devices was removed or false if
        // the device id was not found in the devices array.
        return Promise.resolve(this.devices.delete(device.id));
    }
    terminate() {
        this.setLogger(new Logger());
        const terminations = [];
        this.devices.forEach((value) => {
            terminations.push(value.terminate());
        });
        return Promise.all(terminations);
    }
}

class SubscriptionsManager {
    constructor(opts = {}) {
        this.options = Object.assign({}, {
            subscribe() { return Promise.resolve(); },
            unsubscribe() { return Promise.resolve(); },
        }, opts);
        this.subscriptions = new Map();
        this.subscriptionsCallbacks = {};
    }

    static getSubscriptionKey(sId, cId) {
        return `${sId}:${cId}`;
    }

    clear() {
        this.subscriptions = new Map();
    }

    flagAsUnsubscribe() {
        this.subscriptions.forEach((sub) => {
            sub.subscribed = false;
        });
    }

    resubscribe() {
        this.subscriptions.forEach((entry) => {
            this.maybeSubscribe(entry.sId, entry.cId);
        });
    }

    subscribe(sId, cId, onValue) {
        const key = SubscriptionsManager.getSubscriptionKey(sId, cId);
        if (!this.subscriptions.has(key)) {
            this.subscriptions.set(key, {
                subscribed: false,
                callbacks: [],
                sId,
                cId,
            });
        }
        const subscriptions = this.subscriptions.get(key);
        subscriptions.callbacks.push(onValue);
        return this.maybeSubscribe(sId, cId);
    }
    maybeSubscribe(sId, cId) {
        const key = SubscriptionsManager.getSubscriptionKey(sId, cId);
        const subscriptions = this.subscriptions.get(key);
        if (!subscriptions.subscribed) {
            subscriptions.subscribed = true;
            this.subscriptionsCallbacks[key] = (value) => {
                value = new Uint8Array(value);
                subscriptions.callbacks.forEach(callback => callback(value));
            };
            return this._subscribe(sId, cId, this.subscriptionsCallbacks[key]);
        }
        return Promise.resolve();
    }
    unsubscribe(sId, cId, onValue) {
        const key = SubscriptionsManager.getSubscriptionKey(sId, cId);        if (!this.subscriptions.has(key)) {
            return Promise.resolve();
        }
        const subscriptions = this.subscriptions.get(key);
        const index = subscriptions.callbacks.indexOf(onValue);
        subscriptions.callbacks.splice(index, 1);
        return this.maybeUnsubscribe(sId, cId);
    }
    maybeUnsubscribe(sId, cId) {
        const key = SubscriptionsManager.getSubscriptionKey(sId, cId);
        const subscription = this.subscriptions.get(key);

        if (subscription.subscribed && subscription.callbacks.length <= 0) {
            subscription.subscribed = false;
            this._unsubscribe(sId, cId, this.subscriptionsCallbacks[key]);
        }
        return Promise.resolve();
    }
    _subscribe(sId, cId, callback) {
        return this.options.subscribe(sId, cId, callback);
    }
    _unsubscribe(sId, cId, callback) {
        return this.options.unsubscribe(sId, cId, callback);
    }
}

exports.default = Devices;
exports.Package = Package;
exports.Devices = Devices;
exports.SubscriptionsManager = SubscriptionsManager;
