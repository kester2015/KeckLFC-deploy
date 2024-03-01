# from Hardware import *
# import time
# import warnings

# from Hardware.InstekGPD_4303S import InstekGPD_4303S
# from Hardware.AmonicsEDFA import AmonicsEDFA
from Hardware.ORIONLaser import ORIONLaser

# edfa = AmonicsEDFA()
# edfa.connect()
# edfa.printStatus()

# import numpy as np
# import pyvisa

# rm = pyvisa.ResourceManager()
# print(rm.list_resources())
# test = rm.open_resource('ASRL8::INSTR')
# test.baud_rate = 19200
# test.read_termination = '\r\n'
# test.write(":DRIV:ACC:CUR:CH1?")
# print(test.read())

laser = ORIONLaser()
laser.writeTECsetpoint(25)
# laser.connect()
# print(laser.readStatus())
# laser.disconnect()
# amp.connect()

# print(amp.inst.write('READY?\r'))
# time.sleep(1)
# print(amp.inst.read())

# amp.inst.clear()
# amp.inst.write("READY?")
# # time.sleep(1)
# print( amp.inst.read() )
# time.sleep(1)
# print( amp.inst.read() )

# amp.printStatus()
# print(amp.ASD)

# # amp.preAmp = '0.2A'
# # amp.preAmp = 180
# # amp.activation = 0
# amp.preAmp = '600ma'
# time.sleep(1)
# amp.activation = 1
# amp.ramp_pwr_ma = 200
# amp.pwrAmp = '0.4A'
# amp.pwrAmp = '0.0A'
# amp.pwrAmp = 5000
# amp.pwrAmp = 'Max'
# print(f"PreAmp cur {amp.preAmp} mA")
# print(f"PwrAmp cur {amp.pwrAmp} mA")
# print(f"Input power {amp.inputPwr_mW} mW")
# print(f"Output power {amp.outputPwr_mW} mW")
# amp.preAmp = 0
# amp.pwrAmp = 0

# amp.activation=0
# print("Pump activation: "+amp.activation)
# amp.activation=0
# for ii in range(10):
#     amp.activation=0
# amp.printStatus()