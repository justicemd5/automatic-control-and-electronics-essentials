# Example: Sensitivity and Complementary Sensitivity Analysis

## Purpose
Analyze the sensitivity function $S(s)$ and complementary sensitivity $T(s)$ for a feedback system, illustrating the fundamental trade-offs in controller design.

---

## Setup

Plant: $G(s) = \frac{100}{s(s+10)}$ (motor with integrator)

Controller: $C(s) = K_p = 10$ (proportional)

Loop transfer function:

$$L(s) = C(s)G(s) = \frac{1000}{s(s+10)}$$

---

## Sensitivity Function

$$S(s) = \frac{1}{1 + L(s)} = \frac{s(s+10)}{s^2 + 10s + 1000}$$

### Properties of $S(s)$:

| Frequency | $|S(j\omega)|$ | Interpretation |
|---|---|---|
| $\omega \to 0$ | $\to 0$ | Good: disturbances rejected at DC |
| $\omega = \omega_c$ | $\approx 0.5$ (−6dB) | Near crossover |
| $\omega \to \infty$ | $\to 1$ (0dB) | No disturbance rejection at high freq |
| $\omega \approx \omega_n$ | Peak (> 1) | **Amplification!** |

---

## Complementary Sensitivity Function

$$T(s) = \frac{L(s)}{1 + L(s)} = \frac{1000}{s^2 + 10s + 1000}$$

### Properties of $T(s)$:

| Frequency | $|T(j\omega)|$ | Interpretation |
|---|---|---|
| $\omega \to 0$ | $\to 1$ (0dB) | Good: tracks reference perfectly |
| $\omega = \omega_n$ | Peak | Resonance → overshoot |
| $\omega \to \infty$ | $\to 0$ | Cannot track fast signals |

---

## The Fundamental Identity

$$\boxed{S(j\omega) + T(j\omega) = 1 \quad \forall \; \omega}$$

This means:

```
  Bode Magnitude:
  
  dB
  10 │
   0 │──T(jω)───╲         ╱──S(jω)──
 -10 │            ╲       ╱
 -20 │             ╲     ╱
 -30 │              ╲   ╱
 -40 │               ╲ ╱
     └───────────────────────────────► ω
                     ω_c
                     
  At any frequency: |S| ≈ 1 means |T| ≈ 0 and vice versa.
  You cannot make both small simultaneously!
```

---

## Sensitivity Peak and Robustness

The **maximum sensitivity** $M_S = \max_\omega |S(j\omega)|$ is a key robustness indicator:

$$M_S = \frac{1}{\text{distance from Nyquist plot to } (-1, 0)}$$

| $M_S$ | Gain Margin | Phase Margin | Quality |
|---|---|---|---|
| 1.0 | ∞ | 90° | Very conservative |
| 1.3 | 4.3 (12.6 dB) | 49° | Good |
| 1.5 | 3.0 (9.5 dB) | 39° | Acceptable |
| 2.0 | 2.0 (6.0 dB) | 29° | Aggressive |
| > 2.0 | < 6 dB | < 29° | Poor robustness |

### Recommended: $M_S \leq 2.0$ (industry standard)

For our system:

$$s^2 + 10s + 1000 = 0 \implies \omega_n = \sqrt{1000} = 31.6 \;\text{rad/s}, \quad \zeta = \frac{10}{2\omega_n} = 0.158$$

The low damping ratio means a high resonant peak:

$$M_S \approx \frac{1}{2\zeta\sqrt{1-\zeta^2}} \approx 3.2$$

⚠️ **Pitfall**: $M_S = 3.2 > 2.0$ means this system has poor robustness. A small plant perturbation could cause instability. We need to redesign the controller.

---

## Improved Design

Add a lead compensator or increase damping:

$$C(s) = 10 \cdot \frac{s + 10}{s + 50}$$

This adds phase lead near crossover, improving $\zeta$ and reducing $M_S$.

**Result**: $M_S \approx 1.4$, $PM \approx 52°$, $GM \approx 14$ dB ✓

---

## Bode Sensitivity Integral (Waterbed Effect)

For systems with at least 2 more poles than zeros:

$$\boxed{\int_0^\infty \ln|S(j\omega)|\, d\omega = 0}$$

This means: **if you push $|S|$ down at some frequencies, it must come up at others.**

```
  |S(jω)| dB
    10 │                    ╱╲  ← Amplification region
     0 │────────────────────╱──╲──── (unavoidable!)
   -10 │╲                 ╱     
   -20 │  ╲──────────────╱     ← Rejection region (design goal)
   -30 │    ╲           ╱
       └────────────────────────────► ω
           ω_low      ω_high
           
  Area below 0 dB = Area above 0 dB (waterbed effect)
```

💡 **Insight**: The waterbed effect is the fundamental limitation of feedback control. You cannot have broadband disturbance rejection — you must choose which frequency range matters most and accept amplification elsewhere.

---

## Design Guidelines

1. **$|S(j\omega)| < 1$ at low frequencies**: reject step disturbances
2. **$|T(j\omega)| < 1$ at high frequencies**: reject noise, ensure robustness to unmodeled dynamics
3. **Crossover region is the problem**: $S$ and $T$ are both near 1, neither is small
4. **$M_S \leq 2.0$**: ensures minimum robustness margins
5. **Roll-off of $T$**: at least 20 dB/decade above crossover for noise rejection
