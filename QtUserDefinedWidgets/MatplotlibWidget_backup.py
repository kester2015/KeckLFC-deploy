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


class MyMplCanvas(FigureCanvas):
    """FigureCanvas的最终的父类其实是QWidget。"""

    def __init__(self, parent=None, width=5, height=4, dpi=100):

        self.fig = Figure(figsize=(width, height), dpi=dpi)  # 新建一个figure
        self.axes = self.fig.add_subplot(111)  # 建立一个子图，如果要建立复合图，可以在这里修改

        # self.axes.hold(False)  # 每次绘图的时候不保留上一次绘图的结果
        def t():
            return [0,1,2,3], [random.randint(0, 10) for i in range(4)]
        self.update_xy_fun = t
        self.update_time = 1000
        self.plot_title = "Spectrum"
        self.plot_xlabel = "Wavelength (nm)"
        self.plot_ylabel = "Power (dBm)"

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        '''定义FigureCanvas的尺寸策略，这部分的意思是设置FigureCanvas，使之尽可能的向外填充空间。'''
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    # '''绘制静态图，可以在这里定义自己的绘图逻辑'''

    # def start_static_plot(self):
    #     self.fig.suptitle(self.plot_title)
    #     t = arange(0.0, 3.0, 0.01)
    #     s = sin(2 * pi * t)
    #     self.axes.plot(t, s)
    #     self.axes.set_ylabel(self.plot_ylabel)
    #     self.axes.set_xlabel(self.plot_xlabel)
    #     self.axes.grid(True)

    '''启动绘制动态图'''

    def start_dynamic_plot(self, *args, **kwargs):
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)  # 每隔一段时间就会触发一次update_figure函数。
        timer.start(self.update_time)  # 触发的时间间隔为3秒。

    '''动态图的绘图逻辑可以在这里修改'''

    def update_figure(self):
        self.fig.suptitle(self.plot_title)
        # l = [random.randint(0, 10) for i in range(4)]
        x,y = self.update_xy_fun()
        self.axes.clear()
        self.axes.plot(x,y, 'b')
        self.axes.set_ylabel(self.plot_ylabel)
        self.axes.set_xlabel(self.plot_xlabel)
        self.axes.grid(True)
        self.draw()


class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super(MatplotlibWidget, self).__init__(parent)
        self.initUi()

    def initUi(self):
        self.layout = QVBoxLayout(self)
        self.mpl = MyMplCanvas(self, width=5, height=4, dpi=100)
        # self.mpl.start_static_plot() # 如果你想要初始化的时候就呈现静态图，请把这行注释去掉
        # self.mpl.start_dynamic_plot() # 如果你想要初始化的时候就呈现动态图，请把这行注释去掉
        self.mpl_ntb = NavigationToolbar(self.mpl, self)  # 添加完整的 toolbar

        self.layout.addWidget(self.mpl)
        self.layout.addWidget(self.mpl_ntb)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MatplotlibWidget()
    # ui.mpl.start_static_plot()  # 测试静态图效果
    ui.mpl.start_dynamic_plot() # 测试动态图效果
    ui.show()
    sys.exit(app.exec_()) 
