
import time

from .Device import Device
import numpy as np
import matplotlib.pyplot as plt
import os
import threading




class YOKOGAWAaq6375(Device):

    def __init__(self, addr='GPIB0::1::INSTR', name="YOKOGAWA AQ6375"):
        super().__init__(addr=addr, name=name)

        self.__activation_timeout = 3  # time to wait for device to turn on/off activation and channel status. in unit of second.
        self.inst.timeout = 25000  # communication time-out time set in units of ms
        self.inst.baud_rate = 19200  # baud rate is 9600 by default. THIS SETTING IS NECESSARY for success communication
        self.inst.read_termination = ''  # read_termination is not specified by default.
        self.inst.write_termination = ''  # write_termination is '\r\n' by default.
        self.osaacquiring = False

    def set_resolution(self, resolution_nm):
        self.write(f':SENSE:BANDWIDTH:RESOLUTION {resolution_nm}NM')

    def set_wavelenth_center(self, wavelength_center_nm):
        self.write(f':SENSE:WAVELENGTH:CENTER {wavelength_center_nm}NM')
    
    def set_wavelength_span(self, wavelength_span_nm):
        self.write(f':SENSE:WAVELENGTH:SPAN {wavelength_span_nm}NM')

    def set_wavelength_start(self, wavelength_start_nm):
        self.write(f':SENSE:WAVELENGTH:START {wavelength_start_nm}NM')
    
    def set_wavelength_stop(self, wavelength_stop_nm):
        self.write(f':SENSE:WAVELENGTH:STOP {wavelength_stop_nm}NM')

    def set_sensitivity(self, sensitivity):
        self.write(f':SENSE:SENSE {sensitivity}')

    def set_sampling_step(self, sampling_step_nm):
        self.write(f':SENSE:SWEEP:STEP {sampling_step_nm}NM')

    def set_sample_points(self, sample_points):
        self.write(f':SENSE:SWEEP:POINTS {sample_points}')
    
    def get_sample_points(self):
        return self.query(':SENSE:SWEEP:POINTS?')

    def get_sensitivity(self):
        sensitivity = int(self.query(':SENSE:SENSE?'))
        if sensitivity == 0:
            return 'NHLD'
        elif sensitivity == 1:
            return 'NAUT'
        elif sensitivity == 2:
            return 'MID'
        elif sensitivity == 3:
            return 'HIGH1'
        elif sensitivity == 4:
            return 'HIGH2'
        elif sensitivity == 5:
            return 'HIGH3'
        elif sensitivity == 6:
            return 'NORMAL'
    
    def get_resolution(self):
        return self.query(':SENSE:BANDWIDTH:RESOLUTION?')

    def get_wavelength_center(self):
        return self.query(':SENSE:WAVELENGTH:CENTER?')
    
    def get_wavelength_span(self):
        return self.query(':SENSE:WAVELENGTH:SPAN?')

    def get_wavelength_start(self):
        return self.query(':SENSE:WAVELENGTH:START?')
    
    def get_wavelength_stop(self):
        return self.query(':SENSE:WAVELENGTH:STOP?')
    
    def get_sampling_step(self):
        return self.query(':SENSE:SWEEP:STEP?')
    
    def get_Xdata(self, trace):
        xdata_list = self.query(f'TRACE:X? {trace}').strip().split(',')
        return np.asarray(xdata_list, 'f')
    
    def get_Ydata(self, trace):
        ydata_list = self.query(f'TRACE:Y? {trace}').strip().split(',')
        return np.asarray(ydata_list, 'f')
    
    def get_trace(self, trace):
        xdata = self.get_Xdata(trace)
        ydata = self.get_Ydata(trace)
        return xdata, ydata
    
    def single(self):
        self.write(":INITiate:SMODe SINGle")
        self.write(":INITiate")

    def stop(self):
        self.write(":ABOR")


if __name__ == '__main__':

    pass







