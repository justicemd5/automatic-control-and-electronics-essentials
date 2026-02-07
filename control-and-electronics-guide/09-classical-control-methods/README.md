# 09 — Classical Control Methods

> *Classical control uses frequency-domain and root-locus techniques to design SISO controllers. These methods provide powerful graphical intuition for understanding system behavior and remain the most widely used design tools in industry.*

---

## 9.1 Frequency Response Analysis

### Bode Plot

A Bode plot shows magnitude and phase of $G(j\omega)$ versus frequency on logarithmic scales.

```
  Magnitude [dB]
    40 │──╲
    20 │    ──╲
     0 │────────╳──────── ω_c (gain crossover)
   -20 │          ──╲
   -40 │              ──╲──── −40 dB/dec
       └──────────────────────────────► ω [rad/s]
      0.1    1     10    100   1000
       
  Phase [°]
     0 │──────╲
   -45 │        ──╲
   -90 │────────────╲─────
  -135 │              ──╲
  -180 │──────────────────╳── ω_π (phase crossover)
       └──────────────────────────────► ω [rad/s]
```

### Bode Plot Rules (Asymptotic Approximation)

| Factor | Magnitude Slope | Phase Contribution |
|---|---|---|
| $K$ (constant) | 0 dB/dec, offset $20\log K$ | 0° |
| $s$ (zero at origin) | +20 dB/dec | +90° |
| $1/s$ (pole at origin) | −20 dB/dec | −90° |
| $(s/\omega_z + 1)$ | 0 below $\omega_z$, +20 above | 0° → +90° |
| $1/(s/\omega_p + 1)$ | 0 below $\omega_p$, −20 above | 0° → −90° |
| Complex pair (2nd order) | −40 dB/dec above $\omega_n$ | 0° → −180° |

---

## 9.2 Root Locus

The root locus plots the trajectories of closed-loop poles as a parameter (usually gain $K$) varies from 0 to ∞.

$$1 + K \cdot G(s)H(s) = 0 \implies G(s)H(s) = -\frac{1}{K}$$

### Root Locus Rules

| Rule | Description |
|---|---|
| 1. Branches | Number of branches = number of OL poles |
| 2. Start/End | Start at OL poles ($K=0$), end at OL zeros ($K→∞$) |
| 3. Real axis | Locus exists on real axis to the left of an odd number of real poles+zeros |
| 4. Symmetry | Symmetric about the real axis |
| 5. Asymptotes | $(n-m)$ branches go to infinity at angles $\frac{(2q+1)180°}{n-m}$ |
| 6. Centroid | Asymptotes intersect at $\sigma_a = \frac{\Sigma\text{poles} - \Sigma\text{zeros}}{n-m}$ |
| 7. Breakaway | Solve $dK/ds = 0$ on the real axis |
| 8. Imaginary crossing | Use Routh criterion with $K$ as parameter |

```
  Root Locus Example: G(s) = 1/[s(s+2)(s+4)]
  
  Im
  3 │         × ← jω crossing (K_max for stability)
  2 │       ╱   
  1 │     ╱     
  0 │←──◄──────◄──────◄── Real axis
 -1 │     ╲     ↑poles at 0, -2, -4
 -2 │       ╲   
 -3 │         ×
    └──────────────────────── Re
   -6  -4  -2   0
```

---

## 9.3 Nyquist Stability Criterion

The Nyquist plot maps $L(j\omega)$ in the complex plane as $\omega$ goes from $-\infty$ to $+\infty$.

**Nyquist Criterion:**

$$Z = N + P$$

Where:
- $Z$: number of closed-loop RHP poles (unstable) — must be 0 for stability
- $N$: number of clockwise encirclements of $(-1, 0)$
- $P$: number of open-loop RHP poles

**For stability: $N = -P$** (counter-clockwise encirclements must equal OL unstable poles).

For a stable open-loop system ($P = 0$): the Nyquist plot must **not encircle** $(-1, 0)$.

---

## 9.4 Lead, Lag, and Lead-Lag Compensators

### Lead Compensator (Phase Lead)

$$C_{lead}(s) = K_c \frac{s + z}{s + p} = K_c \frac{\tau s + 1}{\alpha \tau s + 1}, \quad \alpha < 1, \; p > z$$

**Effect**: Adds positive phase near $\omega_c$ → increases phase margin.

```
  Phase contribution:
  
  ∠C(jω)
  φ_max │          ╱╲
        │        ╱    ╲
        │      ╱        ╲
    0°  │────╱────────────╲────
        └──────────────────────► ω
             z    ω_max    p
             
  Maximum phase: φ_max = sin⁻¹((1-α)/(1+α))
  At frequency: ω_max = 1/(τ√α)
```

### Lag Compensator (Gain Reduction)

$$C_{lag}(s) = K_c \frac{s + z}{s + p} = K_c \frac{\tau s + 1}{\beta \tau s + 1}, \quad \beta > 1, \; z > p$$

**Effect**: Reduces gain at high frequencies without affecting phase near $\omega_c$.

### Comparison

| Compensator | PM Improvement | GM Improvement | Bandwidth | Noise |
|---|---|---|---|---|
| Lead | ✓ (direct) | ✓ | Increases | Worsens |
| Lag | ✓ (indirect) | ✓ | Decreases | Improves |
| Lead-Lag | ✓✓ | ✓✓ | Adjustable | Moderate |

---

## 9.5 Design Using Bode Plot

### Lead Compensator Design Procedure

1. Set open-loop DC gain $K$ for steady-state error spec
2. Draw Bode plot of $KG(s)$
3. Find current phase margin → determine needed phase boost $\phi_{boost}$
4. Add 5–12° safety factor: $\phi_{max} = \phi_{boost} + \phi_{safety}$
5. Compute $\alpha$: $\sin\phi_{max} = \frac{1-\alpha}{1+\alpha} \implies \alpha = \frac{1-\sin\phi_{max}}{1+\sin\phi_{max}}$
6. Place $\omega_{max}$ at desired new $\omega_c$: $\tau = \frac{1}{\omega_{max}\sqrt{\alpha}}$
7. Set compensator gain: $K_c = 1/\sqrt{\alpha}$ (to keep $\omega_c$ at $\omega_{max}$)
8. Verify margins on the compensated Bode plot

See: [examples/lead-compensator-design.py](examples/lead-compensator-design.py)

---

## 9.6 Nichols Chart

The Nichols chart plots $|L(j\omega)|$ dB vs. $\angle L(j\omega)$ degrees with contours of constant $|T(j\omega)|$ and $\angle T(j\omega)$.

**Advantages over Bode:**
- Gain and phase on one plot
- Closed-loop magnitude directly readable
- Distance from $(-180°, 0\text{dB})$ shows stability margins at a glance

---

## Examples

| File | Description |
|---|---|
| [lead-compensator-design.py](examples/lead-compensator-design.py) | Bode-based lead compensator design with plots |
| [root-locus-analysis.py](examples/root-locus-analysis.py) | Root locus plotting and gain selection |
| [nyquist-stability.md](examples/nyquist-stability.md) | Nyquist criterion worked example |

---

**Previous → [08-feedback-control-theory](../08-feedback-control-theory/README.md)**  
**Next → [10-modern-control-theory](../10-modern-control-theory/README.md)**
