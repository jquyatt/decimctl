import unittest
from decimctl import DeviceType, status_snapshot
from decimctl.protocol import SO_Source, DUC_Source


class StatusSnapshotTests(unittest.TestCase):
    def test_model_specific_status_fields(self):
        class Registers:
            version_major = 2
            version_minor = 0
            Input1Status = "Unlocked"
            Input2Status = "3G-A 1920x1080p60"
            OutputFormat = "HD 1920x1080i59.94"
            SO_Source = SO_Source.SDI_IN
            HO_Source = SO_Source.HDMI_IN
            DUC_Source = DUC_Source.HDMI_IN

        class Device:
            desc = b"MD-HX"
            serial = b"CLD07151"
            device_type = DeviceType.CPA_HX_V2
            registers = Registers()

        snapshot = status_snapshot(Device())
        self.assertEqual(snapshot["inputs"], {
            "1": "Unlocked", "2": "3G-A 1920x1080p60"
        })
        self.assertEqual(snapshot["configured_scaler_output_format"],
                         "HD 1920x1080i59.94")
        self.assertNotIn("output_mode", snapshot)
        self.assertEqual(snapshot["configured_routing"], {
            "sdi_output_source": "SDI_IN",
            "hdmi_output_source": "HDMI_IN",
            "scaler_source": "HDMI_IN",
        })

    def test_lx_snapshot_reads_registers_once(self):
        class Registers:
            version_major = 1
            version_minor = 1
            Input1Status = "Unlocked"
            Input2Status = "3G-A 1920x1080p60"
            OutputMode = "Auto Select"

        class Device:
            desc = b"MD-LX"
            serial = b"LXAEG554"
            device_type = DeviceType.CPA_LX
            reads = 0

            @property
            def registers(self):
                self.reads += 1
                return Registers()

        device = Device()
        snapshot = status_snapshot(device)
        self.assertEqual(device.reads, 1)
        self.assertEqual(snapshot["output_mode"], "Auto Select")
        self.assertNotIn("configured_routing", snapshot)

        reused = status_snapshot(device, Registers())
        self.assertEqual(device.reads, 1)
        self.assertEqual(reused, snapshot)


if __name__ == "__main__":
    unittest.main()
