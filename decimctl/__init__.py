"""
Module for interfacing with Decimator Design products.

Modified by the decimator-net project for status snapshots and converter controls.

Copyright 2019 Quentin Smith <quentin@mit.edu>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import datetime
from struct import pack
from itertools import chain
from functools import reduce
from ctypes import byref, sizeof, cast, c_char_p, c_void_p, pointer, POINTER, Structure, create_string_buffer
import pylibftdi.driver
import pylibftdi.device
from enum import Flag

from . import protocol

VID = 0x215f
PID = 0x6000

# TODO: Push a patch upstream to allow pylibftdi to accept the VID/PID at runtime.
pylibftdi.driver.USB_VID_LIST = [VID]
pylibftdi.driver.USB_PID_LIST = [PID]
pylibftdi.device.USB_VID_LIST = pylibftdi.driver.USB_VID_LIST
pylibftdi.device.USB_PID_LIST = pylibftdi.driver.USB_PID_LIST
pylibftdi.device.ERR_HELP_NOT_FOUND_FAIL = """
No device could be found. Is the device connected?

Try running the following command to see if the device is listed:

    decimctl list
"""

def now():
    return datetime.datetime.now().isoformat()

def list_devices():
    return pylibftdi.driver.Driver().list_devices()

class ftdi_context(Structure):
    _fields_ = [
        ('usb_ctx', c_void_p),
        ('usb_dev', c_void_p),
    ]

# N.B. enum.auto does not allow combining with int
def auto(state=[1]):
    out = state[0]
    state[0] = out<<1
    return out

class DeviceType(Flag):
    DHA = auto()
    DUC = auto()
    CPA = auto()
    CPA_HX = CPA | auto()
    CPA_HX_V1 = CPA_HX | auto()
    CPA_HX_V2 = CPA_HX | auto()
    CPA_CROSS = CPA | auto()
    CPA_CROSS_V1 = CPA_CROSS | auto()
    CPA_CROSS_V2 = CPA_CROSS | auto()
    CPA_CROSS_V3 = CPA_CROSS | auto()
    CPA_LX = CPA | auto()
    MQS = auto()
    MQA = auto()
    VFA = auto()
    KPA = auto()
    SECTOR_4K = auto()
    SECTOR_64K = auto()
    SECTOR_256K = auto()
    # SECTOR_4K if ??B, SECTOR_64K if ??A
    VFA_VFA = VFA | auto() # 0x6 windows
    VFA_VLA = VFA | auto() # 0xc windows
    VFA_MPA = VFA | auto() # 0x10 windows
    VFA_VPA = VFA | auto() # 0x10 windows
    # SECTOR_4K if MDB, SECTOR_256K if MDA
    VFA_MDA = VFA | auto() # 0x4 windows

    VFA_MQC = VFA | SECTOR_64K | auto() # 0x4 windows
    VFA_MQD = VFA | SECTOR_4K | auto() # 0x4 windows, DMON-QUAD
    VFA_VHA = VFA | SECTOR_4K | auto() # 0x4 windows
    VFA_OAA = VFA | SECTOR_4K | auto() # 0x9 windows
    VFA_OBA = VFA | SECTOR_4K | auto() # 0x4 windows


_SERIAL_PREFIX_TO_TYPE = {
    b'DHA': DeviceType.DHA,
    b'DHB': DeviceType.DHA,
    b'DUC': DeviceType.DUC,
    b'CLA': DeviceType.CPA_HX_V1,
    b'LLA': DeviceType.CPA_HX_V1,
    b'CLB': DeviceType.CPA_HX_V1,
    b'LLB': DeviceType.CPA_HX_V1,
    b'CLC': DeviceType.CPA_HX_V1,
    b'LLC': DeviceType.CPA_HX_V1,
    b'CLD': DeviceType.CPA_HX_V2,
    b'LLD': DeviceType.CPA_HX_V2,
    b'CPA': DeviceType.CPA_CROSS_V1,
    b'LPA': DeviceType.CPA_CROSS_V1,
    b'CPB': DeviceType.CPA_CROSS_V2,
    b'LPB': DeviceType.CPA_CROSS_V2,
    b'CPC': DeviceType.CPA_CROSS_V2,
    b'LPC': DeviceType.CPA_CROSS_V2,
    # Nothing for CPA_CROSS_V3 yet?
    b'CXA': DeviceType.CPA_LX,
    b'LXA': DeviceType.CPA_LX,
    b'CXB': DeviceType.CPA_LX,
    b'LXB': DeviceType.CPA_LX,
    b'MQS': DeviceType.MQS,
    b'MQA': DeviceType.MQA,
    b'MQB': DeviceType.MQA,
    b'MQC': DeviceType.VFA_MQC,
    b'MQD': DeviceType.VFA_MQD, # DMON-QUAD
    b'MDA': DeviceType.VFA_MDA | DeviceType.SECTOR_256K,
    b'MDB': DeviceType.VFA_MDA | DeviceType.SECTOR_4K,
    b'MPA': DeviceType.VFA_MPA | DeviceType.SECTOR_64K,
    b'MPB': DeviceType.VFA_MPA | DeviceType.SECTOR_4K,
    b'VFA': DeviceType.VFA_VFA | DeviceType.SECTOR_64K,
    b'VFB': DeviceType.VFA_VFA | DeviceType.SECTOR_4K,
    b'VLA': DeviceType.VFA_VLA | DeviceType.SECTOR_64K,
    b'VLB': DeviceType.VFA_VLA | DeviceType.SECTOR_4K,
    b'VPA': DeviceType.VFA_VPA | DeviceType.SECTOR_64K,
    b'VPB': DeviceType.VFA_VPA | DeviceType.SECTOR_4K,
    b'OAA': DeviceType.VFA_OAA,
    b'OBA': DeviceType.VFA_OBA,
    b'KPA': DeviceType.KPA,
}

def status_snapshot(device, registers=None):
    """Return a decoded, read-only status snapshot from one register read.

    Output settings are configured values, not proof of the active signal path.
    """
    reg = device.registers if registers is None else registers
    snapshot = {
        "model": device.desc.decode('ascii', errors='replace'),
        "serial": device.serial.decode('ascii', errors='replace'),
        "device_type": str(device.device_type),
        "firmware_version": "%d.%d" % (reg.version_major, reg.version_minor),
        "inputs": {},
    }
    for number in (1, 2, 3):
        value = getattr(reg, "Input%dStatus" % number, None)
        if value is not None:
            snapshot["inputs"][str(number)] = value
    if hasattr(reg, "OutputFormat"):
        snapshot["configured_scaler_output_format"] = reg.OutputFormat
    if hasattr(reg, "OutputMode"):
        snapshot["output_mode"] = reg.OutputMode
    if device.device_type == DeviceType.CPA_HX_V2:
        snapshot["configured_routing"] = {
            "sdi_output_source": reg.SO_Source.name,
            "hdmi_output_source": reg.HO_Source.name,
            "scaler_source": reg.DUC_Source.name,
        }
    return snapshot

class Device(pylibftdi.device.Device):
    def __init__(self, log_raw_data=False, serial=None):
        self.log_file = None
        if log_raw_data:
            self.log_file = open("%s.raw" % now(), 'wb')
        self._requested_serial = serial
        self._serial = create_string_buffer(128)
        self._desc = create_string_buffer(128)
        self.custom_name = None

        super(Device, self).__init__(mode='b')

    def _open_device(self):
        serial = None
        if self._requested_serial:
            serial = c_char_p(self._requested_serial.encode('ascii'))
        return self.fdll.ftdi_usb_open_desc_index(byref(self.ctx), VID, PID, None, serial, 0)

    def _get_info(self):
        self.fdll.ftdi_usb_get_strings2.argtypes = self.fdll.ftdi_usb_get_strings.argtypes
        usb_dev_handle = cast(pointer(self.ctx), POINTER(ftdi_context)).contents.usb_dev
        self.fdll.libusb_get_device.argtypes = (c_void_p,)
        self.fdll.libusb_get_device.restype = c_void_p
        usb_dev = self.fdll.libusb_get_device(usb_dev_handle)
        self.ftdi_fn.ftdi_usb_get_strings2(usb_dev, None, 0, self._desc, 127, self._serial, 127)

        eeprom = create_string_buffer(128)
        self.ftdi_fn.ftdi_read_eeprom()
        self.ftdi_fn.ftdi_get_eeprom_buf(byref(eeprom), len(eeprom))
        self.custom_name = create_string_buffer(eeprom[92:92+16]).value

    def open(self):
        if self._opened:
            return
        super(Device, self).open()

        self._get_info()

        # FT_ResetDevice()
        self.ftdi_fn.ftdi_usb_reset()
        # FT_SetBaudRate(3000000)
        self.baudrate = 3000000
        # FT_SetUSBParameters(65535, 65535)
        self.ftdi_fn.ftdi_read_data_set_chunksize(65535)
        # FT_SetChars(0, 0, 0, 0)
        self.ftdi_fn.ftdi_set_error_char(0, 0)
        self.ftdi_fn.ftdi_set_event_char(0, 0)
        # FT_SetTimeouts(0, 5000) - readTimeout, writeTimeout
        # FT_SetLatencyTimer(1)
        self.ftdi_fn.ftdi_set_latency_timer(1)
        # FT_SetFlowControl(256, 0, 0)
        SIO_RTS_CTS_HS = 0x100
        self.ftdi_fn.ftdi_setflowctrl(SIO_RTS_CTS_HS)
        # FT_SetBitMode(0, 0)
        self.ftdi_fn.ftdi_set_bitmode(0, 0)
        # FT_SetBitMode(0, 4)
        self.ftdi_fn.ftdi_set_bitmode(0, 4)
        # FT_Write("H")
        # + Block until FT_GetStatus returns 1
        self.clock_raw_bytes(b'\x48')
        # FT_SetBitMode(72, 4)
        # This sets the FPGA clock and data pins to be outputs (in to the FPGA).
        self.ftdi_fn.ftdi_set_bitmode(0x48, 4)

    def close(self):
        # FT_SetBitMode(0, 0)
        self.ftdi_fn.ftdi_set_bitmode(0, 0)
        # FT_Close()
        super(Device, self).close()

    @property
    def serial(self):
        return self._serial.value

    @property
    def desc(self):
        return self._desc.value

    # Number of bytes to write/read at a time. If its buffer
    # overflows, the FTDI chip will block on writes.
    CHUNK_SIZE = 256
    
    def clock_raw_bytes(self, data_in):
        """Clock in raw bytes and return the corresponding output.

        Args:
          data_in: bytes
        Returns:
          data_out: bytes
        """
        out = bytes()
        for i in range(0, len(data_in), self.CHUNK_SIZE):
            to_send = data_in[i:i+self.CHUNK_SIZE]
            self.write(to_send)
            out += self.read(len(to_send))
        if self.log_file:
            self.log_file.write(bytes(bytearray(chain.from_iterable(zip(data_in, out)))))
        return out

    def fpga_write_bytes(self, register, value):
        # @TUSB@FPGA_WRITE_BYTES$q ui puc ui ui
        # CPA_SO_Source calls @TUSB@FPGA_WRITE_BYTES(0, &value, 0x31, 0x1) where value is 0->3

        buf = bytearray(protocol.WRITE_PREAMBLE)

        address = (register<<1) & 0xfffe

        buf.extend(protocol.bytes_to_raw_command(pack(">H", address)))

        buf.extend(protocol.bytes_to_raw_command(value))

        buf.extend(protocol.WRITE_POSTAMBLE)

        return self.clock_raw_bytes(bytes(buf))

    def fpga_read_bytes(self, start, length):
        # @TUSB@FPGA_READ_BYTES$q ui puc ui ui o
        # UpdateControls calls @TUSB@FPGA_READ_BYTES(device, &rx_reg, 0, 0x200, True)
        buf = bytearray(protocol.READ_PREAMBLE)

        address = (start<<1) | 1

        buf.extend(protocol.bytes_to_raw_command(pack(">H", address)))

        self.clock_raw_bytes(bytes(buf))

        # FT_Purge(3)
        self.flush()
        # FT_SetBitMode(64, 4)
        self.ftdi_fn.ftdi_set_bitmode(0x40, 4)


        # Toggle the clock line once for each bit.
        buf = b'\x00\x40\x40\x00'*(length<<3)
        data = protocol.raw_response_to_bytes(self.clock_raw_bytes(buf))

        # FT_Write([0])
        # + Block until FT_GetStatus() = 1
        self.clock_raw_bytes(b'\0')
        # FT_SetBitMode(72, 4)
        self.ftdi_fn.ftdi_set_bitmode(0x48, 4)
        # FT_Write(00 40 48)
        # + Block until FT_GetStatus() = 3
        self.clock_raw_bytes(b'\x00\x40\x48')
        return data

    @property
    def raw_registers(self):
        return self.fpga_read_bytes(0, 0x200)

    def _registers(self, type):
        ret = type.from_buffer_copy(self.raw_registers)
        ret._device = self
        return ret

    @property
    def CPA(self):
        if self.device_type == DeviceType.CPA_HX_V2:
            return self._registers(protocol.CPA_HX_V2_Registers)
        if self.device_type == DeviceType.CPA_LX:
            return self._registers(protocol.CPA_LX_Registers)
        return self._registers(protocol.CPA_Registers)

    def set_hx_v2_hdmi_output_source(self, source):
        """Set the MD-HX V2 HDMI output route (0=SDI, 1=HDMI, 2=scaler)."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('HDMI output routing requires an MD-HX V2')
        if type(source) is not int or source not in (0, 1, 2):
            raise ValueError('invalid HDMI output source')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        registers.HO_Source = source
        actual = int(self.CPA.HO_Source)
        if actual != source:
            raise RuntimeError('HDMI output source did not retain the requested value')
        return protocol.SO_Source(actual)

    def set_hx_v2_sdi_output_source(self, source):
        """Set the MD-HX V2 SDI output route (0=SDI, 1=HDMI, 2=scaler)."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('SDI output routing requires an MD-HX V2')
        if type(source) is not int or source not in (0, 1, 2):
            raise ValueError('invalid SDI output source')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        registers.SO_Source = source
        actual = int(self.CPA.SO_Source)
        if actual != source:
            raise RuntimeError('SDI output source did not retain the requested value')
        return protocol.SO_Source(actual)

    def set_hx_v2_audio_pair(self, output, pair, source):
        """Set one MD-HX V2 output audio-pair source (HDMI 1-4, SDI 1-8)."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('audio-pair routing requires an MD-HX V2')
        if output not in ('hdmi', 'sdi'):
            raise ValueError('invalid audio-pair output')
        pair_count = 4 if output == 'hdmi' else 8
        if type(pair) is not int or pair not in range(1, pair_count + 1):
            raise ValueError('invalid audio-pair number')
        if type(source) is not int or source not in range(9):
            raise ValueError('invalid audio-pair source')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        field = f'{output.upper()}_Pair{pair}'
        setattr(registers, field, source)
        actual = int(getattr(self.CPA, field))
        if actual != source:
            raise RuntimeError('audio-pair source did not retain the requested value')
        return protocol.AudioPair(actual)

    def set_hx_v2_no_signal_color(self, field, code):
        """Set a No Signal overlay colour using the MD-HX V2 manual's order."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('No Signal overlay colours require an MD-HX V2')
        fields = {
            'foreground': 'NoSignalForeground',
            'background': 'NoSignalBackground',
        }
        if field not in fields:
            raise ValueError('invalid No Signal overlay colour field')
        if type(code) is not int or code not in range(len(protocol.CPA_HX_V2_NO_SIGNAL_COLORS)):
            raise ValueError('invalid No Signal overlay colour')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        register_field = fields[field]
        offset = getattr(protocol.CPA_HX_V2_Registers, register_field).offset
        value = (bytes(registers)[offset] & ~7) | code
        self.fpga_write_bytes(offset, bytes((value,)))
        actual = bytes(self.CPA)[offset] & 7
        if actual != code:
            raise RuntimeError('No Signal overlay colour did not retain the requested value')
        return actual

    def set_hx_v2_output_3g_b(self, level):
        """Select 3G-SDI Level A (0) or B (1), preserving register 0x2c."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('3G-SDI output level requires an MD-HX V2')
        if type(level) is not int or level not in (0, 1):
            raise ValueError('invalid 3G-SDI output level')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        registers.OUT_3G_B = (int(registers.OUT_3G_B) & ~1) | level
        actual = int(self.CPA.OUT_3G_B) & 1
        if actual != level:
            raise RuntimeError('3G-SDI output level did not retain the requested value')
        return actual

    def set_hx_v2_output_1_loop(self, enabled):
        """Set Output 1 loop-through at register 0x2b bit 0."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('Output 1 loop requires an MD-HX V2')
        if type(enabled) is not int or enabled not in (0, 1):
            raise ValueError('invalid Output 1 loop setting')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        registers.Loop_Enable = (int(registers.Loop_Enable) & ~1) | enabled
        actual = int(self.CPA.Loop_Enable) & 1
        if actual != enabled:
            raise RuntimeError('Output 1 loop did not retain the requested value')
        return actual

    def set_hx_v2_hdmi_output_type(self, code):
        """Select MD-HX V2 HDMI/DVI output encoding at register 0x30."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('HDMI output type requires an MD-HX V2')
        if type(code) is not int or code not in range(7):
            raise ValueError('invalid HDMI output type')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_Registers.HO_Type.offset
        registers.HO_Type = (bytes(registers)[offset] & ~7) | code
        actual = bytes(self.CPA)[offset] & 7
        if actual != code:
            raise RuntimeError('HDMI output type did not retain the requested value')
        return protocol.HO_Type(actual)

    def set_hx_v2_1080i_as_psf(self, enabled):
        """Interpret 1080i input as 1080psf (register 0x20 bit 0)."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('1080i/PSF setting requires an MD-HX V2')
        if type(enabled) is not int or enabled not in (0, 1):
            raise ValueError('invalid 1080i/PSF setting')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        registers.PSFINEnable = (int(registers.PSFINEnable) & ~1) | enabled
        actual = int(self.CPA.PSFINEnable) & 1
        if actual != enabled:
            raise RuntimeError('1080i/PSF setting did not retain the requested value')
        return actual

    def set_hx_v2_flip(self, axis, enabled):
        """Set horizontal or vertical scaler image flip at register 0x2d."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('image flip requires an MD-HX V2')
        if axis not in ('horizontal', 'vertical'):
            raise ValueError('invalid image flip axis')
        if type(enabled) is not int or enabled not in (0, 1):
            raise ValueError('invalid image flip setting')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        field = 'DUC_H_FLIP_EN' if axis == 'horizontal' else 'DUC_V_FLIP_EN'
        setattr(registers, field, enabled)
        actual = int(getattr(self.CPA, field))
        if actual != enabled:
            raise RuntimeError('image flip did not retain the requested value')
        return actual

    def set_hx_v2_scaler_output_format(self, code):
        """Set an MD-HX V2 scaler format by its menu code."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('scaler output format requires an MD-HX V2')
        if type(code) is not int or code not in range(len(protocol.CPA_HX_V2_OUTPUT_FORMATS)):
            raise ValueError('invalid MD-HX V2 scaler output format')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        registers.DUCFormat = (int(registers.DUCFormat) & ~0x3f) | code
        actual = int(self.CPA.DUCFormat) & 0x3f
        if actual != code:
            raise RuntimeError('scaler output format did not retain the requested value')
        return protocol.CPA_HX_V2_OUTPUT_FORMATS[actual]

    def set_hx_v2_scaler_source(self, source):
        """Set the MD-HX V2 scaler input (0=SDI, 1=HDMI)."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('scaler source requires an MD-HX V2')
        if type(source) is not int or source not in (0, 1):
            raise ValueError('invalid MD-HX V2 scaler source')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        registers.DUC_Source = source
        actual = int(self.CPA.DUC_Source)
        if actual != source:
            raise RuntimeError('scaler source did not retain the requested value')
        return protocol.DUC_Source(actual)

    def set_hx_v2_scaler_reference(self, reference):
        """Set scaler reference in register 0x33 bits 1–2, preserving neighbors."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('scaler reference requires an MD-HX V2')
        if type(reference) is not int or reference not in (0, 1, 2, 3):
            raise ValueError('invalid MD-HX V2 scaler reference')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_Registers.DUC_Ref.offset
        value = (bytes(registers)[offset] & ~0x06) | (reference << 1)
        self.fpga_write_bytes(offset, bytes((value,)))
        actual = (bytes(self.CPA)[offset] >> 1) & 3
        if actual != reference:
            raise RuntimeError('scaler reference did not retain the requested value')
        return protocol.DUC_Ref(actual)

    def set_hx_v2_horizontal_filter(self, code):
        """Set the HX V2 pre-scaler horizontal filter at register 0x2a."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('horizontal filter requires an MD-HX V2')
        options = tuple(protocol.DUC_HF)
        if type(code) is not int or code not in range(5):
            raise ValueError('invalid horizontal filter setting')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_Registers.DUC_HF.offset
        value = (bytes(registers)[offset] & ~0x07) | code
        self.fpga_write_bytes(offset, bytes((value,)))
        actual = bytes(self.CPA)[offset] & 0x07
        if actual != code:
            raise RuntimeError('horizontal filter did not retain the requested value')
        return protocol.DUC_HF(actual)

    def set_hx_v2_motion_detect_level(self, level):
        """Set the HX V2 motion threshold at register 0x27, preserving upper bits."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('motion detect level requires an MD-HX V2')
        if type(level) is not int or level not in range(1024):
            raise ValueError('motion detect level must be between 0 and 1023')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_Registers.DUC_TH1.offset
        current = int.from_bytes(bytes(registers)[offset:offset + 2], 'big')
        value = (current & ~0x03ff) | level
        self.fpga_write_bytes(offset, value.to_bytes(2, 'big'))
        actual = int.from_bytes(bytes(self.CPA)[offset:offset + 2], 'big') & 0x03ff
        if actual != level:
            raise RuntimeError('motion detect level did not retain the requested value')
        return actual


    def set_hx_v2_tpg_enabled(self, enabled):
        """Set the HX V2 test pattern generator at register 0x80 bit 0."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('test pattern generator requires an MD-HX V2')
        if type(enabled) is not int or enabled not in (0, 1):
            raise ValueError('invalid test pattern generator setting')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        value = (bytes(registers)[0x80] & ~1) | enabled
        self.fpga_write_bytes(0x80, bytes((value,)))
        actual = bytes(self.CPA)[0x80] & 1
        if actual != enabled:
            raise RuntimeError('test pattern generator did not retain the requested setting')
        return actual

    def set_hx_v2_tpg_pattern(self, code):
        """Select a manual-listed HX V2 test pattern at register 0x81."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('test pattern requires an MD-HX V2')
        if type(code) is not int or code not in range(len(protocol.CPA_HX_V2_TPG_PATTERNS)):
            raise ValueError('invalid test pattern code')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        value = (bytes(registers)[0x81] & ~0x3f) | code
        self.fpga_write_bytes(0x81, bytes((value,)))
        actual = bytes(self.CPA)[0x81] & 0x3f
        if actual != code:
            raise RuntimeError('test pattern did not retain the requested code')
        return protocol.CPA_HX_V2_TPG_PATTERNS[actual]

    def set_hx_v2_overlay_target(self, target):
        """Route HX V2 overlays with register 0x34 low two bits."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('overlay routing requires an MD-HX V2')
        if type(target) is not int or target not in (0, 1, 2, 3):
            raise ValueError('invalid overlay target')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        value = (bytes(registers)[0x34] & ~3) | target
        self.fpga_write_bytes(0x34, bytes((value,)))
        actual = bytes(self.CPA)[0x34] & 3
        if actual != target:
            raise RuntimeError('overlay target did not retain the requested value')
        return actual

    def set_hx_v2_umd_enabled(self, enabled):
        """Enable/disable the HX V2 UMD text overlay at register 0x45 bit 0."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('UMD overlay control requires an MD-HX V2')
        if type(enabled) is not int or enabled not in (0, 1):
            raise ValueError('invalid UMD overlay setting')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_Registers.UMDEnable.offset
        value = (bytes(registers)[offset] & ~1) | enabled
        self.fpga_write_bytes(offset, bytes((value,)))
        actual = bytes(self.CPA)[offset] & 1
        if actual != enabled:
            raise RuntimeError('UMD overlay setting did not retain the requested value')
        return actual

    def _set_hx_v2_umd_palette(self, field, code, options, raw_codes=None):
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('UMD palette control requires an MD-HX V2')
        if type(code) is not int or code not in range(len(options)):
            raise ValueError('invalid UMD palette code')
        raw_code = code if raw_codes is None else raw_codes[code]
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = getattr(protocol.CPA_HX_V2_Registers, field).offset
        value = (bytes(registers)[offset] & ~0x1f) | raw_code
        self.fpga_write_bytes(offset, bytes((value,)))
        actual = bytes(self.CPA)[offset] & 0x1f
        if actual != raw_code:
            raise RuntimeError(f'{field} did not retain the requested palette code')
        return options[code]

    def set_hx_v2_umd_foreground(self, code):
        """Set HX V2 UMD foreground using the palette code at register 0x46."""
        return self._set_hx_v2_umd_palette(
            'UMDForeground', code, protocol.CPA_HX_V2_UMD_FOREGROUNDS)

    def set_hx_v2_umd_background(self, code):
        """Set HX V2 UMD background by menu choice at register 0x47."""
        return self._set_hx_v2_umd_palette(
            'UMDBackground', code, protocol.CPA_HX_V2_UMD_BACKGROUNDS,
            protocol.CPA_HX_V2_UMD_BACKGROUND_MENU_TO_RAW)

    def set_hx_v2_umd_text(self, text):
        """Set up to 16 printable ASCII characters in the HX V2 UMD field.

        The device stores a fixed 16-byte field. Short strings are padded with
        trailing spaces, matching the behavior verified on an MD-HX V2.
        """
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('UMD text requires an MD-HX V2')
        if not isinstance(text, str) or len(text) > 16:
            raise ValueError('UMD text must contain at most 16 characters')
        try:
            encoded = text.ljust(16).encode('ascii')
        except UnicodeEncodeError as exc:
            raise ValueError('UMD text must use printable ASCII characters') from exc
        if any(code < 0x20 or code > 0x7e for code in encoded):
            raise ValueError('UMD text must use printable ASCII characters')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        self.fpga_write_bytes(0xc0, encoded)
        actual = bytes(self.CPA)[0xc0:0xd0]
        if actual != encoded:
            raise RuntimeError('UMD text did not retain the requested value')
        return actual.decode('ascii').rstrip(' ')

    def set_hx_v2_input_format_overlay(self, code):
        """Set the input-format status overlay at register 0x40 low 2 bits."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('input-format overlay requires an MD-HX V2')
        options = protocol.CPA_HX_V2_INPUT_FORMAT_OVERLAY_OPTIONS
        if type(code) is not int or code not in range(len(options)):
            raise ValueError('invalid input-format overlay setting')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_Registers.OSINFormatEnable.offset
        value = (bytes(registers)[offset] & ~3) | code
        self.fpga_write_bytes(offset, bytes((value,)))
        actual = bytes(self.CPA)[offset] & 3
        if actual != code:
            raise RuntimeError('input-format overlay did not retain the requested setting')
        return options[actual]

    def _set_hx_v2_input_format_palette(self, field, code, raw_codes=None):
        """Set an input-format overlay palette field at registers 0x41/0x42."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('input-format palette control requires an MD-HX V2')
        options = (protocol.CPA_HX_V2_UMD_BACKGROUNDS if raw_codes is not None
                   else protocol.CPA_HX_V2_UMD_FOREGROUNDS)
        if type(code) is not int or code not in range(len(options)):
            raise ValueError('invalid input-format palette code')
        raw_code = code if raw_codes is None else raw_codes[code]
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = getattr(protocol.CPA_HX_V2_Registers, field).offset
        value = (bytes(registers)[offset] & ~0x1f) | raw_code
        self.fpga_write_bytes(offset, bytes((value,)))
        actual = bytes(self.CPA)[offset] & 0x1f
        if actual != raw_code:
            raise RuntimeError(f'{field} did not retain the requested palette code')
        return options[code]

    def set_hx_v2_input_format_foreground(self, code):
        """Set MD-HX input-format text foreground at register 0x41."""
        return self._set_hx_v2_input_format_palette('OSFormatForeground', code)

    def set_hx_v2_input_format_background(self, code):
        """Set MD-HX input-format background by menu choice at register 0x42."""
        return self._set_hx_v2_input_format_palette(
            'OSFormatBackground', code,
            protocol.CPA_HX_V2_UMD_BACKGROUND_MENU_TO_RAW)

    def set_hx_v2_test_audio(self, output, code):
        """Set HX V2 test audio for the SDI or HDMI output at 0x82/0x83."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('test audio requires an MD-HX V2')
        if output not in ('sdi', 'hdmi'):
            raise ValueError('invalid test audio output')
        if type(code) is not int or code not in range(len(protocol.CPA_HX_V2_TEST_AUDIO)):
            raise ValueError('invalid test audio code')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = 0x82 if output == 'sdi' else 0x83
        value = (bytes(registers)[offset] & ~3) | code
        self.fpga_write_bytes(offset, bytes((value,)))
        actual = bytes(self.CPA)[offset] & 3
        if actual != code:
            raise RuntimeError('test audio selection did not retain the requested value')
        return protocol.CPA_HX_V2_TEST_AUDIO[actual]

    def _set_hx_v2_audio_meter_byte(self, offset, mask, value, setting):
        """Write one mapped Audio Meters field and verify its masked readback."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('Audio Meters control requires an MD-HX V2')
        if type(offset) is not int or type(mask) is not int or type(value) is not int:
            raise ValueError('invalid Audio Meters register value')
        if not 0 <= offset <= 0xff or not 0 < mask <= 0xff or value & ~mask:
            raise ValueError('invalid Audio Meters register mask or value')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        before = bytes(registers)[offset]
        expected = (before & ~mask) | value
        self.fpga_write_bytes(offset, bytes((expected,)))
        actual = bytes(self.CPA)[offset] & mask
        if actual != value:
            raise RuntimeError(f'{setting} did not retain the requested value')
        return actual

    def set_hx_v2_audio_meter_group(self, group, enabled):
        """Enable/disable Audio Meter Group 1..4 (register 0x60, bits 0..3)."""
        if type(group) is not int or group not in range(1, 5):
            raise ValueError('Audio Meter group must be between 1 and 4')
        if type(enabled) is not int or enabled not in (0, 1):
            raise ValueError('invalid Audio Meter group enable setting')
        mask = 1 << (group - 1)
        return bool(self._set_hx_v2_audio_meter_byte(
            0x60, mask, mask if enabled else 0, f'Audio Meter Group {group}'))

    def set_hx_v2_audio_meter_style(self, code):
        """Set Vertical Bars (0) or Horizontal Bars (1), register 0x61 bits 0..2."""
        if type(code) is not int or code not in range(len(protocol.CPA_HX_V2_AM_STYLES)):
            raise ValueError('invalid Audio Meter style')
        return self._set_hx_v2_audio_meter_byte(0x61, 0x07, code, 'Audio Meter style')

    def set_hx_v2_audio_meter_combination(self, code):
        """Set None/Bar/Float/Both, register 0x61 bits 3..4."""
        if type(code) is not int or code not in range(len(protocol.CPA_HX_V2_AM_COMBINATIONS)):
            raise ValueError('invalid Audio Meter combination')
        actual = self._set_hx_v2_audio_meter_byte(0x61, 0x18, code << 3,
                                                  'Audio Meter combination')
        return actual >> 3

    def set_hx_v2_audio_meter_transparency(self, code):
        """Set transparency code (1=50%, 2=25%, 3=0%), register 0x61 bits 5..6."""
        if type(code) is not int or code not in (1, 2, 3):
            raise ValueError('invalid Audio Meter transparency')
        actual = self._set_hx_v2_audio_meter_byte(0x61, 0x60, code << 5,
                                                  'Audio Meter transparency')
        return actual >> 5

    def set_hx_v2_audio_meter_scale(self, enabled):
        """Set Show Scale at register 0x61 bit 7."""
        if type(enabled) is not int or enabled not in (0, 1):
            raise ValueError('invalid Audio Meter scale setting')
        return bool(self._set_hx_v2_audio_meter_byte(
            0x61, 0x80, enabled << 7, 'Audio Meter scale setting'))

    def set_hx_v2_audio_meter_bar_scale(self, code):
        """Set one of the seven bar scales at register 0x62 bits 0..2."""
        if type(code) is not int or code not in range(len(protocol.CPA_HX_V2_AM_BAR_SCALES)):
            raise ValueError('invalid Audio Meter bar scale')
        return self._set_hx_v2_audio_meter_byte(0x62, 0x07, code,
                                                'Audio Meter bar scale')

    def set_hx_v2_audio_meter_bar_ballistics(self, code):
        """Set bar ballistics at register 0x62 bits 3..4."""
        if type(code) is not int or code not in range(len(protocol.CPA_HX_V2_AM_BALLISTICS)):
            raise ValueError('invalid Audio Meter bar ballistics')
        actual = self._set_hx_v2_audio_meter_byte(0x62, 0x18, code << 3,
                                                  'Audio Meter bar ballistics')
        return actual >> 3

    def set_hx_v2_audio_meter_float_ballistics(self, code):
        """Set float ballistics at register 0x62 bits 5..6."""
        if type(code) is not int or code not in range(len(protocol.CPA_HX_V2_AM_BALLISTICS)):
            raise ValueError('invalid Audio Meter float ballistics')
        actual = self._set_hx_v2_audio_meter_byte(0x62, 0x60, code << 5,
                                                  'Audio Meter float ballistics')
        return actual >> 5

    def set_hx_v2_audio_meter_margin(self, percent):
        """Set meter margin in 0.5% steps, register 0x63 (0..25%)."""
        if type(percent) not in (int, float) or not 0 <= percent <= 25 or percent * 2 % 1:
            raise ValueError('Audio Meter margin must be 0..25% in 0.5% steps')
        actual = self._set_hx_v2_audio_meter_byte(0x63, 0xff, int(percent * 2),
                                                  'Audio Meter margin')
        return actual / 2

    def set_hx_v2_audio_meter_reference_level(self, code):
        """Set -20/-18/-15 dBFS reference, register 0x64 bits 4..5."""
        if type(code) is not int or code not in range(len(protocol.CPA_HX_V2_AM_REFERENCE_LEVELS)):
            raise ValueError('invalid Audio Meter reference level')
        actual = self._set_hx_v2_audio_meter_byte(0x64, 0x30, code << 4,
                                                  'Audio Meter reference level')
        return actual >> 4

    def set_hx_v2_audio_meter_bar_thickness(self, thickness):
        """Set even bar thickness 2..24, encoded in register 0x64 low nibble."""
        if type(thickness) is not int or thickness not in range(2, 25, 2):
            raise ValueError('Audio Meter bar thickness must be an even value from 2 to 24')
        actual = self._set_hx_v2_audio_meter_byte(0x64, 0x0f, thickness // 2 - 1,
                                                  'Audio Meter bar thickness')
        return (actual + 1) * 2

    def _set_hx_v2_audio_meter_threshold(self, offset, dbfs, setting):
        if type(dbfs) not in (int, float) or not -100 <= dbfs <= 0 or dbfs * 2 % 1:
            raise ValueError(f'{setting} must be -100..0 dBFS in 0.5 dB steps')
        return self._set_hx_v2_audio_meter_byte(offset, 0xff, int(-dbfs * 2), setting)

    def set_hx_v2_audio_meter_yellow_start(self, dbfs):
        """Set Yellow Start in 0.5 dBFS steps at register 0x65."""
        actual = self._set_hx_v2_audio_meter_threshold(
            0x65, dbfs, 'Audio Meter yellow start')
        return -actual / 2

    def set_hx_v2_audio_meter_green_start(self, dbfs):
        """Set Green Start in 0.5 dBFS steps at register 0x66."""
        actual = self._set_hx_v2_audio_meter_threshold(
            0x66, dbfs, 'Audio Meter green start')
        return -actual / 2

    def set_hx_v2_auto_save(self, enabled):
        """Set the HX V2 Auto Save Settings Enable bit at register 0x2f."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('Auto Save control requires an MD-HX V2')
        if type(enabled) is not int or enabled not in (0, 1):
            raise ValueError('invalid Auto Save setting')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_Registers.AutoSave.offset
        value = (bytes(registers)[offset] & ~1) | enabled
        self.fpga_write_bytes(offset, bytes((value,)))
        actual = bytes(self.CPA)[offset] & 1
        if actual != enabled:
            raise RuntimeError('Auto Save setting did not retain the requested value')
        return actual

    def set_hx_v2_lcd_off_time(self, code):
        """Set HX V2 LCD-off timer using the eight Setup menu choices."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('LCD off time requires an MD-HX V2')
        if type(code) is not int or code not in range(8):
            raise ValueError('invalid LCD off time')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_Registers.LCDOffTime.offset
        self.fpga_write_bytes(offset, bytes((code,)))
        actual = bytes(self.CPA)[offset] & 7
        if actual != code:
            raise RuntimeError('LCD off time did not retain the requested value')
        return protocol.Time(actual)

    def set_hx_v2_return_to_status_time(self, code):
        """Set the HX V2 Back to Status timer, preserving reserved bits."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('Back to Status time requires an MD-HX V2')
        if type(code) is not int or code not in range(8):
            raise ValueError('invalid Back to Status time')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_Registers.ReturnToStatusTime.offset
        value = (bytes(registers)[offset] & ~7) | code
        self.fpga_write_bytes(offset, bytes((value,)))
        actual = bytes(self.CPA)[offset] & 7
        if actual != code:
            raise RuntimeError('Back to Status time did not retain the requested value')
        return protocol.Time(actual)

    def set_hx_v2_sd_input_aspect(self, code):
        """Set the documented MD-HX V2 SD IN ASPECT menu choice."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('SD IN ASPECT requires an MD-HX V2')
        if type(code) is not int or code not in range(len(protocol.CPA_HX_V2_SD_IN_ASPECTS)):
            raise ValueError('invalid SD IN ASPECT value')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_Registers.DUC_S2S_Aspect.offset
        value = (bytes(registers)[offset] & ~0x1f) | code
        self.fpga_write_bytes(offset, bytes((value,)))
        actual = bytes(self.CPA)[offset] & 0x1f
        if actual != code:
            raise RuntimeError('SD IN ASPECT did not retain the requested value')
        return actual

    def set_hx_v2_sd_output_aspect(self, code):
        """Set the documented MD-HX V2 SD OUT ASPECT menu choice."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('SD OUT ASPECT requires an MD-HX V2')
        if type(code) is not int or code not in range(len(protocol.CPA_HX_V2_SD_OUT_ASPECTS)):
            raise ValueError('invalid SD OUT ASPECT value')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_Registers.DUC_S2H_Aspect.offset
        value = (bytes(registers)[offset] & ~0x1f) | code
        self.fpga_write_bytes(offset, bytes((value,)))
        actual = bytes(self.CPA)[offset] & 0x1f
        if actual != code:
            raise RuntimeError('SD OUT ASPECT did not retain the requested value')
        return actual

    def set_hx_v2_input_image_aspect(self, code):
        """Set the documented MD-HX V2 IN IMAGE ASPECT menu choice."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('IN IMAGE ASPECT requires an MD-HX V2')
        if type(code) is not int or code not in range(len(protocol.CPA_HX_V2_IN_IMAGE_ASPECTS)):
            raise ValueError('invalid IN IMAGE ASPECT value')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_Registers.DUC_H2S_Aspect.offset
        value = (bytes(registers)[offset] & ~0x1f) | code
        self.fpga_write_bytes(offset, bytes((value,)))
        actual = bytes(self.CPA)[offset] & 0x1f
        if actual != code:
            raise RuntimeError('IN IMAGE ASPECT did not retain the requested value')
        return actual

    def set_hx_v2_output_image_aspect(self, code):
        """Set the documented MD-HX V2 OUT IMAGE ASPECT menu choice."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('OUT IMAGE ASPECT requires an MD-HX V2')
        if type(code) is not int or code not in range(len(protocol.CPA_HX_V2_OUT_IMAGE_ASPECTS)):
            raise ValueError('invalid OUT IMAGE ASPECT value')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_Registers.DUC_H2S_Aspect.offset
        value = (bytes(registers)[offset] & 0x1f) | (code << 5)
        self.fpga_write_bytes(offset, bytes((value,)))
        actual = (bytes(self.CPA)[offset] >> 5) & 7
        if actual != code:
            raise RuntimeError('OUT IMAGE ASPECT did not retain the requested value')
        return actual

    def set_hx_v2_safe_action_graticule(self, enabled):
        """Set the observed MD-HX V2 Safe Action graticule enable bit."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('Safe Action graticule requires an MD-HX V2')
        if type(enabled) is not int or enabled not in (0, 1):
            raise ValueError('Safe Action graticule must be 0 or 1')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_GRATICULE_SAFE_ACTION_OFFSET
        mask = protocol.CPA_HX_V2_GRATICULE_SAFE_ACTION_MASK
        value = (bytes(registers)[offset] & ~mask) | (enabled * mask)
        self.fpga_write_bytes(offset, bytes((value,)))
        actual = (bytes(self.CPA)[offset] & mask) != 0
        if actual != bool(enabled):
            raise RuntimeError('Safe Action graticule did not retain the requested value')
        return int(actual)

    def set_hx_v2_safe_title_graticule(self, enabled):
        """Set the observed MD-HX V2 Safe Title graticule enable bit."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('Safe Title graticule requires an MD-HX V2')
        if type(enabled) is not int or enabled not in (0, 1):
            raise ValueError('Safe Title graticule must be 0 or 1')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_GRATICULE_SAFE_TITLE_OFFSET
        mask = protocol.CPA_HX_V2_GRATICULE_SAFE_TITLE_MASK
        value = (bytes(registers)[offset] & ~mask) | (enabled * mask)
        self.fpga_write_bytes(offset, bytes((value,)))
        actual = (bytes(self.CPA)[offset] & mask) != 0
        if actual != bool(enabled):
            raise RuntimeError('Safe Title graticule did not retain the requested value')
        return int(actual)

    def set_hx_v2_centre_cross_graticule(self, enabled):
        """Set the observed MD-HX V2 Centre Cross graticule enable bit."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('Centre Cross graticule requires an MD-HX V2')
        if type(enabled) is not int or enabled not in (0, 1):
            raise ValueError('Centre Cross graticule must be 0 or 1')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_GRATICULE_CENTRE_CROSS_OFFSET
        mask = protocol.CPA_HX_V2_GRATICULE_CENTRE_CROSS_MASK
        value = (bytes(registers)[offset] & ~mask) | (enabled * mask)
        self.fpga_write_bytes(offset, bytes((value,)))
        actual = (bytes(self.CPA)[offset] & mask) != 0
        if actual != bool(enabled):
            raise RuntimeError('Centre Cross graticule did not retain the requested value')
        return int(actual)

    def set_hx_v2_safe_action_graticule_color(self, code):
        """Set the observed MD-HX V2 Safe Action colour menu selection."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('Safe Action colour requires an MD-HX V2')
        if type(code) is not int or code not in range(len(protocol.CPA_HX_V2_GRATICULE_COLORS)):
            raise ValueError('invalid Safe Action graticule colour')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_GRATICULE_SAFE_ACTION_OFFSET
        mask = protocol.CPA_HX_V2_GRATICULE_COLOR_MASK
        encoded = code + protocol.CPA_HX_V2_GRATICULE_COLOR_CODE_BASE
        value = (bytes(registers)[offset] & ~mask) | (encoded << 1)
        self.fpga_write_bytes(offset, bytes((value,)))
        actual = ((bytes(self.CPA)[offset] & mask) >> 1) - protocol.CPA_HX_V2_GRATICULE_COLOR_CODE_BASE
        if actual != code:
            raise RuntimeError('Safe Action graticule colour did not retain the requested value')
        return actual

    def set_hx_v2_safe_title_graticule_color(self, code):
        """Set the observed MD-HX V2 Safe Title colour menu selection."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('Safe Title colour requires an MD-HX V2')
        if type(code) is not int or code not in range(len(protocol.CPA_HX_V2_GRATICULE_COLORS)):
            raise ValueError('invalid Safe Title graticule colour')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_GRATICULE_SAFE_TITLE_OFFSET
        mask = protocol.CPA_HX_V2_GRATICULE_COLOR_MASK
        encoded = code + protocol.CPA_HX_V2_GRATICULE_COLOR_CODE_BASE
        value = (bytes(registers)[offset] & ~mask) | (encoded << 1)
        self.fpga_write_bytes(offset, bytes((value,)))
        actual = ((bytes(self.CPA)[offset] & mask) >> 1) - protocol.CPA_HX_V2_GRATICULE_COLOR_CODE_BASE
        if actual != code:
            raise RuntimeError('Safe Title graticule colour did not retain the requested value')
        return actual

    def set_hx_v2_centre_cross_graticule_color(self, code):
        """Set the observed MD-HX V2 Centre Cross colour menu selection."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('Centre Cross colour requires an MD-HX V2')
        if type(code) is not int or code not in range(len(protocol.CPA_HX_V2_GRATICULE_COLORS)):
            raise ValueError('invalid Centre Cross graticule colour')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_GRATICULE_CENTRE_CROSS_OFFSET
        mask = protocol.CPA_HX_V2_GRATICULE_COLOR_MASK
        encoded = code + protocol.CPA_HX_V2_GRATICULE_COLOR_CODE_BASE
        value = (bytes(registers)[offset] & ~mask) | (encoded << 1)
        self.fpga_write_bytes(offset, bytes((value,)))
        actual = ((bytes(self.CPA)[offset] & mask) >> 1) - protocol.CPA_HX_V2_GRATICULE_COLOR_CODE_BASE
        if actual != code:
            raise RuntimeError('Centre Cross graticule colour did not retain the requested value')
        return actual

    def set_hx_v2_outside_safe_action_graticule_color(self, code):
        """Set the observed MD-HX V2 Outside Safe Action colour menu choice."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('Outside Safe Action colour requires an MD-HX V2')
        if type(code) is not int or code not in range(len(protocol.CPA_HX_V2_GRATICULE_COLORS)):
            raise ValueError('invalid Outside Safe Action graticule colour')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_GRATICULE_OUTSIDE_SAFE_ACTION_COLOR_OFFSET
        mask = protocol.CPA_HX_V2_GRATICULE_OUTSIDE_SAFE_ACTION_COLOR_MASK
        shift = protocol.CPA_HX_V2_GRATICULE_OUTSIDE_SAFE_ACTION_COLOR_SHIFT
        raw_code = protocol.CPA_HX_V2_GRATICULE_OUTSIDE_SAFE_ACTION_MENU_TO_RAW[code]
        value = (bytes(registers)[offset] & ~mask) | (raw_code << shift)
        self.fpga_write_bytes(offset, bytes((value,)))
        actual_raw = (bytes(self.CPA)[offset] & mask) >> shift
        actual = protocol.CPA_HX_V2_GRATICULE_OUTSIDE_SAFE_ACTION_RAW_TO_MENU.get(actual_raw)
        if actual != code:
            raise RuntimeError('Outside Safe Action graticule colour did not retain the requested value')
        return actual

    def set_hx_v2_safe_action_vertical_start(self, percent):
        """Set the observed MD-HX V2 Safe Action vertical start position."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('Safe Action vertical start requires an MD-HX V2')
        if type(percent) not in (int, float) or not 0 <= percent <= 100 or percent * 2 != int(percent * 2):
            raise ValueError('Safe Action vertical start must be a 0.5% step from 0 to 100')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_GRATICULE_SA_VERT_START_OFFSET
        code = int(percent * 2)
        self.fpga_write_bytes(offset, bytes((code,)))
        actual = bytes(self.CPA)[offset]
        if actual != code:
            raise RuntimeError('Safe Action vertical start did not retain the requested value')
        return actual / 2

    def set_hx_v2_safe_action_horizontal_start(self, percent):
        """Set the observed MD-HX V2 Safe Action horizontal start position."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('Safe Action horizontal start requires an MD-HX V2')
        if type(percent) not in (int, float) or not 0 <= percent <= 100 or percent * 2 != int(percent * 2):
            raise ValueError('Safe Action horizontal start must be a 0.5% step from 0 to 100')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_GRATICULE_SA_HORZ_START_OFFSET
        code = int(percent * 2)
        self.fpga_write_bytes(offset, bytes((code,)))
        actual = bytes(self.CPA)[offset]
        if actual != code:
            raise RuntimeError('Safe Action horizontal start did not retain the requested value')
        return actual / 2

    def set_hx_v2_safe_action_horizontal_end(self, percent):
        """Set the observed MD-HX V2 Safe Action horizontal end position."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('Safe Action horizontal end requires an MD-HX V2')
        if type(percent) not in (int, float) or not 0 <= percent <= 100 or percent * 2 != int(percent * 2):
            raise ValueError('Safe Action horizontal end must be a 0.5% step from 0 to 100')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_GRATICULE_SA_HORZ_END_OFFSET
        code = int(percent * 2)
        self.fpga_write_bytes(offset, bytes((code,)))
        actual = bytes(self.CPA)[offset]
        if actual != code:
            raise RuntimeError('Safe Action horizontal end did not retain the requested value')
        return actual / 2

    def set_hx_v2_safe_action_vertical_end(self, percent):
        """Set the observed MD-HX V2 Safe Action vertical end position."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('Safe Action vertical end requires an MD-HX V2')
        if type(percent) not in (int, float) or not 0 <= percent <= 100 or percent * 2 != int(percent * 2):
            raise ValueError('Safe Action vertical end must be a 0.5% step from 0 to 100')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_GRATICULE_SA_VERT_END_OFFSET
        code = int(percent * 2)
        self.fpga_write_bytes(offset, bytes((code,)))
        actual = bytes(self.CPA)[offset]
        if actual != code:
            raise RuntimeError('Safe Action vertical end did not retain the requested value')
        return actual / 2

    def set_hx_v2_safe_title_horizontal_start(self, percent):
        """Set the observed MD-HX V2 Safe Title horizontal start position."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('Safe Title horizontal start requires an MD-HX V2')
        if type(percent) not in (int, float) or not 0 <= percent <= 100 or percent * 2 != int(percent * 2):
            raise ValueError('Safe Title horizontal start must be a 0.5% step from 0 to 100')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_GRATICULE_ST_HORZ_START_OFFSET
        code = int(percent * 2)
        self.fpga_write_bytes(offset, bytes((code,)))
        actual = bytes(self.CPA)[offset]
        if actual != code:
            raise RuntimeError('Safe Title horizontal start did not retain the requested value')
        return actual / 2

    def set_hx_v2_safe_title_horizontal_end(self, percent):
        """Set the observed MD-HX V2 Safe Title horizontal end position."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('Safe Title horizontal end requires an MD-HX V2')
        if type(percent) not in (int, float) or not 0 <= percent <= 100 or percent * 2 != int(percent * 2):
            raise ValueError('Safe Title horizontal end must be a 0.5% step from 0 to 100')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_GRATICULE_ST_HORZ_END_OFFSET
        code = int(percent * 2)
        self.fpga_write_bytes(offset, bytes((code,)))
        actual = bytes(self.CPA)[offset]
        if actual != code:
            raise RuntimeError('Safe Title horizontal end did not retain the requested value')
        return actual / 2

    def set_hx_v2_safe_title_vertical_start(self, percent):
        """Set the observed MD-HX V2 Safe Title vertical start position."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('Safe Title vertical start requires an MD-HX V2')
        if type(percent) not in (int, float) or not 0 <= percent <= 100 or percent * 2 != int(percent * 2):
            raise ValueError('Safe Title vertical start must be a 0.5% step from 0 to 100')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_GRATICULE_ST_VERT_START_OFFSET
        code = int(percent * 2)
        self.fpga_write_bytes(offset, bytes((code,)))
        actual = bytes(self.CPA)[offset]
        if actual != code:
            raise RuntimeError('Safe Title vertical start did not retain the requested value')
        return actual / 2

    def set_hx_v2_safe_title_vertical_end(self, percent):
        """Set the observed MD-HX V2 Safe Title vertical end position."""
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('Safe Title vertical end requires an MD-HX V2')
        if type(percent) not in (int, float) or not 0 <= percent <= 100 or percent * 2 != int(percent * 2):
            raise ValueError('Safe Title vertical end must be a 0.5% step from 0 to 100')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        offset = protocol.CPA_HX_V2_GRATICULE_ST_VERT_END_OFFSET
        code = int(percent * 2)
        self.fpga_write_bytes(offset, bytes((code,)))
        actual = bytes(self.CPA)[offset]
        if actual != code:
            raise RuntimeError('Safe Title vertical end did not retain the requested value')
        return actual / 2

    def set_hx_v2_graticule_16_9_lb_on_4_3(self):
        """Apply the observed MD-HX V2 16:9 LB on 4:3 graticule preset.

        This front-panel action changes the horizontal bounds for Safe Action
        and Safe Title. It leaves vertical bounds, colors, and enable bits
        untouched.
        """
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('graticule aspect preset requires an MD-HX V2')
        registers = self.CPA
        raw = bytes(registers)
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')

        offsets = (
            protocol.CPA_HX_V2_GRATICULE_SA_HORZ_START_OFFSET,
            protocol.CPA_HX_V2_GRATICULE_SA_HORZ_END_OFFSET,
            protocol.CPA_HX_V2_GRATICULE_ST_HORZ_START_OFFSET,
            protocol.CPA_HX_V2_GRATICULE_ST_HORZ_END_OFFSET,
        )
        values = protocol.CPA_HX_V2_GRATICULE_16_9_LB_ON_4_3
        try:
            for offset, value in zip(offsets, values):
                self.fpga_write_bytes(offset, bytes((value,)))
            actual = bytes(self.CPA)
            if any(actual[offset] != value for offset, value in zip(offsets, values)):
                raise RuntimeError('16:9 LB on 4:3 graticule preset did not retain its values')
        except Exception:
            for offset in offsets:
                self.fpga_write_bytes(offset, bytes((raw[offset],)))
            raise
        return tuple(actual[offset] / 2 for offset in offsets)

    def set_hx_v2_graticule_4_3_pb_on_16_9(self):
        """Apply the observed MD-HX V2 4:3 PB on 16:9 graticule preset.

        The front-panel action changes the vertical bounds for Safe Action
        and Safe Title. It leaves horizontal bounds, colors, and enable bits
        untouched.
        """
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('graticule aspect preset requires an MD-HX V2')
        registers = self.CPA
        raw = bytes(registers)
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')

        offsets = (
            protocol.CPA_HX_V2_GRATICULE_SA_VERT_START_OFFSET,
            protocol.CPA_HX_V2_GRATICULE_SA_VERT_END_OFFSET,
            protocol.CPA_HX_V2_GRATICULE_ST_VERT_START_OFFSET,
            protocol.CPA_HX_V2_GRATICULE_ST_VERT_END_OFFSET,
        )
        values = protocol.CPA_HX_V2_GRATICULE_4_3_PB_ON_16_9
        try:
            for offset, value in zip(offsets, values):
                self.fpga_write_bytes(offset, bytes((value,)))
            actual = bytes(self.CPA)
            if any(actual[offset] != value for offset, value in zip(offsets, values)):
                raise RuntimeError('4:3 PB on 16:9 graticule preset did not retain its values')
        except Exception:
            for offset in offsets:
                self.fpga_write_bytes(offset, bytes((raw[offset],)))
            raise
        return tuple(actual[offset] / 2 for offset in offsets)

    def set_hx_v2_graticule_anamorphic(self):
        """Apply the observed MD-HX V2 Anamorphic graticule action.

        On the tested signal, this action restores the default geometry for
        Safe Action and Safe Title. It leaves colors, enable bits, and aspect
        registers untouched.
        """
        if self.device_type != DeviceType.CPA_HX_V2:
            raise ValueError('graticule aspect action requires an MD-HX V2')
        registers = self.CPA
        raw = bytes(registers)
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')

        offsets = (
            protocol.CPA_HX_V2_GRATICULE_SA_HORZ_START_OFFSET,
            protocol.CPA_HX_V2_GRATICULE_SA_HORZ_END_OFFSET,
            protocol.CPA_HX_V2_GRATICULE_SA_VERT_START_OFFSET,
            protocol.CPA_HX_V2_GRATICULE_SA_VERT_END_OFFSET,
            protocol.CPA_HX_V2_GRATICULE_ST_HORZ_START_OFFSET,
            protocol.CPA_HX_V2_GRATICULE_ST_HORZ_END_OFFSET,
            protocol.CPA_HX_V2_GRATICULE_ST_VERT_START_OFFSET,
            protocol.CPA_HX_V2_GRATICULE_ST_VERT_END_OFFSET,
        )
        values = protocol.CPA_HX_V2_GRATICULE_ANAMORPHIC
        try:
            for offset, value in zip(offsets, values):
                self.fpga_write_bytes(offset, bytes((value,)))
            actual = bytes(self.CPA)
            if any(actual[offset] != value for offset, value in zip(offsets, values)):
                raise RuntimeError('Anamorphic graticule action did not retain its values')
        except Exception:
            for offset in offsets:
                self.fpga_write_bytes(offset, bytes((raw[offset],)))
            raise
        return tuple(actual[offset] / 2 for offset in offsets)

    def set_lx_output_mode(self, mode):
        """Set MD-LX output mode, preserving unrelated bits in register 0x37."""
        if self.device_type != DeviceType.CPA_LX:
            raise ValueError('output mode requires an MD-LX')
        if type(mode) is not int or mode not in (0, 1, 2, 3):
            raise ValueError('invalid MD-LX output mode')
        registers = self.CPA
        if bytes(registers.magic) != b'GW':
            raise ValueError('unexpected register signature')
        registers.LXA_Out = (int(registers.LXA_Out) & ~3) | mode
        actual = int(self.CPA.LXA_Out) & 3
        if actual != mode:
            raise RuntimeError('MD-LX output mode did not retain the requested value')
        return protocol.CPA_LX_Registers._output_modes[actual]

    @property
    def VFA(self):
        return self._registers(protocol.VFA_Registers)

    @property
    def KPA(self):
        return self._registers(protocol.KPA_Registers)

    @property
    def device_type(self):
        serial_3 = self.serial[:3]
        return _SERIAL_PREFIX_TO_TYPE.get(serial_3)

    @property
    def registers(self):
        if self.device_type & DeviceType.DHA:
            raise NotImplementedError('DHA not supported')
        elif self.device_type & DeviceType.DUC:
            raise NotImplementedError('DUC not supported')
        elif self.device_type & DeviceType.CPA:
            return self.CPA
        elif self.device_type & DeviceType.MQS:
            raise NotImplementedError('MQS not supported')
        elif self.device_type & DeviceType.MQA:
            raise NotImplementedError('MQA not supported')
        elif self.device_type & DeviceType.VFA:
            return self.VFA
        elif self.device_type & DeviceType.KPA:
            return self.KPA
        else:
            raise NotImplementedError('unrecognized serial prefix %s' % self.serial[:3])

    # To identify the type, look at the first 3 characters of the serial number
    # DHA, DHB => DHA
    # DUC => DUC
    # CLA, LLA => CPA(0) # _CPA_HX_V1
    # CLB, LLB => CPA(1) # _CPA_HX_V1
    # CLC, LLC => CPA(2) # _CPA_HX_V1
    # CLD, LLD => CPA(3) # _CPA_HX_V2
    # CPA, LPA => CPA(4) # _CPA_CROSS_V1
    # CPB, LPB => CPA(5) # _CPA_CROSS_V2
    # CPC, LPC => CPA(6) # _CPA_CROSS_V2
    # ??? => CPA(7) # _CPA_CROSS_V3
    # CXA, LXA => CPA(8) # _CPA_LX
    # CXB, LXB => CPA(9) # _CPA_LX
    # MQS => MQS
    # MQA, MQB => MQA
    # M, V =>
    # MQC => VFA(4,0,0)
    # MQD => VFA(4,2,0)
    # MDA => VFA(4,1,0)
    # MDB => VFA(4,1,1)
    # MPA => VFA(16,1,0)
    # MPB => VFA(16,1,1)
    # VFA => VFA(6,0,0)
    # VFB => VFA(6,0,1)
    # VLA => VFA(12,0,0)
    # VLB => VFA(12,0,1)
    # VPA => VFA(16,0,0)
    # VPB => VFA(16,0,1)
    # OAA => VFA(9,0,0)
    # OBA => VFA(4,4,0)
    
if __name__ == "__main__":
    print(list_devices())

    os.chdir("logs")

    with Device(log_raw_data=True) as dev:
        print(dev.serial)
        dev.CPA.SO_Source = 0

        status_bytes = dev.raw_registers
        open('%s-status.dat' % now(), 'wb').write(status_bytes)
        print(status_bytes)

        print(dev.CPA)

        if False:
            import time
            while True:
                time.sleep(1)
                dev.CPA.SO_Source = 1
                time.sleep(1)
                dev.CPA.SO_Source = 0
