# Example: Mass-Spring-Damper System — Complete Derivation

## Purpose

Derive the mathematical model of a mass-spring-damper system from first principles, obtain the transfer function and state-space representation, and analyze the system's natural frequency and damping characteristics.

---

## Physical System

```
                    k (spring)        b (damper)
  ┌──────┐        ╱╲╱╲╱╲╱╲        ┌──┤├──┐
  │      │────────╲╱╲╱╲╱╲╱────────│  ││  │
  │ WALL │                         │  m   │───► F(t)
  │      │────────────────────────│      │
  └──────┘                         └──┬───┘
                                      │
                                      ▼ x(t) (displacement)
```

**Parameters:**
- $m$: Mass [kg]
- $b$: Damping coefficient [N·s/m]
- $k$: Spring stiffness [N/m]
- $F(t)$: Applied external force [N]
- $x(t)$: Displacement from equilibrium [m]

---

## Step 1: Free-Body Diagram and Newton's Second Law

Forces acting on the mass:
- Applied force: $F(t)$ (positive direction)
- Spring force: $-kx(t)$ (restoring, opposes displacement)
- Damping force: $-b\dot{x}(t)$ (opposes velocity)

Newton's Second Law:

$$m\ddot{x}(t) = F(t) - kx(t) - b\dot{x}(t)$$

Rearranged to standard form:

$$m\ddot{x}(t) + b\dot{x}(t) + kx(t) = F(t)$$

This is a **second-order linear ODE with constant coefficients**.

---

## Step 2: Transfer Function (Laplace Domain)

Taking the Laplace transform with zero initial conditions:

$$m s^2 X(s) + b s X(s) + k X(s) = F(s)$$

$$(ms^2 + bs + k) X(s) = F(s)$$

$$G(s) = \frac{X(s)}{F(s)} = \frac{1}{ms^2 + bs + k}$$

### Standard Second-Order Form

Dividing numerator and denominator by $m$:

$$G(s) = \frac{1/m}{s^2 + \frac{b}{m}s + \frac{k}{m}} = \frac{\omega_n^2/k}{s^2 + 2\zeta\omega_n s + \omega_n^2}$$

Where:
- **Natural frequency**: $\omega_n = \sqrt{k/m}$ [rad/s]
- **Damping ratio**: $\zeta = \frac{b}{2\sqrt{km}}$ [dimensionless]

### Poles

$$s_{1,2} = -\zeta\omega_n \pm \omega_n\sqrt{\zeta^2 - 1}$$

| Damping Ratio $\zeta$ | Pole Type | Response Character |
|---|---|---|
| $\zeta = 0$ | Purely imaginary: $s = \pm j\omega_n$ | Undamped oscillation |
| $0 < \zeta < 1$ | Complex: $-\sigma \pm j\omega_d$ | Underdamped (oscillatory decay) |
| $\zeta = 1$ | Repeated real: $s = -\omega_n$ | Critically damped |
| $\zeta > 1$ | Distinct real: both negative | Overdamped (no oscillation) |

Where $\omega_d = \omega_n\sqrt{1-\zeta^2}$ is the damped natural frequency.

---

## Step 3: State-Space Representation

Choose state variables:
- $x_1 = x$ (position)
- $x_2 = \dot{x}$ (velocity)

Then:

$$\dot{x}_1 = x_2$$
$$\dot{x}_2 = \ddot{x} = \frac{1}{m}(F - bx_2 - kx_1)$$

**State-space matrices:**

$$\mathbf{A} = \begin{bmatrix} 0 & 1 \\ -k/m & -b/m \end{bmatrix}, \quad
\mathbf{B} = \begin{bmatrix} 0 \\ 1/m \end{bmatrix}$$

$$\mathbf{C} = \begin{bmatrix} 1 & 0 \end{bmatrix}, \quad
\mathbf{D} = \begin{bmatrix} 0 \end{bmatrix}$$

(Output is position $x_1 = x$.)

---

## Step 4: Numerical Example

**Parameters**: $m = 1$ kg, $b = 0.5$ N·s/m, $k = 4$ N/m

**Computed quantities:**
- $\omega_n = \sqrt{4/1} = 2$ rad/s
- $\zeta = \frac{0.5}{2\sqrt{4 \cdot 1}} = \frac{0.5}{4} = 0.125$ (underdamped)
- $\omega_d = 2\sqrt{1 - 0.125^2} \approx 1.984$ rad/s
- Poles: $s = -0.25 \pm j1.984$

**Transfer function:**

$$G(s) = \frac{1}{s^2 + 0.5s + 4}$$

**Step response characteristics** (for underdamped second-order system):
- Rise time: $t_r \approx \frac{1.8}{\omega_n} = 0.9$ sec
- Peak time: $t_p = \frac{\pi}{\omega_d} \approx 1.58$ sec
- Overshoot: $M_p = e^{-\pi\zeta/\sqrt{1-\zeta^2}} \approx e^{-0.397} \approx 67.2\%$
- Settling time (2%): $t_s \approx \frac{4}{\zeta\omega_n} = \frac{4}{0.25} = 16$ sec

⚠️ **Pitfall**: With $\zeta = 0.125$, this system has very light damping and will oscillate significantly. In practice, you'd either add physical damping or use a feedback controller.

---

## Step 5: Physical Interpretation

```
  Displacement x(t) for unit step force input (ζ = 0.125)
  
  0.5 │          ╱╲
      │         ╱  ╲        ╱╲
  0.3 │        ╱    ╲      ╱  ╲
  0.25│───────────────╲────╱────╲──────── steady state (F/k)
  0.2 │      ╱        ╲  ╱      ╲  ╱
      │     ╱          ╲╱        ╲╱
  0.0 │────╱
      └─────────────────────────────────── Time (sec)
      0    1    2    3    4    5    6
```

- The mass oscillates around the equilibrium $x_{ss} = F/k = 1/4 = 0.25$ m
- Oscillations decay with time constant $\tau = 1/(\zeta\omega_n) = 4$ sec
- The oscillation frequency is approximately $\omega_n$ (since $\zeta$ is small)

---

## Analogy to Electrical Domain

The mass-spring-damper is mathematically identical to a series RLC circuit:

| Mechanical | Electrical |
|---|---|
| Mass $m$ | Inductance $L$ |
| Damping $b$ | Resistance $R$ |
| Spring $k$ | $1/C$ (inverse capacitance) |
| Force $F$ | Voltage $V$ |
| Displacement $x$ | Charge $q$ |
| Velocity $\dot{x}$ | Current $i$ |

$$L\ddot{q} + R\dot{q} + \frac{1}{C}q = V(t)$$

This is exactly the same equation with different symbols.

---

## Expected Results Summary

| Quantity | Value |
|---|---|
| Natural frequency $\omega_n$ | 2 rad/s ≈ 0.318 Hz |
| Damping ratio $\zeta$ | 0.125 |
| Damped frequency $\omega_d$ | 1.984 rad/s |
| Steady-state displacement | $F/k = 0.25$ m (for unit force) |
| Overshoot | ~67% |
| Settling time (2%) | ~16 sec |
