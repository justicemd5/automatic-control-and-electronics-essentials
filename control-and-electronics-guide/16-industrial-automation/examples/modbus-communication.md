# Example: Modbus RTU Communication Protocol

## Purpose
Understand the Modbus RTU protocol at the byte level — the most widely used industrial communication protocol, found in almost every industrial device manufactured in the last 40 years.

---

## Modbus Basics

### Architecture: Master-Slave

```
  ┌──────────┐     RS-485 Bus (Half-duplex)
  │  Master  │──────┬──────────┬──────────┬─────
  │  (PLC)   │      │          │          │
  └──────────┘   ┌──┴──┐   ┌──┴──┐   ┌──┴──┐
                 │Slave │   │Slave │   │Slave │
                 │ #1   │   │ #2   │   │ #3   │
                 │(VFD) │   │(Temp)│   │(Meter)│
                 └──────┘   └──────┘   └──────┘
  
  • Master initiates ALL communication (request-response)
  • Slaves only respond when addressed
  • Each slave has a unique address (1-247)
  • Address 0 = broadcast (no response expected)
```

### Data Model

| Register Type | Address Range | Access | Size | Description |
|---|---|---|---|---|
| **Coils** | 00001-09999 | R/W | 1 bit | Digital outputs |
| **Discrete Inputs** | 10001-19999 | R | 1 bit | Digital inputs |
| **Input Registers** | 30001-39999 | R | 16 bit | Analog inputs |
| **Holding Registers** | 40001-49999 | R/W | 16 bit | Parameters, setpoints |

---

## Modbus RTU Frame Format

```
  ┌─────────┬──────────┬───────────────┬───────────┐
  │ Address │ Function │    Data       │   CRC     │
  │ 1 byte  │ 1 byte   │ N bytes       │ 2 bytes   │
  └─────────┴──────────┴───────────────┴───────────┘
  
  Total frame: 4 to 256 bytes
  
  Frame delimiter: 3.5 character times of silence (no start/stop bits)
  Inter-char gap: max 1.5 character times between bytes within a frame
```

### Common Function Codes

| Code | Name | Description |
|---|---|---|
| 0x01 | Read Coils | Read 1-2000 digital outputs |
| 0x02 | Read Discrete Inputs | Read 1-2000 digital inputs |
| 0x03 | Read Holding Registers | Read 1-125 16-bit registers |
| 0x04 | Read Input Registers | Read 1-125 16-bit registers |
| 0x06 | Write Single Register | Write one 16-bit register |
| 0x10 | Write Multiple Registers | Write 1-123 registers |

---

## Worked Example: Read Temperature from Sensor

### Scenario

Read the temperature value from Slave #2, stored in Holding Register 40001 (address 0x0000).

### Request (Master → Slave)

```
  Byte:  01    02       03      04      05      06       07    08
  Hex:   02    03     00 00   00 01     --      --
         │     │       │       │
         │     │       │       └─ Number of registers: 1
         │     │       └───────── Starting register: 0x0000 (= 40001)
         │     └─────────────────  Function code: 03 (Read Holding Registers)
         └───────────────────────── Slave address: 2
         
  Full frame: [02] [03] [00] [00] [00] [01] [CRC_Lo] [CRC_Hi]
```

### CRC-16 Calculation

```
  CRC-16/Modbus polynomial: 0xA001
  
  Data bytes: 02 03 00 00 00 01
  
  Step-by-step (simplified):
  1. Init CRC = 0xFFFF
  2. XOR with byte 0x02, shift 8 times with polynomial
  3. XOR with byte 0x03, shift 8 times
  4. ... repeat for all data bytes
  5. Result: CRC = 0xC840
  
  Frame: [02] [03] [00] [00] [00] [01] [40] [C8]
         ← Data bytes →                 ← CRC (LSB first!) →
```

### Response (Slave → Master)

Suppose temperature = 25.6°C, stored as 256 (×10 scaling):

```
  Byte:  01    02    03    04    05      06    07
  Hex:   02    03    02   01 00          --    --
         │     │     │     │
         │     │     │     └─── Register value: 0x0100 = 256 → 25.6°C
         │     │     └───────── Byte count: 2 (1 register × 2 bytes)
         │     └─────────────── Function code: 03 (echo)
         └───────────────────── Slave address: 2
         
  Full: [02] [03] [02] [01] [00] [CRC_Lo] [CRC_Hi]
```

### Error Response

If the slave detects an error, it returns the function code with bit 7 set:

```
  Error response: [02] [83] [02] [CRC_Lo] [CRC_Hi]
                        │     │
                        │     └─── Exception code: 02 = "Illegal data address"
                        └───────── 0x83 = 0x03 | 0x80 (error flag)
```

| Exception Code | Meaning |
|---|---|
| 01 | Illegal function |
| 02 | Illegal data address |
| 03 | Illegal data value |
| 04 | Slave device failure |

---

## Timing

At 9600 baud (most common default):

| Parameter | Value |
|---|---|
| Bit time | 104 µs |
| Character time (11 bits: start + 8 data + parity + stop) | 1.146 ms |
| Inter-character gap (max 1.5 char) | 1.72 ms |
| Frame delimiter (3.5 char silence) | 4.01 ms |
| Typical request (8 bytes) | 9.17 ms |
| Typical response (7 bytes) | 8.02 ms |
| **Round-trip (1 register read)** | **~20 ms** |

For 100 registers at 10 Hz polling: need 100 × 20 ms = 2 s → **too slow at 9600 baud!**

🔧 **Practical**: Use 19200 or 38400 baud for applications needing more throughput. Or switch to Modbus TCP (Ethernet) for orders-of-magnitude faster communication.

---

## RS-485 Physical Layer

```
  Termination resistors (120Ω) at each end of bus:
  
  [120Ω]──┬──────────┬──────────┬──────────┬──[120Ω]
           │          │          │          │
         Master     Slave 1   Slave 2   Slave 3
  
  Wiring: Twisted pair (A/B differential)
  Max devices: 32 per segment (256 with repeaters)
  Max distance: 1200m at 9600 baud, 100m at 115200 baud
  
  Bias resistors (optional, prevent floating bus):
  VCC ──[390Ω]── A line
  GND ──[390Ω]── B line
```

⚠️ **Pitfall**: The most common Modbus problems are: (1) wrong baud rate or parity settings, (2) missing termination resistors causing reflections, (3) A/B lines swapped, and (4) ground potential differences on long runs. Always verify communication with an oscilloscope on the A/B lines during commissioning.

💡 **Insight**: Despite being designed in 1979, Modbus remains dominant because of its simplicity. Any engineer can debug Modbus with a serial monitor and a hex calculator. This transparency is its greatest strength — newer protocols offer more features but are far harder to troubleshoot.
