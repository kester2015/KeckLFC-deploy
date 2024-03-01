import imp
import scipy as sp
from wsapi import *
from .Device import Device
import numpy as np
import matplotlib.pyplot as plt
import copy
import time

#from scipy.interpolate import interp1d


# Finisar Waveshaper
# Follow https://ii-vi.com/use-64-bit-python-3-7-to-control-the-waveshaper-through-the-usb-port/ for connection guide
class Waveshaper(Device):
    c_const = 299792458

    def __init__(self, addr='SN201904', WSname='WS1'):
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

        # Compensation is not actually needed (should=0) after experiment.Aug 8,2022
        # self.__wl_conpensate = -0.25  # wl_conpensate = wsp_wl - AndoOSA_wl, calibrated on Aug.8,2022 by Maodong
        import os
        errcode, _ = ws_create_waveshaper(WSname, os.getenv('APPDATA') + "/WaveManager/wsconfig/" + addr + ".wsconfig")
        self.vaild = errcode >= 0
        if errcode < 0:
            self.error(f"Fail to create the Waveshaper instance: {errcode}")

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
        return beta2

    def set3rdDisper(self, d2, d3, center=1560, centerunit='nm', preview_plot=False):
        if centerunit.upper() == 'NM':
            center = Waveshaper.c_const / center / 1000
        beta2 = (Waveshaper.c_const / center)**2 / (2 * np.pi * Waveshaper.c_const) * (d2 * 1e-3)
        beta3 = (Waveshaper.c_const)**2 / (4 * np.pi * np.pi * center**4) * (d3 * 1e-6)
        self.phase = lambda y: beta2 * ((y - center) * 2 * np.pi)**2 / 2 + beta3 * ((y - center) * 2 * np.pi)**3 / 6

        self.info_phase = f"Set 3rd disper with d2={d2} ps/nm, d3={d3} ps/nm^2, center {center} THz"
        self.info("Waveshaper " + self.info_phase + ".")
        if preview_plot:
            plt.figure(figsize=(6, 3))
            plt.plot(self.freq, [self.phase(x) for x in self.freq])
            plt.xlabel('Freq (THz)')
            plt.ylabel('Phase (Rad)')
            plt.show()
        return beta2, beta3

    # interp phase set by jinhao------------------------------

    def set_interp_phase(self, x_fre, y_phase, center=1560, centerunit='nm', preview_plot=False):
        if centerunit.upper() == 'NM':
            center = Waveshaper.c_const / center / 1000
        from scipy.interpolate import interp1d
        self.phase = interp1d(x_fre, y_phase, kind='cubic', fill_value="extrapolate")

        self.info_phase = f"Set interp phase with center {center} THz"
        self.info("Waveshaper " + self.info_phase + ".")
        if preview_plot:
            plt.figure(figsize=(6, 3))
            plt.plot(self.freq, [self.phase(x) for x in self.freq])
            plt.xlabel('Freq (THz)')
            plt.ylabel('Phase (Rad)')
            plt.show()

    # ------------------------------------------------------------------------

    def setBandPass(self, center=192.175, span=4, unit='thz'):
        if str(unit).casefold() == 'nm':
            startthz = self.__nm2thz(center + span / 2)
            stopthz = self.__nm2thz(center - span / 2)
            center = (startthz + stopthz) / 2
            span = stopthz - startthz
        startf = center - span / 2
        stopf = center + span / 2
        self.info_atten = f"Set atten to BandPass [{startf:.3f}~{stopf:.3f}] THz ([{self.__thz2nm(startf):.3f}~{self.__thz2nm(stopf):.3f}] nm)"
        self.info("Waveshaper " + self.info_atten + ".")
        self.atten = lambda x: 0 if (x < stopf and x > startf) else self.MAX_ATTEN

    def inverseAtten(
            self,
            osa_wl,  # measured on OSA, in nm
            osa_pw,  # measured on OSA, in dBm
            max_atten_db=5,  # Resulted MAXimum attenuation level 
            osa_pw_noise=-30,  # background noise level in dBm
            osa_wl_center=1560,  # pump center wavelength, to calculate FSR_nm, only used when perform_peak_search = True
            osa_wl_FSR=16,  # in GHz, frequency comb FSR, only used when perform_peak_search = True
            bandpass_center=299792458 / 1560 / 1000,
            bandpass_span=None,
            bandpass_unit='thz',
            # perform_center_compensate=True,
            perform_peak_search=True,  # when osa_pw is frequency comb, need 
            plot_peak_search=True):
        osa_wl, osa_pw = osa_wl.flatten(), osa_pw.flatten()
        # if perform_center_compensate:
        #     osa_wl = osa_wl + self.__wl_conpensate
        #     self.info(
        #         self.devicename +
        #         f": inverse Atten BandPass Filter: wl on Waveshaper = wl on OSA + {self.__wl_conpensate:.3f} nm. Change this by self.__wl_conpensate=0.1."
        #     )
        if perform_peak_search:
            FSR_nm = osa_wl_center - 1 / (1 / osa_wl_center + osa_wl_FSR / Waveshaper.c_const)
            wl_increment = np.mean(np.diff(osa_wl))  # wavelength incrementation
            min_distance = FSR_nm / wl_increment  # in unit of (array index counts)
            from scipy.signal import find_peaks
            peak_pos, _ = find_peaks(osa_pw, height=osa_pw_noise, distance=0.9 * min_distance)
            peak_wl, peak_pw = osa_wl[peak_pos], osa_pw[peak_pos]
        else:
            self.warning(
                self.devicename +
                ": inverseAtten: input is spectrum envelop instead of frequency comb, NO peak search is performed.")
            peak_wl, peak_pw = osa_wl[osa_pw > osa_pw_noise], osa_pw[osa_pw > osa_pw_noise]
        if not peak_wl.size > 0:
            raise ValueError(self.devicename + ": inverseAtten: Spectrum to inverse is EMPTY. Try reduce osa_pw_noise.")
        if plot_peak_search:
            plt.figure(figsize=(6, 3))
            plt.plot(osa_wl, osa_pw)
            plt.scatter(peak_wl, peak_pw, color='red')
            plt.xlim([min(peak_wl) - 0.05 * np.ptp(peak_wl), max(peak_wl) + 0.05 * np.ptp(peak_wl)])
            plt.show()
        peak_freq = np.array([self.__nm2thz(wl) for wl in peak_wl]).flatten()
        from scipy.interpolate import interp1d
        atten_intp = interp1d(peak_freq, peak_pw - max(peak_pw) + max_atten_db, bounds_error=False, fill_value=0)

        if (bandpass_center == None) | (bandpass_span == None):
            startf = self.startF
            stopf = self.stopF
            self.info(self.devicename + ": inverse Atten NO BandPass Filter is applied.")
        else:  # center or span is not None, need perform bandPass FIlter
            if str(bandpass_unit).casefold() == 'nm':
                startf = self.__nm2thz(bandpass_center + bandpass_span / 2)
                stopf = self.__nm2thz(bandpass_center - bandpass_span / 2)
            elif str(bandpass_unit).casefold() == 'thz':
                startf = bandpass_center - bandpass_span / 2
                stopf = bandpass_center + bandpass_span / 2
            else:
                raise ValueError(self.devicename + ": inverseAtten: Unrecognized bandpass unit " + str(bandpass_unit) +
                                 ". Should be 'nm'|'thz'")

            # if perform_center_compensate:
            #     centerf, spanf = (startf + stopf) / 2, stopf - startf
            #     centerf_new = self.__nm2thz(self.__thz2nm(centerf) + self.__wl_conpensate)
            #     startf, stopf = centerf_new - spanf / 2, centerf_new + spanf / 2
            #     self.info(
            #         self.devicename +
            #         f": inverse Atten BandPass Filter: center Freq shifted by {centerf_new-centerf:.3f} THz with wl compensation. Disable by pass parameter : perform_center_compensate=False to inverseAtten()"
            #     )
        self.atten = lambda x: (atten_intp(x)
                                if atten_intp(x) > 0 else 0) if (x < stopf and x > startf) else self.MAX_ATTEN
        self.info_atten = f"Set atten to BandPass [{startf:.3f}~{stopf:.3f}] THz ([{self.__thz2nm(startf):.3f}~{self.__thz2nm(stopf):.3f}] nm)"
        self.info_atten = self.info_atten + f"\n Inverse Attenuation is applied with max attenuation {max_atten_db} dB."
        self.info("Waveshaper " + self.info_atten + ".")
        return

    def writeProfile(self, amp=None, phase=None, disable_beep=False):
        if amp is not None:
            if len(amp) != self.numPixels:
                self.error("Invalid amp")
                return
            self.atten = lambda x: amp[int((x - self.startF) * 1000)]
        if phase is not None:
            if len(phase) != self.numPixels:
                self.error("Invalid phase")
                return
            self.phase = lambda x: phase[int((x - self.startF) * 1000)]
        buffer = ''
        for f in self.freq:
            buffer += f"{f:.3f}\t{self.atten(f):.1f}\t{self.phase(f):.6f}\t1\n"
        if self.vaild:
            errcode = ws_load_profile(self.inst, buffer)
            if errcode < 0:
                self.error(f"Waveshaper writing error: {errcode}")
            else:
                self.current_atten = copy.deepcopy(self.atten)
                self.current_phase = copy.deepcopy(self.phase)
                self.info("Waveshaper profile write successful.")
                if not disable_beep:
                    import winsound
                    winsound.Beep(800, 250)
                    winsound.Beep(1000, 250)

    def plotStatus(self, unit='thz'):
        (fig, ((ax1, ax2), (ax3, ax4))) = plt.subplots(2, 2, figsize=(9, 6))
        if str(unit).casefold() == 'thz':
            plot_x = self.freq
            plot_x_label = "Freq (THz)"
        elif str(unit).casefold() == 'nm':
            plot_x = np.array([self.__thz2nm(x) for x in self.freq])
            plot_x_label = "Wavelength (nm)"

        ax1.plot(plot_x, [-self.current_atten(x) for x in self.freq])
        # ax1.set_xlabel("Freq (THz)")
        ax1.set_ylabel("-Atten (dB)")
        ax1.set_title("Current Atten")

        ax2.plot(plot_x, [-self.atten(x) for x in self.freq])
        # ax2.set_xlabel("Freq (THz)")
        # ax2.set_ylabel("-Atten (dB)")
        ax2.set_title("Preview Atten")

        ax3.plot(plot_x, [self.current_phase(x) if self.current_atten(x) < self.MAX_ATTEN else 0 for x in self.freq])
        ax3.set_xlabel(plot_x_label)
        ax3.set_ylabel("Phase (rad)")
        ax3.set_title("Current Phase")

        ax4.plot(plot_x, [self.phase(x) if self.atten(x) < self.MAX_ATTEN else 0 for x in self.freq])
        ax4.set_xlabel(plot_x_label)
        # ax4.set_ylabel("Phase (rad)")
        ax4.set_title("Preview Phase")

    def printStatus(self):
        message = (str(self.devicename) + " Status Summary").center(80, '-') + "\n"
        message += "|\t Atten info: " + self.info_atten + "\n"
        message += "|\t Phase info: " + self.info_phase + "\n"
        self.plotStatus()
        plt.draw()
        self.info(message + (str(self.devicename) + " Status Summary Ends").center(80, '-'))

    def nm2thz(self, nm):
        return self.__nm2thz(nm)

    def thz2nm(self, thz):
        return self.__thz2nm(thz)

    def __nm2thz(self, nm):
        return Waveshaper.c_const / nm / 1000

    def __thz2nm(self, thz):
        return Waveshaper.c_const / thz / 1000
