import imp
from wsapi import *
from .Device import Device
import numpy as np
import matplotlib.pyplot as plt
import copy
import time


# Finisar Waveshaper
# Follow https://ii-vi.com/use-64-bit-python-3-7-to-control-the-waveshaper-through-the-usb-port/ for connection guide
class Waveshaper(Device):
    c_const = 299792458

    def __init__(self, addr='', WSname='WS1'):
        super().__init__(addr=addr, name='Finisar Waveshaper ' + addr, isVISA=False)
        self.inst = WSname
        self.MAX_ATTEN = 60

        self.atten = lambda x: 0
        self.phase = lambda x: 0
        self.current_atten = lambda x: self.MAX_ATTEN
        self.current_phase = lambda x: 0
        self.info_atten = ''
        self.info_phase = ''
        self.startF = 191.25  # in THz, will update when connect
        self.stopF = 196.275  # in THz, will update when connect
        self.freq = np.arange(self.startF, self.stopF, 0.001)
        import os
        errcode, _ = ws_create_waveshaper(WSname, os.getenv('APPDATA') + "/WaveManager/wsconfig/" + addr + ".wsconfig")
        self.vaild = errcode >= 0
        if errcode < 0:
            print(f"Fail to create the Waveshaper instance: {errcode}")

    def connect(self):
        if self.vaild and not self.connected:
            WSname = self.inst
            errcode = ws_open_waveshaper(WSname)
            if errcode < 0:
                ws_delete_waveshaper(WSname)
                return errcode
            else:
                self.startF = ws_get_startfreq(WSname)
                self.stopF = ws_get_stopfreq(WSname)
                self.freq = np.arange(self.startF, self.stopF, 0.001)
                self.numPixels = len(self.freq)
                return super().connect()
        return 0

    def disconnect(self):
        if self.vaild and self.connected:
            WSname = self.inst
            errcode = ws_close_waveshaper(WSname)
            ws_delete_waveshaper(WSname)
            if errcode < 0:
                return errcode
            else:
                return super().disconnect()
        return 0

    def set2ndDisper(self, d2, center=1560, centerunit='nm', preview_plot=False):
        if centerunit.upper() == 'NM':
            center = Waveshaper.c_const / center / 1000
        beta2 = (Waveshaper.c_const / center)**2 / (2 * np.pi * Waveshaper.c_const) * (d2 * 1e-3)
        self.phase = lambda y: beta2 * ((y - center) * 2 * np.pi)**2 / 2

        self.info_phase = f"Set 2nd disper with d2={d2} ps/nm, center {center} THz"
        if preview_plot:
            plt.figure(figsize=(6, 3))
            plt.plot(self.freq, [self.phase(x) for x in self.freq])
            plt.xlabel('Freq (THz)')
            plt.ylabel('Phase (Rad)')
            plt.show()

    def set3rdDisper(self, d2, d3, center=1560, centerunit='nm', preview_plot=False):
        if centerunit.upper() == 'NM':
            center = Waveshaper.c_const / center / 1000
        beta2 = (Waveshaper.c_const / center)**2 / (2 * np.pi * Waveshaper.c_const) * (d2 * 1e-3)
        beta3 = (Waveshaper.c_const)**2 / (4 * np.pi * np.pi * center**4) * (d3 * 1e-6)
        self.phase = lambda y: beta2 * ((y - center) * 2 * np.pi)**2 / 2 + beta3 * ((y - center) * 2 * np.pi)**3 / 6

        self.info_phase = f"Set 3rd disper with d2={d2} ps/nm, d3={d3} ps/nm^2, center {center} THz"
        if preview_plot:
            plt.figure(figsize=(6, 3))
            plt.plot(self.freq, [self.phase(x) for x in self.freq])
            plt.xlabel('Freq (THz)')
            plt.ylabel('Phase (Rad)')
            plt.show()

    def setBandPass(self, center=192.175, span=4, unit='thz'):
        if str(unit).casefold() == 'nm':
            startthz = self.__nm2thz(center + span / 2)
            stopthz = self.__nm2thz(center - span / 2)
            center = (startthz + stopthz) / 2
            span = stopthz - startthz
        startf = center - span / 2
        stopf = center + span / 2
        self.info_atten = f"Set atten to BandPass [{startf}~{stopf}] THz ([{self.__thz2nm(startf):.3f}~{self.__thz2nm(stopf):.3f}] nm)"
        print("Waveshaper " + self.info_atten + ".")
        self.atten = lambda x: 0 if (x < stopf and x > startf) else self.MAX_ATTEN

    def inverseAtten(self,
                     osa_wl, # measured on OSA, in nm
                     osa_pw, # measured on OSA, in dBm
                     max_atten_db = 10, # Resulted MAXimum attenuation level 
                     osa_wl_center = 1560, # pump center wavelength
                     osa_pw_noise = -48, # background noise level in dBm
                     osa_wl_FSR = 16, # GHz
                     bandpass_center = 1560,
                     bandpass_span = None,
                     bandpass_unit = 'nm',
                     plot_peak_search=True):
        FSR_nm = osa_wl_center-1/(1/osa_wl_center+osa_wl_FSR/Waveshaper.c_const)
        wl_increment = np.mean(np.diff(osa_wl.flatten())) # wavelength incrementation
        min_distance = FSR_nm/wl_increment # in unit of (array index counts)
        from scipy.signal import find_peaks
        peak_pos, _ = find_peaks(osa_pw.flatten(),height=osa_pw_noise,distance=0.9*min_distance)
        peak_wl, peak_pw = osa_wl[peak_pos],osa_pw[peak_pos]
        if plot_peak_search:
            plt.figure(figsize=(6, 3))
            plt.plot(osa_wl, osa_pw)
            plt.scatter(peak_wl, peak_pw,color='red')
            plt.xlim([min(peak_wl)-0.05*np.ptp(peak_wl), max(peak_wl)+0.05*np.ptp(peak_wl)])
            plt.show()
        peak_freq = 
        from scipy.interpolate import interp1d
        peak_intp = 
        
        if (bandpass_center==None) | (bandpass_span==None):
            startf = self.startF
            stopf = self.stopF
            print(self.devicename+": inverse Atten NO BandPass Filter is applied.")
        else:
            if str(bandpass_unit).casefold()=='nm':
                startf = self.__nm2thz(bandpass_center+bandpass_span/2)
                stopf = self.__nm2thz(bandpass_center-bandpass_span/2)
            elif str(bandpass_unit).casefold()=='thz':
                startf = bandpass_center-bandpass_span/2
                stopf = bandpass_center+bandpass_span/2
            else:
                raise ValueError(self.devicename+": inverseAtten: Unrecognized bandpass unit "+ str(bandpass_unit)+". Should be 'nm'|'thz'")
        

        self.info_atten = f"Set atten to BandPass [{startf}~{stopf}] THz ([{self.__thz2nm(startf):.3f}~{self.__thz2nm(stopf):.3f}] nm)"
        print("Waveshaper " + self.info_atten + ".")
        return

    def writeProfile(self, amp=None, phase=None):
        if amp is not None:
            if len(amp) != self.numPixels:
                print("Invalid amp")
                return
            self.atten = lambda x: amp[int((x - self.startF) * 1000)]
        if phase is not None:
            if len(phase) != self.numPixels:
                print("Invalid phase")
                return
            self.phase = lambda x: phase[int((x - self.startF) * 1000)]
        buffer = ''
        for f in self.freq:
            buffer += f"{f:.3f}\t{self.atten(f):.1f}\t{self.phase(f):.6f}\t1\n"
        if self.vaild:
            errcode = ws_load_profile(self.inst, buffer)
            if errcode < 0:
                print(f"Waveshaper writing error: {errcode}")
            else:
                self.current_atten = copy.deepcopy(self.atten)
                self.current_phase = copy.deepcopy(self.phase)
                print("Waveshaper profile write successful.")

    def plotStatus(self):
        (fig, ((ax1, ax2), (ax3, ax4))) = plt.subplots(2, 2, figsize=(9, 6))
        ax1.plot(self.freq, [-self.current_atten(x) for x in self.freq])
        # ax1.set_xlabel("Freq (THz)")
        ax1.set_ylabel("-Atten (dB)")
        ax1.set_title("Current Atten")

        ax2.plot(self.freq, [-self.atten(x) for x in self.freq])
        # ax2.set_xlabel("Freq (THz)")
        # ax2.set_ylabel("-Atten (dB)")
        ax2.set_title("Preview Atten")

        ax3.plot(self.freq, [self.current_phase(x) if self.current_atten(x) < self.MAX_ATTEN else 0 for x in self.freq])
        ax3.set_xlabel("Freq (THz)")
        ax3.set_ylabel("Phase (rad)")
        ax3.set_title("Current Phase")

        ax4.plot(self.freq, [self.phase(x) if self.atten(x) < self.MAX_ATTEN else 0 for x in self.freq])
        ax4.set_xlabel("Freq (THz)")
        # ax4.set_ylabel("Phase (rad)")
        ax4.set_title("Preview Phase")

    def printStatus(self):
        print((str(self.devicename) + " Status Summary").center(80, '-'))
        print("|\t Atten info: " + self.info_atten)
        print("|\t Phase info: " + self.info_phase)
        self.plotStatus()
        plt.draw()
        print((str(self.devicename) + " Status Summary Ends").center(80, '-'))

    def __nm2thz(self, nm):
        return Waveshaper.c_const / nm / 1000

    def __thz2nm(self, thz):
        return Waveshaper.c_const / thz / 1000
