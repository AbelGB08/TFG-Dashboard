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

import logging
import re

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from rich.console import Console
from genericworker import *
import interfaces as ifaces

sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, configData, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map, configData)
        self.Period = configData["Period"]["Compute"]
        self.sensors = []

        if startup_check:
            self.startup_check()
        else:
            self.init_sensors(configData.get("Sensors", {}))
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)

    def __del__(self):
        """Destructor"""

    def init_sensors(self, sensor_config):
        """Initialise the INA226 devices described in the config file."""
        try:
            from src.ina226 import INA226
        except ImportError:
            try:
                from ina226 import INA226
            except ImportError as exc:
                console.log(f"[INA226Sensor] Cannot import the INA226 driver: {exc}")
                return

        busnum = int(sensor_config.get("bus", 1))
        shunt_ohms = float(sensor_config.get("shunt_ohms", 0.002))
        max_expected_amps = float(sensor_config.get("max_expected_amps", 20))

        for name, settings in sensor_config.items():
            if not re.fullmatch(r"INA[0-9]+", name):
                continue
            if not isinstance(settings, dict) or "address" not in settings:
                console.log(f"[INA226Sensor] Missing address for {name}; skipping")
                continue

            try:
                sensor = INA226(
                    busnum=busnum,
                    address=int(settings["address"]),
                    max_expected_amps=max_expected_amps,
                    shunt_ohms=shunt_ohms,
                    log_level=logging.ERROR,
                )
                sensor.configure()
                self.sensors.append((name, sensor))
                console.log(f"[INA226Sensor] {name} initialised at 0x{int(settings['address']):02x}")
            except Exception as exc:
                console.log(f"[INA226Sensor] Cannot initialise {name}: {exc}")

        if not self.sensors:
            console.log("[INA226Sensor] No sensors initialised; check Sensors.* in etc/config")

    @QtCore.Slot()
    def compute(self):
        powers = self.readData()
        if not powers:
            return True

        try:
            self.robotstatuspub_proxy.powerState(powers)
        except Exception as exc:
            console.log(f"[INA226Sensor] Error publishing powerState: {exc}")

        return True

    def readData(self):
        """Read all configured INA226 devices and build a PowersMap."""
        powers = {}

        for name, sensor in self.sensors:
            try:
                if not sensor.is_conversion_ready():
                    continue

                power = ifaces.RoboCompRobotStatusPub.PowerData()
                power.voltage = float(sensor.voltage())
                # The driver returns mA; the dashboard stores A.
                power.current = float(sensor.current()) / 1000.0
                powers[name] = power
            except Exception as exc:
                console.log(f"[INA226Sensor] Error reading {name}: {exc}")

        return powers

    def startup_check(self):
        print("Testing RoboCompRobotStatusPub.PowerData from ifaces.RoboCompRobotStatusPub")
        test = ifaces.RoboCompRobotStatusPub.PowerData()
        QTimer.singleShot(200, QtCore.QCoreApplication.instance().quit)


######################
# From the RoboCompRobotStatusPub you can publish calling this methods:
# RoboCompRobotStatusPub.void self.robotstatuspub_proxy.powerState(PowersMap powers)
# RoboCompRobotStatusPub.void self.robotstatuspub_proxy.thermalState(ThermalMap temperatures)

######################
# From the RoboCompRobotStatusPub you can use this types:
# ifaces.RoboCompRobotStatusPub.PowerData
