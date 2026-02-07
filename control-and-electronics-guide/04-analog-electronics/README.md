# 04 — Analog Electronics

> *Analog electronics is the foundation of every measurement, actuation, and signal conditioning circuit. Before signals become digital, they are analog — and the quality of the analog front-end determines the quality of everything downstream.*

---

## 4.1 Circuit Fundamentals

### Ohm's Law and Kirchhoff's Laws

These are the bedrock of all circuit analysis:

$$V = IR \quad \text{(Ohm's Law)}$$

$$\sum V_{loop} = 0 \quad \text{(KVL — Kirchhoff's Voltage Law)}$$

$$\sum I_{node} = 0 \quad \text{(KCL — Kirchhoff's Current Law)}$$

### Power and Energy

$$P = VI = I^2R = \frac{V^2}{R}$$

💡 **Insight**: Power dissipation in resistors is always positive (energy is converted to heat). This is why efficiency matters — every resistor is a loss.

---

## 4.2 Passive Components

| Component | Symbol | Impedance $Z(j\omega)$ | V-I Relationship | Energy Storage |
|---|---|---|---|---|
| Resistor | R | $R$ | $V = IR$ | None (dissipates) |
| Capacitor | C | $\frac{1}{j\omega C}$ | $I = C\frac{dV}{dt}$ | Electric field: $E = \frac{1}{2}CV^2$ |
| Inductor | L | $j\omega L$ | $V = L\frac{dI}{dt}$ | Magnetic field: $E = \frac{1}{2}LI^2$ |

### Impedance in the Frequency Domain

The concept of impedance unifies resistors, capacitors, and inductors into a single framework:

$$Z_{total} = Z_1 + Z_2 \quad \text{(series)}$$
$$\frac{1}{Z_{total}} = \frac{1}{Z_1} + \frac{1}{Z_2} \quad \text{(parallel)}$$

This is identical to the Laplace domain with $s = j\omega$.

```
  Impedance magnitude vs. frequency:
  
  |Z|
   │   L: rises with ω       ╱
   │                        ╱
   │    R: constant    ──────────── R
   │                        ╲
   │   C: falls with ω       ╲
   └──────────────────────────── ω
```

---

## 4.3 Diodes

A diode allows current in one direction only (idealized).

### Ideal Diode Model

$$I = I_S\left(e^{V_D / nV_T} - 1\right)$$

Where $V_T = kT/q \approx 26$ mV at room temperature, $n \approx 1-2$.

### Practical Models

| Model | When to Use |
|---|---|
| Ideal: ON if forward-biased, OFF if reverse | Quick analysis, digital circuits |
| Constant voltage drop: $V_D \approx 0.7$ V (Si) | Most analog circuit analysis |
| Exponential model | Precision circuits, temperature effects |
| SPICE model | Simulation, detailed design |

### Key Diode Applications in Control

- **Rectification**: AC to DC conversion (power supplies)
- **Protection**: Flyback diodes on inductors (motors, relays)
- **Clamping**: Voltage limiting for ADC input protection
- **Reference**: Zener diodes for voltage regulation

---

## 4.4 Transistors: BJT and MOSFET

### BJT (Bipolar Junction Transistor)

```
       C (Collector)
       │
       ├──┤ (Base)
       │  B
       │
       E (Emitter)
```

**Key relationships (active region, NPN):**

$$I_C = \beta I_B \qquad I_E = I_C + I_B \approx I_C \text{ (for large β)}$$

**Small-signal model** (for amplifier analysis):

$$g_m = \frac{I_C}{V_T}, \qquad r_\pi = \frac{\beta}{g_m}$$

### MOSFET (Metal-Oxide-Semiconductor FET)

```
       D (Drain)
       │
       ├──┤ (Gate)
       │  G
       │
       S (Source)
```

**Key relationships (saturation region, NMOS):**

$$I_D = \frac{1}{2} k_n \frac{W}{L} (V_{GS} - V_{th})^2$$

**Why MOSFETs dominate in control electronics:**
- Voltage-controlled (high input impedance → easy to drive from logic)
- Very fast switching (ns range)
- Available in high-voltage, high-current variants for power stages
- Low on-resistance $R_{DS,on}$ for efficient switching

---

## 4.5 Operational Amplifiers (Op-Amps)

The op-amp is the **most important analog building block** in control electronics.

### Ideal Op-Amp Rules

1. **Infinite input impedance**: $I_+ = I_- = 0$ (no current into inputs)
2. **Zero output impedance**: Can drive any load
3. **Infinite open-loop gain**: $A_{OL} \to \infty$
4. **Virtual short** (with negative feedback): $V_+ = V_-$

### Fundamental Configurations

```
  Inverting Amplifier:           Non-Inverting Amplifier:
  
  V_in ──R₁──┬── R_f ──┐       V_in ──────┐
              │         │                   │
              ├─ (−)    │                   (+)
              │  Op-Amp ├── V_out           Op-Amp ── V_out
              ├─ (+)    │                   (−)
              │         │                   │
             GND       (feedback)     R₁──┬── R_f
                                          │
                                         GND
```

| Configuration | Transfer Function | Notes |
|---|---|---|
| Inverting | $\frac{V_{out}}{V_{in}} = -\frac{R_f}{R_1}$ | Inverts signal; input impedance = $R_1$ |
| Non-inverting | $\frac{V_{out}}{V_{in}} = 1 + \frac{R_f}{R_1}$ | No inversion; very high input impedance |
| Voltage follower | $V_{out} = V_{in}$ ($R_f = 0, R_1 = \infty$) | Buffer; impedance matching |
| Summing | $V_{out} = -(R_f/R_1 \cdot V_1 + R_f/R_2 \cdot V_2)$ | Analog addition |
| Differentiator | $V_{out} = -RC \frac{dV_{in}}{dt}$ | Noisy — rarely used in practice |
| Integrator | $V_{out} = -\frac{1}{RC}\int V_{in} dt$ | Core of analog PID controllers |

See: [examples/opamp-inverting-amplifier.md](examples/opamp-inverting-amplifier.md)

---

## 4.6 Analog Filters

Filters are essential for signal conditioning in control systems.

### Filter Types

```
  |H(jω)|
  ────────────────────────────
  1 │────╲                     Low-Pass
    │     ╲
  0 │──────╲──────────────
  
  1 │──────╱──────────────     High-Pass
    │     ╱
  0 │────╱
  
  1 │     ╱╲                   Band-Pass
    │    ╱  ╲
  0 │───╱────╲────────────
  
  1 │──╲    ╱──────────────    Band-Stop (Notch)
    │   ╲  ╱
  0 │    ╲╱
```

### First-Order RC Low-Pass Filter

$$H(s) = \frac{1}{RCs + 1} = \frac{1}{\tau s + 1}$$

- Cutoff frequency: $f_c = \frac{1}{2\pi RC}$
- Roll-off: −20 dB/decade
- Phase at cutoff: −45°

### Second-Order Filters (Sallen-Key, Multiple Feedback)

$$H(s) = \frac{\omega_n^2}{s^2 + \frac{\omega_n}{Q}s + \omega_n^2}$$

- Quality factor $Q$ controls the peaking near cutoff
- Butterworth ($Q = 0.707$): maximally flat passband
- Chebyshev: sharper cutoff but passband ripple
- Bessel: maximally flat group delay (best for transient response)

See: [examples/rc-filter-analysis.py](examples/rc-filter-analysis.py)

---

## 4.7 Noise in Analog Circuits

### Noise Sources

| Type | Origin | Spectrum | Mitigation |
|---|---|---|---|
| Thermal (Johnson) | Random electron motion in resistors | White (flat) | Lower R, lower T |
| Shot | Discrete electron flow across junctions | White | Lower DC current |
| Flicker (1/f) | Semiconductor surface effects | Pink (1/f) | Chopper stabilization |
| EMI | External interference | Varies | Shielding, filtering |

### Noise Figure

$$\text{SNR}_{out} = \text{SNR}_{in} - NF$$

Where NF (Noise Figure) quantifies how much a circuit degrades the signal-to-noise ratio.

🔧 **Practical**: In control systems, the sensor and first amplifier stage dominate noise performance. Design this front-end carefully — no amount of digital filtering can recover signal-to-noise ratio lost in the analog domain.

---

## 4.8 Analog Design Trade-Offs

| Trade-Off | Dimension 1 | Dimension 2 | Reality |
|---|---|---|---|
| **Bandwidth vs. Noise** | Wider BW → captures fast dynamics | Wider BW → more noise | Match BW to signal needs |
| **Gain vs. Bandwidth** | Higher gain amplifies signal | Gain-bandwidth product is constant | Cascade stages for high gain |
| **Speed vs. Power** | Faster circuits → more current | Battery/thermal limits | Choose minimum speed that works |
| **Precision vs. Cost** | Precision components are expensive | Budget constraints | Precision only where it matters |

---

## Examples

| File | Description |
|---|---|
| [opamp-inverting-amplifier.md](examples/opamp-inverting-amplifier.md) | Detailed op-amp inverting amplifier design |
| [rc-filter-analysis.py](examples/rc-filter-analysis.py) | RC filter frequency response simulation |
| [bjt-common-emitter.md](examples/bjt-common-emitter.md) | BJT common-emitter amplifier design |
| [mosfet-switching.md](examples/mosfet-switching.md) | MOSFET as a switch for motor control |

---

**Previous → [03-signals-and-systems](../03-signals-and-systems/README.md)**  
**Next → [05-digital-electronics](../05-digital-electronics/README.md)**
