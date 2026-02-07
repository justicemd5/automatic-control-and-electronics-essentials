"""
Model Reference Adaptive Control (MRAC)
=========================================

Purpose:
    Implement MRAC to control a first-order plant with unknown gain.
    The adaptive controller adjusts its gain online to match the
    closed-loop response to a reference model.

Plant:     ẏ = -a*y + b*u     (a=1 known, b unknown, true b=2)
Reference: ẏ_m = -a_m*y_m + b_m*r  (a_m=3, b_m=3, desired dynamics)

Control law: u = θ̂(t) * r
Adaptation:  θ̂̇ = -γ * e * r    (MIT rule)
             where e = y - y_m
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt


# =============================================================================
# System Parameters
# =============================================================================
# Unknown plant
a_plant = 1.0    # Plant pole (known for simplicity)
b_plant = 2.0    # Plant gain (UNKNOWN to controller)

# Reference model (desired closed-loop behavior)
a_model = 3.0    # Faster pole
b_model = 3.0    # Unity DC gain: b_m/a_m = 1

# Ideal controller gain: θ* = b_m / b_plant = 3/2 = 1.5
theta_star = b_model / b_plant
print(f"Plant: ẏ = -{a_plant}y + {b_plant}u")
print(f"Reference: ẏ_m = -{a_model}y_m + {b_model}r")
print(f"Ideal gain: θ* = {theta_star}")

# Adaptation gain
gamma = 5.0  # Higher = faster adaptation, but may oscillate

# Reference input
def r_func(t):
    """Square wave reference signal."""
    return 1.0 * np.sign(np.sin(0.5 * np.pi * t))


# =============================================================================
# MRAC Dynamics
# =============================================================================
def mrac_system(t, z):
    """
    State vector: z = [y, y_m, theta_hat]
    y: plant output
    y_m: reference model output
    theta_hat: adaptive gain estimate
    """
    y, y_m, theta_hat = z
    
    r = r_func(t)
    
    # Control law
    u = theta_hat * r
    
    # Plant: ẏ = -a*y + b*u
    dy = -a_plant * y + b_plant * u
    
    # Reference model: ẏ_m = -a_m*y_m + b_m*r
    dy_m = -a_model * y_m + b_model * r
    
    # Tracking error
    e = y - y_m
    
    # Adaptation law (MIT rule)
    dtheta = -gamma * e * r
    
    return [dy, dy_m, dtheta]


# =============================================================================
# Simulation
# =============================================================================
t_span = (0, 30)
z0 = [0.0, 0.0, 0.5]  # Start with wrong gain estimate (θ̂₀ = 0.5, ideal = 1.5)

t_eval = np.linspace(0, 30, 3000)
sol = solve_ivp(mrac_system, t_span, z0, t_eval=t_eval,
                method='RK45', max_step=0.01)

t = sol.t
y = sol.y[0]
y_m = sol.y[1]
theta_hat = sol.y[2]
e = y - y_m
r_signal = np.array([r_func(ti) for ti in t])


# =============================================================================
# Also simulate WITHOUT adaptation (fixed wrong gain)
# =============================================================================
def fixed_gain_system(t, z):
    y, y_m = z
    r = r_func(t)
    u = 0.5 * r  # Fixed wrong gain
    dy = -a_plant * y + b_plant * u
    dy_m = -a_model * y_m + b_model * r
    return [dy, dy_m]

sol_fixed = solve_ivp(fixed_gain_system, t_span, [0.0, 0.0],
                       t_eval=t_eval, method='RK45', max_step=0.01)
y_fixed = sol_fixed.y[0]


# =============================================================================
# Plot Results
# =============================================================================
fig, axes = plt.subplots(4, 1, figsize=(12, 12), sharex=True)
fig.suptitle('Model Reference Adaptive Control (MRAC)', fontsize=14)

# Output tracking
axes[0].plot(t, r_signal, 'k:', linewidth=1, alpha=0.5, label='Reference r(t)')
axes[0].plot(t, y_m, 'g-', linewidth=2, label='Model output y_m')
axes[0].plot(t, y, 'b-', linewidth=2, label='Plant output y (MRAC)')
axes[0].plot(t, y_fixed, 'r--', linewidth=1.5, label='Plant output (fixed wrong gain)')
axes[0].set_ylabel('Output')
axes[0].legend(loc='upper right', fontsize=9)
axes[0].grid(True, alpha=0.3)

# Tracking error
axes[1].plot(t, e, 'b-', linewidth=1.5, label='Tracking error e = y − y_m')
axes[1].axhline(y=0, color='k', linestyle=':', alpha=0.5)
axes[1].set_ylabel('Error e(t)')
axes[1].legend(fontsize=9)
axes[1].grid(True, alpha=0.3)

# Adaptive gain
axes[2].plot(t, theta_hat, 'b-', linewidth=2, label='Estimated θ̂(t)')
axes[2].axhline(y=theta_star, color='r', linestyle='--', linewidth=2,
                 label=f'Ideal θ* = {theta_star:.2f}')
axes[2].axhline(y=0.5, color='gray', linestyle=':', alpha=0.5,
                 label='Initial θ̂₀ = 0.5')
axes[2].set_ylabel('Controller Gain θ̂')
axes[2].legend(fontsize=9)
axes[2].grid(True, alpha=0.3)

# Control signal
u_signal = theta_hat * r_signal
axes[3].plot(t, u_signal, 'b-', linewidth=1.5, label='Control u = θ̂·r')
axes[3].set_ylabel('Control u(t)')
axes[3].set_xlabel('Time [s]')
axes[3].legend(fontsize=9)
axes[3].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('mrac-simulation.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"\nResults:")
print(f"  Initial θ̂ = {z0[2]:.2f}, Ideal θ* = {theta_star:.2f}")
print(f"  Final θ̂   = {theta_hat[-1]:.4f}")
print(f"  Adaptation gain γ = {gamma}")
print(f"  Final tracking error: |e| = {abs(e[-1]):.6f}")
