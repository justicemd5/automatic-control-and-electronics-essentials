# Example: H-Bridge Motor Driver Circuit

## Purpose
Design a bidirectional DC motor driver using an H-bridge topology, covering MOSFET selection, gate driving, current sensing, and protection circuits.

---

## H-Bridge Topology

```
  V_motor (+)
      │
  ┌───┼───────────────────┐
  │   │                   │
 Q1   │                  Q3
(P-ch)│               (P-ch)
  │   │                   │
  ├───┼──── Motor ────────┤
  │   │     ──►           │
 Q2   │                  Q4
(N-ch)│               (N-ch)
  │   │                   │
  └───┼───────────────────┘
      │
  R_sense ── Current Sense
      │
     GND
```

### Operating Modes

| Mode | Q1 | Q2 | Q3 | Q4 | Motor |
|---|---|---|---|---|---|
| Forward | ON | OFF | OFF | ON | CW |
| Reverse | OFF | ON | ON | OFF | CCW |
| Brake (low) | OFF | ON | OFF | ON | Short to GND |
| Coast | OFF | OFF | OFF | OFF | Free-running |

⚠️ **Pitfall**: Never turn on Q1+Q2 or Q3+Q4 simultaneously — this creates a **shoot-through** short circuit from V_motor to GND, potentially destroying the MOSFETs instantly.

---

## Design Example

### Motor Specifications
- DC motor: 12V, 5A max, stall current 15A
- Control: PWM at 20 kHz, bidirectional

### MOSFET Selection

**High-side (P-channel)**: IRF4905 (−55V, −74A, $R_{DS,on}$ = 20 mΩ)
**Low-side (N-channel)**: IRLZ44N (55V, 47A, $R_{DS,on}$ = 22 mΩ)

Alternatively, use all N-channel with a high-side gate driver (e.g., IR2110):

```
                    V_motor = 12V
                        │
  Bootstrap ──── High-Side Driver ──── Q1 (N-ch)
  Capacitor                               │
                                      Motor terminal
                                          │
                 Low-Side Driver ───── Q2 (N-ch)
                                          │
                                         GND
```

💡 **Insight**: N-channel MOSFETs have lower $R_{DS,on}$ than P-channel for the same die size. Modern H-bridges use all N-channel MOSFETs with bootstrap or charge-pump gate drivers for the high side.

### Gate Drive Requirements

For the IRLZ44N:
- $V_{GS,th}$ = 1–2V (logic-level compatible)
- $Q_g$ = 48 nC (total gate charge)
- Gate drive current: $I_g = Q_g \times f_{PWM} = 48 \times 10^{-9} \times 20000 = 0.96$ mA (average)
- Peak gate current for fast switching: $I_{g,peak} = Q_g / t_{switch} = 48\text{nC} / 50\text{ns} = 0.96$ A

### Dead Time

Insert dead time between high-side turn-off and low-side turn-on (and vice versa) to prevent shoot-through:

```
  Q1 gate: ────┐          ┌────
               │          │
               └──────────┘
  
  Q2 gate:          ┌────────┐
                    │        │
  ──────────────────┘        └────
  
               │◄─►│ = Dead time (100-500 ns typical)
```

---

## Current Sensing

### Low-Side Shunt Resistor

$$R_{sense} = \frac{V_{sense,max}}{I_{max}} = \frac{0.1}{15} = 6.7 \;\text{mΩ}$$

Power dissipation: $P = I^2 R = 15^2 \times 0.0067 = 1.5$ W

**Select**: 10 mΩ, 2W, 1% precision shunt resistor

Sense voltage at full load: $V_{sense} = 5 \times 0.01 = 50$ mV → amplify with INA180 (current sense amplifier, gain = 50) → $V_{out} = 2.5$ V

---

## Protection Circuits

### Flyback Diodes

```
  ┌─── D1 ───┐      ┌─── D3 ───┐
  │           │      │           │
  Q1          │      Q3          │
  │    Motor  │      │           │
  ├───►──────►├──────┤           │
  │           │      │           │
  Q2          │      Q4          │
  │           │      │           │
  └─── D2 ───┘      └─── D4 ───┘
```

Motor inductance causes voltage spikes when switching off. Body diodes of MOSFETs can absorb this, but external Schottky diodes are faster and more efficient.

### Additional Protections

| Protection | Method | Purpose |
|---|---|---|
| Overcurrent | Current sense + comparator | Prevent MOSFET destruction |
| Overvoltage | TVS diode across V_motor | Clamp regenerative braking spikes |
| Overtemperature | NTC on heat sink + shutdown | Prevent thermal runaway |
| Undervoltage lockout (UVLO) | Gate driver feature | Prevent partial turn-on |
| Reverse polarity | P-MOSFET in supply line | Protect against wrong connection |

---

## Integrated H-Bridge ICs

For lower-current applications, integrated solutions simplify design:

| IC | Voltage | Current | Features |
|---|---|---|---|
| L298N | 46V | 2A per channel | Dual H-bridge, common in Arduino projects |
| DRV8871 | 45V | 3.6A | Single H-bridge, current limiting |
| TB6612FNG | 15V | 1.2A | Dual, efficient, small |
| BTS7960 | 45V | 43A | Half-bridge, high current |

🔧 **Practical**: For prototyping, use an integrated H-bridge driver. For production or high-current applications, discrete MOSFETs give better thermal performance and flexibility.
