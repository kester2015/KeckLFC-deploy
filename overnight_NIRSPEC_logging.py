filedir = r"C:\Users\HSFLFC\OneDrive - California Institute of Technology (1)\Vahala Group\Maodong\Projects\Keck\Tests after Commission\Logs\20230921"
filename = filedir+"\\"+"NIRSPEC_Test_2023_0921_1.csv"

# create dir if not exist
import os
if not os.path.exists(filedir):
    os.makedirs(filedir)

from Hardware.InstekGppDCSupply import InstekGppDCSupply
rfampPS = InstekGppDCSupply(addr='ASRL34::INSTR', name='RF amplifier PS 30V 4A')
rfampPS.connect()
rfampPS.printStatus()


from Hardware.InstekGPD_4303S import InstekGPD_4303S
rfoscPS = InstekGPD_4303S(addr='ASRL5::INSTR', name='RF oscilator PS, CH2 15V, CH3 1V')
rfoscPS.connect()
rfoscPS.printStatus()


from Hardware.ORIONLaser import ORIONLaser
rio = ORIONLaser(addr='ASRL55::INSTR')
rio.connect()
# rio.printStatus()

from Hardware.Agilent_86142B import Agilent_86142B
osa = Agilent_86142B('GPIB0::30::INSTR')
osa.connect()

from Hardware.PritelAmp import PritelAmp
ptamp = PritelAmp(addr='ASRL6::INSTR', name='Pritel Amp')
ptamp.connect()
# ptamp.printStatus()

from Hardware.AmonicsEDFA import AmonicsEDFA
amonic27 = AmonicsEDFA(addr='ASRL7::INSTR', name='Amonics EDFA 27 dBm')
amonic27.connect()
# amonic27.printStatus()

amonic23 = AmonicsEDFA(addr='ASRL13::INSTR', name='Amonics EDFA 23 dBm')
amonic23.connect()
# amonic23.printStatus()

from Hardware.SRS_SIM900 import SRS_SIM900, SRS_PIDcontrol_SIM960
srs = SRS_SIM900(addr='GPIB0::2::INSTR')
srs.connect()
servo_FC = SRS_PIDcontrol_SIM960(srs, 1, name='Filter Cavity PDH Lock Servo')
servo_IM = SRS_PIDcontrol_SIM960(srs, 3, name='Minicomb Intensity Lock Servo')
servo_RB = SRS_PIDcontrol_SIM960(srs, 5, name='Rio Laser Fceo Rb spectroscopy Lock Servo')


from Hardware.PendulumCNT90 import PendulumCNT90
cnt90 = PendulumCNT90(addr='GPIB0::10::INSTR', name='Pendulum CNT90')
cnt90.connect()


from Hardware.TEC_TC720 import TEC_TC720
# tec_PPLN = TEC_TC720(addr='ASRL46::INSTR')
tec_wg = TEC_TC720(addr='COM8', name='Octave Waveguide TEC (TC720)')
tec_wg.connect()

tec_ppln = TEC_TC720(addr='COM46', name='PPLN Doubler TEC (TC720)')
tec_ppln.connect()




import time

# If file already exists, don't write header
if not os.path.exists(filename):
    with  open(filename,"w") as f:
        #TODO: write table head
        f.write(time.strftime('%Z')+",")
        f.write("Pritel Cur (mA)"+",")

        f.write("Pritel Pwr (mW)"+",")
        f.write("Rb lock error"+",")

        f.write("Rb lock measure"+",")

        f.write("Rb lock output"+",")

        f.write("Freq Counter (Hz)"+",")

        f.write("IM lock error"+",")
        f.write("IM lock measure"+",")
        f.write("IM lock output"+",")

        f.write("PPLN Temp (C)"+",")
        f.write("WG Temp (C)"+",")

        f.write("\n")

ii = 218
while True:
    try:
        with open(filename,"a") as f:
            TSTAMP = time.ctime()

            f.write(TSTAMP+",")

            f.write(f"{ptamp.pwrAmp:.5f}"+",")
            f.write(f"{ptamp.outputPwr_mW:.5f}"+",")

            f.write(f"{servo_RB.amplified_error:.8f}"+",")
            f.write(f"{servo_RB.measure_input:.8f}"+",")
            f.write(f"{servo_RB.output_voltage:.8f}"+",")
            
            f.write(f"{cnt90.measFreq('c', log_info=True):.5f}"+",")

            f.write(f"{servo_IM.amplified_error:.8f}"+",")
            f.write(f"{servo_IM.measure_input:.8f}"+",")
            f.write(f"{servo_IM.output_voltage:.8f}"+",")
            
            f.write(f"{tec_ppln.get_temp(log_info=True):.5f}"+",")
            f.write(f"{tec_wg.get_temp(log_info=True):.5f}"+",")

            f.write("\n")

            ii = ii+1
            osa.save_trace('a',filedir+"\\"+"Minicomb" +"\\" +str(ii)+ ".mat", plot=False)
            
            servo_IM.printStatus()
            servo_RB.printStatus()
            ptamp.printStatus()

            #####
            amonic27.printStatus()
            amonic23.printStatus()
            rfampPS.printStatus()

            try:
                rfoscPS.printStatus()
            except:
                # reconnect rfoscPS
                rfoscPS.info("Data loging error: Reconnecting rfoscPS")
                time.sleep(1)
                rfoscPS.disconnect()
                time.sleep(1)
                rfoscPS.connect()
                time.sleep(1)
                rfoscPS.printStatus()

            try:
                rio.printStatus()
            except:
                # reconnect rio
                rio.info("Data loging error: Reconnecting rio")
                time.sleep(1)
                rio.disconnect()
                time.sleep(1)
                rio.connect()
                time.sleep(1)
                rio.printStatus()
            #####
    except Exception as e:
        print(e)
    time.sleep(300)