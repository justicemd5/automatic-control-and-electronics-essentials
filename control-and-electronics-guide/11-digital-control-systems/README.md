# 11 — Digital Control Systems

> *Most modern controllers are implemented digitally — a microcontroller samples the sensor, computes the control law, and outputs a command at discrete time intervals. Understanding discretization, Z-transforms, and digital implementation issues is essential for any practicing control engineer.*

---

## 11.1 Continuous vs. Discrete Control

```
  Continuous:  r(t) → C(s) → G(s) → y(t)
  
  Digital:     r[k] → C(z) → ZOH → G(s) → Sampler → y[k]
  
               ┌────────────────────────────────────┐
  r[k] ──►(+)─┤ Digital     DAC    Plant   ADC     ├──► y[k]
           −↑  │ Controller  + ZOH  G(s)   + Sample │
            │  └────────────────────────────────────┘
            └───────────────────────────────────────────┘
                                T_s (sample period)
```

### Sampling Requirements

| Guideline | Rule | Reasoning |
|---|---|---|
| Nyquist | $f_s > 2 f_{BW}$ | Minimum to avoid aliasing |
| Control practice | $f_s \geq 10 \times f_{BW}$ | Good performance margin |
| Fast response | $f_s \geq 20 \times f_{BW}$ | Near-continuous behavior |
| Motor control | $f_s = 5\text{–}20$ kHz | PWM frequency = sample rate |
| Process control | $f_s = 1\text{–}10$ Hz | Slow processes, 10× dynamics |

---

## 11.2 The Z-Transform

$$Z\{x[k]\} = X(z) = \sum_{k=0}^{\infty} x[k] z^{-k}$$

### Key Z-Transform Pairs

| $x[k]$ | $X(z)$ |
|---|---|
| $\delta[k]$ | $1$ |
| $u[k]$ (step) | $\frac{z}{z-1}$ |
| $a^k u[k]$ | $\frac{z}{z-a}$ |
| $k \cdot u[k]$ (ramp) | $\frac{z}{(z-1)^2}$ |
| $e^{-aT_s k}$ | $\frac{z}{z - e^{-aT_s}}$ |

### Z-Domain ↔ S-Domain Mapping

$$z = e^{sT_s}$$

| s-plane | z-plane |
|---|---|
| Left half ($\text{Re}(s) < 0$) | Inside unit circle ($|z| < 1$) |
| Imaginary axis ($\text{Re}(s) = 0$) | Unit circle ($|z| = 1$) |
| Right half ($\text{Re}(s) > 0$) | Outside unit circle ($|z| > 1$) |

---

## 11.3 Discretization Methods

### Zero-Order Hold (ZOH) — Exact

$$G(z) = (1 - z^{-1}) \mathcal{Z}\left\{\frac{G(s)}{s}\right\}$$

This is the **exact** discretization when using a DAC with ZOH.

### Tustin (Bilinear) Transformation

$$s = \frac{2}{T_s} \cdot \frac{z-1}{z+1}$$

Preserves frequency response characteristics (no aliasing).

### Forward Euler

$$s \approx \frac{z-1}{T_s}$$

Simple but can cause instability. Only use for very fast sampling.

### Backward Euler

$$s \approx \frac{z-1}{zT_s}$$

Always stable for stable continuous systems (good for stiff systems).

### Comparison

| Method | Stability Mapping | Frequency Warping | Complexity |
|---|---|---|---|
| ZOH (exact) | Exact | None | Medium |
| Tustin | Exact | Yes (correctable) | Low |
| Forward Euler | May destabilize | None | Lowest |
| Backward Euler | Always stable | None | Low |
| Matched pole-zero | Approximate | None | Medium |

See: [examples/discretization-comparison.py](examples/discretization-comparison.py)

---

## 11.4 Digital PID Implementation

### Position Form

$$u[k] = K_p e[k] + K_i T_s \sum_{j=0}^{k} e[j] + K_d \frac{e[k] - e[k-1]}{T_s}$$

### Velocity (Incremental) Form (preferred)

$$\Delta u[k] = u[k] - u[k-1]$$

$$\Delta u = K_p(e[k] - e[k-1]) + K_i T_s \cdot e[k] + K_d \frac{e[k] - 2e[k-1] + e[k-2]}{T_s}$$

$$u[k] = u[k-1] + \Delta u[k]$$

**Advantages of velocity form:**
- Bumpless transfer between manual/auto modes
- Anti-windup is simpler (just stop accumulating)
- No initialization issues

See: [examples/digital-pid.c](examples/digital-pid.c)

---

## 11.5 Computational Delay

A one-sample computation delay adds:

$$G_{delay}(z) = z^{-1}$$

This reduces phase margin by approximately:

$$\Delta \phi \approx \omega_c \cdot T_s \text{ radians} = \frac{\omega_c \cdot T_s \cdot 180}{\pi} \text{ degrees}$$

⚠️ **Pitfall**: At $f_s = 10 \times f_{BW}$, one sample delay reduces phase margin by ~18°. If your continuous design has PM = 45°, the digital implementation may only have PM = 27° — dangerously low!

**Mitigation**: Design the continuous controller with extra phase margin, or use a Smith predictor for the delay.

---

## 11.6 Anti-Aliasing Filter

An analog low-pass filter **before** the ADC prevents high-frequency signals from aliasing into the control band:

$$f_{cutoff} = \frac{f_s}{2} \text{ to } \frac{f_s}{4}$$

```
  Sensor → Anti-alias filter → ADC → Digital Controller → DAC → Plant
           (analog LPF)                                  (ZOH)
```

---

## Examples

| File | Description |
|---|---|
| [discretization-comparison.py](examples/discretization-comparison.py) | Compare ZOH, Tustin, Euler methods |
| [digital-pid.c](examples/digital-pid.c) | Production-quality digital PID in C |
| [sampling-effects.md](examples/sampling-effects.md) | Effect of sample rate on control performance |

---

**Previous → [10-modern-control-theory](../10-modern-control-theory/README.md)**  
**Next → [12-state-estimation](../12-state-estimation/README.md)**
