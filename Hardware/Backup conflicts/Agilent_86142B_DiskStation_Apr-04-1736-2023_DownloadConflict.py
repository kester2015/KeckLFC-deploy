import warnings
import time

from .Device import Device
import numpy as np
import matplotlib.pyplot as plt
import os
import threading
''' Author: Maodong Gao, version 0.0, Dec 03 2021 '''
''' PLEASE FOLLOW camelCase Convention to maintain '''
''' Adapted from https://github.com/kester2015/ANDO_control/blob/main/osa_control.py '''


class AndoOSA_AQ6315E(Device):

    def __init__(self, addr='GPIB0::30::INSTR', name="Agilent 86142B"):
        super().__init__(addr=addr, name=name)
        self.__available_traces = ['A', 'B', 'C', 'D', 'E', 'F']
        self.__available_sensitivity = ['norm', 'high1', 'high2', 'high3']
        self.__activation_timeout = 3  # time to wait for device to turn on/off activation and channel status. in unit of second.
        self.inst.timeout = 25000  # communication time-out time set in units of ms
        self.inst.baud_rate = 19200  # baud rate is 9600 by default. THIS SETTING IS NECESSARY for success communication
        self.inst.read_termination = '\r\n'  # read_termination is not specified by default.
        self.inst.write_termination = '\r\n'  # write_termination is '\r\n' by default.
        self.osaacquiring = False

    def printStatus(self):

        def highlight_status(status_string):
            """Color refer https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal"""
            if status_string in ['UNLOCKED', 'ON']:  # Show a green color
                return "\x1b[1;34;42m" + status_string + "\x1b[0m"
            elif status_string in ['LOCKED', 'OFF']:  # Show a red color
                return "\x1b[1;34;41m" + status_string + "\x1b[0m"
            else:
                return status_string

        message = str(self.devicename).center(81, '-') + "\n"
        message = message + "|" + "ANDO AQ-6315 Optical Spectrum Analyzer Status Summary".center(80, '-') + "\n"

        message = message + "ANDO AQ-6315 Optical Spectrum Analyzer Status Summary Ends".center(80, '-') + "\n"
        print(message)
        return message

    @property
    def resolution(self):
        return self.get_resolution()

    @resolution.setter
    def resolution(self, res):
        self.set_resolution(res)

    @property
    def reflevel(self):
        return self.get_reflevel()

    @reflevel.setter
    def reflevel(self, reflevel):
        self.set_reflevel(reflevel)

    @property
    def wlstart(self):
        return self.get_wlstart()

    @wlstart.setter
    def wlstart(self, wl):
        self.set_wlstart(wl)

    @property
    def wlstop(self):
        return self.get_wlstop()

    @wlstop.setter
    def wlstop(self, wl):
        self.set_wlstop(wl)

    @property
    def wlspan(self):
        return self.get_wlspan()

    @wlspan.setter
    def wlspan(self, wl):
        self.set_wlspan(wl)

    @property
    def wlcenter(self):
        return self.get_wlcenter()

    @wlcenter.setter
    def wlcenter(self, wl):
        self.set_wlcenter(wl)

    # --------------------------------- OSA Functions --------------------------------- #

    def get_reflevel(self):
        return float(self.query('DISP:WIND:TRAC:Y:SCAL:RLEV?'))

    def set_reflevel(self, reflevel):
        reflevel = float(reflevel)
        self.write(f'DISP:WIND:TRAC:Y:SCAL:RLEV {reflevel:.1f}')        #   here is write not query
        reflevel = self.get_reflevel()
        print(self.devicename + f": Reference level set to {reflevel:.1f} dBm.")

    def get_wlstart(self):
        return float(self.query('SENS:WAV:STAR?'))

    def set_wlstart(self, wlstart):
        wlstart = float(wlstart)
        self.write(f'SENS:WAV:STAR {wlstart:.2f}nm')
        wlstart = self.get_wlstart()
        print(self.devicename + f": Scan start wavelength set to {wlstart:.2f} nm.")

    def get_wlstop(self):
        return float(self.query('SENS:WAV:STOP?'))

    def set_wlstop(self, wlstop):
        wlstop = float(wlstop)
        self.write(f'SENS:WAV:STOP {wlstop:.2f}nm')       #   here is write not query ,also need nm
        wlstop = self.get_wlstop()
        print(self.devicename + f": Scan stop wavelength set to {wlstop:.2f} nm.")

    def get_wlspan(self):
        return self.get_wlstop() - self.get_wlstart()

    def set_wlspan(self, wlspan):
        wlspan = float(wlspan)
        wlcenter = self.get_wlcenter()
        wlstart_new = wlcenter - wlspan / 2
        wlstop_new = wlcenter + wlspan / 2
        self.set_wlstart(wlstart_new)
        self.set_wlstop(wlstop_new)
        print(self.devicename + f": Scan span wavelength set to {wlspan:.2f} nm.")

    def get_wlcenter(self):
        return (self.get_wlstop() + self.get_wlstart()) / 2

    def set_wlcenter(self, wlcenter):
        wlcenter = float(wlcenter)
        wlspan = self.get_wlspan()
        wlstart_new = wlcenter - wlspan / 2
        wlstop_new = wlcenter + wlspan / 2
        self.set_wlstart(wlstart_new)
        self.set_wlstop(wlstop_new)
        print(self.devicename + f": Scan center wavelength set to {wlcenter:.2f} nm.")

    def get_resolution(self):
        return float(self.query('SENS:BAND:RES?'))

    def set_resolution(self, res):
        res = float(res)
        self.write(f'SENS:BAND:RES {res:.2f}')
        res= float(self.query('SENS:BAND:RES?'))
        print(self.devicename + f": Resolution set to {res:.2f} nm.")

    def Run(self):
        self.write('INIT:CONT 1')  # equivlant to repeat softkey
        print(self.devicename + ": Spectrum collection RUN (repeat) start.")   #   how to query the status?

    def Single(self):
        self.write('INIT:IMM')  # equivlant to repeat softkey
        print(self.devicename + ": Spectrum collection SINGLE run start.")

    def Stop(self):
        self.write('INIT:CONT 0')  # equivlant to repeat softkey
        print(self.devicename + ": Spectrum collection STOPped.")

    def set_sens(self, sens):
        sens = float(sens)
        self.write(f'SENS:POW:DC:RANG:LOW {sens:.1f}')
        sens = float(self.query('SENS:POW:DC:RANG:LOW?'))
        print(self.devicename + ": OSA sensitivity set to " + sens + "dBm.")

    def blank_trace(self, trace):
        trace = str(trace).capitalize()
        if trace.casefold() == 'all':
            for t in self.__available_traces:
                self.blank_trace(t)
            return
        if trace.casefold() not in [str(t).casefold() for t in self.__available_traces]:
            raise ValueError(self.devicename + ": Trace name " + trace + " unrecognized. " +
                             "AQ6315 trace must select from " + str(self.__available_traces))
        self.write("DISP:WIND:TRAC TR" + trace+ ",OFF")
        print(self.devicename + ": Trace " + trace + " is blanked.")

    def disp_trace(self, trace):
        trace = str(trace).capitalize()
        if trace.casefold() == 'all':
            for t in self.__available_traces:
                self.disp_trace(t)
            return
        if trace.casefold() not in [str(t).casefold() for t in self.__available_traces]:
            raise ValueError(self.devicename + ": Trace name " + trace + " unrecognized. " +
                             "AQ6315 trace must select from " + str(self.__available_traces))
        self.write("DISP:WIND:TRAC TR" + trace + ",ON")
        print(self.devicename + ": Trace " + trace + " is displayed.")

    def write_trace(self, trace):               # what is write trace?
        trace = str(trace).capitalize()
        if trace.casefold() == 'all':
            for t in self.__available_traces:
                self.write_trace(t)
            return
        if trace.casefold() not in [str(t).casefold() for t in self.__available_traces]:
            raise ValueError(self.devicename + ": Trace name " + trace + " unrecognized. " +
                             "AQ6315 trace must select from " + str(self.__available_traces))
        self.query("WRT" + trace)
        print(self.devicename + ": Trace " + trace + " is being written.")

    def fix_trace(self, trace):
        trace = str(trace).capitalize()
        if trace.casefold() == 'all':
            for t in self.__available_traces:
                self.fix_trace(t)
            return
        if trace.casefold() not in [str(t).casefold() for t in self.__available_traces]:
            raise ValueError(self.devicename + ": Trace name " + trace + " unrecognized. " +
                             "AQ6315 trace must select from " + str(self.__available_traces))
        self.write("TRAC:FEED:CONT TR" + trace+",NEV")
        print(self.devicename + ": Trace " + trace + " is fixed.")
    
    def update_trace(self, trace):
        trace = str(trace).capitalize()
        if trace.casefold() == 'all':
            for t in self.__available_traces:
                self.update_trace(t)
            return
        if trace.casefold() not in [str(t).casefold() for t in self.__available_traces]:
            raise ValueError(self.devicename + ": Trace name " + trace + " unrecognized. " +
                             "AQ6315 trace must select from " + str(self.__available_traces))
        self.write("TRAC:FEED:CONT TR" + trace+",ALW")
        print(self.devicename + ": Trace " + trace + " is updated.")

    def osa(self, trace):
        from IPython.display import display, clear_output
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        while self.osaacquiring:
            wl, pw = self.get_trace(trace, plot=False)
            ax.cla()
            # try:
            #     if self.oscxlim != None:
            #         ax.set_xlim(self.oscxlim)
            #     if self.oscylim != None:
            #         ax.set_ylim(self.oscylim)
            # except:
            #     self.osaacquiring = False
            #     print('Invalid oscscale')
            ax.plot(wl, pw)
            display(fig)
            clear_output(wait=True)

    def startosa(self, trace):
        if not self.osaacquiring:
            self.osaacquiring = True
            x = threading.Thread(target=self.osa, args=(trace,))
            x.start()

    def stoposa(self):
        self.osaacquiring = False

    # def get_trace(self, trace, plot=True, filename=None):
    #     trace = str(trace).capitalize()
    #     if trace.casefold() not in [str(t).casefold() for t in self.__available_traces]:
    #         raise ValueError(self.devicename + ": Trace name " + trace + " unrecognized. " +
    #                          "AQ6315 trace must select from " + str(self.__available_traces))
    #     # remove the leading and the trailing characters, split values, remove the first value showing number of values in a dataset
    #     wl = self.query('WDAT' + trace).strip().split(',')[1:]        #MMEM:STOR:TRAC? TRA
    #     intensity = self.query('LDAT' + trace).strip().split(',')[1:]
    #     # list of strings -> numpy array (vector) of floats
    #     wl = np.asarray(wl, 'f').T
    #     intensity = np.asarray(intensity, 'f').T
    #     if plot:
    #         plt.figure()
    #         plt.plot(wl, intensity)
    #         plt.xlabel('wavelength (nm)')
    #         plt.ylabel('intensity (dBm)')
    #         plt.ylim(bottom=-75)
    #         if filename is not None:
    #             plt.savefig(filename + '.png')
    #         plt.show()
    #         print(self.devicename + ": Trace " + trace + " data is collected and is shown in the plot.")
    #     return wl, intensity

    def get_trace(self, trace, plot=True, filename=None):
        trace = str(trace).capitalize()
        if trace.casefold() not in [str(t).casefold() for t in self.__available_traces]:
            raise ValueError(self.devicename + ": Trace name " + trace + " unrecognized. " +
                             "AQ6315 trace must select from " + str(self.__available_traces))
        # remove the leading and the trailing characters, split values, remove the first value showing number of values in a dataset
        #wl = self.query('WDAT' + trace).strip().split(',')[1:]        #MMEM:STOR:TRAC? TRA
        self.write('form ascii')
        self.write('trac:data:y? tra')
        d=self.read('trac:data:y? tra')
        d=d.replace('\n','')
        d=d.split(',')
        d=np.array(d)
        intensity=d.astype(float)
        wl=np.linspace(getStart(OSA),getStop(OSA),len(power))
        #intensity = self.query('LDAT' + trace).strip().split(',')[1:]
        # list of strings -> numpy array (vector) of floats
        wl = np.asarray(wl, 'f').T
        intensity = np.asarray(intensity, 'f').T
        if plot:
            plt.figure()
            plt.plot(wl, intensity)
            plt.xlabel('wavelength (nm)')
            plt.ylabel('intensity (dBm)')
            plt.ylim(bottom=-75)
            if filename is not None:
                plt.savefig(filename + '.png')
            plt.show()
            print(self.devicename + ": Trace " + trace + " data is collected and is shown in the plot.")
        return wl, intensity



    def getData(OSA):
        print('Getting data from OSA')
        OSA.write('form ascii')
        OSA.write('trac:data:y? tra')
        d=OSA.read('trac:data:y? tra')
        d=d.replace('\n','')
        d=d.split(',')
        d=np.array(d)
        power=d.astype(float)
        
        WL=np.linspace(getStart(OSA),getStop(OSA),len(power))
        return WL, power




    def save_trace(self, trace, filename, extensions=['.mat', '.txt']):
        trace = str(trace).capitalize()
        # Extension handle
        available_extensions = ['.mat', '.txt', '.fits', '.csv']
        if str(extensions).casefold() == 'all':
            extensions = available_extensions
        if not isinstance(extensions, list):
            extensions = [extensions]
        extensions = [str(tt).casefold() for tt in extensions]
        for ext in extensions:
            if ext not in available_extensions:
                raise ValueError(self.devicename + ": To save extension " + ext + " is not available yet. Available: " +
                                 str(available_extensions))
        # File name extension handle
        filedir, single_filename = os.path.split(filename)
        if os.path.splitext(single_filename)[-1] in extensions:
            warnings.warn(self.devicename + ": Filename extension " + os.path.splitext(single_filename)[-1] +
                          " is ignored. This function save " + str(extensions) +
                          ". Change extension to save by extensions=['.mat']")
            filename = os.path.splitext(filename)[0]
        # File directory handle
        if (not os.path.isdir(filedir)) and (not filedir == ''):
            warnings.warn(self.devicename + ": Directory " + filedir + " does not exist. Creating new directory.")
            os.makedirs(filedir)
        # File already exists handle
        for ext in extensions:
            if os.path.isfile(filename + ext):
                warnings.warn(self.devicename + ": To save Filename " + filename + ext +
                              " already exists. Previous file renamed.")
                from datetime import datetime
                now = datetime.now()  # current date and time
                date_time = now.strftime("%Y%m%d_%H%M%S")  # example: '20220811_105537'
                new_name = filename + '_' + date_time + '_bak' + ext
                os.rename(filename + ext, new_name)
        # Data read
        wl, intensity = self.get_trace(trace, plot=True, filename=filename)
        # Data save
        for ext in extensions:
            if ext == '.mat':
                # save .mat file
                from scipy.io import savemat
                try:
                    savemat(filename + '.mat', {
                        'OSAWavelength': wl,
                        'OSAPower': intensity,
                        'resolution': self.resolution,
                        'timestamp': time.ctime()
                    },
                            oned_as='column')
                    print(self.devicename + ": Trace " + trace + " data is saved to " + filename + '.mat')
                except:
                    warnings.warn(self.devicename + ": Save trace to " + filename + ".mat failed.")
                    import sys
                    e = sys.exc_info()[0]
                    print(f"Error:{e}")
            elif ext == '.txt':
                # Save .txt file
                try:
                    wl_str = np.asarray(wl, 'str')
                    intensity_str = np.asarray(intensity, 'str')
                    data = np.column_stack((wl_str, intensity_str))
                    with open(filename + '.txt', "w") as txt_file:
                        for line in data:
                            txt_file.write(" ".join(line) + "\n")
                    print(self.devicename + ": Trace " + trace + " data is saved to " + filename + '.txt')
                    # todo: add exception handler
                except:
                    warnings.warn(self.devicename + ": Save trace to " + filename + ".txt failed.")
                    import sys
                    e = sys.exc_info()[0]
                    print(f"Error:{e}")
            elif ext == '.fits':
                try:
                    from astropy.io import fits
                    hdu = fits.PrimaryHDU(np.array([wl, intensity]).T)
                    hdulist = fits.HDUList([hdu])
                    hdulist.writeto(filename + '.fits')
                    hdulist.close()
                    print(self.devicename + ": Trace " + trace + " data is saved to " + filename + '.fits')
                except:
                    warnings.warn(self.devicename + ": Save trace to " + filename + ".fits failed.")
                    import sys
                    e = sys.exc_info()[0]
                    print(f"Error:{e}")
            elif ext == '.csv':
                try:
                    np.savetxt(filename + '.csv', np.array([wl, intensity]).T, delimiter=",")
                    print(self.devicename + ": Trace " + trace + " data is saved to " + filename + '.csv')
                except:
                    warnings.warn(self.devicename + ": Save trace to " + filename + ".csv failed.")
                    import sys
                    e = sys.exc_info()[0]
                    print(f"Error:{e}")
        return


if __name__ == '__main__':

    pass
