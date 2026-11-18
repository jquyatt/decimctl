import unittest

from decimctl import Device, DeviceType
from decimctl.protocol import CPA_HX_V2_Registers, CPA_LX_Registers, SO_Source


class FakeDevice:
    set_hx_v2_hdmi_output_source = Device.set_hx_v2_hdmi_output_source
    set_hx_v2_sdi_output_source = Device.set_hx_v2_sdi_output_source
    set_hx_v2_audio_pair = Device.set_hx_v2_audio_pair
    set_hx_v2_no_signal_color = Device.set_hx_v2_no_signal_color
    set_hx_v2_output_3g_b = Device.set_hx_v2_output_3g_b
    set_hx_v2_output_1_loop = Device.set_hx_v2_output_1_loop
    set_hx_v2_hdmi_output_type = Device.set_hx_v2_hdmi_output_type
    set_hx_v2_scaler_reference = Device.set_hx_v2_scaler_reference
    set_hx_v2_horizontal_filter = Device.set_hx_v2_horizontal_filter
    set_hx_v2_motion_detect_level = Device.set_hx_v2_motion_detect_level
    set_hx_v2_outside_safe_action_graticule_color = Device.set_hx_v2_outside_safe_action_graticule_color
    set_hx_v2_tpg_enabled = Device.set_hx_v2_tpg_enabled
    set_hx_v2_tpg_pattern = Device.set_hx_v2_tpg_pattern
    set_hx_v2_overlay_target = Device.set_hx_v2_overlay_target
    set_hx_v2_umd_enabled = Device.set_hx_v2_umd_enabled
    set_hx_v2_umd_foreground = Device.set_hx_v2_umd_foreground
    set_hx_v2_umd_background = Device.set_hx_v2_umd_background
    _set_hx_v2_umd_palette = Device._set_hx_v2_umd_palette
    set_hx_v2_input_format_overlay = Device.set_hx_v2_input_format_overlay
    set_hx_v2_input_format_foreground = Device.set_hx_v2_input_format_foreground
    set_hx_v2_input_format_background = Device.set_hx_v2_input_format_background
    _set_hx_v2_input_format_palette = Device._set_hx_v2_input_format_palette
    set_hx_v2_test_audio = Device.set_hx_v2_test_audio
    _set_hx_v2_audio_meter_byte = Device._set_hx_v2_audio_meter_byte
    set_hx_v2_audio_meter_group = Device.set_hx_v2_audio_meter_group
    set_hx_v2_audio_meter_style = Device.set_hx_v2_audio_meter_style
    set_hx_v2_audio_meter_combination = Device.set_hx_v2_audio_meter_combination
    set_hx_v2_audio_meter_transparency = Device.set_hx_v2_audio_meter_transparency
    set_hx_v2_audio_meter_scale = Device.set_hx_v2_audio_meter_scale
    set_hx_v2_audio_meter_bar_scale = Device.set_hx_v2_audio_meter_bar_scale
    set_hx_v2_audio_meter_bar_ballistics = Device.set_hx_v2_audio_meter_bar_ballistics
    set_hx_v2_audio_meter_float_ballistics = Device.set_hx_v2_audio_meter_float_ballistics
    set_hx_v2_audio_meter_margin = Device.set_hx_v2_audio_meter_margin
    set_hx_v2_audio_meter_reference_level = Device.set_hx_v2_audio_meter_reference_level
    set_hx_v2_audio_meter_bar_thickness = Device.set_hx_v2_audio_meter_bar_thickness
    _set_hx_v2_audio_meter_threshold = Device._set_hx_v2_audio_meter_threshold
    set_hx_v2_audio_meter_yellow_start = Device.set_hx_v2_audio_meter_yellow_start
    set_hx_v2_audio_meter_green_start = Device.set_hx_v2_audio_meter_green_start
    set_hx_v2_auto_save = Device.set_hx_v2_auto_save
    set_hx_v2_lcd_off_time = Device.set_hx_v2_lcd_off_time
    set_hx_v2_return_to_status_time = Device.set_hx_v2_return_to_status_time
    set_hx_v2_sd_input_aspect = Device.set_hx_v2_sd_input_aspect
    set_hx_v2_sd_output_aspect = Device.set_hx_v2_sd_output_aspect
    set_hx_v2_input_image_aspect = Device.set_hx_v2_input_image_aspect
    set_hx_v2_output_image_aspect = Device.set_hx_v2_output_image_aspect
    set_hx_v2_safe_action_graticule = Device.set_hx_v2_safe_action_graticule
    set_hx_v2_safe_title_graticule = Device.set_hx_v2_safe_title_graticule
    set_hx_v2_centre_cross_graticule = Device.set_hx_v2_centre_cross_graticule
    set_hx_v2_safe_action_graticule_color = Device.set_hx_v2_safe_action_graticule_color
    set_hx_v2_safe_title_graticule_color = Device.set_hx_v2_safe_title_graticule_color
    set_hx_v2_centre_cross_graticule_color = Device.set_hx_v2_centre_cross_graticule_color
    set_hx_v2_safe_action_vertical_start = Device.set_hx_v2_safe_action_vertical_start
    set_hx_v2_safe_action_horizontal_start = Device.set_hx_v2_safe_action_horizontal_start
    set_hx_v2_safe_action_horizontal_end = Device.set_hx_v2_safe_action_horizontal_end
    set_hx_v2_safe_action_vertical_end = Device.set_hx_v2_safe_action_vertical_end
    set_hx_v2_safe_title_horizontal_start = Device.set_hx_v2_safe_title_horizontal_start
    set_hx_v2_safe_title_horizontal_end = Device.set_hx_v2_safe_title_horizontal_end
    set_hx_v2_safe_title_vertical_start = Device.set_hx_v2_safe_title_vertical_start
    set_hx_v2_safe_title_vertical_end = Device.set_hx_v2_safe_title_vertical_end
    set_hx_v2_graticule_16_9_lb_on_4_3 = Device.set_hx_v2_graticule_16_9_lb_on_4_3
    set_hx_v2_graticule_4_3_pb_on_16_9 = Device.set_hx_v2_graticule_4_3_pb_on_16_9
    set_hx_v2_graticule_anamorphic = Device.set_hx_v2_graticule_anamorphic
    set_hx_v2_umd_text = Device.set_hx_v2_umd_text
    set_hx_v2_1080i_as_psf = Device.set_hx_v2_1080i_as_psf
    set_hx_v2_flip = Device.set_hx_v2_flip
    set_hx_v2_scaler_output_format = Device.set_hx_v2_scaler_output_format
    set_hx_v2_scaler_source = Device.set_hx_v2_scaler_source
    set_lx_output_mode = Device.set_lx_output_mode

    def __init__(self, device_type, register_type):
        self.device_type = device_type
        self.register_type = register_type
        self.raw = bytearray(0x200)
        self.raw[:2] = b'GW'
        self.writes = []

    @property
    def CPA(self):
        registers = self.register_type.from_buffer_copy(self.raw)
        registers._device = self
        return registers

    def fpga_write_bytes(self, offset, value):
        self.writes.append((offset, value))
        self.raw[offset:offset + len(value)] = value


class CPAWriteTests(unittest.TestCase):
    def test_hx_audio_pair_writes_preserve_neighbor_pair(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x38] = 0xa5
        device.raw[0x3d] = 0x69
        hdmi_pair_2 = int(device.CPA.HDMI_Pair2)
        sdi_pair_7 = int(device.CPA.SDI_Pair7)

        self.assertEqual(device.set_hx_v2_audio_pair('hdmi', 1, 8).name, 'OFF')
        self.assertEqual(device.set_hx_v2_audio_pair('sdi', 8, 6).name, 'GROUP_4_PAIR_1')

        self.assertEqual(int(device.CPA.HDMI_Pair1), 8)
        self.assertEqual(int(device.CPA.HDMI_Pair2), hdmi_pair_2)
        self.assertEqual(int(device.CPA.SDI_Pair8), 6)
        self.assertEqual(int(device.CPA.SDI_Pair7), sdi_pair_7)
        self.assertEqual([offset for offset, _ in device.writes], [0x38, 0x3d])

    def test_hx_no_signal_colors_preserve_reserved_bits(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x43] = 0xa8
        device.raw[0x44] = 0xd0

        self.assertEqual(device.set_hx_v2_no_signal_color('foreground', 7), 7)
        self.assertEqual(device.set_hx_v2_no_signal_color('background', 3), 3)

        self.assertEqual(device.raw[0x43], 0xaf)
        self.assertEqual(device.raw[0x44], 0xd3)
        self.assertEqual(device.writes, [(0x43, b'\xaf'), (0x44, b'\xd3')])

    def test_hx_audio_pair_writes_reject_invalid_fields(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        with self.assertRaises(ValueError):
            device.set_hx_v2_audio_pair('hdmi', 5, 0)
        with self.assertRaises(ValueError):
            device.set_hx_v2_audio_pair('sdi', 1, 9)
        with self.assertRaises(ValueError):
            device.set_hx_v2_audio_pair('unknown', 1, 0)

    def test_hx_tpg_writes_preserve_neighbor_bits(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x80] = 0x80
        device.raw[0x81] = 0xc0
        self.assertEqual(device.set_hx_v2_tpg_pattern(1), 'Bars 100/0/100/0')
        self.assertEqual(device.set_hx_v2_tpg_enabled(1), 1)
        self.assertEqual(device.writes, [(0x81, b'\xc1'), (0x80, b'\x81')])

    def test_hx_overlay_target_preserves_neighbor_bits(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x34] = 0xfc
        self.assertEqual(device.set_hx_v2_overlay_target(2), 2)
        self.assertEqual(device.writes, [(0x34, b'\xfe')])

    def test_hx_umd_enable_preserves_neighbor_bits(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x45] = 0xfe
        self.assertEqual(device.set_hx_v2_umd_enabled(1), 1)
        self.assertEqual(device.writes, [(0x45, b'\xff')])
        self.assertEqual(device.set_hx_v2_umd_enabled(0), 0)
        self.assertEqual(device.writes[-1], (0x45, b'\xfe'))

    def test_hx_umd_palette_writes_preserve_neighbor_bits(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x46] = 0xe0
        device.raw[0x47] = 0xf8
        self.assertEqual(device.set_hx_v2_umd_foreground(21), 'Magenta (Transparent 0%)')
        self.assertEqual(device.set_hx_v2_umd_background(5), 'Red (Transparent 50%)')
        self.assertEqual(device.set_hx_v2_umd_background(24), 'White (Transparent 0%)')
        self.assertEqual(device.writes, [(0x46, b'\xf5'), (0x47, b'\xec'), (0x47, b'\xff')])

    def test_hx_input_format_overlay_preserves_neighbor_bits(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x40] = 0xfc
        self.assertEqual(device.set_hx_v2_input_format_overlay(2), 'Show Always')
        self.assertEqual(device.writes, [(0x40, b'\xfe')])

    def test_hx_input_format_palette_writes_preserve_neighbor_bits(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x41] = 0xe0
        device.raw[0x42] = 0xa0
        self.assertEqual(device.set_hx_v2_input_format_foreground(21), 'Magenta (Transparent 0%)')
        self.assertEqual(device.set_hx_v2_input_format_background(17), 'Black (Transparent 0%)')
        self.assertEqual(device.writes, [(0x41, b'\xf5'), (0x42, b'\xb8')])
        with self.assertRaises(ValueError):
            device.set_hx_v2_input_format_background(25)

    def test_hx_umd_background_menu_indices_map_to_register_codes(self):
        from decimctl.protocol import CPA_HX_V2_UMD_BACKGROUND_MENU_TO_RAW

        self.assertEqual(CPA_HX_V2_UMD_BACKGROUND_MENU_TO_RAW[0], 0)
        self.assertEqual(CPA_HX_V2_UMD_BACKGROUND_MENU_TO_RAW[1], 8)
        self.assertEqual(CPA_HX_V2_UMD_BACKGROUND_MENU_TO_RAW[17], 24)
        self.assertEqual(CPA_HX_V2_UMD_BACKGROUND_MENU_TO_RAW[24], 31)

    def test_hx_outside_safe_action_color_uses_menu_mapping_and_preserves_neighbors(self):
        from decimctl.protocol import CPA_HX_V2_GRATICULE_OUTSIDE_SAFE_ACTION_MENU_TO_RAW

        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x5b] = 0xe0
        self.assertEqual(device.set_hx_v2_outside_safe_action_graticule_color(0), 0)
        self.assertEqual(device.raw[0x5b], 0xe0)
        self.assertEqual(device.set_hx_v2_outside_safe_action_graticule_color(1), 1)
        self.assertEqual(device.raw[0x5b], 0xe8)
        self.assertEqual(device.set_hx_v2_outside_safe_action_graticule_color(11), 11)
        self.assertEqual(device.raw[0x5b], 0xf2)
        self.assertEqual(device.set_hx_v2_outside_safe_action_graticule_color(24), 24)
        self.assertEqual(device.raw[0x5b], 0xff)
        self.assertEqual(CPA_HX_V2_GRATICULE_OUTSIDE_SAFE_ACTION_MENU_TO_RAW[11], 18)
        self.assertEqual(device.writes, [
            (0x5b, b'\xe0'), (0x5b, b'\xe8'), (0x5b, b'\xf2'), (0x5b, b'\xff'),
        ])

    def test_hx_test_audio_writes_selected_output_and_preserves_neighbors(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x82] = 0xfc
        device.raw[0x83] = 0xf8
        self.assertEqual(device.set_hx_v2_test_audio('sdi', 1), '1 kHz Tone')
        self.assertEqual(device.set_hx_v2_test_audio('hdmi', 2), '1 kHz / 500 Hz / Broken Tones')
        self.assertEqual(device.writes, [(0x82, b'\xfd'), (0x83, b'\xfa')])

    def test_hx_audio_meter_writes_preserve_register_masks_and_read_back(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x60] = 0xf0
        self.assertTrue(device.set_hx_v2_audio_meter_group(1, 1))
        device.raw[0x61] = 0x05
        self.assertEqual(device.set_hx_v2_audio_meter_style(1), 1)
        self.assertEqual(device.set_hx_v2_audio_meter_combination(3), 3)
        self.assertEqual(device.set_hx_v2_audio_meter_transparency(2), 2)
        self.assertTrue(device.set_hx_v2_audio_meter_scale(1))
        device.raw[0x62] = 0x80
        self.assertEqual(device.set_hx_v2_audio_meter_bar_scale(6), 6)
        self.assertEqual(device.set_hx_v2_audio_meter_bar_ballistics(2), 2)
        self.assertEqual(device.set_hx_v2_audio_meter_float_ballistics(1), 1)
        self.assertEqual(device.set_hx_v2_audio_meter_margin(5), 5)
        device.raw[0x64] = 0xc0
        self.assertEqual(device.set_hx_v2_audio_meter_reference_level(2), 2)
        self.assertEqual(device.set_hx_v2_audio_meter_bar_thickness(24), 24)
        self.assertEqual(device.set_hx_v2_audio_meter_yellow_start(-10), -10)
        self.assertEqual(device.set_hx_v2_audio_meter_green_start(-20), -20)
        self.assertEqual(device.raw[0x60], 0xf1)
        self.assertEqual(device.raw[0x61], 0xd9)
        self.assertEqual(device.raw[0x62], 0xb6)
        self.assertEqual(device.raw[0x63], 10)
        self.assertEqual(device.raw[0x64], 0xeb)
        self.assertEqual(device.raw[0x65:0x67], bytes((20, 40)))

    def test_hx_audio_meter_writes_reject_out_of_range_values(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        with self.assertRaises(ValueError):
            device.set_hx_v2_audio_meter_group(5, 1)
        with self.assertRaises(ValueError):
            device.set_hx_v2_audio_meter_transparency(0)
        with self.assertRaises(ValueError):
            device.set_hx_v2_audio_meter_bar_scale(7)
        with self.assertRaises(ValueError):
            device.set_hx_v2_audio_meter_margin(5.25)
        with self.assertRaises(ValueError):
            device.set_hx_v2_audio_meter_bar_thickness(23)
        with self.assertRaises(ValueError):
            device.set_hx_v2_audio_meter_yellow_start(-100.25)

    def test_hx_setup_writes_preserve_or_select_expected_registers(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x2f] = 0x80
        device.raw[0x35] = 0xf7
        device.raw[0x36] = 0xf8
        self.assertEqual(device.set_hx_v2_auto_save(0), 0)
        self.assertEqual(device.set_hx_v2_lcd_off_time(7).name, 'NEVER')
        self.assertEqual(device.set_hx_v2_return_to_status_time(3).name, 'T_1m')
        self.assertEqual(device.writes, [(0x2f, b'\x80'), (0x35, b'\x07'), (0x36, b'\xfb')])
        with self.assertRaises(ValueError):
            device.set_hx_v2_return_to_status_time(8)

    def test_hx_route_writes_only_register_32_and_verifies(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x32] = 2
        result = device.set_hx_v2_hdmi_output_source(1)
        self.assertEqual(result, SO_Source.HDMI_IN)
        self.assertEqual(device.writes, [(0x32, b'\x01')])
        self.assertEqual(device.CPA.HO_Source, SO_Source.HDMI_IN)

    def test_hx_sdi_route_writes_only_register_31_and_verifies(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x31] = 2
        result = device.set_hx_v2_sdi_output_source(1)
        self.assertEqual(result, SO_Source.HDMI_IN)
        self.assertEqual(device.writes, [(0x31, b'\x01')])
        self.assertEqual(device.CPA.SO_Source, SO_Source.HDMI_IN)

    def test_hx_3g_level_preserves_other_bits(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x2c] = 0x80
        self.assertEqual(device.set_hx_v2_output_3g_b(1), 1)
        self.assertEqual(device.writes, [(0x2c, b'\x81')])
        self.assertEqual(int(device.CPA.OUT_3G_B) & 1, 1)

    def test_hx_output_1_loop_preserves_other_bits(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x2b] = 0x81
        self.assertEqual(device.set_hx_v2_output_1_loop(0), 0)
        self.assertEqual(device.writes, [(0x2b, b'\x80')])
        self.assertEqual(int(device.CPA.Loop_Enable) & 1, 0)

    def test_hx_hdmi_type_preserves_other_bits(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x30] = 0x81
        result = device.set_hx_v2_hdmi_output_type(3)
        self.assertEqual(result.name, 'HDMI_YCbCr_422_2ch')
        self.assertEqual(device.writes, [(0x30, b'\x83')])
        self.assertEqual(bytes(device.CPA)[0x30] & 7, 3)

    def test_hx_reference_preserves_source_and_genlock_bits(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x33] = 0xf9
        result = device.set_hx_v2_scaler_reference(2)
        self.assertEqual(result.name, 'SDI_IN')
        self.assertEqual(device.writes, [(0x33, b'\xfd')])
        self.assertEqual((bytes(device.CPA)[0x33] >> 1) & 3, 2)


    def test_hx_1080i_psf_preserves_other_bits(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x20] = 0x80
        self.assertEqual(device.set_hx_v2_1080i_as_psf(1), 1)
        self.assertEqual(device.writes, [(0x20, b'\x81')])
        self.assertEqual(int(device.CPA.PSFINEnable) & 1, 1)

    def test_hx_flip_preserves_other_bits_and_axis(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x2d] = 0xfc
        self.assertEqual(device.set_hx_v2_flip('horizontal', 1), 1)
        self.assertEqual(device.writes, [(0x2d, b'\xfd')])
        self.assertEqual(device.set_hx_v2_flip('vertical', 1), 1)
        self.assertEqual(device.writes[-1], (0x2d, b'\xff'))
        with self.assertRaises(ValueError):
            device.set_hx_v2_flip('diagonal', 1)

    def test_lx_mode_preserves_other_bits(self):
        device = FakeDevice(DeviceType.CPA_LX, CPA_LX_Registers)
        device.raw[0x37] = 0x80
        result = device.set_lx_output_mode(3)
        self.assertEqual(result, 'HDMI to HDMI and SDI')
        self.assertEqual(device.writes, [(0x37, b'\x83')])

    def test_hx_scaler_format_preserves_other_bits(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x22] = 0x80 | 13
        result = device.set_hx_v2_scaler_output_format(14)
        self.assertEqual(result, 'HD 1920x1080i50')
        self.assertEqual(device.writes, [(0x22, b'\x8e')])

    def test_hx_scaler_source_preserves_other_bits(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x33] = 0x07
        result = device.set_hx_v2_scaler_source(0)
        self.assertEqual(result.name, 'SDI_IN')
        self.assertEqual(device.writes, [(0x33, b'\x06')])

    def test_hx_horizontal_filter_preserves_neighbor_bits(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x2a] = 0xf8
        self.assertEqual(device.set_hx_v2_horizontal_filter(4).name, 'HIGH')
        self.assertEqual(device.writes, [(0x2a, b'\xfc')])

    def test_hx_motion_detect_level_preserves_upper_bits(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x27:0x29] = b'\xa5\xa0'
        self.assertEqual(device.set_hx_v2_motion_detect_level(512), 512)
        self.assertEqual(device.writes, [(0x27, b'\xa6\x00')])
        with self.assertRaises(ValueError):
            device.set_hx_v2_motion_detect_level(1024)

    def test_hx_aspect_writes_preserve_neighboring_choices(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x23] = 0xe0
        device.raw[0x24] = 0xa0
        device.raw[0x25] = 0xa5

        self.assertEqual(device.set_hx_v2_sd_input_aspect(2), 2)
        self.assertEqual(device.set_hx_v2_sd_output_aspect(1), 1)
        self.assertEqual(device.set_hx_v2_input_image_aspect(4), 4)
        self.assertEqual(device.raw[0x25], 0xa4)
        self.assertEqual(device.set_hx_v2_output_image_aspect(2), 2)

        self.assertEqual(device.raw[0x23:0x26], bytes((0xe2, 0xa1, 0x44)))
        self.assertEqual(device.writes, [
            (0x23, b'\xe2'), (0x24, b'\xa1'),
            (0x25, b'\xa4'), (0x25, b'\x44'),
        ])
        with self.assertRaises(ValueError):
            device.set_hx_v2_input_image_aspect(28)
        self.assertEqual(len(device.writes), 4)

    def test_hx_graticule_enable_and_color_writes_preserve_neighbor_bits(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        device.raw[0x50] = 0x80
        device.raw[0x55] = 0x40
        device.raw[0x5a] = 0xc0

        self.assertEqual(device.set_hx_v2_safe_action_graticule(1), 1)
        self.assertEqual(device.set_hx_v2_safe_action_graticule_color(0), 0)
        self.assertEqual(device.set_hx_v2_safe_title_graticule(1), 1)
        self.assertEqual(device.set_hx_v2_safe_title_graticule_color(24), 24)
        self.assertEqual(device.set_hx_v2_centre_cross_graticule(1), 1)
        self.assertEqual(device.set_hx_v2_centre_cross_graticule_color(16), 16)

        self.assertEqual(device.raw[0x50], 0x8f)
        self.assertEqual(device.raw[0x55], 0x7f)
        self.assertEqual(device.raw[0x5a], 0xef)

    def test_hx_graticule_geometry_writes_half_percent_steps(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        setters = (
            (0x52, device.set_hx_v2_safe_action_vertical_start),
            (0x51, device.set_hx_v2_safe_action_horizontal_start),
            (0x53, device.set_hx_v2_safe_action_horizontal_end),
            (0x54, device.set_hx_v2_safe_action_vertical_end),
            (0x56, device.set_hx_v2_safe_title_horizontal_start),
            (0x58, device.set_hx_v2_safe_title_horizontal_end),
            (0x57, device.set_hx_v2_safe_title_vertical_start),
            (0x59, device.set_hx_v2_safe_title_vertical_end),
        )
        for offset, setter in setters:
            self.assertEqual(setter(5.5), 5.5)
            self.assertEqual(device.raw[offset], 11)
        self.assertEqual(device.writes, [(offset, b'\x0b') for offset, _ in setters])
        with self.assertRaises(ValueError):
            device.set_hx_v2_safe_action_horizontal_start(5.25)

    def test_hx_graticule_actions_write_the_observed_geometry_fields(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        self.assertEqual(device.set_hx_v2_graticule_16_9_lb_on_4_3(),
                         (17.5, 82.5, 22.5, 77.5))
        self.assertEqual(device.writes, [
            (0x51, b'\x23'), (0x53, b'\xa5'),
            (0x56, b'-'), (0x58, b'\x9b'),
        ])

        device.writes.clear()
        self.assertEqual(device.set_hx_v2_graticule_4_3_pb_on_16_9(),
                         (17.5, 82.5, 22.5, 77.5))
        self.assertEqual(device.writes, [
            (0x52, b'\x23'), (0x54, b'\xa5'),
            (0x57, b'-'), (0x59, b'\x9b'),
        ])

        device.writes.clear()
        self.assertEqual(device.set_hx_v2_graticule_anamorphic(),
                         (5.0, 95.0, 5.0, 95.0, 10.0, 90.0, 10.0, 90.0))
        self.assertEqual([offset for offset, _ in device.writes],
                         [0x51, 0x53, 0x52, 0x54, 0x56, 0x58, 0x57, 0x59])

    def test_hx_umd_text_is_padded_and_rejects_invalid_input_before_write(self):
        device = FakeDevice(DeviceType.CPA_HX_V2, CPA_HX_V2_Registers)
        self.assertEqual(device.set_hx_v2_umd_text('DECIMATOR'), 'DECIMATOR')
        expected = b'DECIMATOR' + (b' ' * 7)
        self.assertEqual(device.raw[0xc0:0xd0], expected)
        self.assertEqual(device.writes, [(0xc0, expected)])

        for invalid in ('x' * 17, 'café', 'line\nfeed', b'bytes'):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                device.set_hx_v2_umd_text(invalid)
        self.assertEqual(device.writes, [(0xc0, expected)])

    def test_rejects_wrong_device_and_values(self):
        device = FakeDevice(DeviceType.CPA_LX, CPA_LX_Registers)
        with self.assertRaises(ValueError):
            device.set_hx_v2_hdmi_output_source(1)
        with self.assertRaises(ValueError):
            device.set_hx_v2_return_to_status_time(1)
        with self.assertRaises(ValueError):
            device.set_lx_output_mode(True)


if __name__ == '__main__':
    unittest.main()
