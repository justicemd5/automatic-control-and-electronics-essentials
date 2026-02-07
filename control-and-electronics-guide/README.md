# Automatic Control Systems & Electronics — Complete Learning Guide

> **A rigorous, hands-on, self-study repository for mastering control theory, analog & digital electronics, signal processing, and embedded systems.**

---

## Who This Is For

| Audience | Assumed Background |
|---|---|
| Engineering students (EE, ME, CS) | Calculus, linear algebra, basic physics, programming |
| Self-taught engineers | Comfort with math notation and at least one programming language |
| Software engineers → controls/electronics | Strong coding skills, willing to learn the physics and math |
| Practicing EEs broadening scope | Solid analog/digital fundamentals, want deeper control theory |

**This guide does NOT assume prior formal training in control systems or electronics.**  
**This guide does NOT oversimplify.** Every "why" is answered alongside every "how."

---

## Repository Structure

```
control-and-electronics-guide/
│
├── README.md                          ← You are here
│
├── 01-foundations/
│   ├── README.md                      ← What are control systems & electronics?
│   └── examples/
│       ├── open-vs-closed-loop.md
│       ├── block-diagram-basics.md
│       └── common-misconceptions.md
│
├── 02-mathematical-modeling/
│   ├── README.md                      ← DEs, Laplace, Z-transforms, state-space
│   └── examples/
│       ├── mass-spring-damper.md
│       ├── dc-motor-model.py
│       ├── thermal-system-model.md
│       └── rlc-circuit-model.py
│
├── 03-signals-and-systems/
│   ├── README.md                      ← Continuous/discrete signals, Fourier, sampling
│   └── examples/
│       ├── convolution-example.py
│       ├── sampling-aliasing.md
│       ├── fourier-analysis.py
│       └── impulse-response.md
│
├── 04-analog-electronics/
│   ├── README.md                      ← Passives, diodes, transistors, op-amps, filters
│   └── examples/
│       ├── opamp-inverting-amplifier.md
│       ├── rc-filter-analysis.py
│       ├── bjt-common-emitter.md
│       └── mosfet-switching.md
│
├── 05-digital-electronics/
│   ├── README.md                      ← Gates, sequential logic, FSMs, timing, HDL
│   └── examples/
│       ├── fsm-design.md
│       ├── counter-verilog.v
│       ├── combinational-logic.md
│       └── flip-flop-timing.md
│
├── 06-power-electronics/
│   ├── README.md                      ← Rectifiers, converters, inverters, PWM
│   └── examples/
│       ├── buck-converter-analysis.md
│       ├── pwm-control.py
│       ├── full-bridge-rectifier.md
│       └── thermal-design.md
│
├── 07-sensors-and-actuators/
│   ├── README.md                      ← Measurement, calibration, motors, interfacing
│   └── examples/
│       ├── sensor-calibration.md
│       ├── motor-driver-circuit.md
│       ├── thermocouple-interface.md
│       └── encoder-reading.md
│
├── 08-feedback-control-theory/
│   ├── README.md                      ← Feedback, stability, sensitivity, robustness
│   └── examples/
│       ├── feedback-loop-diagram.md
│       ├── sensitivity-analysis.md
│       └── disturbance-rejection.md
│
├── 09-classical-control/
│   ├── README.md                      ← PID, root locus, Bode, Nyquist
│   └── examples/
│       ├── pid-controller-design.py
│       ├── bode-plot-analysis.md
│       ├── root-locus-example.py
│       └── nyquist-stability.md
│
├── 10-modern-control/
│   ├── README.md                      ← State-space, controllability, LQR
│   └── examples/
│       ├── state-feedback-design.py
│       ├── lqr-example.md
│       ├── controllability-check.py
│       └── observability-analysis.md
│
├── 11-digital-control-and-discrete-systems/
│   ├── README.md                      ← Discretization, Z-domain, digital PID
│   └── examples/
│       ├── digital-pid.py
│       ├── discretization-effects.md
│       ├── z-transform-analysis.py
│       └── quantization-effects.md
│
├── 12-state-estimation-and-observers/
│   ├── README.md                      ← Luenberger, Kalman, EKF, UKF, sensor fusion
│   └── examples/
│       ├── kalman-filter.py
│       ├── observer-design.md
│       ├── ekf-example.py
│       └── sensor-fusion.md
│
├── 13-nonlinear-and-adaptive-control/
│   ├── README.md                      ← Lyapunov, feedback linearization, adaptive
│   └── examples/
│       ├── lyapunov-stability.md
│       ├── adaptive-control-example.py
│       ├── feedback-linearization.md
│       └── gain-scheduling.py
│
├── 14-robust-and-optimal-control/
│   ├── README.md                      ← H∞, uncertainty, optimal formulations
│   └── examples/
│       ├── robust-control-intuition.md
│       ├── optimal-control-problem.md
│       ├── h-infinity-example.md
│       └── lqg-design.py
│
├── 15-embedded-and-real-time-systems/
│   ├── README.md                      ← MCUs, RTOS, ADC/DAC, control on hardware
│   └── examples/
│       ├── timer-based-control.c
│       ├── adc-reading.md
│       ├── interrupt-driven-control.c
│       └── rtos-task-scheduling.md
│
├── 16-industrial-automation-and-plc/
│   ├── README.md                      ← PLC, ladder logic, SCADA, fieldbus
│   └── examples/
│       ├── ladder-logic-example.md
│       ├── plc-control-loop.md
│       ├── scada-architecture.md
│       └── function-block-diagram.md
│
├── 17-robotics-and-mechatronics/
│   ├── README.md                      ← Kinematics, dynamics, trajectory, integration
│   └── examples/
│       ├── robotic-arm-kinematics.md
│       ├── trajectory-planning.py
│       ├── pid-motor-control.md
│       └── inverse-kinematics.py
│
├── 18-communication-and-control-interfaces/
│   ├── README.md                      ← Serial, fieldbuses, networked control
│   └── examples/
│       ├── can-bus-overview.md
│       ├── modbus-communication.md
│       ├── spi-i2c-comparison.md
│       └── ethernet-ip-basics.md
│
├── 19-safety-reliability-and-standards/
│   ├── README.md                      ← Fault detection, redundancy, IEC/ISO
│   └── examples/
│       ├── safety-analysis.md
│       ├── fault-tree.md
│       ├── sil-determination.md
│       └── fmea-example.md
│
├── 20-advanced-and-emerging-topics/
│   ├── README.md                      ← MPC, digital twins, CPS, AI control, HIL
│   └── examples/
│       ├── mpc-example.py
│       ├── hil-testing.md
│       ├── digital-twin-concept.md
│       └── reinforcement-learning-control.md
│
└── appendix/
    ├── README.md                      ← Math refresher, symbols, references
    ├── laplace-transform-table.md
    ├── z-transform-table.md
    ├── complex-numbers-refresher.md
    └── linear-algebra-essentials.md
```

---

## How to Use This Guide

### Sequential Study (Recommended for Beginners)
1. Start at **01-foundations** and work through each numbered section.
2. Read the section `README.md` first — it contains the theory.
3. Then study each example in the `examples/` subdirectory.
4. Run the `.py` files, compile the `.c` and `.v` files, and work through the `.md` examples on paper.

### Reference Mode (For Practicing Engineers)
- Jump directly to the section you need.
- Each section is self-contained with cross-references where dependencies exist.

### Hands-On Mode
- Every section has runnable code or detailed worked examples.
- Python examples use `numpy`, `scipy`, and `matplotlib` — install with:
  ```bash
  pip install numpy scipy matplotlib control
  ```
- C examples target ARM Cortex-M or generic embedded platforms.
- Verilog examples can be simulated with Icarus Verilog or any HDL simulator.

---

## Conventions Used Throughout

| Convention | Meaning |
|---|---|
| $s$ | Laplace-domain complex variable |
| $z$ | Z-domain complex variable |
| $G(s)$, $H(s)$ | Transfer functions (plant, controller/sensor) |
| $\mathbf{x}$, $\mathbf{u}$, $\mathbf{y}$ | State, input, output vectors |
| $\mathbf{A}, \mathbf{B}, \mathbf{C}, \mathbf{D}$ | State-space matrices |
| Block diagrams | Mermaid format (render with any Mermaid-compatible viewer) |
| `⚠️ Pitfall` | Common mistake or misconception |
| `💡 Insight` | Physical or mathematical intuition worth remembering |
| `🔧 Practical` | Industry-relevant engineering tip |

---

## Core Philosophy

1. **Mathematics is the language** — we don't shy away from it, but we always explain what the math *means physically*.
2. **Every diagram earns its place** — diagrams show signal flow, energy flow, or system structure; never decoration.
3. **Every example lives in its own file** — so you can study, modify, and run it independently.
4. **Why before How** — understanding *why* a technique works prevents cargo-cult engineering.
5. **Trade-offs are explicit** — real engineering is about choosing among imperfect options.

---

## Prerequisites Checklist

Before beginning, you should be comfortable with:

- [ ] **Calculus**: Derivatives, integrals, differential equations
- [ ] **Linear Algebra**: Matrices, eigenvalues, vector spaces
- [ ] **Complex Numbers**: Euler's formula, magnitude, phase
- [ ] **Basic Physics**: Newton's laws, Kirchhoff's laws, energy conservation
- [ ] **Programming**: At least one language (Python recommended)

If any of these feel rusty, start with the **appendix/** refresher materials.

---

## Dependencies & Tools

| Tool | Purpose | Install |
|---|---|---|
| Python 3.8+ | Simulations, plotting | `python.org` or system package manager |
| NumPy | Numerical computation | `pip install numpy` |
| SciPy | Signal processing, integration | `pip install scipy` |
| Matplotlib | Plotting | `pip install matplotlib` |
| python-control | Control systems toolbox | `pip install control` |
| GCC/ARM-GCC | Embedded C compilation | System package manager |
| Icarus Verilog | HDL simulation (optional) | `apt install iverilog` |

---

## License & Attribution

This guide is provided for educational purposes. All examples are original or based on standard textbook formulations with proper attribution where applicable. Feel free to clone, study, and extend.

---

*"The best way to understand control systems is to close the loop between theory and practice."*

**Begin your journey → [01-foundations/README.md](01-foundations/README.md)**
