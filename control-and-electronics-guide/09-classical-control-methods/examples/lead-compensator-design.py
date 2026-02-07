"""
Lead Compensator Design — Bode Plot Method
=============================================

Purpose:
    Design a lead compensator for a given plant to achieve specified
    phase margin and crossover frequency targets. Visualize the
    uncompensated and compensated Bode plots side by side.

Plant:
    G(s) = 100 / [s(s + 10)]
    
Requirements:
    - Steady-state velocity error constant: Kv >= 100
    - Phase margin: PM >= 45°
    - Gain margin: GM >= 10 dB

Expected Behavior:
    - Uncompensated system has insufficient phase margin
    - Lead compensator adds phase near crossover frequency
    - Compensated system meets all specifications
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal


# =============================================================================
# Plant Definition
# =============================================================================
# G(s) = 100 / [s(s + 10)]
num_G = [100]
den_G = [1, 10, 0]   # s^2 + 10s (includes the s in denominator)
G = signal.TransferFunction(num_G, den_G)


# =============================================================================
# Step 1: Check Steady-State Requirements
# =============================================================================
# For Kv >= 100: Kv = lim(s->0) s*K*G(s) = K * 100/10 = 10K
# Need 10K >= 100 => K >= 10
K = 10  # Gain to meet Kv = 100

# Apply gain
num_KG = [K * 100]  # = 1000
den_KG = den_G
KG = signal.TransferFunction(num_KG, den_KG)


# =============================================================================
# Step 2: Analyze Uncompensated System
# =============================================================================
w = np.logspace(-1, 3, 1000)
w_KG, mag_KG, phase_KG = signal.bode(KG, w)

# Find gain crossover frequency (where |KG| = 0 dB)
mag_KG_linear = 10**(mag_KG / 20)
idx_gc = np.argmin(np.abs(mag_KG_linear - 1.0))
wc_uncomp = w_KG[idx_gc]
pm_uncomp = 180 + phase_KG[idx_gc]

print("=" * 60)
print("UNCOMPENSATED SYSTEM ANALYSIS")
print("=" * 60)
print(f"  Gain crossover frequency: ωc = {wc_uncomp:.1f} rad/s")
print(f"  Phase at ωc: {phase_KG[idx_gc]:.1f}°")
print(f"  Phase margin: PM = {pm_uncomp:.1f}°")
print(f"  Kv = {K * 100 / 10:.0f} (meets requirement: Kv >= 100)")

# Find phase crossover (where phase = -180°)
idx_pc = np.argmin(np.abs(phase_KG - (-180)))
gm_uncomp = -mag_KG[idx_pc]
print(f"  Gain margin: GM = {gm_uncomp:.1f} dB")
print(f"\n  PM = {pm_uncomp:.1f}° < 45° → Need lead compensation!")


# =============================================================================
# Step 3: Design Lead Compensator
# =============================================================================
# Target PM = 45° + 5° safety = 50°
# Phase boost needed: φ_max = 50° - PM_uncomp
phi_max_needed = 50 - pm_uncomp
# Add extra margin for gain increase effect
phi_max = phi_max_needed + 10  # degrees (extra safety)
phi_max_rad = np.radians(phi_max)

print(f"\n{'=' * 60}")
print("LEAD COMPENSATOR DESIGN")
print("=" * 60)
print(f"  Phase boost needed: {phi_max_needed:.1f}° + 10° safety = {phi_max:.1f}°")

# Calculate alpha
alpha = (1 - np.sin(phi_max_rad)) / (1 + np.sin(phi_max_rad))
print(f"  α = {alpha:.4f}")

# New crossover frequency: where |KG(jω)| = -10*log10(1/α) dB
# (compensator adds 10*log10(1/α)/2 dB at ω_max)
gain_at_wmax = -10 * np.log10(1 / alpha) / 2
idx_new_wc = np.argmin(np.abs(mag_KG - gain_at_wmax))
wc_new = w_KG[idx_new_wc]
print(f"  New ωc target: {wc_new:.1f} rad/s")

# Calculate tau
tau = 1 / (wc_new * np.sqrt(alpha))
print(f"  τ = {tau:.6f} s")

# Lead compensator: C_lead(s) = (τs + 1) / (ατs + 1)
zero = 1 / tau
pole = 1 / (alpha * tau)
print(f"  Zero: z = {zero:.1f} rad/s")
print(f"  Pole: p = {pole:.1f} rad/s")

# Compensator transfer function
num_C = [tau, 1]
den_C = [alpha * tau, 1]


# =============================================================================
# Step 4: Verify Compensated System
# =============================================================================
# L(s) = K * C_lead(s) * G(s)
num_L = np.polymul(num_KG, num_C)
den_L = np.polymul(den_KG, den_C)
L = signal.TransferFunction(num_L, den_L)

w_L, mag_L, phase_L = signal.bode(L, w)

# Find new gain crossover
mag_L_linear = 10**(mag_L / 20)
idx_gc_comp = np.argmin(np.abs(mag_L_linear - 1.0))
wc_comp = w_L[idx_gc_comp]
pm_comp = 180 + phase_L[idx_gc_comp]

# Find new phase crossover
idx_pc_comp = np.argmin(np.abs(phase_L - (-180)))
gm_comp = -mag_L[idx_pc_comp]

print(f"\n{'=' * 60}")
print("COMPENSATED SYSTEM RESULTS")
print("=" * 60)
print(f"  Gain crossover: ωc = {wc_comp:.1f} rad/s")
print(f"  Phase margin: PM = {pm_comp:.1f}° {'✓' if pm_comp >= 45 else '✗'} (target: ≥ 45°)")
print(f"  Gain margin: GM = {gm_comp:.1f} dB {'✓' if gm_comp >= 10 else '✗'} (target: ≥ 10 dB)")


# =============================================================================
# Step 5: Plot Bode Diagrams
# =============================================================================
fig, (ax_mag, ax_phase) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
fig.suptitle('Lead Compensator Design — Bode Plot Method', fontsize=14)

# Magnitude plot
ax_mag.semilogx(w_KG, mag_KG, 'b--', linewidth=1.5, label=f'Uncompensated (PM={pm_uncomp:.1f}°)')
ax_mag.semilogx(w_L, mag_L, 'r-', linewidth=2, label=f'Compensated (PM={pm_comp:.1f}°)')
ax_mag.axhline(y=0, color='k', linestyle=':', alpha=0.5)
ax_mag.axvline(x=wc_uncomp, color='b', linestyle=':', alpha=0.3, label=f'ωc_old={wc_uncomp:.1f}')
ax_mag.axvline(x=wc_comp, color='r', linestyle=':', alpha=0.3, label=f'ωc_new={wc_comp:.1f}')
ax_mag.set_ylabel('Magnitude [dB]')
ax_mag.legend(fontsize=9)
ax_mag.grid(True, which='both', alpha=0.3)
ax_mag.set_ylim(-60, 60)

# Phase plot
ax_phase.semilogx(w_KG, phase_KG, 'b--', linewidth=1.5, label='Uncompensated')
ax_phase.semilogx(w_L, phase_L, 'r-', linewidth=2, label='Compensated')
ax_phase.axhline(y=-180, color='k', linestyle=':', alpha=0.5, label='-180° line')
ax_phase.axhline(y=-180 + 45, color='g', linestyle='--', alpha=0.5, label='PM = 45° target')

# Mark phase margins
ax_phase.annotate(f'PM = {pm_uncomp:.1f}°',
                  xy=(wc_uncomp, phase_KG[idx_gc]), fontsize=10,
                  xytext=(wc_uncomp * 3, phase_KG[idx_gc] + 15),
                  arrowprops=dict(arrowstyle='->', color='blue'),
                  color='blue')
ax_phase.annotate(f'PM = {pm_comp:.1f}°',
                  xy=(wc_comp, phase_L[idx_gc_comp]), fontsize=10,
                  xytext=(wc_comp * 3, phase_L[idx_gc_comp] + 15),
                  arrowprops=dict(arrowstyle='->', color='red'),
                  color='red')

ax_phase.set_ylabel('Phase [°]')
ax_phase.set_xlabel('Frequency [rad/s]')
ax_phase.legend(fontsize=9)
ax_phase.grid(True, which='both', alpha=0.3)
ax_phase.set_ylim(-270, 0)

plt.tight_layout()
plt.savefig('lead-compensator-bode.png', dpi=150, bbox_inches='tight')
plt.show()


# =============================================================================
# Step 6: Closed-Loop Step Response
# =============================================================================
# Closed-loop: T(s) = L(s) / (1 + L(s))
num_T = num_L
den_T = np.polyadd(den_L, num_L)
T = signal.TransferFunction(num_T, den_T)

# Also compute uncompensated closed-loop
num_T_uncomp = num_KG
den_T_uncomp = np.polyadd(den_KG, num_KG)
T_uncomp = signal.TransferFunction(num_T_uncomp, den_T_uncomp)

t = np.linspace(0, 1.0, 1000)
t_uncomp, y_uncomp = signal.step(T_uncomp, T=t)
t_comp, y_comp = signal.step(T, T=t)

fig2, ax2 = plt.subplots(figsize=(10, 5))
ax2.plot(t_uncomp, y_uncomp, 'b--', linewidth=1.5, label='Uncompensated')
ax2.plot(t_comp, y_comp, 'r-', linewidth=2, label='Compensated')
ax2.axhline(y=1.0, color='k', linestyle=':', alpha=0.5)
ax2.set_xlabel('Time [s]')
ax2.set_ylabel('Output')
ax2.set_title('Closed-Loop Step Response')
ax2.legend()
ax2.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('lead-compensator-step.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"\nStep response metrics (compensated):")
print(f"  Overshoot: {(np.max(y_comp) - 1) * 100:.1f}%")
idx_settle = np.where(np.abs(y_comp - 1.0) > 0.02)[0]
if len(idx_settle) > 0:
    print(f"  2% settling time: ~{t_comp[idx_settle[-1]]:.3f} s")
