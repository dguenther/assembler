Assembler.py
============

Assembler syntax: python assembler.py infile outfile

* Single-line comments are allowed, either '#' or '//' may be used
* Multi-line comments are not allowed.
* Labels must be defined on a line by themselves. They point to the next line of assembly code that occurs.
* Assembly instruction tokens are separated by whitespace only.

Instructions
------------

* R-Type instructions are written in assembly like so:
	opcode destination source source
	
	For example::
	
	 sll $4 $7 $5
	 and $4 $4 $2

* I-Type instructions are written in assembly like so:
	opcode destination source immediate
	
	For example::
	
	 addiu $1 $1 2
	 lw $2 $1 0
	
* J-Type instructions are written in assembly like so:
	opcode immediate
	
	For example::
	
	 j loop
	 jal $1