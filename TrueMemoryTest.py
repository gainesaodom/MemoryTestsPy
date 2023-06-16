# module for interacting with the 23k640 sram chip 
# supports reading and writing in "Byte Operation"
# supports reading status register
# does not support "Page Operation" or "Sequential Operation"
# does not support writing to status register 
# Author: Amaar Ebrahim
# Email: aae0008@auburn.edu

import spidev

# 23k640 instruction bytes - don't touch
# these variables are named according to the "instruction name" they correspond 
# to in the 23k640 datasheet 
READ = 0x03
WRITE = 0x02
RDSR = 0x05

# application-specific constant parameters
memory_size = 65536      # Number of memory cells
address_bits = 16       # Number of address bits
data_bits = 8           # Number of data bits (8 in this case, for one byte)
instruction_bits = 8    # Number of instruction bits  


# spi config
bus = 0
device = 0

spi = spidev.SpiDev()
spi.open(bus, device)


spi.mode = 0b00
spi.max_speed_hz = 5000
spi.bits_per_word = 8

# functions

def _transfer(message):
	return spi.xfer3(message)


# Reads the status of the chip
def get_status():
	response = _transfer([RDSR, 0x00])
	return response[-1]


# Reads the byte at 16-bit address `address`
def read(address):

	# if address has bits beyond bit 15, it means address is wider than 16-bits
	if (address >> 16 != 0):
		raise Error("Argument #1 `address` needs to be a 16-bit value at most")

	# first 8 bits 		- 00000101
	upper_half_of_addr = (address >> 8) & 0xFF
	lower_half_of_addr = (address & 0xFF)
	message = [READ, upper_half_of_addr, lower_half_of_addr, 0x00]

	response = _transfer(message)
	return response[-1]


# Writes a byte `value` to 16-bit address `address`
# Writing does not return anything.
def write(address, value):
	if (address >> 16 != 0):
		raise Error("Argument #1 `address` needs to be a 16-bit value at most")

	if (value >> 8 != 0):
		raise Error("Argument #2 `value` needs to be an 8-bit value at most")

	upper_half_of_addr = (address >> 8) & 0xFF
	lower_half_of_addr = (address & 0xFF)

	message = [WRITE, upper_half_of_addr, lower_half_of_addr, value, 0x00]

	_transfer(message)
	
    
def checkerboard_test(memory_size,step):
    for address in range(memory_size):
        if ((address % 2 == 0) and (step == 1)) or ((address % 2 == 1) and (step == 2)) :
            write(address, 0xAA)
        else:
            write(address, 0x55)
    for i in range(memory_size):
        readValue = read(i)
        if ((readValue != 0xAA) and (i % 2 == 0) and (step == 1)) or ((readValue != 0x55) and (i % 2 == 1) and (step == 1)):
            print(f"Checkerboard test part 1 failed at address {i}")
            return
        if ((readValue != 0xAA) and (i % 2 == 1) and (step == 2)) or ((readValue != 0x55) and (i % 2 == 0) and (step == 2)):
            print(f"Checkerboard test part 2 failed at address {i}")
            return
        
def march_A_test(memory_size):
    for address in range(memory_size):
        # M0   
        writeValue = 0x00            
        write(address, writeValue)
    for address in range(memory_size):
        # M1
        M1 = ReadZeroWriteOneZeroOne(address)
        if (M1): 
            print(f"March A test failed at address {address}")
            return
    for address in range(memory_size):
        # M2
        M2 = ReadOneWriteZeroOne(address)
        if (M2): 
            print(f"March A test failed at address {address}")
            return
    for address in reversed(range(memory_size)):
        # M3
        M3 = ReadOneWriteZeroOneZero(address)
        if (M3): 
            print(f"March A test failed at address {address}")
            return
    for address in reversed(range(memory_size)):
        # M4
        M4 = ReadZeroWriteOneZero(address)
        if (M4): 
            print(f"March A test failed at address {address}")
            return
    
def sequence_test(memory_size, datum):
    for address in range(memory_size):
        # Write datum
        write(address,datum)
    # Verify all cells
    for i in range(memory_size):
        readValue = read(i)
        if readValue != datum:
            print(f"Sequence test failed at address {i}")
            return
        
def ReadZeroWriteOneZeroOne(address): #M1

    for i in range(data_bits):

        tempValue = ((read(address)>>i) & 1)                  # read 0 
        if (tempValue!= 0): 
            return True;

        write(address, (read(address) | (1<<i)))             # write 1
        write(address, (read(address)  & ~(1<<i)))           # write 0
        write(address, (read(address) | (1<<i)))             # write 1

    return False;  

def ReadOneWriteZeroOne(address): #M2

    for i in range(data_bits):
        tempValue = ((read(address)>>i) & 1)                 # read 1 

        if (tempValue!= 1): 
            return True

        write(address, (read(address) & ~(1<<i)))            # write 0    
        write(address, (read(address) | (1<<i)))             # write 1    

    return False 

def ReadOneWriteZeroOneZero(address):

    for i in reversed(range(data_bits)):
    
        tempValue = ((read(address)>>i) & 1)                 # read 1 

        if (tempValue!= 1): 
            return True

        write(address, (read(address) & ~(1<<i)))            # write 0    
        write(address, (read(address) | (1<<i)))             # write 1
        write(address, (read(address) & ~(1<<i)))            # write 0
        
    return False 

def ReadZeroWriteOneZero(address): #M2

    for i in reversed(range(data_bits)):
        tempValue = ((read(address)>>i) & 1)                 # read 0 

        if (tempValue!= 0): 
            return True

        write(address, (read(address) | (1<<i)))             # write 1
        write(address, (read(address) & ~(1<<i)))            # write 0    

    return False 

# Perform checkerboard test
checkerboard_test(memory_size, 1)
print("Checkerboard test step 1 complete!")

checkerboard_test(memory_size, 2)
print("Checkerboard test step 2 complete!")

# Perform March A test
march_A_test(memory_size)
print("March A complete!")