"""
Kalman Filter — 1D Temperature Estimation
===========================================

Purpose:
    Implement a simple 1D Kalman filter to estimate the true temperature
    of a room from noisy sensor readings. Demonstrates the core Kalman
    algorithm and shows how the filter adapts to noise levels.

Model:
    State: x = temperature [°C]
    Model: x[k+1] = x[k] + w[k]  (temperature is roughly constant)
    Measurement: y[k] = x[k] + v[k]  (noisy thermometer)
    
    Q = 0.01  (small process noise: temperature changes slowly)
    R = 4.0   (measurement noise variance: ±2°C sensor noise)

Expected: Kalman estimate is much smoother than raw measurements
    and converges to the true value.
"""

import numpy as np
import matplotlib.pyplot as plt


# =============================================================================
# Parameters
# =============================================================================
np.random.seed(42)

# True temperature (slowly varying)
n_steps = 200
t = np.arange(n_steps)
T_true = 22.0 + 0.5 * np.sin(2 * np.pi * t / 100)  # Slow sinusoidal drift

# Noise parameters
Q = 0.01     # Process noise covariance (how much temp changes per step)
R = 4.0      # Measurement noise covariance (sensor noise variance)

# Generate noisy measurements
w = np.random.normal(0, np.sqrt(Q), n_steps)  # Process noise
v = np.random.normal(0, np.sqrt(R), n_steps)  # Measurement noise
y_meas = T_true + v  # Noisy measurements


# =============================================================================
# Kalman Filter Implementation
# =============================================================================
# State-space: x[k+1] = A*x[k] + w,  y[k] = C*x[k] + v
A = 1.0  # State transition (constant temperature model)
C = 1.0  # Measurement matrix (direct observation)

# Initialize
x_hat = np.zeros(n_steps)      # Estimated state
P = np.zeros(n_steps)          # Error covariance
K = np.zeros(n_steps)          # Kalman gain
innovation = np.zeros(n_steps) # Measurement residual

x_hat[0] = 20.0  # Initial guess (deliberately wrong!)
P[0] = 10.0       # Large initial uncertainty

print("Kalman Filter — 1D Temperature Estimation")
print(f"  True temperature: ~{np.mean(T_true):.1f}°C (with slow drift)")
print(f"  Process noise Q = {Q} (model: temperature nearly constant)")
print(f"  Measurement noise R = {R} (sensor std dev = ±{np.sqrt(R):.1f}°C)")
print(f"  Initial estimate: x̂₀ = {x_hat[0]}°C, P₀ = {P[0]}")

for k in range(1, n_steps):
    # === PREDICT ===
    x_hat_minus = A * x_hat[k-1]          # Predicted state
    P_minus = A * P[k-1] * A + Q          # Predicted covariance
    
    # === UPDATE ===
    innovation[k] = y_meas[k] - C * x_hat_minus   # Measurement residual
    S = C * P_minus * C + R                         # Innovation covariance
    K[k] = P_minus * C / S                          # Kalman gain
    
    x_hat[k] = x_hat_minus + K[k] * innovation[k]  # Updated estimate
    P[k] = (1 - K[k] * C) * P_minus                # Updated covariance


# =============================================================================
# Compute Errors
# =============================================================================
error_meas = y_meas - T_true
error_kalman = x_hat - T_true

rmse_meas = np.sqrt(np.mean(error_meas**2))
rmse_kalman = np.sqrt(np.mean(error_kalman[10:]**2))  # Skip transient

print(f"\nResults:")
print(f"  Measurement RMSE: {rmse_meas:.2f}°C")
print(f"  Kalman RMSE:      {rmse_kalman:.2f}°C")
print(f"  Improvement:      {(1 - rmse_kalman/rmse_meas)*100:.0f}%")
print(f"  Steady-state Kalman gain: K = {K[-1]:.4f}")
print(f"  Steady-state error std:   σ = {np.sqrt(P[-1]):.4f}°C")


# =============================================================================
# Plot Results
# =============================================================================
fig, axes = plt.subplots(4, 1, figsize=(12, 12), sharex=True)
fig.suptitle('Kalman Filter — 1D Temperature Estimation', fontsize=14)

# Temperature estimates
axes[0].plot(t, T_true, 'g-', linewidth=2, label='True temperature')
axes[0].plot(t, y_meas, 'r.', markersize=3, alpha=0.5, label='Noisy measurements')
axes[0].plot(t, x_hat, 'b-', linewidth=2, label='Kalman estimate')
axes[0].fill_between(t, x_hat - 2*np.sqrt(P), x_hat + 2*np.sqrt(P),
                      alpha=0.2, color='blue', label='±2σ confidence')
axes[0].set_ylabel('Temperature [°C]')
axes[0].legend(loc='upper right', fontsize=9)
axes[0].grid(True, alpha=0.3)

# Estimation error
axes[1].plot(t, error_meas, 'r.', markersize=3, alpha=0.3, label='Measurement error')
axes[1].plot(t, error_kalman, 'b-', linewidth=1.5, label='Kalman error')
axes[1].axhline(y=0, color='k', linestyle=':', alpha=0.5)
axes[1].set_ylabel('Error [°C]')
axes[1].legend(fontsize=9)
axes[1].grid(True, alpha=0.3)

# Kalman gain evolution
axes[2].plot(t, K, 'b-', linewidth=2)
axes[2].set_ylabel('Kalman Gain K')
axes[2].grid(True, alpha=0.3)
axes[2].annotate(f'K_ss = {K[-1]:.4f}', xy=(n_steps*0.8, K[-1]),
                  fontsize=12, bbox=dict(boxstyle='round', facecolor='wheat'))

# Error covariance evolution
axes[3].plot(t, P, 'b-', linewidth=2)
axes[3].set_ylabel('Error Covariance P')
axes[3].set_xlabel('Time Step k')
axes[3].grid(True, alpha=0.3)
axes[3].annotate(f'P_ss = {P[-1]:.4f}', xy=(n_steps*0.8, P[-1]),
                  fontsize=12, bbox=dict(boxstyle='round', facecolor='wheat'))

plt.tight_layout()
plt.savefig('kalman-1d-temperature.png', dpi=150, bbox_inches='tight')
plt.show()
