# Example: BJT Common-Emitter Amplifier

## Purpose

Design and analyze a BJT common-emitter amplifier — the fundamental single-transistor voltage amplifier. This configuration is widely used in sensor signal conditioning and small-signal amplification.

---

## Circuit

```
         V_CC (+12V)
           │
           R_C (collector resistor)
           │
           ├──────── V_out (C_out coupling)
           │
      C    │
      ─────┤ (NPN BJT, e.g., 2N2222)
      B    │
      │    E
      │    │
  V_in ── R_B    R_E (emitter resistor)
  (C_in)  │    │
          GND  GND
```

### Voltage Divider Bias (More Stable)

```
        V_CC
         │
    ┌── R_1 ──┬── R_C ──┬─── V_out
    │         │         │
    │    B ───┤    C    │
    │    (Q1 NPN)       │
    │    E ───┤         │
    │         │         │
    └── R_2 ──┘    R_E ──┘
         │              │
        GND            GND
```

---

## DC Bias Analysis (Voltage Divider)

### Design Equations

Base voltage:
$$V_B = V_{CC} \frac{R_2}{R_1 + R_2}$$

Emitter voltage:
$$V_E = V_B - V_{BE} \approx V_B - 0.7 \text{ V}$$

Emitter/Collector current ($\beta \gg 1$):
$$I_C \approx I_E = \frac{V_E}{R_E}$$

Collector voltage:
$$V_C = V_{CC} - I_C R_C$$

### Design Rules of Thumb

1. Set $V_E \approx 1-2$ V for thermal stability
2. Set $V_C \approx V_{CC}/2$ for maximum output swing
3. Choose $R_1 \| R_2 \ll \beta R_E$ for bias stability (≤ 0.1βR_E)

---

## Small-Signal (AC) Analysis

### Small-Signal Parameters

$$g_m = \frac{I_C}{V_T} = \frac{I_C}{26\text{mV}} \qquad r_\pi = \frac{\beta}{g_m} = \frac{\beta V_T}{I_C}$$

### Voltage Gain

**Without emitter bypass capacitor:**

$$A_v = -\frac{g_m R_C}{1 + g_m R_E} \approx -\frac{R_C}{R_E} \quad \text{(if } g_m R_E \gg 1\text{)}$$

**With emitter bypass capacitor** (R_E bypassed at AC):

$$A_v = -g_m R_C = -\frac{I_C \cdot R_C}{V_T}$$

💡 **Insight**: Without the bypass capacitor, the gain is approximately $-R_C/R_E$ — **independent of transistor parameters**. This is negative feedback (emitter degeneration) at work! With the bypass cap, gain is higher but depends on $I_C$ and is less stable.

---

## Numerical Design

**Requirements**: Gain ≈ −10, $V_{CC}$ = 12 V, using 2N2222 ($\beta \approx 200$)

### Step 1: Choose Operating Point
- $I_C = 1$ mA (reasonable for small-signal amplifier)
- $V_E = 1.2$ V → $R_E = V_E / I_C = 1.2\text{V} / 1\text{mA} = 1.2\text{ k}\Omega$ (use 1.2 kΩ)
- $V_C \approx V_{CC}/2 = 6$ V → $R_C = (V_{CC} - V_C) / I_C = 6\text{V} / 1\text{mA} = 6\text{ k}\Omega$

### Step 2: Bias Resistors
- $V_B = V_E + 0.7 = 1.9$ V
- $V_B / V_{CC} = 1.9/12 = 0.158$
- Choose $R_2 = 10\text{ k}\Omega$, then $R_1 = R_2 (V_{CC}/V_B - 1) = 10\text{k}(12/1.9 - 1) \approx 53\text{ k}\Omega$ (use 56 kΩ)

### Step 3: Verify Gain
- Without bypass: $A_v \approx -R_C / R_E = -6\text{k}/1.2\text{k} = -5$
- With bypass: $g_m = 1\text{mA}/26\text{mV} = 38.5\text{ mA/V}$, $A_v = -g_m R_C = -231$

For $A_v = -10$ with partial bypass:
Use a split emitter resistor: $R_{E1} = 600\Omega$ (bypassed), $R_{E2} = 600\Omega$ (unbypassed)
$$A_v \approx -\frac{R_C}{R_{E2}} = -\frac{6\text{k}}{600} = -10$$ ✓

---

## Frequency Response

### Low-Frequency Cutoff
Determined by coupling capacitors ($C_{in}$, $C_{out}$) and bypass capacitor ($C_E$).

### High-Frequency Cutoff
Determined by transistor's $f_T$ (transition frequency) and Miller effect:

$$C_{Miller} = C_{BC}(1 + |A_v|)$$

For 2N2222: $C_{BC} \approx 8$ pF, so $C_{Miller} = 8(1+10) = 88$ pF

Combined with source resistance: $f_{high} = \frac{1}{2\pi R_s C_{Miller}}$

---

## Key Design Trade-Offs

| More of... | Benefit | Cost |
|---|---|---|
| Emitter degeneration ($R_E$) | Stable gain, less distortion | Lower gain |
| Collector current ($I_C$) | Higher $g_m$, higher gain | More power dissipation |
| Higher $V_{CC}$ | Larger output swing | More power consumption |
| Bypass capacitor | Higher AC gain | Gain depends on $\beta$, less predictable |

⚠️ **Pitfall**: Designing for maximum gain without emitter degeneration creates an amplifier whose gain varies wildly with temperature, transistor replacement, and aging. Always use some degeneration in practical designs.
