sample = """2199943210
3987894921
9856789892
8767896789
9899965678
"""

#data = sample
data = open('in9.txt').read()

lines = [list(map(int, c)) for c in data.strip().split('\n')]

print(lines)
nrow = len(lines)
ncol = len(lines[0])

def neighbors(pos):
    # yields list of neighbor positions to a given row,col
    (row, col) = pos
    if row > 0:
        yield (row - 1, col)
    if row < nrow - 1:
        yield (row + 1, col)
    if col > 0:
        yield (row, col - 1)
    if col < ncol - 1:
        yield (row, col + 1)

def get(pos):
    (row, col) = pos
    return lines[row][col]

def findLows():
    lows = []
    for row in range(nrow):
        for col in range(ncol):
            pos = (row, col)
            val = get(pos)
            if all(val < get(x) for x in neighbors(pos)):
                print(f"low @ {pos}: {val}")
                lows.append(pos)

    return lows

lows = findLows()

def flood(pos):
    result = set()
    edge = set()
    result.add(pos)
    edge.add(pos)
    while len(edge) > 0:
        pos = edge.pop()
        ns = [x for x in neighbors(pos) if x not in result and get(x) != 9]
        edge.update(ns)
        result.update(ns)

    return result


#print(f"sum of risk = {sum(lows)}")
floods = []
for pos in lows:
    fp = flood(pos)
    print(f"flood from {pos} = size {len(fp)}: {fp}")
    floods.append((pos, len(fp)))

top3 = sorted(floods, key=lambda x: x[1], reverse=True)[:3]
print(top3)
print(f"prod of top3 sizes = {top3[0][1] * top3[1][1] * top3[2][1]}")