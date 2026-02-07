# Laplace Transform Reference Table

## Transform Definition

$$F(s) = \mathcal{L}\{f(t)\} = \int_0^{\infty} f(t) e^{-st} \, dt$$

$$f(t) = \mathcal{L}^{-1}\{F(s)\} = \frac{1}{2\pi j} \int_{\sigma - j\infty}^{\sigma + j\infty} F(s) e^{st} \, ds$$

---

## Common Transform Pairs

| # | $f(t)$, $t \geq 0$ | $F(s)$ | Notes |
|---|---|---|---|
| 1 | $\delta(t)$ (impulse) | $1$ | Unit impulse |
| 2 | $1$ (step) | $\dfrac{1}{s}$ | Unit step $u(t)$ |
| 3 | $t$ (ramp) | $\dfrac{1}{s^2}$ | |
| 4 | $t^n$ | $\dfrac{n!}{s^{n+1}}$ | $n = 0, 1, 2, \ldots$ |
| 5 | $e^{-at}$ | $\dfrac{1}{s+a}$ | Exponential decay |
| 6 | $t e^{-at}$ | $\dfrac{1}{(s+a)^2}$ | |
| 7 | $t^n e^{-at}$ | $\dfrac{n!}{(s+a)^{n+1}}$ | |
| 8 | $\sin(\omega t)$ | $\dfrac{\omega}{s^2 + \omega^2}$ | |
| 9 | $\cos(\omega t)$ | $\dfrac{s}{s^2 + \omega^2}$ | |
| 10 | $e^{-at} \sin(\omega t)$ | $\dfrac{\omega}{(s+a)^2 + \omega^2}$ | Damped sine |
| 11 | $e^{-at} \cos(\omega t)$ | $\dfrac{s+a}{(s+a)^2 + \omega^2}$ | Damped cosine |
| 12 | $1 - e^{-at}$ | $\dfrac{a}{s(s+a)}$ | Step response of 1st order |
| 13 | $\dfrac{1}{b-a}(e^{-at} - e^{-bt})$ | $\dfrac{1}{(s+a)(s+b)}$ | $a \neq b$ |

---

## Properties

| Property | $f(t)$ | $F(s)$ |
|---|---|---|
| **Linearity** | $af_1(t) + bf_2(t)$ | $aF_1(s) + bF_2(s)$ |
| **Time derivative** | $\dot{f}(t)$ | $sF(s) - f(0^-)$ |
| **2nd derivative** | $\ddot{f}(t)$ | $s^2 F(s) - sf(0^-) - \dot{f}(0^-)$ |
| **n-th derivative** | $f^{(n)}(t)$ | $s^n F(s) - \sum_{k=0}^{n-1} s^{n-1-k} f^{(k)}(0^-)$ |
| **Integration** | $\int_0^t f(\tau) d\tau$ | $\dfrac{F(s)}{s}$ |
| **Time delay** | $f(t - T)u(t-T)$ | $e^{-Ts} F(s)$ |
| **Time scaling** | $f(at)$ | $\dfrac{1}{a} F\!\left(\dfrac{s}{a}\right)$ |
| **s-shift** | $e^{-at} f(t)$ | $F(s+a)$ |
| **Multiplication by t** | $t f(t)$ | $-\dfrac{dF(s)}{ds}$ |
| **Convolution** | $(f_1 * f_2)(t)$ | $F_1(s) \cdot F_2(s)$ |
| **Initial value** | $f(0^+)$ | $\lim_{s \to \infty} sF(s)$ |
| **Final value** | $\lim_{t \to \infty} f(t)$ | $\lim_{s \to 0} sF(s)$ ★ |

★ **Final Value Theorem** only valid if all poles of $sF(s)$ have negative real parts (system is stable).

---

## Standard Transfer Functions

### First-Order System

$$G(s) = \frac{K}{\tau s + 1}$$

- DC gain: $K$
- Time constant: $\tau$
- Step response: $y(t) = K(1 - e^{-t/\tau})$
- Bandwidth: $\omega_{BW} = 1/\tau$

### Second-Order System

$$G(s) = \frac{\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}$$

| Parameter | Symbol | Effect |
|---|---|---|
| Natural frequency | $\omega_n$ | Speed of response |
| Damping ratio | $\zeta$ | Oscillation amount |

| $\zeta$ | Response | Poles |
|---|---|---|
| $0 < \zeta < 1$ | Underdamped (oscillatory) | Complex conjugate |
| $\zeta = 1$ | Critically damped | Real, repeated |
| $\zeta > 1$ | Overdamped | Real, distinct |

Key formulas:
- Peak time: $t_p = \dfrac{\pi}{\omega_n\sqrt{1-\zeta^2}}$
- Overshoot: $M_p = e^{-\pi\zeta/\sqrt{1-\zeta^2}} \times 100\%$
- Settling time (2%): $t_s \approx \dfrac{4}{\zeta\omega_n}$

### PID Controller

$$C(s) = K_p + \frac{K_i}{s} + K_d s = K_p\left(1 + \frac{1}{T_i s} + T_d s\right)$$

---

## Partial Fraction Expansion (Quick Reference)

### Distinct Real Poles

$$\frac{N(s)}{(s+a)(s+b)} = \frac{A}{s+a} + \frac{B}{s+b}$$

$A = \left.\frac{N(s)}{s+b}\right|_{s=-a}, \quad B = \left.\frac{N(s)}{s+a}\right|_{s=-b}$

### Repeated Poles

$$\frac{N(s)}{(s+a)^2} = \frac{A}{(s+a)^2} + \frac{B}{s+a}$$

### Complex Poles

$$\frac{\omega}{(s+\sigma)^2 + \omega^2} \quad \longleftrightarrow \quad e^{-\sigma t}\sin(\omega t)$$

Keep complex poles as a pair — don't split into partial fractions with complex coefficients.

---

**← Back to [Appendix](README.md)**
