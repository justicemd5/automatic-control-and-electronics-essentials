"""
RLC Circuit Model — Transfer Function and Step Response
========================================================

Purpose:
    Model a series RLC circuit, derive its transfer function,
    and simulate the step response showing underdamped, critically
    damped, and overdamped cases.

Circuit:
    
    V_in ──── L ──── R ──── C ──── GND
                            │
                          V_out (voltage across C)

Governing Equation (KVL):
    L * di/dt + R*i + (1/C) * ∫i dt = V_in
    
    Or in terms of V_out = (1/C) * ∫i dt:
    LC * d²V_out/dt² + RC * dV_out/dt + V_out = V_in

Transfer Function:
    G(s) = V_out(s) / V_in(s) = 1 / (LCs² + RCs + 1)
    
    In standard form:
    G(s) = ωn² / (s² + 2ζωn·s + ωn²)
    
    where:
        ωn = 1/√(LC)           — natural frequency
        ζ  = (R/2) * √(C/L)   — damping ratio

Expected Behavior:
    - ζ < 1: Underdamped — oscillatory step response
    - ζ = 1: Critically damped — fastest non-oscillatory response
    - ζ > 1: Overdamped — sluggish, no oscillation
"""

import numpy as np
from scipy import signal
import matplotlib.pyplot as plt


# =============================================================================
# Circuit Parameters
# =============================================================================
L = 1e-3     # Inductance [H] = 1 mH
C = 1e-6     # Capacitance [F] = 1 μF

# Natural frequency (same for all cases)
omega_n = 1 / np.sqrt(L * C)
f_n = omega_n / (2 * np.pi)

print("=" * 60)
print("Series RLC Circuit Analysis")
print("=" * 60)
print(f"L = {L*1e3:.1f} mH, C = {C*1e6:.1f} μF")
print(f"Natural frequency: ωn = {omega_n:.1f} rad/s = {f_n:.1f} Hz")
print(f"Period: T = {1/f_n*1e3:.3f} ms")


# =============================================================================
# Three Damping Cases
# =============================================================================
# R for critical damping: R_crit = 2 * sqrt(L/C)
R_crit = 2 * np.sqrt(L / C)
print(f"\nCritical resistance: R_crit = {R_crit:.2f} Ω")

cases = {
    'Underdamped (ζ=0.2)': R_crit * 0.2,
    'Critically Damped (ζ=1.0)': R_crit * 1.0,
    'Overdamped (ζ=2.0)': R_crit * 2.0,
}

print(f"\n{'Case':<30} {'R [Ω]':>10} {'ζ':>8} {'Poles':>30}")
print("-" * 80)


# =============================================================================
# Simulation and Plotting
# =============================================================================
fig, axes = plt.subplots(2, 1, figsize=(10, 8))
colors = ['#2196F3', '#4CAF50', '#FF5722']

for idx, (name, R) in enumerate(cases.items()):
    # Damping ratio
    zeta = (R / 2) * np.sqrt(C / L)
    
    # Transfer function: 1 / (LC*s² + RC*s + 1)
    # Or equivalently: ωn² / (s² + 2ζωn*s + ωn²)
    num = [omega_n**2]
    den = [1, 2 * zeta * omega_n, omega_n**2]
    
    sys = signal.TransferFunction(num, den)
    poles = np.roots(den)
    
    # Print info
    pole_str = ', '.join([f'{p:.0f}' for p in poles])
    print(f"{name:<30} {R:>10.2f} {zeta:>8.2f} {pole_str:>30}")
    
    # Step response
    t = np.linspace(0, 0.01, 2000)  # 10 ms window
    t_out, y_out = signal.step(sys, T=t)
    
    # Plot step response
    axes[0].plot(t_out * 1e3, y_out, color=colors[idx], linewidth=2,
                 label=f'{name}, R={R:.1f}Ω')
    
    # Bode magnitude plot
    w = np.logspace(2, 6, 1000)
    w_out, mag, phase = signal.bode(sys, w)
    axes[1].semilogx(w_out / (2 * np.pi), mag, color=colors[idx],
                     linewidth=2, label=name)

# Step response formatting
axes[0].axhline(y=1, color='gray', linestyle='--', alpha=0.5, label='Setpoint')
axes[0].set_xlabel('Time [ms]')
axes[0].set_ylabel('V_out / V_in')
axes[0].set_title('RLC Circuit Step Response — Effect of Damping')
axes[0].legend(loc='lower right')
axes[0].grid(True, alpha=0.3)
axes[0].set_ylim(-0.1, 1.8)

# Bode plot formatting
axes[1].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
axes[1].axvline(x=f_n, color='gray', linestyle=':', alpha=0.5,
                label=f'fn = {f_n:.0f} Hz')
axes[1].set_xlabel('Frequency [Hz]')
axes[1].set_ylabel('Magnitude [dB]')
axes[1].set_title('RLC Circuit Frequency Response — Bode Magnitude')
axes[1].legend()
axes[1].grid(True, alpha=0.3, which='both')

plt.tight_layout()
plt.savefig('rlc-circuit-response.png', dpi=150, bbox_inches='tight')
plt.show()


# =============================================================================
# Energy Analysis
# =============================================================================
print("\n" + "=" * 60)
print("Energy Analysis at Resonance")
print("=" * 60)

R_under = cases['Underdamped (ζ=0.2)']
Q_factor = 1 / (2 * 0.2)  # Q = 1/(2ζ)
bandwidth = omega_n / Q_factor

print(f"\nFor the underdamped case (ζ = 0.2):")
print(f"  Quality factor Q = {Q_factor:.1f}")
print(f"  Resonant peak = {20*np.log10(Q_factor):.1f} dB")
print(f"  Bandwidth = {bandwidth/(2*np.pi):.1f} Hz")
print(f"  Energy stored / Energy dissipated per cycle = Q/(2π) = {Q_factor/(2*np.pi):.2f}")
print(f"\nPhysical interpretation:")
print(f"  At resonance, energy sloshes between L (magnetic) and C (electric)")
print(f"  The Q factor tells you how many oscillations before energy decays to 1/e")
print(f"  Higher R → lower Q → faster energy dissipation → more damping")
