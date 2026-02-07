"""
Pole Placement via State Feedback
===================================

Purpose:
    Design a full-state feedback controller using pole placement
    for a double-integrator plant (e.g., position control of a mass).
    Compare open-loop and closed-loop responses.

Plant (state-space):
    ẋ = Ax + Bu,  y = Cx
    
    A = [[0, 1],    B = [[0],    C = [1, 0]
         [0, 0]]         [1]]
         
    This is: ẍ = u  (double integrator: mass with force input)
    States: x1 = position, x2 = velocity

Design:
    Place closed-loop poles at s = -3 ± j3  (ζ = 0.707, ωn = 4.24)
"""

import numpy as np
from scipy import signal
from scipy.linalg import solve
import matplotlib.pyplot as plt


# =============================================================================
# Plant Definition
# =============================================================================
A = np.array([[0, 1],
              [0, 0]])
B = np.array([[0],
              [1]])
C = np.array([[1, 0]])
D = np.array([[0]])

n = A.shape[0]  # Number of states

print("Plant: Double Integrator (mass with force input)")
print(f"  A = {A.tolist()}")
print(f"  B = {B.tolist()}")
print(f"  C = {C.tolist()}")
print(f"  Open-loop eigenvalues: {np.linalg.eigvals(A)}")


# =============================================================================
# Check Controllability
# =============================================================================
# Controllability matrix: C = [B, AB, A²B, ..., A^(n-1)B]
controllability_matrix = np.hstack([
    np.linalg.matrix_power(A, i) @ B for i in range(n)
])
rank = np.linalg.matrix_rank(controllability_matrix)

print(f"\nControllability Matrix:")
print(f"  {controllability_matrix.tolist()}")
print(f"  Rank = {rank} (need {n} for controllability)")
print(f"  System is {'CONTROLLABLE ✓' if rank == n else 'NOT CONTROLLABLE ✗'}")


# =============================================================================
# Pole Placement using Ackermann's Formula
# =============================================================================
desired_poles = np.array([-3 + 3j, -3 - 3j])  # ζ = 0.707, ωn = 4.24

print(f"\nDesired closed-loop poles: {desired_poles}")
print(f"  Damping ratio ζ = {abs(desired_poles[0].real) / abs(desired_poles[0]):.3f}")
print(f"  Natural frequency ωn = {abs(desired_poles[0]):.2f} rad/s")

# Desired characteristic polynomial: (s - p1)(s - p2)
# = s² + 6s + 18
desired_char_poly = np.poly(desired_poles)  # [1, 6, 18]
print(f"  Desired char. poly: s² + {desired_char_poly[1]:.1f}s + {desired_char_poly[2]:.1f}")

# Ackermann's formula: K = [0 ... 0 1] * C^{-1} * α_c(A)
# α_c(A) = A² + 6A + 18I
alpha_c_A = (np.linalg.matrix_power(A, 2) 
             + desired_char_poly[1] * A 
             + desired_char_poly[2] * np.eye(n))

e_n = np.zeros(n)
e_n[-1] = 1  # [0, 1] for 2nd order

K = e_n @ np.linalg.inv(controllability_matrix) @ alpha_c_A
K = K.reshape(1, -1)  # Row vector

print(f"\nState Feedback Gain:")
print(f"  K = {K}")

# Verify: eigenvalues of (A - BK)
A_cl = A - B @ K
cl_poles = np.linalg.eigvals(A_cl)
print(f"  Closed-loop eigenvalues: {cl_poles}")
print(f"  Match desired: {np.allclose(sorted(cl_poles, key=lambda x: x.real), sorted(desired_poles, key=lambda x: x.real))}")


# =============================================================================
# Reference Tracking Gain (DC gain correction)
# =============================================================================
# For step reference tracking: u = -Kx + N_bar * r
# N_bar = 1 / (C * (-A + BK)^{-1} * B)  -- corrects steady-state gain
N_bar_inv = C @ np.linalg.solve(-(A - B @ K), B)
N_bar = 1.0 / N_bar_inv[0, 0]
print(f"\nReference gain N_bar = {N_bar:.2f}")


# =============================================================================
# Simulate Step Response
# =============================================================================
# Closed-loop state-space: ẋ = (A-BK)x + B*N_bar*r
B_cl = B * N_bar

sys_cl = signal.StateSpace(A_cl, B_cl, C, D)
sys_ol = signal.StateSpace(A, B, C, D)

t = np.linspace(0, 3, 1000)

# Closed-loop step response
t_cl, y_cl, x_cl = signal.lsim(sys_cl, U=np.ones_like(t), T=t)

# Open-loop step response (ramp output for double integrator!)
t_ol, y_ol, x_ol = signal.lsim(sys_ol, U=np.ones_like(t), T=t)

fig, axes = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
fig.suptitle('State Feedback Pole Placement — Double Integrator', fontsize=14)

# Position (output)
axes[0].plot(t_cl, y_cl, 'b-', linewidth=2, label='Closed-loop (with feedback)')
axes[0].plot(t_ol, y_ol, 'r--', linewidth=1.5, label='Open-loop (no feedback)')
axes[0].axhline(y=1.0, color='k', linestyle=':', alpha=0.5, label='Reference')
axes[0].set_ylabel('Position x₁')
axes[0].legend()
axes[0].grid(True, alpha=0.3)
axes[0].set_ylim(-0.2, 2.5)

# Velocity (state x2)
axes[1].plot(t_cl, x_cl[:, 1], 'b-', linewidth=2, label='Closed-loop velocity')
axes[1].plot(t_ol, x_ol[:, 1], 'r--', linewidth=1.5, label='Open-loop velocity')
axes[1].set_ylabel('Velocity x₂')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Control input u = -Kx + N_bar*r
u_cl = -K @ x_cl.T + N_bar * np.ones_like(t)
u_ol = np.ones_like(t)
axes[2].plot(t_cl, u_cl.flatten(), 'b-', linewidth=2, label='Closed-loop u')
axes[2].plot(t_ol, u_ol, 'r--', linewidth=1.5, label='Open-loop u')
axes[2].set_ylabel('Control Input u')
axes[2].set_xlabel('Time [s]')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('pole-placement-response.png', dpi=150, bbox_inches='tight')
plt.show()


# =============================================================================
# Summary
# =============================================================================
overshoot = (np.max(y_cl) - 1) * 100
idx_settle = np.where(np.abs(y_cl - 1.0) > 0.02)[0]
settle_time = t_cl[idx_settle[-1]] if len(idx_settle) > 0 else 0

print(f"\n{'=' * 50}")
print("Step Response Metrics (Closed-Loop):")
print(f"  Overshoot: {overshoot:.1f}%")
print(f"  2% settling time: ~{settle_time:.2f} s")
print(f"  Steady-state value: {y_cl[-1]:.4f}")
print(f"\nNote: Open-loop double integrator diverges (position → ∞)")
print(f"  Feedback stabilizes and controls the unstable plant.")
