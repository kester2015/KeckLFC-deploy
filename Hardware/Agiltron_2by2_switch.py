from .Device import Device


from typing import Optional

import pyvisa
from pyvisa.constants import Parity


# def check_port(fiber_port: int, number_of_ports: int) -> bool:
#     """
#     Check if given fiber port is an integer and in the range of valid fiber ports.

#     Args:
#         port (int): fiber port to switch to
#         number_of_ports (int): total number of fiber ports on the switch

#     Raises:
#         TypeError: unsupported type for the fiber port
#         ValueError: fiber port out of range

#     Returns:
#         bool: returns True if the fiber port is valid, False otherwise
#     """
#     if not isinstance(fiber_port, int):
#         raise TypeError(f"unsupported type for fiber port: {type(fiber_port)}")
#     v = (fiber_port > 0) & (fiber_port <= number_of_ports)
#     if not v:
#         raise ValueError(f"fiber port {fiber_port} out of range")
#     else:
#         return v


class AgiltronSelfAlign22(Device):
    def __init__(self, addr='COM49', name='Agiltron 2 by 2 switch'):
        # resource_name: str, timeout: int = 2, number_of_ports: int = 16,):
        super().__init__(addr=addr, name=name, isVISA=False)

        self.rm = pyvisa.ResourceManager()
        self.instrument = self.rm.open_resource(
            resource_name=self.addr,
            timeout=2,
            parity=Parity.none,
            data_bits=8,
            baud_rate=9600,
            write_termination="\r\n",
            read_termination="\r\n",
        )
        # self.number_of_ports: int = 2
        self.status: Optional[int] = None

        # status 1 YJ, status 2 HK comb

        self.isVISA = True
        self.inst = self.instrument # for compatibility with Device class


    # def home(self) -> None:
    #     """
    #     Home the fiber switch, i.e. move to port 1.
    #     """
    #     self.instrument.write_raw(b"\x01\x12\x00\x00")


    # def set_status(self, fiber_port: int) -> None:
    #     """
    #     Switch fiber switch to port `fiber_port`.

    #     Args:
    #         fiber_port (int): fiber port to switch to
    #     """
    #     self.instrument.clear()
    #     check_port(fiber_port, self.number_of_ports)
    #     if fiber_port != self.fiber_port:
    #         cmd = b"\x01\x12\x00" + bytes([fiber_port])
    #         self.instrument.write_raw(cmd)
    #         # ret = self.instrument.read_bytes(4)
    #         # assert (
    #         #     ret == b"\x01\x35\xff\xff"
    #         # ), f"invalid return message, fiber port not set to {fiber_port}"
    #         self.fiber_port = fiber_port
    
    def check_mode_version(self):
        self.instrument.write_raw(b"\x01\x06\x00\x00")
        ret = self.instrument.read_bytes(4)
        #self.info(ret)
        assert (
            ret == b"\x01\x06\x15\x1f"
        ), f"wrong mode version, should be 0x15, 0x1f, but got {ret}. need further investigation"

    def check_status(self):
        self.instrument.write_raw(b"\x01\x13\x00\x00")
        ret = self.instrument.read_bytes(4)
        #self.info(ret)
        status_dict={1: b"\x01\x13\x01\x00", 2: b"\x01\x13\x02\x00"}
        "if ret belongs to status_dict, return the key, else return wrong status"
        for key, value in status_dict.items():
            if ret == value:
                return key
        return Warning(f"wrong status, should be 1 or 2, but got {ret}. need further investigation")
    
    def set_status(self, status: int) -> None:
        #self.instrument.clear()
        self.check_mode_version()
        self.status = self.check_status()
        if status != self.status:
            cmd = b"\x01\x14\x00" + bytes([status])
            self.instrument.write_raw(cmd)
            ret = self.instrument.read_bytes(4) 
            assert (
                ret == b"\x01\x14" + bytes([status]) + b"\x00"
            ), f"invalid return message, status not set to {status}"
            self.info(f"status set to {status}")
            self.status = status
        else:
            pass





       