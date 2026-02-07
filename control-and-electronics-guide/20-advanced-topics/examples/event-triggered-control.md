# Example: Event-Triggered vs. Periodic Control

## Purpose
Compare periodic (time-triggered) control with event-triggered control, showing how event-triggered approaches reduce communication while maintaining performance.

---

## System: Networked Temperature Control

```
  Sensor ────── Network ────── Controller ────── Heater
  (remote)    (WiFi/Ethernet)   (central)        (remote)
  
  Challenge: Network bandwidth is limited, shared with other devices
  Goal: Maintain temperature control while minimizing network packets
```

Plant: First-order thermal system with delay

$$G(s) = \frac{2.0}{30s + 1} e^{-3s}$$

(Gain = 2 °C/W, time constant = 30 s, delay = 3 s)

---

## Approach 1: Periodic Control (Baseline)

Sample every $T_s = 1$ s, send measurement to controller, receive command.

```
  Packets/second: 2 (1 measurement + 1 command)
  
  Time: ──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──┼──
          ↑  ↑  ↑  ↑  ↑  ↑  ↑  ↑  ↑  ↑  ↑  ↑  ↑  ↑  ↑
         (send measurement, receive command — every 1 s)
```

Over 1 hour: $2 \times 3600 = 7200$ packets

---

## Approach 2: Event-Triggered Control

Send measurement **only when** the temperature deviates significantly from the last sent value:

$$\text{Send if } |T(t) - T(t_{last\_sent})| > \delta$$

Where $\delta = 0.3$ °C (triggering threshold).

Between events, the controller uses the **last received measurement** (zero-order hold).

```
  Time: ──┼─────────┼──┼──┼─────────────────┼──────────────
          ↑         ↑  ↑  ↑                 ↑
         (send only when temperature changes by > 0.3°C)
```

---

## Performance Comparison

### Step Response (Setpoint Change: 20°C → 25°C)

```
  Temperature [°C]
  26│        ╱───────────── Periodic (slight overshoot)
  25│── ──╱╱─────╱───────── Event-triggered (similar tracking)
  24│   ╱╱    ╱╱
  23│  ╱╱   ╱╱
  22│ ╱╱  ╱╱
  21│╱╱ ╱╱
  20│╱╱╱
     └────────────────────── Time [s]
     0   30   60   90  120  150
```

| Metric | Periodic ($T_s = 1$ s) | Event-Triggered ($\delta = 0.3$ °C) |
|---|---|---|
| Rise time | 42 s | 44 s (+5%) |
| Overshoot | 8% | 10% |
| Settling (2%) | 95 s | 102 s (+7%) |
| Steady-state error | 0.0°C | < 0.3°C (bounded by δ) |
| **Packets (300 s sim)** | **600** | **87** |
| **Bandwidth savings** | Baseline | **85% reduction** |

---

## Triggering Analysis

### When Do Events Occur?

```
  Setpoint change at t=0:
  
  Temperature:  ╱──────────────────────────────
               ╱
              ╱
             ╱
  ──────────╱
  
  Events:    ▲▲▲▲▲▲▲▲▲▲▲          ▲    ▲         ▲
             └──── Dense ─────┘ └── Sparse (steady state) ──┘
  
  During transient: Many events (large temperature changes)
  During steady state: Very few events (temperature stable)
```

This is the key advantage: **communication resources are automatically allocated where they're needed** — during transients, not during steady state.

---

## Design Considerations

### Choosing δ (Triggering Threshold)

| δ | Events | Performance | Steady-State Error |
|---|---|---|---|
| 0.1 °C | Many (~250) | Nearly identical to periodic | < 0.1 °C |
| 0.3 °C | Moderate (~87) | Slight degradation | < 0.3 °C |
| 1.0 °C | Few (~30) | Noticeable oscillation | < 1.0 °C |
| 3.0 °C | Very few (~10) | Poor tracking | < 3.0 °C |

**Guideline**: Set $\delta$ to ~5-10% of the typical setpoint change.

### Minimum Inter-Event Time

To prevent "Zeno behavior" (infinite events in finite time due to noise):

$$t_{k+1} - t_k \geq \tau_{min}$$

Typical: $\tau_{min} = 0.1 \times T_s$ (10% of nominal sample time)

---

## Implementation

### Sensor Side (Edge Device)

```
  last_sent_value = read_temperature()
  send(last_sent_value)
  
  loop:
      current_value = read_temperature()
      
      if |current_value - last_sent_value| > delta:
          send(current_value)
          last_sent_value = current_value
          
      if time_since_last_send > max_interval:
          send(current_value)             # Heartbeat
          last_sent_value = current_value
          
      sleep(check_interval)              # Check at faster rate than Ts
```

### Controller Side

```
  last_measurement = 0
  last_command = 0
  
  on_receive(measurement):
      last_measurement = measurement
      
  periodic_control(Ts):                   # Controller runs periodically
      error = setpoint - last_measurement
      command = PID_update(error)
      if command != last_command:          # Optional: event-triggered output
          send(command)
          last_command = command
```

### Heartbeat Mechanism

Even if no events occur, send a measurement every $T_{max}$ (e.g., 30 s):

- Confirms the sensor is alive
- Prevents stale data in the controller
- Required for safety (detect communication loss)

---

## Stability Guarantee

For event-triggered control with the triggering condition:

$$\|e_s(t)\| \leq \sigma \|e(t)\| + \delta$$

Where $e_s$ is the sampling error and $e$ is the control error, the closed-loop system is **Input-to-State Stable (ISS)** with ultimate bound proportional to $\delta$.

This means:
- The system converges to a neighborhood of the setpoint
- The neighborhood size is determined by $\delta$
- Smaller $\delta$ → better performance, more events

💡 **Insight**: Event-triggered control is especially valuable for: (1) battery-powered wireless sensors (saves energy), (2) shared networks with many devices (reduces congestion), (3) multi-agent systems (scales better than periodic polling). It's a natural fit for IoT and Industry 4.0 applications.

⚠️ **Pitfall**: Event-triggered control complicates stability analysis because the sampling is no longer uniform. Classical discrete-time stability tools (Z-transform, etc.) don't directly apply. Use Lyapunov-based analysis or ISS theory instead.
