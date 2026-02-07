# Example: Reading an I²C Temperature Sensor (TMP102)

## Purpose
Demonstrate I²C communication at the register level by reading temperature from a TMP102 sensor, covering addressing, read/write sequences, and data conversion.

---

## Device: TMP102 Temperature Sensor

| Parameter | Value |
|---|---|
| I²C Address | 0x48 (A0 pin = GND) |
| Resolution | 12-bit (0.0625°C/LSB) |
| Range | −25°C to +85°C (typical) |
| Supply | 1.4V to 3.6V |

### Register Map

| Register | Address | Size | Description |
|---|---|---|---|
| Temperature | 0x00 | 2 bytes | Read-only, 12-bit result |
| Configuration | 0x01 | 2 bytes | Settings (conversion rate, etc.) |
| T_LOW | 0x02 | 2 bytes | Low temperature threshold |
| T_HIGH | 0x03 | 2 bytes | High temperature threshold |

---

## Step 1: I²C Write — Set Register Pointer

To read temperature, first write the register pointer (0x00):

```
  I²C Bus Transaction: Write register pointer
  
  Master sends:
  ┌─────┬─────────────────┬───┬─────┬────────────┬─────┬─────┐
  │START│  0x48 (7-bit)   │ W │ ACK │  0x00      │ ACK │STOP │
  │  S  │ 1001000         │ 0 │  A  │ (reg addr) │  A  │  P  │
  └─────┴─────────────────┴───┴─────┴────────────┴─────┴─────┘
          └── Device address ──┘       └── Register pointer ─┘
  
  Byte 1: (0x48 << 1) | 0 = 0x90  (address + write bit)
  Byte 2: 0x00 (temperature register)
```

### Signal Detail

```
  SDA: ─┐ ┌1┐0┐0┐1┐0┐0┐0┐W┐ ┌A┐0┐0┐0┐0┐0┐0┐0┐0┐ ┌A┐ ┌─
        └─┘ └─┘ └─┘ └─┘ └─┘ └┘ └─┘ └─┘ └─┘ └─┘ └─┘ └┘ ┘
  SCL: ──┐┌─┐┌─┐┌─┐┌─┐┌─┐┌─┐┌─┐┌─┐┌─┐┌─┐┌─┐┌─┐┌─┐┌─┐┌─┐──
         └┘ └┘ └┘ └┘ └┘ └┘ └┘ └┘ └┘ └┘ └┘ └┘ └┘ └┘ └┘ └┘
       S  ←── Address byte ──→ A ←── Register byte ──→ A  P
       │                       │                       │  │
    Start                    ACK from                ACK  Stop
                             slave                  from
                                                   slave
```

---

## Step 2: I²C Read — Get Temperature Data

Now read 2 bytes from the temperature register:

```
  Master receives:
  ┌─────┬─────────────────┬───┬─────┬────────────┬─────┬────────────┬──────┬─────┐
  │START│  0x48 (7-bit)   │ R │ ACK │  MSB       │ ACK │  LSB       │ NACK │STOP │
  │  S  │ 1001000         │ 1 │  A  │ (temp[11:4])│  A  │(temp[3:0]) │  NA  │  P  │
  └─────┴─────────────────┴───┴─────┴────────────┴─────┴────────────┴──────┴─────┘
          └── Address + Read ──┘       └── Master ACKs ──┘  └── Master NACKs ──┘
  
  Byte 1: (0x48 << 1) | 1 = 0x91  (address + read bit)
  Byte 2: MSB of temperature (from slave)
  Byte 3: LSB of temperature (from slave)
  
  Master sends ACK after MSB (want more data)
  Master sends NACK after LSB (done reading)
```

---

## Step 3: Convert Raw Data to Temperature

### Data Format (12-bit, left-justified)

```
  MSB byte:  [D11 D10 D9 D8 D7 D6 D5 D4]
  LSB byte:  [D3  D2  D1 D0  0   0   0   0]
  
  Temperature register = (MSB << 4) | (LSB >> 4)
  
  Positive: temp_C = raw * 0.0625
  Negative: raw is in two's complement
```

### Conversion Code (C)

```c
float TMP102_ReadTemperature(void)
{
    uint8_t data[2];
    
    /* Write register pointer */
    uint8_t reg = 0x00;
    I2C_Write(TMP102_ADDR, &reg, 1);
    
    /* Read 2 bytes */
    I2C_Read(TMP102_ADDR, data, 2);
    
    /* Combine MSB and LSB */
    int16_t raw = ((int16_t)data[0] << 4) | (data[1] >> 4);
    
    /* Handle negative temperatures (12-bit two's complement) */
    if (raw & 0x0800) {
        raw |= 0xF000;  /* Sign-extend to 16 bits */
    }
    
    /* Convert to Celsius */
    return raw * 0.0625f;
}
```

### Worked Example

Suppose we read: MSB = 0x19, LSB = 0x80

```
  MSB = 0x19 = 0001 1001
  LSB = 0x80 = 1000 0000
  
  raw = (0x19 << 4) | (0x80 >> 4)
      = 0x0190     | 0x08
      = 0x0198
      = 408 (decimal)
  
  Temperature = 408 × 0.0625 = 25.5°C ✓
```

### Negative Temperature Example

Read: MSB = 0xFC, LSB = 0x80

```
  raw = (0xFC << 4) | (0x80 >> 4) = 0x0FC8 → no, wait:
  
  MSB = 0xFC = 1111 1100
  LSB = 0x80 = 1000 0000
  
  raw = (0xFC << 4) | (0x80 >> 4)
      = 0x0FC0    | 0x08
      = 0x0FC8
  
  Bit 11 (0x0800) is set → negative!
  Sign extend: raw |= 0xF000 → 0xFFC8
  
  As signed: 0xFFC8 = -56
  Temperature = -56 × 0.0625 = -3.5°C ✓
```

---

## Common I²C Issues

| Problem | Symptom | Solution |
|---|---|---|
| Missing pull-ups | SDA/SCL never go high | Add 4.7kΩ to VCC on both lines |
| Wrong address | NACK on first byte | Check A0/A1 pins, scan bus |
| Bus stuck (SDA held low) | Communication frozen | Toggle SCL 9 times to release |
| Clock stretching | Slow operation | Increase I²C timeout |
| Repeated start issue | Some MCUs fail | Verify I²C peripheral supports Sr |

### I²C Bus Scan (Debugging)

```c
/* Scan all possible 7-bit addresses */
for (uint8_t addr = 0x08; addr < 0x78; addr++) {
    if (I2C_Probe(addr) == ACK) {
        printf("Device found at 0x%02X\n", addr);
    }
}
```

⚠️ **Pitfall**: Pull-up resistor value matters! Too high (e.g., 10kΩ) at 400 kHz → slow rise times → communication errors. Too low (e.g., 1kΩ) → excessive current. Use 4.7kΩ for 100 kHz, 2.2kΩ for 400 kHz as starting points.

💡 **Insight**: When an I²C bus "locks up" (SDA stuck low), it's usually because a slave was interrupted mid-byte and is still holding SDA for the data bit it was sending. The fix: clock SCL 9 times while SDA is released — the slave will eventually release SDA and the bus recovers.
