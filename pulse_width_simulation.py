import numpy as np
import matplotlib.pyplot as plt

class PulseGenerator:
    def __init__(self,frep,T,Pin_ave, f_c = 192):
        self.f_rep = frep
        self.f_c = f_c
        self.T = T
        self.NT = T.shape[-1] # number of time points
        self.dT = T[1] - T[0] # time interval
        self.Pin_ave = Pin_ave # average input power
        f = np.fft.fftfreq(self.NT, d=self.dT) # frequency points
        self.f = np.fft.fftshift(f_c - f) # frequency points

    def getSech2Pulse(self,T_FWHM):
        T0 = T_FWHM / 1.763
        P0 = self.Pin_ave / self.f_rep / 2 / T0
        A0 = np.sqrt(P0) / np.cosh(self.T / T0)
        if self.checkPulseEnergy(A0):
            return A0
        else:
            return None

    def getGaussianPulse(self,T_FWHM):
        T0 = T_FWHM / np.sqrt(2) / np.sqrt(np.log(2))
        P0 = self.Pin_ave / np.sqrt(np.pi / 2) / self.f_rep / T0
        A0 = np.sqrt(P0) * np.exp(-(self.T / T0)**2)
        if self.checkPulseEnergy(A0):
            return A0
        else:
            return None
    
    def getEOMPulse(self,LineNum):
        # EO Modulation
        MD_PM = LineNum / 2  # Modulation Depth of PMs
        Att = 0.5
        P_DC = np.pi / 2
        MD_IM = np.pi / 2  # Modulation Depth of IM
        A0 = np.sqrt(self.Pin_ave/Att) \
            * np.exp(1j * MD_PM * np.sin(2 * np.pi * self.f_rep * self.T)) \
            * np.cos(P_DC/2 + MD_IM/2 * np.sin(2 * np.pi * self.f_rep * self.T))
        if self.checkPulseEnergy(A0):
            return A0
        else:
            return None
    
    def addDispersion(self, A0, disp2):
        c_const = 299792.458
        Aw = np.fft.fft(A0)
        N_side = self.T.shape[-1] // 2
        b2 = 2 * np.pi * disp2 * c_const * (self.f_rep / self.f_c)**2
        Aw[-N_side:] *= np.exp(1j * b2 * np.arange(-N_side, 0)**2 / 2)
        Aw[:N_side] *= np.exp(1j * b2 * np.arange(0, N_side)**2 / 2)
        return np.fft.ifft(Aw)

    def evaluate(self, A):
        self.plotpulse(A)
        self.plotspectrum(A)
        _,_,pw = self.getautocorrelation(A)
        print(f'pulse width {self.getpulsewidth(A)} ps, autocorrelation width {pw} ({pw * 0.648}) ps, power {self.getPower(A)} W')

    def getPower(self,A):
        I0 = np.abs(A)**2
        E_pulse0 = np.sum(I0) * self.dT
        return E_pulse0 * self.f_rep

    def checkPulseEnergy(self,A0):
        P0_ave = self.getPower(A0)
        return P0_ave / self.Pin_ave > 0.98 and P0_ave / self.Pin_ave < 1.02

    def getpulsewidth(self, A):
        I = np.abs(A)**2
        I = I / np.max(I)
        N = len(np.where(I > 0.5)[0])
        return self.dT * N

    def plotpulse(self,A):
        I = np.abs(A)**2
        plt.figure(2)
        plt.plot(self.T, I)
        plt.show()

    def plotspectrum(self,A, l_min = 1520, l_max = 1600):
        L = 299792.458 / self.f
        Aw = np.fft.fft(A)
        Aw = np.fft.fftshift(Aw)
        Iw = 20 * np.log10(np.abs(Aw))
        lidxrange = np.where((L > l_min) & (L < l_max))[0]
        L = L[lidxrange]
        Iw = Iw[lidxrange]
        plt.figure(3)
        plt.plot(L, Iw)
        plt.show()

    def getautocorrelation(self, A):
        I_corr = np.zeros(self.NT)
        A2 = A
        for ii in range(self.NT):
            A2 = np.roll(A2, 1)
            I_corr[ii] = np.abs(np.sum(A * A2))**2
        I_corr = np.fft.fftshift(I_corr)
        I_corr = I_corr / np.max(I_corr)
        PulseWidth = len(np.where(I_corr > 0.5)[0]) * self.dT
        return self.T, I_corr, PulseWidth


class PulseSim:
    c_const = 299792.458

    def __init__(self, length, alpha, beta, gamma, loss = 0):
        self.length = length
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.spliceloss = loss # power loss in dB

    def input(self, T, A0, f0):  # ps W THz
        self.T = T
        self.NT = T.shape[-1]
        self.dT = T[1] - T[0]
        self.A0 = A0 * 10 ** (-self.spliceloss/20)
        self.f0 = f0

    def setup(self, Nsteps, method):
        self.Nsteps = Nsteps
        self.AA = []
        self.AAw = []
        self.Z = np.linspace(0, self.length, Nsteps)
        self.dz = self.Z[1] - self.Z[0]

        f = np.fft.fftfreq(self.NT, d=self.dT)
        D = -self.alpha / 2
        n = 2
        for b in self.beta:
            D += 1j * b * (-2 * np.pi * f)**n / np.math.factorial(n)
            n += 1
        self.delta = D

        f = self.f0 - f  # exp(i k x(T) - i w t)
        self.F = np.fft.fftshift(f)

        if method == 'RK4IP':
            self.next = self.RK4IP_next
        elif method == 'SSS':
            self.next = self.SSS_next
        else:
            self.next = self.RK4IP_next

    def A2f(self, A):
        Aw = np.fft.fft(A)
        return np.fft.fftshift(Aw)

    def D_op(self, A, dz):  # [exp^(D*dz)] A
        Aw = np.fft.fft(A)
        Aw = Aw * np.exp(dz * self.delta)
        return np.fft.ifft(Aw)

    def N_op(self, A, dz):  # [N * dz] A
        return 1j * self.gamma * dz * np.abs(A)**2 * A

    def RK4IP_next(self, A, h):
        AI = self.D_op(A, h / 2)
        k1 = self.D_op(self.N_op(A, h), h / 2)
        k2 = self.N_op(AI + k1 / 2, h)
        k3 = self.N_op(AI + k2 / 2, h)
        k4 = self.N_op(self.D_op(AI + k3, h / 2), h)
        A = self.D_op(AI + k1 / 6 + k2 / 3 + k3 / 3, h / 2) + k4 / 6
        return A

    def SSS_next(self, A, h):
        A1 = self.D_op(A, h / 2)
        A2 = A1 + self.N_op(A1, h)
        A = self.D_op(A2, h / 2)
        return A

    def calc(self, Nsteps, method='RK4IP'):
        self.setup(Nsteps, method)
        A = self.A0
        for z in self.Z:
            A = self.next(A, self.dz)
            self.AA.append(A)
            Aw = self.A2f(A)
            self.AAw.append(Aw)

    def plot(self, l_min, l_max):
        # Filter outputs
        self.Iw = 20 * np.log10(np.abs(self.AAw))
        L = self.c_const / self.F
        lidxrange = np.where((L > l_min) & (L < l_max))[0]
        L = L[lidxrange]
        Iw = [f[lidxrange] for f in self.Iw]
        # plot
        plt.figure(1)
        plt.pcolormesh(L, self.Z, Iw, cmap='jet')
        plt.show()

    def output(self):
        return self.T, self.AA[-1]
    
    def getA(self, z):
        return self.AA[np.argmin(np.abs(self.Z - z))]

    def plotpulse(self, z=None, shift=False):
        if z is None:
            z = self.Z[-1]
        T = self.T
        I = np.abs(self.AA[np.argmin(np.abs(self.Z - z))])**2
        if shift:
            I = np.fft.fftshift(I)
        plt.figure(2)
        plt.plot(T, I)
        plt.show()
        return T, I

    def plotspectrum(self, l_min, l_max, z=None):
        if z is None:
            z = self.Z[-1]
        self.Iw = 20 * np.log10(np.abs(self.AAw))
        L = self.c_const / self.F
        lidxrange = np.where((L > l_min) & (L < l_max))[0]
        L = L[lidxrange]
        Iw = self.Iw[np.argmin(np.abs(self.Z - z))]
        Iw = Iw[lidxrange]
        plt.figure(3)
        plt.plot(L, Iw)
        plt.show()
        return L, Iw

    def getpulsewidth(self, A):
        I = np.abs(A)**2
        I = I / np.max(I)
        N = len(np.where(I > 0.5)[0])
        return self.dT * N

    def plotpulsewidth(self,silent = False):
        out = []
        for ii in range(self.Nsteps):
            out.append(self.getpulsewidth(self.AA[ii]))
        if not silent:
            plt.figure(4)
            plt.plot(self.Z, out)
            plt.show()
        return out

    def plotpulseenergy(self):
        out = []
        for ii in range(self.Nsteps):
            t = self.getpulsewidth(self.AA[ii])
            P_peak = np.max(np.abs(self.AA[ii])**2)
            out.append(P_peak * t)
        plt.figure(5)
        plt.plot(self.Z, out)
        plt.show()
        return out

class HNLFmodule:
    def  __init__(self, fiber_segments):
        self.fibers = fiber_segments

    def input(self, T, A0, f0):  # ps W THz
        self.T = T
        self.NT = T.shape[-1]
        self.dT = T[1] - T[0]
        self.A0 = A0
        self.f0 = f0

    def output(self):
        return self.fibers[-1].output()

    def calc(self, dz, method='RK4IP'):
        A = self.A0
        T = self.T
        for fiber in self.fibers:
            fiber.input(T,A,self.f0)
            fiber.calc(int(np.floor(fiber.length / dz)), method)
            T, A = fiber.output()

    def plotpulsewidth(self):
        pw = []
        L = [0]
        for fiber in self.fibers:
            L = np.append(L, fiber.Z + L[-1])
            pw = np.append(pw, fiber.plotpulsewidth(silent = True))
        L = L[1:]
        plt.figure(4)
        plt.plot(L, pw)
        plt.show()
        return L,pw
    
    def getA(self, z):
        for fiber in self.fibers:
            if z <= fiber.length:
                return fiber.getA(z)
            else:
                z -= fiber.length

    def plotpulse(self, z=None, shift=False):
        if z is None:
            return self.fibers[-1].plotpulse(shift = shift)
        for fiber in self.fibers:
            if z <= fiber.length:
                return fiber.plotpulse(z = z, shift = shift)
            else:
                z -= fiber.length
    
    def plotspectrum(self, l_min, l_max, z=None):
        if z is None:
            return self.fibers[-1].plotspectrum(l_min, l_max)
        for fiber in self.fibers:
            if z <= fiber.length:
                return fiber.plotspectrum(l_min,l_max,z)
            else:
                z -= fiber.length