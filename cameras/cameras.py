import sys
import random
from math import ceil
from cameraInitialization import tryCameras
from cameraInitialization import copyViewedByCamera
from cameraInitialization import copyPositionCoveredBy
import config


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

populations = config.populations
patience = config.patience
a = config.a
b = config.b
sampleSize = config.sampleSize
step = config.step
migrationTime = config.migrationTime
mutationRatio = config.mutationRatio
# how many genes each genepool/population has
geneSize = max(80, int(ceil(max(gridX, gridY) * 10 / populations)))


# This function evaluates how good a gene is based on two factors:
# First and foremost, the number of cameras it uses(length of the list).
# Second and less important, the sum of how many times each position
# is covered by a camera(coverage score).
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
# It initially sets the child equal to one parent, and then it proceeds to 
# replace a part of the child with a part of the second parent.
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
 
# This function fixes the newly created child, inserting mutation at user chosen rate.
def fixOrMutate(child):
    # First, we have to assess which positions are not covered enough.
    # At the same time, cameras that cover already covered enough positions
    # are kicked out.
    random.shuffle(child)
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
    # This is done by specifically adding cameras covering them, in 2 ways:
    #   a) We select cameras that cover the maximum possible amount of positions,
    # including the not covered enough one. This way we hope to eliminate as many
    # undercovered positions as possible in one go, fixing the solution.
    #   b) We select randomly cameras that cover the not covered enough position.
    # This way, we are purely mutating our solution.
    mutate = True if random.randrange(mutationRatio) < 1 else False
    while len(myMinimumGrid) > 0:
        position = list(myMinimumGrid.keys())[0]
        coverage = myMinimumGrid[position]
        if mutate:
            while True:
                cam = random.choice(positionCoveredBy[position[0]][position[1]])
                if cam not in child:
                    checkCamera(cam, myMinimumGrid)
                    child.append(cam)
                    break
        else:
            sortedList = sorted(positionCoveredBy[position[0]][position[1]], \
                key = lambda l: len(l))
            index = 0
            while True:
                cam = sortedList[index]
                if cam not in child:
                    checkCamera(cam, myMinimumGrid)
                    child.append(cam)
                    break
                index += 1

    fitness = fitnessFunction(child)
    return child, fitness

# A simple solution checker
def solutionCheck(gene):
    myMinimumGrid = minimumCoverageGrid.copy()
    for cam in gene:
        checkCamera(cam, myMinimumGrid)
    message =  1 if len(myMinimumGrid) == 0 else 0
    return message


# Here, our main program begins.
# Setting up necessary structures..
tryCameras(sys.argv[-1])
viewedByCamera = copyViewedByCamera()
positionCoveredBy = copyPositionCoveredBy()
minimumCoverageGrid = {}
for i in range(gridX):
    for j in range(gridY):
        if grid[i][j] != 0:
            minimumCoverageGrid[(i, j)] = 0
genepools = []
for i in range(populations):
    genepools.append([])

# Generating initial population(s)..
for i in range(populations):
    for j in range(geneSize):
        gene = createGene()
        genepools[i].append(gene)


peakFitness = gridX * gridY
fitnessUnchanged = 0
rounds = 0
n = geneSize 
# Evolution starts..
while True:
    rounds += 1
    # Migrating between multiple populations in a circular manner..
    if rounds % migrationTime == 0 and populations > 1:
        migrating = []
        # 2 genes are taken from each population.
        for pop in range(populations):
            genepool = genepools[pop]
            sample = []
            while len(sample) < sampleSize:
                i = random.randrange(n)
                if genepool[i] not in sample:
                    sample.append((i, genepool[i][1]))
            sample.sort(key = lambda gene: gene[1])
            i = sample[0][0] # parent1 index
            j = sample[1][0] # parent2 index
            if i > j:
                i, j = j, i
            migrating.append(genepool[i])
            migrating.append(genepool[j])
            genepool.pop(i)
            genepool.pop(j - 1)
        index = 0
        for pop in range(populations):
            if pop + 1 == populations:
                pop = -1
            genepool = genepools[pop + 1]
            genepool.append(migrating[index])
            genepool.append(migrating[index + 1])
            index += 2

    # Every population creates an amount of children depending its size.
    temp = peakFitness
    for pop in range(populations):
        genepool = genepools[pop]
        children = []
        # For every 'step' genes, we create two children.
        for i in range(0, geneSize, step):
            # Sampling random genes..
            sample = []
            while len(sample) < sampleSize:
                i = random.randrange(n)
                if genepool[i] not in sample and i not in children:
                    sample.append((i, genepool[i][1]))
            sample.sort(key = lambda gene: gene[1])
            # Selecting the 2 superior sampled genes as parents..
            p1 = sample[0][0] # parent1 index
            p2 = sample[1][0] # parent2 index

            child1 = fixOrMutate(crossover(genepool[p1][0], genepool[p2][0]))
            child2 = fixOrMutate(crossover(genepool[p1][0], genepool[p2][0]))
            # We keep the best child and the best parent.
            if genepool[p1][1] < genepool[p2][1]:
                genepool[p2] = child1 if child1[1] < child2[1] else child2
                children.append(j)
            else:
                genepool[p1] = child1 if child1[1] < child2[1] else child2
                children.append(i)

        genepool.sort(key = lambda gene: gene[1])
        if peakFitness > int(genepool[0][1]):
            peakFitness = int(genepool[0][1])
            fitnessUnchanged = 0

    # Checking if peak fitness score improved..
    if temp == peakFitness:
        fitnessUnchanged += 1
        if fitnessUnchanged > patience:
            break
    print(rounds, peakFitness)

print(genepool[0])
