# Example: Effect of Sample Rate on Control Performance

## Purpose
Demonstrate how the sampling period $T_s$ affects closed-loop stability and performance in a digital control system.

---

## System

**Continuous plant**: $G(s) = \frac{1}{s(s+1)}$ (motor speed control)

**Continuous PI controller**: $C(s) = 2 + \frac{4}{s}$ (designed for PM = 50°)

**Digital implementation**: Tustin discretization with various sample rates

---

## Continuous Design Performance

$$L(s) = C(s)G(s) = \frac{2s + 4}{s^2(s+1)}$$

- Crossover frequency: $\omega_c \approx 2$ rad/s
- Phase margin: $PM \approx 50°$
- Gain margin: $GM \approx 14$ dB

---

## Impact of Sample Rate

| $T_s$ [ms] | $f_s/f_{BW}$ ratio | PM (digital) | Overshoot | Stable? |
|---|---|---|---|---|
| 10 | 100× | 49° | 12% | ✓ (near-continuous) |
| 50 | 20× | 46° | 15% | ✓ (good) |
| 100 | 10× | 39° | 25% | ✓ (acceptable) |
| 200 | 5× | 28° | 42% | ✓ (aggressive) |
| 500 | 2× | 8° | 85% | Barely |
| 700 | 1.4× | — | — | ✗ Unstable! |

---

## Analysis: Why Does Sampling Degrade Performance?

### 1. Computational Delay
Each sample introduces a delay of up to $T_s$:

$$\text{Phase loss} \approx \omega_c \cdot T_s \text{ radians}$$

At $T_s = 200$ ms: $\Delta\phi = 2 \times 0.2 = 0.4$ rad $= 23°$

This alone reduces PM from 50° to 27°!

### 2. Zero-Order Hold
The ZOH introduces additional phase lag:

$$G_{ZOH}(j\omega) = \frac{1 - e^{-j\omega T_s}}{j\omega} \approx T_s \cdot e^{-j\omega T_s / 2}$$

The half-sample delay adds another $\omega_c T_s / 2$ radians.

### 3. Frequency Folding (Aliasing)
Noise above $f_s/2$ folds back into the control band, corrupting the measurement.

---

## Step Response Comparison

```
  y(t)
  
  1.4 │                      ╱╲   Ts = 200ms (oscillatory)
  1.2 │        ╱╲           ╱  ╲─ ─ ─ ─ ─
  1.0 │─ ─ ──╱──╲─────────╱
  0.8 │    ╱      ╲      ╱        Ts = 50ms (good)
  0.6 │   ╱        ╲───╱──────── Ts = 10ms (near-continuous)
  0.4 │  ╱
  0.2 │ ╱
  0.0 │╱
      └─────────────────────────── t [s]
      0    1    2    3    4    5
```

---

## Practical Guidelines

### Minimum Sample Rate Selection

$$f_s \geq \frac{20}{\pi} \cdot \omega_c \approx 6.4 \cdot f_{BW}$$

This limits phase loss to ~18° (acceptable for PM > 45° designs).

### Recommended Practice

| Application | Minimum $f_s/f_{BW}$ | Preferred | Reason |
|---|---|---|---|
| Position servo | 10× | 20× | Tight stability margins |
| Speed control | 10× | 15× | Moderate margins |
| Temperature | 5× | 10× | Slow dynamics, large margins |
| Power supply | 20× | 50× | Very fast transients |

### If You Can't Sample Fast Enough

1. **Reduce controller bandwidth**: Lower $\omega_c$ to restore margins
2. **Use predictor-corrector**: Smith predictor compensates for delay
3. **Multi-rate control**: Inner loop fast, outer loop slow
4. **Redesign in discrete domain**: Design $C(z)$ directly (no discretization errors)

⚠️ **Pitfall**: Never design a continuous controller and discretize it at a sample rate less than 10× the bandwidth. The discrete system will behave very differently from the continuous design.

💡 **Insight**: If you must use a slow sample rate, design the controller directly in the z-domain using root locus or frequency response methods for the discrete plant model $G(z)$. This accounts for the ZOH and delay exactly.
