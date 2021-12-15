from helpers import *
import numpy
import networkx

sample = '''1163751742
1381373672
2136511328
3694931569
7463417111
1319128137
1359912421
3125421639
1293138521
2311944581
'''

tiny = '''
12
34
'''

#parsed = IntMatrix().parse(tiny)
#parsed = IntMatrix().parse(sample)
parsed = IntMatrix().parse(open('in15.txt').read())

print(parsed)

def offset_and_wrap(m, offset):
    # returns m after having added offset and wrap on [1..9]
    return ((m + offset - 1) % 9) + 1

#full = offset_and_wrap(parsed, 7)

fullrow = numpy.concatenate([offset_and_wrap(parsed, tilex) for tilex in range(5)], axis=1)
full = numpy.concatenate([offset_and_wrap(fullrow, tiley) for tiley in range(5)], axis=0)

print(full)

parsed = full

G = networkx.DiGraph()
for y in range(parsed.shape[0]):
    for x in range(parsed.shape[1]):
        if x < parsed.shape[1] - 1:
            G.add_edge((x,y), (x+1,y), weight=parsed[y,x+1])
            G.add_edge((x+1,y), (x,y), weight=parsed[y,x])
        if y < parsed.shape[0] - 1:
            G.add_edge((x,y), (x,y+1), weight=parsed[y+1,x])
            G.add_edge((x,y+1), (x,y), weight=parsed[y,x])
        G.nodes[(x,y)]['weight'] = parsed[y,x]

sp = networkx.shortest_path(G, (0,0), (parsed.shape[1]-1, parsed.shape[0]-1), weight='weight')
ws = [G.nodes[n]['weight'] for n in sp]
print(sum(ws[1:]))
