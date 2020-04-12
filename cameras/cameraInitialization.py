import numpy as np
import sys

grid = []
radius, gridX, gridY = 0, 0, 0
viewedByCamera, positionCoveredBy = [], []
def readGrid(filename):
    global gridX, gridY, radius, grid, viewedByCamera, positionCoveredBy
    with open(filename) as fp:
        line = fp.readline()
        gridX, gridY = [int(el.strip()) for el in line.split(',')]
        line = fp.readline()
        radius = int(line[0])
        for i in range(gridX):
            line = fp.readline()
            l = [int(el.strip()) for el in line.split(',')]
            grid.append(l)
    viewedByCamera = [[[] for x in range(gridY)] for y in range(gridX)]
    positionCoveredBy = [[[] for x in range(gridY)] for y in range(gridX)]



# This function checks whether a candidate position is covered by a camera
# pos: point we place the camera.
# candidate: position we want to determine if it can be viewed by the camera
def validityTest(pos, candidate):
    # pos and candidate are on the same row
    if pos[0] == candidate[0]: 
        if pos[1] < candidate[1]:
            yStart = pos[1]
            yEnd = candidate[1]
        else:
            yStart = candidate[1]
            yEnd = pos[1]

        for j in range(yStart, yEnd + 1):
            if grid[pos[0]][j] == 0:
                return 0
    # pos and candidate are on the same column
    elif pos[1] == candidate[1]:
        if pos[0] < candidate[0]:
            xStart = pos[0]
            xEnd = candidate[0]
        else:
            xStart = candidate[0]
            xEnd = pos[0]

        for i in range(xStart, xEnd + 1):
            if grid[i][pos[1]] == 0:
                return 0
    # pos and candidate are on different row and column
    else:
        # l1: line connecting pos and candidate
        # we obtain the angle l1 has with the xx' axis
        a1 = float(pos[1] - candidate[1]) / (pos[0] - candidate[0])
        angle1 = np.degrees(np.arctan([abs(a1)]))
        xStart = min(pos[0], candidate[0])
        xEnd = max(pos[0], candidate[0])
        yStart = min(pos[1], candidate[1])
        yEnd = max(pos[1], candidate[1])

        for i in range(xStart, xEnd + 1):
            for j in range(yStart, yEnd + 1):
                if grid[i][j] == 0:
                    # l2: line connecting pos and testing point (i, j)
                    # similarly, we obtain the angle l2 has with the xx' axis
                    if j == pos[1]:
                        angle2 = 0
                    elif i == pos[0]:
                        angle2 = 90
                    else:
                        a2 = float(j - pos[1]) / (i - pos[0])
                        angle2 = np.degrees(np.arctan([abs(a2)]))
                    # if the angle between l1 and l2 is less than 30 degrees,
                    # and the testing point is wall(0), we determine that this
                    # wall obstructs the ability of the camera to view the candidate
                    if abs(angle1 - angle2) < 30:
                        return 0

    return 1

# This function places a camera at a certain point(pos) and determines which
# positions are covered by it
def placeCamera(pos):
    for i in range(max(pos[0] - radius, 0), min(pos[0] + radius + 1, gridX)):
        for j in range(max(pos[1] - radius, 0), min(pos[1] + radius + 1, gridY)):
            candidate = (i, j)
            if candidate != pos and grid[i][j] != 0:
                if validityTest(pos, candidate) == 1:
                    viewedByCamera[pos[0]][pos[1]].append(candidate)
                    positionCoveredBy[i][j].append(pos)

# This function proceeds to place a camera at every possible point
def tryCameras(filename):
    readGrid(filename)

    for i in range(gridX):
        for j in range(gridY):
            if grid[i][j] == 0:
                continue
            pos = (i, j)
            placeCamera(pos)

def calculateMaxMinCoverage():
    maxMinCoverage = gridX * gridY
    for i in range(gridX):
        for j in range(gridY):
            n = len(positionCoveredBy[i][j])
            if n > 0 and n < maxMinCoverage:
                maxMinCoverage = n
    return maxMinCoverage

def copyViewedByCamera():
    return viewedByCamera.copy()

def copyPositionCoveredBy():
    return positionCoveredBy.copy()
