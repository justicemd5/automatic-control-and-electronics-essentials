# 14 — Robust and Optimal Control

> *How do we design controllers that perform well despite model uncertainties (robust control) or that minimize a defined cost function (optimal control)? These two branches represent the pinnacle of linear control theory.*

---

## 14.1 The Need for Robustness

No model is perfect. Real plants have:

- **Parametric uncertainty**: Component tolerances (resistor ±5%)
- **Unmodeled dynamics**: Neglected high-frequency resonances
- **Nonlinearities**: Saturation, dead zones (see Section 13)
- **Time variations**: Aging, temperature changes
- **Disturbances**: External forces, measurement noise

A robust controller maintains stability and performance **despite** these uncertainties.

---

## 14.2 Uncertainty Modeling

### Unstructured Uncertainty

Frequency-domain bounds on the plant deviation:

$$G_{\text{true}}(j\omega) = G_0(j\omega)(1 + \Delta(j\omega) W(j\omega))$$

Where:
- $G_0(s)$: Nominal plant model
- $\Delta(s)$: Unknown but $\|\Delta\|_\infty \leq 1$
- $W(s)$: Weighting function bounding uncertainty magnitude

Typical uncertainty profile:

```
  |W(jω)|
   │
 1.0│                      ╱╱╱╱
   │                   ╱╱
 0.5│              ╱╱╱
   │          ╱╱╱
 0.1│─────────╱
   │  (low uncertainty     (high uncertainty
   │   at low freq)         at high freq)
   └──────────────────────────── ω
```

### Parametric Uncertainty

$$G(s) = \frac{K}{s + a}, \quad K \in [1.5, 2.5], \quad a \in [0.8, 1.2]$$

This defines a **family** of plants. The controller must stabilize all members.

---

## 14.3 Small Gain Theorem

The fundamental stability result for interconnected systems:

If the loop gain $\|T(s)\|_\infty \cdot \|\Delta\|_\infty < 1$, the feedback system is stable for all $\Delta$ with $\|\Delta\|_\infty \leq 1$.

$$\boxed{\|T\|_\infty < \frac{1}{\|\Delta\|_\infty}}$$

---

## 14.4 $H_\infty$ Control

Minimize the worst-case (infinity norm) of a weighted transfer function.

### Mixed Sensitivity Problem

$$\min_K \left\| \begin{bmatrix} W_1 S \\ W_2 KS \\ W_3 T \end{bmatrix} \right\|_\infty$$

Where:
- $S = (I + GK)^{-1}$: Sensitivity (error rejection)
- $T = GK(I + GK)^{-1}$: Complementary sensitivity (noise rejection)
- $KS = K(I + GK)^{-1}$: Control effort

```
  |W₁| = Performance weight
  ─────── Want |S| small here (good tracking)
  
  |W₃| = Robustness weight
  ─────── Want |T| small here (robust to uncertainty)
  
  Magnitude
   │
   │   ┌─── |W₁|          |W₃| ───┐
   │   │                           │
   │   │    ↑ Want |S| < 1/|W₁|   │ ↑ Want |T| < 1/|W₃|
   │   │                           │
   └───┴───────────────────────────┴───── ω
       Low freq          High freq
```

💡 **Insight**: The constraint $S + T = I$ means you cannot make both small simultaneously — this is the fundamental performance-robustness tradeoff.

See: [examples/hinf-mixed-sensitivity.md](examples/hinf-mixed-sensitivity.md)

---

## 14.5 Linear Quadratic Regulator (LQR)

The most important optimal control result: minimize a quadratic cost function for a linear system.

### Problem

Given: $\dot{x} = Ax + Bu$

Minimize:

$$J = \int_0^\infty \left( x^T Q x + u^T R u \right) dt$$

Where:
- $Q \geq 0$: State penalty (large → small deviations)
- $R > 0$: Control penalty (large → less control effort)

### Solution

The optimal feedback law is:

$$u^* = -Kx, \quad K = R^{-1}B^T P$$

Where $P$ is the solution to the Algebraic Riccati Equation (ARE):

$$\boxed{A^T P + PA - PBR^{-1}B^T P + Q = 0}$$

### Properties of LQR

- **Guaranteed stability** (if $(A, B)$ controllable and $Q = C^T C$ with $(A, C)$ observable)
- **Phase margin ≥ 60°** for each input channel (SISO)
- **Gain margin**: $[0.5, \infty)$ — infinite upward gain margin!
- Robustness degrades for MIMO systems (use LQG/LTR)

See: [examples/lqr-inverted-pendulum.py](examples/lqr-inverted-pendulum.py)

---

## 14.6 Linear Quadratic Gaussian (LQG)

Combines LQR with Kalman filter (from Section 12) for output feedback with noise:

```
                   ┌─────────────────────────┐
                   │       LQG Controller     │
  r ──►(Σ)──►     │  ┌────────┐  ┌────────┐  │ u    ┌───────┐  y
         │         │  │  LQR   │←─│ Kalman │◄─┼──────│ Plant │──┼──►
         │         │  │ u=-Kx̂  │  │ Filter │  │      │ + w,v │  │
         │         │  └────────┘  └────────┘  │      └───────┘  │
         │         └─────────────────────────┘                  │
         └──────────────────────────────────────────────────────┘
```

**Separation Principle**: Design LQR and Kalman filter independently — the combined system is optimal!

⚠️ **Pitfall**: LQG does NOT inherit the robustness guarantees of LQR. An LQG controller can have arbitrarily small stability margins. Use LQG/LTR (Loop Transfer Recovery) to recover LQR-like margins.

---

## 14.7 LQR Tuning Guidelines

| Goal | Adjust | Effect |
|---|---|---|
| Faster response | Increase $Q$ | More aggressive control |
| Less overshoot | Increase $R$ | Smoother, slower response |
| Penalize one state | Increase $Q_{ii}$ | That state regulated tighter |
| Limit actuator use | Increase $R$ | Reduced control magnitude |

### Bryson's Rule (starting point)

$$Q_{ii} = \frac{1}{x_{i,\max}^2}, \quad R_{jj} = \frac{1}{u_{j,\max}^2}$$

Where $x_{i,\max}$ and $u_{j,\max}$ are the maximum acceptable values.

---

## Examples

| File | Description |
|---|---|
| [hinf-mixed-sensitivity.md](examples/hinf-mixed-sensitivity.md) | $H_\infty$ weight selection and design |
| [lqr-inverted-pendulum.py](examples/lqr-inverted-pendulum.py) | LQR for cart-pendulum balancing |
| [robustness-analysis.md](examples/robustness-analysis.md) | Margin analysis under uncertainty |

---

**Previous → [13-nonlinear-and-adaptive-control](../13-nonlinear-and-adaptive-control/README.md)**  
**Next → [15-embedded-control-systems](../15-embedded-control-systems/README.md)**
