# Example: SIL Verification Calculation

## Purpose
Calculate the Safety Integrity Level (SIL) achieved by a safety function, demonstrating the quantitative verification process required by IEC 61508.

---

## Safety Function: Emergency Stop via Pressure Switch

### System Description

A pressure relief system that shuts a valve when tank pressure exceeds the setpoint:

```
  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ Pressure │    │  Logic   │    │  Valve   │    │  Final   │
  │ Sensor   │───►│  Solver  │───►│  Driver  │───►│  Element │
  │ (PT)     │    │  (PLC)   │    │ (Solenoid│    │  (Valve) │
  │          │    │          │    │  Driver) │    │          │
  └──────────┘    └──────────┘    └──────────┘    └──────────┘
  
  Sensor        Logic Solver       Output           Actuator
  Subsystem     Subsystem          Subsystem
```

**Target**: SIL 2 (PFD < $10^{-2}$)

---

## Step 1: Component Failure Data

| Component | Dangerous Failure Rate λ_D | Safe Failure Rate λ_S | Diagnostic Coverage DC |
|---|---|---|---|
| Pressure transmitter | $5.0 \times 10^{-7}$ /h | $1.0 \times 10^{-6}$ /h | 60% |
| Safety PLC (1oo1D) | $1.0 \times 10^{-8}$ /h | $5.0 \times 10^{-8}$ /h | 99% |
| Solenoid driver | $3.0 \times 10^{-7}$ /h | $5.0 \times 10^{-7}$ /h | 0% (no diagnostics) |
| Shutdown valve | $1.0 \times 10^{-6}$ /h | $2.0 \times 10^{-6}$ /h | 0% (tested manually) |

Test interval: $T_1 = 8760$ hours (1 year)

---

## Step 2: Calculate PFD for Each Subsystem

### Sensor Subsystem (1oo1 architecture)

$$\text{PFD}_{sensor} = (1 - DC) \cdot \lambda_{DU} \cdot \frac{T_1}{2} + DC \cdot \lambda_{DD} \cdot \text{MTTR}$$

Where:
- $\lambda_{DU} = (1 - DC) \cdot \lambda_D = (1 - 0.6) \times 5.0 \times 10^{-7} = 2.0 \times 10^{-7}$ /h (undetected)
- $\lambda_{DD} = DC \cdot \lambda_D = 0.6 \times 5.0 \times 10^{-7} = 3.0 \times 10^{-7}$ /h (detected)
- MTTR = 8 hours (repair time for detected faults)

$$\text{PFD}_{sensor} = 2.0 \times 10^{-7} \times \frac{8760}{2} + 3.0 \times 10^{-7} \times 8$$

$$= 8.76 \times 10^{-4} + 2.4 \times 10^{-6} \approx 8.78 \times 10^{-4}$$

### Logic Solver Subsystem (Safety PLC, 1oo1D)

$$\lambda_{DU} = (1 - 0.99) \times 1.0 \times 10^{-8} = 1.0 \times 10^{-10}$$ /h

$$\text{PFD}_{logic} = 1.0 \times 10^{-10} \times \frac{8760}{2} = 4.38 \times 10^{-7}$$

(Negligible compared to sensor and valve)

### Output + Valve Subsystem (1oo1, no diagnostics)

$$\lambda_{DU,driver} = 3.0 \times 10^{-7}$$ /h (DC = 0)

$$\lambda_{DU,valve} = 1.0 \times 10^{-6}$$ /h (DC = 0)

$$\text{PFD}_{output} = (3.0 \times 10^{-7} + 1.0 \times 10^{-6}) \times \frac{8760}{2}$$

$$= 1.3 \times 10^{-6} \times 4380 = 5.69 \times 10^{-3}$$

---

## Step 3: Total System PFD

For a series safety function (all subsystems must work):

$$\text{PFD}_{total} = \text{PFD}_{sensor} + \text{PFD}_{logic} + \text{PFD}_{output}$$

$$= 8.78 \times 10^{-4} + 4.38 \times 10^{-7} + 5.69 \times 10^{-3}$$

$$\boxed{\text{PFD}_{total} = 6.57 \times 10^{-3}}$$

### SIL Assessment

| SIL | PFD Range | Our PFD | Pass? |
|---|---|---|---|
| SIL 1 | $10^{-2}$ to $10^{-1}$ | $6.57 \times 10^{-3}$ | ✓ (exceeds) |
| **SIL 2** | $10^{-3}$ to $10^{-2}$ | $6.57 \times 10^{-3}$ | **✓ Pass** |
| SIL 3 | $10^{-4}$ to $10^{-3}$ | $6.57 \times 10^{-3}$ | ✗ Fail |

**Result: SIL 2 achieved** ✓

But just barely — the dominant contributor is the valve subsystem ($5.69 \times 10^{-3}$), which accounts for 87% of the total PFD.

---

## Step 4: Improvement Options

### Option A: More Frequent Testing

Reduce test interval from 1 year to 6 months ($T_1 = 4380$ h):

$$\text{PFD}_{output,new} = 1.3 \times 10^{-6} \times 2190 = 2.85 \times 10^{-3}$$

$$\text{PFD}_{total,new} = 3.29 \times 10^{-3}$$ → Still SIL 2, with more margin

### Option B: Redundant Valve (1oo2)

$$\text{PFD}_{valve,1oo2} = \frac{(\lambda_{DU} \cdot T_1)^2}{3} = \frac{(1.0 \times 10^{-6} \times 8760)^2}{3} = 2.56 \times 10^{-5}$$

$$\text{PFD}_{total,new} = 8.78 \times 10^{-4} + 2.56 \times 10^{-5} = 9.04 \times 10^{-4}$$ → **SIL 3 achievable!**

### Option C: Add Partial Stroke Testing (PST) to Valve

PST gives ~60% diagnostic coverage for the valve:

$$\lambda_{DU,valve} = (1 - 0.6) \times 1.0 \times 10^{-6} = 4.0 \times 10^{-7}$$ /h

$$\text{PFD}_{valve,PST} = 4.0 \times 10^{-7} \times 4380 = 1.75 \times 10^{-3}$$

Better, but still SIL 2.

---

## Summary

```
  PFD Contribution Breakdown:
  
  Sensor: ████░░░░░░░░░░░░░░░░░░░░  13%  (8.78e-4)
  Logic:  ░░░░░░░░░░░░░░░░░░░░░░░░   0%  (4.38e-7)
  Output: ████████████████████████   87%  (5.69e-3)
          ────────────────────────
  Total:                             100% (6.57e-3) → SIL 2 ✓
  
  The valve dominates! Improving the valve (redundancy or testing)
  gives the biggest safety improvement.
```

💡 **Insight**: In almost every safety system, the final element (valve, breaker, relay) dominates the PFD because: (1) it has moving parts (higher failure rate), (2) it typically has no online diagnostics, and (3) failures are only discovered during proof testing. This is why partial stroke testing and redundant valves are so common in process safety.

⚠️ **Pitfall**: This calculation assumes independent failures. Common-cause failures (e.g., both sensors fail due to the same corrosive environment) must be accounted for using a β-factor model, which typically adds 2-10% to the PFD for redundant architectures.
