# Example: UART/RS-485 Configuration and Debugging

## Purpose
Walk through UART configuration, common issues, and debugging techniques — the skills needed for every embedded and industrial project.

---

## UART Configuration Parameters

### The "8N1" Shorthand

**9600 8N1** means:
- **9600**: Baud rate (bits per second)
- **8**: 8 data bits
- **N**: No parity
- **1**: 1 stop bit

Total frame = 1 start + 8 data + 0 parity + 1 stop = **10 bits per character**

Actual throughput: $9600 / 10 = 960$ characters/second

### Common Configurations

| Application | Baud | Data | Parity | Stop | Notes |
|---|---|---|---|---|---|
| Debug console | 115200 | 8 | N | 1 | Fast, no error checking |
| Modbus RTU | 9600-38400 | 8 | E | 1 | Even parity standard |
| GPS NMEA | 4800/9600 | 8 | N | 1 | Fixed by GPS module |
| DMX512 (lighting) | 250000 | 8 | N | 2 | 2 stop bits |
| MIDI (music) | 31250 | 8 | N | 1 | Non-standard baud |

---

## RS-485 Half-Duplex Direction Control

```
  MCU                     RS-485 Transceiver          Bus
  ┌─────┐                ┌──────────────────┐
  │     │─── TX ─────────│ DI          A ───│──── A (Data+)
  │     │◄── RX ─────────│ RO          B ───│──── B (Data−)
  │     │─── DE/RE̅ ──────│ DE              │
  │     │                │ RE̅              │
  └─────┘                └──────────────────┘
  
  DE = Driver Enable (high = transmit)
  RE̅ = Receiver Enable (low = receive)
  
  Connect DE and RE̅ together:
    HIGH → Transmit mode
    LOW  → Receive mode
```

### Direction Control Timing

```
  Direction: ──────┐                              ┌──────
  (DE pin)    RX   │         TX mode              │  RX
                   └──────────────────────────────┘
                   ↑                              ↑
              Assert DE              Deassert DE
              BEFORE first byte      AFTER last byte
              (allow ~1 bit time)    (allow ~1 bit time after stop bit)
  
  TX Data:    ───────┐ S D0...D7 P SP ┌──────────────────
                     └────────────────┘
```

### Common Direction Control Bug

```
  WRONG: Deassert DE immediately after writing to TX register
  
  DE:  ───┐     ┌───
          └─────┘
  TX:     ┐ S D0 D1 D2 D3 D4 D5 D6 D7 SP ┌──
          └────────────────────────────────┘
                                    ↑
                              DE already low!
                              Last bits corrupted!
  
  FIX: Wait for TX Complete flag (not TX Empty!)
       TXE = TX register empty (byte moved to shift register)
       TC  = Transmission Complete (shift register empty)
       
       Wait for TC before deasserting DE, or use hardware DE control.
```

⚠️ **Pitfall**: The most common RS-485 bug is deasserting DE too early, corrupting the last byte. Many STM32 UARTs have hardware DE control (RS-485 mode) that handles this automatically — always use it when available.

---

## Debugging Techniques

### 1. Oscilloscope Analysis

```
  Decoding "0x55" (binary: 01010101) at 9600 baud:
  
  Voltage [V]
  3.3│    ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌────
     │    │ │ │ │ │ │ │ │ │
  0.0│────┘ └─┘ └─┘ └─┘ └─┘
     │   S  0  1  0  1  0  1  0  1  SP
     │   │                          │
     │   Start                     Stop
     │
  Each bit = 1/9600 = 104.17 µs
  
  0x55 is the ideal test byte: alternating bits create a clear pattern.
```

### 2. Loopback Test

Connect TX directly to RX (or A to B on RS-485). Send known patterns and verify reception:

```
  Test patterns:
  1. 0x55 (01010101) — Clock-like pattern, tests timing
  2. 0xAA (10101010) — Complement of 0x55
  3. 0xFF (11111111) — All ones, tests idle level
  4. 0x00 (00000000) — All zeros
  5. "Hello\r\n"      — ASCII string
```

### 3. Common Problems and Solutions

| Symptom | Likely Cause | Solution |
|---|---|---|
| No data at all | Wrong baud rate, TX/RX swapped | Verify with scope, swap wires |
| Garbled data | Baud rate mismatch (1-3%) | Check both ends match exactly |
| Occasional errors | Noise on long cable | Use RS-485, add termination |
| First byte lost | Receiver not ready | Add small delay before first byte |
| Last byte corrupted | DE deasserted too early (RS-485) | Wait for TC flag |
| 0x00 received | Break condition (TX held low) | Check TX line, noise |
| Data works one way only | Half-duplex direction issue | Check DE/RE̅ control logic |
| Works at 9600, fails at 115200 | Clock accuracy insufficient | Use external crystal, not RC oscillator |

### 4. Baud Rate Error Calculation

MCU UART baud rate is derived from the system clock:

$$\text{Baud} = \frac{f_{CLK}}{16 \times \text{BRR}}$$

Example: $f_{CLK} = 72$ MHz, target = 9600 baud:

$$\text{BRR} = \frac{72{,}000{,}000}{16 \times 9600} = 468.75$$

Rounded to 469:

$$\text{Actual baud} = \frac{72{,}000{,}000}{16 \times 469} = 9596.93 \text{ baud}$$

$$\text{Error} = \frac{9600 - 9596.93}{9600} = 0.032\%$$

This is well within the ±3% tolerance.

💡 **Insight**: Baud rate errors compound over the frame length. At ±3% error on each end, the worst case is 6% total, which over 10 bits means the last bit is sampled 0.6 bit-times off center. This is why UART works with only ~3% accuracy, but tighter is always better.
