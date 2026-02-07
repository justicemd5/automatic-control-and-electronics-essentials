"""
LQR Design for Inverted Pendulum on Cart
==========================================

Purpose:
    Design and simulate an LQR controller for the classic
    cart-pendulum (cart-pole) balancing problem. Demonstrates
    Q/R tuning and the effect on state regulation.

State: x = [cart_position, cart_velocity, angle, angular_velocity]
      (angle = 0 is upright, positive = clockwise)

Linearized model about the upright equilibrium.
"""

import numpy as np
from scipy.linalg import solve_continuous_are
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt


# =============================================================================
# System Parameters
# =============================================================================
M = 1.0    # Cart mass [kg]
m = 0.3    # Pendulum mass [kg]
L = 0.5    # Pendulum half-length [m]
g = 9.81   # Gravity [m/s²]
b = 0.1    # Cart friction [N·s/m]

# Derived
mt = M + m  # Total mass


# =============================================================================
# Linearized State-Space Model (about upright equilibrium)
# =============================================================================
# State: x = [cart_pos, cart_vel, theta, theta_dot]
# Input: u = force on cart

A = np.array([
    [0,       1,             0,           0],
    [0,   -b/mt,       -m*g/mt,           0],
    [0,       0,             0,           1],
    [0, b/(mt*L), mt*g/(mt*L),           0]
])

B = np.array([
    [0],
    [1/mt],
    [0],
    [-1/(mt*L)]
])

C = np.array([
    [1, 0, 0, 0],
    [0, 0, 1, 0]
])

print("System matrices:")
print(f"A =\n{A}")
print(f"\nB =\n{B.flatten()}")

# Check open-loop eigenvalues
eig_ol = np.linalg.eigvals(A)
print(f"\nOpen-loop eigenvalues: {eig_ol}")
print(f"System is {'UNSTABLE' if any(e.real > 0 for e in eig_ol) else 'stable'}")

# Check controllability
Wc = np.hstack([B, A @ B, A @ A @ B, A @ A @ A @ B])
rank_Wc = np.linalg.matrix_rank(Wc)
print(f"Controllability rank: {rank_Wc} / {A.shape[0]} → {'Controllable ✓' if rank_Wc == 4 else 'NOT controllable ✗'}")


# =============================================================================
# LQR Design - Three Different Tunings
# =============================================================================
def design_lqr(A, B, Q, R):
    """Solve the continuous-time LQR problem."""
    P = solve_continuous_are(A, B, Q, R)
    K = np.linalg.inv(R) @ B.T @ P
    eig_cl = np.linalg.eigvals(A - B @ K)
    return K, P, eig_cl


# --- Tuning 1: Balanced (Bryson's rule) ---
# Max acceptable: position = 0.5m, velocity = 2m/s, angle = 15°, ang_vel = 2rad/s
# Max force: 20 N
Q1 = np.diag([1/0.5**2, 1/2**2, 1/(15*np.pi/180)**2, 1/2**2])
R1 = np.array([[1/20**2]])

K1, P1, eig1 = design_lqr(A, B, Q1, R1)
print(f"\n--- Tuning 1: Balanced (Bryson's rule) ---")
print(f"Q = diag{np.diag(Q1).tolist()}")
print(f"R = {R1[0,0]:.6f}")
print(f"K = {K1.flatten()}")
print(f"Closed-loop eigenvalues: {eig1}")

# --- Tuning 2: Aggressive (tight angle control) ---
Q2 = np.diag([1, 0.1, 100, 1])
R2 = np.array([[0.01]])

K2, P2, eig2 = design_lqr(A, B, Q2, R2)
print(f"\n--- Tuning 2: Aggressive (tight angle control) ---")
print(f"K = {K2.flatten()}")
print(f"Closed-loop eigenvalues: {eig2}")

# --- Tuning 3: Conservative (limit control effort) ---
Q3 = np.diag([1, 0.1, 10, 0.1])
R3 = np.array([[1]])

K3, P3, eig3 = design_lqr(A, B, Q3, R3)
print(f"\n--- Tuning 3: Conservative (low effort) ---")
print(f"K = {K3.flatten()}")
print(f"Closed-loop eigenvalues: {eig3}")


# =============================================================================
# Nonlinear Simulation
# =============================================================================
def pendulum_nonlinear(t, x, K):
    """Full nonlinear equations of motion with LQR feedback."""
    pos, vel, theta, omega = x
    
    # LQR control
    u = -K @ x
    u = np.clip(u, -50, 50)  # Actuator saturation
    F = u[0]
    
    # Nonlinear dynamics
    sin_t = np.sin(theta)
    cos_t = np.cos(theta)
    
    denom = mt - m * cos_t**2
    
    acc = (F - b * vel + m * L * omega**2 * sin_t - m * g * sin_t * cos_t) / denom
    alpha = (-F * cos_t + b * vel * cos_t - m * L * omega**2 * sin_t * cos_t + mt * g * sin_t) / (L * denom)
    
    return [vel, acc, omega, alpha]


# Initial condition: pendulum tilted 20° from upright
x0 = [0.0, 0.0, 20 * np.pi / 180, 0.0]
t_span = (0, 5)
t_eval = np.linspace(0, 5, 1000)

# Simulate all three tunings
results = {}
for name, K in [("Balanced", K1), ("Aggressive", K2), ("Conservative", K3)]:
    sol = solve_ivp(lambda t, x: pendulum_nonlinear(t, x, K),
                    t_span, x0, t_eval=t_eval, method='RK45', max_step=0.005)
    u_hist = np.array([-K @ sol.y[:, i] for i in range(len(sol.t))])
    u_hist = np.clip(u_hist, -50, 50)
    results[name] = {'t': sol.t, 'x': sol.y, 'u': u_hist.flatten()}


# =============================================================================
# Plot Results
# =============================================================================
fig, axes = plt.subplots(4, 1, figsize=(12, 14), sharex=True)
fig.suptitle('LQR Control of Inverted Pendulum — Three Tunings', fontsize=14)

colors = {'Balanced': 'blue', 'Aggressive': 'red', 'Conservative': 'green'}
labels_y = ['Cart Position [m]', 'Cart Velocity [m/s]', 
            'Pendulum Angle [°]', 'Control Force [N]']

for name, res in results.items():
    c = colors[name]
    axes[0].plot(res['t'], res['x'][0], color=c, linewidth=2, label=name)
    axes[1].plot(res['t'], res['x'][1], color=c, linewidth=2)
    axes[2].plot(res['t'], res['x'][2] * 180 / np.pi, color=c, linewidth=2)
    axes[3].plot(res['t'], res['u'], color=c, linewidth=2)

for i, label in enumerate(labels_y):
    axes[i].set_ylabel(label)
    axes[i].grid(True, alpha=0.3)
    axes[i].axhline(y=0, color='k', linestyle=':', alpha=0.5)

axes[0].legend(fontsize=11)
axes[3].set_xlabel('Time [s]')

# Add saturation limits to force plot
axes[3].axhline(y=50, color='k', linestyle='--', alpha=0.3, label='Saturation')
axes[3].axhline(y=-50, color='k', linestyle='--', alpha=0.3)

plt.tight_layout()
plt.savefig('lqr-inverted-pendulum.png', dpi=150, bbox_inches='tight')
plt.show()


# =============================================================================
# Summary Table
# =============================================================================
print("\n" + "=" * 70)
print("Performance Comparison")
print("=" * 70)
print(f"{'Tuning':<15} {'Settle[s]':<12} {'Max |θ|[°]':<12} {'Max |F|[N]':<12} {'Max |x|[m]':<12}")
print("-" * 70)

for name, res in results.items():
    theta_max = np.max(np.abs(res['x'][2])) * 180 / np.pi
    force_max = np.max(np.abs(res['u']))
    pos_max = np.max(np.abs(res['x'][0]))
    
    # Settling time (2% of initial angle = 0.4°)
    theta_deg = np.abs(res['x'][2]) * 180 / np.pi
    settled = theta_deg < 0.4
    if np.any(settled):
        settle_idx = np.argmax(settled)
        settle_t = res['t'][settle_idx]
    else:
        settle_t = float('inf')
    
    print(f"{name:<15} {settle_t:<12.2f} {theta_max:<12.1f} {force_max:<12.1f} {pos_max:<12.3f}")

print("\nKey: Aggressive = fast angle control, large force")
print("     Conservative = slow but gentle, minimal force")
print("     Balanced = Bryson's rule starting point")
