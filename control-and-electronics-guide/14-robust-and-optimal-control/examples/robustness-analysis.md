# Example: Robustness Analysis Under Parametric Uncertainty

## Purpose
Analyze how a nominal controller performs when plant parameters deviate from their design values, and demonstrate stability margin evaluation.

---

## Nominal Plant

Second-order system representing a motor speed controller:

$$G_0(s) = \frac{K_0}{\tau_0 s + 1} \cdot \frac{1}{s} = \frac{5}{s(0.2s + 1)}$$

With PID controller (tuned at nominal):

$$C(s) = 2 + \frac{5}{s} + 0.1s = \frac{0.1s^2 + 2s + 5}{s}$$

---

## Parametric Uncertainty

| Parameter | Nominal | Range | Uncertainty |
|---|---|---|---|
| Gain $K$ | 5.0 | [3.5, 7.0] | ±30% |
| Time constant $\tau$ | 0.2 s | [0.15, 0.30] | −25% / +50% |

This defines a family of 4 corner plants:

| Case | $K$ | $\tau$ | $G(s)$ |
|---|---|---|---|
| Nominal | 5.0 | 0.20 | $\frac{5}{s(0.2s+1)}$ |
| Low-K, Fast | 3.5 | 0.15 | $\frac{3.5}{s(0.15s+1)}$ |
| Low-K, Slow | 3.5 | 0.30 | $\frac{3.5}{s(0.3s+1)}$ |
| High-K, Fast | 7.0 | 0.15 | $\frac{7}{s(0.15s+1)}$ |
| High-K, Slow | 7.0 | 0.30 | $\frac{7}{s(0.3s+1)}$ |

---

## Step 1: Nominal Stability Margins

Open-loop at nominal: $L_0(s) = C(s) G_0(s)$

$$L_0(s) = \frac{(0.1s^2 + 2s + 5) \cdot 5}{s^2(0.2s + 1)}$$

Bode analysis at nominal:

| Metric | Value |
|---|---|
| Gain crossover | $\omega_{gc} = 8.2$ rad/s |
| Phase margin | 48° |
| Gain margin | 12.5 dB |
| Delay margin | 0.10 s |

These margins suggest reasonable robustness. But are they sufficient for the parameter variations?

---

## Step 2: Worst-Case Analysis

### At Each Corner Plant

| Case | $\omega_{gc}$ [rad/s] | Phase Margin | Gain Margin | Stable? |
|---|---|---|---|---|
| Nominal | 8.2 | 48° | 12.5 dB | ✓ |
| Low-K, Fast | 6.5 | 55° | 15.1 dB | ✓ |
| Low-K, Slow | 6.1 | 38° | 10.2 dB | ✓ |
| High-K, Fast | 10.8 | 35° | 8.3 dB | ✓ |
| High-K, Slow | 9.5 | 22° | 5.8 dB | ⚠️ Marginal |

**Worst case**: High-K, Slow ($K=7$, $\tau=0.3$) with only 22° phase margin.

---

## Step 3: Sensitivity Analysis

### Bode Plot of Sensitivity Function $S(j\omega)$

```
  |S(jω)| [dB]
   6│            ╱╲ ← High-K, Slow (peak = 5.2 dB)
   3│          ╱╱  ╲╲
   0│── ── ──╱╱──────╲╲── ── ── ── ── 0 dB
  -3│      ╱╱         ╲╲ ← Nominal (peak = 2.8 dB)
  -6│    ╱╱             ╲
 -20│──╱╱                 ╲
 -40│╱╱                     (all converge to 0 dB at high freq)
    └────────────────────────── ω [rad/s]
    0.1   1    5  10   50  100
```

| Case | Peak $|S|$ | $M_s$ | Assessment |
|---|---|---|---|
| Nominal | 2.8 dB | 1.38 | Good |
| Low-K, Fast | 1.9 dB | 1.24 | Very good |
| Low-K, Slow | 4.1 dB | 1.60 | Acceptable |
| High-K, Fast | 3.8 dB | 1.55 | Acceptable |
| High-K, Slow | **5.2 dB** | **1.82** | ⚠️ Near limit ($M_s < 2$) |

💡 **Insight**: The peak sensitivity $M_s$ is a better robustness indicator than gain/phase margins alone. $M_s < 2$ (6 dB) is the standard robustness requirement. Our worst case ($M_s = 1.82$) meets this, but barely.

---

## Step 4: Step Response Comparison

```
  Output y(t)
  1.4│              ╱╲
  1.3│            ╱╱  ╲ ← High-K, Slow (30% overshoot)
  1.2│          ╱╱    ╲╲
  1.1│        ╱╱       ╲──── Nominal (15% overshoot)
  1.0│── ──╱╱────────────────── Setpoint
  0.8│   ╱╱
  0.6│  ╱╱   ← Low-K, Slow (slow response)
  0.4│ ╱╱
  0.2│╱╱
  0.0│
     └───────────────────────── Time [s]
     0   0.2  0.4  0.6  0.8  1.0
```

| Case | Rise Time | Overshoot | Settling (2%) |
|---|---|---|---|
| Nominal | 0.12 s | 15% | 0.45 s |
| Low-K, Fast | 0.15 s | 8% | 0.35 s |
| Low-K, Slow | 0.20 s | 10% | 0.55 s |
| High-K, Fast | 0.08 s | 25% | 0.50 s |
| High-K, Slow | 0.10 s | **30%** | **0.70 s** |

---

## Step 5: Design Improvement

The worst-case overshoot of 30% is unacceptable. Options:

### Option A: Detune the controller
Reduce $K_p$ from 2.0 to 1.5 → sacrifices nominal performance for robustness.

### Option B: Add a low-pass filter
$$C_{new}(s) = C(s) \cdot \frac{1}{0.01s + 1}$$

Rolls off high-frequency gain, improving phase margin at the cost of bandwidth.

### Option C: Use $H_\infty$ (Section 14.4)
Design with uncertainty explicitly modeled — guarantees $M_s < 2$ for all plants in the family.

---

## Key Takeaways

1. **Nominal margins are necessary but not sufficient** — always check corners of the uncertainty set
2. **Peak sensitivity $M_s$** captures robustness better than PM/GM alone
3. **High gain + slow plant** is typically the worst case (gain pushes crossover higher, slow plant adds more phase lag)
4. **The Bode sensitivity integral** (waterbed effect) means improving sensitivity at one frequency worsens it at another — there's no free lunch

⚠️ **Pitfall**: Testing only the four corners may miss the actual worst case if parameters interact nonlinearly with the loop gain. For critical applications, use structured singular value (μ-analysis) for a rigorous worst-case bound.
