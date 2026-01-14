import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# --- Physical Parameters ---
fs = 16e9                   # Comb spacing (16 GHz)
delta_phi_pm = 35           # PM drive (Controls bandwidth, ~100 teeth)
delta_phi_im = 0.25 * np.pi  # IM drive (Under-driven to flatten)
phi_bias = 0.25 * np.pi     # IM Bias (Quadrature bias)
theta = 0.5 * np.pi         # Phase sync (Critical for symmetry)

# --- Simulation Settings ---
N_points = 2**18            # High resolution for FFT
N_periods = 200             # Capture many cycles for sharp teeth
T_s = 1/fs
t = np.linspace(0, N_periods * T_s, N_points, endpoint=False)
dt = t[1] - t[0]

# --- Math Model ---
# 1. Phase Modulated Field (The "Carrier" for the comb)
E_pm = np.exp(1j * delta_phi_pm * np.sin(2 * np.pi * fs * t))

# 2. Intensity Modulator (Acting as the spectral equalizer)
# We use the field transmission function for an MZM
T_im = np.cos(delta_phi_im * np.cos(2 * np.pi * fs * t + theta) + phi_bias)

# 3. Combined Output
E_total = T_im * E_pm

# --- Spectral Analysis ---
spec = np.fft.fftshift(np.fft.fft(E_total))
freqs = np.fft.fftshift(np.fft.fftfreq(N_points, d=dt))
# Power in dB, normalized to the highest peak
power_db = 10 * np.log10(np.abs(spec)**2 / np.max(np.abs(spec)**2) + 1e-10)

# --- Plotting ---
plt.figure(figsize=(12, 6))

# Define the viewing window (±900 GHz)
mask = (freqs > -900e9) & (freqs < 900e9)

# Plotting the continuous spectrum (simulating an OSA trace)
plt.plot(freqs[mask] / 1e9, power_db[mask], color='darkcyan', lw=0.8)

plt.title(f'EO Comb Spectrum: {fs/1e9:.0f} GHz Spacing (~100 Teeth)', fontsize=14)
plt.xlabel('Frequency Offset from Carrier (GHz)', fontsize=12)
plt.ylabel('Relative Power (dB)', fontsize=12)
plt.xlim([-950, 950])
plt.ylim([-30, 5])
plt.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()

plt.show()

# --- Quantitative Check ---
# Identifying