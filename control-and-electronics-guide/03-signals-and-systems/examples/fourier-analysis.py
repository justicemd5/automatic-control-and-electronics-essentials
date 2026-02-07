"""
Fourier Analysis — FFT of Real-World-Like Signals
==================================================

Purpose:
    Demonstrate the use of the Fast Fourier Transform (FFT) to analyze
    the frequency content of signals. Show practical aspects: windowing,
    spectral leakage, and resolution limits.

Signals analyzed:
    1. Clean sinusoid — sharp spectral line
    2. Sum of sinusoids — multiple frequency components
    3. Sinusoid + noise — extracting signal from noise
    4. Chirp signal — time-varying frequency (spectrogram)

Expected Behavior:
    - FFT reveals frequency components that are invisible in time domain
    - Windowing reduces spectral leakage
    - Noise floor limits detection of weak signals
    - Frequency resolution = fs / N
"""

import numpy as np
import matplotlib.pyplot as plt


# =============================================================================
# Parameters
# =============================================================================
fs = 1000       # Sampling frequency [Hz]
T = 1.0         # Signal duration [s]
N = int(fs * T) # Number of samples
t = np.arange(N) / fs
freqs = np.fft.rfftfreq(N, 1 / fs)  # Positive frequencies only


def compute_spectrum(signal, window=None):
    """Compute magnitude spectrum in dB with optional windowing."""
    if window is not None:
        signal = signal * window
    spectrum = np.fft.rfft(signal) / N
    magnitude_db = 20 * np.log10(np.abs(spectrum) + 1e-12)
    return magnitude_db


# =============================================================================
# Signal 1: Clean Sinusoid
# =============================================================================
f1 = 50  # Hz
x1 = np.sin(2 * np.pi * f1 * t)


# =============================================================================
# Signal 2: Sum of Sinusoids (simulating a vibrating structure)
# =============================================================================
# Fundamental + harmonics with decreasing amplitude
x2 = (1.0 * np.sin(2 * np.pi * 60 * t) +     # 60 Hz, amplitude 1.0
      0.5 * np.sin(2 * np.pi * 120 * t) +     # 120 Hz (2nd harmonic)
      0.3 * np.sin(2 * np.pi * 180 * t) +     # 180 Hz (3rd harmonic)
      0.1 * np.sin(2 * np.pi * 300 * t))      # 300 Hz (5th harmonic)


# =============================================================================
# Signal 3: Sinusoid Buried in Noise
# =============================================================================
np.random.seed(42)
noise = np.random.randn(N) * 2.0  # Strong noise
x3 = np.sin(2 * np.pi * 100 * t) + noise  # 100 Hz signal, SNR ≈ -6 dB


# =============================================================================
# Signal 4: Chirp (frequency sweep from 10 Hz to 400 Hz)
# =============================================================================
f_start, f_end = 10, 400
x4 = np.sin(2 * np.pi * (f_start * t + (f_end - f_start) / (2 * T) * t**2))


# =============================================================================
# Compute Spectra
# =============================================================================
# Hanning window for reduced spectral leakage
hann = np.hanning(N)

spec1_rect = compute_spectrum(x1)               # No window
spec1_hann = compute_spectrum(x1, hann)          # Hanning window
spec2 = compute_spectrum(x2, hann)
spec3 = compute_spectrum(x3, hann)
spec4 = compute_spectrum(x4, hann)


# =============================================================================
# Plotting
# =============================================================================
fig, axes = plt.subplots(4, 2, figsize=(14, 14))

# --- Signal 1: Clean sinusoid ---
axes[0, 0].plot(t[:200], x1[:200], 'b-', linewidth=1)
axes[0, 0].set_title(f'Signal 1: {f1} Hz Sinusoid (time domain)')
axes[0, 0].set_ylabel('Amplitude')
axes[0, 0].grid(True, alpha=0.3)

axes[0, 1].plot(freqs, spec1_rect, 'b-', alpha=0.5, label='Rectangular window')
axes[0, 1].plot(freqs, spec1_hann, 'r-', linewidth=2, label='Hanning window')
axes[0, 1].set_title('Spectrum: Effect of Windowing')
axes[0, 1].set_ylabel('Magnitude [dB]')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)
axes[0, 1].set_xlim(0, 200)
axes[0, 1].set_ylim(-80, 0)

# --- Signal 2: Multiple frequencies ---
axes[1, 0].plot(t[:200], x2[:200], 'g-', linewidth=1)
axes[1, 0].set_title('Signal 2: Sum of Harmonics (time domain)')
axes[1, 0].set_ylabel('Amplitude')
axes[1, 0].grid(True, alpha=0.3)

axes[1, 1].plot(freqs, spec2, 'g-', linewidth=2)
axes[1, 1].set_title('Spectrum: Harmonic Content Revealed')
axes[1, 1].set_ylabel('Magnitude [dB]')
axes[1, 1].grid(True, alpha=0.3)
axes[1, 1].set_xlim(0, 400)
axes[1, 1].set_ylim(-80, 0)
# Mark the harmonics
for f, a in [(60, 1.0), (120, 0.5), (180, 0.3), (300, 0.1)]:
    axes[1, 1].axvline(x=f, color='r', linestyle='--', alpha=0.3)
    axes[1, 1].annotate(f'{f}Hz', (f, -5), fontsize=8, ha='center')

# --- Signal 3: Signal + noise ---
axes[2, 0].plot(t[:200], x3[:200], 'orange', linewidth=1)
axes[2, 0].set_title('Signal 3: 100 Hz Sinusoid + Strong Noise')
axes[2, 0].set_ylabel('Amplitude')
axes[2, 0].grid(True, alpha=0.3)

axes[2, 1].plot(freqs, spec3, 'orange', linewidth=1, alpha=0.7)
axes[2, 1].axvline(x=100, color='r', linewidth=2, linestyle='--',
                   label='True signal at 100 Hz')
axes[2, 1].set_title('Spectrum: Signal Visible Above Noise Floor')
axes[2, 1].set_ylabel('Magnitude [dB]')
axes[2, 1].legend()
axes[2, 1].grid(True, alpha=0.3)
axes[2, 1].set_xlim(0, 500)
axes[2, 1].set_ylim(-50, 0)

# --- Signal 4: Chirp ---
axes[3, 0].plot(t, x4, 'm-', linewidth=0.5)
axes[3, 0].set_title('Signal 4: Chirp 10→400 Hz')
axes[3, 0].set_xlabel('Time [s]')
axes[3, 0].set_ylabel('Amplitude')
axes[3, 0].grid(True, alpha=0.3)

# Spectrogram for the chirp (time-frequency analysis)
axes[3, 1].specgram(x4, NFFT=128, Fs=fs, noverlap=64, cmap='inferno')
axes[3, 1].set_title('Spectrogram: Time-Frequency View of Chirp')
axes[3, 1].set_xlabel('Time [s]')
axes[3, 1].set_ylabel('Frequency [Hz]')

plt.tight_layout()
plt.savefig('fourier-analysis.png', dpi=150, bbox_inches='tight')
plt.show()


# =============================================================================
# Summary
# =============================================================================
print("=" * 60)
print("Fourier Analysis Summary")
print("=" * 60)
print(f"Sampling rate: {fs} Hz")
print(f"Signal duration: {T} s")
print(f"Number of samples: {N}")
print(f"Frequency resolution: Δf = fs/N = {fs/N} Hz")
print(f"Maximum frequency: fs/2 = {fs/2} Hz")
print(f"\nKey observations:")
print(f"  1. FFT clearly identifies frequency components")
print(f"  2. Hanning window reduces spectral leakage (sidelobes)")
print(f"  3. 100 Hz signal visible above noise floor despite low SNR")
print(f"  4. Spectrogram shows time-varying frequency of chirp")
print(f"  5. Frequency resolution limits ability to distinguish close frequencies")
