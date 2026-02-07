"""
Discretization Method Comparison
==================================

Purpose:
    Compare different discretization methods (ZOH, Tustin, Forward/Backward Euler)
    applied to the same continuous-time transfer function.
    Show step responses and Bode plots of each discrete approximation.

Continuous System:
    G(s) = 10 / (s + 10)   (first-order LPF, τ = 0.1s, f_c = 1.59 Hz)

Sample Period:
    T_s = 0.02 s  (f_s = 50 Hz, ratio = f_s/f_c ≈ 31)
"""

import numpy as np
from scipy import signal
import matplotlib.pyplot as plt


# =============================================================================
# Continuous System
# =============================================================================
num_c = [10]
den_c = [1, 10]
G_c = signal.TransferFunction(num_c, den_c)

Ts = 0.02  # Sample period [s]
fs = 1 / Ts
print(f"Continuous system: G(s) = 10/(s+10)")
print(f"  Time constant τ = 0.1 s")
print(f"  Bandwidth f_c = {10/(2*np.pi):.2f} Hz")
print(f"  Sample rate f_s = {fs:.0f} Hz")
print(f"  Oversampling ratio = {fs / (10/(2*np.pi)):.1f}×")


# =============================================================================
# Discretization Methods
# =============================================================================

# 1. ZOH (exact discretization for DAC + plant)
G_zoh = signal.cont2discrete((num_c, den_c), Ts, method='zoh')

# 2. Tustin (bilinear transformation)
G_tustin = signal.cont2discrete((num_c, den_c), Ts, method='bilinear')

# 3. Forward Euler: s ≈ (z-1)/Ts
# G(z) = 10 / ((z-1)/Ts + 10) = 10*Ts / (z - 1 + 10*Ts)
a_fe = 10 * Ts
num_fe = [a_fe]
den_fe = [1, -(1 - a_fe)]
G_fe = signal.dlti(num_fe, den_fe, dt=Ts)

# 4. Backward Euler: s ≈ (z-1)/(z*Ts)
# G(z) = 10 / ((z-1)/(z*Ts) + 10) = 10*Ts*z / (z - 1 + 10*Ts*z) = 10*Ts*z / ((1+10*Ts)*z - 1)
a_be = 10 * Ts
num_be = [a_be / (1 + a_be), 0]  # Include z factor
den_be = [1, -1 / (1 + a_be)]
G_be = signal.dlti(num_be, den_be, dt=Ts)

methods = {
    'ZOH (exact)': G_zoh,
    'Tustin (bilinear)': G_tustin,
    'Forward Euler': G_fe,
    'Backward Euler': G_be,
}

# Print discrete transfer functions
for name, G_d in methods.items():
    if hasattr(G_d, '__len__') and len(G_d) > 2:
        num, den = G_d[0].flatten(), G_d[1].flatten()
    else:
        num, den = G_d.num, G_d.den
        if hasattr(num, 'flatten'):
            num = num.flatten()
        if hasattr(den, 'flatten'):
            den = den.flatten()
    print(f"\n{name}:")
    print(f"  Numerator:   {np.round(num, 6)}")
    print(f"  Denominator: {np.round(den, 6)}")


# =============================================================================
# Step Response Comparison
# =============================================================================
t_c = np.linspace(0, 0.5, 1000)
t_c_step, y_c_step = signal.step(G_c, T=t_c)

n_samples = int(0.5 / Ts) + 1
k = np.arange(n_samples)
t_d = k * Ts

fig1, ax1 = plt.subplots(figsize=(10, 6))

# Continuous reference
ax1.plot(t_c_step, y_c_step, 'k-', linewidth=2, label='Continuous (exact)')

colors = ['blue', 'red', 'green', 'orange']
markers = ['o', 's', '^', 'D']

for (name, G_d), color, marker in zip(methods.items(), colors, markers):
    if hasattr(G_d, '__len__') and len(G_d) > 2:
        sys_d = signal.dlti(G_d[0].flatten(), G_d[1].flatten(), dt=Ts)
    else:
        sys_d = G_d
    
    t_out, y_out = signal.dstep(sys_d, n=n_samples)
    y_out = np.array(y_out[0]).flatten()
    t_out = np.arange(len(y_out)) * Ts
    
    ax1.step(t_out, y_out, where='post', color=color, linewidth=1.5,
             label=name, alpha=0.8)
    ax1.plot(t_out[::2], y_out[::2], marker, color=color, markersize=5, alpha=0.6)

ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Output')
ax1.set_title(f'Step Response Comparison (Ts = {Ts*1000:.0f} ms)')
ax1.legend(loc='lower right')
ax1.grid(True, alpha=0.3)
ax1.set_xlim(-0.01, 0.5)
plt.tight_layout()
plt.savefig('discretization-step.png', dpi=150, bbox_inches='tight')
plt.show()


# =============================================================================
# Bode Plot Comparison
# =============================================================================
w_c = np.logspace(-1, 3, 500)
w_c_bode, mag_c, phase_c = signal.bode(G_c, w_c)

fig2, (ax_mag, ax_phase) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
fig2.suptitle(f'Bode Plot Comparison (fs = {fs:.0f} Hz)', fontsize=14)

ax_mag.semilogx(w_c_bode, mag_c, 'k-', linewidth=2, label='Continuous')
ax_phase.semilogx(w_c_bode, phase_c, 'k-', linewidth=2, label='Continuous')

for (name, G_d), color in zip(methods.items(), colors):
    if hasattr(G_d, '__len__') and len(G_d) > 2:
        sys_d = signal.dlti(G_d[0].flatten(), G_d[1].flatten(), dt=Ts)
    else:
        sys_d = G_d
    
    # Frequency response of discrete system
    w_d = np.logspace(-1, np.log10(np.pi / Ts), 300)
    w_d, H_d = signal.dfreqresp(sys_d, w=w_d * Ts)
    
    mag_d = 20 * np.log10(np.abs(H_d))
    phase_d = np.degrees(np.angle(H_d))
    
    ax_mag.semilogx(w_d / Ts, mag_d, color=color, linewidth=1.5, label=name)
    ax_phase.semilogx(w_d / Ts, phase_d, color=color, linewidth=1.5, label=name)

# Nyquist frequency line
ax_mag.axvline(x=np.pi / Ts, color='gray', linestyle=':', alpha=0.5, label='Nyquist freq')
ax_phase.axvline(x=np.pi / Ts, color='gray', linestyle=':', alpha=0.5)

ax_mag.set_ylabel('Magnitude [dB]')
ax_mag.legend(fontsize=8, loc='lower left')
ax_mag.grid(True, which='both', alpha=0.3)

ax_phase.set_ylabel('Phase [°]')
ax_phase.set_xlabel('Frequency [rad/s]')
ax_phase.legend(fontsize=8, loc='lower left')
ax_phase.grid(True, which='both', alpha=0.3)

plt.tight_layout()
plt.savefig('discretization-bode.png', dpi=150, bbox_inches='tight')
plt.show()


# =============================================================================
# Summary
# =============================================================================
print(f"\n{'='*60}")
print("DISCRETIZATION SUMMARY")
print(f"{'='*60}")
print(f"""
  Method          | Preserves | Best For
  ────────────────┼───────────┼──────────────────────
  ZOH             | Step resp | DAC+plant (standard)
  Tustin          | Frequency | Filters, compensators
  Forward Euler   | Simplicity| Very fast sampling only
  Backward Euler  | Stability | Stiff systems

  General advice:
  - Use ZOH when modeling a sampled-data system (plant + DAC)
  - Use Tustin when discretizing a controller designed in s-domain
  - Avoid Forward Euler unless Ts << smallest time constant
  - Backward Euler is unconditionally stable but less accurate
""")
