# Example: Full-Bridge Rectifier Analysis

## Purpose
Analyze a full-bridge rectifier circuit with filter capacitor for converting AC mains to DC, including ripple voltage calculation and component selection.

---

## Circuit

```
  AC Input          Bridge Rectifier              Filter    Load
  (transformer                                       │
   secondary)    D1 ──►──┐    ┌──◄── D3              │
       ┌─────────────────┤    ├─────────────┬─── + ──┤
       │                 │    │             │        │
     ~ │              (V_out across)     C_filter  R_load
       │                 │    │             │        │
       └─────────────────┤    ├─────────────┴─── − ──┤
                 D2 ──►──┘    └──◄── D4              │
```

---

## Without Filter Capacitor

The output is a full-wave rectified sine:

$$V_{out}(t) = V_m |\sin(\omega t)|$$

```
  V_out
  V_m │  ╱╲    ╱╲    ╱╲    ╱╲
      │ ╱  ╲  ╱  ╲  ╱  ╲  ╱  ╲
      │╱    ╲╱    ╲╱    ╲╱    ╲
  0   └────────────────────────── t
      
  Average: V_avg = 2·V_m/π ≈ 0.636 × V_m
  Ripple frequency: 2× line frequency (100/120 Hz)
```

---

## With Filter Capacitor

The capacitor charges to $V_m$ and discharges through the load between peaks:

```
  V_out
  V_m │──╲    ╱──╲    ╱──╲    ╱──  ← V_m (peak)
      │   ╲  ╱    ╲  ╱    ╲  ╱
      │    ╲╱      ╲╱      ╲╱     ← V_m - ΔV (trough)
      │   
      │   ◄──── ΔV (ripple) ────►
  0   └────────────────────────── t
```

### Ripple Voltage

$$\boxed{\Delta V \approx \frac{I_{load}}{2 f_{line} \cdot C}}$$

Where:
- $I_{load}$: DC load current [A]
- $f_{line}$: AC line frequency [Hz] (50 or 60 Hz)
- $C$: Filter capacitance [F]
- Factor 2: full-bridge rectifier doubles the ripple frequency

---

## Design Example: 12V DC Power Supply

### Requirements
- Output: 12V DC, 1A
- Input: 230V AC, 50 Hz mains
- Ripple: < 5% (< 0.6V peak-to-peak)

### Step 1: Transformer Selection

$$V_{secondary,rms} = \frac{V_{out} + V_{ripple}/2 + 2V_{diode}}{\sqrt{2}} = \frac{12 + 0.3 + 1.4}{1.414} \approx 9.7 \;\text{V rms}$$

**Select**: 230V:10V transformer (gives $V_m = 10\sqrt{2} = 14.1$ V)

Actual DC output: $V_{DC} \approx V_m - 2V_D = 14.1 - 1.4 = 12.7$ V ✓

### Step 2: Filter Capacitor

$$C = \frac{I_{load}}{2 f_{line} \cdot \Delta V} = \frac{1.0}{2 \times 50 \times 0.6} = 16,700 \;\mu\text{F}$$

**Select**: $C = 22,000 \;\mu\text{F}$, 25V electrolytic

Actual ripple: $\Delta V = \frac{1.0}{2 \times 50 \times 0.022} = 0.45$ V (3.5%) ✓

### Step 3: Diode Selection

- $V_{RRM} > V_m \times \sqrt{2}$ (safety margin) → $V_{RRM} > 20$ V (use 50V-rated)
- $I_{avg} > I_{load} / 2 = 0.5$ A
- $I_{surge}$ at turn-on can be very high (capacitor charging)

**Select**: 1N5401 (3A, 100V) or bridge module KBP206 (2A, 600V)

### Summary

| Component | Value | Part |
|---|---|---|
| Transformer | 230V:10V, 15VA | Standard |
| Bridge diodes | 100V, 3A | 4× 1N5401 |
| Filter cap | 22,000 μF / 25V | Electrolytic |
| Output voltage | 12.7V ± 0.23V | Meets spec |

⚠️ **Pitfall**: The DC output from a rectifier-filter is not well-regulated — it varies with load current and mains voltage. For a stable 12V output, add a linear voltage regulator (e.g., 7812) or use a switching regulator after the rectifier.
