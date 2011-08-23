#!/usr/bin/python
from datetime import datetime
import logging
import sys

COMMENT_CHARS = ['#','//']
INSTRUCTION_WIDTH = 16
IMMEDIATE_BITS = 6

OPCODES = {'and':'0000',
           'or':'0000',
           'xor':'0000',
           'sll':'0000',
           'srl':'0000',
           'add':'0000',
           'sub':'0000',
           'slt':'0000',
           'addiu':'0001',
           'subiu':'0010',
           'addi':'0011',
           'subi':'0100',
           'j':'0101',
           'jr':'0110',
           'jal':'0111',
           'beq':'1000',
           'bne':'1001',
           'lw':'1010',
           'sw':'1011',
           'overflow':'1100'
          }
            
ALUCODES = {'and':'000',
            'or':'001',
            'xor':'010',
            'sll':'011',
            'srl':'100',
            'add':'101',
            'sub':'110',
            'slt':'111'
           }

REGISTERS = {'$0':'000',
             '$1':'001',
             '$2':'010',
             '$3':'011',
             '$4':'100',
             '$5':'101',
             '$6':'110',
             '$7':'111'
            }

LABELS = {}
            
def main(argv=None):
    
    # Load arguments dynamically
    if argv is None:
        argv = sys.argv
        
    # Exit if args != 2
    # argv[0] is the name of the script you're running, so chop it off before counting
    if (len(sys.argv[1:]) != 2):
        sys.exit("Syntax: python assembler.py infile outfile")

    # Exit if args equal each other (would overwrite input file)
    if (argv[1] == argv[2]):
        sys.exit("Error: Input and output filenames are the same!")
    
    # Check if file exists, and if so, open it
    if fileExists(argv[1]):
        inFile = open(argv[1],'r')
        print "Opened %s successfully." % (argv[1])
    else:
        sys.exit("Error: The input file could not be read!")

    lineNum = 0
    instructions = []
    valid = True
        
    for line in inFile:
        # increase line counter by 1
        lineNum += 1
        
        # remove comments from line
        newLine = removeComments(line, COMMENT_CHARS)
        # if the resulting line is empty, skip it
        newLine = newLine.strip()
        if (newLine == ""):
            continue

        # lowercase the line
        newLine = newLine.lower()
        # split the line into separate elements
        splitLine = newLine.split()
        lineElements = len(splitLine)
        
        # process line based on number of elements
        if (lineElements == 1):
            success = processOneElement(splitLine[0], (len(instructions)), lineNum)
            valid = valid and success
        elif (lineElements == 2):
            result = processTwoElements(splitLine, lineNum)
            if (result == None):
                valid = False
            else:
                instructions.append(result)
        elif (lineElements == 4):
            result = processFourElements(splitLine, lineNum)
            if (result == None):
                valid = False
            else:
                instructions.append(result)
        else:
            logging.error('%d: Could not parse instruction - invalid number of elements' % lineNum)
            valid = False
    inFile.close()
    
    # run another pass to set labels to their addresses
    # note that invalid instructions are left in the list
    for line in instructions:
        if (line[0] in OPCODES):
            if (line[-1] in LABELS):
                line[0] = OPCODES[line[0]]
                line[-1] = LABELS[line[-1]]
            else:
                logging.error('Label \'%s\' is undefined' % line[-1])
                valid = False

    # check to see if the file assembled without errors
    if valid:
        print "Build succeeded."
        output = generateOutput(instructions)
        success = writeToFile(argv[2], output)
        if success:
            print "Output file written to %s." % (argv[2])
        else:
            print "Error: Output file could not be written"
    else:
        print "Build failed."
    
    return 0

def fileExists(filename):
    try:
        file = open(filename)
        return True
    except IOError as e:
        return False
    
def removeComments(line, commentChars):
    for char in commentChars:
        index = line.find(char)
        if (index == -1):
            return line
        else:
            return line[:index]
    
def processOneElement(element, pointsTo, lineNum):
    ''' Processes labels '''
    if (element[-1] == ":"):
        label = element[:-1]
        if label not in LABELS:
            isValid = checkSigned(pointsTo,lineNum)
            if (isValid):
                pointsTo = convertSignedDecToBin(pointsTo)
                LABELS[label] = pointsTo
            else:
                logging.error('%d:Label points to an invalid location (%s)' % (lineNum, pointsTo))
        else:
            logging.error('%d:Label has already been defined' % lineNum)
            return False
    else:
        logging.error('%d:Label is missing semicolon' % lineNum)
        return False
    return True

def processTwoElements(splitLine, lineNum):
    ''' Processes J-Type instructions '''
    opcode = splitLine[0]
    immediate = splitLine[1]
    
    if opcode not in OPCODES:
        logging.error('%d: Invalid opcode' % lineNum)
        return None
    if (opcode == 'j'):
        return [opcode,'000000',immediate]
    if (opcode == 'jal'):
        if (immediate in REGISTERS):
            return [OPCODES[opcode],REGISTERS[immediate].zfill(12)]
        else:
            logging.error('%d: Invalid register for JAL' % lineNum)
    return splitLine
    
def processFourElements(splitLine, lineNum):
    ''' Processes R-Type instructions and I-Type instructions '''
    opcode = splitLine[0]
    rd = splitLine[1]
    rs = splitLine[2]
    rt = splitLine[3]
    
    if opcode not in OPCODES:
        logging.error('%d: Invalid opcode' % lineNum)
        return None
    if ((rd in REGISTERS) and (rs in REGISTERS)):
        if (opcode in ['and','or','xor','sll','srl','add','sub','jr','slt','overflow']):   
        # make sure all the register names are valid
            if ((rt in REGISTERS)):
                return [OPCODES[opcode],REGISTERS[rd],REGISTERS[rs],REGISTERS[rt],ALUCODES.get(opcode, '000')]
            else:
                logging.error('%d: Invalid register name' % lineNum)    
        elif (opcode in ['addiu','subiu','addi','subi','beq','bne','lw','sw']):
            # check numbers in ops that don't use labels
            if (opcode in ['addiu','subiu']):
                validNum = checkUnsigned(rt, lineNum)
                if (validNum):
                    number = convertUnsignedDecToBin(rt)
                    return [OPCODES[opcode],REGISTERS[rd],REGISTERS[rs],number]
            elif (opcode in ['addi','subi','lw','sw']):
                validNum = checkSigned(rt, lineNum)
                if (validNum):
                    number = convertSignedDecToBin(rt)
                    return [OPCODES[opcode],REGISTERS[rd],REGISTERS[rs],number]
            else:
                # leave opcode unconverted to note that reparsing is needed on the next pass
                return [opcode,REGISTERS[rd],REGISTERS[rs],rt]
    else:
        logging.error('%d: Invalid register name' % lineNum)  
    return None 

def checkUnsigned(rt, lineNum):
    rt = int(rt)
    if (rt != float(rt)):
        logging.error('%d: Can\'t use floating point numbers' % lineNum)
        return False        
    if (rt < 0):
        logging.error('%d: Unsigned instructions can\'t use negative numbers' % lineNum)
        return False
    if (rt > 63):
        logging.error('%d: Unsigned numbers are limited to 6 bits (0 to 63)' % lineNum)
        return False
    return True
    
def checkSigned(rt, lineNum):
    rt = int(rt)
    if (rt != float(rt)):
        logging.error('%d: Can\'t use floating point numbers' % lineNum)
        return False
    if ((rt < -32) or (rt > 31)):
        logging.error('%d: Unsigned numbers are limited to 6 bits (-32 to 31)' % lineNum)
        return False
    return True

def convertUnsignedDecToBin(number):
    number = int(number)
    # remove the '0b' that python prepends to binary numbers
    number = bin(number)[2:]
    return number.zfill(IMMEDIATE_BITS)
    
def convertSignedDecToBin(number):
    number = int(number)
    if (number < 0):
        number = bin(number)[3:]
        while (len(number) < IMMEDIATE_BITS):
            number = number[0] + number
        return number
    else:
        return bin(number)[2:].zfill(IMMEDIATE_BITS)

def generateOutput(instructions):
    out = '-- File created using Derek Guenther and Greg Schafer\'s assembler\n'
    out += '-- %s\n' % datetime.now()
    out += 'WIDTH = %s;\n' % (INSTRUCTION_WIDTH)
    out += 'DEPTH = %s;\n\n' % (len(instructions))
    out += 'ADDRESS_RADIX = UNS;\n'
    out += 'DATA_RADIX=BIN;\n\n'
    out += 'CONTENT BEGIN\n'
    
    count = 0
    for line in instructions:
        out +=  '\t%s:\t %s;\n' % (count,''.join(line))
        count += 1
        
    out += 'END;'
    return out
    
def writeToFile(filename, output):
    try:
        f = open(filename, 'w')
        f.write(output)
        f.close()
        return True
    except:
        logging.error("The output file could not be written.")
        return False
        
if __name__ == "__main__":
    sys.exit(main())
