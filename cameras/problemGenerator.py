import random
import os
from cameraInitialization import tryCameras
from cameraInitialization import calculateMaxMinCoverage

dimsMsg = 'State the dimensions of your random grid, leaving a space between them.' \
    ' Both dimensions should be at least 3, as your room will have outside walls.'
radiusMsg = 'Would you like to specify the camera radius? y/n'
yRadiusMsg = 'Type your custom camera radius. It should obviously be bigger than ' \
    'zero.'
nRadiusMsg = 'The camera radius has been set to '
roomMsg = 'Would you like to produce an empty room, or a completely random room? ' \
    'empty/random\n(It should be noted that the completely random room version ' \
    'is much slower as dimensions grow. Also, the possible values for minimum ' \
    'coverage may be limited or not available at all)'
minCovMsg = 'What should be the minimum coverage of each position of the grid?' \
   ' Value should be larger than 0 and up to '
errorMsg = 'Please read the instructions carefully.'


print(dimsMsg)
while True:
    N, M = map(int, input().split())
    if N > 2 and M > 2:
        break
    print(errorMsg)

print(radiusMsg)
while True:
    readRadius = input()
    if readRadius == 'y':
        print(yRadiusMsg)
        while True:
            radius = int(input())
            if radius > 0:
                break
            print(errorMsg)
        break
    elif readRadius == 'n':
        radius = random.randrange(max(N, M) - 1)
        print(nRadiusMsg + '{}.'.format(radius))
        break
    print(errorMsg)

print(roomMsg)
while True:
    mode = input()
    if mode == 'random' or mode == 'empty':
        break
    print(errorMsg)

filename = "grid{}X{}-R{}.txt".format(N, M, radius)
with open(filename, "w") as fp:
    fp.write("{},{}\n".format(N, M))
    fp.write("{}\n".format(radius))
    for i in range(M - 1):
        fp.write("0,")
    fp.write("0\n")

    for i in range(1, N - 1):
        fp.write("0,")
        for j in range(1, M - 1):
            if mode == 'empty':
                fp.write("1,")
            else:
                fp.write("{},".format(random.randrange(2)))
        fp.write("0\n")

    for i in range(M - 1):
        fp.write("0,")
    fp.write("0\n")

if mode == 'random':
    tryCameras(filename)
    maxMinCoverage = calculateMaxMinCoverage()
elif mode == 'empty':
    maxMinCoverage = min(radius + 1, N - 2) * min(radius + 1, M - 2) - 1

print(minCovMsg + '{}.'.format(maxMinCoverage))
while True:
    minCoverage = int(input())
    if minCoverage > 0 and minCoverage <= maxMinCoverage:
        break
    print('Please read the instructions carefully.')

with open(filename, "a") as fp:
    fp.write("{}\n".format(minCoverage))

finalFilename = "grid{}X{}-R{}-MC{}.txt".format(N, M, radius, minCoverage)
os.rename(filename, finalFilename)
