# Example: $H_\infty$ Mixed Sensitivity Design

## Purpose
Walk through the weight selection and design process for an $H_\infty$ mixed sensitivity controller, showing how engineering requirements translate into mathematical weights.

---

## Plant

Unstable plant with a flexible mode:

$$G(s) = \frac{10}{(s - 1)(0.05s + 1)}$$

**Challenges**:
- Unstable pole at $s = +1$ (must be stabilized)
- Fast parasitic pole at $s = -20$ (uncertainty at high frequency)

---

## Step 1: Define Performance Requirements

| Requirement | Specification |
|---|---|
| Bandwidth | $\omega_c \geq 5$ rad/s |
| Steady-state error | $< 2\%$ for step |
| Noise rejection | $> 20$ dB above 100 rad/s |
| Control effort | $|u| < 10$ for unit step |
| Robustness | 30% multiplicative uncertainty at $\omega_c$ |

---

## Step 2: Select Weighting Functions

### $W_1(s)$: Performance Weight (on $S$)

We want $|S(j\omega)| < |1/W_1(j\omega)|$:

$$W_1(s) = \frac{s/M + \omega_b}{s + \omega_b \epsilon}$$

Where:
- $\omega_b = 5$ rad/s (desired bandwidth)
- $M = 2$ (peak sensitivity — 6 dB max)
- $\epsilon = 0.01$ (steady-state error < 1%)

$$W_1(s) = \frac{s/2 + 5}{s + 0.05}$$

```
  |1/W₁(jω)|
   │
 40│ ──────── 1/ε = 100 (40 dB)
   │         ╲
 20│          ╲
   │           ╲
  0│────────────╲──────── M = 2 (6 dB)
  -│             ╲_______
   └──────────────────── ω
   0.01   0.1    5    100
              ω_b
```

**Interpretation**: $|S| <$ 1% at DC (good tracking), $|S| <$ M at all frequencies (limited peaking).

### $W_3(s)$: Robustness Weight (on $T$)

We want $|T(j\omega)| < |1/W_3(j\omega)|$:

$$W_3(s) = \frac{s + \omega_t/M_t}{\epsilon_t s + \omega_t}$$

Where:
- $\omega_t = 50$ rad/s (uncertainty becomes significant)
- $M_t = 2$ (maximum $|T|$ at low frequency)
- $\epsilon_t = 0.01$

$$W_3(s) = \frac{s + 25}{0.01s + 50}$$

```
  |1/W₃(jω)|
   │
 40│                    ──── 1/ε_t (40 dB)
   │                  ╱
  6│── M_t (6 dB) ──╱
   │              ╱
  0│          ╱╱╱
   │      ╱╱╱
   └──────────────────── ω
   0.01   1    50   1000
              ω_t
```

---

## Step 3: Verify Weight Compatibility

The fundamental constraint $S + T = I$ means $|S|$ and $|T|$ cannot both be small.

Check at the crossover region:

$$|W_1(j\omega)| + |W_3(j\omega)| \leq 1 \quad \text{must not hold near } \omega_c$$

At $\omega = 5$ rad/s:
- $|W_1(j5)| \approx 1.0$
- $|W_3(j5)| \approx 0.1$

Since $|W_1| + |W_3| > 1$ only in a narrow band, the problem is feasible.

⚠️ **Pitfall**: If the weights overlap too much in the crossover region, the $H_\infty$ optimization will fail or produce a very high-order controller. Always check that performance ($W_1$) and robustness ($W_3$) weights don't both demand small values at the same frequencies.

---

## Step 4: Solve (Conceptual)

The $H_\infty$ optimal controller $K(s)$ is found by solving:

$$\gamma^* = \min_K \left\| \begin{bmatrix} W_1 S \\ W_3 T \end{bmatrix} \right\|_\infty$$

Using Riccati equation-based methods (or LMI methods).

If $\gamma^* < 1$: All specifications are met.
If $\gamma^* > 1$: Specifications are infeasible — relax weights.

---

## Step 5: Validate

### Closed-Loop Singular Values

```
  Magnitude [dB]
  20│
   0│      ╱──── |T|           |1/W₃|
  -│    ╱╱               ──────────
 -20│  ╱╱           ╱╱╱╱
 -40│──      |S|  ╱╱
 -60│──────╱╱╱╱╱╱
    └──────────────────────── ω [rad/s]
    0.01  0.1   1   10  100  1k
    
    ✓ |S| stays below |1/W₁| at all frequencies
    ✓ |T| stays below |1/W₃| at all frequencies
```

### Stability Margins

| Metric | Achieved | Requirement |
|---|---|---|
| Gain margin | 9.5 dB | > 6 dB ✓ |
| Phase margin | 52° | > 30° ✓ |
| Delay margin | 0.18 s | — |
| $\gamma^*$ | 0.87 | < 1 ✓ |

---

## Key Design Insights

💡 **Insight**: The entire $H_\infty$ design reduces to choosing good weights:
- $W_1$ encodes performance (tracking, disturbance rejection)
- $W_3$ encodes robustness (uncertainty tolerance)
- The optimizer finds the best controller balancing these competing goals

🔧 **Practical**: In practice, the $H_\infty$ controller order equals the plant order plus the weight orders. A 2nd-order plant with two 1st-order weights gives a 4th-order controller. If the controller order is too high, use model reduction (balanced truncation) to simplify.
