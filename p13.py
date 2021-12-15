sample = """6,10
0,14
9,10
0,3
10,4
4,11
6,0
6,12
4,1
0,13
10,12
3,4
3,0
8,4
1,10
2,14
8,10
9,0

fold along y=7
fold along x=5
"""

import re

#data = sample
data = open('in13.txt').read()

dotstr,foldstr = data.strip().split('\n\n')
dots = [tuple(map(int, ps.split(','))) for ps in dotstr.split('\n')]
def parseFold(line):
    print(line)
    m = re.match(r'fold along (\w+)=(\d+)', line)
    return (m.group(1), int(m.group(2)))

folds = [parseFold(line) for line in foldstr.split('\n')]

print(dots)
print(folds)


def fold(dots, axis, foldLine):
    """Fold along axis (x or y) and foldLine. Returns new dots,
    with new coordinates along the given axis.
    """
    def foldCoord(coord, foldLine):
        assert coord != foldLine
        if coord < foldLine:
            return coord
        elif coord > foldLine:
            return 2*foldLine - coord
        
    if axis == 'x':
        return [(foldCoord(x, foldLine), y) for (x,y) in dots]
    else:
        return [(x, foldCoord(y, foldLine)) for (x,y) in dots]

def render(dots):
    maxX = max(d[0] for d in dots) + 1
    maxY = max(d[1] for d in dots) + 1

    board = [['.'] * maxX for i in range(maxY)]

    for (x,y) in dots:
        board[y][x] = '#'
    print('\n'.join(''.join(str(x) for x in line) for line in board))

render(dots)
for (axis, foldLine) in folds:
    dots = fold(dots, axis, foldLine)
    print("---")
    render(dots)
print(f"ndots={len(set(dots))}")