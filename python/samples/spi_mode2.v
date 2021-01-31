module spi_mode2(input clk, 
           input mosi_in,
           output mosi_out,
           input sck_in, 
           output sck_out,
           input data_in,
           output data_out
         );

         assign sck_out = ~sck_r[1];
         assign mosi_out = mosi_r[1];
         assign data_out = data_r[1];

         reg [1:0] sck_r;
         reg [1:0] mosi_r;
         reg [1:0] data_r;

         always @(posedge clk) begin
           sck_r <= {sck_r[0], sck_in};
           mosi_r <= {mosi_r[0], mosi_in};
           data_r <= {data_r[0], data_in};
         end

endmodule
