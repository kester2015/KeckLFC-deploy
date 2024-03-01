from .Device import Device
import numpy as np
import time


class ORIONLaser(Device):
    def __init__(self, addr='ASRL4::INSTR', name="ORION Laser Module"):
        super().__init__(addr=addr, name=name, isVISA=False)
        self.inst = self.rm.open_resource(addr, read_termination='\xA5')
        self.__thermistor_A = 1.2146e-3
        self.__thermistor_B = 2.1922e-4
        self.__thermistor_C = 1.5244e-7
        self.__default_TEC_Ohm = 9661  # ohm, about 25.5 degC
        self.__default_laserCur = 1450  # in unit of 0.1mA

    def default_DiodCur_TEC(self):
        self.writeTECsetpoint(self.__steinhart_hart_ohm2degC(self.__default_TEC_Ohm), volatile=False)
        self.writeLaserdiodeCur_mA(self.__default_laserCur/10, volatile=False)

    def printStatus(self):
        message = "ORION Laser Module Status Summary".center(80, '-') + "\n"
        ID = self.readProductID()
        time.sleep(0.1)
        ver = self.readFirmwareVersion()
        time.sleep(0.1)
        SN = self.readSerialNumber()
        message = message + str("Product ID: " + ID + ", Ver " + ver +
                                f", SN: {SN}").center(80, '-') + "\n"
        time.sleep(0.1)
        message = message + f"|\t Status Code: {self.readStatus()}\n"
        time.sleep(0.1)
        message = message + f"|\t Photo monitor voltage: {self.readPhotomonitorV():.3f} Volt (also mA, r=1kOhm)\n"
        time.sleep(0.1)
        message = message + f"|\t Board Temp:   {self.readBoardTemp():.4f} " + u'\N{DEGREE SIGN}' + "C\n"
        time.sleep(0.1)
        message = message + f"|\t Thermis Temp: {self.readThermisTemp():.4f} " + u'\N{DEGREE SIGN}' + "C\n"
        time.sleep(0.1)

        message = message + f"|\t Volatile Settings (reset to non-volatile after re-plug): \n"
        cur = self.readLaserdiodeCur_mA(volatile=True)
        time.sleep(0.1)
        tec = self.readTECsetpoint(volatile=True)
        message = message + f"|\t\t Diode Cur = {cur:.4f} mA, TEC Set = {tec:.3f}" + u'\N{DEGREE SIGN}' + "C\n"
        time.sleep(0.1)

        message = message + f"|\t Non Volatile Settings (Doesn't reset after re-plug): \n"
        cur = self.readLaserdiodeCur_mA(volatile=False)
        time.sleep(0.1)
        tec = self.readTECsetpoint(volatile=False)
        message = message + f"|\t\t Diode Cur = {cur:.4f} mA, TEC Set = {tec:.3f}" + u'\N{DEGREE SIGN}' + "C\n"
        message = message + "ORION Laser Module Status Summary Ends".center(
            80, '-')
        print(message)
        return message

    def readFirmwareVersion(self):
        response = self.query(0x01)
        version = int.from_bytes(response['data'], byteorder='big')
        major = (version & 0xF000) >> 12
        minor = (version & 0x0FF0) >> 4
        patch = (version & 0x000F)
        return f'{major}.{minor}.{patch}'

    def readSerialNumber(self):
        response = self.query(0x08)
        SN = int.from_bytes(response['data'], byteorder='big')
        return SN

    def readStatus(self):
        response = self.query(0x0E)
        W1 = response['data'][0]
        W2 = response['data'][1]
        W3 = response['data'][2]
        print(W1)
        print(W2)
        print(W3)
        return response['data']

    def readProductID(self):
        response = self.query(0x42)
        return str(response['data'].decode())

    def readBoardTemp(self):
        v = int.from_bytes(self.query(0x12)['data'],
                           byteorder='big') * 2.5 / 65520
        if v > 2.273 or v < 0.210:
            print(
                self.devicename +
                f": Board temperature read sensor voltage {v} V, out of range (2.273V -20C, 0.210V 90C)."
            )
            return np.NaN
        Board_V = [
            2.273, 2.124, 1.919, 1.667, 1.390, 1.115, 0.867, 0.660, 0.497,
            0.372, 0.279, 0.210
        ]
        Board_T = [-20., -10., 0., 10., 20., 30., 40., 50., 60., 70., 80., 90.]
        return np.interp(v, Board_V[::-1], Board_T[::-1])

    def readThermisTemp(self):
        Thermistor_V = int.from_bytes(self.query(0x11)['data'],
                                      byteorder='big') * 2.5 / 65520
        Thermistor_Ohms = Thermistor_V * 10000 / (2.5 - Thermistor_V)
        return self.__steinhart_hart_ohm2degC(Thermistor_Ohms)

    def readPhotomonitorV(self):
        return int.from_bytes(
            self.query(0x13)['data'], byteorder='big'
        ) * 2.5 / 65520  # Volts or mA (monitor has 1KOhm resist)

    def readLaserdiodeCur_mA(self, volatile=False):  # return in mA
        if volatile:
            return int.from_bytes(self.query(0x1D)['data'],
                                  byteorder='big') / 10
        else:
            return int.from_bytes(self.query(0x26)['data'],
                                  byteorder='big') / 10

    def writeLaserdiodeCur_mA(self, mA, volatile=True):  # return in mA
        setpoint = int(np.round(mA)*10).to_bytes(2,'big') # in units of 0.1mA, thus need *10
        print(self.devicename+": Set "+ ("volatile" if volatile else "non-volatile") + f" laser diode current to {mA} mA.")
        if volatile:
            return self.query(0x1E, data=setpoint, read=False)
        else:
            return self.query(0x27, data=setpoint, read=False)
        
    def readTECsetpoint(self, volatile=False):
        if volatile:
            return self.__steinhart_hart_ohm2degC(
                int.from_bytes(self.query(0x1F)['data'], byteorder='big'))
        else:
            return self.__steinhart_hart_ohm2degC(
                int.from_bytes(self.query(0x28)['data'], byteorder='big'))

    def writeTECsetpoint(self, temp, volatile=True):
        setpoint = self.__steinhart_hart_degC2ohm(temp).to_bytes(2, 'big')
        print(self.devicename+": Set "+ ("volatile" if volatile else "non-volatile") + f" TEC setpoint to {temp} degC. ({self.__steinhart_hart_degC2ohm(temp)} ohm).")
        if volatile:
            return self.query(0x20, data=setpoint, read=False)
        else:
            return self.query(0x29, data=setpoint, read=False)
        

    def query(self, cmdID, data=[], pktID=0, read=True):
        packetlength = len(data) + 7
        packet = bytearray(packetlength + 2)
        packet[0] = 0xA9
        packet[1] - pktID & 0xFF
        packet[2] = packetlength
        packet[4] = 0xFF  # Dest ID
        packet[5] = 0x01 if read else 0x02
        packet[6] = cmdID & 0xFF
        packet[7:7 + len(data)] = data
        packet[-2] = -sum(packet) & 0xFF  # Checksum
        packet[-1] = 0xA5
        self.inst.write_raw(bytes(packet))
        return self.read()

    def read(self):
        packet = bytearray(self.inst.read_raw())[1:]  # Remove leading 0x00
        ret = {}
        ret['valid'] = True
        if not (packet[0] == 0xA9 and packet[-1] == 0xA5):
            ret['valid'] = False
            print(
                self.devicename +
                f": Error read. Invaild header {packet[0]} (expect 0xA9=169) or footer {packet[-1]} (expect 0xA5=165)"
            )
        if not sum(packet[:-1]) & 0xFF == 0:
            ret['valid'] = False
            print(self.devicename + ": Error read. Checksum Error.")
        ret['packetlength'] = packet[2]
        ret['status'] = packet[6]
        ret['cmdID'] = packet[7]
        ret['data'] = packet[8:packet[2]]
        return ret

    def connect(self):
        self.query(0x24, read=False)
        return super().connect()

    def disconnect(self):
        self.query(0x25, read=False)
        return super().disconnect()
    
    def _ohm2degC(self, ohm):
        return self.__steinhart_hart_ohm2degC(ohm)
    def _degC2ohm(self, degC):
        return self.__steinhart_hart_degC2ohm(degC)

    def __steinhart_hart_ohm2degC(self, R):
        A = self.__thermistor_A
        B = self.__thermistor_B
        C = self.__thermistor_C
        TK = 1 / (A + B * np.log(R) + C * np.power(np.log(R), 3))
        return TK - 273.15

    def __steinhart_hart_degC2ohm(self, Tc):
        A = self.__thermistor_A
        B = self.__thermistor_B
        C = self.__thermistor_C
        TK = Tc + 273.15
        x = (A - 1 / TK) / C
        y = np.sqrt(np.power(B / 3 / C, 3) + np.power(x, 2) / 4)
        return int(
            np.round(
                np.exp(
                    np.power(y - x / 2, 1 / 3) - np.power(y + x / 2, 1 / 3))))
