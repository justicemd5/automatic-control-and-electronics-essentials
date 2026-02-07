# Example: IMU + GPS Sensor Fusion Overview

## Purpose
Explain how Kalman filtering fuses inertial measurement unit (IMU) data with GPS to achieve accurate navigation.

---

## The Complementary Nature of IMU and GPS

| Property | IMU (Accelerometer + Gyroscope) | GPS |
|---|---|---|
| Update rate | 100–1000 Hz | 1–10 Hz |
| Short-term accuracy | Excellent | Moderate |
| Long-term accuracy | Drifts (integration error) | Excellent (no drift) |
| Noise | High-frequency | Low-frequency |
| Works indoors | Yes | No |
| Latency | ~1 ms | ~100 ms |

**Key insight**: IMU is accurate in the short term but drifts; GPS is accurate in the long term but noisy and slow. Kalman filtering combines the best of both.

---

## State Vector

For a typical navigation system:

$$x = \begin{bmatrix} p_x \\ p_y \\ p_z \\ v_x \\ v_y \\ v_z \\ \phi \\ \theta \\ \psi \\ b_{ax} \\ b_{ay} \\ b_{az} \\ b_{gx} \\ b_{gy} \\ b_{gz} \end{bmatrix} \quad \begin{matrix} \leftarrow \text{Position (3)} \\ \\ \\ \leftarrow \text{Velocity (3)} \\ \\ \\ \leftarrow \text{Attitude/Euler angles (3)} \\ \\ \\ \leftarrow \text{Accelerometer bias (3)} \\ \\ \\ \leftarrow \text{Gyroscope bias (3)} \\ \\ \end{matrix}$$

Total: 15 states (minimal navigation filter)

---

## Process Model (IMU-driven prediction)

$$\dot{p} = v$$
$$\dot{v} = R(\phi, \theta, \psi) \cdot (a_{meas} - b_a) + g$$
$$\dot{\Phi} = \omega_{meas} - b_g$$
$$\dot{b}_a = \text{noise (random walk)}$$
$$\dot{b}_g = \text{noise (random walk)}$$

Where $R$ is the rotation matrix from body to navigation frame.

**This is nonlinear** → Use Extended Kalman Filter (EKF) or Error-State Kalman Filter.

---

## Measurement Model (GPS updates)

When GPS provides a fix:

$$y_{GPS} = \begin{bmatrix} p_x \\ p_y \\ p_z \\ v_x \\ v_y \\ v_z \end{bmatrix} + v_{GPS}$$

$$C_{GPS} = \begin{bmatrix} I_{3\times3} & 0 & 0 & 0 & 0 \\ 0 & I_{3\times3} & 0 & 0 & 0 \end{bmatrix}$$

---

## Filter Timeline

```
  Time → ──────────────────────────────────────────────────
  
  IMU:    ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑
          │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
          P P P P P P P P P P P P P P P P P P P P P P  (Predict at 100Hz)
          
  GPS:                ↑                   ↑
                      │                   │
                      U                   U  (Update at 1Hz)
                      
  P = Predict (propagate state with IMU)
  U = Update (correct with GPS measurement)
  
  Between GPS updates: position estimate drifts slightly
  At GPS update: position snaps back to truth
```

---

## Typical Noise Parameters

| Parameter | Value | Unit |
|---|---|---|
| Accelerometer noise | 0.01 | m/s²/√Hz |
| Accelerometer bias stability | 0.1 | mg |
| Gyroscope noise | 0.01 | °/s/√Hz |
| Gyroscope bias stability | 10 | °/hr |
| GPS position accuracy | 2.5 | m (CEP) |
| GPS velocity accuracy | 0.1 | m/s |

---

## Error-State Kalman Filter (ESKF)

For navigation, the **error-state** formulation is preferred:

1. Propagate the **nominal state** using the nonlinear equations (no Jacobians needed)
2. The Kalman filter estimates the **error state** $\delta x = x_{true} - x_{nominal}$
3. The error state is approximately linear → standard Kalman filter works well
4. At each GPS update, correct the nominal state and reset the error state to zero

**Advantages:**
- Error state is small → linearization is accurate
- Error state stays near zero → numerical stability
- Quaternion handling is cleaner than with Euler angles

---

## Performance

| Configuration | Horizontal Accuracy |
|---|---|
| GPS only | ~2.5 m |
| IMU only (1 min) | ~100 m (drift) |
| IMU + GPS (Kalman) | ~0.5 m |
| IMU + GPS + Barometer | ~0.3 m (especially vertical) |
| IMU + RTK-GPS | ~0.02 m |

💡 **Insight**: The Kalman filter doesn't just average the sensors — it intelligently weights them based on their current uncertainty. During GPS outage, the filter relies on IMU prediction while the uncertainty grows. When GPS returns, the filter aggressively corrects the accumulated drift.

🔧 **Practical**: Most commercial drone flight controllers (PX4, ArduPilot) implement a 15-24 state EKF for navigation. The filter runs at 100-400 Hz and is the most computationally expensive task on the flight controller.
