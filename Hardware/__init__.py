import platform
if platform.system() == 'Windows':
    from .Waveshaper import Waveshaper
from .RedPitaya import RedPitaya, FG, FPGA1
from .Servo import Servo
from .RbClock import RbClock
from .PendulumCNT90 import PendulumCNT90
from .SRS_SIM900 import SRS_SIM900, SRS_PIDcontrol_SIM960

from .Agilent_86142B import Agilent_86142B

from .TEC_LFC3751 import TEC_LFC3751

from .ORIONLaser import ORIONLaser

from .AmonicsEDFA import AmonicsEDFA
from .PritelAmp import PritelAmp
from .InstekGPD_4303S import InstekGPD_4303S
from .InstekGppDCSupply import InstekGppDCSupply

from .OZopticsVOA import OZopticsVOA

from .AndoOSA_AQ6315E import AndoOSA_AQ6315E