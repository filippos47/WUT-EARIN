# How many genepools we will spawn
populations = 5
# If after this number of rounds we have not managed to get a better
# fitness score than before, we terminate our program.
patience = 500
# Fitness function's constants
a = 1
b = 0.000001
# How many genes are we going to sample
sampleSize = 10
# For each step, a population produces two children, eventually keeping one.
step = 40
# Every time this number of rounds passes we migrate between populations.
migrationTime = 5
# For every 'mutationRatio' children we apply a pure mutation.
mutationRatio = 1
