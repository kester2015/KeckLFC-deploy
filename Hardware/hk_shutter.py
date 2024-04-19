

from .Device import Device
import time
import serial


class hk_shutter(Device):

    def __init__(
        self,
        addr="COM12",
        name="hk_shutter",
        isVISA=False,
        timeout=1,
        **kwargs,
    ):
        super().__init__(addr=addr, name=name, isVISA=isVISA, **kwargs)

        self.baud_rate = 9600
        self.read_termination = '\r\n'
        self.timeout = timeout # in unit of second

    def connect(self):
        if not self.connected:
            try:
                #make connection with controller
                self.ser = serial.Serial(port=self.addr, timeout=self.timeout, baudrate=self.baud_rate, 
                                         parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS)
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

    # def write(self, cmd: str):
    #     # print(bytes(cmd, 'utf-8'))
    #     if not cmd.endswith("\r\n"):
    #         cmd += "\r\n"
    #     self.__flush_buffer()
    #     self.ser.write(bytes(cmd, 'utf-8'))
    #     time.sleep(0.2)

    # def read(self):
    #     return self.ser.read(self.ser.in_waiting).decode('utf-8').strip()

    def set_status(self, status):

        self.__flush_buffer()

        stu=self.get_status()
        if status == stu:
            print("Shutter is already set to " + str(status))
            return stu
        if status != stu:
            jump = self.ser.write('ens\r'.encode())
            self.ser.read(size=jump+5)
            stu=self.get_status()
            print("Shutter is set to " + str(stu))
            return stu
        
    def get_status(self):
        self.__flush_buffer()

        jump = self.ser.write('ens?\r'.encode())
        #print(jump)
        kk1=self.ser.read(size=jump)
        #print(kk1)
        res = self.ser.read()
        #print(res)
        kk2=self.ser.read(size=8)

        if res == b'0':
            print("Shutter is 0")
            return 0
        elif res == b'1':
            print("Shutter is 1")
            return 1
        else:
            print("Shutter is not responding or buffer is not cleared")
            return -1
        
    def set_mode(self, mode):

        self.__flush_buffer()

        mod=self.get_mode()
        if mode == mod:
            print("Shutter is already set to " + str(mode) + "\n"
                  "mode num:  1:manual  2:Auto  3:Single  4:Repeat  5: External Gate" )
            return mod
        if mode != mod:
            jump = self.ser.write(f'mode={mode}\r'.encode())
            #print(jump)
            kk1=self.ser.read(size=jump-2)
            #print(kk1)
            res = self.ser.read()
            #print(res)
            kk3=self.ser.read(size=3)
            #print(kk3)
            mod=self.get_mode()
            print("Shutter is set to " + str(mod) + "\n"
                  "mode num:  1:manual  2:Auto  3:Single  4:Repeat  5: External Gate" )
            return mod
    
    def get_mode(self):
        self.__flush_buffer()

        jump = self.ser.write('mode?\r'.encode())
        #print(jump)
        kk1=self.ser.read(size=jump)
        #print(kk1)
        res = self.ser.read()
        #print(res)
        kk2=self.ser.read(size=3)

        if res == b'1':
            print("Shutter is in Manual mode")
            return 1
        elif res == b'2':
            print("Shutter is in Auto mode")
            return 2
        elif res == b'3':
            print("Shutter is in Single mode")
            return 3
        elif res == b'4':
            print("Shutter is in Repeat mode")
            return 4
        elif res == b'5':
            print("Shutter is in External Gate mode")
            return 5
        else:
            print("Shutter is not responding or buffer is not cleared")
            return -1


                
        