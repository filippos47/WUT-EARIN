import random
import os
from cameraInitialization import tryCameras
from cameraInitialization import calculateMaxMinCoverage

print('State the dimensions of your random grid, leaving a space between them.' \
    ' Both dimensions should be at least 3.')
while True:
    N, M = map(int, input().split())
    if N > 2 and M > 2:
        break
    print('Please read the instructions carefully.')

print('Would you like to specify the camera radius? y/n')
readRadius = input()

if readRadius == 'y':
    print('Type your custom camera radius. It should not be greater than ' \
    'the biggest dimension you specified and obviously bigger than zero.')
    while True:
        radius = int(input())
        if radius <= max(N, M) and radius > 0:
            break
        print('Please read the instructions carefully.')
else:
    radius = random.randrange(max(N, M))
    print('The camera radius has been set to {}.'.format(radius))

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
            fp.write("1,")
        fp.write("0\n")

    for i in range(M - 1):
        fp.write("0,")
    fp.write("0\n")

tryCameras(filename)
maxMinCoverage = calculateMaxMinCoverage()
print('What should be the minimum coverage of each position of the grid?' \
   ' Value should be larger than 0 and up to {}.'.format(maxMinCoverage))
while True:
    minCoverage = int(input())
    if minCoverage > 0 and minCoverage <= maxMinCoverage:
        break
    print('Please read the instructions carefully.')

with open(filename, "a") as fp:
    fp.write("{}\n".format(minCoverage))
