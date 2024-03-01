from audioop import add
from cProfile import label
import enum
from re import L

from sympy import E
from .Device import Device
import numpy as np
import matplotlib.pyplot as plt
import warnings
import os

class TDS2024C(Device):

    def __init__(self, addr="USB0::0x0699::0x03A6::C031910::INSTR", name="TDS2024C OSC", isVISA=True):
        super().__init__(addr=addr, name=name, isVISA=isVISA)
        self.inst.timeout = 5000
        self.query_delay = 3000 # ms, delay while query curve
        self.inst.read_termination = '\n'  # read_termination is not specified by default.
        self.inst.write_termination = '\r\n'  # write_termination is '\r\n' by default.

        self.wvfm = None # Store the last read wvfm 

    def get_autocorr_FWHM_single(self, data_x=None, data_y=None, filename="autocorr\\test", trace=2, fit_range=50, additional_plotdata=None):
        '''
        fit_range: in NUM of points
        aadditional_plotdata (x,y): additional data to plot in saved plots
        ----
        return

        comb_FWHM: comb FWHM in ps.
        '''
        filename = os.path.splitext(filename)[0]
        def lorentian(x,A,x0,dx):
            return A/((x-x0)*(x-x0)+dx*dx)
        if data_x==None or data_y==None:
            self.save_trace(filename=filename, trace=trace, extensions=['.mat'], plot=False, additional_data=additional_plotdata)
            data_x = self.wvfm['X'].reshape(-1)
            data_y = self.wvfm['Y'].reshape(-1)

        fit_center = np.argmax(data_y)
        fit_start = int(fit_center-fit_range/2)
        fit_stop = int(fit_center+fit_range/2)

        x0_init = data_x[fit_center]

        front = data_y[:fit_center][::-1]
        back = data_y[fit_center:]
        thre = 0.5*data_y[fit_center]
        pos1 = fit_center-next(x for x, val in enumerate(front) if val<thre)
        pos2 = next(x for x, val in enumerate(back) if val<thre) + fit_center
        dx_init = (data_x[pos2]-data_x[pos1])/2

        A_init = data_y[fit_center]*dx_init*dx_init

        from scipy.optimize import curve_fit
        popt, pcov = curve_fit(lorentian, data_x[fit_start:fit_stop], data_y[fit_start:fit_stop], p0=np.asarray([A_init,x0_init,dx_init]))

        # EOM_rep_rate = 16e9;
        # ratio = 1/rep_time/EOM_rep_rate
        ratio = 1.560e-8;
        electrical_pulse_width = popt[2] * ratio # electrical width, s
        comb_FWHM = electrical_pulse_width*2*0.648 # comb FWHM

        if additional_plotdata != None:
            total_panel = 3
            figsize_x = 13.5
        else:
            total_panel = 2
            figsize_x = 10
        fig = plt.figure(figsize=(figsize_x,4))

        plt.subplot(1,total_panel,1)
        plt.plot(data_x*ratio*1e12, data_y, label='original data')
        plt.plot(data_x*ratio*1e12, lorentian(data_x,*popt), label='lorentian fitted')
        plt.legend()
        plt.xlabel("optical time (ps)")
        plt.ylabel("Autocorr (Volt)")
        plt.title(f"electrical {electrical_pulse_width*1e12:.3f} ps, comb FWHM {comb_FWHM*1e12:.3f} ps")

        plt.subplot(1,total_panel,2)
        plt.plot(data_x[fit_start:fit_stop]*ratio*1e12, data_y[fit_start:fit_stop], label='original data')
        plt.plot(data_x[fit_start:fit_stop]*ratio*1e12, lorentian(data_x[fit_start:fit_stop],*popt), label='lorentian fitted')
        plt.legend()
        plt.xlabel("optical time (ps)")
        plt.ylabel("Autocorr (Volt)")
        plt.title(f"zoom in, {dx_init*ratio*2*0.648*1e12:.3f}")
        
        if additional_plotdata != None:
            plt.subplot(1,total_panel,3)
            plt.plot(*additional_plotdata)

        plt.show()
        fig.savefig(filename+f"_{comb_FWHM*1e12:.3f}ps.png")

        return comb_FWHM*1e12, lorentian(data_x,*popt), fig

    def get_trace(self, trace=2, plot=True):
        self.write("DAT:SOU CH" + str(trace))
        self.write("DAT:ENC ASCI")
        self.write('WFMPre:PT_Fmt Y')
        self.write('DAT:WID 2')
        # bytes per point, nbits = 8*nbytes
        self.write('DAT:STAR 1')
        self.write('DAT:STOP 2500')

        preamble = self.query('WFMP?')
        curve = self.inst.query_ascii_values("CURV?",delay=self.query_delay/1000)

        pream = str(preamble).split(';')

        wvfm={}
        wvfm['BYT_Nr'] = int(pream[0]); # bytes per point
        wvfm['BIT_Nr'] = int(pream[1]); # bits per point, = BYT_Nr*8
        wvfm['ENCd'] = pream[2]; #ASC|BIN
        wvfm['BN_Fmt'] = pream[3]; #RI|RP
        wvfm['BYT_Or'] = pream[4]; # LSB|MSB
        wvfm['NR_Pt'] = int(pream[5]); # num of points, 2500
        wvfm['WFID'] = pream[6];
        wvfm['PT_FMT'] = pream[7]; # ENV|Y
        wvfm['XINcr'] =  float(pream[8]); # X increment
        wvfm['PT_Off'] = float(pream[9]);
        wvfm['XZEro'] = float(pream[10]);
        wvfm['XUNit'] = pream[11];
        wvfm['YMUlt'] = float(pream[12]);
        wvfm['YZEro'] = float(pream[13]);
        wvfm['YOFF'] = float(pream[14]);
        wvfm['YUNit'] = pream[15];

        wvfm['Y'] = wvfm['YZEro'] + wvfm['YMUlt']*(np.array(curve) - wvfm['YOFF']);
        wvfm['X'] = wvfm['XZEro'] + wvfm['XINcr']*(np.array(range(wvfm['NR_Pt'])) - wvfm['PT_Off']);

        print(self.devicename+": Trace "+str(trace)+" data read finished.")
        if plot:
            plt.plot(wvfm['X'], wvfm['Y'])
            plt.xlabel("time ("+wvfm['XUNit']+")")
            plt.ylabel("voltage ("+wvfm['YUNit']+")")

        self.wvfm = wvfm
        return wvfm

    def save_trace(self, filename, trace=2, extensions=['.mat', '.txt'], plot=True, additional_data = None):
        '''
        additional_data is only vaild in .mat files
        '''
        trace = str(trace).capitalize()
        # Extension handle
        available_extensions = ['.mat', '.txt', '.fits', '.csv']
        if str(extensions).casefold() == 'all':
            extensions = available_extensions
        if not isinstance(extensions,list):
            extensions = [extensions]
        extensions = [str(tt).casefold() for tt in extensions]
        for ext in extensions:
            if ext not in available_extensions:
                raise ValueError(self.devicename+": To save extension "+ext+" is not available yet. Available: "+str(available_extensions))
        # File name extension handle
        filedir, single_filename = os.path.split(filename)
        if os.path.splitext(single_filename)[-1] in extensions:
            warnings.warn(self.devicename+": Filename extension "+os.path.splitext(single_filename)[-1]+
                          " is ignored. This function save "+str(extensions)+". Change extension to save by extensions=['.mat']")
            filename = os.path.splitext(filename)[0]
        # File directory handle
        if (not os.path.isdir(filedir)) and (not filedir == ''):
            warnings.warn(self.devicename+": Directory "+filedir+" does not exist. Creating new directory.")
            os.makedirs(filedir)
        # File already exists handle
        for ext in extensions:
            if os.path.isfile(filename+ext):
                warnings.warn(self.devicename+": To save Filename "+filename+ext+" already exists. Previous file renamed.")
                from datetime import datetime
                now = datetime.now() # current date and time
                date_time = now.strftime("%Y%m%d_%H%M%S") # example: '20220811_105537'
                new_name = filename+'_'+date_time+'_bak'+ext
                os.rename(filename+ext, new_name)
        # Data read
        wvfm = self.get_trace(trace=trace, plot=plot)
        wvfm['additional_data']=additional_data
        # Data save
        for ext in extensions:
            if ext == '.mat':
                # save .mat file
                from scipy.io import savemat
                try:
                    savemat(filename+'.mat', wvfm, oned_as='column')
                    print(self.devicename+": Trace "+trace+" data is saved to "+filename+'.mat')
                except:
                    warnings.warn(self.devicename+": Save trace to "+filename+".mat failed.")
                    import sys
                    e = sys.exc_info()[0]
                    print(f"Error:{e}")
            elif ext == '.txt':
                # Save .txt file
                try:
                    x_str = np.asarray(wvfm['X'],'str')
                    y_str = np.asarray(wvfm['Y'],'str')
                    data = np.column_stack((x_str, y_str))
                    with open(filename+'.txt', "w") as txt_file:
                        for line in data:
                            txt_file.write(" ".join(line) + "\n")
                    print(self.devicename+": Trace "+trace+" data is saved to "+filename+'.txt')
                    # todo: add exception handler
                except:
                    warnings.warn(self.devicename+": Save trace to "+filename+".txt failed.")
                    import sys
                    e = sys.exc_info()[0]
                    print(f"Error:{e}")
            elif ext == '.fits':
                try:
                    from astropy.io import fits
                    hdu = fits.PrimaryHDU(np.vstack([wvfm['X'],wvfm['Y']]).T)
                    hdulist = fits.HDUList([hdu])
                    hdulist.writeto(filename+'.fits')
                    hdulist.close()
                    print(self.devicename+": Trace "+trace+" data is saved to "+filename+'.fits')
                except:
                    warnings.warn(self.devicename+": Save trace to "+filename+".fits failed.")
                    import sys
                    e = sys.exc_info()[0]
                    print(f"Error:{e}")
            elif ext == '.csv':
                try:
                    np.savetxt(filename+'.csv', np.vstack([wvfm['X'],wvfm['Y']]).T , delimiter=",")
                    print(self.devicename+": Trace "+trace+" data is saved to "+filename+'.csv')
                except:
                    warnings.warn(self.devicename+": Save trace to "+filename+".csv failed.")
                    import sys
                    e = sys.exc_info()[0]
                    print(f"Error:{e}")
        return
