
from Hardware.AmonicsEDFA import AmonicsEDFA
from Hardware.PritelAmp import PritelAmp
from Hardware.InstekGPD_4303S import InstekGPD_4303S
from Hardware.InstekGppDCSupply import InstekGppDCSupply
from Hardware.RbClock import RbClock
from Hardware.Waveshaper import Waveshaper
from Hardware.ORIONLaser import ORIONLaser
from Hardware.TEC_LFC3751 import TEC_LFC3751
from Hardware.SRS_SIM900 import SRS_SIM900, SRS_PIDcontrol_SIM960
from Hardware.AndoOSA_AQ6315E import AndoOSA_AQ6315E
# from .Hardware import *
# from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

from QtUserDefinedWidgets.MatplotlibWidget import MatplotlibWidget
import sys



class DeviceManager(object):
    def __init__(self,
                amamp_addr = 'ASRL13::INSTR', amamp_name = 'AEDFA 23dbm',
                amamp2_addr = 'ASRL4::INSTR', amamp2_name = 'AEDFA 13dbm',
                ptamp_addr = 'ASRL6::INSTR', ptamp_name = 'Pritel',
                RFoscPS_addr = 'ASRL5::INSTR', RFoscPS_name = 'RF osc',
                RFampPS_addr = 'ASRL10::INSTR', RFampPS_name = 'RF amp',
                rbclock_addr = 'ASRL9::INSTR', rbclock_name = 'Rb Clock',
                wsp_addr = 'SN201904', wsp_name = "WS1",
                rio_addr = 'ASRL12::INSTR', rio_name = 'RIO',
                FCtec_addr = 'ASRL18::INSTR', FCtec_name = 'FC tec',
                srs_addr = 'ASRL21::INSTR', srs_name = 'srs',
                osa_addr = 'GPIB0::1::INSTR',osa_name = 'Ando OSA',
                ) -> None:
        self.amamp_addr, self.amamp_name = amamp_addr, amamp_name
        self.amamp2_addr, self.amamp2_name = amamp2_addr, amamp2_name
        self.ptamp_addr, self.ptamp_name  = ptamp_addr, ptamp_name
        self.RFoscPS_addr, self.RFoscPS_name = RFoscPS_addr, RFoscPS_name
        self.RFampPS_addr, self.RFampPS_name = RFampPS_addr, RFampPS_name
        self.rbclock_addr, self.rbclock_name = rbclock_addr, rbclock_name
        self.wsp_addr, self.wsp_name = wsp_addr, wsp_name
        self.rio_addr, self.rio_name = rio_addr, rio_name
        self.FCtec_addr, self.FCtec_name = FCtec_addr, FCtec_name
        self.srs_addr, self.srs_name = srs_addr, srs_name
        self.osa_addr, self.osa_name = osa_addr, osa_name

    def init_device_obj(self):
        self.amamp = AmonicsEDFA(addr=self.amamp_addr, name=self.amamp_name)
        self.amamp2= AmonicsEDFA(addr=self.amamp2_addr,name=self.amamp2_name)
        self.ptamp = PritelAmp(addr=self.ptamp_addr, name=self.ptamp_name)
        self.RFampPS=InstekGppDCSupply(addr=self.RFampPS_addr, name=self.RFampPS_name)
        self.RFoscPS=InstekGPD_4303S(addr=self.RFoscPS_addr, name=self.RFoscPS_name)
        self.rbclock=RbClock(addr=self.rbclock_addr, name=self.rbclock_name)
        self.wsp = Waveshaper(addr=self.wsp_addr, WSname=self.wsp_name)
        self.rio = ORIONLaser(addr=self.rio_addr, name=self.rio_name)
        self.FCtec = TEC_LFC3751(addr=self.FCtec_addr, name=self.FCtec_name)
        self.srs = SRS_SIM900(addr=self.srs_addr, name=self.srs_name)
        self.osa = AndoOSA_AQ6315E(addr=self.osa_addr,name=self.osa_name)

        self._dev_list = [self.amamp, self.amamp2, self.ptamp, self.RFampPS, self.RFoscPS, self.rbclock,self.wsp, self.rio, self.FCtec,self.srs,self.osa]
        
    def connect_all(self):
        self.init_device_obj()
        for device in self._dev_list:
            try:
                device.connect()
            except:
                import sys
                e = sys.exc_info()[0]
                print(f"Error:{e}")


class MainWidget(QWidget):
    def __init__(self,parent=None):
        super(MainWidget,self).__init__(parent)
        self.dm = DeviceManager()
        # self.dm.connect_all()

        self.setWindowTitle("Laser Frequency Comb Controller")
        self.setupUi()

    def setupUi(self):
        # self.main_widget = QWidget()
        main_layout = QHBoxLayout(self)

        self.device_widget = self.setup_device_widget()
        main_layout.addWidget(self.device_widget)

        self.spectrum_widget = self.setup_spectrum_widget()
        main_layout.addWidget(self.spectrum_widget)

        self.locking_widget = self.setup_locking_widget()
        # self.locking_widget = self.srs_locking_widget("FC_locking")
        main_layout.addWidget(self.locking_widget)

        QtCore.QMetaObject.connectSlotsByName(self)

    @pyqtSlot()
    def on_FC_locking_start_button_clicked(self):
        print("pressed")
        self.findChild(QLineEdit, "FC_locking_out_edit").setText("0")
    @pyqtSlot()
    def on_connect_all_button_clicked(self):
        print("pressed connect_all")


    def setup_device_widget(self):
        device_widget = QWidget()
        device_layout = QGridLayout(device_widget)
        name_column, addr_column, alias_column, connect_column = 0,1,2,3
        device_layout.addWidget(QLabel("Var name"),0,name_column)
        device_layout.addWidget(QLabel("Address"),0,addr_column)
        device_layout.addWidget(QLabel("Alias"),0,alias_column)
        connect_all_button = QPushButton("Connect All")
        connect_all_button.setObjectName("connect_all_button")
        device_layout.addWidget(connect_all_button, 0, connect_column)
        
        row = 1 # start row
        def add_device(name, default_addr="", default_alias=""):
            device_layout.addWidget(QLabel(name), row, name_column)
            addr_edit = QLineEdit()
            addr_edit.setObjectName(name+"_addr_edit")
            addr_edit.setText(default_addr)
            # addr_edit.setMinimumWidth(80)
            device_layout.addWidget(addr_edit, row, addr_column)
            name_edit = QLineEdit()
            name_edit.setObjectName(name+"_alias_edit")
            name_edit.setText(default_alias)
            # name_edit.setMinimumWidth(80)
            device_layout.addWidget(name_edit, row, alias_column)
            connect_button = QPushButton("connect")
            connect_button.setObjectName(name+"_connect_button")
            # connect_button.setMaximumWidth(30)
            device_layout.addWidget(connect_button, row, connect_column)
            return row # keep track of current row
        row = add_device("amamp", default_addr="ASRL13::INSTR", default_alias="AEDFA-23") + 1 # current row add 1
        row = add_device("amamp2", default_addr="ASRL4::INSTR", default_alias="AEDFA-13") + 1
        row = add_device("ptamp", default_addr="ASRL6::INSTR", default_alias="Pritel") + 1
        row = add_device("RFoscPS", default_addr="ASRL5::INSTR", default_alias="RF osc") + 1
        row = add_device("RFampPS", default_addr="ASRL10::INSTR", default_alias="RF amp") + 1
        row = add_device("rbclock", default_addr="ASRL9::INSTR", default_alias="Rb clock") + 1
        row = add_device("wsp", default_addr="SN201904", default_alias="WSP") + 1
        row = add_device("rio", default_addr="ASRL12::INSTR", default_alias="RIO") + 1
        row = add_device("FCtec", default_addr="ASRL18::INSTR", default_alias="FC tec") + 1
        row = add_device("srs", default_addr="ASRL21::INSTR", default_alias="SRS") + 1
        row = add_device("osa", default_addr="GPIB0::1::INSTR", default_alias="Ando OSA") + 1

        return device_widget

    def setup_spectrum_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(self.osa_control_widget())
        spectrum_widget = MatplotlibWidget() #QWidget()
        spectrum_widget.canvas.plot_ylim = (-80, None)
        spectrum_widget.setObjectName("spectrum_plot_widget")
        layout.addWidget(spectrum_widget)
        # spectrum_widget.canvas.update_xy_fun = lambda: self.dm.osa.get_trace('c',plot=False)
        # spectrum_widget.canvas.start_dynamic_plot()
        return widget

    def osa_control_widget(self):
        widget = QGroupBox("OSA setup")
        layout = QGridLayout(widget)
        layout.addWidget(QLabel("StartWL"),0,0)
        start_wl_edit = QLineEdit("900")
        start_wl_edit.setObjectName("osa_start_wl_edit")
        layout.addWidget(start_wl_edit,0,1)
        layout.addWidget(QLabel("StopWL"),1,0)
        stop_wl_edit = QLineEdit("1000")
        stop_wl_edit.setObjectName("osa_stop_wl_edit")
        layout.addWidget(stop_wl_edit,1,1)
        layout.addWidget(QLabel("Trace"),2,0)
        trace_edit = QLineEdit("b")
        trace_edit.setObjectName("osa_trace_edit")
        layout.addWidget(trace_edit,2,1)

        label = QLabel("Sens")
        label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        layout.addWidget(label,2,2)
        sens_edit = QLineEdit("norm")
        sens_edit.setObjectName("osa_sens_edit")
        layout.addWidget(sens_edit,2,3)

        start_osa_button = QPushButton("StartOSA")
        start_osa_button.setObjectName("osa_start_button")
        layout.addWidget(start_osa_button,0,2)
        stop_osa_button = QPushButton("StopOSA")
        stop_osa_button.setObjectName("osa_stop_button")
        layout.addWidget(stop_osa_button,0,3)
        single_osa_button = QPushButton("SingleOSA")
        single_osa_button.setObjectName("osa_single_button")
        layout.addWidget(single_osa_button,0,4)

        layout2 = QVBoxLayout()
        save_filename_edit = QLineEdit("To save File dir here")
        save_filename_edit.setObjectName("osa_save_filename_edit")
        layout2.addWidget(save_filename_edit)
        layout.addLayout(layout2,1,2,1,3)

        save_osa_button = QPushButton("Single and Save OSA")
        save_osa_button.setObjectName("osa_save_button")
        layout.addWidget(save_osa_button,2,4)

        return widget

    def setup_locking_widget(self):
        locking_widget = QWidget()
        locking_layout = QVBoxLayout(locking_widget)
        
        locking_layout.addWidget(self.srs_locking_widget("FC_locking"))
        locking_layout.addWidget(self.srs_locking_widget("IM_locking"))
        locking_layout.addWidget(self.srs_locking_widget("LLC_locking"))
        return locking_widget

    def srs_locking_widget(self, name): # srs: stanford research system, SIM960 module
        widget = QGroupBox(name)
        grid = QGridLayout(widget)

        grid.addWidget(QLabel("P"),0,0)
        p_edit_line = QLineEdit()
        p_edit_line.setObjectName(name+"_p_edit")
        grid.addWidget(p_edit_line,0,1)

        grid.addWidget(QLabel("I"),1,0)
        i_edit_line = QLineEdit()
        i_edit_line.setObjectName(name+"_i_edit")
        grid.addWidget(i_edit_line,1,1)

        grid.addWidget(QLabel("D"),2,0)
        d_edit_line = QLineEdit()
        d_edit_line.setObjectName(name+"_d_edit")
        grid.addWidget(d_edit_line,2,1)

        grid.addWidget(QLabel("SetPoint"),0,2)
        sp_edit_line = QLineEdit()
        sp_edit_line.setObjectName(name+"_sp_edit")
        grid.addWidget(sp_edit_line,0,3)

        grid.addWidget(QLabel("Manual"),1,2)
        man_edit_line = QLineEdit()
        man_edit_line.setObjectName(name+"_man_edit")
        grid.addWidget(man_edit_line,1,3)

        grid.addWidget(QLabel("Output"),2,2)
        out_edit_line = QLineEdit()
        out_edit_line.setObjectName(name+"_out_edit")
        grid.addWidget(out_edit_line,2,3)

        start_button = QPushButton("Start")
        start_button.setObjectName(name+"_start_button")
        grid.addWidget(start_button, 3,3)

        return widget


class MainController(MainWidget):
    def __init__(self) -> None:
        super().__init__()
        self.dm = DeviceManager(amamp_addr = self.findChild(QLineEdit,"amamp_addr_edit").text(), amamp_name = self.findChild(QLineEdit,"amamp_alias_edit").text(),
                                amamp2_addr = self.findChild(QLineEdit,"amamp_addr_edit").text(), amamp2_name = self.findChild(QLineEdit,"amamp2_alias_edit").text(),
                                ptamp_addr = self.findChild(QLineEdit,"ptamp_addr_edit").text(), ptamp_name = self.findChild(QLineEdit,"ptamp_alias_edit").text(),
                                RFoscPS_addr = self.findChild(QLineEdit,"RFoscPS_addr_edit").text(), RFoscPS_name = self.findChild(QLineEdit,"RFoscPS_alias_edit").text(),
                                RFampPS_addr = self.findChild(QLineEdit,"RFampPS_addr_edit").text(), RFampPS_name = self.findChild(QLineEdit,"RFampPS_alias_edit").text(),
                                rbclock_addr = self.findChild(QLineEdit,"rbclock_addr_edit").text(), rbclock_name = self.findChild(QLineEdit,"rbclock_alias_edit").text(),
                                wsp_addr = self.findChild(QLineEdit,"wsp_addr_edit").text(), wsp_name = self.findChild(QLineEdit,"wsp_alias_edit").text(),
                                rio_addr = self.findChild(QLineEdit,"rio_addr_edit").text(), rio_name = self.findChild(QLineEdit,"rio_alias_edit").text(),
                                FCtec_addr = self.findChild(QLineEdit,"FCtec_addr_edit").text(), FCtec_name = self.findChild(QLineEdit,"FCtec_alias_edit").text(),
                                srs_addr = self.findChild(QLineEdit,"srs_addr_edit").text(), srs_name = self.findChild(QLineEdit,"srs_alias_edit").text(),
                                osa_addr = self.findChild(QLineEdit,"osa_addr_edit").text(),osa_name = self.findChild(QLineEdit,"osa_alias_edit").text(),
                                )
    @pyqtSlot()
    def on_connect_all_button_clicked(self):
        self.dm.connect_all()
    @pyqtSlot()
    def on_amamp_connect_button_clicked(self):
        self.dm.amamp.connect()
    @pyqtSlot()
    def on_amamp2_connect_button_clicked(self):
        self.dm.amamp2.connect()
    @pyqtSlot()
    def on_ptamp_connect_button_clicked(self):
        self.dm.ptamp.connect()
    @pyqtSlot()
    def on_RFoscPS_connect_button_clicked(self):
        self.dm.RFoscPS.connect()
    @pyqtSlot()
    def on_RFampPS_connect_button_clicked(self):
        self.dm.RFampPS.connect()
    @pyqtSlot()
    def on_rbclock_connect_button_clicked(self):
        self.dm.rbclock.connect()
    @pyqtSlot()
    def on_wsp_connect_button_clicked(self):
        self.dm.wsp.connect()
    @pyqtSlot()
    def on_rio_connect_button_clicked(self):
        self.dm.rio.connect()
    @pyqtSlot()
    def on_FCtec_connect_button_clicked(self):
        self.dm.FCtec.connect()
    @pyqtSlot()
    def on_srs_connect_button_clicked(self):
        self.dm.srs.connect()
    @pyqtSlot()
    def on_osa_connect_button_clicked(self):
        self.dm.osa.connect()

    @pyqtSlot()
    def on_osa_start_button_clicked(self):
        self.dm.osa.Run()
        trace = self.findChild(QLineEdit,"osa_trace_edit").text()
        canvas = self.findChild(MatplotlibWidget,"spectrum_plot_widget").canvas
        canvas.update_xy_fun = lambda: self.dm.osa.get_trace(trace,plot=False)
        canvas.start_dynamic_plot()

    @pyqtSlot()
    def on_osa_stop_button_clicked(self):
        self.dm.osa.Run()
        trace = self.findChild(QLineEdit,"osa_trace_edit").text()

        canvas = self.findChild(MatplotlibWidget,"spectrum_plot_widget").canvas
        canvas.update_xy_fun = lambda: self.dm.osa.get_trace(trace,plot=False)
        canvas.start_dynamic_plot()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = MainController()
    demo.show()
    sys.exit(app.exec_())