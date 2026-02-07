"""
PWM Control — Signal Generation and Motor Speed Simulation
===========================================================

Purpose:
    Demonstrate PWM signal generation at various duty cycles,
    show the relationship between duty cycle and average voltage,
    and illustrate the effect of PWM frequency on output ripple.

Equations:
    Average voltage: V_avg = D × V_supply
    Duty cycle: D = t_on / T_period
    
    For a motor with electrical time constant τ_e = L/R:
    Current ripple: ΔI ≈ V_supply × D × (1-D) / (f_PWM × L)

Expected Behavior:
    - Higher duty cycle → higher average voltage → faster motor
    - Higher PWM frequency → smoother current → less torque ripple
    - PWM frequency must be >> motor electrical time constant
"""

import numpy as np
import matplotlib.pyplot as plt


# =============================================================================
# Parameters
# =============================================================================
V_supply = 12.0    # Supply voltage [V]
f_pwm = 20000      # PWM frequency [Hz] = 20 kHz (above audible range)
T_pwm = 1 / f_pwm  # PWM period [s]


# =============================================================================
# Part 1: PWM Signals at Different Duty Cycles
# =============================================================================
duty_cycles = [0.0, 0.25, 0.50, 0.75, 1.0]
n_periods = 3       # Show 3 PWM periods
dt = T_pwm / 500    # Time resolution
t = np.arange(0, n_periods * T_pwm, dt)

fig1, axes = plt.subplots(len(duty_cycles), 1, figsize=(12, 10), sharex=True)
fig1.suptitle(f'PWM Signals at {f_pwm/1000:.0f} kHz', fontsize=14)

for i, D in enumerate(duty_cycles):
    # Generate PWM signal
    t_in_period = t % T_pwm
    pwm_signal = np.where(t_in_period < D * T_pwm, V_supply, 0)
    
    # Average voltage
    V_avg = D * V_supply
    
    axes[i].fill_between(t * 1e3, pwm_signal, alpha=0.3, color='blue')
    axes[i].plot(t * 1e3, pwm_signal, 'b-', linewidth=1)
    axes[i].axhline(y=V_avg, color='r', linestyle='--', linewidth=2,
                     label=f'V_avg = {V_avg:.1f}V')
    axes[i].set_ylabel(f'D={D:.0%}\n[V]')
    axes[i].set_ylim(-0.5, V_supply * 1.1)
    axes[i].legend(loc='upper right', fontsize=9)
    axes[i].grid(True, alpha=0.3)

axes[-1].set_xlabel('Time [ms]')
plt.tight_layout()
plt.savefig('pwm-signals.png', dpi=150, bbox_inches='tight')
plt.show()


# =============================================================================
# Part 2: Effect of PWM Frequency on Current Ripple
# =============================================================================
# Simulate motor current with different PWM frequencies
# Motor model: L * dI/dt + R*I = V_pwm(t) - Kb*ω
# Simplified: just R-L circuit with V_pwm input

R_motor = 2.0      # Motor resistance [Ω]
L_motor = 5e-3     # Motor inductance [H] = 5 mH
tau_e = L_motor / R_motor  # Electrical time constant = 2.5 ms

D_test = 0.5       # 50% duty cycle
V_avg = D_test * V_supply  # Average voltage = 6V
I_avg = V_avg / R_motor    # Average current = 3A (no back-EMF for simplicity)

frequencies = [1000, 5000, 20000, 100000]  # 1kHz to 100kHz
fig2, axes2 = plt.subplots(len(frequencies), 1, figsize=(12, 10), sharex=False)
fig2.suptitle(f'Motor Current vs PWM Frequency (D={D_test:.0%}, τ_e={tau_e*1e3:.1f}ms)',
              fontsize=14)

for idx, f in enumerate(frequencies):
    T = 1 / f
    # Simulate 10 periods
    t_sim = np.linspace(0, 10 * T, 10000)
    dt_sim = t_sim[1] - t_sim[0]
    
    # PWM voltage signal
    t_in_period = t_sim % T
    V_pwm = np.where(t_in_period < D_test * T, V_supply, 0)
    
    # Simulate R-L circuit: L*dI/dt = V - R*I
    I = np.zeros_like(t_sim)
    I[0] = I_avg  # Start near steady state
    
    for k in range(len(t_sim) - 1):
        dIdt = (V_pwm[k] - R_motor * I[k]) / L_motor
        I[k+1] = I[k] + dIdt * dt_sim
    
    # Current ripple (peak-to-peak in steady state, last 3 periods)
    I_ss = I[len(I)//2:]
    ripple = np.max(I_ss) - np.min(I_ss)
    
    # Theoretical ripple: ΔI = V_supply * D * (1-D) / (f * L)
    ripple_theory = V_supply * D_test * (1 - D_test) / (f * L_motor)
    
    axes2[idx].plot(t_sim * 1e3, I, 'b-', linewidth=1)
    axes2[idx].axhline(y=I_avg, color='r', linestyle='--',
                        label=f'I_avg = {I_avg:.1f}A')
    axes2[idx].set_ylabel(f'f={f/1000:.0f}kHz\nI [A]')
    axes2[idx].legend(loc='upper right', fontsize=9)
    axes2[idx].grid(True, alpha=0.3)
    axes2[idx].set_title(
        f'Ripple: {ripple:.3f}A (theoretical: {ripple_theory:.3f}A)',
        fontsize=10, loc='left')

axes2[-1].set_xlabel('Time [ms]')
plt.tight_layout()
plt.savefig('pwm-frequency-effect.png', dpi=150, bbox_inches='tight')
plt.show()


# =============================================================================
# Part 3: Duty Cycle vs Average Voltage / Speed
# =============================================================================
D_range = np.linspace(0, 1, 100)
V_avg_range = D_range * V_supply

fig3, ax3 = plt.subplots(figsize=(8, 5))
ax3.plot(D_range * 100, V_avg_range, 'b-', linewidth=2)
ax3.set_xlabel('Duty Cycle [%]')
ax3.set_ylabel('Average Voltage [V]')
ax3.set_title('PWM Duty Cycle vs. Average Output Voltage')
ax3.grid(True, alpha=0.3)
ax3.fill_between(D_range * 100, V_avg_range, alpha=0.1, color='blue')
ax3.set_xlim(0, 100)
ax3.set_ylim(0, V_supply * 1.05)

# Add annotations
ax3.annotate('Linear relationship:\nV_avg = D × V_supply',
             xy=(50, 6), fontsize=12, ha='center',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.tight_layout()
plt.savefig('pwm-duty-cycle.png', dpi=150, bbox_inches='tight')
plt.show()


# =============================================================================
# Summary
# =============================================================================
print("=" * 60)
print("PWM Control Summary")
print("=" * 60)
print(f"Supply voltage: {V_supply} V")
print(f"Motor parameters: R={R_motor}Ω, L={L_motor*1e3}mH, τ_e={tau_e*1e3}ms")
print(f"\nKey results:")
print(f"  V_avg = D × V_supply (linear relationship)")
print(f"  Current ripple ∝ 1/f_PWM (inversely proportional to frequency)")
print(f"  f_PWM should be >> 1/τ_e = {1/tau_e:.0f} Hz for smooth current")
print(f"\nPractical guidelines:")
print(f"  - Motor drives: f_PWM = 5-20 kHz (above audible)")
print(f"  - LED drivers: f_PWM > 1 kHz (no visible flicker)")
print(f"  - Power converters: f_PWM = 100kHz-2MHz (small components)")
