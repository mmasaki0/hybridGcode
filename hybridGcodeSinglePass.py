class ANSI:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    UNDERLINE = '\033[4m'

# load gcode
while True:
    try:
        filename = input("Enter filename: ").strip()
        file = open(filename, "r")
        print(ANSI.OKGREEN + "   File " + filename + " found." + ANSI.ENDC)
        break
    except FileNotFoundError:
        print(ANSI.FAIL + "Invalid filename, try again." + ANSI.ENDC)

# define process names
processPrinting = input("Enter printing process name: ")
processMachining = input("Enter machining process name: ")



file.close()