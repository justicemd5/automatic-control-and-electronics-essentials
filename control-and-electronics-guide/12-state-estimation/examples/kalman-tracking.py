"""
Kalman Filter — 2D Position/Velocity Tracking
================================================

Purpose:
    Track a moving object in 1D using noisy position measurements.
    The Kalman filter estimates both position and velocity, even
    though only position is measured.

Model:
    State: x = [position, velocity]
    Dynamics: constant velocity model
        x[k+1] = [[1, Ts], [0, 1]] x[k] + process_noise
    Measurement: y[k] = [1, 0] x[k] + measurement_noise
"""

import numpy as np
import matplotlib.pyplot as plt


# =============================================================================
# Parameters
# =============================================================================
np.random.seed(123)

Ts = 0.1       # Sample period [s]
n_steps = 300
t = np.arange(n_steps) * Ts

# True trajectory: accelerating then decelerating
a_true = np.zeros(n_steps)
a_true[:100] = 1.0     # Accelerate
a_true[100:200] = 0.0  # Constant velocity
a_true[200:] = -1.5    # Decelerate

# Generate true position and velocity
v_true = np.cumsum(a_true * Ts)
x_true = np.cumsum(v_true * Ts)

# Noise parameters
sigma_process = 0.5      # Process noise std (accounts for acceleration)
sigma_meas = 2.0         # Measurement noise std (position sensor noise)

Q = np.array([[Ts**4/4, Ts**3/2],
              [Ts**3/2, Ts**2  ]]) * sigma_process**2  # Process noise

R = np.array([[sigma_meas**2]])  # Measurement noise

# Noisy measurements (position only)
y_meas = x_true + np.random.normal(0, sigma_meas, n_steps)


# =============================================================================
# State-Space Model
# =============================================================================
A = np.array([[1, Ts],
              [0, 1]])    # Constant velocity model

B = np.array([[Ts**2/2],
              [Ts]])       # Not used (no known input)

C = np.array([[1, 0]])    # Measure position only

n_states = 2


# =============================================================================
# Kalman Filter
# =============================================================================
x_hat = np.zeros((n_steps, n_states))   # State estimates
P = np.zeros((n_steps, n_states, n_states))  # Covariance
K_history = np.zeros((n_steps, n_states))     # Gain history

# Initialize
x_hat[0] = [0, 0]  # Start at origin, zero velocity
P[0] = np.eye(n_states) * 100  # Very uncertain initially

for k in range(1, n_steps):
    # === PREDICT ===
    x_pred = A @ x_hat[k-1]
    P_pred = A @ P[k-1] @ A.T + Q
    
    # === UPDATE ===
    innovation = y_meas[k] - C @ x_pred
    S = C @ P_pred @ C.T + R
    K = P_pred @ C.T @ np.linalg.inv(S)
    
    x_hat[k] = x_pred + (K @ innovation).flatten()
    P[k] = (np.eye(n_states) - K @ C) @ P_pred
    K_history[k] = K.flatten()


# =============================================================================
# Results
# =============================================================================
pos_hat = x_hat[:, 0]
vel_hat = x_hat[:, 1]

pos_rmse = np.sqrt(np.mean((pos_hat[20:] - x_true[20:])**2))
vel_rmse = np.sqrt(np.mean((vel_hat[20:] - v_true[20:])**2))
meas_rmse = np.sqrt(np.mean((y_meas[20:] - x_true[20:])**2))

print("Kalman Filter — 2D Position/Velocity Tracking")
print(f"  Position RMSE (measurement): {meas_rmse:.2f} m")
print(f"  Position RMSE (Kalman):      {pos_rmse:.2f} m")
print(f"  Velocity RMSE (Kalman):      {vel_rmse:.2f} m/s")
print(f"  (Velocity is not measured, only estimated!)")


# =============================================================================
# Plot Results
# =============================================================================
fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
fig.suptitle('Kalman Filter — 2D Tracking (Position + Velocity)', fontsize=14)

# Position
axes[0].plot(t, x_true, 'g-', linewidth=2, label='True position')
axes[0].plot(t, y_meas, 'r.', markersize=3, alpha=0.4, label='Measurements')
axes[0].plot(t, pos_hat, 'b-', linewidth=2, label='Kalman estimate')
pos_std = np.sqrt(P[:, 0, 0])
axes[0].fill_between(t, pos_hat - 2*pos_std, pos_hat + 2*pos_std,
                      alpha=0.15, color='blue', label='±2σ')
axes[0].set_ylabel('Position [m]')
axes[0].legend(loc='upper left', fontsize=9)
axes[0].grid(True, alpha=0.3)

# Velocity
axes[1].plot(t, v_true, 'g-', linewidth=2, label='True velocity')
axes[1].plot(t, vel_hat, 'b-', linewidth=2, label='Kalman estimate')
vel_std = np.sqrt(P[:, 1, 1])
axes[1].fill_between(t, vel_hat - 2*vel_std, vel_hat + 2*vel_std,
                      alpha=0.15, color='blue', label='±2σ')
axes[1].set_ylabel('Velocity [m/s]')
axes[1].legend(loc='upper left', fontsize=9)
axes[1].grid(True, alpha=0.3)
axes[1].annotate('Velocity is ESTIMATED\n(not measured!)',
                  xy=(15, 8), fontsize=11,
                  bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))

# Kalman gains
axes[2].plot(t, K_history[:, 0], 'b-', linewidth=1.5, label='K_position')
axes[2].plot(t, K_history[:, 1], 'r-', linewidth=1.5, label='K_velocity')
axes[2].set_ylabel('Kalman Gain')
axes[2].set_xlabel('Time [s]')
axes[2].legend(fontsize=9)
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('kalman-tracking.png', dpi=150, bbox_inches='tight')
plt.show()
