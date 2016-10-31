#########################################################################################
#Purpose: STATUS_PDU_Decoder.py script parses the hex dump, recognises the SUFIs present,
#         parses the components and prints the output in console.
#Input  : Hex dump corresponding to the STATUS PDU.
#Author : Shailesh kaushik
#Date   : October 24, 2016
#########################################################################################

import sys
import time
from string import whitespace

#Following Module strips whitespaces, linefeed, tabs and carriage return characters from the hex dump string provided.
def strip_white_spaces(string):
    return string.translate(None, "\n '\n\r'\t")

#Following module converts the hex dump string into a binary string.
def hex_to_binary():
    global hex_string
    
    binary_string = bin(int(hex_string, 16))[2:].zfill(len(hex_string)*4)
    return binary_string

#Following module decodes the binary string as a NO_MORE SUFI and re assigns the binary string at the end of the NO_MORE SUFI
#so that next SUFI can be decoded if present.
def decode_NO_MORE():
    global binary_string
    
    print "\nSUFI Type: NO_MORE"
    binary_string = binary_string[4:]

#Following module decodes the binary string as a WINDOW SUFI and re assigns the binary string at the end of the WINDOW SUFI
#so that next SUFI can be decoded if present.
def decode_WINDOW():
    global binary_string
    
    print "\n\nSUFI Type: WINDOW"
    print "WSN(Window Size number): %d" % (int(binary_string[4:16], 2))
    binary_string = binary_string[16:]

#Following module decodes the binary string as a ACK SUFI and re assigns the binary string at the end of the ACK SUFI
#so that next SUFI can be decoded if present.
def decode_ACK():
    global binary_string
    
    print "\n\nSUFI Type: ACK"
    print "LSN (Last Sequence Number): %d" % (int(binary_string[4:16], 2))
    binary_string = binary_string[16:]

#Following module decodes the binary string as a BITMAP SUFI and re assigns the binary string at the end of the BITMAP SUFI
#so that next SUFI can be decoded if present.
def decode_BITMAP():
    global binary_string
    
    print "\n\nSUFI Type: BITMAP"
    bitmap_length = (int(binary_string[4:8], 2))
    print "Number of Bitmaps: %d " % (bitmap_length + 1)
    fsn = (int(binary_string[8:20], 2))
    print "FSN (first Sequence Number): %d" % fsn
    print "Bitmap: %s" % binary_string[20: 20 + (bitmap_length + 1) * 8]

#Following Block makes a list of Sequence numbers for which NACK was received based on the Bitmap field present in binary string
#from position 20 to {20 + Number 0f bitmaps * 8}
    nack_list = []
    for x in range(20, 20 + (bitmap_length + 1) * 8):
        if binary_string[x] == "0":
            nack_list.append(fsn + x - 20)
    print "%d Nacks received for sequence numbers: %s" % (len(nack_list), nack_list)

#Following block reprints the nack list in aggregated order. For example, In place of prints 1,2,3,4 it prints 1 to 4.
    min = nack_list[0]
    max = nack_list[0]
    prev = nack_list[0]
    for x in nack_list[1:]:
        if (1 == x - prev):
            max = x
        else:
            print "Nacks received from %d to %d (%d)" % (min, max, max - min + 1)
            min = x
            max = x
        prev = x
    print "Nacks received from %d to %d (%d)" % (min, max, max - min + 1)
    
    binary_string = binary_string[20 + (bitmap_length + 1) * 8:]

#Following module decodes the binary string as a MRW_ACK SUFI and re assigns the binary string at the end of the MRW_ACK SUFI
#so that next SUFI can be decoded if present.
def decode_MRW_ACK():
    global binary_string
    
    print "\n\nSUFI Type: MRW_ACK"
    print "N: %d" % (int(binary_string[4:8], 2))
    print "SN_ACK: %d" % (int(binary_string[8:20], 2))
    binary_string = binary_string[20:]

#Following module decodes the binary string as a POLL SUFI and re assigns the binary string at the end of the POLL SUFI
#so that next SUFI can be decoded if present.
def decode_POLL():
    global binary_string
    
    print "\n\nSUFI Type: POLL"
    print "Poll_SN: %d" % (int(binary_string[4:16], 2))
    binary_string = binary_string[16:]

#Following module decodes the binary string as a LIST SUFI and re assigns the binary string at the end of the LIST SUFI
#so that next SUFI can be decoded if present.
def decode_LIST():
    global binary_string
    
    print "\n\nSUFI Type: LIST"
    list_length = (int(binary_string[4:8], 2))
    offset = 8
    print "LENGTH: %d" % list_length

    for x in range(1, list_length + 1):
        print "SN[%d]: %d" % (x, int(binary_string[offset:offset + 12], 2))
        print "L[%d]: %d" % (x, int(binary_string[offset + 12:offset + 16], 2))
        offset = offset + 16
    binary_string = binary_string[4 + 4 + (12 + 4) * list_length:]

#Following module decodes the binary string as a RLIST SUFI and re assigns the binary string at the end of the RLIST SUFI
#so that next SUFI can be decoded if present.
def decode_RLIST():
    global binary_string
    erroneous_SN_list = []
    error_burst_indicator = 0
    error_burst_infimum = 0
    
    print "\n\nSUFI Type: RLIST"
    num_of_CW = (int(binary_string[4:8], 2))
    fsn = (int(binary_string[8:20], 2))
    offset = 20
    print "LENGTH: %d" % num_of_CW
    print "FSN: %d" % fsn
    erroneous_SN_list.append(fsn)
    error_burst_infimum = fsn

#Following block decodes the number based on the values of CWs
#CW '0001' represents Error burst indicator
#If the LSB of last CW is not 1 or if it represents Error burst indicator then RLIST SUFI encoding is invalid.
    number = fsn
    for x in range(1, num_of_CW + 1):
        if (binary_string[offset:offset + 4] == '0001'):
            error_burst_indicator = 1
            error_burst_infimum = number
            print "CW[%d]: %s : Error Burst Indicator" % (x, binary_string[offset:offset + 4])
        elif (x == num_of_CW and binary_string[offset + 3] != '1') or (binary_string[offset:offset + 4] == '0001' and x == num_of_CW):
            print "The encoding of RLIST SUFI is invalid. Exiting now..."
            time.sleep(3)
            exit(1)
        elif (binary_string[offset + 3] == '1'):
            print "CW[%d]: %s" % (x, binary_string[offset:offset + 4])
            number = number * 2 + int(binary_string[offset:offset + 3],2)
            if (error_burst_indicator != 1):
                erroneous_SN_list.append(number - erroneous_SN_list[-1])
                number = erroneous_SN_list[-1]
            else:
                error_burst_indicator = 0
                for x in range (error_burst_infimum + 1, number - erroneous_SN_list[-1] + 1):
                    erroneous_SN_list.append(x)
                number = erroneous_SN_list[-1]
        else:
            print "CW[%d]: %s" % (x, binary_string[offset:offset + 4])
            number = number * 2 + int(binary_string[offset:offset + 3],2)
        
        offset = offset + 4

#Following block reprints the erroneous_SN_list in aggregated order. For example, In place of prints 1,2,3,4 it prints 1 to 4.
    min = erroneous_SN_list[0]
    max = erroneous_SN_list[0]
    prev = erroneous_SN_list[0]
    for x in erroneous_SN_list[1:]:
        if (1 == x - prev):
            max = x
        else:
            print "Erroneous sequence numbers are from %d to %d (%d)" % (min, max, max - min + 1)
            min = x
            max = x
        prev = x
    print "Erroneous sequence numbers are from %d to %d (%d)" % (min, max, max - min + 1)
    print erroneous_SN_list
    
    binary_string = binary_string[4 + 4 + 12 + 4 * num_of_CW:]

#Following module decodes the binary string as a MRW SUFI and re assigns the binary string at the end of the MRW SUFI
#so that next SUFI can be decoded if present.
def decode_MRW():
    global binary_string
    
    print "\n\nSUFI Type: MRW"
    num_of_MRW_fields = (int(binary_string[4:8], 2))
    offset = 8
    print "LENGTH: %d", num_of_MRW_fields

    for x in range(1, num_of_MRW_fields + 1):
        print "SN_MRW[%d]: %d" % (x, int(binary_string[offset:offset + 12],2))
        offset = offset + 12

    print "N_Length: %d" % (int(binary_string[offset:offset + 4],2))
    binary_string = binary_string[4 + 4 + 12 * num_of_MRW_fields + 4:]

#Following Module checks the First four bits of Binary string to check the SUFI type and
#calls the relevant decoding function based on the detected SUFI type
#to decode and print the contents of the SUFI detected.
def find_SUFI_type_and_decode():
    global binary_string
    
    if (binary_string[0:4] == '0000'):
        decode_NO_MORE()
    elif(binary_string[0:4] == '0001'):
        decode_WINDOW()
    elif(binary_string[0:4] == '0010'):
        decode_ACK()
    elif(binary_string[0:4] == '0011'):
        decode_LIST()
    elif(binary_string[0:4] == '0100'):
        decode_BITMAP()
    elif(binary_string[0:4] == '0101'):
        decode_RLIST()
    elif(binary_string[0:4] == '0110'):
        decode_MRW()
    elif(binary_string[0:4] == '0111'):
        decode_MRW_ACK()
    elif(binary_string[0:4] == '1000'):
        decode_POLL()
    else:
        print "\nHex dump does not correspond to valid SUFI "

#Following Module takes an input hex string representing a status PDU.
#Changes it into Binary string.
#Confirms that the hex string represents a Status PDU.
#Calls find_SUFI_type_and_decode module until all the SUFIs present in the status PDU dump have been decoded.
def main():
    global hex_string
    global binary_string
    
    input_hex_string = raw_input("\nPlease enter the hex dump: ")

    hex_string = strip_white_spaces(input_hex_string)

#Following block checks if the hex_string is valid.
    try:
        int(hex_string, 16)
    except ValueError:
        print " The string is invalid! Exiting..."
        time.sleep(3)
        exit(1)

    binary_string = hex_to_binary()
    
    if (binary_string[0:4] != '0000'):
        print "Provided dump do not represent STATUS PDU.Exiting now!!!"
        time.sleep(3)
        exit(1)
    else:
        binary_string = binary_string[4:]

    while (len(binary_string) > 0):
        find_SUFI_type_and_decode()

    while(1):
        choice =  raw_input("\n\nDecode another SUFI: y/n  ")

        if (choice == 'y' or choice =='Y'):
            main()
        elif (choice == 'n' or choice == 'N'):
            exit(0)
        else:
            print "\nwrong choice..!! Please enter y or n"


hex_string = "00"
binary_string = bin(int(hex_string,16))[2:].zfill(8)

main()
