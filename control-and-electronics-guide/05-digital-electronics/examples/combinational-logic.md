# Example: Combinational Logic — 7-Segment Display Decoder

## Purpose

Design a combinational logic circuit that converts a 4-bit binary input (0–9) into the 7 control signals needed to display the corresponding digit on a 7-segment LED display.

---

## 7-Segment Display Layout

```
     ─── a ───
    │         │
    f         b
    │         │
     ─── g ───
    │         │
    e         c
    │         │
     ─── d ───   (dp)
```

Segments are labeled a–g (plus optional decimal point dp).

---

## Truth Table

| Decimal | D3 D2 D1 D0 | a | b | c | d | e | f | g |
|---|---|---|---|---|---|---|---|---|
| 0 | 0000 | 1 | 1 | 1 | 1 | 1 | 1 | 0 |
| 1 | 0001 | 0 | 1 | 1 | 0 | 0 | 0 | 0 |
| 2 | 0010 | 1 | 1 | 0 | 1 | 1 | 0 | 1 |
| 3 | 0011 | 1 | 1 | 1 | 1 | 0 | 0 | 1 |
| 4 | 0100 | 0 | 1 | 1 | 0 | 0 | 1 | 1 |
| 5 | 0101 | 1 | 0 | 1 | 1 | 0 | 1 | 1 |
| 6 | 0110 | 1 | 0 | 1 | 1 | 1 | 1 | 1 |
| 7 | 0111 | 1 | 1 | 1 | 0 | 0 | 0 | 0 |
| 8 | 1000 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| 9 | 1001 | 1 | 1 | 1 | 1 | 0 | 1 | 1 |
| 10–15 | 1010–1111 | X | X | X | X | X | X | X |

Entries 10–15 are "don't care" (X) since we only display 0–9.

---

## K-Map Minimization (Segment 'a')

Segment 'a' is ON for digits: 0, 2, 3, 5, 6, 7, 8, 9

```
  K-Map for segment 'a':
  
              D1 D0
  D3 D2   00  01  11  10
    00   │  1 │  0 │  1 │  1 │
    01   │  0 │  1 │  1 │  1 │
    11   │  X │  X │  X │  X │
    10   │  1 │  1 │  X │  X │
    
  Groups (using don't-cares as 1):
  - D3 (row 10,11 = all 1/X): a = D3 + ...
  - D2·D0: covers (01,01), (01,11), (11,01), (11,11)
  - D̄2·D̄0: covers (00,00), (00,10), (10,00), (10,10)
  - D1·D̄2: need to check remaining
  
  Simplified: a = D3 + D1 + (D2 ⊕ D0)
            = D3 + D1 + D2·D0 + D̄2·D̄0
```

(Exact minimization depends on grouping choices with don't-cares.)

---

## Boolean Expressions (Minimized)

Using don't-care terms for inputs 10–15:

$$a = D_3 + D_1 + D_2 \odot D_0 = D_3 + D_1 + \overline{D_2 \oplus D_0}$$

$$b = \overline{D_2} + \overline{D_1 \oplus D_0}$$

$$c = D_2 + \overline{D_1} + D_0$$

$$d = D_3 + \overline{D_2} \cdot \overline{D_0} + D_1 \cdot \overline{D_0} + \overline{D_2} \cdot D_1 + D_2 \cdot \overline{D_1} \cdot D_0$$

$$e = \overline{D_0} \cdot (\overline{D_2} + D_1)$$

$$f = D_3 + D_2 \cdot \overline{D_1} + \overline{D_1} \cdot \overline{D_0} + D_2 \cdot \overline{D_0}$$

$$g = D_3 + D_2 \oplus D_1 + D_1 \cdot \overline{D_0}$$

---

## Circuit Block Diagram

```
                    ┌──────────────────────┐
  D3 ──────────────►│                      ├──► a
  D2 ──────────────►│   7-Segment          ├──► b
  D1 ──────────────►│   Decoder            ├──► c
  D0 ──────────────►│   (Combinational     ├──► d
                    │    Logic)             ├──► e
                    │                      ├──► f
                    │                      ├──► g
                    └──────────────────────┘
```

🔧 **Practical**: In real designs, you'd use a dedicated decoder IC (e.g., 7447, CD4511) or implement this in an FPGA/microcontroller. The logic minimization exercise teaches the methodology — the actual implementation is a lookup table in firmware or a standard IC.

---

## Expected Results

| Input | Display | Active Segments |
|---|---|---|
| 0000 | **0** | a, b, c, d, e, f |
| 0001 | **1** | b, c |
| 0101 | **5** | a, c, d, f, g |
| 1001 | **9** | a, b, c, d, f, g |
