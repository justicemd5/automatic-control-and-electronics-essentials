# Example: Joint PID vs. Computed Torque Control

## Purpose
Compare simple joint-space PID with model-based computed torque control for a 2-link robot, showing when and why model-based control is necessary.

---

## The Robot

2-DOF planar manipulator (same as kinematics example):

$$M(q)\ddot{q} + C(q,\dot{q})\dot{q} + g(q) = \tau$$

Where for a 2-link robot:

$$M(q) = \begin{bmatrix} (m_1 + m_2)l_1^2 + m_2 l_2^2 + 2m_2 l_1 l_2 c_2 & m_2 l_2^2 + m_2 l_1 l_2 c_2 \\ m_2 l_2^2 + m_2 l_1 l_2 c_2 & m_2 l_2^2 \end{bmatrix}$$

Parameters: $m_1 = 3$ kg, $m_2 = 2$ kg, $l_1 = 1$ m, $l_2 = 0.8$ m

---

## Control Strategy 1: Joint PID

$$\tau = K_p(q_d - q) + K_d(\dot{q}_d - \dot{q}) + K_i \int(q_d - q) dt$$

Each joint has its own independent PID controller.

### Tuning

$$K_p = \text{diag}(100, 50), \quad K_d = \text{diag}(20, 10), \quad K_i = \text{diag}(10, 5)$$

### When Joint PID Works Well

```
  Error [rad]
  0.05│  ╱╲
      │ ╱  ╲─── Slow motion (0.5 rad/s)
  0.02│╱     ╲───────── → Error < 2°  ← ACCEPTABLE
      │        ────────
  0.00│─────────────────────── Time
```

### When Joint PID Fails

```
  Error [rad]
  0.15│  ╱╲    ╱╲
      │ ╱  ╲  ╱  ╲─── Fast motion (5 rad/s)
  0.10│╱    ╲╱    ╲
      │            ╲── Coupling oscillations
  0.05│             ╲╱╲
      │               ╲── → Error > 8°  ← UNACCEPTABLE
  0.00│─────────────────────── Time
```

**Why?** At high speeds, Coriolis and centrifugal terms become significant. Joint 1's motion creates forces on joint 2 (and vice versa). The independent PIDs interpret these coupling forces as disturbances and fight them inefficiently.

---

## Control Strategy 2: Computed Torque

$$\tau = M(q)\left(\ddot{q}_d + K_d(\dot{q}_d - \dot{q}) + K_p(q_d - q)\right) + C(q,\dot{q})\dot{q} + g(q)$$

This cancels all nonlinear dynamics, yielding linear error dynamics:

$$\ddot{e} + K_d \dot{e} + K_p e = 0$$

### Tuning

Choose $K_p$ and $K_d$ to place error dynamics poles:

For $\omega_n = 20$ rad/s, $\zeta = 0.8$:

$$K_p = \omega_n^2 = 400, \quad K_d = 2\zeta\omega_n = 32$$

(Same gains for both joints — the model compensation equalizes the dynamics)

---

## Performance Comparison

### Trajectory: Circle in Cartesian Space

Both joints follow sinusoidal trajectories (from IK) at moderate speed:

$$q_1(t) = 0.5 + 0.3\sin(2\pi t), \quad q_2(t) = -0.8 + 0.4\cos(2\pi t)$$

### Tracking Error

| Speed | Joint PID | Computed Torque | Improvement |
|---|---|---|---|
| Slow (0.5 Hz) | 1.2° peak | 0.1° peak | 12× |
| Medium (1 Hz) | 4.5° peak | 0.15° peak | 30× |
| Fast (3 Hz) | 12° peak | 0.3° peak | 40× |
| Very fast (5 Hz) | **Unstable!** | 0.5° peak | ∞ |

### Tracking at 1 Hz

```
  Joint 1 Error [deg]
  5│     ╱╲           ╱╲
   │   ╱╱  ╲╲       ╱╱  ╲╲     PID
  2│  ╱╱    ╲╲     ╱╱    ╲╲
   │ ╱╱      ╲╲   ╱╱      ╲╲
  0│╱╱────────╲╲─╱╱────────╲╲──
   │           ╲╱            ╲╱
 -3│
  
  0.3│                              Computed Torque
  0.1│ ╱╲     ╱╲     ╱╲
  0.0│╱──╲───╱──╲───╱──╲───────
 -0.1│    ╲ ╱    ╲ ╱    ╲ ╱
 -0.3│     ╲╱     ╲╱     ╲╱
     └──────────────────────── Time [s]
     0    0.5    1.0    1.5    2.0
```

### Torque Comparison

```
  Joint 1 Torque [N·m]
  
  PID:             Computed Torque:
  50│ ╱╲  ╱╲       50│  ╱╲   ╱╲
  25│╱  ╲╱  ╲      25│ ╱  ╲─╱  ╲
   0│        ╲       0│╱        ╲
 -25│         ╲╱╲  -25│         ╲╱╲
                     
  (Jerky, reactive) (Smooth, feedforward-dominated)
```

---

## Why Computed Torque Works

The key insight: most of the control effort is **feedforward** (compensating known dynamics), not **feedback** (reacting to errors).

```
  Total torque = Feedforward (model-based)  +  Feedback (error correction)
  
  Computed Torque:     τ = M(q)q̈_d + C(q,q̇)q̇ + g(q)  +  M(q)(Kd·ė + Kp·e)
                            └──── ~90% of torque ────┘     └── ~10% ──────┘
  
  Joint PID:           τ = Kp·e + Kd·ė + Ki·∫e dt
                            └──── 100% feedback (must be very large) ────┘
```

---

## Practical Considerations

### When to Use Joint PID

✅ Slow motions (< 10% of natural frequency)
✅ Light payloads relative to robot mass
✅ High gear ratios (gears decouple joints effectively)
✅ Simple systems where model is unavailable

### When to Use Computed Torque

✅ Fast, precise motions
✅ Direct-drive robots (no gears)
✅ Varying payloads
✅ Good dynamic model available

### Challenges with Computed Torque

⚠️ **Model accuracy**: Requires accurate $M(q)$, $C(q, \dot{q})$, $g(q)$.
  - Friction, cable routing, and flexibility are hard to model
  - Parameter identification is non-trivial

⚠️ **Computational cost**: Must compute full dynamics at control rate.
  - For a 6-DOF robot: hundreds of multiplications per cycle
  - Modern MCUs handle this, but it's not trivial

⚠️ **Sensor requirements**: Needs accurate velocity measurements.
  - Numerical differentiation of encoder adds noise
  - Observers or high-resolution encoders help

💡 **Insight**: In practice, industrial robots use a hybrid: PD control with gravity compensation (a simpler version of computed torque that only cancels gravity without requiring velocity-dependent terms):

$$\tau = K_p(q_d - q) + K_d(\dot{q}_d - \dot{q}) + g(q)$$

This captures 70-80% of the benefit with 20% of the complexity, because gravity is the largest single nonlinear term.
