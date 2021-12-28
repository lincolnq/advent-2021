sample = '''..#.#..#####.#.#.#.###.##.....###.##.#..###.####..#####..#....#..#..##..###..######.###...####..#..#####..##..#.#####...##.#.#..#.##..#.#......#.###.######.###.####...#.##.##..#..#..#####.....#.#....###..#.##......#.....#..#..#..##..#...##.######.####.####.#.#...#.......#..#.#.#...####.##.#......#..#...##.#.##..#...##.#.##..###.#......#.#.......#.#.#.####.###.##...#.....####.#..#..#.##.#....##..#.####....##...##..#...#......#.#.......#.......##..####..#...#.#.#...##..#.#..###..#####........#..####......#..#

#..#.
#....
##..#
..#..
..###
'''

from helpers import *

parser = Sections(map=Matrix(), image=Matrix())

#sects = parser.parse(sample)
sects = parser.parse(open('in20.txt').read())
print(sects)

maparr = sects['map'].reshape((-1,))
print(maparr)
print(len(maparr))

def b2i(bs):
    """Binary array to integer, left to right"""
    result = 0
    for b in bs:
        result *= 2
        result += 1 if b else 0
    return result

def output(m):
    print('\n'.join(''.join(m[ri]) for ri in range(m.shape[0])))

def enhance(i, map, fill):
    i2 = numpy.pad(i, 2, constant_values=fill)
    i3 = numpy.pad(i, 1, constant_values=fill)
    #print(i2)

    for rowi in range(1, i2.shape[0] - 1):
        for coli in range(1, i2.shape[1] - 1):
            threesq = i2[rowi-1:rowi+2, coli-1:coli+2]
            ix = b2i(threesq.reshape((-1,)) == '#')
            i3[rowi - 1,coli - 1] = map[ix]

    #output(i3)

    # also compute new fill
    if fill == '#':
        newfill = map[511]
    else:
        newfill = map[0]

    return i3, newfill

im = sects['image']
fill = '.'

for i in range(50):
    im,fill = enhance(im, maparr, fill)
    print(f'-- with {fill} around --')

print(numpy.count_nonzero(im == '#'))