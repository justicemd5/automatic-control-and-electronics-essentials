# Example: Thermal System Model

## Purpose

Derive the mathematical model of a simple thermal system using the thermal-electrical analogy. This example demonstrates how energy conservation leads to the same mathematical structures as electrical circuits.

---

## Physical System: Heated Room with Insulation

```
  Outside                    Wall                    Room
  T_out(t)     R_wall       (thermal              T_room(t)
  ───────── ──/\/\/\/── resistance) ──┬── C_room (thermal
                                      │    capacitance)
                                      │
                                  Q_heater(t)
                                  (heat input)
```

**Equivalent electrical circuit:**

```
  T_out ──── R_wall ────┬──── T_room
                        │
                     C_room
                        │
                       GND
                    (+ Q_heater current source)
```

---

## Parameters

| Symbol | Description | Units | Typical Value |
|---|---|---|---|
| $C_{room}$ | Thermal capacitance of room air + furniture | J/°C | 500,000 |
| $R_{wall}$ | Thermal resistance of walls/insulation | °C/W | 0.01 |
| $T_{out}$ | Outside temperature | °C | Variable |
| $T_{room}$ | Room temperature (state variable) | °C | To be controlled |
| $Q_{heater}$ | Heater power input | W | 0–5000 |

---

## Derivation

### Energy Conservation

Rate of energy storage = Heat in − Heat out

$$C_{room} \frac{dT_{room}}{dt} = Q_{heater}(t) - \frac{T_{room}(t) - T_{out}(t)}{R_{wall}}$$

### Rearranged

$$C_{room} \frac{dT_{room}}{dt} + \frac{1}{R_{wall}} T_{room}(t) = Q_{heater}(t) + \frac{T_{out}(t)}{R_{wall}}$$

This is a **first-order linear ODE** — the thermal equivalent of an RC circuit.

---

## Transfer Function

Taking Laplace transform (zero ICs, constant $T_{out}$):

$$C_{room} s \cdot T_{room}(s) + \frac{1}{R_{wall}} T_{room}(s) = Q_{heater}(s) + \frac{T_{out}}{R_{wall} \cdot s}$$

**From heater to room temperature** (with $T_{out} = 0$ for the transfer function):

$$\frac{T_{room}(s)}{Q_{heater}(s)} = \frac{R_{wall}}{R_{wall} C_{room} s + 1} = \frac{R_{wall}}{\tau s + 1}$$

Where the **thermal time constant** is:

$$\tau = R_{wall} \cdot C_{room}$$

### Numerical Values

$$\tau = 0.01 \times 500{,}000 = 5{,}000 \text{ seconds} \approx 83 \text{ minutes}$$

💡 **Insight**: This is why rooms heat up slowly — the thermal time constant is enormous compared to electrical time constants (microseconds to milliseconds).

---

## State-Space Model

**State**: $x = T_{room}$  
**Input**: $u = Q_{heater}$  
**Disturbance**: $d = T_{out}$  

$$\dot{x} = -\frac{1}{R_{wall} C_{room}} x + \frac{1}{C_{room}} u + \frac{1}{R_{wall} C_{room}} d$$

$$y = x$$

Matrices:

$$A = -\frac{1}{\tau}, \quad B = \frac{1}{C_{room}}, \quad B_d = \frac{1}{\tau}, \quad C = 1, \quad D = 0$$

---

## Multi-Room Extension

For two rooms with a shared wall:

```
  T_out ── R_ext ──┬── T₁ ── R_int ──┬── T₂ ── R_ext ── T_out
                   │                  │
                 C₁(T₁)            C₂(T₂)
                   │                  │
                Q₁(heater)        Q₂(heater)
```

This gives a **second-order system** (two state variables):

$$C_1 \dot{T}_1 = Q_1 - \frac{T_1 - T_{out}}{R_{ext}} - \frac{T_1 - T_2}{R_{int}}$$

$$C_2 \dot{T}_2 = Q_2 - \frac{T_2 - T_{out}}{R_{ext}} - \frac{T_2 - T_1}{R_{int}}$$

State-space form with $\mathbf{x} = [T_1, T_2]^T$:

$$\mathbf{A} = \begin{bmatrix} -\frac{1}{C_1}\left(\frac{1}{R_{ext}} + \frac{1}{R_{int}}\right) & \frac{1}{C_1 R_{int}} \\ \frac{1}{C_2 R_{int}} & -\frac{1}{C_2}\left(\frac{1}{R_{ext}} + \frac{1}{R_{int}}\right) \end{bmatrix}$$

---

## Steady-State Analysis

At steady state ($\dot{T}_{room} = 0$):

$$T_{room,ss} = R_{wall} \cdot Q_{heater} + T_{out}$$

**Example**: With $Q_{heater} = 2000$ W, $R_{wall} = 0.01$ °C/W, $T_{out} = 0°C$:

$$T_{room,ss} = 0.01 \times 2000 + 0 = 20°C$$

To maintain 22°C when it's -10°C outside:

$$Q_{needed} = \frac{T_{room} - T_{out}}{R_{wall}} = \frac{22 - (-10)}{0.01} = 3200 \text{ W}$$

---

## Step Response (Heater Turned On)

Starting from $T_{room}(0) = T_{out}$, with constant heater power $Q_0$:

$$T_{room}(t) = T_{out} + R_{wall} \cdot Q_0 \left(1 - e^{-t/\tau}\right)$$

```
  Temperature
  T_out + R·Q ├──────────────────────────── asymptote
              │           ╱─────────────
              │         ╱
              │       ╱
              │     ╱    63.2% reached at t = τ
              │   ╱
              │  ╱
  T_out       ├╱
              └─────┬─────┬─────┬──────── Time
                    τ    2τ    3τ
                         98.2% at 4τ
```

---

## Key Engineering Insights

1. **Better insulation** (larger $R_{wall}$) reduces steady-state heating power but increases time constant
2. **Thermal mass** (larger $C_{room}$) increases time constant but provides disturbance rejection (temperature changes slowly)
3. The **trade-off**: Fast response vs. disturbance rejection is fundamental — it appears in every domain

🔧 **Practical**: Building thermal models are used in HVAC design, data center cooling, and electronic device thermal management. The same math applies whether you're modeling a room, a CPU package, or a chemical reactor.
