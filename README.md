# decimctl for decimator-net

This fork of [Quentin Smith’s decimctl](https://github.com/quentinmit/decimctl) adds MD-HX V2 and MD-LX controls and status reporting for decimator-net.

This repository contains EXPERIMENTAL code for interfacing with
Decimator Designs products. BUYER BEWARE! It has only received cursory
testing on the MD-HX converter. It's entirely possible for your device
to be BRICKED.

To install, use the standard pip tools (e.g. `pip install .`) and run
the "decimctl" command. Run `decimctl list` to find the serial number of your converter.

For a compact, machine-readable status snapshot, run
`decimctl status --serial SERIAL --json`. The JSON includes the model,
serial, device type, firmware version, decoded input statuses, and any
model-specific output setting currently supported. MD-HX V2 snapshots
also include configured SDI, HDMI, and scaler sources. This is a read-only
command; output settings describe configured values and may differ from
the active signal path.

Python callers can use `decimctl.status_snapshot(device)` with an open
`decimctl.Device`. It reads the device registers once and returns the same
dictionary used by the JSON command.

On a tested MD-HX V2, an open `Device` supports readback-checked setters for
SDI/HDMI output routing, scaler source/reference/output format, output level
and loop, HDMI output type, 1080i-as-PSF, horizontal filter, motion-detect
level, horizontal/vertical flip, test pattern enable/selection, test audio,
overlay destination, input-format status and palette, UMD enable, text and
palette, audio pair routing, audio meters, graticules, SD IN/OUT and IN/OUT
IMAGE ASPECT, Auto Save, LCD off time, and return-to-status time.
`set_hx_v2_graticule_16_9_lb_on_4_3()` applies the observed
Graticules → 16:9 LB on 4:3 action by setting the four horizontal Safe Action
and Safe Title bounds, then verifies readback. Aspect choices follow the
public MD-HX V2 menu order. IN IMAGE
uses the low five bits of its register byte and OUT IMAGE uses the upper three.
Each setter preserves the other aspect field. Enumerated codes
follow the corresponding `decimctl.protocol.CPA_HX_V2_*` option tuples; boolean
settings accept `0` or `1`. On MD-LX, `set_lx_output_mode(0..3)` sets the output
routing mode. Each method writes only the mapped register bits, preserves
neighboring bits, and reads the value back before returning. These methods
require exclusive access to the device; close UCP before using them.

## Tests

Install the package and its `pylibftdi` dependency, then run
`python -m unittest discover -s tests -v`. The test suite uses fake register
buffers and does not open USB devices.
