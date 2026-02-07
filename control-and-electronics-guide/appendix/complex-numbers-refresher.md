# Complex Numbers Refresher

## Why Complex Numbers in Control and Electronics?

Complex numbers appear everywhere:
- **Phasors**: AC circuit analysis
- **Transfer functions**: Poles and zeros in the s-plane
- **Frequency response**: $G(j\omega)$ is a complex number at each frequency
- **Eigenvalues**: System stability (real part), oscillation frequency (imaginary part)
- **Fourier/Laplace transforms**: Decompose signals into complex exponentials

---

## Representations

### Rectangular Form

$$z = a + jb$$

- $a = \text{Re}(z)$ — real part
- $b = \text{Im}(z)$ — imaginary part
- $j = \sqrt{-1}$ (engineers use $j$; mathematicians use $i$)

### Polar Form

$$z = r \angle \theta = r(\cos\theta + j\sin\theta)$$

- $r = |z| = \sqrt{a^2 + b^2}$ — magnitude (modulus)
- $\theta = \arg(z) = \arctan(b/a)$ — angle (argument), in correct quadrant

### Euler's Form

$$z = r e^{j\theta}$$

This is the most powerful form. **Euler's formula**:

$$e^{j\theta} = \cos\theta + j\sin\theta$$

```
  Imaginary (j)
       ▲
       │    z = a + jb
    b ─┤    ╱ = r∠θ
       │   ╱
       │  ╱  r
       │ ╱
       │╱ θ
  ─────┼──────────► Real
       │    a
```

---

## Arithmetic

### Addition/Subtraction (use rectangular)

$$(a + jb) + (c + jd) = (a+c) + j(b+d)$$

### Multiplication (use polar)

$$r_1 e^{j\theta_1} \cdot r_2 e^{j\theta_2} = r_1 r_2 \, e^{j(\theta_1 + \theta_2)}$$

**Magnitudes multiply, angles add.**

### Division (use polar)

$$\frac{r_1 e^{j\theta_1}}{r_2 e^{j\theta_2}} = \frac{r_1}{r_2} e^{j(\theta_1 - \theta_2)}$$

**Magnitudes divide, angles subtract.**

### Complex Conjugate

$$\bar{z} = a - jb = r e^{-j\theta}$$

Useful property: $z \cdot \bar{z} = |z|^2 = a^2 + b^2$ (always real and positive)

### Rationalizing (dividing in rectangular form)

$$\frac{z_1}{z_2} = \frac{z_1 \cdot \bar{z_2}}{z_2 \cdot \bar{z_2}} = \frac{z_1 \cdot \bar{z_2}}{|z_2|^2}$$

---

## Key Identities

| Identity | Formula |
|---|---|
| Euler's formula | $e^{j\theta} = \cos\theta + j\sin\theta$ |
| Cosine from exponentials | $\cos\theta = \frac{e^{j\theta} + e^{-j\theta}}{2}$ |
| Sine from exponentials | $\sin\theta = \frac{e^{j\theta} - e^{-j\theta}}{2j}$ |
| Magnitude squared | $\|z\|^2 = z \cdot \bar{z}$ |
| De Moivre's theorem | $(e^{j\theta})^n = e^{jn\theta}$ |

---

## Application: Phasors (AC Circuits)

A sinusoidal voltage $v(t) = V_m \cos(\omega t + \phi)$ is represented as:

$$\mathbf{V} = V_m e^{j\phi} = V_m \angle \phi$$

### Impedances

| Element | Time Domain | Phasor Domain (Impedance $Z$) |
|---|---|---|
| Resistor | $v = Ri$ | $Z_R = R$ |
| Capacitor | $i = C \frac{dv}{dt}$ | $Z_C = \dfrac{1}{j\omega C}$ |
| Inductor | $v = L \frac{di}{dt}$ | $Z_L = j\omega L$ |

### Example: Series RLC

$$Z_{total} = R + j\omega L + \frac{1}{j\omega C} = R + j\left(\omega L - \frac{1}{\omega C}\right)$$

At resonance ($\omega_0 = 1/\sqrt{LC}$): $Z = R$ (purely resistive)

```
  Impedance in complex plane:
  
  jX (Reactance)
  ▲
  │     Z = R + jX
  │    ╱|
  │   ╱ |  X = ωL - 1/(ωC)
  │  ╱  |
  │ ╱ θ |
  ├╱────┤──────► R (Resistance)
  │     R
  │
  |Z| = √(R² + X²)
  θ = arctan(X/R)
```

---

## Application: Transfer Function Evaluation

To find the frequency response $G(j\omega)$, substitute $s = j\omega$:

### Example

$$G(s) = \frac{10}{s + 5}$$

At $\omega = 5$ rad/s:

$$G(j5) = \frac{10}{j5 + 5} = \frac{10}{5 + j5}$$

Rationalize:

$$= \frac{10(5 - j5)}{(5+j5)(5-j5)} = \frac{10(5-j5)}{25+25} = \frac{50 - j50}{50} = 1 - j1$$

Magnitude: $|G(j5)| = \sqrt{1^2 + 1^2} = \sqrt{2} \approx 1.414$

In dB: $20\log_{10}(\sqrt{2}) = 3.01$ dB

Phase: $\angle G(j5) = \arctan(-1/1) = -45°$

---

## Common Mistakes

⚠️ **arctan quadrant**: `atan(b/a)` gives wrong angle in Q2 and Q3. Always use `atan2(b, a)`.

⚠️ **j² = -1**: When multiplying $(a+jb)(c+jd)$, the $jb \cdot jd = j^2 bd = -bd$ term is real!

⚠️ **Degrees vs radians**: Most math libraries use radians. Control textbooks often use degrees for Bode plots. Be consistent.

⚠️ **Conjugate symmetry**: For real signals, poles and zeros always come in conjugate pairs: if $s = -2 + j3$ is a pole, then $s = -2 - j3$ must also be a pole.

---

**← Back to [Appendix](README.md)**
