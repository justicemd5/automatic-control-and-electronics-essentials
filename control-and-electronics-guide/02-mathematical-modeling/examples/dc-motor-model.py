"""
DC Motor Mathematical Model — Derivation and Simulation
========================================================

Purpose:
    Derive the coupled electrical-mechanical model of a DC motor,
    convert to transfer function and state-space forms, and simulate
    the step response.

Physical Model:
    A DC motor has two coupled subsystems:
    
    Electrical (armature circuit):
        L * di/dt + R*i = V - Kb*ω
        
    Mechanical (rotor):
        J * dω/dt + b*ω = Kt*i - τ_load
    
    Coupling:
        Back-EMF:  e = Kb * ω
        Torque:    τ = Kt * i
        
    For an ideal motor: Kt = Kb = K (motor constant)

Transfer Function (from voltage V to angular velocity ω):
    
    ω(s)     Kt
    ──── = ──────────────────────────────────
    V(s)   (Ls + R)(Js + b) + Kt·Kb

    This is a second-order system with one electrical and one mechanical pole.

State Variables:
    x1 = i  (armature current)
    x2 = ω  (angular velocity)

State-Space Form:
    ┌ di/dt ┐   ┌ -R/L   -Kb/L ┐ ┌ i ┐   ┌ 1/L ┐
    │       │ = │               │ │   │ + │     │ V
    └ dω/dt ┘   └ Kt/J   -b/J  ┘ └ ω ┘   └  0  ┘

Expected Behavior:
    - Step voltage input → current spikes, then decays as back-EMF builds
    - Angular velocity rises and settles to steady-state
    - Steady-state speed: ω_ss = Kt*V / (R*b + Kt*Kb)
"""

import numpy as np
from scipy import signal
import matplotlib.pyplot as plt


# =============================================================================
# Motor Parameters (typical small DC motor)
# =============================================================================
R = 1.0       # Armature resistance [Ω]
L = 0.5       # Armature inductance [H]
Kt = 0.01     # Torque constant [N·m/A]
Kb = 0.01     # Back-EMF constant [V·s/rad] (= Kt for ideal motor)
J = 0.01      # Rotor moment of inertia [kg·m²]
b = 0.1       # Viscous friction coefficient [N·m·s/rad]
V_input = 12  # Step input voltage [V]


# =============================================================================
# Transfer Function: V(s) → ω(s)
# =============================================================================
# Numerator: Kt
# Denominator: (Ls + R)(Js + b) + Kt*Kb = LJ*s² + (Lb + RJ)*s + (Rb + Kt*Kb)

num = [Kt]
den = [L * J, (L * b + R * J), (R * b + Kt * Kb)]

print("=" * 60)
print("DC Motor Transfer Function: V(s) → ω(s)")
print("=" * 60)
print(f"Numerator coefficients:   {num}")
print(f"Denominator coefficients: {den}")

# Create transfer function object
motor_tf = signal.TransferFunction(num, den)
print(f"\nPoles: {np.roots(den)}")
print(f"Zeros: {np.roots(num) if len(num) > 1 else 'None'}")

# Steady-state speed for unit voltage
omega_ss = Kt / (R * b + Kt * Kb)
print(f"\nSteady-state speed per volt: {omega_ss:.4f} rad/s/V")
print(f"Steady-state speed at {V_input}V: {omega_ss * V_input:.4f} rad/s")


# =============================================================================
# State-Space Model
# =============================================================================
A = np.array([
    [-R / L, -Kb / L],
    [Kt / J, -b / J]
])

B = np.array([
    [1 / L],
    [0]
])

C_current = np.array([[1, 0]])   # Output = current
C_speed = np.array([[0, 1]])     # Output = angular velocity
D = np.array([[0]])

print("\n" + "=" * 60)
print("State-Space Matrices")
print("=" * 60)
print(f"A = \n{A}")
print(f"\nB = \n{B}")
print(f"\nC (speed output) = {C_speed}")
print(f"\nD = {D}")

# Verify eigenvalues match transfer function poles
eigenvalues = np.linalg.eigvals(A)
print(f"\nEigenvalues of A: {eigenvalues}")
print(f"(Should match poles: {np.roots(den)})")


# =============================================================================
# Simulation: Step Response
# =============================================================================
t = np.linspace(0, 3, 1000)

# Using state-space for simulation (to get both current and speed)
motor_ss_speed = signal.StateSpace(A, B, C_speed, D)
motor_ss_current = signal.StateSpace(A, B, C_current, D)

t_out, omega_out = signal.step(motor_ss_speed, T=t)
_, current_out = signal.step(motor_ss_current, T=t)

# Scale by input voltage (step response is for unit step)
omega_out *= V_input
current_out *= V_input


# =============================================================================
# Plotting
# =============================================================================
fig, axes = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

# Plot 1: Angular velocity
axes[0].plot(t_out, omega_out, 'b-', linewidth=2, label='ω(t)')
axes[0].axhline(y=omega_ss * V_input, color='r', linestyle='--',
                label=f'Steady state = {omega_ss * V_input:.3f} rad/s')
axes[0].set_ylabel('Angular Velocity [rad/s]')
axes[0].set_title(f'DC Motor Step Response (V = {V_input} V)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Plot 2: Armature current
axes[1].plot(t_out, current_out, 'r-', linewidth=2, label='i(t)')
i_initial = V_input / R
i_ss = Kt * omega_ss * V_input  # Not quite right; let's compute properly
# At steady state: i_ss = (V - Kb*ω_ss) / R
omega_ss_actual = omega_ss * V_input
i_ss_actual = (V_input - Kb * omega_ss_actual) / R
axes[1].axhline(y=i_ss_actual, color='b', linestyle='--',
                label=f'Steady-state current = {i_ss_actual:.3f} A')
axes[1].axhline(y=V_input / R, color='g', linestyle=':',
                label=f'Initial current (V/R) = {V_input / R:.1f} A')
axes[1].set_ylabel('Current [A]')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Plot 3: Back-EMF
back_emf = Kb * omega_out
axes[2].plot(t_out, back_emf, 'g-', linewidth=2, label='e(t) = Kb·ω(t)')
axes[2].plot(t_out, V_input - back_emf, 'm--', linewidth=1.5,
             label='V - e(t) (net voltage across R,L)')
axes[2].set_ylabel('Voltage [V]')
axes[2].set_xlabel('Time [s]')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('dc-motor-step-response.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n" + "=" * 60)
print("Simulation Summary")
print("=" * 60)
print(f"Initial current (t=0+): V/R = {V_input/R:.2f} A")
print(f"Steady-state current:   {i_ss_actual:.4f} A")
print(f"Steady-state speed:     {omega_ss_actual:.4f} rad/s")
print(f"Back-EMF at steady state: {Kb * omega_ss_actual:.4f} V")
print(f"\nPhysical interpretation:")
print(f"  - At t=0, motor is stalled: no back-EMF, maximum current")
print(f"  - As motor spins up, back-EMF opposes applied voltage")
print(f"  - Current decreases as speed increases")
print(f"  - At steady state, just enough current flows to overcome friction")
