# INA226Sensor

RoboComp component that reads the INA226 power monitors and publishes them
through the `RobotStatusPub` IceStorm topic.

## Dependencies

- RoboComp (CMake helpers, `ConfigLoader`, IceStorm)
- Python 3, `PySide6`, `rich`, `Ice`
- `smbus2` on the Raspberry Pi

## Configuration

The component reads `etc/config`. The I2C devices are configured with dotted
keys:

```ini
Sensors.bus = 1
Sensors.shunt_ohms = 0.002
Sensors.max_expected_amps = 20
Sensors.INA1.address = 64
Sensors.INA2.address = 65
Sensors.INA3.address = 66
Sensors.INA4.address = 67
Sensors.INA5.address = 68
Period.Compute = 1000
```

Addresses are decimal: `0x40 = 64` ... `0x44 = 68`.

## Published data

The component calls:

```text
powerState({
  "INA1": PowerData(voltage=24.1, current=1.8),
  ...
})
```

- `voltage` is in volts.
- `current` is in amperes.
- The dashboard computes `pow = voltage * current`.

## Build and run

```bash
pip install -r requirements.txt   # smbus2
cmake . && make
rcnode
bin/INA226Sensor etc/config
```

If `RobotStatusPub.idsl` is not installed, copy it to
`$ROBOCOMP/interfaces/IDSLs/` or add its directory to `SLICE_PATH`.
