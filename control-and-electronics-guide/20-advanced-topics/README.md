# 20 — Advanced Topics

> *This final section surveys cutting-edge areas where control theory meets modern computing: Model Predictive Control, machine learning for control, networked control systems, and emerging paradigms that are reshaping the field.*

---

## 20.1 Model Predictive Control (MPC)

### The MPC Concept

At each time step, solve an optimization problem over a prediction horizon:

$$\min_{u_0, \ldots, u_{N-1}} \sum_{k=0}^{N-1} \left( x_k^T Q x_k + u_k^T R u_k \right) + x_N^T P x_N$$

Subject to:
- $x_{k+1} = A x_k + B u_k$ (system dynamics)
- $u_{\min} \leq u_k \leq u_{\max}$ (actuator constraints)
- $x_{\min} \leq x_k \leq x_{\max}$ (state constraints)

Apply only the **first** control action $u_0$, then repeat next time step.

```
  ┌──────── Prediction Horizon N ────────┐
  │                                       │
  Past     │ Now    Future (predicted)     │
  ─────────┤────────────────────────────── │─── Time
           │  u₀  u₁  u₂  u₃  ...  u_{N-1}
           │   ↓
           │ Apply only u₀, then re-solve
           │
  Measured │ Predicted trajectory
  state    │ (from model)
```

### MPC vs. Classical Control

| Feature | PID / LQR | MPC |
|---|---|---|
| Constraints | Not directly handled | **Explicitly handled** |
| Preview | No | Yes (uses future reference) |
| Multi-variable | Separate loops | **Natural MIMO** |
| Computation | Negligible | **Significant** (QP solver) |
| Tuning | Gains | Weights Q, R + horizon N |
| Optimality | None / quadratic cost | **Optimal within horizon** |

### Where MPC Excels

- Chemical processes (constraints are critical: temperatures, pressures)
- Autonomous driving (obstacle avoidance as constraints)
- Building HVAC (energy optimization with comfort constraints)
- Power electronics (fast MPC at > 100 kHz now feasible)

See: [examples/mpc-double-integrator.py](examples/mpc-double-integrator.py)

---

## 20.2 Machine Learning in Control

### Approaches

| Approach | Description | Maturity |
|---|---|---|
| **Reinforcement Learning (RL)** | Agent learns control policy by trial and error | Research → early industry |
| **Neural Network Models** | Learn plant dynamics from data | Active research |
| **Gaussian Process (GP)** | Probabilistic model learning with uncertainty | Research |
| **System Identification + ML** | Data-driven model for classical controller | Established |
| **Neural Network Controller** | Replace PID with NN | Niche applications |

### RL for Control

```
  ┌─────────┐    action a    ┌────────────┐
  │  Agent  │────────────────►│Environment │
  │  (NN    │◄────────────────│ (Plant)    │
  │ policy) │  state s,       │            │
  │         │  reward r       │            │
  └─────────┘                 └────────────┘
  
  Policy: π(s) → a    (maps state to action)
  Goal:   Maximize Σ γ^t · r_t   (discounted future reward)
  
  Training: Millions of simulated episodes
  Deploy:   Run trained policy in real-time (just a forward pass)
```

### Challenges

⚠️ **Safety**: RL has no inherent safety guarantees during training or deployment. A robot learning to walk might fall thousands of times.

⚠️ **Sim-to-real gap**: Policies trained in simulation often fail in reality due to modeling errors.

⚠️ **Sample efficiency**: Model-free RL requires millions of interactions — impractical for real hardware.

💡 **Insight**: The most practical ML-for-control approach today is to use ML for the *model* (system identification), then use a proven controller (MPC, PID) on top. This preserves safety guarantees while leveraging ML's ability to learn complex dynamics.

---

## 20.3 Networked Control Systems

### Challenges of Control Over Networks

```
  Sensor ──── Network (Ethernet, WiFi, 5G) ──── Controller ──── Actuator
                    │
              ┌─────┴─────┐
              │ Delays     │
              │ Packet loss│
              │ Jitter     │
              │ Bandwidth  │
              └────────────┘
```

| Challenge | Effect | Mitigation |
|---|---|---|
| Variable delay | Phase margin reduction | Smith predictor, delay compensation |
| Packet loss | Missing sensor data | Hold last value, Kalman prediction |
| Jitter | Varying sample time | Timestamped data, jitter buffer |
| Bandwidth | Limited update rate | Event-triggered control |
| Security | Cyber attacks | Encryption, authentication |

### Event-Triggered Control

Instead of periodic sampling, send data only when "something happens":

$$\text{Send if } \|x(t) - x(t_{last})\| > \delta$$

```
  Periodic:    │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │    (16 transmissions)
               ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲
  
  Event-       │         │   │ │       │         │    (6 transmissions)
  triggered:   ▲         ▲   ▲ ▲       ▲         ▲
                          ↑   ↑         ↑
                     (state changed significantly)
  
  → 60% reduction in network traffic with similar control performance
```

---

## 20.4 Digital Twins

A **digital twin** is a real-time simulation model that mirrors a physical system:

```
  Physical System          │        Digital Twin
  ┌──────────────┐         │        ┌──────────────┐
  │   Sensors    │─── data ┼───────►│   Simulation │
  │   Actuators  │◄── cmd ─┼────────│   Model      │
  │              │         │        │              │
  └──────────────┘         │        └──────┬───────┘
                           │               │
                           │        ┌──────▼───────┐
                           │        │ Diagnostics  │
                           │        │ Optimization │
                           │        │ What-if      │
                           │        └──────────────┘
```

### Applications

- **Predictive maintenance**: Model predicts bearing failure 2 weeks ahead
- **Virtual commissioning**: Test control software before hardware exists
- **Optimization**: Simulate parameter changes before applying to real plant
- **Anomaly detection**: Deviation between twin and reality = fault

---

## 20.5 Emerging Areas

### Quantum Control
- Controlling quantum systems (quantum computing, quantum sensors)
- Dealing with measurement backaction and decoherence
- Open-loop pulse sequences designed via optimal control

### Distributed and Multi-Agent Control
- Swarm robotics (consensus algorithms)
- Microgrids (distributed energy resource coordination)
- Autonomous vehicle platoons

### Edge Computing for Control
- Run complex algorithms (ML, MPC) on edge devices
- FPGA-based control for nanosecond response
- Hardware-in-the-loop (HIL) simulation

---

## Examples

| File | Description |
|---|---|
| [mpc-double-integrator.py](examples/mpc-double-integrator.py) | Basic MPC with constraints |
| [event-triggered-control.md](examples/event-triggered-control.md) | Event-triggered vs. periodic comparison |
| [ml-system-id.md](examples/ml-system-id.md) | Neural network for system identification |

---

**Previous → [19-safety-and-reliability](../19-safety-and-reliability/README.md)**  
**Next → [appendix](../appendix/README.md)**
