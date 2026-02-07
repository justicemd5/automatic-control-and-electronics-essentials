"""
RC Filter Analysis — Frequency Response of Low-Pass and High-Pass Filters
==========================================================================

Purpose:
    Analyze first-order RC filters (low-pass and high-pass), compute and
    plot their Bode diagrams, and demonstrate the effect of component
    values on cutoff frequency and roll-off.

Circuits:
    Low-Pass:  V_in ──R──┬── V_out     High-Pass: V_in ──C──┬── V_out
                         │                                    │
                         C                                    R
                         │                                    │
                        GND                                  GND

Transfer Functions:
    Low-Pass:  H_LP(s) = 1 / (RCs + 1)
    High-Pass: H_HP(s) = RCs / (RCs + 1)

    Note: H_LP(s) + H_HP(s) = 1 (complementary pair)

Expected Behavior:
    - LP: passes low frequencies, attenuates high frequencies
    - HP: passes high frequencies, attenuates low frequencies
    - Both: -3 dB at cutoff frequency fc = 1/(2πRC)
    - Roll-off: 20 dB/decade (first-order)
"""

import numpy as np
from scipy import signal
import matplotlib.pyplot as plt


# =============================================================================
# Component Values
# =============================================================================
# Three different RC combinations to show the effect of cutoff frequency
designs = [
    {'R': 10e3, 'C': 100e-9, 'label': 'R=10kΩ, C=100nF'},    # fc = 159 Hz
    {'R': 10e3, 'C': 10e-9,  'label': 'R=10kΩ, C=10nF'},     # fc = 1.59 kHz
    {'R': 1e3,  'C': 10e-9,  'label': 'R=1kΩ, C=10nF'},      # fc = 15.9 kHz
]

print("=" * 60)
print("RC Filter Analysis")
print("=" * 60)


# =============================================================================
# Bode Plot: Low-Pass Filters
# =============================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
colors = ['#2196F3', '#4CAF50', '#FF5722']
freq_range = np.logspace(0, 6, 1000)  # 1 Hz to 1 MHz

for i, d in enumerate(designs):
    R, C = d['R'], d['C']
    fc = 1 / (2 * np.pi * R * C)
    tau = R * C
    
    print(f"\n{d['label']}:")
    print(f"  Cutoff frequency: fc = {fc:.1f} Hz")
    print(f"  Time constant: τ = {tau*1e6:.1f} μs")
    
    # Low-pass: H(s) = 1 / (τs + 1) = ωc / (s + ωc)
    wc = 2 * np.pi * fc
    lp_sys = signal.TransferFunction([wc], [1, wc])
    w_lp, mag_lp, phase_lp = signal.bode(lp_sys, freq_range * 2 * np.pi)
    
    # High-pass: H(s) = τs / (τs + 1) = s / (s + ωc)
    hp_sys = signal.TransferFunction([1, 0], [1, wc])
    w_hp, mag_hp, phase_hp = signal.bode(hp_sys, freq_range * 2 * np.pi)
    
    # Plot low-pass magnitude
    axes[0, 0].semilogx(w_lp / (2*np.pi), mag_lp, color=colors[i],
                         linewidth=2, label=f'{d["label"]} (fc={fc:.0f}Hz)')
    
    # Plot low-pass phase
    axes[1, 0].semilogx(w_lp / (2*np.pi), phase_lp, color=colors[i],
                         linewidth=2, label=f'fc={fc:.0f}Hz')
    
    # Plot high-pass magnitude
    axes[0, 1].semilogx(w_hp / (2*np.pi), mag_hp, color=colors[i],
                         linewidth=2, label=f'{d["label"]} (fc={fc:.0f}Hz)')
    
    # Plot high-pass phase
    axes[1, 1].semilogx(w_hp / (2*np.pi), phase_hp, color=colors[i],
                         linewidth=2, label=f'fc={fc:.0f}Hz')

# Formatting
axes[0, 0].set_title('Low-Pass Filter — Magnitude')
axes[0, 0].set_ylabel('Magnitude [dB]')
axes[0, 0].axhline(y=-3, color='gray', linestyle='--', alpha=0.5, label='-3 dB')
axes[0, 0].legend(fontsize=8)
axes[0, 0].grid(True, alpha=0.3, which='both')
axes[0, 0].set_ylim(-60, 5)

axes[1, 0].set_title('Low-Pass Filter — Phase')
axes[1, 0].set_xlabel('Frequency [Hz]')
axes[1, 0].set_ylabel('Phase [degrees]')
axes[1, 0].axhline(y=-45, color='gray', linestyle='--', alpha=0.5, label='-45°')
axes[1, 0].legend(fontsize=8)
axes[1, 0].grid(True, alpha=0.3, which='both')

axes[0, 1].set_title('High-Pass Filter — Magnitude')
axes[0, 1].set_ylabel('Magnitude [dB]')
axes[0, 1].axhline(y=-3, color='gray', linestyle='--', alpha=0.5, label='-3 dB')
axes[0, 1].legend(fontsize=8)
axes[0, 1].grid(True, alpha=0.3, which='both')
axes[0, 1].set_ylim(-60, 5)

axes[1, 1].set_title('High-Pass Filter — Phase')
axes[1, 1].set_xlabel('Frequency [Hz]')
axes[1, 1].set_ylabel('Phase [degrees]')
axes[1, 1].axhline(y=45, color='gray', linestyle='--', alpha=0.5, label='+45°')
axes[1, 1].legend(fontsize=8)
axes[1, 1].grid(True, alpha=0.3, which='both')

plt.tight_layout()
plt.savefig('rc-filter-bode.png', dpi=150, bbox_inches='tight')
plt.show()


# =============================================================================
# Step Response Comparison
# =============================================================================
fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))

for i, d in enumerate(designs):
    R, C = d['R'], d['C']
    fc = 1 / (2 * np.pi * R * C)
    wc = 2 * np.pi * fc
    tau = R * C
    
    # Time vector: 5 time constants
    t = np.linspace(0, 5 * tau, 1000)
    
    # Low-pass step response: y(t) = 1 - exp(-t/τ)
    lp_sys = signal.TransferFunction([wc], [1, wc])
    t_out, y_lp = signal.step(lp_sys, T=t)
    
    # High-pass step response: y(t) = exp(-t/τ)
    hp_sys = signal.TransferFunction([1, 0], [1, wc])
    _, y_hp = signal.step(hp_sys, T=t)
    
    axes2[0].plot(t_out * 1e6, y_lp, color=colors[i], linewidth=2,
                  label=f'τ={tau*1e6:.0f}μs')
    axes2[1].plot(t_out * 1e6, y_hp, color=colors[i], linewidth=2,
                  label=f'τ={tau*1e6:.0f}μs')

axes2[0].set_title('Low-Pass Step Response')
axes2[0].set_xlabel('Time [μs]')
axes2[0].set_ylabel('Output / Input')
axes2[0].legend()
axes2[0].grid(True, alpha=0.3)
axes2[0].axhline(y=0.632, color='gray', linestyle='--', alpha=0.5)

axes2[1].set_title('High-Pass Step Response')
axes2[1].set_xlabel('Time [μs]')
axes2[1].set_ylabel('Output / Input')
axes2[1].legend()
axes2[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('rc-filter-step-response.png', dpi=150, bbox_inches='tight')
plt.show()


# =============================================================================
# Summary
# =============================================================================
print("\n" + "=" * 60)
print("Key Design Insights")
print("=" * 60)
print("1. Cutoff frequency fc = 1/(2πRC) — inversely proportional to RC product")
print("2. First-order filters roll off at 20 dB/decade (6 dB/octave)")
print("3. At the cutoff frequency: magnitude = -3 dB, phase = -45° (LP)")
print("4. LP and HP are complementary: H_LP + H_HP = 1")
print("5. Step response time constant τ = RC determines settling speed")
print("6. For steeper roll-off, cascade stages or use active filters (Butterworth, etc.)")
