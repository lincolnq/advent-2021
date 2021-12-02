from dataclasses import dataclass
import dataclasses

test = '''forward 5
down 5
forward 8
up 3
down 8
forward 2
'''

#lines = test.strip().split('\n')
lines = open('in2.txt').read().strip().split('\n')
def parse(l):
    sp = l.split()
    return (sp[0], int(sp[1]))

instructions = [parse(l) for l in lines]

print(instructions)

@dataclass
class Model:
    hpos: int
    aim: int
    depth: int


pos = Model(0, 0, 0)
for i in instructions:
    if i[0] == 'forward':
        pos = dataclasses.replace(pos, hpos=pos.hpos + i[1], depth=pos.depth + pos.aim * i[1])
    elif i[0] == 'up':
        pos = dataclasses.replace(pos, aim=pos.aim - i[1])
    elif i[0] == 'down':
        pos = dataclasses.replace(pos, aim=pos.aim + i[1])

print(pos)
print(pos.hpos * pos.depth)