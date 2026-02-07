# Example: Lyapunov Stability Analysis — Damped Pendulum

## Purpose
Apply Lyapunov's direct method to prove stability of the damped pendulum at the downward equilibrium, illustrating the energy-based approach.

---

## System: Damped Pendulum

$$ml^2 \ddot{\theta} + c\dot{\theta} + mgl\sin\theta = 0$$

State variables: $x_1 = \theta$ (angle), $x_2 = \dot{\theta}$ (angular velocity)

$$\dot{x}_1 = x_2$$
$$\dot{x}_2 = -\frac{g}{l}\sin x_1 - \frac{c}{ml^2}x_2$$

Equilibrium: $(x_1, x_2) = (0, 0)$ (pendulum hanging straight down)

---

## Step 1: Choose a Lyapunov Candidate

Use the total mechanical energy (shifted so $V = 0$ at equilibrium):

$$V(x_1, x_2) = \underbrace{\frac{1}{2}ml^2 x_2^2}_{\text{Kinetic energy}} + \underbrace{mgl(1 - \cos x_1)}_{\text{Potential energy (shifted)}}$$

### Check Condition 1: $V(0,0) = 0$

$$V(0, 0) = 0 + mgl(1 - 1) = 0 \quad ✓$$

### Check Condition 2: $V(x) > 0$ for $x \neq 0$

- $\frac{1}{2}ml^2 x_2^2 \geq 0$ (zero only when $x_2 = 0$)
- $mgl(1 - \cos x_1) \geq 0$ (zero only when $x_1 = 0 \mod 2\pi$)
- Both terms ≥ 0, and at least one > 0 when $(x_1, x_2) \neq (0, 0)$ in $|x_1| < \pi$

$$V > 0 \quad \forall (x_1, x_2) \neq (0,0), \; |x_1| < \pi \quad ✓$$

(Locally positive definite in the basin around $\theta = 0$)

---

## Step 2: Compute $\dot{V}$

$$\dot{V} = \frac{\partial V}{\partial x_1}\dot{x}_1 + \frac{\partial V}{\partial x_2}\dot{x}_2$$

$$\frac{\partial V}{\partial x_1} = mgl \sin x_1$$

$$\frac{\partial V}{\partial x_2} = ml^2 x_2$$

$$\dot{V} = mgl \sin x_1 \cdot x_2 + ml^2 x_2 \left(-\frac{g}{l}\sin x_1 - \frac{c}{ml^2}x_2\right)$$

$$= \cancel{mgl x_2 \sin x_1} - \cancel{mgl x_2 \sin x_1} - c x_2^2$$

$$\boxed{\dot{V} = -c x_2^2 \leq 0}$$

### Check Condition 3: $\dot{V} \leq 0$

Since $c > 0$ (positive damping):

$$\dot{V} = -c x_2^2 \leq 0 \quad ✓$$

---

## Step 3: Interpret the Result

$\dot{V} \leq 0$ proves **stability** (Lyapunov sense).

But $\dot{V} = 0$ when $x_2 = 0$ (not just at the origin!) — this is only negative *semi*-definite.

### Can we prove asymptotic stability?

**LaSalle's Invariance Principle**: If the largest invariant set where $\dot{V} = 0$ is only the origin, then the system is asymptotically stable.

$\dot{V} = 0 \implies x_2 = 0 \implies \dot{x}_2 = 0 \implies -\frac{g}{l}\sin x_1 = 0 \implies x_1 = 0$

The only invariant set where $\dot{V} = 0$ is $\{(0, 0)\}$.

$$\boxed{\text{The equilibrium } (0,0) \text{ is asymptotically stable.}}$$

---

## Physical Interpretation

| Mathematical | Physical |
|---|---|
| $V > 0$ | Energy is always positive (except at rest) |
| $\dot{V} = -cx_2^2 \leq 0$ | Damping always dissipates energy |
| $\dot{V} = 0$ only at $x_2 = 0$ | Energy dissipation stops only when velocity is zero |
| LaSalle: only at origin | Can't have $x_2 = 0$ permanently unless $x_1 = 0$ too |

The proof says: **energy monotonically decreases due to damping, and the system cannot get "stuck" at a non-equilibrium configuration with zero velocity**, because gravity would restart the motion.

---

## Comparison: Linear vs. Nonlinear Analysis

**Linearization** at $(0, 0)$: $\sin\theta \approx \theta$

$$A = \begin{bmatrix} 0 & 1 \\ -g/l & -c/ml^2 \end{bmatrix}$$

Eigenvalues determine local stability → valid only near equilibrium.

**Lyapunov analysis**: Valid for the entire region $|\theta| < \pi$ — much stronger result!

💡 **Insight**: Lyapunov's method proves stability without solving the differential equation. The challenge is finding a suitable $V(x)$ — for mechanical systems, energy is the natural choice. For general systems, finding $V(x)$ can be very difficult (there is no systematic method for nonlinear systems).
