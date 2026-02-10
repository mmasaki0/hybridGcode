import math
import re
import datetime

# console output text colors
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

# process class 
class process:
    def __init__(self, process, lineStart, lineEnd=None):
        self.process = process
        self.lineStart = lineStart

# file reading
processes = []
writeSkip = []
machiningFeedRate = "F288"

firstComments = []

with open(filename, 'r') as inFile:
    lines = [line.strip() for line in inFile]

# first pass indexing
for lineNum, line in enumerate(lines):
    keywords = line.split(' ')

    # add first comments to writeSkip
    if keywords[0] == ';':
        if lineNum == 0 or len(firstComments) != 0 and lineNum == firstComments[-1] + 1:
            firstComments.append(lineNum)
    
    # indexes processes
    if keywords[0] == ';' and keywords[1] == "process":
        processes.append(process(keywords[2], lineNum))
    elif keywords[0] == ';' and keywords[1] == "layer" and keywords[2] == "end":
        processes.append(process(keywords[2], lineNum))

writeSkip.extend(firstComments)

currentProcess = ""

for lineNum, line in enumerate(lines):
    keywords = line.split(' ')
    

    if keywords[0] != ';':
        workingLine = line

        # replaces E motor with A motor reversed (extruder)
        # workingLine = workingLine.replace(" E", " A-")
        # flips coordinate system upside down (machines counterclockwise by right hand rule)
        workingLine = workingLine.replace(" Z", " Z-").replace("--", "-")

        lines[lineNum] = workingLine
        keywords = lines[lineNum].split(' ')
    
    # iterate through processes to see which process its in and lower feedrate if machining
    for processNum in range(0, len(processes)):
        if lineNum == processes[processNum].lineStart:
            currentProcess = processes[processNum].process
            print(currentProcess)
    if currentProcess == processMachining and keywords[0] != ';':
        matches = [keyword for keyword in keywords if re.match("F", keyword)]
        if len(matches) == 1:
            keywords[keywords.index(matches[0])] = machiningFeedRate
            lines[lineNum] = " ".join(keywords)

# reverse machining process lines
for processNum in range(0, len(processes) - 1):

    currentProcess = processes[processNum]
    nextProcess = processes[processNum + 1]

    # check for machining process
    if currentProcess.process == processMachining:
        lineStartOffset = 0
        lineEndOffset = -1
        # iterates through process lines until first G line found
        for lineNum in range(0, nextProcess.lineStart - currentProcess.lineStart):
            if lines[currentProcess.lineStart + lineNum][0] == 'G':
                lineStartOffset = lineNum
                break

        # print(nextProcess.lineStart + lineEndOffset - currentProcess.lineStart - lineStartOffset)
        for lineNum in range(0, math.ceil((nextProcess.lineStart + lineEndOffset - currentProcess.lineStart - lineStartOffset) / 2) ):
            temp = lines[currentProcess.lineStart + lineStartOffset + lineNum]
            lines[currentProcess.lineStart + lineStartOffset + lineNum] = lines[nextProcess.lineStart + lineEndOffset - lineNum]
            lines[nextProcess.lineStart + lineEndOffset - lineNum] = temp

# write file
with open(filename.split('.')[0]+"_hybrid."+filename.split('.')[1], 'w') as outTempFile:
    for lineNum, line in enumerate(lines):
        if lineNum not in writeSkip:
            outTempFile.write(line + "\n")
        
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    outTempFile.write("; G-Code Hybridized by Masaki Maruo\n; " + timestamp)

print(ANSI.OKGREEN + "   File " + filename.split('.')[0]+"_hybrid."+filename.split('.')[1] + " written." + ANSI.ENDC)