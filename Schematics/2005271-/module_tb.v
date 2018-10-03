// Verilog testbench created by dumbTestbench.py
`timescale 100ns / 1ns

module agc;

reg rst = 1;
initial
  begin
    $dumpfile("agc.lxt2");
    $dumpvars(0, agc);
    # 1 rst = 0;
    # 1000 $finish;
  end

reg CLOCK = 0;
always #4.8828125 CLOCK = !CLOCK;

reg CCH34 = 0, CCH35 = 0, CCHG_ = 0, CGA22 = 0, CHWL01_ = 0, CHWL02_ = 0,
  CHWL03_ = 0, CHWL04_ = 0, CHWL05_ = 0, CHWL06_ = 0, CHWL07_ = 0, CHWL08_ = 0,
  CHWL09_ = 0, CHWL10_ = 0, CHWL11_ = 0, CHWL12_ = 0, CHWL13_ = 0, CHWL14_ = 0,
  CHWL16_ = 0, DKBSNC = 0, DKSTRT = 0, END = 0, F12B = 0, FS13 = 0, FS14 = 0,
  GOJAM = 0, HIGH0_ = 0, HIGH1_ = 0, HIGH2_ = 0, HIGH3_ = 0, PC15_ = 0,
  WCH34_ = 0, WCH35_ = 0, WCHG_ = 0, XB3_ = 0, XB4_ = 0, XT1_ = 0;

wire ADVCTR, BSYNC_, CCH13, CCH14, CH1307, DATA_, DKCTR1, DKCTR1_, DKCTR2,
  DKCTR2_, DKCTR3, DKCTR3_, DKCTR4, DKCTR4_, DKCTR5, DKCTR5_, DKDATA, DKDATB,
  DKDAT_, DLKCLR, F12B_, F14H, FS13_, LOW0_, LOW1_, LOW2_, LOW3_, LOW4_,
  LOW5_, LOW6_, LOW7_, ORDRBT, RCH13_, RCH14_, RDOUT_, WCH13_, WCH14_,
  WDORDR, WRD1B1, WRD1BP, WRD2B2, WRD2B3, d16CNT, d1CNT, d32CNT;

A22 iA22 (
  rst, CCH34, CCH35, CCHG_, CGA22, CHWL01_, CHWL02_, CHWL03_, CHWL04_, CHWL05_,
  CHWL06_, CHWL07_, CHWL08_, CHWL09_, CHWL10_, CHWL11_, CHWL12_, CHWL13_,
  CHWL14_, CHWL16_, DKBSNC, DKSTRT, END, F12B, FS13, FS14, GOJAM, HIGH0_,
  HIGH1_, HIGH2_, HIGH3_, PC15_, WCH34_, WCH35_, WCHG_, XB3_, XB4_, XT1_,
  BSYNC_, CCH13, DATA_, DKCTR2, DKCTR3, DKCTR3_, DKDAT_, DLKCLR, F12B_, FS13_,
  LOW0_, LOW1_, LOW2_, LOW3_, LOW4_, LOW5_, LOW6_, LOW7_, ORDRBT, RCH13_,
  RDOUT_, WCH13_, WDORDR, WRD1B1, WRD1BP, WRD2B2, WRD2B3, ADVCTR, CCH14,
  CH1307, DKCTR1, DKCTR1_, DKCTR2_, DKCTR4, DKCTR4_, DKCTR5, DKCTR5_, DKDATA,
  DKDATB, F14H, RCH14_, WCH14_, d16CNT, d1CNT, d32CNT
);

initial $timeformat(-9, 0, " ns", 10);
initial $monitor("%t: %d", $time, CLOCK);

endmodule