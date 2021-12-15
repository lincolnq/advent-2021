from helpers import *
from io import StringIO

sample = '''NNCB

CH -> B
HH -> N
CB -> H
NH -> C
HB -> C
HC -> B
HN -> C
NN -> C
BH -> H
NC -> B
NB -> B
BN -> B
BB -> N
BC -> B
CC -> N
CN -> C
'''

#data = sample
data = open('in14.txt').read()

parser = Sections(
    template=Id, 
    rules=Lines() ** Re('$$ -> $$')
    )

s = parser.parse(data)
rules = dict(s['rules'])

from collections import defaultdict

def compile(s):
    result = defaultdict(lambda: 0)
    for i in range(len(s) - 1):
        chars = s[i:i+2]
        result[chars] += 1

    return result


def step(polymer, rules):
    result = defaultdict(lambda: 0)
    for pair, count in polymer.items():
        midchar = rules.get(pair)
        if midchar:
            newpair1 = pair[0] + midchar
            result[newpair1] += count
            newpair2 = midchar + pair[1]
            result[newpair2] += count
        else:
            result[pair] += count
    return result

polymer = compile(s['template'])
print(polymer)
for i in range(40):
    polymer = step(polymer, rules)

    print(polymer)

from collections import Counter
elems = Counter()
for (pair, count) in polymer.items():
    # add the first of each pair
    elems[pair[0]] += count
# add the final character
elems[s['template'][-1]] += 1
mc = elems.most_common()
print(mc)
print(mc[0][1] - mc[-1][1])