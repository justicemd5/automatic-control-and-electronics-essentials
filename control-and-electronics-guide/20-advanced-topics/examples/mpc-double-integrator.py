"""
Model Predictive Control (MPC) — Double Integrator with Constraints
====================================================================

Purpose:
    Implement a basic MPC controller for a double integrator system
    (e.g., position control of a mass) with input and state constraints.
    Uses quadratic programming (QP) to solve the optimization at each step.

System:
    ẍ = u  (force on unit mass)
    State: x = [position, velocity]
    Input: u = force (constrained to [-1, +1])
    State constraint: velocity ∈ [-0.5, +0.5]

Dependencies:
    pip install numpy scipy matplotlib
    Optional: pip install cvxpy (for cleaner QP formulation)
"""

import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt


# =============================================================================
# System Definition (Discrete-Time)
# =============================================================================
dt = 0.1  # Sample time [s]

# Continuous: ẋ = [0 1; 0 0]x + [0; 1]u
# Discretized (ZOH):
A = np.array([[1, dt],
              [0, 1]])

B = np.array([[0.5 * dt**2],
              [dt]])

nx = 2  # Number of states
nu = 1  # Number of inputs


# =============================================================================
# MPC Parameters
# =============================================================================
N = 20          # Prediction horizon
Q = np.diag([10.0, 1.0])    # State penalty [position, velocity]
R = np.array([[0.1]])        # Input penalty
P = Q * 10                   # Terminal cost (should be from DARE, simplified here)

# Constraints
u_min, u_max = -1.0, 1.0      # Input constraints
v_min, v_max = -0.5, 0.5      # Velocity constraints


# =============================================================================
# MPC Solver (using scipy.optimize)
# =============================================================================
def mpc_solve(x0, x_ref, N, A, B, Q, R, P):
    """
    Solve the MPC optimization problem.
    
    Decision variables: U = [u_0, u_1, ..., u_{N-1}]  (N × nu)
    
    Minimize:  Σ (x_k - x_ref)' Q (x_k - x_ref) + u_k' R u_k
               + (x_N - x_ref)' P (x_N - x_ref)
    
    Subject to: x_{k+1} = A x_k + B u_k
                u_min ≤ u_k ≤ u_max
                v_min ≤ x_k[1] ≤ v_max
    """
    
    def cost_function(U_flat):
        """Compute the total cost for a given input sequence."""
        U = U_flat.reshape(N, nu)
        x = x0.copy()
        cost = 0.0
        
        for k in range(N):
            # State cost
            dx = x - x_ref
            cost += dx @ Q @ dx + U[k] @ R @ U[k]
            
            # Propagate dynamics
            x = A @ x + B @ U[k]
        
        # Terminal cost
        dx = x - x_ref
        cost += dx @ P @ dx
        
        return cost
    
    def velocity_constraint_lower(U_flat, step):
        """Velocity >= v_min at time step 'step'."""
        U = U_flat.reshape(N, nu)
        x = x0.copy()
        for k in range(step + 1):
            x = A @ x + B @ U[k]
        return x[1] - v_min  # Must be >= 0
    
    def velocity_constraint_upper(U_flat, step):
        """Velocity <= v_max at time step 'step'."""
        U = U_flat.reshape(N, nu)
        x = x0.copy()
        for k in range(step + 1):
            x = A @ x + B @ U[k]
        return v_max - x[1]  # Must be >= 0
    
    # Input bounds
    bounds = [(u_min, u_max)] * N
    
    # Velocity constraints at each prediction step
    constraints = []
    for k in range(N):
        constraints.append({
            'type': 'ineq',
            'fun': velocity_constraint_lower,
            'args': (k,)
        })
        constraints.append({
            'type': 'ineq',
            'fun': velocity_constraint_upper,
            'args': (k,)
        })
    
    # Initial guess (warm start with zeros)
    U0 = np.zeros(N * nu)
    
    # Solve
    result = minimize(cost_function, U0, method='SLSQP',
                      bounds=bounds, constraints=constraints,
                      options={'maxiter': 200, 'ftol': 1e-8})
    
    if not result.success:
        print(f"  Warning: MPC solver did not converge: {result.message}")
    
    U_opt = result.x.reshape(N, nu)
    return U_opt[0]  # Return only the first control action


# =============================================================================
# Simulation
# =============================================================================
T_sim = 8.0  # Total simulation time [s]
n_steps = int(T_sim / dt)

# Reference: step from 0 to 1 at t=0
x_ref = np.array([1.0, 0.0])  # Target: position=1, velocity=0

# Initial state
x = np.array([0.0, 0.0])

# Storage
x_hist = np.zeros((n_steps + 1, nx))
u_hist = np.zeros((n_steps, nu))
x_hist[0] = x

print("Running MPC simulation...")
print(f"  Horizon N={N}, Q=diag({np.diag(Q)}), R={R[0,0]}")
print(f"  Input constraint: [{u_min}, {u_max}]")
print(f"  Velocity constraint: [{v_min}, {v_max}]")

for k in range(n_steps):
    # Solve MPC
    u = mpc_solve(x, x_ref, N, A, B, Q, R, P)
    
    # Apply control and simulate
    x = A @ x + B @ u
    
    # Store
    u_hist[k] = u
    x_hist[k + 1] = x
    
    if k % 20 == 0:
        print(f"  t={k*dt:.1f}s: pos={x[0]:.3f}, vel={x[1]:.3f}, u={u[0]:.3f}")

t = np.arange(n_steps + 1) * dt


# =============================================================================
# Compare with Unconstrained LQR
# =============================================================================
# Solve discrete-time Riccati for comparison
from scipy.linalg import solve_discrete_are
P_lqr = solve_discrete_are(A, B, Q, R)
K_lqr = np.linalg.inv(R + B.T @ P_lqr @ B) @ B.T @ P_lqr @ A

x_lqr = np.array([0.0, 0.0])
x_lqr_hist = np.zeros((n_steps + 1, nx))
u_lqr_hist = np.zeros((n_steps, nu))
x_lqr_hist[0] = x_lqr

for k in range(n_steps):
    u_lqr = -K_lqr @ (x_lqr - x_ref)
    # LQR doesn't respect constraints — show violation
    x_lqr = A @ x_lqr + B @ u_lqr
    u_lqr_hist[k] = u_lqr
    x_lqr_hist[k + 1] = x_lqr


# =============================================================================
# Plot Results
# =============================================================================
fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
fig.suptitle('Model Predictive Control vs LQR — Double Integrator', fontsize=14)

# Position
axes[0].plot(t, x_hist[:, 0], 'b-', linewidth=2, label='MPC')
axes[0].plot(t, x_lqr_hist[:, 0], 'r--', linewidth=2, label='LQR (unconstrained)')
axes[0].axhline(y=x_ref[0], color='k', linestyle=':', alpha=0.5, label='Reference')
axes[0].set_ylabel('Position')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Velocity
axes[1].plot(t, x_hist[:, 1], 'b-', linewidth=2, label='MPC')
axes[1].plot(t, x_lqr_hist[:, 1], 'r--', linewidth=2, label='LQR')
axes[1].axhline(y=v_max, color='orange', linewidth=2, linestyle='--', label=f'Constraint (±{v_max})')
axes[1].axhline(y=v_min, color='orange', linewidth=2, linestyle='--')
axes[1].fill_between(t, v_min, v_max, alpha=0.1, color='green', label='Feasible region')
axes[1].set_ylabel('Velocity')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Control input
t_u = np.arange(n_steps) * dt
axes[2].step(t_u, u_hist[:, 0], 'b-', linewidth=2, where='post', label='MPC')
axes[2].step(t_u, u_lqr_hist[:, 0], 'r--', linewidth=2, where='post', label='LQR')
axes[2].axhline(y=u_max, color='orange', linewidth=2, linestyle='--', label=f'Constraint (±{u_max})')
axes[2].axhline(y=u_min, color='orange', linewidth=2, linestyle='--')
axes[2].fill_between(t_u, u_min, u_max, alpha=0.1, color='green')
axes[2].set_ylabel('Control Input u')
axes[2].set_xlabel('Time [s]')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('mpc-double-integrator.png', dpi=150, bbox_inches='tight')
plt.show()

# Summary
print("\nResults:")
print(f"  MPC settling time: ~{np.where(np.abs(x_hist[:, 0] - 1.0) < 0.05)[0][0] * dt:.1f}s")
lqr_settle = np.where(np.abs(x_lqr_hist[:, 0] - 1.0) < 0.05)[0]
if len(lqr_settle) > 0:
    print(f"  LQR settling time: ~{lqr_settle[0] * dt:.1f}s")
print(f"  MPC max velocity:  {np.max(np.abs(x_hist[:, 1])):.3f} (limit: {v_max})")
print(f"  LQR max velocity:  {np.max(np.abs(x_lqr_hist[:, 1])):.3f} (VIOLATES constraint!)")
print(f"  MPC max |u|:       {np.max(np.abs(u_hist)):.3f} (limit: {u_max})")
print(f"  LQR max |u|:       {np.max(np.abs(u_lqr_hist)):.3f} (VIOLATES constraint!)")
