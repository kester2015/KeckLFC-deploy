import numpy as np
import matplotlib.pyplot as plt
import warnings
import time
from scipy.io import loadmat


# file_dir1=r'D:\astrocomb\matlab\RB_cell_peak.mat'
# file_dir2=r'D:\astrocomb\matlab\RB_cell_peak2.mat'
# file_dir3=r'D:\astrocomb\matlab\RB_cell_peak3.mat'

# from LFC.Hardware.SRS_SIM900 import SRS_SIM900, SRS_PIDcontrol_SIM960
# srs = SRS_SIM900(addr='GPIB0::2::INSTR')
# srs.connect()
# servo_FC = SRS_PIDcontrol_SIM960(srs, 1, name='Filter Cavity PDH Lock Servo')
# servo_IM = SRS_PIDcontrol_SIM960(srs, 3, name='Minicomb Intensity Lock Servo')
# servo_RB = SRS_PIDcontrol_SIM960(srs, 5, name='Rio Laser Fceo Rb spectroscopy Lock Servo')


class AutoRbLock():
    def __init__(self, osc, fg, servo_RB):
        self.osc = osc
        self.fg = fg
        self.servo_RB = servo_RB
        self.file_dir1 = r"C:\Users\HSFLFC\Desktop\Keck\Keck Comb\LFC\Rb_locking_data\01.npy"
        self.file_dir2 = r"C:\Users\HSFLFC\Desktop\Keck\Keck Comb\LFC\Rb_locking_data\02.npy"
        self.file_dir3 = r"C:\Users\HSFLFC\Desktop\Keck\Keck Comb\LFC\Rb_locking_data\03.npy"

    def load_history_trace(self, file_dir):
        # data = loadmat(file_dir)
        # xx=data['X']
        # yy=data['Y']
        # xx=xx.flatten()
        # yy=yy.flatten()
        # return xx,yy
        data = np.load(file_dir)
        xx = data[0]
        yy = data[1]
        return xx, yy

    def change_scan_range(self,start,stop):
        amplitude = stop - start
        ofset = (stop + start)/2
        self.fg.set_channel_frequency(channel=1, freq=10,amp=amplitude,offset=ofset,phase=0 )
        #return start,stop
        # TODO: use fg to change

    def get_trace(self, trace = 1):

        wvfm = self.osc.get_trace(trace)
        x=wvfm['X']
        y=wvfm['Y']
        return x,y


    def cvv(self,x,y,step):    #x,y is real trace, corex,corey is history trace
        if step==1:
            corex,corey=self.load_history_trace(self.file_dir1)
        elif step==2:
            corex,corey=self.load_history_trace(self.file_dir2)
        elif step==3:
            corex,corey=self.load_history_trace(self.file_dir3)
        else:
            warnings.warn('step is wrong')

        # start=1110
        # end=1240
        # corex=x[start:end]
        # corey=y[start:end]
        # plt.plot(x,y)
        # plt.plot(corex,corey)

        aver_corey=sum(corey)/len(corey)
        renormal_y=y-aver_corey
        renormal_corey=corey-aver_corey
        # plt.plot(x,renormal_y)
        # plt.plot(corex,renormal_corey)

        cvv=np.convolve(renormal_corey[::-1],renormal_y,'same')
        #cvv2=np.convolve(renormal_corey,renormal_y,'same')
        len_core=len(renormal_corey)
        len_data=len(renormal_y)
        max_position=np.argmax(cvv[round(len_core/2):len_data-round(len_core/2)])+round(len_core/2)
        print(f'max position={max_position}')
        plt.plot(x,renormal_y)
        #plt.plot(x,cvv2)
        plt.plot(corex,renormal_corey)
        plt.plot(x,cvv)
        plt.plot(x[max_position],cvv[max_position],'o')
        plt.show()
        time.sleep(0.5)

        amp=self.fg.get_channel_amplitude(channel=1)
        offset=self.fg.get_channel_offset(channel=1)

        start=offset-amp/2
        stop=offset+amp/2

        new_offset=start+(stop-start)*max_position/len_data
        new_amp=(stop-start)*len_core/len_data

        return new_amp,new_offset,max_position,cvv[max_position]

    def scan_offset(self,step):
        amp=self.fg.get_channel_amplitude(channel=1)
        offset=self.fg.get_channel_offset(channel=1)
        maxp=[]
        for i in list(range(11)):
            ofset=offset+(i-5)*0.1*amp
            self.fg.set_channel_parameters(channel=1, freq=10, amp=amp, offset=ofset, phase=0)
            time.sleep(24)
            x,y=self.get_trace()
            _,newoff,maxp1,maxv=self.cvv(x,y,step)
            maxp.append([maxv,maxp1,newoff])
        
        #maxp=np.array(maxp)
        biggest=sorted(maxp,key=lambda x:x[0],reverse=True)
        biggest=biggest[0:5]
        maxp=np.array(biggest)
        len_data=len(y)
        position=np.argmin(abs(maxp[:,1]-0.5*len_data))
        new_offset=maxp[position,2]

        return new_offset


    def lock(self,amp_lock,offset_lock):
        self.fg.set_channel_func(1, 'dc')
        self.fg.set_channel_parameters(channel=1, freq=10, amp=amp_lock, offset=offset_lock, phase=0)
        self.fg.set_channel_state(1, 1)
        self.servo_RB.output_mode = 'pid'

        self.fg.get_channel_parameters(1)
        self.servo_RB.printStatus()

    def lock_test(self,amp_test):
        amp_test=amp_test/2
        offset_test=self.fg.get_channel_offset(channel=1)
        #amp_test=0.01
        self.fg.set_channel_parameters(channel=1, freq=10, amp=amp_test, offset=offset_test, phase=0)
        self.fg.set_channel_func(1, 'ramp')
        self.fg.set_channel_state(1, 1)

        self.fg.get_channel_parameters(1)
        shift=[]
        
        for i in list(range(30)):
            shift.append(self.servo_RB.output_voltage)
            time.sleep(0.02)

        shift=np.array(shift)
        hight=np.max(shift)-np.min(shift)

        plt.plot(shift)
        plt.show()
        time.sleep(0.5)
        if (hight>amp_test/2) & (hight<amp_test*2):
            self.fg.set_channel_func(1, 'dc')
            print('lock success')
            return 1
            
        else:
            warnings.warn('lock fail')
            return 0
        
    
    def end_lock(self):
        self.fg.set_channel_state(1, 0)
        self.servo_RB.output_mode='man'

        self.fg.get_channel_parameters(1)
        self.servo_RB.printStatus()
    

        











if __name__ == '__main__':
    from LFC.Hardware.SRS_SIM900 import SRS_SIM900, SRS_PIDcontrol_SIM960
    srs = SRS_SIM900(addr='GPIB0::2::INSTR')
    srs.connect()
    servo_FC = SRS_PIDcontrol_SIM960(srs, 1, name='Filter Cavity PDH Lock Servo')
    servo_IM = SRS_PIDcontrol_SIM960(srs, 3, name='Minicomb Intensity Lock Servo')
    servo_RB = SRS_PIDcontrol_SIM960(srs, 5, name='Rio Laser Fceo Rb spectroscopy Lock Servo')
    from LFC.Hardware.TDS2024C import TDS2024C
    osc = TDS2024C()
    osc.connect()
    from LFC.Hardware.KeysightFG_33500 import KeysightFG_33500
    fg = KeysightFG_33500(addr='USB0::0x0957::0x2807::MY59003824::INSTR', name='Keysight FG 33500')
    fg.connect()
    from LFC.Hardware import autolock
    import time
    import matplotlib.pyplot as plt
    autolock = autolock.AutoRbLock(osc, fg, servo_RB)

    # tart with full trace amp=8, offset=0
    servo_RB.output_mode='man'
    fg.set_channel_parameters(channel=1, freq=10, amp=8, offset=0, phase=0)
    fg.set_channel_func(1, 'ramp')
    fg.set_channel_state(1, 1)
    time.sleep(24)
    trace_x,trace_y=autolock.get_trace(trace = 1)
    plt.plot(trace_x,trace_y)
    plt.show()
    time.sleep(0.5)

    # get step 1 trace
    namp,noffset,_,_=autolock.cvv(trace_x,trace_y,1)
    print(namp,noffset)

    # scan step 1 trace, get better offset
    fg.set_channel_parameters(channel=1, freq=10, amp=namp, offset=noffset, phase=0)
    noffset=autolock.scan_offset(step=2)

    #set to find step 2 trace
    fg.set_channel_parameters(channel=1, freq=10, amp=namp, offset=noffset, phase=0)
    time.sleep(24)
    trace_x,trace_y=autolock.get_trace(trace = 1)
    plt.plot(trace_x,trace_y)
    plt.show()
    time.sleep(0.5)

    #find step 2 trace, amp and offset
    namp,noffset,_,_=autolock.cvv(trace_x,trace_y,2)
    print(namp,noffset)

    #go directly to step 3 trace, no scan offset
    fg.set_channel_parameters(channel=1, freq=10, amp=namp, offset=noffset, phase=0)
    time.sleep(24)
    trace_x,trace_y=autolock.get_trace(trace = 1)
    plt.plot(trace_x,trace_y)
    plt.show()
    time.sleep(0.5)

    namp,noffset,_,_=autolock.cvv(trace_x,trace_y,3)
    print(namp,noffset)

    # lock and lock test
    autolock.lock(namp,noffset)
    time.sleep(2)
    autolock.lock_test(namp)

###################End of auto lock######################


        

