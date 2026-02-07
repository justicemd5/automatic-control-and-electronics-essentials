# Example: CAN Bus Design for Motor Controller Network

## Purpose
Design a CAN bus network for a multi-axis motor controller system, covering message design, priority assignment, bus loading, and physical layer.

---

## System: 4-Axis Robot Controller

```
  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
  │  Axis 1  │    │  Axis 2  │    │  Axis 3  │    │  Axis 4  │
  │ (Motor   │    │ (Motor   │    │ (Motor   │    │ (Motor   │
  │  Driver) │    │  Driver) │    │  Driver) │    │  Driver) │
  └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘
       │               │               │               │
  ─────┴───────────────┴───────────────┴───────────────┴─────── CAN Bus
       │                                                        │
  ┌────┴─────┐                                           ┌──────┴──┐
  │  Master  │                                           │ Safety  │
  │Controller│                                           │ Module  │
  │ (Motion  │                                           │ (E-Stop │
  │  Planner)│                                           │  STO)   │
  └──────────┘                                           └─────────┘
  
  Bus: CAN 2.0B, 1 Mbit/s, 120Ω termination at each end
```

---

## Message Design

### Priority Assignment (Lower ID = Higher Priority)

| ID (hex) | Priority | Sender | Message | Cycle | DLC |
|---|---|---|---|---|---|
| **0x080** | Highest | Safety | Emergency stop | Event | 2 |
| **0x100-0x103** | High | Master | Position commands (Axis 1-4) | 1 ms | 8 |
| **0x180-0x183** | Medium-High | Drives | Position + Current feedback (1-4) | 1 ms | 8 |
| **0x200-0x203** | Medium | Drives | Status + Temperature (1-4) | 10 ms | 4 |
| **0x300** | Low | Master | Configuration/Parameter write | Event | 8 |
| **0x380-0x383** | Low | Drives | Configuration response (1-4) | Event | 8 |
| **0x700-0x703** | Lowest | Drives | Heartbeat (1-4) | 100 ms | 1 |

### Message Format Details

#### Position Command (0x100 + axis_id)

```
  Byte 0-3: Target position (int32, 0.001° resolution)
  Byte 4-5: Feedforward velocity (int16, 0.1 RPM resolution)
  Byte 6-7: Feedforward torque (int16, 0.01 N·m resolution)
  
  Example: Move axis 1 to 90.000°, FF velocity 100 RPM, FF torque 5.0 N·m
  
  ID:   0x100
  Data: [00 01 5F 90] [03 E8] [01 F4]
         └─ 90000 ──┘  └1000┘  └ 500┘
         = 90.000°    = 100.0  = 5.00
                       RPM      N·m
```

#### Position + Current Feedback (0x180 + axis_id)

```
  Byte 0-3: Actual position (int32, 0.001° resolution)
  Byte 4-5: Actual velocity (int16, 0.1 RPM resolution)
  Byte 6-7: Actual current (int16, 0.01 A resolution)
```

#### Emergency Stop (0x080)

```
  Byte 0: Error code
          0x01 = E-Stop pressed
          0x02 = Overcurrent
          0x04 = Overtemperature
          0x08 = Encoder fault
  Byte 1: Axis number (0 = all, 1-4 = specific)
```

---

## Bus Loading Calculation

### Message Sizes (with overhead)

CAN frame overhead: SOF(1) + ID(11) + RTR(1) + IDE(1) + r0(1) + DLC(4) + CRC(15) + DEL(1) + ACK(2) + EOF(7) + IFS(3) = **47 bits** overhead

Plus data bits and bit-stuffing (~20% average overhead).

| Message | Period | Data bits | Frame bits (est.) | Rate [frames/s] | Bit rate [kbit/s] |
|---|---|---|---|---|---|
| Pos command ×4 | 1 ms | 64 | 130 | 4000 | 520 |
| Pos feedback ×4 | 1 ms | 64 | 130 | 4000 | 520 |
| Status ×4 | 10 ms | 32 | 108 | 400 | 43 |
| Heartbeat ×4 | 100 ms | 8 | 80 | 40 | 3 |
| **Total** | | | | **8440** | **~1086** |

⚠️ At 1 Mbit/s: **Bus load ≈ 108%** — **too high!**

### Solution: Reduce to Feasible Load

Option A: Increase bus speed to 2 Mbit/s (CAN FD) → 54% load ✓

Option B: Reduce feedback to 2 ms cycle:
- Command: 4000 frames/s × 130 bits = 520 kbit/s
- Feedback: 2000 frames/s × 130 bits = 260 kbit/s  
- Total: ~826 kbit/s → **83% load** (still marginal)

Option C: Reduce to 2 ms command + 2 ms feedback:
- Total: ~600 kbit/s → **60% load** ✓

🔧 **Practical**: Keep CAN bus load below 70% to allow for occasional bursts (error frames, retransmissions). Above 80%, latency increases significantly.

---

## Physical Layer Design

### Wiring

```
  ┌─────┐           Twisted pair             ┌─────┐
  │Node │─── CAN_H ═════════════════════ CAN_H ───│Node │
  │  A  │─── CAN_L ═════════════════════ CAN_L ───│  B  │
  │     │─── GND   ─────────────────────  GND  ───│     │
  └─────┘                                         └─────┘
  
  ┌───┐                                           ┌───┐
  │120│ Ω  Termination                    Termination │120│ Ω
  │   │    (at each end                   (at each end │   │
  └───┘     of bus only)                   of bus only)└───┘
```

### Maximum Bus Length vs. Speed

| Bit Rate | Max Bus Length | Max Stub Length |
|---|---|---|
| 1 Mbit/s | 40 m | 0.3 m |
| 500 kbit/s | 100 m | 0.6 m |
| 250 kbit/s | 250 m | 2 m |
| 125 kbit/s | 500 m | 5 m |
| 50 kbit/s | 1000 m | 13 m |

### Common Physical Layer Issues

| Issue | Cause | Fix |
|---|---|---|
| Intermittent errors | Missing termination | Add 120Ω at both ends |
| Works at low speed only | Reflections (stubs too long) | Shorten stubs, add termination |
| Ground shift errors | Different ground potentials | Use isolated CAN transceivers |
| Ringing on oscilloscope | Impedance mismatch | Check termination, cable quality |
| One node dies → bus down | Bus-off state | Implement bus-off recovery |

💡 **Insight**: Always check the CAN bus with an oscilloscope during development. The eye diagram should show clean transitions with minimal ringing. Dominant level: CAN_H ≈ 3.5V, CAN_L ≈ 1.5V. Recessive level: both ≈ 2.5V. Differential voltage: dominant = 2V, recessive = 0V.

---

## Error Handling

CAN has built-in error detection (5 mechanisms):
1. **Bit monitoring**: Transmitter checks bus matches what it sent
2. **Bit stuffing**: After 5 identical bits, opposite bit inserted
3. **CRC check**: 15-bit CRC on each frame
4. **ACK check**: At least one receiver must acknowledge
5. **Frame format**: Fixed fields checked

Nodes track error counters (TEC/REC):
- **Error Active**: TEC < 128, REC < 128 (normal operation)
- **Error Passive**: TEC > 127 or REC > 127 (reduced priority)
- **Bus Off**: TEC > 255 (disconnected from bus)

⚠️ **Pitfall**: A single faulty node can flood the bus with error frames and cause all nodes to go bus-off. Always implement bus-off recovery (automatic or manual) and monitor error counters.
