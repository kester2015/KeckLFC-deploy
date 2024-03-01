import numpy as np
import struct
import threading
from .Device import Device


class RedPitaya(Device):
    def __init__(self, addr, name=None):
        if name is None:
            name = "Red Pitaya"
        super().__init__(addr, name=name, isVISA=False)
        self.inst = scpi(addr, timeout=1)
        self.isVISA = True
        self.oscacquiring = False
        self.oscdecimation = 1
        self.oscunit = "VOLTS"
        self.oscxlim = None
        self.oscylim = None
        self.osctrigger = "NOW"

    def connect(self):
        return super().connect()

    def write(self, cmd):
        self.inst.tx_txt(cmd)

    def read(self):
        return self.inst.rx_txt()

    def query(self, cmd):
        self.write(cmd)
        return self.read()

    # region INPUT functions

    # Slow analog inputs
    def ain(self, port):
        if port in [1, 2]:
            return float(self.query(f'ANALOG:PIN? AIN{port - 1}'))

    # Fast analog inputs
    def acquire(self, port):
        if port not in [1, 2]:
            return
        self.write('ACQ:DATA:FORMAT BIN')
        if self.oscunit == 'VOLTS':
            self.write('ACQ:DATA:UNITS VOLTS')
        else:
            self.write('ACQ:DATA:UNITS RAW')
        self.write(f'ACQ:DEC {self.oscdecimation}')

        self.write('ACQ:START')
        self.write(f'ACQ:TRIG {self.osctrigger}')
        self.write(f'ACQ:SOUR{port}:GAIN HV')

        while 1:
            self.write('ACQ:TRIG:STAT?')
            if self.read() == 'TD':
                break

        self.write(f'ACQ:SOUR{port}:DATA?')
        buff_byte = self.inst.rx_arb()
        self.write('ACQ:STOP')
        if self.oscunit == 'VOLTS':
            return [
                struct.unpack('!f', bytearray(buff_byte[i:i + 4]))[0]
                for i in range(0, len(buff_byte), 4)
            ]
        else:
            return [
                struct.unpack('!h', bytearray(buff_byte[i:i + 2]))[0]
                for i in range(0, len(buff_byte), 2)
            ]

    def osc(self, port):
        import matplotlib.pyplot as plt
        from IPython.display import display, clear_output
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        while self.oscacquiring:
            y = self.acquire(port)
            t = np.linspace(0, self.oscdecimation * 133.42e-6, num=len(y))
            ax.cla()
            try:
                if self.oscxlim != None:
                    ax.set_xlim(self.oscxlim)
                if self.oscylim != None:
                    ax.set_ylim(self.oscylim)
            except:
                self.oscacquiring = False
                self.warning('Invalid oscscale')
            ax.plot(t, y)
            display(fig)
            clear_output(wait=True)

    def setosc(self,
               xlim="keep",
               ylim="keep",
               dec="keep",
               unit="keep",
               trigger="keep"):
        if xlim != "keep":
            self.oscxlim = xlim
        if ylim != "keep":
            self.oscylim = ylim
        if dec != "keep" and dec in 2**np.arange(17):
            self.oscdecimation = dec
        if unit != "keep" and unit in ["VOLTS", "RAW"]:
            self.oscunit = unit
        if trigger != "keep" and trigger in [
                "DISABLED", "NOW", "CH1_PE", "CH1_NE", "CH2_PE", "CH2_NE",
                "EXT_PE", "EXT_NE", "AWG_PE", "AWG_NE"
        ]:
            self.osctrigger = trigger

    def startosc(self, port):
        if not self.oscacquiring:
            self.oscacquiring = True
            x = threading.Thread(target=self.osc, args=(port, ))
            x.start()

    def stoposc(self):
        self.oscacquiring = False

    # endregion

    # region OUTPUT functions

    # Slow analog outputs
    def aout(self, port, value):
        if port in [1, 2]:
            self.write(f'ANALOG:PIN AOUT{port - 1},{value}')

    # Fast analog onputs
    def signalGenerator(self,
                        port=1,
                        outEnable=False,
                        func='SINE',
                        arb=None,
                        freq=10e6,
                        amp=1,
                        offset=0,
                        phase=0,
                        dcyc=0.5,
                        burst=False,
                        trigger='INT'):

        if port not in [1, 2]:
            return "Port"

        if not outEnable:
            self.write(f'OUTPUT{port}:STATE OFF')
            return "OFF"

        if func not in [
                'SINE', 'SQUARE', 'TRIANGLE', 'SAWU', 'SAWD', 'PWM',
                'ARBITRARY', 'DC', 'DC_NEG'
        ]:
            return "Function"
        self.write(f'SOUR{port}:FUNC {func}')
        if func == 'ARBITRARY':
            self.write(f'SOUR{port}:TRAC:DATA:DATA {arb}')
            self.write(f'OUTPUT{port}:STATE ON')
            return "ON"

        if freq < 0 or freq > 62.5e6:
            return "Freq"
        self.write(f'SOUR{port}:FREQ:FIX {freq}')

        if amp < -1 or amp > 1:
            return "Amp"
        self.write(f'SOUR{port}:VOLT {amp}')

        if offset < -1 or offset > 1:
            return "Offset"
        self.write(f'SOUR{port}:VOLT:OFFS {offset}')

        if phase < -360 or phase > 360:
            return "Phase"
        self.write(f'SOUR{port}:PHAS {phase}')

        if dcyc < 0 or dcyc > 1:
            return "Duty cycle"
        self.write(f'SOUR{port}:DCYC {dcyc}')

        self.write(
            f'SOUR{port}:BURS:STAT {"BURST" if burst else "CONTINUOUS"}')
        if burst:
            pass

        if trigger not in ['EXT_PE', 'EXT_NE', 'INT', 'GATED']:
            return "Trigger"
        self.write(f'SOUR{port}:TRIG:SOUR {trigger}')

        self.write(f'OUTPUT{port}:STATE ON')
        return "ON"

    def ramp(self, port, outEnable=True, freq=10, amp=1, ofs=0):
        self.signalGenerator(port=port,
                             outEnable=outEnable,
                             func='TRIANGLE',
                             offset=ofs,
                             amp=amp,
                             freq=freq)

    def dc(self, port, offset, outEnable=True):
        self.signalGenerator(port=port,
                             outEnable=outEnable,
                             func='DC',
                             amp=0,
                             offset=offset)

    def disable(self, port):
        self.signalGenerator(port=port, outEnable=False)

    def alignPhase(self):
        self.write('PHAS:ALIGN')

    def setOutTrigger(self, port=1):
        if port in [1, 2]:
            self.write(f'SOUR{port}:TRIG:INT')
        else:
            self.write('SOUR:TRIG:INT')

    # endregion


class FPGA1(RedPitaya):
    def __init__(self, addr):
        super().__init__(addr, name="Amplitude lock loop FPGA " + addr)
        self.P = 1
        self.I = 0.1
        self.output = 0
        self.setpoint = 0
        self.inPort = 1
        self.outPort = 1
        self.locked = False

    def PILoop(self):
        x = self.acquire(port=self.inPort, dec=8)
        Pdx = self.setpoint - x[-1]
        Idx = self.setpoint - np.mean(x)
        self.output += self.P * (Pdx + self.I * Idx)
        self.aout(port=self.outPort, value=self.output)
        self.locked = Pdx < 0.1 and Idx < 0.1
        return x


class FG(RedPitaya):
    def __init__(self, addr):
        super().__init__(addr, name="Filter cavity lock loop FPGA " + addr)
        self.phase = 0
        self.state = 0

    def startfg(self,phase = None):
        if phase is not None:
            self.phase = phase
        self.state = 1
        self.signalGenerator(port=1, outEnable=True,
                                 phase=self.phase)  # LO
        self.signalGenerator(port=2, outEnable=True, amp=0.1)  # PM

    def stopfg(self):
        if self.state:
            self.state = 0
            self.disable(port=1)
            self.disable(port=2)


# region factory API
## Copied from https://github.com/RedPitaya/RedPitaya/blob/master/Examples/python/redpitaya_scpi.py
import socket

__author__ = "Luka Golinar, Iztok Jeras"
__copyright__ = "Copyright 2015, Red Pitaya"


class scpi(object):
    """SCPI class used to access Red Pitaya over an IP network."""
    delimiter = '\r\n'

    def __init__(self, host, timeout=None, port=5000):
        """Initialize object and open IP connection.
        Host IP should be a string in parentheses, like '192.168.1.100'.
        """
        self.host = host
        self.port = port
        self.timeout = timeout

    def __del__(self):
        if self._socket is not None:
            self._socket.close()
        self._socket = None

    def open(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.timeout is not None:
            self._socket.settimeout(self.timeout)

        self._socket.connect((self.host, self.port))

    def close(self):
        """Close IP connection."""
        self.__del__()

    def rx_txt(self, chunksize=4096):
        """Receive text string and return it after removing the delimiter."""
        msg = ''
        while 1:
            chunk = self._socket.recv(chunksize + len(self.delimiter)).decode(
                'utf-8')  # Receive chunk size of 2^n preferably
            msg += chunk
            if (len(chunk) and chunk[-2:] == self.delimiter):
                break
        return msg[:-2]

    def rx_arb(self):
        numOfBytes = 0
        """ Recieve binary data from scpi server"""
        str = b''
        while (len(str) != 1):
            str = (self._socket.recv(1))
        if not (str == b'#'):
            return False
        str = b''
        while (len(str) != 1):
            str = (self._socket.recv(1))
        numOfNumBytes = int(str)
        if not (numOfNumBytes > 0):
            return False
        str = b''
        while (len(str) != numOfNumBytes):
            str += (self._socket.recv(1))
        numOfBytes = int(str)
        str = b''
        while (len(str) != numOfBytes):
            str += (self._socket.recv(4096))
        return str

    def tx_txt(self, msg):
        """Send text string ending and append delimiter."""
        return self._socket.send((msg + self.delimiter).encode('utf-8'))

    def txrx_txt(self, msg):
        """Send/receive text string."""
        self.tx_txt(msg)
        return self.rx_txt()

# IEEE Mandated Commands

    def cls(self):
        """Clear Status Command"""
        return self.tx_txt('*CLS')

    def ese(self, value: int):
        """Standard Event Status Enable Command"""
        return self.tx_txt('*ESE {}'.format(value))

    def ese_q(self):
        """Standard Event Status Enable Query"""
        return self.txrx_txt('*ESE?')

    def esr_q(self):
        """Standard Event Status Register Query"""
        return self.txrx_txt('*ESR?')

    def idn_q(self):
        """Identification Query"""
        return self.txrx_txt('*IDN?')

    def opc(self):
        """Operation Complete Command"""
        return self.tx_txt('*OPC')

    def opc_q(self):
        """Operation Complete Query"""
        return self.txrx_txt('*OPC?')

    def rst(self):
        """Reset Command"""
        return self.tx_txt('*RST')

    def sre(self):
        """Service Request Enable Command"""
        return self.tx_txt('*SRE')

    def sre_q(self):
        """Service Request Enable Query"""
        return self.txrx_txt('*SRE?')

    def stb_q(self):
        """Read Status Byte Query"""
        return self.txrx_txt('*STB?')

# :SYSTem

    def err_c(self):
        """Error count."""
        return self.txrx_txt('SYST:ERR:COUN?')

    def err_c(self):
        """Error next."""
        return self.txrx_txt('SYST:ERR:NEXT?')


# endregion factory API