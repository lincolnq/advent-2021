sample = '''5483143223
2745854711
5264556173
6141336146
6357385478
4167524645
2176841721
6882881134
4846848554
5283751526
'''

#ata = sample
data = open('in11.txt').read()

lines = [list(map(int, c)) for c in data.strip().split('\n')]

print(lines)
nrow = len(lines)
ncol = len(lines[0])


def neighbors(pos):
    # yields list of neighbor positions to a given row,col
    # (not including self)
    (row, col) = pos
    minrow = row - 1 if row > 0 else row
    maxrow = row + 1 if row < nrow - 1 else row
    mincol = col - 1 if col > 0 else col
    maxcol = col + 1 if col < ncol - 1 else col

    for irow in range(minrow, maxrow + 1):
        for icol in range(mincol, maxcol + 1):
            if (irow,icol) != pos:
                yield (irow, icol)

def get(pos):
    (row, col) = pos
    return lines[row][col]

print(list(neighbors((1,1))))

def printboard(lines):
    print('\n'.join(''.join(str(x) for x in row) for row in lines))

def timeStep(lines):
    """simple timestep to increment"""
    return [[x + 1 for x in row] for row in lines]

def processFlashes(lines):
    """increment all neighbors of all flashed octopi, avoid dupe flashes;
    then reset all flashed to 0"""
    flashes = set()

    while True:
        flashed = False
        # go through
        for row,items in enumerate(lines):
            for col,v in enumerate(items):
                pos = (row, col)
                if pos not in flashes and v > 9:
                    flashed = True
                    flashes.add(pos)
                    for (nr, nc) in neighbors(pos):
                        lines[nr][nc] += 1
        if not flashed:
            break
    
    print(f"{len(flashes)} flashes this step: {flashes}")

    for (row,col) in flashes:
        lines[row][col] = 0
    
    return (lines, len(flashes))


def step(lines):
    lines = timeStep(lines)
    return processFlashes(lines)

#flashes = 0
for i in range(100000):
    (lines, newFlashes) = step(lines)
    if newFlashes == nrow*ncol:
        print(f"stopping at step {i+1} with all flashes!")
        break

