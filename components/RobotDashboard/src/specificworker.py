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

import re
import threading

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from rich.console import Console
from genericworker import *
import interfaces as ifaces

sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)

BODY_TEMPERATURE_KEYS = {"base", "chimenea", "exterior", "bandeja"}


def _normalize_key(key) -> str:
    return str(key).strip().lower().replace("-", "_")


def _ina_sensor_name(key):
    """Return ``INA<n>`` for keys such as INA1, ina_1 or ina/1."""
    normalized = _normalize_key(key)
    match = re.fullmatch(r"ina[_\s/]*([1-9][0-9]*)", normalized)
    return f"INA{match.group(1)}" if match else None


def _is_victron(key) -> bool:
    return "victron" in _normalize_key(key)


def _sbc_channel(key):
    """Return the 1..4 channel index for an SBC current key."""
    normalized = _normalize_key(key)
    patterns = (
        r"sbc[_\s/]*(?:amps?[_\s/]*)?([1-4])",
        r"amps?[_\s/]*([1-4])",
    )
    for pattern in patterns:
        match = re.fullmatch(pattern, normalized)
        if match:
            return int(match.group(1))
    return None


def _sbt_channel(key):
    """Return the 1..4 channel index for an SBT temperature key."""
    normalized = _normalize_key(key)
    patterns = (
        r"sbt[_\s/]*(?:temp(?:erature)?[_\s/]*)?([1-4])",
        r"temp(?:erature)?[_\s/]*([1-4])",
    )
    for pattern in patterns:
        match = re.fullmatch(pattern, normalized)
        if match:
            return int(match.group(1))
    return None


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, configData, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map, configData)
        self.Period = configData["Period"]["Compute"]

        self._buffer_lock = threading.Lock()
        self._body_temperature_buffer = {}
        self._sbc_buffer = {}
        self._sbt_buffer = {}
        self._unknown_keys = set()

        if startup_check:
            self.startup_check()
        else:
            # Imported here so ``--startup-check`` does not need Flask.
            try:
                from src import dashboard_app
            except ImportError:  # allows running with src/ directly on PYTHONPATH
                import dashboard_app

            web_config = configData.get("Web", {})
            host = web_config.get("Host", "0.0.0.0")
            port = int(web_config.get("Port", 5000))
            console.log(f"Starting RobotDashboard web server on {host}:{port}")
            dashboard_app.start_server(host=host, port=port)

    def __del__(self):
        """Destructor"""

    @QtCore.Slot()
    def compute(self):
        # The dashboard is event driven: data arrives through IceStorm
        # subscriptions, so there is no periodic task.
        return True

    def _warn_unknown_key(self, message: str, key) -> None:
        normalized = _normalize_key(key)
        if normalized not in self._unknown_keys:
            self._unknown_keys.add(normalized)
            console.log(f"[RobotDashboard] {message}: {key!r}")

    def startup_check(self):
        print("Testing RoboCompRobotStatusPub.PowerData from ifaces.RoboCompRobotStatusPub")
        test = ifaces.RoboCompRobotStatusPub.PowerData()
        QTimer.singleShot(200, QtCore.QCoreApplication.instance().quit)

    # =============== Methods for Component SubscribesTo ================
    # ===================================================================

    #
    # SUBSCRIPTION to powerState method from RobotStatusPub interface
    #
    def RobotStatusPub_powerState(self, powers):
        if powers is None:
            return

        for key, power in powers.items():
            # PowerData is defined by RobotStatusPub.idsl.  The fallback to
            # "voltaje" keeps compatibility with the first generated version.
            voltage = getattr(power, "voltage", getattr(power, "voltaje", 0.0))
            current = getattr(power, "current", 0.0)

            ina_name = _ina_sensor_name(key)
            if ina_name:
                dashboard_app.store_power(ina_name, voltage, current)
                continue

            if _is_victron(key):
                dashboard_app.store_victron(voltage, current)
                continue

            channel = _sbc_channel(key)
            if channel:
                with self._buffer_lock:
                    self._sbc_buffer[channel] = current
                    complete = len(self._sbc_buffer) == 4
                    values = dict(self._sbc_buffer) if complete else None
                    if complete:
                        self._sbc_buffer.clear()
                if values:
                    dashboard_app.store_sbc(values)
                continue

            self._warn_unknown_key("Ignoring unknown power key", key)

    #
    # SUBSCRIPTION to thermalState method from RobotStatusPub interface
    #
    def RobotStatusPub_thermalState(self, temperatures):
        if temperatures is None:
            return

        for key, temperature in temperatures.items():
            normalized = _normalize_key(key)

            if normalized in BODY_TEMPERATURE_KEYS:
                with self._buffer_lock:
                    self._body_temperature_buffer[normalized] = temperature
                    complete = len(self._body_temperature_buffer) == 4
                    values = dict(self._body_temperature_buffer) if complete else None
                    if complete:
                        self._body_temperature_buffer.clear()
                if values:
                    dashboard_app.store_temperatures(values)
                continue

            channel = _sbt_channel(key)
            if channel:
                with self._buffer_lock:
                    self._sbt_buffer[channel] = temperature
                    complete = len(self._sbt_buffer) == 4
                    values = dict(self._sbt_buffer) if complete else None
                    if complete:
                        self._sbt_buffer.clear()
                if values:
                    dashboard_app.store_sbt(values)
                continue

            self._warn_unknown_key("Ignoring unknown thermal key", key)


# ===================================================================
# ===================================================================


######################
# From the RoboCompRobotStatusPub you can use this types:
# ifaces.RoboCompRobotStatusPub.PowerData
