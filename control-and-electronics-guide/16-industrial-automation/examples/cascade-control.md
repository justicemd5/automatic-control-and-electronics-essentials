# Example: Cascade Control — Temperature via Flow

## Purpose
Design a cascade control system for a heat exchanger where an outer temperature loop sets the setpoint for an inner flow loop, demonstrating the most common advanced control structure in process industry.

---

## Process Description

```
  Hot Utility (Steam)
       │
       ▼
  ┌────╥────┐
  │    ║    │  Heat Exchanger
  │  ══╬══  │
  │    ║    │
  └────╥────┘
       │
       ▼
  Steam Condensate
  
  Process Fluid ──►┌──────────────┐──► Product
                    │              │    (T_out)
                    │  Shell-Tube  │
                    │  Exchanger   │
                    └──────────────┘
                          ↑
  ┌─────────┐     ┌──────┴───────┐
  │ Control │     │ Steam Flow   │
  │  Valve  │◄────│ Transmitter  │
  │ (FCV)   │     │ (FT)         │
  └─────────┘     └──────────────┘
```

---

## Why Cascade? Single Loop vs. Cascade

### Problem with Single Loop

```
  Single Loop:
  
  T_sp ──►[Temp PID]──► Valve ──► Exchanger ──► T_out
                ↑                                  │
                └──────────────────────────────────┘
```

**Issues**:
- Steam pressure disturbances change flow before temperature changes → slow correction
- The valve + flow dynamics add significant lag inside the temperature loop
- Temperature sensor is slow (large time constant)

### Solution: Cascade

```
  Cascade:
  
  T_sp ──►[Temp PID]──► F_sp ──►[Flow PID]──► Valve ──► Exchanger ──► T_out
           (Master)       ↑       (Slave)                                │
               ↑          │          ↑                                   │
               │          │          └────── Flow sensor ◄───────────────┤
               │          │                  (fast: τ = 1s)              │
               └──────────┼────── Temp sensor ◄──────────────────────────┘
                          │       (slow: τ = 30s)
                          │
                    (inner loop rejects
                     flow disturbances
                     before they affect
                     temperature)
```

---

## Process Model

### Inner Loop (Flow)

$$G_{flow}(s) = \frac{K_v}{(\tau_v s + 1)} = \frac{2.0}{(3s + 1)}$$

- Valve + transmitter: $K_v = 2.0$ (m³/h per % valve)
- Time constant: $\tau_v = 3$ s (valve + flow dynamics)

### Outer Loop (Temperature)

$$G_{temp}(s) = \frac{K_t e^{-\theta s}}{(\tau_1 s + 1)(\tau_2 s + 1)} = \frac{15 \cdot e^{-5s}}{(30s + 1)(10s + 1)}$$

- Process gain: $K_t = 15$ °C per m³/h
- Time constants: 30 s, 10 s (thermal inertia)
- Dead time: 5 s (transport delay in pipes)

---

## Controller Design

### Step 1: Inner (Flow) PID — Tune First

**Rule**: Inner loop bandwidth should be 5-10× faster than outer loop.

Using IMC tuning for the flow process:

$$K_{c,inner} = \frac{\tau_v}{K_v \cdot \lambda_{inner}} = \frac{3}{2.0 \cdot 1.0} = 1.5$$

$$\tau_{I,inner} = \tau_v = 3 \text{ s}$$

Inner PID: $K_p = 1.5$, $K_i = 0.5$ (= $K_p / \tau_I$), $K_d = 0$

**Inner closed-loop transfer function**:

$$G_{cl,inner}(s) = \frac{C_{inner} G_{flow}}{1 + C_{inner} G_{flow}} \approx \frac{1}{\lambda_{inner} s + 1} = \frac{1}{s + 1}$$

(Approximately first-order with time constant = $\lambda_{inner} = 1$ s)

### Step 2: Outer (Temperature) PID — Tune Second

The outer loop sees the inner closed-loop as part of its plant:

$$G_{outer}(s) = G_{cl,inner}(s) \cdot G_{temp}(s) = \frac{15 \cdot e^{-5s}}{(s + 1)(30s + 1)(10s + 1)}$$

Using SIMC (Skogestad IMC) tuning:

$$\tau_1 = 30, \quad \theta_{eff} = 5 + 10 + 1 = 16 \text{ s (half-rule approximation)}$$

$$K_{c,outer} = \frac{\tau_1}{K_t \cdot (\theta_{eff} + \lambda_{outer})} = \frac{30}{15 \cdot (16 + 16)} = 0.0625$$

$$\tau_{I,outer} = \min(\tau_1, 4(\theta_{eff} + \lambda_{outer})) = \min(30, 128) = 30 \text{ s}$$

Outer PID: $K_p = 0.063$, $K_i = 0.0021$ (= $K_p / \tau_I$), $K_d = 0$

---

## Performance Comparison

### Steam Pressure Disturbance at t = 100s (+20%)

```
  Temperature [°C]
  82│       ╱╲
  81│     ╱╱  ╲╲  ← Single loop (peak deviation = 2.5°C)
  80│── ╱╱──────╲╲────────────── Setpoint
  79│  ╱          ╲
  80│                ╲─────────── Recovery at t ≈ 200s
    │
  80.3│  ╱╲
  80│─╱──╲────────────────────── Cascade (peak = 0.3°C!)
  79.7│
     └────────────────────────── Time [s]
     0   50   100  150  200  250  300
```

| Metric | Single Loop | Cascade |
|---|---|---|
| Peak temperature deviation | 2.5 °C | **0.3 °C** |
| Recovery time (2% band) | 180 s | **40 s** |
| IAE (integral absolute error) | 125 | **12** |

The cascade reduces the disturbance impact by **~10×** because the inner flow loop corrects the steam flow change before it significantly affects temperature.

---

## Implementation Notes

### Mode Handling

```
  Cascade Mode States:
  
  1. MANUAL:    Operator directly controls valve position
                Inner loop: Manual
                Outer loop: Tracking (follows actual temp)
  
  2. AUTO (no cascade):  Inner loop controls flow
                         Outer loop: Off
                         Operator sets flow setpoint
  
  3. CASCADE:   Outer loop controls temperature
                Inner loop receives setpoint from outer
                Operator sets temperature setpoint
  
  Transition: MANUAL → AUTO → CASCADE (always step up)
  Emergency:  CASCADE → MANUAL (immediate)
```

### Anti-Windup

When the inner loop is in Manual mode, the outer loop integrator must be frozen (or the outer loop must track) to prevent windup:

```
  IF inner_loop.mode ≠ CASCADE THEN
      outer_loop.integrator := outer_loop.output  (* freeze *)
      outer_loop.setpoint := actual_temperature    (* track *)
  END_IF
```

⚠️ **Pitfall**: Always test the cascade handoff — switching between manual and cascade can cause bumps if the integral terms aren't properly initialized. Use bumpless transfer on both controllers.

💡 **Insight**: The cascade structure appears everywhere in process control: temperature-flow, pressure-flow, level-flow, speed-current. The pattern is always the same: slow outer variable controlled through a fast inner variable, with the inner loop rejecting disturbances that the outer loop would respond to too slowly.
