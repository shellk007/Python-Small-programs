# This script prints the hailstone pattern for a given number
# and prints all the number in the pattern. It also counts the
# total number of entries of the pattern

#Author: Shailesh Kaushik

def print_hailstone_pattern():
    print "Please enter the number for which you want to create Hailestone pattern."

    prompt = '>'

#Following loop checks if the entry is valid or not. 
#Hailstone pattern can only be calculated for whole numbers(Positive Integers)
    while(1):
        try:
            seed = int(raw_input(prompt))
        except ValueError:
            print "Please enter a positive integer."
            continue
        if (seed <= 0):
            print "Hailstone pattern can't be calculated for 0 or negative numbers. Enter another number"
        elif(isinstance(seed, int) == True):
            break
            	
    num = seed
    count = 1
    print "%d" % num
	
#Following loop calculates and prints the next number of Hailstone pattern in each iteration until it reduses to 1.
    while(num != 1):
        if (num%2 == 0):
            num = num/2
            count += 1
            print "%d" % num
        else:
            num = num * 3 + 1
            print "%d" % num
            count += 1
    
    print "Total number in the pattern are %d" % count
    print "Would you like to check another pattern (y/n)"
    
    while(1):
        choice = raw_input(prompt)
        if (choice != 'y' and choice != 'n' and choice != 'Y' and choice != 'N'):
            print "Wrong choice!! Please enter y/n"
        elif (choice == 'y' or choice == 'Y'):
            print_hailstone_pattern()
        else:
            print " Exiting the program now..."
            exit()

print_hailstone_pattern()
