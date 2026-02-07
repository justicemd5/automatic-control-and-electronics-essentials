# Example: Thermocouple Interface with Cold-Junction Compensation

## Purpose
Design a Type-K thermocouple measurement circuit, understanding thermoelectric effects, cold-junction compensation, and signal conditioning.

---

## Thermocouple Principles

A thermocouple generates a voltage proportional to the **temperature difference** between two junctions of dissimilar metals:

```
  Hot Junction              Cold Junction (Reference)
  (measurement point)       (connector / PCB)
  
     Chromel (+) ─────────────────────┐
         │                            │ ← V_measured
     Alumel (−)  ─────────────────────┘
         
  T_hot                          T_cold
  (unknown)                      (known or measured)
```

**Seebeck voltage**:

$$V = \int_{T_{cold}}^{T_{hot}} [S_A(T) - S_B(T)] \, dT \approx \alpha \cdot (T_{hot} - T_{cold})$$

For Type-K: $\alpha \approx 41 \;\mu\text{V/°C}$ (varies with temperature)

---

## The Cold-Junction Problem

A thermocouple measures **temperature difference**, not absolute temperature. If $T_{cold}$ is unknown, you cannot determine $T_{hot}$.

Traditional solution: Ice bath at 0°C → $T_{cold} = 0°C$ → $V = \alpha \cdot T_{hot}$

Modern solution: **Electronic cold-junction compensation** — measure $T_{cold}$ with a separate sensor (thermistor, RTD, or IC) at the connector.

```
  Thermocouple           Connector         Measurement
  Wire                   (PCB)             Circuit
  
  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐
  │   T_hot      │  │   T_cold     │  │                 │
  │   Chromel ───┼──┼──► Cu ───────┼──┼── + Amplifier   │
  │   Alumel ────┼──┼──► Cu ───────┼──┼── −             │
  │              │  │              │  │                 │
  │              │  │   [IC Temp   │  │   V_TC ────►    │
  │              │  │    Sensor]───┼──┼── T_cold ──►  MCU│
  └──────────────┘  └──────────────┘  └─────────────────┘
  
  T_hot = f(V_TC) + T_cold
```

---

## Signal Conditioning Circuit

### Requirements for Type-K (0–500°C range)

- Signal range: 0 to ~20.6 mV
- Required gain: ~150× to fill 0–3.3V ADC range
- Noise: thermocouple wires are long → pick up EMI
- Common-mode voltage: up to ±2V from ground loops

### Circuit Design

```
  TC+ ──── R_filter ──┬──── IN+  ┌──────────┐
                      │          │  AD8495   │──── V_out (5 mV/°C)
                    C_filter     │  TC Amp   │
                      │          │  with CJC │
  TC− ──── R_filter ──┴──── IN−  └──────────┘
                                      │
                                    T_cold sensor
                                    (internal)
```

**AD8495** output: $V_{out} = 5 \;\text{mV/°C} \times T_{hot}$ (with internal CJC)

At 25°C: $V_{out} = 125$ mV  
At 500°C: $V_{out} = 2500$ mV  

### Input Filter

EMI filter for noise rejection:

$$R_{filter} = 100 \;\Omega, \quad C_{filter} = 100 \;\text{nF}$$
$$f_{cutoff} = \frac{1}{2\pi R C} = \frac{1}{2\pi \times 100 \times 100 \times 10^{-9}} \approx 16 \;\text{kHz}$$

This rejects high-frequency noise while preserving the slow thermocouple signal.

---

## Type-K Voltage-Temperature Table (Selected Points)

| Temperature [°C] | Voltage [mV] | Sensitivity [μV/°C] |
|---|---|---|
| −200 | −5.891 | ~18 |
| 0 | 0.000 | ~40 |
| 100 | 4.096 | ~41 |
| 200 | 8.138 | ~41 |
| 300 | 12.209 | ~42 |
| 500 | 20.644 | ~43 |
| 1000 | 41.276 | ~39 |
| 1372 (max) | 54.886 | ~34 |

⚠️ **Pitfall**: The thermocouple sensitivity varies with temperature — it is NOT constant. For accurate measurement, use polynomial conversion (NIST ITS-90 tables) rather than a simple linear approximation.

---

## NIST Polynomial (Type K, 0–1372°C)

$$T = \sum_{i=0}^{9} c_i \cdot V^i$$

Where $V$ is in millivolts and $T$ is in °C. The coefficients $c_i$ are tabulated in NIST Monograph 175.

For a simpler approximation (0–500°C, ±0.5°C accuracy):

$$T \approx -0.0001 V^3 + 0.0308 V^2 + 24.35 V + 0.12$$

Where $V$ is in millivolts.

---

## Integrated Solutions

| IC | Type | CJC | Output | Accuracy |
|---|---|---|---|---|
| AD8495 | Analog amp | Internal | 5 mV/°C | ±2°C |
| MAX31855 | Digital (SPI) | Internal | 14-bit | ±2°C |
| MAX6675 | Digital (SPI) | Internal | 12-bit | ±3°C |
| ADS1118 | ADC + CJC | Internal | 16-bit | ±0.5°C (with cal.) |

🔧 **Practical**: For most applications, a MAX31855 + SPI is the simplest solution. For high accuracy, use an ADS1118 with external precision CJC sensor and NIST polynomial lookup.
