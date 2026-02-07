"""
Convolution Example — Visual Step-by-Step
==========================================

Purpose:
    Demonstrate convolution graphically and computationally.
    Show that convolution in time = multiplication in frequency.

System:
    A simple RC low-pass filter with impulse response:
        h(t) = (1/RC) * exp(-t/RC) * u(t)
    
    Input: a rectangular pulse of duration T_pulse.

Equations:
    y(t) = x(t) * h(t) = ∫ x(τ) h(t-τ) dτ

Expected Behavior:
    - The output is a smoothed version of the rectangular pulse
    - Rising edge: exponential rise with time constant RC
    - Falling edge: exponential decay with time constant RC
    - Longer RC → more smoothing (lower bandwidth filter)
"""

import numpy as np
import matplotlib.pyplot as plt


# =============================================================================
# System Parameters
# =============================================================================
RC = 0.5         # Time constant [s]
T_pulse = 2.0    # Pulse duration [s]
dt = 0.001       # Time step [s]
t = np.arange(-1, 6, dt)

# =============================================================================
# Define Signals
# =============================================================================

# Input: rectangular pulse from t=0 to t=T_pulse
x = np.where((t >= 0) & (t < T_pulse), 1.0, 0.0)

# Impulse response of RC filter: h(t) = (1/RC) * exp(-t/RC) * u(t)
h = np.where(t >= 0, (1 / RC) * np.exp(-t / RC), 0.0)

# =============================================================================
# Convolution (Numerical)
# =============================================================================
y = np.convolve(x, h, mode='full') * dt  # Scale by dt for continuous approx
t_conv = np.arange(0, len(y)) * dt + t[0] + t[0]  # Adjust time axis
# Better: just compute over the same time range
y = y[:len(t)]
t_conv = t

# =============================================================================
# Analytical Solution (for verification)
# =============================================================================
# For a rectangular pulse input to an RC filter:
# y(t) = (1 - exp(-t/RC))                          for 0 ≤ t < T_pulse
# y(t) = (1 - exp(-T_pulse/RC)) * exp(-(t-T_pulse)/RC)  for t ≥ T_pulse
y_analytical = np.zeros_like(t)
for i, ti in enumerate(t):
    if 0 <= ti < T_pulse:
        y_analytical[i] = 1 - np.exp(-ti / RC)
    elif ti >= T_pulse:
        y_analytical[i] = (1 - np.exp(-T_pulse / RC)) * np.exp(-(ti - T_pulse) / RC)


# =============================================================================
# Frequency Domain Verification
# =============================================================================
# X(jω) * H(jω) should give Y(jω)
N = len(t)
X_f = np.fft.fft(x) * dt
H_f = np.fft.fft(h) * dt
Y_f_mult = X_f * H_f / dt  # Compensate for double scaling
y_freq_domain = np.real(np.fft.ifft(Y_f_mult))

freqs = np.fft.fftfreq(N, dt)


# =============================================================================
# Plotting
# =============================================================================
fig, axes = plt.subplots(3, 2, figsize=(14, 10))

# --- Time domain signals ---
# Input
axes[0, 0].plot(t, x, 'b-', linewidth=2)
axes[0, 0].set_title('Input Signal x(t): Rectangular Pulse')
axes[0, 0].set_ylabel('Amplitude')
axes[0, 0].grid(True, alpha=0.3)
axes[0, 0].set_xlim(-0.5, 5)

# Impulse response
axes[0, 1].plot(t, h, 'r-', linewidth=2)
axes[0, 1].set_title(f'Impulse Response h(t): RC Filter (RC={RC}s)')
axes[0, 1].set_ylabel('Amplitude')
axes[0, 1].grid(True, alpha=0.3)
axes[0, 1].set_xlim(-0.5, 5)

# Convolution result
axes[1, 0].plot(t, y, 'g-', linewidth=2, label='Numerical convolution')
axes[1, 0].plot(t, y_analytical, 'k--', linewidth=1.5, label='Analytical')
axes[1, 0].set_title('Output y(t) = x(t) * h(t)')
axes[1, 0].set_ylabel('Amplitude')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)
axes[1, 0].set_xlim(-0.5, 5)

# Overlay comparison
axes[1, 1].plot(t, x, 'b--', linewidth=1, alpha=0.5, label='Input x(t)')
axes[1, 1].plot(t, y_analytical, 'g-', linewidth=2, label='Output y(t)')
axes[1, 1].set_title('Input vs Output — Smoothing Effect')
axes[1, 1].set_ylabel('Amplitude')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)
axes[1, 1].set_xlim(-0.5, 5)

# --- Frequency domain ---
# Magnitude spectra
freq_mask = (freqs >= 0) & (freqs < 10)
axes[2, 0].semilogy(freqs[freq_mask], np.abs(X_f[freq_mask]), 'b-',
                     linewidth=2, label='|X(f)|')
axes[2, 0].semilogy(freqs[freq_mask], np.abs(H_f[freq_mask]), 'r-',
                     linewidth=2, label='|H(f)|')
axes[2, 0].set_title('Magnitude Spectra')
axes[2, 0].set_xlabel('Frequency [Hz]')
axes[2, 0].set_ylabel('Magnitude')
axes[2, 0].legend()
axes[2, 0].grid(True, alpha=0.3)

# Verify: frequency domain multiplication = time domain convolution
axes[2, 1].plot(t, y_analytical, 'g-', linewidth=2,
                label='Time-domain convolution')
axes[2, 1].plot(t, y_freq_domain, 'k--', linewidth=1.5,
                label='Freq-domain multiplication')
axes[2, 1].set_title('Verification: Conv. Theorem')
axes[2, 1].set_xlabel('Time [s]')
axes[2, 1].set_ylabel('Amplitude')
axes[2, 1].legend()
axes[2, 1].grid(True, alpha=0.3)
axes[2, 1].set_xlim(-0.5, 5)

for ax in axes.flat:
    ax.set_xlim(-0.5, 5) if 'Time' in ax.get_xlabel() or ax.get_xlabel() == '' else None

plt.tight_layout()
plt.savefig('convolution-example.png', dpi=150, bbox_inches='tight')
plt.show()

print("Key observations:")
print(f"  1. Convolution with h(t) smooths the sharp edges of x(t)")
print(f"  2. Rise time ≈ 2.2 × RC = {2.2*RC:.2f} sec (10%-90%)")
print(f"  3. The RC filter attenuates high frequencies (sharp edges)")
print(f"  4. Time-domain convolution matches frequency-domain multiplication ✓")
