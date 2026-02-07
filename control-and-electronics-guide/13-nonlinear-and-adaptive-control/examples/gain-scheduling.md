# Example: Gain-Scheduled PID for Variable-Speed Motor

## Purpose
Design a gain-scheduled PID controller for a DC motor whose dynamics change significantly with speed, demonstrating the practical approach to nonlinear control.

---

## The Problem

A DC motor's transfer function changes with operating speed due to back-EMF effects:

$$G(s, \omega_0) = \frac{K(\omega_0)}{s + a(\omega_0)}$$

At different speeds:

| Operating Point $\omega_0$ | $K$ | $a$ | $\tau = 1/a$ | Character |
|---|---|---|---|---|
| Low (100 RPM) | 5.0 | 2.0 | 0.50 s | Slow, high gain |
| Medium (500 RPM) | 3.0 | 5.0 | 0.20 s | Moderate |
| High (1000 RPM) | 1.5 | 10.0 | 0.10 s | Fast, low gain |

A single PID tuned at one operating point will perform poorly at others.

---

## Design: PID at Each Operating Point

### Low Speed (100 RPM)

Plant: $G(s) = \frac{5}{s+2}$

Design for PM = 50°, bandwidth $\omega_c = 10$ rad/s:

$$K_p = 3.0, \quad K_i = 6.0, \quad K_d = 0.15$$

### Medium Speed (500 RPM)

Plant: $G(s) = \frac{3}{s+5}$

$$K_p = 5.5, \quad K_i = 15.0, \quad K_d = 0.10$$

### High Speed (1000 RPM)

Plant: $G(s) = \frac{1.5}{s+10}$

$$K_p = 12.0, \quad K_i = 40.0, \quad K_d = 0.05$$

---

## Gain Schedule Implementation

### Lookup Table with Linear Interpolation

```
  Speed [RPM]:    100    250    500    750    1000
  Kp:             3.0    4.2    5.5    8.5    12.0
  Ki:             6.0    10.5   15.0   27.0   40.0
  Kd:             0.15   0.12   0.10   0.07   0.05
```

```
  Kp
  12 │                              ╱●
  10 │                         ╱╱
   8 │                    ●╱╱
   6 │              ●╱╱
   4 │         ●╱╱
   2 │    ●╱╱
     └───────────────────────────── Speed [RPM]
      100  250  500  750  1000
```

### Pseudocode

```
function get_pid_gains(speed_rpm):
    // Lookup table
    speeds = [100, 250, 500, 750, 1000]
    Kp_table = [3.0, 4.2, 5.5, 8.5, 12.0]
    Ki_table = [6.0, 10.5, 15.0, 27.0, 40.0]
    Kd_table = [0.15, 0.12, 0.10, 0.07, 0.05]
    
    // Linear interpolation
    Kp = interpolate(speeds, Kp_table, speed_rpm)
    Ki = interpolate(speeds, Ki_table, speed_rpm)
    Kd = interpolate(speeds, Kd_table, speed_rpm)
    
    return Kp, Ki, Kd
```

---

## Performance Comparison

### Without Gain Scheduling (Fixed PID at Medium Speed)

| Speed | Overshoot | Settling Time | Steady-State | Quality |
|---|---|---|---|---|
| Low (100 RPM) | 35% | 1.2 s | OK | Poor (too aggressive) |
| Medium (500 RPM) | 12% | 0.4 s | 0% error | Good (design point) |
| High (1000 RPM) | 5% | 0.8 s | Slow | Poor (too conservative) |

### With Gain Scheduling

| Speed | Overshoot | Settling Time | Steady-State | Quality |
|---|---|---|---|---|
| Low (100 RPM) | 12% | 0.5 s | 0% error | Good |
| Medium (500 RPM) | 12% | 0.4 s | 0% error | Good |
| High (1000 RPM) | 10% | 0.3 s | 0% error | Good |

---

## Implementation Considerations

### 1. Scheduling Variable Selection

The scheduling variable must:
- Be measurable in real-time
- Vary slowly compared to control loop bandwidth
- Capture the dominant parameter variation

Common scheduling variables:

| Application | Scheduling Variable |
|---|---|
| Motor control | Speed, current |
| Aircraft | Altitude, Mach number |
| Chemical process | Flow rate, temperature |
| Automotive engine | RPM, throttle position |

### 2. Bumpless Transfer

When gains change, the integral term must be adjusted to prevent output jumps:

$$I_{new} = I_{old} + (K_{p,old} - K_{p,new}) \cdot e$$

### 3. Rate of Change Limiting

If the scheduling variable changes rapidly, limit the rate of gain change:

$$K_p(t) = K_p(t - T_s) + \text{clamp}\left(\Delta K_p, -\Delta K_{max}, +\Delta K_{max}\right)$$

⚠️ **Pitfall**: Gain scheduling has no stability guarantee during transitions between operating points. If the scheduling variable changes faster than the control dynamics, the controller may destabilize. Always test transitions in simulation.

💡 **Insight**: Despite being theoretically less elegant than adaptive control, gain scheduling is overwhelmingly preferred in industry because: (1) it's simple to understand and implement, (2) stability at each operating point is verified at design time, (3) it doesn't require persistent excitation, and (4) it's easy to certify for safety-critical systems.
