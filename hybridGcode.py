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

class process:
    def __init__(self, layer, process):
        self.layer = layer
        self.process = process


def cleanLine(line):
    # removes leading and trailing whitespace
    return line.strip()

# file reading



# first pass for indexing

linesSkip = []

class writeSkip:
    def __init__(self, reason, lineStart, lineEnd=None):
        self.reason = reason
        self.lineStart = lineStart
        self.lineEnd = lineEnd

with open(filename, 'r') as inFile:
    currentProcess = 'Setup'
    for lineNum, line in enumerate(inFile):
        
        # check if first line is a comment
        if(lineNum == 0 and line[0] == ';'):
            linesSkip.append(writeSkip("firstComment", 0))

        keywords = line.strip().split(' ')

        if(keywords[0] == ';' and keywords[1] == 'process'):
            print(keywords, lineNum)

        if(keywords[0] == ';' and keywords[1] == 'layer'):
            print(keywords, lineNum)

# second pass for modifying

with open(filename, 'r') as inFile, open(filename.split('.')[0]+"_temp."+filename.split('.')[1], 'w') as outTempFile:
    for lineNum, line in enumerate(inFile):
        # cleans line
        workingLine = line.strip()

        # replacement operations
        workingLine = workingLine.replace(" E", " A-").replace(" Z", " Z-").replace("--", "-")

        # write to file
        outTempFile.write(workingLine + "\n")

# third pass for removing lines

print(linesSkip[0].lineEnd)