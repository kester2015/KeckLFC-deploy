try:
    from .Device import Device
except:
    from Device import Device

# import pyvisa

import serial
import time

class Arduino_relay(Device):
    def __init__(self, addr="COM44", name = "Arduino Relay Circuit", timeout=1, **kwargs):
        super().__init__(addr=addr, name = name, isVISA=False, **kwargs) # Arduino does not support Visa
        self.baud_rate = 9600
        self.read_termination = '\r\n'
        self.timeout = timeout # in unit of second
        self.max_query_trial = 10
    
    def printStatus(self):
        def highlight_status(status_string):
            """Color refer https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal"""
            # insert "\x1b[1;34;42m" and "\x1b[0m" before and after "OK_to_Amplify"
            status_string = status_string.replace("OK_to_Amplify", "\x1b[1;34;42m OK_to_Amplify \x1b[0m") # Green color
            # insert "\x1b[1;34;41m" and "\x1b[0m" before and after "STOPPING"
            status_string = status_string.replace("STOPPING", "\x1b[1;34;41m STOPPING \x1b[0m") # Red color
            # insert "\x1b[1;34;42m" and "\x1b[0m" before and after "passing"
            status_string = status_string.replace("passing", "\x1b[1;34;42m passing \x1b[0m") # Green color
            # insert "\x1b[1;34;41m" and "\x1b[0m" before and after "shutted"
            status_string = status_string.replace("shutted", "\x1b[1;34;41m shutted \x1b[0m") # Red color
            return status_string
            
        message = "Arduino Relay Module Status Summary".center(80, '-') + "\n"
        relay_info = self.get_relay_info()
        # insert "|\t" after every "\n"
        relay_info = relay_info.replace("\n", "\n|\t\t")
        message = message + f"|\t Relay Status: {highlight_status(self.get_relay_status())}\n"
        message = message + f"|\t Relay Info: {relay_info}\n"
        YJ_info = self.get_YJ_info()
        # insert "|\t" after every "\n"
        YJ_info = YJ_info.replace("\n", "\n|\t\t")
        message = message + f"|\t YJ Shutter State: {highlight_status(YJ_info)}\n"
        message = message + "Arduino Relay Module Status Summary Ends".center(80, '-')
        self.info(message)
        return message

    def connect(self):
        if not self.connected:
            try:
                #make connection with controller
                self.ser = serial.Serial(port=self.addr, timeout=self.timeout, baudrate=self.baud_rate)
                self.connected = True
                self.info(self.devicename + " connected")
                return 1
            except:
                import sys
                e = sys.exc_info()[0]
                self.info(f"Error:{e}")
                return -1
        return 0
    
    def disconnect(self):
        if self.connected:
            self.ser.close()
            self.connected = False
            self.info(self.devicename + " disconnected")
            return 1
        return 0
    
    def __flush_buffer(self):
        self.ser.flushInput()
        self.ser.flushOutput()

    def write(self, cmd: str):
        # print(bytes(cmd, 'utf-8'))
        if not cmd.endswith("\r\n"):
            cmd += "\r\n"
        self.__flush_buffer()
        self.ser.write(bytes(cmd, 'utf-8'))
        time.sleep(0.2)

    def read(self):
        return self.ser.read(self.ser.in_waiting).decode('utf-8').strip()
    
    def query(self, cmd):
        num_trial = 1
        self.write(cmd)
        result = self.read()
        while result == "" and num_trial <= self.max_query_trial:
            self.write(cmd)
            self.info(self.devicename+f": Failed to query {cmd}, trial num {num_trial}, trying again")
            result = self.read()
            num_trial += 1
        if result == "":
            self.error(f"Failed to query {cmd}")
            return None
        return result
    
    # def read_line(self):
    #     return self.ser.readline() #.decode('utf-8').strip()

    @property
    def info_str_relay(self):
        return self.query("GET")
    
    @property
    def info_str_YJ(self):
        return self.query("YJState")

    def reset_relay_latch(self):
        return self.query("reset")
    
    def get_relay_info(self):
        return self.query("get")
    
    def shut_YJ(self):
        return self.query("YJShut")
    
    def pass_YJ(self):
        return self.query("YJPass")
    
    def get_YJ_info(self):
        return self.query("YJState")
    
    def get_API_help(self):
        return self.query("help")
    
    def set_relay_low_threshold(self, low_threshold):
        if low_threshold < 0 or low_threshold > 1023:
            self.error(self.devicename+f": Invalid low threshold value {low_threshold}, must be between 0 and 1023.")
            return None
        if low_threshold<100:
            self.info(self.devicename+f": Low threshold value {low_threshold} is too low, may cause false trigger. Level is be between 0 (0V) and 1023 (5V).")
            # get user confirmation
            while True:
                user_input = input("Do you want to continue? (y/n): ")
                if user_input.casefold() in ["y", "yes"]:
                    break
                elif user_input.casefold() in ["n", "no"]:
                    self.info(self.devicename+f": Low threshold value {low_threshold} is too low, operation cancelled.")
                    return None
                else:
                    self.info(self.devicename+f": Invalid input {user_input}, please enter y or n.")
        return self.query(f"THRESHOLD {low_threshold}")
    
    def set_relay_high_threshold(self, high_threshold):
        if high_threshold < 0 or high_threshold > 1023:
            self.error(self.devicename+f": Invalid high threshold value {high_threshold}, must be between 0 and 1023.")
            return None
        if high_threshold>900:
            self.info(self.devicename+f": High threshold value {high_threshold} is too high, may cause false trigger. Level is be between 0 (0V) and 1023 (5V).")
            # get user confirmation
            while True:
                user_input = input("Do you want to continue? (y/n): ")
                if user_input.casefold() in ["y", "yes"]:
                    break
                elif user_input.casefold() in ["n", "no"]:
                    self.info(self.devicename+f": High threshold value {high_threshold} is too high, operation cancelled.")
                    return None
                else:
                    self.info(self.devicename+f": Invalid input {user_input}, please enter y or n.")
        return self.query(f"HIGH {high_threshold}")
    
    def get_relay_low_threshold(self):
        # Get string after "Low threshold is"  and before "\n"
        return int(self.info_str_relay.casefold().split("Low threshold is".casefold())[1].split("\n")[0])
    
    def get_relay_high_threshold(self):
        # Get string after "High threshold is"  and before "\n"
        return int(self.info_str_relay.casefold().split("High threshold is".casefold())[1].split("\n")[0])

    def get_current_low_voltage(self):
        # Get string after "Now voltage to judge (low) is"  and before "\n"
        return int(self.info_str_relay.casefold().split("Now voltage to judge (low) is".casefold())[1].split("\n")[0])
    
    def get_current_high_voltage(self):
        # Get string after "Now voltage to judge (high) is"  and before "\n"
        return int(self.info_str_relay.casefold().split("Now voltage to judge (high) is".casefold())[1].split("\n")[0])
    
    def get_current_voltage(self):
        # Get string after "Now voltage is"  and before "\n"
        return int(self.info_str_relay.casefold().split("Now voltage is".casefold())[1].split("\n")[0])
    
    def get_relay_status(self):
        relay_info = self.info_str_relay.casefold()
        low_threshold = int(relay_info.split("Low threshold is".casefold())[1].split("\n")[0])
        high_threshold = int(relay_info.split("High threshold is".casefold())[1].split("\n")[0])
        current_low_voltage = int(relay_info.split("Now voltage to judge (low) is".casefold())[1].split("\n")[0])
        current_high_voltage = int(relay_info.split("Now voltage to judge (high) is".casefold())[1].split("\n")[0])
        current_voltage = int(relay_info.split("Now voltage is".casefold())[1].split("\n")[0])
        # relay is on only if current_low_voltage > low_threshold and current_high_voltage < high_threshold
        # NEVER put "OK_to_Amplify" in status code, unless current state is really OK to amplify
        if current_low_voltage > low_threshold and current_high_voltage < high_threshold:
            return "relay sending OK_to_Amplify signal to amplifier"
        elif current_voltage > low_threshold and current_voltage < high_threshold:
            return "relay is STOPPING amplifier, but will be OK_to_Amplify after reset_relay_latch."
        else:
            if current_voltage <= low_threshold:
                return "relay is STOPPING amplifier, because input power is too low"
            elif current_voltage >= high_threshold:
                return "relay is STOPPING amplifier, because input power is too high"
            return "relay is STOPPING amplifier"
    
    
    
    

    
if "__main__" == __name__:
    ii = 0
    ard = Arduino_relay()
    ard.connect()
    ard.printStatus()
    print(ard.get_relay_low_threshold())
    print(ard.get_relay_high_threshold())
    ard.reset_relay_latch()
    ard.printStatus()
    ard.pass_YJ()
    ard.printStatus()
    ard.shut_YJ()
    ard.printStatus()
    # while True:
    #     # print(ard.query(f"reset{ii}"))
    #     print(ard.query(f"get{ii}"))
    #     # ard.ser.flushInput()
    #     # ard.ser.flushOutput()
    #     # # ard.write("th\n")
    #     # ard.write(f"reset{ii}\r\n")
    #     # # time.sleep(1)
    #     # print(ard.ser.read(ard.ser.in_waiting).decode('utf-8').strip()=="")
    #     ii += 1

    ard.disconnect()