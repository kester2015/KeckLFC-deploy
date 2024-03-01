from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport
from mcculw import ul
from mcculw.enums import InfoType, BoardInfo, AiChanType, TcType, TempScale, TInOptions
import warnings
import numpy as np
try:
    from .Device import Device
except:
    from Device import Device


class USB2408(Device):
    def __init__(self, addr=0, name=None   #"USB-2408 DAQ"
                 , isVISA=False):
        '''
        addr is Board number. From 0.
        '''
        super().__init__(addr, name, isVISA)
        self.__num_channels = 8

        if addr==1: # This Board is on optical table breadboard
            self.thermocouple_positions = ["RF Oscillator", "RF amplifier", 
                                           "Main Phase Modulators", "Filter Cavity",
                                           "Board Glycol out", "Board Glycol in",
                                           "Compression Stage","Rubidium (Rb) Cell D2-210"]
            if self.devicename == None:
                self.devicename = "USB-2408 DAQ on Optical Table Breadboard"
        elif addr==0: # This Board is in electronics rack
            self.thermocouple_positions = ["Rack side buffle (middle side rack)", "Waveshaper (upper rack)",
                                           "Rb clock (middle rack)", "Pritel (middle upper rack)",
                                           "Rack Glycol out", "Rack Glycol in",
                                           "Power Supply Shelf (bottom rack)", "Unconnected"]
            if self.devicename == None:
                self.devicename = "USB-2408 DAQ in Electronics Rack"
        else:
            warnings.warn(self.devicename+
                          f": Board number {addr} is not pre-setted when commission (Jun-28,2023). "+
                          "Thermocouple positions (self.thermocouple_positions) not set.")
            self.thermocouple_positions = ["Position not Pre-setted"]*self.__num_channels
            if self.devicename == None:
                self.devicename = "USB-2408 DAQ"


    def printStatus(self):
        message = "USB-2408 Thermal DAQ Status Summary".center(80, '-') + "\n"

        temperature = self.get_temp_all()
        for ii in range(self.__num_channels):
            message += f"|Channel {ii}: \t {temperature[ii]:.3f} C \tat "+str(self.thermocouple_positions[ii])+"\n"

        message = message + "USB-2408 Thermal DAQ Status Summary Ends".center(80, '-')


    def connect(self, set_TC=True):
        '''
        set_TC True will set each channel to TC at connection
        '''
        if not self.connected:
            device_to_show = "USB-2408" # Board model number, Don't CHange!
            # Verify board is Board 0 in InstaCal.  If not, show message...
            print(f"Looking for Board {self.addr} in InstaCal to be "+ device_to_show +" series...")

            try:
                # Get the devices name...
                board_name = ul.get_board_name(self.addr)
            except Exception as e:
                if ul.ErrorCode(1):
                    # No board at that number throws error
                    print(f"\nNo board found at Board {self.addr}.")
                    print(e)
                    return -1
            else:
                if device_to_show in board_name:
                    # Board 0 is the desired device...
                    print(board_name+f" found as Board number {self.addr}.\n")
                    ul.flash_led(self.addr)

                    if set_TC:
                        for ii in range(self.__num_channels):
                            self.set_chan_TC(ii)

                    print(self.devicename+" connected.")
                    self.connected = True
                    return 1
                        
                else:
                    # Board 0 is NOT desired device...
                    print("\nNo "+device_to_show+f" series found as Board {self.addr}. Please run InstaCal.")
                    return -1
        else:
            return 0

    def set_chan_TC(self, channel): # TODO: allow other configuration
        # Set channel type to TC (thermocouple)
        ul.set_config(
            InfoType.BOARDINFO, self.addr, channel, BoardInfo.ADCHANTYPE,
            AiChanType.TC)
        # Set thermocouple type to type J
        ul.set_config(
            InfoType.BOARDINFO, self.addr, channel, BoardInfo.CHANTCTYPE,
            TcType.J)
        # Set the temperature scale to CELSIUS
        ul.set_config(
            InfoType.BOARDINFO, self.addr, channel, BoardInfo.TEMPSCALE,
            TempScale.CELSIUS)
        # Set data rate to 60Hz
        ul.set_config(
            InfoType.BOARDINFO, self.addr, channel, BoardInfo.ADDATARATE, 60)
        print(self.devicename + ": set channel {:d} done".format(channel))

    def get_temp(self, chan):
        try:
            # select a channel
            channel = chan
            # Read data from the channel:
            options = TInOptions.NOFILTER
            try:
                value_temperature = ul.t_in(self.addr, channel, TempScale.CELSIUS, options)
            except Exception as e:
                print("Error: " + str(e))
            print(self.devicename+": Channel {:d}:  {:.3f} Degrees.".format(channel, value_temperature) + "\t Position at "+str(self.thermocouple_positions[channel])+".")
            return value_temperature
        except Exception as e:
            print(e)
            return np.NAN

    def get_temp_all(self):
        return [self.get_temp(chan=ii) for ii in range(self.__num_channels)]


if __name__=="__main__":
    import time
    #initialize device and get temperature
    daq = USB2408(addr=0)
    daq.connect()
    daq2 = USB2408(addr=1)
    daq2.connect()

    # import time
    # time.sleep(1)
    # print(daq.get_temp_all())
    # time.sleep(1)
    # print(daq2.get_temp_all())


    # filename = r"Z:\Maodong\Projects\Keck\System Assembly test\Full_Comb_Running_2023_0330.txt"   
    # filename = r"Z:\Maodong\Projects\Keck\System Assembly test\Cabinet_open_test_2023_0605.txt"   
    # filename = r"C:\Users\HSFLFC\Desktop\Keck\Logs\DAQ_Temperature\DAQ_Temperature_2023_0628_1.txt"

    # with  open(filename,"w") as f:
    #     #TODO: write table head
    #     f.write(time.strftime('%Z')+"\t")
    #     for ii in daq.thermocouple_positions:
    #         f.write(ii+"\t")
    #     for ii in daq2.thermocouple_positions:
    #         f.write(ii+"\t")
    #     f.write("\n")
    # while True:
    #     try:
    #         with open(filename,"a") as f:
    #             f.write(time.ctime()+"\t")

    #             print("DAQ1 Temp".center(80,'-'))
    #             Temp = daq.get_temp_all()
                
    #             for jj in Temp:
    #                 f.write(f"{jj:.5f}\t")

    #             print("DAQ2 Temp".center(80,'-'))
    #             Temp = daq2.get_temp_all()
    #             for jj in Temp:
    #                 f.write(f"{jj:.5f}\t")

    #             f.write("\n")
    #     except Exception as e:
    #         print(e)
    #     time.sleep(2)

    filename = r"C:\Users\HSFLFC\Desktop\Keck\Logs\DAQ_Temperature\DAQ_Temperature_test.csv"

    with  open(filename,"w") as f:
        #TODO: write table head
        f.write(time.strftime('%Z')+",")
        for ii in daq.thermocouple_positions:
            f.write(ii+",")
        for ii in daq2.thermocouple_positions:
            f.write(ii+",")
        f.write("\n")
    while True:
        try:
            with open(filename,"a") as f:
                f.write(time.ctime()+",")

                print("DAQ1 Temp".center(80,'-'))
                Temp = daq.get_temp_all()
                
                for jj in Temp:
                    f.write(f"{jj:.5f},")

                print("DAQ2 Temp".center(80,'-'))
                Temp = daq2.get_temp_all()
                for jj in Temp:
                    f.write(f"{jj:.5f},")

                f.write("\n")
        except Exception as e:
            print(e)
        time.sleep(2)