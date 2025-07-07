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

sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, configData, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map, configData)
        self.Period = configData["Period"]["Compute"]
        print(configData["address"])
        if startup_check:
            self.startup_check()
        else:
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)

    def __del__(self):
        """Destructor"""


    @QtCore.Slot()
    def compute(self):
        print('SpecificWorker.compute...')
        self.robotstatuspub_proxy.thermalState(self.readData())

        return True
    
    def readData(self):
        """Read data from sensors or other sources"""
        # Example of creating a Temperature object
        ret = {}
        for i in range(2):
            ret[f"temp{i}"] = 8.2
        return ret

    def startup_check(self):
        print(f"Testing RoboCompRobotStatusPub.PowerData from ifaces.RoboCompRobotStatusPub")
        test = ifaces.RoboCompRobotStatusPub.PowerData()
        QTimer.singleShot(200, QApplication.instance().quit)





    ######################
    # From the RoboCompRobotStatusPub you can publish calling this methods:
    # RoboCompRobotStatusPub.void self.robotstatuspub_proxy.powerState(PowersMap powers)
    # RoboCompRobotStatusPub.void self.robotstatuspub_proxy.thermalState(ThermalMap temperatures)

    ######################
    # From the RoboCompRobotStatusPub you can use this types:
    # ifaces.RoboCompRobotStatusPub.PowerData


