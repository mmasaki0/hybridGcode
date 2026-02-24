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
    def __init__(self, process, lineStart):
        self.process = process
        self.lineStart = lineStart

# feature class
class feature:
    def __init__(self, feature, lineStart):
        self.feature = feature
        self.lineStart = lineStart
    
class layer:
    def __init__(self, layer, lineStart):
        self.feature = layer
        self.lineStart = lineStart

# file reading
processes = []
features = []
layers = []

multipass = False

readSkip = []
writeSkip = []
writeInsert = {}
machiningFeedRate = "F288"
zHopHeight = "Z-50"

firstComments = []

with open(filename, 'r') as inFile:
    lines = [line.strip() for line in inFile]

#prepass remove empty lines
for lineNum, line in enumerate(lines):
    if len(line) < 1:
        readSkip.append(lineNum)
for index in range(0, len(readSkip)):
    del lines[readSkip[index] - index]

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
    
    if keywords[0] == ';' and keywords[1] == "feature":
        features.append(feature(" ".join(keywords[2:]), lineNum))

    elif keywords[0] == ';' and keywords[1] == "layer":
        layers.append(layer(keywords[2], lineNum))
        # print(lineNum, lines[lineNum])

writeSkip.extend(firstComments)

if len(processes) > 3:
    multipass = True

currentProcess = ""
currentFeature = ""

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
    
    # iterate through processes to see which process its in
    for processNum in range(0, len(processes)):
        if lineNum == processes[processNum].lineStart:
            currentProcess = processes[processNum].process
            # print(currentProcess)
    
    # iterate through features to see which feature its in
    for featureNum in range(0, len(features)):
        if lineNum == features[featureNum].lineStart:
            currentFeature = features[featureNum].feature
            # print(currentFeature)

    if currentProcess == processMachining and keywords[0] != ';':
        matches = [keyword for keyword in keywords if re.match("F", keyword)]
        if len(matches) == 1:
            keywords[keywords.index(matches[0])] = machiningFeedRate
            lines[lineNum] = " ".join(keywords)
    if currentProcess == processMachining and currentFeature == "skirt":
        writeSkip.append(lineNum)
        # print("skirt at ", lineNum)

# by process modifications
for processNum in range(0, len(processes) - 1):
    print("process:", processes[processNum].process)

    currentProcess = processes[processNum]
    nextProcess = processes[processNum + 1]

    # check for machining process
    if currentProcess.process == processMachining:

        # insert Z rise before each machining process
        writeInsert[currentProcess.lineStart - 1] = "G1 " + zHopHeight

        lineStartOffset = 0
        lineEndOffset = -1

        # iterates through process lines until first G line found
        for lineNum in range(0, nextProcess.lineStart - currentProcess.lineStart):
            if lines[currentProcess.lineStart + lineNum][0] == 'G':
                lineStartOffset = lineNum
                break

        # reverses lines using found offset
        lineSwapMin = currentProcess.lineStart + lineStartOffset
        lineSwapMax = nextProcess.lineStart + lineEndOffset
        print(lineSwapMin, lineSwapMax)
        print(0, math.ceil((lineSwapMax - lineSwapMin) / 2))
        for lineNum in range(0, math.ceil((lineSwapMax - lineSwapMin) / 2)):
            temp = lines[lineSwapMin + lineNum]
            lines[lineSwapMin + lineNum] = lines[lineSwapMax - lineNum]
            lines[lineSwapMax - lineNum] = temp
            print("swapped", lineSwapMin + lineNum, lineSwapMax - lineNum)
            if lineSwapMin + lineNum in writeSkip:
                if lineSwapMax - lineNum in writeSkip:
                    #if both in writeskip, swap
                    skipTemp = lineSwapMin + lineNum
                    writeSkip[writeSkip.index(lineSwapMin + lineNum)] = lineSwapMax - lineNum
                    writeSkip.append(skipTemp)
                    print("writeskip swapped", lineSwapMin + lineNum,  lineSwapMax - lineNum)
                else:
                    #else rewrite only one
                    writeSkip[writeSkip.index(lineSwapMin + lineNum)] = lineSwapMax - lineNum
                    print("writeskip replaced", lineSwapMin + lineNum, lineSwapMax - lineNum)
            
        # if multipass:
        #     # loop through process and add Z reset and Z revert
        #     writingZ = True
        #     maxZ = None
        #     nextZ = None

        #     for lineNum in range(nextProcess.lineStart, currentProcess.lineStart, -1):
        #         keywords = lines[lineNum].split(' ')
        #         if len(keywords) > 5 and keywords[0] == ';' and keywords[1] == "layer":
        #             maxZ = nextZ = float(keywords[5])
        #             break

        #     for lineNum in range(currentProcess.lineStart + 2, nextProcess.lineStart):
        #         keywords = lines[lineNum].split(' ')

        #         # change nextZ at every layer comment
        #         if len(keywords) > 2 and keywords[0] == ';' and keywords[1] == "layer":
        #             if nextZ == None :
        #                 nextZ = -50
        #                 writingZ=True
        #             else:
        #                 nextZ -= 1
        #                 writingZ = True
                    
                

        #         # check if first x y line in layer
        #         if writingZ and isinstance(nextZ, float) and len(keywords) >= 4 and keywords[0] == "G1" and keywords[1][0] == 'X' and keywords[2][0] == 'Y':
        #             writeInsert[lineNum] = "G1 Z-" + str(nextZ)
        #             writingZ = False

        #     writeInsert[nextProcess.lineStart - 1] = "G1 Z-" + str(maxZ) + " ; bob"

# write file
with open(filename.split('.')[0]+"_hybrid."+filename.split('.')[1], 'w') as outFile:
    for lineNum, line in enumerate(lines):
        if lineNum not in writeSkip:
            outFile.write(line + "\n")

            if lineNum in writeInsert:
                outFile.write(writeInsert[lineNum] + "\n")
        
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    outFile.write("; G-Code Hybridized by Masaki Maruo\n; " + timestamp)

print(ANSI.OKGREEN + "   File " + filename.split('.')[0]+"_hybrid."+filename.split('.')[1] + " written." + ANSI.ENDC)