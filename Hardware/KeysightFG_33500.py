from .Device import Device
import time


class KeysightFG_33500(Device):

    def __init__(
        self,
        addr="USB0::0x0957::0x2807::MY59003824::INSTR",
        name="Keysight Function Generator 33500 Series",
        isVISA=True,
    ):
        super().__init__(addr=addr, name=name, isVISA=isVISA)

    @property
    def IDN(self):
        return self.query("*IDN?")
    
    
    def sin(self,chennel):
        self.write(f"SOUR{chennel}:FUNC SIN")

    def square(self,chennel):
        self.write(f"SOUR{chennel}:FUNC SQU")

    def ramp(self,chennel):
        self.write(f"SOUR{chennel}:FUNC RAMP")
    
    # def arbitary(self, func_array, sample_rate, amp, offset, phase=0):
    #     self.write(f"APPL:USER {sample_rate}, {amp}, {offset}, {phase}")
    #     self.write(f"DATA:VOL:CLE")
    #     self.write(f"DATA:VOL:DATA {func_array}")
    #     self.write(f"FUNC:USER")

    def dc_voltage(self, chennel):
        self.write(f"SOUR{chennel}:FUNC DC")
                   
    
    # def dc_current(self, current):
    #     self.write(f"APPL:DC DEF, DEF, DEF, {current}")

    


    #set output channel impedance
    # def set_channel_impedance(self, channel, impedance):
    #     self.write(f"OUTP{channel}:IMP {impedance}")
    #set output channel amplitude
    def set_channel_amplitude(self, channel, amp):
        self.write(f"SOUR{channel}:VOLT {amp}")
    #set output channel offset
    def set_channel_offset(self, channel, offset):
        self.write(f"SOUR{channel}:VOLT:OFFS {offset}")
    #set output channel phase
    def set_channel_phase(self, channel, phase):
        self.write(f"SOUR{channel}:PHAS {phase}")
    #set output channel frequency
    def set_channel_frequency(self, channel, freq):
        self.write(f"SOUR{channel}:FREQ {freq}")
    #set output channel duty cycle
    # def set_channel_duty_cycle(self, channel, duty):
    #     self.write(f"DUTY{channel} {duty}")
    # #set output channel symmetry
    # def set_channel_symmetry(self, channel, sym):
    #     self.write(f"SYMM{channel} {sym}")
    # #set output channel state
    def set_channel_state(self, channel, state):
        if str(state).casefold() in ["off", "0"]:
            self.write(f"OUTP{channel} OFF")
        elif str(state).casefold() in ["on", "1"]:
            self.write(f"OUTP{channel} ON")
        else:
            raise ValueError("Invalid state")


    def set_channel_func(self, channel, func=str):
        if func.casefold() in ["sine", "sin"]:
            self.sin(channel)  
        elif func.casefold() in ["square", "squ"]:
            self.square(channel)
        elif func.casefold() in ["ramp"]:
            self.ramp(channel)
        elif func.casefold() in ["dc"]:
            self.dc_voltage(channel)
        else:
            raise ValueError("Invalid function")
        print(self.get_channel_function(channel))



    #get output channel amplitude
    def get_channel_amplitude(self, channel):
        return float(self.query(f"SOUR{channel}:VOLT?"))
    #get output channel offset
    def get_channel_offset(self, channel):
        return float(self.query(f"SOUR{channel}:VOLT:OFFS?"))
    #get output channel phase
    def get_channel_phase(self, channel):
        return float(self.query(f"SOUR{channel}:PHAS?"))
    #get output channel frequency
    def get_channel_frequency(self, channel):
        return float(self.query(f"SOUR{channel}:FREQ?"))
    def get_channel_state(self, channel):
        return self.query(f"OUTP{channel}?")
    def get_channel_function(self, channel):
        return self.query(f"SOUR{channel}:FUNC?")
    
    def get_sync_state(self):
        return self.query(f"OUTP:SYNC?")
    
    def set_trigger_type(self,channel, state):
        if state not in ['IMM', 'EXT', 'BUS']:
            raise ValueError("Invalid state")
        self.write(f"TRIG{channel}:SOUR {state}")



    def set_trigger_source(self, source):
        self.write(f"OUTP:TRIG:SOUR CH{source}")
        print('trig source='+self.query(f"OUTP:TRIG:SOUR?"))

    def set_trigger_offupdown(self, state):
        if str(state).casefold() in ["off", "OFF", "0"]:
            self.write(f"OUTP:TRIG OFF")
        elif str(state).casefold() in ["UP", "up"]:
            self.write(f"OUTP:TRIG:SLOP POS")
        elif str(state).casefold() in ["DOWN", "down"]:
            self.write(f"OUTP:TRIG:SLOP NEG")
        else:
            raise ValueError("Invalid state")
        print('trig state='+ self.query(f"OUTP:TRIG?"))
        print('trig slope='+self.query(f"OUTP:TRIG:SLOP?"))
 
    def set_sync_onoff(self, state):
        if str(state).casefold() in ["off", "OFF", "0"]:
            self.write(f"OUTP:SYNC OFF")
        elif str(state).casefold() in ["ON", "on", "1"]:
            self.write(f"OUTP:SYNC ON")
        else:
            raise ValueError("Invalid state")
        self.get_sync_state()
        
    


    #get output channel duty cycle
    # def get_channel_duty_cycle(self, channel):
    #     return self.query(f"DUTY{channel}?")
    # #get output channel symmetry
    # def get_channel_symmetry(self, channel):
    #     return self.query(f"SYMM{channel}?")
    # #get output channel impedance
    # def get_channel_impedance(self, channel):
    #     return self.query(f"OUTP{channel}:IMP?")
    #get output channel state
    
    
    #get channel parameters
    def get_channel_parameters(self, channel):
        print(f"Channel {channel} parameters:")

        print(f"Frequency: {self.get_channel_frequency(channel)}")
        print(f"Amplitude: {self.get_channel_amplitude(channel)}")
        print(f"Offset: {self.get_channel_offset(channel)}")
        print(f"Phase: {self.get_channel_phase(channel)}")
        #print(f"Duty Cycle: {self.get_channel_duty_cycle(channel)}")
        #print(f"Symmetry: {self.get_channel_symmetry(channel)}")
        #print(f"Impedance: {self.get_channel_impedance(channel)}")
        print(f"State: {self.get_channel_state(channel)}")
        print(f"Function: {self.get_channel_function(channel)}")
    

    #apply wave function with parameters to output channel
    def set_channel_parameters(self, channel , freq, amp, offset, phase):
        # if function == "sin":
        #     self.sin(self,channel)
        # elif function == "square":
        #     self.square(self,channel)
        # elif function == "ramp":
        #     self.ramp(self,channel)
        # elif function == "dc":
        #     self.dc_voltage(self,channel)
        # else:
        #     print("Function not supported")
        self.set_channel_frequency(channel, freq)
        self.set_channel_amplitude(channel, amp)
        self.set_channel_offset(channel, offset)
        self.set_channel_phase(channel, phase)
        
        self.get_channel_parameters(channel)
       

    
if __name__ == "__main__":
    fg = KeysightFG_33500()
    fg.connect()
    print(fg.IDN)
    fg.disconnect()