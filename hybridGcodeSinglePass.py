class ANSI:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    UNDERLINE = '\033[4m'

# load gcode
while True:
    try:
        filename = input("Enter .gcode filename: ").strip()
        # validate file directory and readability
        with open(filename, "r") as infile:
            infile.readline()
        print(ANSI.OKGREEN + "   File " + filename + " found." + ANSI.ENDC)
        break
    except FileNotFoundError:
        print(ANSI.FAIL + "Invalid filename, try again." + ANSI.ENDC)

# define process names
processPrinting = input("Enter printing process name: ")
processMachining = input("Enter machining process name: ")

# from my understanding, the z axis needs to be flipped to machine in the right direction (feed direction). this should flip the part upside down and i'm not completely sure how the nozzle doesnt collide with the bed.

# with open(filename, 'r') as infile, open(filename + "-hybrid.gcode", 'w'):
#     firstNonComment = None
#     for line in file:
#         if firstNonComment == None
            

