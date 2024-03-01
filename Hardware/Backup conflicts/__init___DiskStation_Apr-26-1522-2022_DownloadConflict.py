import platform
if platform.system() == 'Windows':
    from .Waveshaper import Waveshaper
from .RedPitaya import RedPitaya, FG, FPGA1
from .Servo import Servo
from .RbClock import RbClock
from .PendulumCNT90 import PendulumCNT90

from .AmonicsEDFA import AmonicsEDFA
from .PritelAmp import PritelAmp
from .InstekGPD_4303S import InstekGPD_4303S
from .InstekGppDCSupply import InstekGppDCSupply