/*
 * Parameterized Synchronous Up/Down Counter with Enable
 * ======================================================
 *
 * Purpose:
 *     Implement a configurable N-bit counter in Verilog with:
 *     - Synchronous reset
 *     - Enable signal
 *     - Up/down direction control
 *     - Overflow/underflow detection
 *     - Terminal count output
 *
 * Parameters:
 *     WIDTH - Bit width of the counter (default: 8)
 *
 * Ports:
 *     clk     - Clock input (rising-edge triggered)
 *     rst_n   - Active-low synchronous reset
 *     enable  - Counter increments/decrements only when enable=1
 *     up_down - Direction: 1=count up, 0=count down
 *     count   - Current counter value (WIDTH bits)
 *     overflow  - Pulses high when counter wraps from max to 0
 *     underflow - Pulses high when counter wraps from 0 to max
 *     tc      - Terminal count: high when at max (up) or 0 (down)
 *
 * Expected Behavior:
 *     - Counting up: 0, 1, 2, ..., 2^WIDTH-1, 0, 1, ...
 *     - Counting down: 2^WIDTH-1, ..., 2, 1, 0, 2^WIDTH-1, ...
 *     - Reset sets counter to 0
 *     - Counter holds value when enable=0
 */

module up_down_counter #(
    parameter WIDTH = 8  // Bit width of the counter
)(
    input  wire              clk,       // System clock
    input  wire              rst_n,     // Active-low synchronous reset
    input  wire              enable,    // Count enable
    input  wire              up_down,   // 1 = count up, 0 = count down
    output reg  [WIDTH-1:0]  count,     // Counter output
    output wire              overflow,  // High on upward wrap-around
    output wire              underflow, // High on downward wrap-around
    output wire              tc         // Terminal count
);

    // Maximum counter value: 2^WIDTH - 1 (all ones)
    localparam MAX_COUNT = {WIDTH{1'b1}};  // e.g., 8'hFF for WIDTH=8

    // Internal signals for next count value
    wire [WIDTH-1:0] count_next;
    wire             at_max;
    wire             at_min;

    // Detect terminal conditions
    assign at_max = (count == MAX_COUNT);  // Counter at maximum value
    assign at_min = (count == {WIDTH{1'b0}});  // Counter at zero

    // Compute next count value based on direction
    // When counting up and at max, wrap to 0
    // When counting down and at min, wrap to max
    assign count_next = up_down ? (count + {{(WIDTH-1){1'b0}}, 1'b1}) :
                                  (count - {{(WIDTH-1){1'b0}}, 1'b1});

    // Sequential logic: update counter on rising clock edge
    always @(posedge clk) begin
        if (!rst_n) begin
            // Synchronous reset: set counter to zero
            count <= {WIDTH{1'b0}};
        end else if (enable) begin
            // Count only when enabled
            count <= count_next;
        end
        // else: hold current value (enable=0)
    end

    // Overflow: counting up, at max, and enabled (will wrap next cycle)
    // This signal is valid in the cycle BEFORE the wrap occurs
    assign overflow  = enable & up_down & at_max;

    // Underflow: counting down, at min, and enabled (will wrap next cycle)
    assign underflow = enable & ~up_down & at_min;

    // Terminal count: at the end of the counting range
    assign tc = up_down ? at_max : at_min;

endmodule


/*
 * Testbench for the Up/Down Counter
 * ===================================
 * 
 * This testbench verifies:
 * 1. Reset behavior
 * 2. Counting up with overflow detection
 * 3. Counting down with underflow detection
 * 4. Enable/disable functionality
 * 5. Direction change mid-count
 *
 * To simulate with Icarus Verilog:
 *     iverilog -o counter_tb counter-verilog.v
 *     vvp counter_tb
 *     gtkwave counter_tb.vcd   (optional: view waveforms)
 */

module counter_tb;

    // Use a small width (4 bits) for manageable simulation
    parameter TB_WIDTH = 4;

    reg                     clk;
    reg                     rst_n;
    reg                     enable;
    reg                     up_down;
    wire [TB_WIDTH-1:0]     count;
    wire                    overflow;
    wire                    underflow;
    wire                    tc;

    // Instantiate the Device Under Test (DUT)
    up_down_counter #(
        .WIDTH(TB_WIDTH)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .enable(enable),
        .up_down(up_down),
        .count(count),
        .overflow(overflow),
        .underflow(underflow),
        .tc(tc)
    );

    // Clock generation: 10ns period (100 MHz)
    initial clk = 0;
    always #5 clk = ~clk;

    // Dump waveforms for viewing
    initial begin
        $dumpfile("counter_tb.vcd");
        $dumpvars(0, counter_tb);
    end

    // Test sequence
    initial begin
        $display("=== Up/Down Counter Testbench (WIDTH=%0d) ===", TB_WIDTH);
        $display("Time\tRst\tEn\tU/D\tCount\tOF\tUF\tTC");
        $monitor("%0t\t%b\t%b\t%b\t%0d\t%b\t%b\t%b",
                 $time, rst_n, enable, up_down, count,
                 overflow, underflow, tc);

        // --- Test 1: Reset ---
        rst_n   = 0;       // Assert reset
        enable  = 0;
        up_down = 1;       // Up direction
        #20;               // Hold reset for 2 clock cycles

        // --- Test 2: Release reset, count up ---
        rst_n = 1;         // Release reset
        enable = 1;        // Enable counting
        up_down = 1;       // Count up
        #200;              // Count for 20 cycles (will overflow at count=15)

        // --- Test 3: Disable counting ---
        enable = 0;
        #30;               // Counter should hold its value
        enable = 1;        // Re-enable
        #20;

        // --- Test 4: Switch to count down ---
        up_down = 0;       // Count down
        #200;              // Count down through zero (underflow)

        // --- Test 5: Reset during counting ---
        rst_n = 0;
        #10;
        rst_n = 1;
        #50;

        $display("\n=== Testbench Complete ===");
        $finish;
    end

endmodule
