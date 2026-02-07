"""
Luenberger Observer Design
============================

Purpose:
    Design a full-order Luenberger observer for a system where
    only the output (position) is measured, and velocity must be
    estimated. Show the estimation error convergence.

System:
    Mass-spring-damper: m*ẍ + c*ẋ + k*x = F
    States: x1 = position, x2 = velocity
    Output: y = x1 (position only)
    
    A = [[0, 1], [-k/m, -c/m]]
    B = [[0], [1/m]]
    C = [1, 0]

Observer:
    x̂̇ = A*x̂ + B*u + L*(y - C*x̂)
    Observer poles placed 5× faster than plant poles
"""

import numpy as np
from scipy import signal
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt


# =============================================================================
# System Parameters
# =============================================================================
m = 1.0    # Mass [kg]
c = 2.0    # Damping [N·s/m]
k = 10.0   # Stiffness [N/m]

# State-space matrices
A = np.array([[0, 1],
              [-k/m, -c/m]])
B = np.array([[0],
              [1/m]])
C = np.array([[1, 0]])
D = np.array([[0]])

# Plant eigenvalues
plant_poles = np.linalg.eigvals(A)
print("System: Mass-Spring-Damper")
print(f"  m = {m}, c = {c}, k = {k}")
print(f"  Plant poles: {plant_poles}")
wn = np.sqrt(k/m)
zeta = c / (2 * np.sqrt(k * m))
print(f"  ωn = {wn:.2f} rad/s, ζ = {zeta:.2f}")


# =============================================================================
# Observer Design
# =============================================================================
# Place observer poles 5× faster than plant poles
obs_poles = 5 * plant_poles
print(f"\nObserver poles: {obs_poles}")

# Desired observer characteristic polynomial
# (s - p1)(s - p2) = s² - (p1+p2)s + p1*p2
obs_char = np.poly(obs_poles)  # [1, -(p1+p2), p1*p2]

# For a 2nd-order system with C = [1 0]:
# Observer gains from Ackermann's formula
# Or directly: det(sI - A + LC) should match desired polynomial

# A - LC eigenvalues = observer poles
# Observability matrix
O = np.vstack([C, C @ A])
print(f"\nObservability matrix:\n  {O.tolist()}")
print(f"  Rank = {np.linalg.matrix_rank(O)} → {'Observable ✓' if np.linalg.matrix_rank(O) == 2 else 'Not Observable ✗'}")

# Ackermann for observer: L = alpha_o(A) * O^{-1} * [0; 1]
alpha_o_A = np.linalg.matrix_power(A, 2) + obs_char[1] * A + obs_char[2] * np.eye(2)
e_n = np.array([0, 1])
L = alpha_o_A @ np.linalg.inv(O) @ e_n
L = L.reshape(-1, 1)

print(f"\nObserver gain L = {L.flatten()}")

# Verify observer poles
A_obs = A - L @ C
obs_eigs = np.linalg.eigvals(A_obs)
print(f"  Observer eigenvalues: {obs_eigs}")
print(f"  Match desired: {np.allclose(sorted(obs_eigs, key=lambda x: x.real), sorted(obs_poles, key=lambda x: x.real))}")


# =============================================================================
# Simulation: Plant + Observer
# =============================================================================
def plant_observer(t, z, A, B, C, L):
    """Combined plant + observer dynamics."""
    x = z[:2]         # True states
    x_hat = z[2:4]    # Estimated states
    
    # Input (step force)
    u = np.array([1.0]) if t > 0.5 else np.array([0.0])
    
    # Plant dynamics: ẋ = Ax + Bu
    dx = A @ x + (B @ u).flatten()
    
    # Observer dynamics: x̂̇ = Ax̂ + Bu + L(y - Cx̂)
    y = C @ x       # True output (measurement)
    y_hat = C @ x_hat  # Estimated output
    innovation = y - y_hat  # Measurement residual
    dx_hat = A @ x_hat + (B @ u).flatten() + (L @ innovation).flatten()
    
    return np.concatenate([dx, dx_hat])


# Initial conditions: plant at origin, observer has wrong initial estimate
x0_plant = np.array([0.0, 0.0])
x0_observer = np.array([0.5, -1.0])  # Wrong initial guess!
z0 = np.concatenate([x0_plant, x0_observer])

t_span = (0, 5)
t_eval = np.linspace(0, 5, 2000)

sol = solve_ivp(plant_observer, t_span, z0, t_eval=t_eval,
                args=(A, B, C, L), method='RK45', max_step=0.001)


# =============================================================================
# Extract Results
# =============================================================================
t = sol.t
x1_true = sol.y[0]     # True position
x2_true = sol.y[1]     # True velocity
x1_hat = sol.y[2]      # Estimated position
x2_hat = sol.y[3]      # Estimated velocity

e1 = x1_true - x1_hat  # Position estimation error
e2 = x2_true - x2_hat  # Velocity estimation error


# =============================================================================
# Plot Results
# =============================================================================
fig, axes = plt.subplots(4, 1, figsize=(12, 12), sharex=True)
fig.suptitle('Luenberger Observer — State Estimation', fontsize=14)

# Position
axes[0].plot(t, x1_true, 'b-', linewidth=2, label='True position x₁')
axes[0].plot(t, x1_hat, 'r--', linewidth=2, label='Estimated position x̂₁')
axes[0].set_ylabel('Position [m]')
axes[0].legend(loc='upper right')
axes[0].grid(True, alpha=0.3)

# Velocity
axes[1].plot(t, x2_true, 'b-', linewidth=2, label='True velocity x₂')
axes[1].plot(t, x2_hat, 'r--', linewidth=2, label='Estimated velocity x̂₂')
axes[1].set_ylabel('Velocity [m/s]')
axes[1].legend(loc='upper right')
axes[1].grid(True, alpha=0.3)

# Estimation errors
axes[2].plot(t, e1, 'b-', linewidth=2, label='Position error (x₁ − x̂₁)')
axes[2].plot(t, e2, 'r-', linewidth=2, label='Velocity error (x₂ − x̂₂)')
axes[2].set_ylabel('Estimation Error')
axes[2].legend(loc='upper right')
axes[2].grid(True, alpha=0.3)
axes[2].axhline(y=0, color='k', linestyle=':', alpha=0.5)

# Error magnitude (log scale)
e_mag = np.sqrt(e1**2 + e2**2)
axes[3].semilogy(t, e_mag + 1e-10, 'k-', linewidth=2)
axes[3].set_ylabel('‖Error‖ (log)')
axes[3].set_xlabel('Time [s]')
axes[3].grid(True, alpha=0.3)

# Calculate convergence time
mask = e_mag > 0.01
if np.any(mask):
    conv_time = t[np.where(mask)[0][-1]]
    axes[3].axvline(x=conv_time, color='g', linestyle='--',
                     label=f'1% convergence: {conv_time:.2f}s')
    axes[3].legend()

plt.tight_layout()
plt.savefig('observer-estimation.png', dpi=150, bbox_inches='tight')
plt.show()


# =============================================================================
# Summary
# =============================================================================
print(f"\n{'=' * 50}")
print("Observer Performance Summary:")
print(f"  Initial estimation error: [{x0_observer[0] - x0_plant[0]:.1f}, {x0_observer[1] - x0_plant[1]:.1f}]")
print(f"  Observer pole speed: {abs(obs_poles[0].real):.1f}× plant pole speed")
print(f"  Expected convergence: τ_obs = {1/abs(obs_poles[0].real):.4f} s")
print(f"  Final estimation error: [{e1[-1]:.6f}, {e2[-1]:.6f}]")
print(f"\nKey insight: Observer converges despite starting with")
print(f"  completely wrong state estimates, using only position measurement!")
