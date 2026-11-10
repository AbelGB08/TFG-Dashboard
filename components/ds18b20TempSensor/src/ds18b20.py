"""Minimal DS18B20 reader for the ds18b20TempSensor component."""

import os
from typing import Optional


DEFAULT_ROOT = "/sys/bus/w1/devices"


def read_temperature(sensor_id: str, root: str = DEFAULT_ROOT) -> Optional[float]:
    """Read a DS18B20 temperature in degrees Celsius.

    Returns ``None`` if the sensor cannot be read.
    """
    sensor_file = os.path.join(root, sensor_id, "w1_slave")
    try:
        with open(sensor_file, "r", encoding="utf-8") as handle:
            lines = handle.readlines()

        # A valid w1_slave file ends its first line with YES.  The second
        # line contains the raw value in millidegrees Celsius.
        if not lines or "YES" not in lines[0]:
            return None

        temperature_data = lines[1].split("=")[1]
        return float(temperature_data) / 1000.0
    except (OSError, IndexError, ValueError):
        return None
