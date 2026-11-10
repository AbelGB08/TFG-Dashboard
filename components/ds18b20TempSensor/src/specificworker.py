#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#    Copyright (C) 2025 by YOUR NAME HERE
#
#    This file is part of RoboComp
#
#    RoboComp is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    RoboComp is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with RoboComp.  If not, see <http://www.gnu.org/licenses/>.
#

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from rich.console import Console
from genericworker import *
import interfaces as ifaces

try:
    from src.ds18b20 import read_temperature
except ImportError:  # allows running with src/ directly on PYTHONPATH
    from ds18b20 import read_temperature

sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)

TEMPERATURE_KEYS = ("base", "chimenea", "exterior", "bandeja")


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, configData, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map, configData)
        self.Period = configData["Period"]["Compute"]

        sensor_config = configData.get("Sensors", {})
        self.w1_root = sensor_config.get("root", "/sys/bus/w1/devices")
        self.sensor_ids = {
            key: sensor_config[key]
            for key in TEMPERATURE_KEYS
            if key in sensor_config
        }

        if startup_check:
            self.startup_check()
        else:
            if not self.sensor_ids:
                console.log("[ds18b20TempSensor] No Sensors.* entries found in etc/config")
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)

    def __del__(self):
        """Destructor"""

    @QtCore.Slot()
    def compute(self):
        temperatures = self.readData()
        if not temperatures:
            return True

        try:
            self.robotstatuspub_proxy.thermalState(temperatures)
        except Exception as exc:
            console.log(f"[ds18b20TempSensor] Error publishing thermalState: {exc}")

        return True

    def readData(self):
        """Read the configured DS18B20 devices and build a ThermalMap."""
        temperatures = {}

        for key, sensor_id in self.sensor_ids.items():
            temperature = read_temperature(str(sensor_id), self.w1_root)
            if temperature is None:
                console.log(f"[ds18b20TempSensor] Cannot read {key} ({sensor_id})")
                continue
            temperatures[key] = float(temperature)

        return temperatures

    def startup_check(self):
        print("Testing RoboCompRobotStatusPub thermal publication")
        QTimer.singleShot(200, QtCore.QCoreApplication.instance().quit)


######################
# From the RoboCompRobotStatusPub you can publish calling this methods:
# RoboCompRobotStatusPub.void self.robotstatuspub_proxy.powerState(PowersMap powers)
# RoboCompRobotStatusPub.void self.robotstatuspub_proxy.thermalState(ThermalMap temperatures)

######################
# From the RoboCompRobotStatusPub you can use this types:
# ifaces.RoboCompRobotStatusPub.PowerData
