# Z-Transform Reference Table

## Transform Definition

$$F(z) = \mathcal{Z}\{f[k]\} = \sum_{k=0}^{\infty} f[k] z^{-k}$$

$$f[k] = \frac{1}{2\pi j} \oint F(z) z^{k-1} dz$$

---

## Common Transform Pairs

| # | $f[k]$, $k \geq 0$ | $F(z)$ | Notes |
|---|---|---|---|
| 1 | $\delta[k]$ (impulse) | $1$ | |
| 2 | $1$ (step) | $\dfrac{z}{z-1}$ | |
| 3 | $k$ (ramp) | $\dfrac{z}{(z-1)^2}$ | |
| 4 | $k^2$ | $\dfrac{z(z+1)}{(z-1)^3}$ | |
| 5 | $a^k$ | $\dfrac{z}{z-a}$ | Geometric sequence |
| 6 | $k a^k$ | $\dfrac{az}{(z-a)^2}$ | |
| 7 | $\sin(\omega k T)$ | $\dfrac{z \sin(\omega T)}{z^2 - 2z\cos(\omega T) + 1}$ | |
| 8 | $\cos(\omega k T)$ | $\dfrac{z(z - \cos(\omega T))}{z^2 - 2z\cos(\omega T) + 1}$ | |
| 9 | $a^k \sin(\omega k T)$ | $\dfrac{az \sin(\omega T)}{z^2 - 2az\cos(\omega T) + a^2}$ | |
| 10 | $a^k \cos(\omega k T)$ | $\dfrac{z(z - a\cos(\omega T))}{z^2 - 2az\cos(\omega T) + a^2}$ | |
| 11 | $1 - a^k$ | $\dfrac{(1-a)z}{(z-1)(z-a)}$ | Step response |

---

## Properties

| Property | $f[k]$ | $F(z)$ |
|---|---|---|
| **Linearity** | $af_1[k] + bf_2[k]$ | $aF_1(z) + bF_2(z)$ |
| **Time shift (delay)** | $f[k-n]$ | $z^{-n} F(z)$ |
| **Time advance** | $f[k+1]$ | $zF(z) - zf[0]$ |
| **Scaling** | $a^k f[k]$ | $F(z/a)$ |
| **Time reversal** | $f[-k]$ | $F(z^{-1})$ |
| **Multiplication by k** | $k f[k]$ | $-z \dfrac{dF(z)}{dz}$ |
| **Convolution** | $(f_1 * f_2)[k]$ | $F_1(z) \cdot F_2(z)$ |
| **Accumulation** | $\sum_{m=0}^{k} f[m]$ | $\dfrac{z}{z-1} F(z)$ |
| **Initial value** | $f[0]$ | $\lim_{z \to \infty} F(z)$ |
| **Final value** | $\lim_{k \to \infty} f[k]$ | $\lim_{z \to 1} (z-1)F(z)$ ★ |

★ **Final Value Theorem**: Only valid if all poles of $(z-1)F(z)$ are inside the unit circle.

---

## Discretization Methods

Converting $G(s)$ to $G(z)$ with sample time $T$:

### Forward Euler

$$s = \frac{z - 1}{T}$$

- Simple but can be unstable
- Maps left half-plane outside unit circle for large $T$

### Backward Euler

$$s = \frac{z - 1}{Tz}$$

- Always stable if continuous system is stable
- Adds damping (conservative)

### Bilinear (Tustin)

$$s = \frac{2}{T} \cdot \frac{z - 1}{z + 1}$$

- Best frequency response match
- Warps frequencies: $\omega_{digital} = \frac{2}{T}\tan\left(\frac{\omega_{analog} T}{2}\right)$
- Pre-warp critical frequency for exact match

### Zero-Order Hold (ZOH)

$$G(z) = (1 - z^{-1}) \mathcal{Z}\left\{\frac{G(s)}{s}\right\}$$

- Most physically accurate (models the DAC)
- Preferred for simulation and implementation

### Comparison

```
  Mapping of s-plane to z-plane:
  
  s-plane (continuous)          z-plane (discrete)
  
  jω                            Unit circle
  ▲                             ┌───────┐
  │ ×  ×                        │ ×  ×  │ ← Poles mapped
  │        ← Stable region      │       │    inside circle
  │ ×  ×     (left half)        │ ×  ×  │    = stable
  ├──────────► σ                └───┼───┘
  │                                 │
                                    ▼
  Continuous poles at              Discrete poles at
  s = -σ ± jω                     z = e^{sT}
```

---

## Stability Regions

| Method | Stable s-plane → z-plane mapping |
|---|---|
| Forward Euler | Circle centered at (1,0), radius 1/T — may exclude stable poles |
| Backward Euler | Entire interior of unit circle — always maps stable to stable |
| Tustin | Exact mapping of left half-plane to unit circle interior |
| ZOH | Exact: $z = e^{sT}$ |

**Rule of thumb**: For control systems, use Tustin with prewarping or ZOH. Avoid forward Euler except for very fast sampling ($\omega_{BW} \cdot T \ll 1$).

---

## Digital Controller Forms

### Direct Form (from transfer function)

$$C(z) = \frac{b_0 + b_1 z^{-1} + b_2 z^{-2}}{1 + a_1 z^{-1} + a_2 z^{-2}}$$

Difference equation:
$$u[k] = b_0 e[k] + b_1 e[k-1] + b_2 e[k-2] - a_1 u[k-1] - a_2 u[k-2]$$

### Digital PID (Velocity Form)

$$\Delta u[k] = K_p (e[k] - e[k-1]) + K_i T e[k] + \frac{K_d}{T}(e[k] - 2e[k-1] + e[k-2])$$

Advantages: No integral windup, bumpless transfer.

---

**← Back to [Appendix](README.md)**
