sample = '''v...>>.vv>
.vv>>.vv..
>>.>v>...v
>>v>>.>.v.
v>v.vv.v..
>.>>..v...
.vv..>.>v.
v.v..>>v.v
....v..v.>
'''

#sample = '...>>>>>...'

from helpers import *
#parsed = Matrix().parse(sample)
parsed = Matrix().parse(open('in25.txt').read())

print(parsed)

def output(m):
    print('\n'.join(''.join(m[ri]) for ri in range(m.shape[0])))

def stepHerd(m, char, axis):
    herd = m == char
    lookahead = numpy.roll(herd, 1, axis)
    movedHerd = lookahead & (m == '.')
    # ok, all herd members at movedHerd should move, which means they vacate their original spots
    origSpots = numpy.roll(movedHerd, -1, axis)

    result = m[:]
    result[origSpots] = '.'
    result[movedHerd] = char
    return result, numpy.count_nonzero(movedHerd)

def step(m):
    m,moved = stepHerd(m, '>', 1)
    m,moved2 = stepHerd(m, 'v', 0)
    return m,moved+moved2

def part1(m):
    output(m)
    for i in range(1000):
        #print("--step--")
        m,moved = step(m)
        #output(m)
        if moved == 0:
            print(f"done after {i+1} steps")
            break
        #else:
            #print(f"moved {moved}")



part1(parsed)