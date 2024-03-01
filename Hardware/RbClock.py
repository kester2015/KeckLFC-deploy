from .Device import Device


class RbClock(Device):
    def __init__(self, addr='ASRL9::INSTR', name="FS725 Rubidium Frequency Standard"):
        super().__init__(addr=addr, name=name)
        self.inst.read_termination = '\r'

    def printStatus(self):
        def highlight_status(status_string):
            """Color refer https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal"""
            if status_string in ['LOCKED']:  # Show a green color
                return "\x1b[1;34;42m" + status_string + "\x1b[0m"
            elif status_string in ['UNLOCKED']:  # Show a red color
                return "\x1b[1;34;41m" + status_string + "\x1b[0m"
            else:
                return status_string
        message = str(self.devicename).center(81,'-')+"\n"
        message = message + "|"+ "FS725 Rubidium Frequency Standard Status Summary".center(80, '-') + "\n"
        message = message + "|"+ ("Model: " + 'FS725' + ", Serial No." + self.serialNumber).center(80, '-') + "\n"
        message = message + "|\t Phase Lock Status: " + highlight_status('LOCKED' if self.isPhaseLocked() else 'UNLOCKED') + "\n"
        message = message + "|\t Freq  Lock Status: " + highlight_status('LOCKED' if self.isFreqLocked() else 'UNLOCKED') + "\n"
        message = message + "FS725 Rubidium Frequency Standard Status Summary Ends".center(80, '-') + "\n"
        self.info(message)
        return message

    @property
    def serialNumber(self):
        self.write("SN?")
        return str(self.inst.read(termination='\r'))

    def isPhaseLocked(self):
        self.write("PL?")
        # return self.inst.read() == "1"
        return self.inst.read(termination='\r') == "1"

    def isFreqLocked(self):
        self.write("LO?")
        return self.inst.read(termination='\r') == "1"
