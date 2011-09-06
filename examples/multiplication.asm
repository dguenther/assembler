# Multiplication Asm Program
# Authors:
#	Derek Guenther
#	Greg Schafer
#
#------------------------------------------------------------------
# Pseudocode:
# 	count = 0
# 	loop
#		if (pb2)
#			read dipswitch and store to memory+count
#			count++
#			if (count == 2)
#				break
# 	load val1 from memory+0
# 	load val2 from memory+1
# 	product = 0
# 	for (i = 0; i < 8; i++)
#		if ((2^i & val1) != 0)
#			testproduct = product + val2 << i
#			if (testproduct < product)
#				overflow_occurred = true
#			product = testproduct
# 	if overflow_occurred
#		write to decimal point
# 	write to 7-segment display
#
#------------------------------------------------------------------
#
# Register usage:
# 	$1 = pb2 status/product, $2/$3 = dips vals, $4 = testproduct/loopcondition,
# 	$5 = counter, $6 = overflow flag, $7 = constants
#
#------------------------------------------------------------------
#
# Program:
#

init:				# some initialization (label not needed)
	addi $5 $0 0		# set register 5 (counter) to zero
	addi $7 $0 1		# set register 7 to 1
	
inloop:				# input loop (wait for right push button to be pushed)
	lw $1 $5 1			# read from right push button
	beq $1 $0 inloop	# if push button is up (== zero) keep looping

read-ds:			# read dip switch value (label not needed)
	lw $2 $0 0			# push button is down, so load the value of the dip switch=
	sw $2 $5 10  		# store that value to mem[10]+counter
	addi $5 $5 1		# increment the counter
	beq $5 $7 inloop	# if count == 1 (1 value has been read) jump back to input loop

mul:				# prepare for multiplication of input values
	lw $2 $0 10		    # load 1st dip switch value (val1) into reg2
	lw $3 $0 11		    # load 2nd dip switch value (val2) into reg3
	addi $1 $0 0		# set register 1 (product) to zero
	addi $4 $0 0		# set register 4 (testproduct) to zero
	addi $5 $0 0		# set register 5 (counter) to zero
	
mul-iter:			# start of multiplication evaluation loop
	sll $4 $7 $5		# shift 1 left by the loop counter and store in reg4 ($4 = 2^i)
	and $4 $4 $2		# select the i-th bit of reg2 (val1)
	beq $4 $0 mul-iterB	# if that bit is zero, goto mul-iterB (does i++ and i < 8)
	sll $4 $3 $5		# else shift reg3 (val2) left by i
	add $4 $4 $1		# add product to testproduct
	slt $6 $4 $1		# if testproduct < product, overflow occurred
	addi $1 $4 0		# store testproduct in product
mul-iterB:			# end of loop (increments counter and checks loop condition)
	addi $5 $5 1		# increment loop-counter
	addi $4 $0 7		# set reg4 to loop end condition check
	bne $5 $4 mul-iter	# if the loop-counter != 7, continue looping

display:			# calculation complete, display results
	sw $6 $0 2			# stores value of reg6 (overflow flag) to right decimal point
	sw $1 $0 0			# stores value of reg1 (product) to the display
	j init				# loop program!	
	