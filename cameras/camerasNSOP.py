import numpy as np
import sys
import random
from math import ceil
from cameraInitialization import tryCameras
from cameraInitialization import copyViewedByCamera
from cameraInitialization import copyPositionCoveredBy


with open(sys.argv[-1]) as fp:
    line = fp.readline()
    gridX, gridY = [int(el.strip()) for el in line.split(',')]
    line = fp.readline()
    radius = int(line)
    grid = []
    for i in range(gridX):
        line = fp.readline()
        l = [int(el.strip()) for el in line.split(',')]
        grid.append(l)
    line = fp.readline()
    minCoverage = int(line)

geneSize = int(ceil(max(gridX, gridY) * 10))
stopCriterion = 1000
genepool = []
a = 1
b = 0.000001
step = 50

# This function evaluates how good a gene is based on two factors:
# First and foremost, the number of cameras it uses.
# Second and less important, the sum of how many times each position
# is covered by a camera.
# The second factor will act as a tie breaker between solutions 
# with equal number of cameras.
def fitnessFunction(gene):
    coverageCounter = 0
    for cam in gene:
        coverageCounter += len(viewedByCamera[cam[0]][cam[1]])

    return a * len(gene) + b * coverageCounter

# This function tries to add a camera to a gene. If this camera
# is useful to the gene, it's added. 
# We define useful as covering at least one place which is not
# covered enough at the time.
def checkCamera(cam, myMinimumGrid):
    usefulCam = False
    for position in viewedByCamera[cam[0]][cam[1]]:
        if position in myMinimumGrid:
            usefulCam = True
            myMinimumGrid[position] += 1
            if myMinimumGrid[position] == minCoverage:
                myMinimumGrid.pop(position)
    return usefulCam

# This function proceeds to create a new gene. Until every position has
# at least minCoverage, it keeps adding random cams to the gene.
# Finally, it returns the newly created gene along with its fitness.
def createGene():
    myMinimumGrid = minimumCoverageGrid.copy()
    camPositions = []

    while True:
        while True:
            i = random.randrange(gridX)
            j = random.randrange(gridY)
            if grid[i][j] == 1 and (i, j) not in camPositions:
                cam = (i, j)
                break

        if checkCamera(cam, myMinimumGrid):
            camPositions.append(cam)
            if len(myMinimumGrid) == 0:
                break
    
    fitness = fitnessFunction(camPositions)
    return camPositions, fitness

# This function produces a new child, by making a crossover between 2 parents.
def crossover(parent1, parent2):
    largerParent = list(parent1) if len(parent1) > len(parent2) else list(parent2)
    smallerParent = list(parent2) if largerParent == list(parent1) else list(parent1)
    child = smallerParent
    start = random.randrange(len(smallerParent))
    stop = random.randrange(len(smallerParent))
    if start > stop:
        stop, start = start, stop
    offset = random.randrange(max(len(largerParent) - len(smallerParent), 1))
    child[start:stop] = largerParent[offset + start:offset + stop]
    return child
 
# This function fixes the newly created child, mutating it at the same time.
def fixAndMutate(child):
    # First, we have to assess which positions are not covered enough.
    # At the same time, cameras that cover already covered enough positions
    # are kicked out.
    myMinimumGrid = minimumCoverageGrid.copy()
    index = 0
    toBeDeleted = []
    deletions = 0
    for cam in child:
        if not checkCamera(cam, myMinimumGrid):
            toBeDeleted.append(index)

        index += 1
        if len(myMinimumGrid) == 0:
            while index < len(myMinimumGrid):
                toBeDeleted.append(index)
                index += 1
            break
    
    for i in toBeDeleted:
        child.pop(i - deletions)
        deletions += 1

    # Now, we are going to fix the remaining not covered enough positions.
    # This is done by specifically adding cameras covering them.
    while len(myMinimumGrid) > 0:
        position = list(myMinimumGrid.keys())[0]
        coverage = myMinimumGrid[position]
        while coverage < minCoverage:
            cam = random.choice(positionCoveredBy[position[0]][position[1]])
            if cam not in child:
                checkCamera(cam, myMinimumGrid)
                child.append(cam)
                break
            coverage += 1

    fitness = fitnessFunction(child)
    return child, fitness

# A simple solution checker
def solutionCheck(gene):
    myMinimumGrid = minimumCoverageGrid.copy()
    for cam in gene:
        checkCamera(cam, myMinimumGrid)
    message =  1 if len(myMinimumGrid) == 0 else 0
    return message


# Here, our main program begins
tryCameras(sys.argv[-1])
viewedByCamera = copyViewedByCamera()
positionCoveredBy = copyPositionCoveredBy()
minimumCoverageGrid = {}
for i in range(gridX):
    for j in range(gridY):
        if grid[i][j] != 0:
            minimumCoverageGrid[(i, j)] = 0


for i in range(geneSize):
    gene = createGene()
    genepool.append(gene)


peakFitness = gridX * gridY
fitnessUnchanged = 0
rounds = 0
n = len(genepool)
while True:
    rounds += 1
    children = []
    
    #for every 'step' genes, we create one child
    for i in range(0, geneSize, step):
        p1 = random.randrange(n)
        while p1 in children:
            p1 = random.randrange(n)
        p2 = random.randrange(n)
        while p1 == p2 or p2 in children:
            p2 = random.randrange(n)

        child1 = fixAndMutate(crossover(genepool[p1][0], genepool[p2][0]))
        child2 = fixAndMutate(crossover(genepool[p1][0], genepool[p2][0]))

        # We keep the best child and the best parent
        if genepool[p1][1] < genepool[p2][1]:
            genepool[p2] = child1 if (child1[1] < child2[1] and genepool[-1][1] / genepool[0][1] < 0.5) else child2
            children.append(j)
        else:
            genepool[p1] = child1 if (child1[1] < child2[1] and genepool[-1][1] / genepool[0][1] < 0.5) else child2
            children.append(i)

    genepool.sort(key = lambda gene: gene[1])
    if peakFitness > int(genepool[0][1]):
        peakFitness = int(genepool[0][1])
        fitnessUnchanged = 0
    else:
        fitnessUnchanged += 1
        if fitnessUnchanged > stopCriterion:
            break
    print(rounds, peakFitness)

print(genepool[0])
print(solutionCheck(genepool[0][0]))
