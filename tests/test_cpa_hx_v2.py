import unittest

from decimctl import Device, DeviceType
from decimctl.protocol import (
    CPA_HX_V2_CalcFormatString,
    CPA_HX_V2_Registers,
    CPA_HX_V2_TPG_PATTERNS,
    CPA_LX_Registers,
    CPA_Registers,
)


class CPAHXV2StatusTests(unittest.TestCase):
    def test_same_hdmi_signal_uses_different_status_layouts(self):
        registers = bytearray(0x200)
        registers[0x12] = 0x20

        registers[0x13] = 0x1c
        hx = CPA_HX_V2_Registers.from_buffer_copy(registers)
        self.assertEqual(hx.Input2Status, "3G-A 1920x1080p60")
        self.assertTrue(hx.Input2Locked)
        self.assertEqual(int(hx.Input2Standard), 3)
        self.assertEqual(hx.Input2HDFractional, 0)
        self.assertEqual(hx.Input23GB, 0)

        registers[0x13] = 0x07
        lx = CPA_Registers.from_buffer_copy(registers)
        self.assertEqual(lx.Input2Status, "3G-A 1920x1080p60")

    def test_lock_and_three_g_variants(self):
        self.assertEqual(CPA_HX_V2_CalcFormatString(0x20, 0x0c), "Unlocked")
        self.assertEqual(CPA_HX_V2_CalcFormatString(0x21, 0x1f),
                         "3G-B 1920x1080p59.94")
        self.assertEqual(CPA_HX_V2_CalcFormatString(0x28, 0x1c),
                         "3G-A 2048x1080p60")
        self.assertEqual(CPA_HX_V2_CalcFormatString(0x21, 0x1c), "Unknown")

    def test_device_type_selects_matching_register_layout(self):
        class StubDevice:
            def __init__(self, device_type):
                self.device_type = device_type

            def _registers(self, register_type):
                return register_type

        self.assertIs(Device.CPA.fget(StubDevice(DeviceType.CPA_HX_V2)),
                      CPA_HX_V2_Registers)
        self.assertIs(Device.CPA.fget(StubDevice(DeviceType.CPA_LX)),
                      CPA_LX_Registers)

    def test_both_hx_v2_serial_prefixes_select_v2_device_type(self):
        for prefix in (b"CLD", b"LLD"):
            with self.subTest(prefix=prefix):
                device = type("StubDevice", (), {"serial": prefix + b"00000"})()
                self.assertIs(
                    Device.device_type.fget(device), DeviceType.CPA_HX_V2
                )

    def test_lx_output_mode_uses_register_37_low_bits(self):
        registers = bytearray(0x200)
        lx = CPA_LX_Registers.from_buffer_copy(registers)
        self.assertEqual(lx.OutputMode, "Auto Select")

        registers[0x37] = 0x83
        lx = CPA_LX_Registers.from_buffer_copy(registers)
        self.assertEqual(lx.OutputMode, "HDMI to HDMI and SDI")

    def test_cpa_fields_after_motion_threshold_keep_wire_offsets(self):
        self.assertEqual(CPA_HX_V2_Registers.DUC_TH1.offset, 0x27)
        self.assertEqual(CPA_HX_V2_Registers.Loop_Enable.offset, 0x2b)
        self.assertEqual(CPA_HX_V2_Registers.HO_Type.offset, 0x30)
        self.assertEqual(CPA_HX_V2_Registers.SO_Source.offset, 0x31)
        self.assertEqual(CPA_HX_V2_Registers.HO_Source.offset, 0x32)
        self.assertEqual(CPA_HX_V2_Registers.DUC_Source.offset, 0x33)
        self.assertEqual(CPA_LX_Registers.LXA_Out.offset, 0x37)

        registers = bytearray(0x200)
        registers[0x2b] = 1
        registers[0x30:0x34] = bytes([1, 2, 2, 1])
        hx = CPA_HX_V2_Registers.from_buffer_copy(registers)
        self.assertEqual(hx.Loop_Enable, 1)
        self.assertEqual(hx.HO_Type.name, "HDMI_RGB_444_2ch")
        self.assertEqual(hx.SO_Source.name, "DUC")
        self.assertEqual(hx.HO_Source.name, "DUC")
        self.assertEqual(hx.DUC_Source.name, "HDMI_IN")

    def test_output_format_uses_v2_menu_order(self):
        registers = bytearray(0x200)
        registers[0x22] = 13
        hx = CPA_HX_V2_Registers.from_buffer_copy(registers)
        self.assertEqual(hx.DUCFormat, 13)
        self.assertEqual(hx.OutputFormat, "HD 1920x1080i59.94")

        registers[0x22] = 63
        hx = CPA_HX_V2_Registers.from_buffer_copy(registers)
        self.assertEqual(hx.OutputFormat, "Unknown")

    def test_tpg_pattern_names_follow_manual_menu_order(self):
        self.assertEqual(len(CPA_HX_V2_TPG_PATTERNS), 58)
        self.assertEqual(CPA_HX_V2_TPG_PATTERNS[0], "SMPTE HD Bars")
        self.assertEqual(CPA_HX_V2_TPG_PATTERNS[20], "White 75%")
        self.assertEqual(CPA_HX_V2_TPG_PATTERNS[40], "Y Move Dn Y ZP")
        self.assertEqual(CPA_HX_V2_TPG_PATTERNS[57], "C Move Out C ZP")

    def test_audio_meter_fields_use_observed_register_offsets(self):
        self.assertEqual(CPA_HX_V2_Registers.AM1_EN.offset, 0x60)
        self.assertEqual(CPA_HX_V2_Registers.Scale_EN.offset, 0x61)
        self.assertEqual(CPA_HX_V2_Registers.AM_Style.offset, 0x61)
        self.assertEqual(CPA_HX_V2_Registers.AM_BarScale.offset, 0x62)
        self.assertEqual(CPA_HX_V2_Registers.AM_Margin.offset, 0x63)
        self.assertEqual(CPA_HX_V2_Registers.AM_ReferenceLevel.offset, 0x64)
        self.assertEqual(CPA_HX_V2_Registers.AM_BarThickness.offset, 0x64)
        self.assertEqual(CPA_HX_V2_Registers.AM_YellowStart.offset, 0x65)
        self.assertEqual(CPA_HX_V2_Registers.AM_GreenStart.offset, 0x66)

        raw = bytearray(0x200)
        raw[0x60] = 0x0b  # Groups 1, 2, and 4.
        raw[0x61] = 0x80 | (3 << 5) | (2 << 3) | 1
        raw[0x62] = (1 << 5) | (2 << 3) | 6
        raw[0x63] = 10
        raw[0x64] = (2 << 4) | 5
        raw[0x65] = 20
        raw[0x66] = 40
        registers = CPA_HX_V2_Registers.from_buffer_copy(raw)

        self.assertEqual([registers.AM1_EN, registers.AM2_EN,
                          registers.AM3_EN, registers.AM4_EN], [1, 1, 0, 1])
        self.assertEqual(registers.Scale_EN, 1)
        self.assertEqual(registers.AM_Transparency, 3)
        self.assertEqual(registers.AM_Combination, 2)
        self.assertEqual(registers.AM_Style, 1)
        self.assertEqual(registers.AM_BarScale, 6)
        self.assertEqual(registers.AM_BarBallistics, 2)
        self.assertEqual(registers.AM_FloatBallistics, 1)
        self.assertEqual(registers.AM_Margin, 10)
        self.assertEqual(registers.AM_ReferenceLevel, 2)
        self.assertEqual(registers.AM_BarThickness, 5)
        self.assertEqual(registers.AM_YellowStart, 20)
        self.assertEqual(registers.AM_GreenStart, 40)


if __name__ == "__main__":
    unittest.main()
