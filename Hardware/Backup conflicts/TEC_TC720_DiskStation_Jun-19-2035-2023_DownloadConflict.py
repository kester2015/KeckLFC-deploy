from .Device import Device

import time
import numpy as np
from collections import deque
import warnings


class TEC_TC720(Device):
    def __init__(self, addr, name='TC720 Temp Controller', **kwargs):
        super().__init__(addr=addr, name=name, **kwargs)

        self.inst.timeout = 25000  # communication time-out time set in units of ms
        self.inst.baud_rate = 230400  # baud rate is 9600 by default. THIS SETTING IS NECESSARY for success communication
        self.inst.read_termination = '\r\n'  # read_termination is not specified by default.
        self.inst.write_termination = '\r\n'  # write_termination is '\r\n' by default.
        self.inst.baud_rate = 230400
        self.inst.data_bits = 8
        self.inst.stop_bits = constants.StopBits.one
        self.inst.parity = constants.Parity.none
        self.inst.timeout = 2000
        self.inst.read_termination = '\r'
        self.inst.write_termination = '\r'
        
        self._setpoint = 0
        self._temperature = 0
        self._current = 0
        self._voltage = 0
        self._power = 0
        self._status = 0
        self._error = 0

    def get_setpoint(self):
        return self._setpoint

    def set_setpoint(self, setpoint):
        self._setpoint = setpoint
        self._write('setpoint', setpoint)

    def get_temperature(self):
        return self._temperature

    def get_current(self):
        return self._current

    def get_voltage(self):
        return self._voltage

    def get_power(self):
        return self._power

    def get_status(self):
        return self._status

    def get_error(self):
        return self._error

    def _update(self):
        self._setpoint = self._read('setpoint')
        self._temperature = self._read('temperature')
        self._current = self._read('current')
        self._voltage = self._read('voltage')
        self._power = self._read('power')
        self._status = self._read('status')
        self._error = self._read('error')