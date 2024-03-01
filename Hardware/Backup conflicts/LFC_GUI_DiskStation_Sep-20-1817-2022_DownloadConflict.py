
from Hardware.AndoOSA_AQ6315E import AndoOSA_AQ6315E

# from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

from QtUserDefinedWidgets.MatplotlibWidget import MatplotlibWidget
import sys



class DeviceManager(object):
    def __init__(self) -> None:
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
        def add_device(name, default_addr="COM0"):
            device_layout.addWidget(QLabel(name), row, 0)
            addr_edit = QLineEdit()
            addr_edit.setObjectName(name+"_addr_edit")
            device_layout.addWidget(addr_edit, row, 1)
            row=row+1
        add_device("")
        connect_all_button = QPushButton("Connect All")
        connect_all_button.setObjectName("connect_all_button")
        # self.connect_all_button.clicked.connect(lambda:print("connect_all_button button pressed"))
        device_layout.addWidget(self.connect_all_button, row,1)
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



if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = MainWidget()
    demo.show()
    sys.exit(app.exec_())