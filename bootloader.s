const N 11

addi t1, #0
read_file t2
addi fp, x0, N
addi t1, t1, #4
jalr ra, x0, loop
loop:
read_file t0, t1
sw fp, t0
addi fp, fp, #1
addi t1, t1, #4
bltu t1, t2 loop
jalr x0, N