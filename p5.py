import re

test = '''0,9 -> 5,9
8,0 -> 0,8
9,4 -> 3,4
2,2 -> 2,1
7,0 -> 7,4
6,4 -> 2,0
0,9 -> 2,9
3,4 -> 1,4
0,0 -> 8,8
5,5 -> 8,2
'''

#data = test
#canvasx,canvasy = 10,10

data = open('in5.txt').read()
canvasx,canvasy = 1000,1000

inLines = data.strip().split('\n')

def parsePoint(line):
    m = re.match(r'(\d+),(\d+) -> (\d+),(\d+)', line)
    return ((int(m.group(1)), int(m.group(2))), (int(m.group(3)), int(m.group(4))))


lines = [parsePoint(x) for x in inLines]

#print(lines)


# mutable canvas
canvas = [[0] * canvasx for i in range(canvasy)]

def draw(canvas):
    result = '\n'.join(''.join(str(x) if x > 0 else '.' for x in row) for row in canvas)
    print(result)


def drawDot(canvas, point):
    (x,y) = point
    canvas[y][x] += 1

def drawLine(canvas, points):
    ((x1,y1),(x2,y2)) = points
    deltax = 0 if x1 == x2 else 1 if x2 > x1 else -1
    deltay = 0 if y1 == y2 else 1 if y2 > y1 else -1

    # walk from first to second point
    drawDot(canvas, (x1,y1))
    while x1 != x2 or y1 != y2:
        x1 += deltax
        y1 += deltay
        drawDot(canvas, (x1, y1))

for line in lines:
    drawLine(canvas, line)

#draw(canvas)

num2s = 0
for row in canvas:
    num2s += sum(1 if x>=2 else 0 for x in row)

print(f"{num2s} 2 or greaters")