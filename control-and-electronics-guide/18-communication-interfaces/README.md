# 18 — Communication Interfaces

> *Control systems don't operate in isolation. They exchange data with sensors, actuators, other controllers, and supervisory systems through a variety of communication protocols. This section covers the essential interfaces from board-level (SPI, I²C) to field-level (CAN, RS-485) to network-level (Ethernet).*

---

## 18.1 Communication Fundamentals

### Serial vs. Parallel

| Feature | Serial | Parallel |
|---|---|---|
| Wires | Few (1-4) | Many (8-32) |
| Speed | Up to Gbps | Limited by skew |
| Distance | Long (meters to km) | Short (< 0.5 m) |
| Cost | Low | High |
| Modern trend | **Dominant** | Legacy (old buses) |

### Synchronous vs. Asynchronous

```
  Synchronous (SPI, I²C):
  
  CLK:  ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐
        ┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └
  DATA: ═╤═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══
        D7  D6  D5  D4  D3  D2  D1  D0
  
  → Receiver samples on clock edge, no baud rate agreement needed
  
  
  Asynchronous (UART, RS-485):
  
  DATA: ────┐ ╤═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╤───────
       Idle │Start D0  D1  D2  D3  D4  D5  D6  D7 Stop
            └─────────────────────────────────────┘
  
  → Both sides must agree on baud rate (within ~3%)
```

---

## 18.2 UART / RS-232 / RS-485

### UART Frame

```
  ┌─────┬────┬────┬────┬────┬────┬────┬────┬────┬──────┬─────┐
  │Start│ D0 │ D1 │ D2 │ D3 │ D4 │ D5 │ D6 │ D7 │Parity│Stop │
  │ bit │    │    │    │    │    │    │    │    │(opt) │ bit │
  └─────┴────┴────┴────┴────┴────┴────┴────┴────┴──────┴─────┘
    0                    8 data bits                        1
```

### RS-232 vs. RS-485

| Feature | RS-232 | RS-485 |
|---|---|---|
| Signaling | Single-ended | Differential |
| Voltage | ±3V to ±15V | ±1.5V to ±6V |
| Topology | Point-to-point | Multi-drop bus |
| Max devices | 2 | 32 (256 with high-Z) |
| Max distance | 15 m | **1200 m** |
| Noise immunity | Low | **High** |
| Duplex | Full | Half (2-wire) or Full (4-wire) |

See: [examples/uart-protocol.md](examples/uart-protocol.md)

---

## 18.3 SPI (Serial Peripheral Interface)

### Signals

```
  Master                           Slave
  ┌──────┐                        ┌──────┐
  │      │───── SCLK ────────────►│      │
  │      │───── MOSI ────────────►│      │  (Master Out, Slave In)
  │      │◄──── MISO ─────────────│      │  (Master In, Slave Out)
  │      │───── CS̄ ──────────────►│      │  (Chip Select, active low)
  └──────┘                        └──────┘
```

### Timing (Mode 0: CPOL=0, CPHA=0)

```
  CS̄:   ────┐                                    ┌────
            └────────────────────────────────────┘
  SCLK:     ─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─
              └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘
  MOSI:  ═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══════
            D7  D6  D5  D4  D3  D2  D1  D0
  MISO:  ═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══════
            D7  D6  D5  D4  D3  D2  D1  D0
  
  ↑ Data valid on rising edge (sample), changes on falling edge
```

### SPI Modes

| Mode | CPOL | CPHA | Clock Idle | Sample Edge |
|---|---|---|---|---|
| 0 | 0 | 0 | Low | Rising |
| 1 | 0 | 1 | Low | Falling |
| 2 | 1 | 0 | High | Falling |
| 3 | 1 | 1 | High | Rising |

**Common uses**: ADC, DAC, flash memory, display controllers, high-speed sensors
**Speed**: 1-100 MHz typical, up to 200 MHz

---

## 18.4 I²C (Inter-Integrated Circuit)

### Bus Architecture

```
       VCC
        │
       ┌┤├┐ ┌┤├┐  Pull-up resistors (4.7kΩ typical)
       │   │ │   │
  SDA ─┴───┼─┴───┼─────┬─────┬─────
           │     │     │     │
  SCL ─────┴─────┴─────┼─────┼─────
                        │     │
                   ┌────┴┐ ┌──┴──┐
                   │Slave│ │Slave│
                   │0x48 │ │0x68 │
                   └─────┘ └─────┘
```

### Protocol

```
  START  Address (7-bit)  R/W  ACK   Data byte    ACK   STOP
  ┌─┐ ┌──────────────────┬───┬───┐ ┌───────────┬───┐ ┌─┐
  │S│ │ A6 A5 A4 A3 A2 A1│A0 │R/W│ │ D7...D0   │ACK│ │P│
  └─┘ └──────────────────┴───┴───┘ └───────────┴───┘ └─┘
       └──── Master sends ────┘     └── Master/Slave ─┘
  
  Start: SDA ↓ while SCL high
  Stop:  SDA ↑ while SCL high
  ACK:   Receiver pulls SDA low during 9th clock
```

### Speed Grades

| Mode | Speed | Notes |
|---|---|---|
| Standard | 100 kHz | Original |
| Fast | 400 kHz | Most common |
| Fast Plus | 1 MHz | Stronger pull-ups needed |
| High Speed | 3.4 MHz | Special master code |

See: [examples/i2c-sensor-read.md](examples/i2c-sensor-read.md)

---

## 18.5 CAN (Controller Area Network)

The dominant protocol for automotive, industrial, and robotics applications.

### Bus Topology

```
  120Ω                                           120Ω
  ┌┤├┐                                           ┌┤├┐
  │   │                                           │   │
  ┴───┴───┬─────────┬─────────┬─────────┬────────┴───┴
  CAN_H   │         │         │         │
  CAN_L   │         │         │         │
  ────────┬┘─────────┬┘────────┬┘────────┬┘
          │          │         │         │
       ┌──┴──┐   ┌──┴──┐  ┌──┴──┐  ┌──┴──┐
       │ECU 1│   │ECU 2│  │ECU 3│  │ECU 4│
       │Motor│   │Brake│  │Dash │  │Body │
       └─────┘   └─────┘  └─────┘  └─────┘
```

### CAN Frame

```
  ┌───┬──────────┬───┬───┬────┬──────────────┬──────┬───┬───┬───────┐
  │SOF│  ID (11) │RTR│IDE│DLC │  Data (0-8B) │ CRC  │ACK│EOF│  IFS  │
  │ 1 │  bits    │ 1 │ 1 │ 4  │  0-64 bits   │ 15+1 │2  │ 7 │  3    │
  └───┴──────────┴───┴───┴────┴──────────────┴──────┴───┴───┴───────┘
  
  SOF: Start of Frame (dominant bit)
  ID:  Message identifier (also determines priority!)
  RTR: Remote Transmission Request
  DLC: Data Length Code (0-8 bytes)
  CRC: Cyclic Redundancy Check
  ACK: Acknowledge (all receivers)
```

### CAN Arbitration (Priority)

```
  Node A (ID=0x100):  0 0 0 1 0 0 0 0 0 0 0 0...
  Node B (ID=0x080):  0 0 0 0 1 0 0 0 0 0 0 0...
  Bus:                0 0 0 0 ← Node A sees recessive but bus is dominant
                              → Node A LOSES, backs off
                              → Node B WINS (lower ID = higher priority)
  
  This happens automatically, without collision or retransmission!
  → Deterministic latency for high-priority messages
```

💡 **Insight**: CAN's non-destructive bitwise arbitration is its killer feature. Unlike Ethernet (CSMA/CD), high-priority CAN messages are never delayed by lower-priority traffic. This makes CAN ideal for real-time systems.

See: [examples/can-bus-design.md](examples/can-bus-design.md)

---

## 18.6 Protocol Selection Guide

| Criteria | SPI | I²C | UART/485 | CAN |
|---|---|---|---|---|
| **Speed** | ★★★★★ | ★★☆ | ★★☆ | ★★★ |
| **Distance** | ★☆ | ★☆ | ★★★★ | ★★★★ |
| **Wire count** | ★★☆ (4) | ★★★★ (2) | ★★★ (2-3) | ★★★★ (2) |
| **Multi-device** | ★★☆ | ★★★★ | ★★★ | ★★★★★ |
| **Error detection** | ★☆ | ★★☆ | ★★☆ | ★★★★★ |
| **Determinism** | ★★★★ | ★★★ | ★★☆ | ★★★★★ |
| **Complexity** | ★★★★ | ★★★ | ★★★★★ | ★★☆ |
| **Best for** | Board-level, fast | Board sensors | Long distance | Automotive, industrial |

---

## Examples

| File | Description |
|---|---|
| [uart-protocol.md](examples/uart-protocol.md) | UART/RS-485 configuration and debugging |
| [i2c-sensor-read.md](examples/i2c-sensor-read.md) | Reading an I²C temperature sensor |
| [can-bus-design.md](examples/can-bus-design.md) | CAN bus design for motor controller |

---

**Previous → [17-robotics-and-motion-control](../17-robotics-and-motion-control/README.md)**  
**Next → [19-safety-and-reliability](../19-safety-and-reliability/README.md)**
