# Example: Thermal Design for Power Electronics

## Purpose
Demonstrate the thermal equivalent circuit method for heat sink selection in power electronics, ensuring junction temperature stays within safe limits.

---

## Thermal Resistance Model

Heat flows from the semiconductor junction to the ambient air through a series of thermal resistances, analogous to electrical current through resistors:

```
  T_junction ─── R_θJC ─── T_case ─── R_θCS ─── T_heatsink ─── R_θSA ─── T_ambient
      │                       │                      │                       │
      ▼                       ▼                      ▼                       ▼
   (hot)                   (warm)                 (warm)                  (cool)
   
  Electrical analogy:
  P_loss ─── R_θJC ─── R_θCS ─── R_θSA ─── GND (T_ambient)
  (current)  (resistors)                     (voltage reference)
```

### Thermal Ohm's Law

$$\boxed{T_J = T_A + P_{loss} \times (R_{\theta JC} + R_{\theta CS} + R_{\theta SA})}$$

Where:
- $T_J$: Junction temperature [°C]
- $T_A$: Ambient temperature [°C]
- $P_{loss}$: Total power dissipation [W]
- $R_{\theta JC}$: Junction-to-case thermal resistance [°C/W] — device property
- $R_{\theta CS}$: Case-to-sink thermal resistance [°C/W] — thermal interface
- $R_{\theta SA}$: Sink-to-ambient thermal resistance [°C/W] — heat sink property

---

## Design Example

### Scenario: MOSFET in a Buck Converter

**Given:**
- MOSFET: IRFZ44N in TO-220 package
  - $R_{\theta JC} = 1.5$ °C/W
  - $T_{J,max} = 175$ °C
- Power dissipation: $P_{loss} = 5$ W (conduction + switching)
- Ambient temperature: $T_A = 40$ °C (inside an enclosure)
- Thermal interface: thermal pad, $R_{\theta CS} = 0.5$ °C/W

### Step 1: Calculate Required Total Thermal Resistance

$$R_{\theta,total} \leq \frac{T_{J,max} - T_A}{P_{loss}} = \frac{175 - 40}{5} = 27 \;\text{°C/W}$$

### Step 2: Calculate Required Heat Sink Thermal Resistance

$$R_{\theta SA} \leq R_{\theta,total} - R_{\theta JC} - R_{\theta CS} = 27 - 1.5 - 0.5 = 25 \;\text{°C/W}$$

This is easily achievable — even no heat sink might work (TO-220 in free air: $R_{\theta JA} \approx 62$ °C/W).

### Step 3: Check Without Heat Sink

$$T_J = 40 + 5 \times 62 = 350 \;\text{°C}$$

**Far exceeds $T_{J,max}$!** A heat sink is definitely needed.

### Step 4: Select Heat Sink

For $R_{\theta SA} \leq 25$ °C/W with 80% derating:

**Target**: $R_{\theta SA} \leq 20$ °C/W → select a small finned heat sink

**Example**: Aavid 577202B00000G, $R_{\theta SA} = 13$ °C/W (natural convection)

### Step 5: Verify Final Temperature

$$T_J = 40 + 5 \times (1.5 + 0.5 + 13) = 40 + 75 = 115 \;\text{°C}$$

$$115°\text{C} < 175°\text{C}$$ ✓ with 60°C margin

---

## Thermal Interface Materials

| Material | $R_{\theta CS}$ [°C/W] | Pros | Cons |
|---|---|---|---|
| Thermal grease | 0.1–0.5 | Lowest resistance | Messy, pump-out over time |
| Thermal pad (silicone) | 0.5–2.0 | Clean, easy | Moderate resistance |
| Phase-change material | 0.2–0.5 | Self-applying | Higher cost |
| Bare metal (no TIM) | 1.0–5.0 | Simplest | Air gaps increase resistance |
| Electrical insulator pad | 0.5–3.0 | Isolates case from sink | Higher resistance |

🔧 **Practical**: Always use thermal interface material. Air gaps between case and heat sink can have $R_{\theta CS} > 5$ °C/W, negating the benefit of an expensive heat sink.

---

## Forced Convection

If natural convection is insufficient, add a fan:

$$R_{\theta SA,forced} \approx \frac{R_{\theta SA,natural}}{3 \text{ to } 5}$$

A heat sink with $R_{\theta SA} = 13$ °C/W naturally becomes ~3–4 °C/W with a small fan.

---

## Design Rules Summary

| Rule | Reason |
|---|---|
| Design for worst-case $T_A$ | Enclosures can be 20-40°C above room temp |
| Derate $T_{J,max}$ by 20-30% | Reliability degrades exponentially with temperature |
| Account for all heat sources | Multiple devices on one sink share thermal budget |
| Verify with measurement | Thermal models are approximate — measure $T_{case}$ |
| Consider transient thermal | Pulsed loads may exceed steady-state $T_J$ briefly |

💡 **Insight**: For every 10°C reduction in junction temperature, semiconductor lifetime approximately doubles (Arrhenius relationship). Thermal design directly impacts reliability.
