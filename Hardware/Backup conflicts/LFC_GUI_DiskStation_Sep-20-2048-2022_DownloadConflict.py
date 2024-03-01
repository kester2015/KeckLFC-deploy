
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
        self.amamp2=AmonicsEDFA
        self.osa = AndoOSA_AQ6315E()
        self._dev_list = [self.osa]
        

    def connect_all(self):
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
        row = 0
        name_column, addr_column, alias_column, connect_column = 0,1,2,3
        
        def add_device(name, default_addr="ASRL1::INSTR", default_alias=""):
            device_layout.addWidget(QLabel(name), row, name_column)
            addr_edit = QLineEdit()
            addr_edit.setObjectName(name+"_addr_edit")
            addr_edit.setText(default_addr)
            # addr_edit.setMinimumWidth(80)
            device_layout.addWidget(addr_edit, row, addr_column)
            name_edit = QLineEdit()
            name_edit.setObjectName(name+"_name_edit")
            name_edit.setText(default_alias)
            # name_edit.setMinimumWidth(80)
            device_layout.addWidget(name_edit, row, alias_column)
            connect_button = QPushButton("connect")
            connect_button.setObjectName(name+"_connect_button")
            # connect_button.setMaximumWidth(30)
            device_layout.addWidget(connect_button, row, connect_column)
            return row # keep track of current row
        row = add_device("amamp", default_addr="ASRL13::INSTR", default_alias="23dbm AEDFA") + 1 # current row add 1
        row = add_device("amamp2", default_addr="ASRL4::INSTR") + 1
        row = add_device("ptamp", default_addr="ASRL6::INSTR") + 1
        row = add_device("RFoscPS", default_addr="ASRL5::INSTR") + 1
        row = add_device("RFampPS", default_addr="ASRL10::INSTR") + 1
        row = add_device("rbclock", default_addr="ASRL9::INSTR") + 1
        row = add_device("wsp", default_addr="SN201904") + 1
        row = add_device("rio", default_addr="ASRL12::INSTR") + 1
        row = add_device("FCtec", default_addr="ASRL18::INSTR") + 1
        row = add_device("srs", default_addr="ASRL21::INSTR") + 1
        row = add_device("osa", default_addr="GPIB0::1::INSTR") + 1

        connect_all_button = QPushButton("Connect All")
        connect_all_button.setObjectName("connect_all_button")
        # self.connect_all_button.clicked.connect(lambda:print("connect_all_button button pressed"))
        device_layout.addWidget(connect_all_button, row,1)

        device_layout.setColumnStretch(addr_column,5)
        return device_widget

    def setup_spectrum_widget(self):
        spectrum_widget = MatplotlibWidget() #QWidget()
        spectrum_widget.canvas.plot_ylim = (-80, None)
        spectrum_widget.canvas.update_xy_fun = lambda: self.dm.osa.get_trace('c',plot=False)
        # spectrum_widget.canvas.start_dynamic_plot()
        return spectrum_widget

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = MainController()
    demo.show()
    sys.exit(app.exec_())