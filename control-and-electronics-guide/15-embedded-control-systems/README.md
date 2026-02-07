# 15 — Embedded Control Systems

> *Control algorithms ultimately run on microcontrollers. This section bridges the gap between control theory and embedded implementation — covering MCU architecture, real-time constraints, fixed-point arithmetic, and hardware peripherals essential for control.*

---

## 15.1 Microcontroller Architecture for Control

### Typical Control MCU Block Diagram

```
  ┌─────────────────────────────────────────────────────┐
  │                    Microcontroller                   │
  │                                                     │
  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐           │
  │  │ CPU  │  │ Flash│  │ SRAM │  │ DMA  │           │
  │  │(ARM  │  │(Code)│  │(Data)│  │      │           │
  │  │Cortex│  └──────┘  └──────┘  └──────┘           │
  │  │ M4F) │                                          │
  │  └──┬───┘                                          │
  │     │ AHB/APB Bus                                  │
  │  ┌──┴──┬──────┬──────┬──────┬──────┬──────┐       │
  │  │Timer│ ADC  │ DAC  │ PWM  │UART/ │ GPIO │       │
  │  │     │12-bit│      │      │SPI/  │      │       │
  │  │     │      │      │      │I²C   │      │       │
  │  └─────┴──────┴──────┴──────┴──────┴──────┘       │
  └─────────────────────────────────────────────────────┘
         │       │      │      │       │       │
         ▼       ▼      ▼      ▼       ▼       ▼
       Timing  Sensors Analog  Motor  Comms   I/O
```

### Key Peripherals for Control

| Peripheral | Control Use | Typical Specs |
|---|---|---|
| **ADC** | Read sensors (current, voltage, temp) | 12-bit, 1 MSPS |
| **PWM Timer** | Drive power stage (motor, converter) | 16-bit, up to 100 kHz |
| **DAC** | Analog output reference | 12-bit, 1 MSPS |
| **DMA** | Transfer ADC → memory without CPU | Reduces interrupt load |
| **Quadrature Encoder** | Read position encoders | 32-bit counter |
| **Comparator** | Overcurrent protection | < 100 ns response |
| **Watchdog** | Detect software hangs | Reset on timeout |

---

## 15.2 Real-Time Control Loop

### Interrupt-Driven Architecture

```
          Timer Interrupt (e.g., 10 kHz)
                    │
                    ▼
  ┌──────────────────────────────────────────┐
  │ 1. Read ADC (sensor measurements)        │  ← 2 µs
  │ 2. State estimation / filtering          │  ← 5 µs
  │ 3. Compute control law (PID / FOC)       │  ← 3 µs
  │ 4. Apply output (update PWM duty)        │  ← 1 µs
  │ 5. Log / communicate (if time permits)   │  ← variable
  │ 6. Return from interrupt                 │
  └──────────────────────────────────────────┘
  
  Total: ~11 µs out of 100 µs period = 11% CPU utilization
  
  ├──── Control ISR ────┤       Idle / Background      │
  ╠═════════════════════╬═══════════════════════════════╣
  0                   11 µs                           100 µs
```

### Critical Timing Requirements

| Constraint | Requirement |
|---|---|
| **Jitter** | < 1% of control period |
| **Latency** | ADC sample → PWM update < 1 period |
| **Worst-case execution** | Must complete before next interrupt |
| **Priority** | Control ISR = highest priority |

⚠️ **Pitfall**: Never use `printf`, `malloc`, or floating-point library calls inside a control ISR. They have unbounded execution time and will cause jitter or overruns.

---

## 15.3 Fixed-Point Arithmetic

Many control MCUs lack an FPU, or fixed-point is preferred for deterministic timing.

### Q-Format Notation

$Q_{m.n}$: $m$ integer bits + $n$ fractional bits (plus 1 sign bit)

**Q15 (Q1.15)**: 16-bit signed, 1 integer bit, 15 fractional bits
- Range: $[-1, +1 - 2^{-15}]$
- Resolution: $2^{-15} = 3.05 \times 10^{-5}$

**Q16.16**: 32-bit signed, 16 integer bits, 16 fractional bits
- Range: $[-32768, +32767.99998]$
- Resolution: $2^{-16} = 1.53 \times 10^{-5}$

### Fixed-Point Operations

```c
// Q15 multiplication (result in Q30, shift back to Q15)
int16_t q15_mul(int16_t a, int16_t b) {
    return (int16_t)(((int32_t)a * (int32_t)b) >> 15);
}

// Q16.16 multiplication
int32_t q16_mul(int32_t a, int32_t b) {
    return (int32_t)(((int64_t)a * (int64_t)b) >> 16);
}

// Float to Q15 conversion
int16_t float_to_q15(float x) {
    return (int16_t)(x * 32768.0f);
}
```

See: [examples/fixed-point-pid.c](examples/fixed-point-pid.c)

---

## 15.4 ADC for Control

### Timing Synchronization

For motor control, ADC sampling must be synchronized with PWM:

```
  PWM:    ┌────────┐        ┌────────┐
          │        │        │        │
  ────────┘        └────────┘        └────
          ↑                 ↑
          │ ADC trigger     │ ADC trigger
          │ at PWM center   │ at PWM center
          
  Why center? Current ripple is at average value → accurate measurement
```

### ADC Configuration Checklist

- [ ] Sample rate ≥ 10× control bandwidth
- [ ] Resolution adequate (12-bit = 0.024% FSR)
- [ ] Trigger source = timer (not software!)
- [ ] DMA transfer to avoid CPU intervention
- [ ] Correct voltage reference (internal vs. external)
- [ ] Anti-aliasing filter on analog input

---

## 15.5 RTOS vs. Bare-Metal

| Feature | Bare-Metal | RTOS |
|---|---|---|
| **Latency** | Lowest (direct ISR) | Slightly higher (scheduler overhead) |
| **Determinism** | Best (if careful) | Good (priority-based) |
| **Complexity** | Low for simple systems | Manages complex systems well |
| **Multi-rate loops** | Manual timer management | Tasks with different periods |
| **Best for** | Single fast control loop | Multiple loops + communication |

### Common RTOS for Control

- **FreeRTOS**: Most popular, many MCU ports
- **Zephyr**: Modern, Linux Foundation backed
- **RT-Thread**: Popular in Asia
- **bare-metal + timer ISR**: Often sufficient for single-loop control

See: [examples/rtos-control-tasks.md](examples/rtos-control-tasks.md)

---

## 15.6 Safety Features

| Feature | Purpose | Implementation |
|---|---|---|
| **Watchdog timer** | Detect software hang | Reset if not "kicked" periodically |
| **Hardware fault ISR** | Handle illegal operations | HardFault handler with safe state |
| **PWM emergency stop** | Kill motor drive on fault | Hardware comparator → PWM brake |
| **Stack overflow check** | Detect memory corruption | Canary value at stack boundary |
| **CRC on flash** | Verify code integrity | Boot-time check |

---

## Examples

| File | Description |
|---|---|
| [fixed-point-pid.c](examples/fixed-point-pid.c) | Complete fixed-point PID in C |
| [rtos-control-tasks.md](examples/rtos-control-tasks.md) | Multi-rate control with FreeRTOS |
| [adc-pwm-sync.md](examples/adc-pwm-sync.md) | ADC-PWM synchronization setup |

---

**Previous → [14-robust-and-optimal-control](../14-robust-and-optimal-control/README.md)**  
**Next → [16-industrial-automation](../16-industrial-automation/README.md)**
