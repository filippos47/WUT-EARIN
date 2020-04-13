# how many genepools we will spawn
populations = 5
# if after this number of rounds we have not managed to get a better
# fitness score than before, we terminate our program
patience = 500
# fitness function's constants
a = 1
b = 0.000001
# how many genes are we gonna sample
sampleSize = 2
# for each step we produce one child
step = 40
# every time this number of rounds passes we migrate between populations
migrationTime = 10
# for every 'mutationRatio' children we apply a pure mutation
mutationRatio = 80
