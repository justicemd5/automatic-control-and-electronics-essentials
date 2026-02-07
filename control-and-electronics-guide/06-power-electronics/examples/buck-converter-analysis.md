# Example: Buck Converter Analysis — Complete Design

## Purpose
Design a buck (step-down) DC-DC converter from 12V to 5V at 2A output, selecting all key components and calculating ripple, efficiency, and thermal requirements.

---

## Specifications

| Parameter | Value |
|---|---|
| Input voltage $V_{in}$ | 12 V |
| Output voltage $V_{out}$ | 5 V |
| Output current $I_{out}$ | 2 A |
| Switching frequency $f_{sw}$ | 500 kHz |
| Output voltage ripple | < 1% (50 mV) |
| Operating mode | Continuous Conduction Mode (CCM) |

---

## Duty Cycle

$$D = \frac{V_{out}}{V_{in}} = \frac{5}{12} \approx 0.417 = 41.7\%$$

---

## Inductor Selection

### Inductor Current Ripple

$$\Delta I_L = \frac{(V_{in} - V_{out}) \cdot D}{f_{sw} \cdot L}$$

Design rule: $\Delta I_L = 20\text{–}40\%$ of $I_{out}$ for good CCM operation.

Target: $\Delta I_L = 0.3 \times I_{out} = 0.6$ A

$$L = \frac{(V_{in} - V_{out}) \cdot D}{f_{sw} \cdot \Delta I_L} = \frac{(12 - 5) \times 0.417}{500000 \times 0.6} = \frac{2.917}{300000} \approx 9.7 \;\mu\text{H}$$

**Select**: $L = 10 \;\mu\text{H}$ (standard value, Wurth 744774110)

### Verify Ripple

$$\Delta I_L = \frac{7 \times 0.417}{500000 \times 10 \times 10^{-6}} = \frac{2.917}{5.0} = 0.583 \;\text{A}$$

Peak inductor current: $I_{L,peak} = I_{out} + \Delta I_L / 2 = 2 + 0.292 = 2.29$ A

Saturation current rating must exceed: $I_{sat} > 2.29$ A (with margin, select $I_{sat} > 3$ A)

---

## Output Capacitor

$$\Delta V_{out} = \frac{\Delta I_L}{8 \cdot f_{sw} \cdot C_{out}}$$

$$C_{out} = \frac{\Delta I_L}{8 \cdot f_{sw} \cdot \Delta V_{out}} = \frac{0.583}{8 \times 500000 \times 0.05} = \frac{0.583}{200000} \approx 2.9 \;\mu\text{F}$$

**Select**: $C_{out} = 22 \;\mu\text{F}$ ceramic (MLCC X5R, ESR < 5 mΩ)

Using larger capacitance provides margin and reduces ripple further:

$$\Delta V_{out} = \frac{0.583}{8 \times 500000 \times 22 \times 10^{-6}} = 6.6 \;\text{mV}$$ ✓ (well under 50 mV)

⚠️ **Pitfall**: Capacitor ESR contributes additional ripple: $\Delta V_{ESR} = \Delta I_L \times ESR$. For ceramic caps with ESR ~ 5 mΩ: $\Delta V_{ESR} = 0.583 \times 0.005 = 2.9$ mV. Total ripple ≈ 9.5 mV. For electrolytic caps with ESR ~ 100 mΩ, ESR-ripple would dominate!

---

## MOSFET Selection (High-Side Switch)

Requirements:
- $V_{DS,max} > V_{in} \times 1.5 = 18$ V
- $I_D > I_{L,peak} \times 2 = 4.6$ A (with margin)
- $R_{DS,on}$: as low as possible for efficiency
- $Q_g$: as low as possible for fast switching

**Select**: Si4838DY (N-channel, 30V, 25A, $R_{DS,on}$ = 8 mΩ, $Q_g$ = 14 nC)

### Conduction Loss

$$P_{cond} = I_{out}^2 \times R_{DS,on} \times D = 4 \times 0.008 \times 0.417 = 13.3 \;\text{mW}$$

### Switching Loss

$$P_{sw} = \frac{1}{2} V_{in} \cdot I_{out} \cdot (t_r + t_f) \cdot f_{sw} = \frac{1}{2} \times 12 \times 2 \times 20 \times 10^{-9} \times 500000 = 120 \;\text{mW}$$

---

## Freewheeling Diode (or Synchronous Rectifier)

**Schottky diode**: SS34 (3A, 40V, $V_F$ = 0.45V)

$$P_{diode} = V_F \cdot I_{out} \cdot (1-D) = 0.45 \times 2 \times 0.583 = 524 \;\text{mW}$$

🔧 **Practical**: For higher efficiency, replace the diode with a second MOSFET (synchronous buck). This reduces rectifier loss to $I^2 R_{DS,on}(1-D) \approx 18.7$ mW — a 25× improvement!

---

## Efficiency Estimate

$$P_{out} = V_{out} \times I_{out} = 5 \times 2 = 10 \;\text{W}$$

| Loss Component | Power |
|---|---|
| MOSFET conduction | 13 mW |
| MOSFET switching | 120 mW |
| Diode conduction | 524 mW |
| Inductor DCR ($R_{DCR}$ ≈ 30 mΩ) | $I^2 R = 120$ mW |
| **Total losses** | **~777 mW** |

$$\eta = \frac{10}{10 + 0.777} = 92.8\%$$

With synchronous rectification: losses drop to ~270 mW → $\eta \approx 97.4\%$

---

## Component Summary

| Component | Value | Part Number |
|---|---|---|
| Inductor | 10 μH, 3A sat | Wurth 744774110 |
| Output cap | 22 μF ceramic X5R | GRM32ER61C226 |
| Input cap | 10 μF ceramic | Standard |
| High-side MOSFET | 30V, 8mΩ | Si4838DY |
| Freewheeling diode | 40V Schottky, 3A | SS34 |
| Controller IC | (integrated PWM controller) | TPS5430 or similar |
