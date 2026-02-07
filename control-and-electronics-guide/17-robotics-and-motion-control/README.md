# 17 — Robotics and Motion Control

> *Robotics combines control theory, electronics, and mechanical engineering into systems that interact with the physical world. This section covers kinematics, dynamics, trajectory planning, and the control architectures that make robots move precisely.*

---

## 17.1 Robot Classification

| Type | DOF | Application | Control Challenge |
|---|---|---|---|
| **Cartesian** | 3 (XYZ) | CNC machines, 3D printers | Simple kinematics |
| **SCARA** | 4 | Pick-and-place, assembly | Fast planar motion |
| **6-axis articulated** | 6 | Welding, painting, general | Complex kinematics |
| **Delta/parallel** | 3-6 | High-speed packaging | Coupled dynamics |
| **Collaborative** | 6-7 | Human interaction | Force control, safety |
| **Mobile** | 2-3 | AGV, warehouse robots | Navigation, SLAM |

---

## 17.2 Forward and Inverse Kinematics

### Forward Kinematics (FK)

Given joint angles $q = [\theta_1, \theta_2, \ldots, \theta_n]^T$, find end-effector pose:

$$T_{0n} = T_{01}(\theta_1) \cdot T_{12}(\theta_2) \cdots T_{(n-1)n}(\theta_n)$$

Using Denavit-Hartenberg (DH) parameters:

$$T_{i-1,i} = \begin{bmatrix}
c\theta_i & -s\theta_i c\alpha_i & s\theta_i s\alpha_i & a_i c\theta_i \\
s\theta_i & c\theta_i c\alpha_i & -c\theta_i s\alpha_i & a_i s\theta_i \\
0 & s\alpha_i & c\alpha_i & d_i \\
0 & 0 & 0 & 1
\end{bmatrix}$$

### Inverse Kinematics (IK)

Given desired end-effector pose, find joint angles. Generally:
- **Analytical** (closed-form): Possible for specific geometries (e.g., 6R with spherical wrist)
- **Numerical** (iterative): General but slower, may not converge

Numerical IK via Jacobian:

$$\Delta q = J^{-1}(q) \cdot \Delta x \quad \text{or} \quad \Delta q = J^{\dagger}(q) \cdot \Delta x$$

Where $J^\dagger$ is the pseudo-inverse (for redundant robots).

See: [examples/2dof-kinematics.py](examples/2dof-kinematics.py)

---

## 17.3 Jacobian Matrix

The Jacobian relates joint velocities to end-effector velocities:

$$\dot{x} = J(q) \cdot \dot{q}$$

$$J = \begin{bmatrix} \frac{\partial x}{\partial q_1} & \cdots & \frac{\partial x}{\partial q_n} \end{bmatrix}$$

### Singularities

When $\det(J) = 0$ (or $J$ loses rank), the robot loses one or more DOF:

```
  Workspace boundary                Elbow singularity
  (arm fully extended):             (links aligned):
  
       ┌─────●                         ┌──────────●
       │   ╱   ← Can't move           │
       │ ╱       further out           │ ← Infinite joint velocity
       ●                               ●    needed for Cartesian motion
```

⚠️ **Pitfall**: Near singularities, $J^{-1}$ has very large entries, causing enormous joint velocities for small Cartesian commands. Always implement singularity detection and limit joint velocities.

---

## 17.4 Robot Dynamics

### Euler-Lagrange Formulation

$$M(q)\ddot{q} + C(q, \dot{q})\dot{q} + g(q) = \tau$$

Where:
- $M(q)$: Inertia matrix (symmetric, positive definite)
- $C(q, \dot{q})$: Coriolis and centrifugal matrix
- $g(q)$: Gravity vector
- $\tau$: Joint torques (control input)

### Properties

- $M(q) > 0$ always (system is always controllable in joint space)
- $\dot{M} - 2C$ is skew-symmetric (important for control proofs)
- Gravity $g(q)$ can be computed from potential energy

---

## 17.5 Motion Control Architectures

### Joint Space Control

```
  q_d ──►(Σ)──► [Joint PID] ──► τ ──► [Robot] ──► q
           ↑                                        │
           └────────────────────────────────────────┘
```

Simple but doesn't account for nonlinear dynamics. Works for slow motions.

### Computed Torque Control

$$\tau = M(q)\left(\ddot{q}_d + K_d(\dot{q}_d - \dot{q}) + K_p(q_d - q)\right) + C(q, \dot{q})\dot{q} + g(q)$$

Cancels nonlinear dynamics → error dynamics become linear:

$$\ddot{e} + K_d \dot{e} + K_p e = 0$$

### Impedance Control

Instead of controlling position, control the dynamic relationship between force and position:

$$M_d \ddot{x}_e + B_d \dot{x}_e + K_d x_e = F_{ext}$$

Where $x_e = x - x_d$ (position error), and $M_d, B_d, K_d$ are desired impedance parameters.

```
  Free space:  Robot moves to target (stiff spring behavior)
  Contact:     Robot complies with external forces (soft spring)
  
  Force F
   │         ╱ Stiff (high Kd)
   │       ╱
   │     ╱
   │   ╱ ← Desired impedance
   │ ╱
   │╱─────── Compliant (low Kd)
   └───────────── Displacement x
```

---

## 17.6 Trajectory Planning

### Point-to-Point: Trapezoidal Velocity Profile

```
  Velocity
  v_max │    ┌─────────────┐
        │   ╱│             │╲
        │  ╱ │             │ ╲
        │ ╱  │             │  ╲
  ──────┘╱───┴─────────────┴───╲───── Time
        t1   t2            t3  t4
        
  t1→t2: Acceleration phase (constant accel)
  t2→t3: Cruise phase (constant velocity)
  t3→t4: Deceleration phase (constant decel)
```

### Multi-Point: Cubic Spline Interpolation

For smooth motion through waypoints $q_0, q_1, \ldots, q_n$:

$$q(t) = a_i + b_i(t - t_i) + c_i(t - t_i)^2 + d_i(t - t_i)^3$$

Constraints:
- Position continuity: $q_i(t_{i+1}) = q_{i+1}(t_{i+1})$
- Velocity continuity: $\dot{q}_i(t_{i+1}) = \dot{q}_{i+1}(t_{i+1})$
- Acceleration continuity: $\ddot{q}_i(t_{i+1}) = \ddot{q}_{i+1}(t_{i+1})$

See: [examples/trajectory-planning.py](examples/trajectory-planning.py)

---

## 17.7 Servo Drive Structure

The standard cascaded servo drive (see also Section 15):

```
  Trajectory ──► Position ──► Velocity ──► Current ──► Motor
  Generator       Loop          Loop          Loop
  (Planner)     (100 Hz)     (1 kHz)      (20 kHz)
  
                  ↑              ↑              ↑
               Encoder      Encoder/        Current
               (position)   Derivative      Sensor
                            (velocity)
```

Each loop has ~10× bandwidth of its outer loop, ensuring stability.

---

## Examples

| File | Description |
|---|---|
| [2dof-kinematics.py](examples/2dof-kinematics.py) | FK/IK for 2-link planar robot |
| [trajectory-planning.py](examples/trajectory-planning.py) | Trapezoidal and S-curve profiles |
| [pid-vs-computed-torque.md](examples/pid-vs-computed-torque.md) | Joint PID vs. computed torque comparison |

---

**Previous → [16-industrial-automation](../16-industrial-automation/README.md)**  
**Next → [18-communication-interfaces](../18-communication-interfaces/README.md)**
