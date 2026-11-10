# ds18b20TempSensor

RoboComp component that reads the four DS18B20 body-temperature sensors and
publishes them through the `RobotStatusPub` IceStorm topic.

## Dependencies

- RoboComp (CMake helpers, `ConfigLoader`, IceStorm)
- Python 3, `PySide6`, `rich`, `Ice`
- Linux `w1`/`wire1` support for DS18B20

## Configuration

The component reads `etc/config`:

```ini
Sensors.root = "/sys/bus/w1/devices"
Sensors.base = "28-3ce104571023"
Sensors.chimenea = "28-3ce104571b69"
Sensors.exterior = "28-3ce10457c7cf"
Sensors.bandeja = "28-3ce10457e22d"
Period.Compute = 2000
```

The device IDs can be obtained with:

```bash
ls /sys/bus/w1/devices/
```

The period should be at least 1000 ms; the DS18B20 conversion can take up to
750 ms. Two seconds is a safe default.

## Published data

```text
thermalState({
  "base": 21.3,
  "chimenea": 34.8,
  "exterior": 15.2,
  "bandeja": 22.1
})
```

If a sensor cannot be read, it is omitted from the map and the dashboard does
not store an incomplete body-temperature row.

## Build and run

```bash
cmake . && make
rcnode
bin/ds18b20TempSensor etc/config
```
