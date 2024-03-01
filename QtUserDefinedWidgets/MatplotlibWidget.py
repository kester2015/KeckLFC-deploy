import sys
import random
import matplotlib

matplotlib.use("Qt5Agg")
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QSizePolicy, QWidget
from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# This is a user defined class
class MyMplCanvas(FigureCanvas):
    """The ultimate parent class of FigureCanvas is QWidget """

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)  # create a new figure
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        self.axes = self.fig.add_subplot(111)  # create one subplot

        self.update_xy_fun = lambda: ([0,1,2,3], [random.randint(0, 10) for i in range(4)])
        self.update_time = 1000

        self.dynamic = False
        self.updating = False
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_figure)  # connect update_figure function to timeout signal

        self.plot_title = "Spectrum"
        self.plot_xlabel = "Wavelength (nm)"
        self.plot_ylabel = "Power (dBm)"
        self.plot_xlim = (None, None)
        self.plot_ylim = (None, None)
        

        '''Set FigureCanvas to Extend to outside as much as possible'''
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def start_dynamic_plot(self, *args, **kwargs):
        self.updating = True
        self.timer.start(self.update_time)  # trigger timeout every  self.update_time miliseconds

    def stop_dynamic_plot(self,*args, **kwargs):
        self.updating = False
        self.timer.stop()

    def update_figure(self): # can be rewritten
        self.fig.suptitle(self.plot_title)
        x,y = self.update_xy_fun()
        self.axes.clear()
        self.axes.plot(x,y, 'b')
        self.axes.set_ylabel(self.plot_ylabel)
        self.axes.set_xlabel(self.plot_xlabel)
        self.axes.set_xlim(self.plot_xlim)
        self.axes.set_ylim(self.plot_ylim)
        self.axes.grid(True)
        self.draw()

class MatplotlibWidget(QWidget):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        super(MatplotlibWidget, self).__init__(parent)
        self.canvas = MyMplCanvas(self, width=width, height=height, dpi=dpi)
        self.initUi()

    def initUi(self):
        self.layout = QVBoxLayout(self)
        # self.start_static_plot() # 
        # self.start_dynamic_plot() # 
        self.toolbar = NavigationToolbar(self.canvas, self)  # Add toolbar

        self.layout.addWidget(self.canvas)
        self.layout.addWidget(self.toolbar)