# 16 — Industrial Automation

> *Industrial automation applies control theory at scale — managing entire factories, chemical plants, and power systems. This section covers PLCs, SCADA, industrial communication, and the control hierarchy from field devices to enterprise systems.*

---

## 16.1 Automation Hierarchy (ISA-95)

```
  Level 4 │ Enterprise  │ ERP (SAP, Oracle)     │ Days-Months
  ────────┤             │ Business planning      │
  Level 3 │ Operations  │ MES, Batch mgmt       │ Hours-Days
  ────────┤             │ Production scheduling  │
  Level 2 │ Supervisory │ SCADA / HMI           │ Seconds-Hours
  ────────┤             │ Operator interface     │
  Level 1 │ Control     │ PLC / DCS / PID loops  │ ms-Seconds
  ────────┤             │ Real-time control      │
  Level 0 │ Field       │ Sensors & Actuators    │ µs-ms
          │             │ Valves, motors, meters │
```

---

## 16.2 Programmable Logic Controllers (PLCs)

### PLC Architecture

```
  ┌────────────────────────────────────────────────┐
  │                   PLC Rack                     │
  │                                                │
  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐      │
  │  │ CPU  │  │  DI  │  │  DO  │  │  AI  │ ...  │
  │  │Module│  │Module │  │Module│  │Module│      │
  │  │      │  │16ch   │  │16ch  │  │8ch   │      │
  │  │      │  │24VDC  │  │24VDC │  │4-20mA│      │
  │  └──┬───┘  └──┬───┘  └──┬───┘  └──┬───┘      │
  │     └──────┴───┴────┴───┴──────┴───┘           │
  │              Backplane Bus                     │
  └────────────────────────────────────────────────┘
        │              │              │
    Programming    Field Wiring    Network
    (Ethernet)     (Sensors/       (to SCADA)
                    Actuators)
```

### I/O Types

| Type | Signal | Example | PLC Module |
|---|---|---|---|
| Digital Input | ON/OFF (24V) | Limit switch, proximity sensor | DI |
| Digital Output | ON/OFF (24V) | Solenoid, indicator lamp | DO |
| Analog Input | 4-20 mA or 0-10V | Pressure transmitter, RTD | AI |
| Analog Output | 4-20 mA or 0-10V | Control valve, VFD speed ref | AO |

### The 4-20 mA Standard

```
  Current [mA]
  20 │───────────────────────● 100% (full scale)
     │                    ╱╱
  12 │──────────────●╱╱╱     50%
     │           ╱╱╱
   4 │──────●╱╱╱               0% (zero / live zero)
     │
   0 │  ← Wire broken (fault detection!)
     └────────────────────────── Process Variable
     
  Why 4 mA (not 0 mA) for zero?
  → A broken wire reads 0 mA, clearly distinguishable from "zero reading"
  → Sensor can be powered over the same 2 wires (loop-powered)
```

💡 **Insight**: The 4-20 mA standard is one of the most successful interface standards in engineering. It provides: (1) noise immunity (current loop is resistant to voltage drops), (2) fault detection (0 mA = wire break), (3) long distance (up to 1 km), and (4) 2-wire power + signal.

---

## 16.3 PLC Programming Languages (IEC 61131-3)

| Language | Type | Best For |
|---|---|---|
| **Ladder Diagram (LD)** | Graphical | Boolean logic, interlocks |
| **Function Block Diagram (FBD)** | Graphical | Continuous control, PID |
| **Structured Text (ST)** | Textual | Complex algorithms, math |
| **Instruction List (IL)** | Textual | Low-level (deprecated) |
| **Sequential Function Chart (SFC)** | Graphical | Sequential processes, batches |

See: [examples/ladder-logic.md](examples/ladder-logic.md)

---

## 16.4 SCADA Systems

**Supervisory Control And Data Acquisition**

```
  ┌──────────────────────────────────────────┐
  │              SCADA Server                 │
  │  ┌────────┐  ┌────────┐  ┌────────┐     │
  │  │Historian│  │ Alarm  │  │ Trend  │     │
  │  │Database │  │ Server │  │ Server │     │
  │  └────────┘  └────────┘  └────────┘     │
  └──────────┬───────────────────┬───────────┘
             │    Ethernet/IP    │
      ┌──────┴──────┐    ┌──────┴──────┐
      │  HMI Panel  │    │  HMI Panel  │
      │ (Operator)  │    │ (Engineer)  │
      └──────┬──────┘    └──────┬──────┘
             │                  │
      ┌──────┴──────┐    ┌─────┴───────┐
      │   PLC #1    │    │   PLC #2    │
      │ (Pumping)   │    │ (Mixing)    │
      └─────────────┘    └─────────────┘
```

### SCADA Functions

| Function | Description |
|---|---|
| **Monitoring** | Real-time display of process values |
| **Trending** | Historical data recording and display |
| **Alarming** | Threshold violations, priorities, acknowledgment |
| **Remote control** | Operator setpoint changes, manual overrides |
| **Reporting** | Shift reports, production summaries |

---

## 16.5 Industrial Communication Protocols

| Protocol | Medium | Speed | Distance | Use Case |
|---|---|---|---|---|
| **Modbus RTU** | RS-485 | 115.2 kbps | 1200 m | Simple devices, legacy |
| **Modbus TCP** | Ethernet | 100 Mbps | 100 m | Ethernet-based Modbus |
| **PROFIBUS DP** | RS-485 | 12 Mbps | 100 m | Siemens ecosystem |
| **PROFINET** | Ethernet | 100 Mbps | 100 m | Siemens, real-time |
| **EtherNet/IP** | Ethernet | 100 Mbps | 100 m | Allen-Bradley/Rockwell |
| **EtherCAT** | Ethernet | 100 Mbps | 100 m | Motion control, fast I/O |
| **OPC UA** | Ethernet | Variable | Any | Platform-independent |

---

## 16.6 PID Control in Industrial Settings

### Cascade Control (Common in Process Industry)

```
  Setpoint ──►[Master PID]──►Setpoint──►[Slave PID]──►Valve──►Process──►
       ↑          (slow)          ↑         (fast)               │
       │                          │                              │
       │                          └──── Fast sensor ◄────────────┤
       │                                                         │
       └──────────── Slow sensor ◄───────────────────────────────┘
```

**Example**: Temperature control of a heat exchanger
- Master: Temperature PID (slow, minutes) → outputs flow setpoint
- Slave: Flow PID (fast, seconds) → controls valve

See: [examples/cascade-control.md](examples/cascade-control.md)

---

## 16.7 Batch Control (ISA-88)

For batch processes (pharmaceutical, food, chemical):

```
  ┌─────────────────────────────────┐
  │         Batch Recipe            │
  │                                 │
  │  ┌─────┐   ┌─────┐   ┌─────┐  │
  │  │Fill  │──►│Heat  │──►│Mix   │ │
  │  │Tank  │   │to 80°│   │30min │ │
  │  └─────┘   └─────┘   └─────┘  │
  │      │                    │     │
  │      ▼                    ▼     │
  │  ┌─────┐             ┌─────┐   │
  │  │Check │             │Cool  │  │
  │  │Level │             │to 25°│  │
  │  └─────┘             └─────┘   │
  └─────────────────────────────────┘
```

---

## Examples

| File | Description |
|---|---|
| [ladder-logic.md](examples/ladder-logic.md) | Motor start/stop circuit in Ladder Diagram |
| [cascade-control.md](examples/cascade-control.md) | Cascade temperature-flow control |
| [modbus-communication.md](examples/modbus-communication.md) | Modbus RTU protocol walkthrough |

---

**Previous → [15-embedded-control-systems](../15-embedded-control-systems/README.md)**  
**Next → [17-robotics-and-motion-control](../17-robotics-and-motion-control/README.md)**
