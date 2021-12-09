sample = """be cfbegad cbdgef fgaecd cgeb fdcge agebfd fecdb fabcd edb | fdgacbe cefdb cefbgd gcbe
edbfga begcd cbg gc gcadebf fbgde acbgfd abcde gfcbed gfec | fcgedb cgb dgebacf gc
fgaebd cg bdaec gdafb agbcfd gdcbef bgcad gfac gcb cdgabef | cg cg fdcagb cbg
fbegcd cbd adcefb dageb afcb bc aefdc ecdab fgdeca fcdbega | efabcd cedba gadfec cb
aecbfdg fbg gf bafeg dbefa fcge gcbea fcaegb dgceab fcbdga | gecf egdcabf bgf bfgea
fgeab ca afcebg bdacfeg cfaedg gcfdb baec bfadeg bafgc acf | gebdcfa ecba ca fadegcb
dbcfg fgd bdegcaf fgec aegbdf ecdfab fbedc dacgb gdcebf gf | cefg dcbef fcge gbcadfe
bdfegc cbegaf gecbf dfcage bdacg ed bedf ced adcbefg gebcd | ed bcgafe cdgba cbgef
egadfb cdbfeg cegd fecab cgb gbdefca cg fgcdab egfdb bfceg | gbdfcae bgc cg cgb
gcafb gcf dcaebfg ecagb gf abcdeg gaef cafbge fdbac fegbdc | fgae cfgab fg bagce
"""

# segments:
#  11
# 2  3
#  44
# 5  6
#  77
allnums = frozenset([1,2,3,4,5,6,7])
segs = {
    0: [1,3,6,7,5,2], 
    1: [3,6],
    2: [1,3,4,5,7],
    3: [1,3,4,6,7],
    4: [2,4,3,6],
    5: [1,2,4,6,7],
    6: [1,2,5,7,6,4],
    7: [1,3,6],
    8: [1,2,3,4,5,6,7],
    9: [4,2,1,3,6,7],
}

import z3

def parseLine(l):
    (all10, num) = [parseNumSeq(s) for s in l.split('|')]
    return (all10, num)

def parseNumSeq(s):
    return s.strip().split()

#data = sample
data = open('in8.txt').read()
lines = [parseLine(x) for x in data.strip().split('\n')]


def addExample(s, vars, example):
    '''Constrain solver 's' by adding the given example digit.
    `vars` is a mapping of character to the z3 variable with that name.

    The way we do this is by taking all the digits this example
    could possibly refer to (depending on its length), and constraining
    the solver accordingly.

    e..g, if given 'cdfbe'
    it must be a 2,3, or 5
    we add a top level 'Or' constraint -- either it's a 2,3, or 5
    the constraint "it is digit X" means: for all the letters in
    the example (cdfbe), all must be lit in digit X.
    "all must be lit" (but we don't know which) is equivalent to
    "each one must not be the unlit segments".
    So that's an 'And' constraint, saying that none of cdfbe can be
    the left two segments (2 or 5).
    '''

    exampleVars = [vars[c] for c in example]
    cs = []
    for _, v in segs.items():
        if len(v) == len(example):
            # figure out the segments not in-use
            notinuse = allnums - set(v)
            # constrain that the exampleVars are not the notinuse ones
            c = z3.And([
                var != d
                for var in exampleVars
                for d in notinuse
            ])
            cs.append(c)    

    # ok, we now need to 'Or' together all those cs
    # since could be any of those digits
    s.add(z3.Or(cs))


def solveAll10(all10):
    '''create a Solver, constrain it appropriately,
    add all examples from `all10` digit examples to it,
    then solve, returning the mapping of letter
    to highlighted segment.
    '''
    s = z3.Solver()

    atog = z3.Ints('a b c d e f g')
    vars = {n: v for (n,v) in zip('abcdefg', atog)}
    # goal is to assign uniquely a->g to 1->7 given constraints
    s.add(z3.Distinct(*atog))
    s.add([x >= 1 for x in atog])
    s.add([x <= 7 for x in atog])

    for example in all10:
        addExample(s, vars, example)

    s.check()
    m = s.model()
    result = {}
    for k in s.model():
        result[str(k)] = m[k].as_long()
    return result

def interpSeg(lit):
    '''Interpret the segment, given the lit segment IDs [1-7].
    Returns the decimal digit 0-9.'''
    for k,v in segs.items():
        if set(v) == set(lit):
            return k

print(lines[0][0])

result = 0

for (all10, numstrs) in lines:
    key = solveAll10(all10)
    print(key)
    print(numstrs)
    #numstr = numstrs[0]
    #breakpoint()
    #interpSeg([key[c] for c in numstr])
    numdigits = ''.join(str(interpSeg([key[c] for c in numstr])) for numstr in numstrs)
    num = int(numdigits)
    print(num)
    result += num

print(f"Total result = {result}")
    
