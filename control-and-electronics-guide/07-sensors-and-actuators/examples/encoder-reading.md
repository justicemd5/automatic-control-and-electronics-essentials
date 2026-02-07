# Example: Quadrature Encoder Reading

## Purpose
Explain how incremental quadrature encoders work, implement decoding logic, and calculate position and velocity from encoder signals.

---

## Quadrature Encoder Signals

An incremental encoder produces two square-wave channels (A and B) shifted by 90° (quadrature):

```
  Clockwise rotation:
  
  Ch A: ──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──
          └─┘  └─┘  └─┘  └─┘  └─┘
          
  Ch B:  ──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──
           └─┘  └─┘  └─┘  └─┘  └─┘
  
  State:  00 01 11 10 00 01 11 10 00
  
  ────────────────────────────────────►  time
  
  Counter-clockwise rotation:
  
  Ch A:  ──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──
           └─┘  └─┘  └─┘  └─┘  └─┘
           
  Ch B: ──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──
          └─┘  └─┘  └─┘  └─┘  └─┘
  
  State:  00 10 11 01 00 10 11 01 00
```

---

## Decoding Methods

### 1× Decoding (Single Edge, Single Channel)
Count rising edges of Channel A only → 1 count per encoder line

### 2× Decoding (Both Edges, Single Channel)
Count rising and falling edges of Channel A → 2 counts per line

### 4× Decoding (Both Edges, Both Channels)
Count all edges of both channels → 4 counts per line (maximum resolution)

```
  Ch A: ──┐ ┌──┐ ┌──
          └─┘  └─┘
          
  Ch B:  ──┐ ┌──┐ ┌──
           └─┘  └─┘
           
  4×:   ↑ ↑ ↑ ↑ ↑ ↑ ↑ ↑   ← 8 counts per encoder line pair
  2×:   ↑   ↑   ↑   ↑     ← 4 counts
  1×:   ↑       ↑         ← 2 counts
```

For an encoder with PPR (Pulses Per Revolution) = 1000:
- 1× decoding: 1000 counts/rev → 0.36° resolution
- 4× decoding: 4000 counts/rev → 0.09° resolution

---

## State Machine Decoding

### State Transition Table (4× Decoding)

| Previous (AB) | Current (AB) | Action |
|---|---|---|
| 00 | 01 | Count +1 (CW) |
| 01 | 11 | Count +1 |
| 11 | 10 | Count +1 |
| 10 | 00 | Count +1 |
| 00 | 10 | Count −1 (CCW) |
| 10 | 11 | Count −1 |
| 11 | 01 | Count −1 |
| 01 | 00 | Count −1 |
| XX | XX (same) | No change |
| All others | — | Error (missed step) |

### Lookup Table Implementation (Efficient)

```
  Index = (previous_AB << 2) | current_AB  (4-bit index, 0–15)
  
  Lookup table (16 entries):
  
  Index  Prev  Curr  Action
  0x0    00    00    0  (no change)
  0x1    00    01    +1
  0x2    00    10    −1
  0x3    00    11    ERROR
  0x4    01    00    −1
  0x5    01    01    0
  0x6    01    10    ERROR
  0x7    01    11    +1
  0x8    10    00    +1
  0x9    10    01    ERROR
  0xA    10    10    0
  0xB    10    11    −1
  0xC    11    00    ERROR
  0xD    11    01    −1
  0xE    11    10    +1
  0xF    11    11    0
```

### C Implementation

```c
// Quadrature decoder lookup table
// Index: [prev_A, prev_B, curr_A, curr_B]
const int8_t ENCODER_TABLE[16] = {
     0, +1, -1,  2,  // prev=00
    -1,  0,  2, +1,  // prev=01
    +1,  2,  0, -1,  // prev=10
     2, -1, +1,  0   // prev=11
};
// 2 = error (missed step)

volatile int32_t encoder_count = 0;
uint8_t prev_state = 0;

void encoder_isr(void) {
    uint8_t curr_state = (READ_PIN_A << 1) | READ_PIN_B;
    uint8_t index = (prev_state << 2) | curr_state;
    int8_t delta = ENCODER_TABLE[index];
    
    if (delta == 2) {
        // Error: missed a step (too fast or noise)
        error_count++;
    } else {
        encoder_count += delta;
    }
    prev_state = curr_state;
}
```

---

## Position and Velocity Calculation

### Position

$$\theta = \frac{2\pi \cdot \text{count}}{4 \cdot PPR} \quad \text{[radians]}$$

### Velocity Methods

**Method 1: Finite Difference** (good at medium–high speeds)

$$\omega = \frac{\Delta\text{count}}{4 \cdot PPR} \cdot \frac{2\pi}{\Delta t} \quad \text{[rad/s]}$$

Sample at fixed intervals (e.g., $\Delta t = 1$ ms), compute count difference.

**Method 2: Period Measurement** (good at low speeds)

Measure time between edges:

$$\omega = \frac{2\pi}{4 \cdot PPR \cdot T_{edge}} \quad \text{[rad/s]}$$

**Method 3: Hybrid** (best across all speeds)

Use period measurement at low speeds, finite difference at high speeds. Switch when count per sample interval drops below a threshold (e.g., 5 counts).

💡 **Insight**: At very low speeds, finite difference gives poor resolution (quantization noise). At very high speeds, period measurement timer may overflow. The hybrid approach handles both extremes.

---

## Hardware Interface

### Microcontroller Timer in Encoder Mode

Most ARM Cortex-M microcontrollers have hardware encoder interfaces:

```
  STM32 Timer in Encoder Mode:
  
  Encoder Ch A ──── TIM2_CH1 (PA0)
  Encoder Ch B ──── TIM2_CH2 (PA1)
  Index Z ────────── EXTI interrupt (optional)
  
  Timer counter auto-increments/decrements based on A/B edges.
  No software ISR needed for counting → zero CPU overhead.
  Counter register = position at any time.
```

### Signal Conditioning

```
  Encoder  ──── 100Ω ──┬──── MCU Input
  Output                │
                      0.1μF
                        │
                       GND
                       
  (RC filter: f_c = 16kHz, removes noise without affecting signal)
```

For long cable runs (>1m), use differential line drivers (RS-422/AM26LS31) and receivers at the MCU end.

🔧 **Practical**: Always use hardware encoder mode when available. Software decoding via GPIO interrupts fails above ~50 kHz edge rate due to ISR latency. A 1000-PPR encoder at 3000 RPM generates 200 kHz edge rate in 4× mode.
