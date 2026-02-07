# Example: Multi-Point Sensor Calibration

## Purpose
Demonstrate how to calibrate a sensor using known reference standards, fit a calibration curve, and quantify accuracy. We use an NTC thermistor as the case study.

---

## The Calibration Problem

A raw sensor reading (voltage, resistance, counts) must be mapped to a physical quantity (temperature, pressure, force). This mapping is the **calibration function**.

```
  Physical     Sensor      Raw         Calibration     Engineering
  Quantity  →  Element  →  Signal   →   Function    →   Value
  (T, P, F)              (V, R, N)    y = f(x)       (°C, Pa, N)
```

---

## NTC Thermistor Calibration

### Steinhart-Hart Equation (Theoretical Model)

$$\frac{1}{T} = A + B \ln(R) + C [\ln(R)]^3$$

Where $T$ is in Kelvin, $R$ is resistance in Ohms, and $A, B, C$ are device-specific coefficients.

### Calibration Data

Measurements taken with the thermistor in a calibration bath alongside a reference Pt100 RTD:

| Reference T [°C] | Measured R [Ω] | $\ln(R)$ |
|---|---|---|
| 0.0 | 32,650 | 10.394 |
| 10.0 | 19,900 | 9.898 |
| 20.0 | 12,490 | 9.433 |
| 25.0 | 10,000 | 9.210 |
| 30.0 | 8,057 | 8.994 |
| 40.0 | 5,326 | 8.580 |
| 50.0 | 3,602 | 8.189 |
| 60.0 | 2,488 | 7.819 |
| 70.0 | 1,752 | 7.469 |
| 80.0 | 1,258 | 7.137 |
| 90.0 | 919 | 6.824 |
| 100.0 | 682 | 6.526 |

### Step 1: Fit Steinhart-Hart Coefficients

Using three calibration points (0°C, 50°C, 100°C) to solve 3 equations for 3 unknowns:

$$\frac{1}{T_1} = A + B \ln(R_1) + C[\ln(R_1)]^3$$
$$\frac{1}{T_2} = A + B \ln(R_2) + C[\ln(R_2)]^3$$
$$\frac{1}{T_3} = A + B \ln(R_3) + C[\ln(R_3)]^3$$

Solving the system:

$$A = 1.125 \times 10^{-3}, \quad B = 2.347 \times 10^{-4}, \quad C = 0.856 \times 10^{-7}$$

### Step 2: Verify Against All Data Points

| Reference T [°C] | Calculated T [°C] | Error [°C] |
|---|---|---|
| 0.0 | 0.02 | +0.02 |
| 10.0 | 10.08 | +0.08 |
| 20.0 | 19.95 | −0.05 |
| 25.0 | 25.00 | 0.00 |
| 30.0 | 30.03 | +0.03 |
| 40.0 | 39.92 | −0.08 |
| 50.0 | 50.00 | 0.00 |
| 60.0 | 60.07 | +0.07 |
| 70.0 | 69.95 | −0.05 |
| 80.0 | 80.04 | +0.04 |
| 90.0 | 89.93 | −0.07 |
| 100.0 | 100.00 | 0.00 |

Maximum error: ±0.08°C — excellent!

---

## Alternative: Polynomial Calibration

For sensors with a simpler response, a polynomial fit suffices:

$$T = a_0 + a_1 V + a_2 V^2 + a_3 V^3$$

### When to Use Each Method

| Method | Best For | Accuracy | Complexity |
|---|---|---|---|
| Steinhart-Hart | NTC thermistors | Very high | Medium |
| Linear 2-point | Linear sensors (RTD, LM35) | Good | Low |
| Polynomial | Any sensor, moderate accuracy | Good | Low |
| Lookup table + interpolation | Highly nonlinear sensors | High | Low (CPU) |
| Neural network | Complex multi-input sensors | Highest | High |

---

## Calibration Best Practices

1. **Use traceable references**: Calibrate against NIST-traceable standards
2. **Cover the full range**: Include points near both extremes
3. **Include midpoints**: At least 5 points for nonlinear sensors
4. **Ascending and descending**: Check for hysteresis
5. **Environmental conditions**: Note ambient temperature, humidity
6. **Recalibrate periodically**: Sensors drift over time (6–12 month intervals)
7. **Record uncertainty**: Every calibration has an associated uncertainty budget

🔧 **Practical**: In production, a 2-point calibration (offset + gain) at the factory is common. Higher-accuracy applications use multi-point calibration stored in EEPROM on the sensor PCB.
