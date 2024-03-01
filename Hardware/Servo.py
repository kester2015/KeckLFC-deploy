import numpy as np
import threading, time
from collections import deque


class Servo():
    def __init__(self, finput, foutput, name='Servo'):
        self.fin = finput
        self.fout = foutput
        self.name = name
        self.dt = 0.001
        self.P = 1
        self.I = 0
        self.D = 0
        self.buffersize = 1024
        self.setpoint = 0
        self.locked = False
        self.locking = False
        self.monitor = False
        self.tol = 4e-3

    def start(self, setpoint, y0, ylim):
        self.y = y0
        self.ylim = ylim
        import matplotlib.pyplot as plt
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(1, 1, 1)
        if not self.locking:
            self.locking = True
            self.worker = threading.Thread(target=self.process,
                                           args=(setpoint, ))
            self.worker.start()
            self.info(f"{self.name} started")

    def stop(self):
        self.locking = False
        self.info(f"{self.name} stoped")

    def stop(self):
        self.locking = False
        self.info(f"{self.name} stoped")

    def process(self, setpoint):
        self.q = deque()
        self.setpoint = setpoint
        while self.locking:
            self.x = self.fin(0)  # Dummy args for lambda x expression
            self.q.append(self.x)
            if len(self.q) < 10:
                time.sleep(self.dt)
                continue
            if len(self.q) > self.buffersize:
                self.q.popleft()

            Pdx = self.setpoint - self.x
            Idx = self.setpoint - np.mean(self.q)
            self.locked = np.abs(Pdx) < self.tol
            Ddx = self.q[-1] - self.q[-2]
            self.y += self.P * (Pdx + self.I * Idx) + self.D * Ddx
            if self.y > self.ylim[1]:
                self.y = self.ylim[1]
                self.locked = False
            elif self.y < self.ylim[0]:
                self.y = self.ylim[0]
                self.locked = False
            self.fout(self.y)
            if self.monitor:
                worker = threading.Thread(target=self.plot)
                worker.run()
            time.sleep(self.dt)

    def plot(self):
        from IPython.display import display, clear_output
        self.ax.cla()
        self.ax.plot(self.q)
#         self.ax.set_ylim(self.setpoint - self.tol * 20,
#                          self.setpoint + self.tol * 20)
        display(self.fig)
        self.info(f"Locked:{self.locked}, x:{self.x}, y:{self.y}")
        clear_output(wait=True)

    def tune(self,
             dt=None,
             ylim=None,
             P=None,
             I=None,
             D=None,
             buffersize=None,
             setpoint=None):
        if dt != None:
            self.dt = dt
        if ylim != None:
            self.ylim = ylim
        if P != None:
            self.P = P
        if I != None:
            self.I = I
        if D != None:
            self.D = D
        if buffersize != None:
            self.buffersize = buffersize
        if setpoint != None:
            self.setpoint = setpoint