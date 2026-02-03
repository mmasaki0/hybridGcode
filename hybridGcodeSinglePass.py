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

# operation functions

class layerProcess:
    def __init__(self, layer, process):
        self.layer = layer
        self.process = process


def cleanLine(line):
    # removes leading and trailing whitespace
    return line.strip()

# file reading

# first pass reads and identifies layers and processes
with open(filename, 'r') as infile:
    print('')

with open(filename, 'r') as infile:
    previousLine = None
    for line in infile:
        lineProcessing = line
        
        lineProcessing = cleanLine(lineProcessing)
        
        # check if first comment block ends

        # 

        # save current line to be readible in next line
        previousLine = lineProcessing


