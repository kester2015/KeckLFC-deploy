from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport
from time import sleep
from mcculw import ul
from mcculw.enums import InfoType, BoardInfo, AiChanType, TcType, TempScale, TInOptions
import warnings
from Device import Device

class USB2408(Device):
    def __init__(self, addr=' remain to be set', name='USB2408', isVISA=True, board_num=0):
        super().__init__(addr, name, isVISA)
        # self.inst.timeout = 25000  # communication time-out time set in units of ms
        # self.inst.baud_rate = 9600  # 
        # self.inst.read_termination = '\r\n'  # read_termination is not specified by default.

        self._max_read_line = 32 # Maximum lines to read before 'Done' is read.


        self.board_num = board_num

        self.value_temperature = [0]*8



    def USB2408_set(self):
        device_to_show = "USB-2408"
        #board_num = 0
        # Verify board is Board 0 in InstaCal.  If not, show message...
        self.info("Looking for Board 0 in InstaCal to be {0} series...".format(device_to_show))

        try:
            # Get the devices name...
            board_name = ul.get_board_name(self.board_num)

        except Exception as e:
            if ul.ErrorCode(1):
                # No board at that number throws error
                self.info("\nNo board found at Board 0.")
                self.error(e)
                return

        else:
            if device_to_show in board_name:
                # Board 0 is the desired device...
                self.info("{0} found as Board number {1}.\n".format(board_name, self.board_num))
                ul.flash_led(self.board_num)

                for i in range(8):
                # select a channel
                    channel = i
                    # Set channel type to TC (thermocouple)
                    ul.set_config(
                        InfoType.BOARDINFO, self.board_num, channel, BoardInfo.ADCHANTYPE,
                        AiChanType.TC)
                    # Set thermocouple type to type J
                    ul.set_config(
                        InfoType.BOARDINFO, self.board_num, channel, BoardInfo.CHANTCTYPE,
                        TcType.J)
                    # Set the temperature scale to CELSIUS
                    ul.set_config(
                        InfoType.BOARDINFO, self.board_num, channel, BoardInfo.TEMPSCALE,
                        TempScale.CELSIUS)
                    # Set data rate to 60Hz
                    ul.set_config(
                        InfoType.BOARDINFO, self.board_num, channel, BoardInfo.ADDATARATE, 60)
                    self.info("set channel {:d} done".format(i))
                    
                    #sleep(0.2)

            else:
                # Board 0 is NOT desired device...
                self.warning("\nNo {0} series found as Board 0. Please run InstaCal.".format(device_to_show))
                return
        




    def USB2408_get_temp(self):
        try:

            for i in range(8):
                # select a channel
                channel = i
                #Set channel type to TC (thermocouple)

                # ul.set_config(
                #     InfoType.BOARDINFO, self.board_num, channel, BoardInfo.ADCHANTYPE,
                #     AiChanType.TC)
                # # Set thermocouple type to type J
                # ul.set_config(
                #     InfoType.BOARDINFO, self.board_num, channel, BoardInfo.CHANTCTYPE,
                #     TcType.J)
                # # Set the temperature scale to CELSIUS
                # ul.set_config(
                #     InfoType.BOARDINFO, self.board_num, channel, BoardInfo.TEMPSCALE,
                #     TempScale.CELSIUS)
                # # Set data rate to 60Hz
                # ul.set_config(
                #     InfoType.BOARDINFO, self.board_num, channel, BoardInfo.ADDATARATE, 60)

                # Read data from the channel:
                options = TInOptions.NOFILTER
                try:
                    self.value_temperature[i] = ul.t_in(self.board_num, channel, TempScale.CELSIUS, options)
                except Exception as e:
                    self.info("Error: " + str(e))
                self.info("Channel {:d}:  {:.3f} Degrees.".format(channel, self.value_temperature[i]))

                
        except Exception as e:
            self.info(e)

    def get_temps(self):
        return self.value_temperature

    def time_get_temp(self,days):
        j=1
        t=days*2880

        for j in range(t):
            USB2408.USB2408_get_temp()







        
if __name__ == '__main__':

    #initialize device and get temperature
    USB2408 = USB2408()
    USB2408.USB2408_set()
    USB2408.USB2408_get_temp()
    print(USB2408.get_temps())








