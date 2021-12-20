#sample = '''[[[1,2],3],4]'''
sample = "[[[[[9,8],1],2],3],4]"

sampleLines = '''[[[0,[5,8]],[[1,7],[9,6]]],[[4,[1,2]],[[1,4],2]]]
[[[5,[2,8]],4],[5,[[9,9],0]]]
[6,[[[6,2],[5,6]],[[7,6],[4,7]]]]
[[[6,[0,7]],[0,9]],[4,[9,[9,0]]]]
[[[7,[6,4]],[3,[1,3]]],[[[5,5],1],9]]
[[6,[[7,3],[3,2]]],[[[3,8],[5,7]],4]]
[[[[5,4],[7,7]],8],[[8,3],8]]
[[9,3],[[9,9],[6,[4,9]]]]
[[2,[[7,7],7]],[[5,8],[[9,3],[0,2]]]]
[[[[5,2],5],[8,[3,7]]],[[5,[7,5]],[4,4]]]'''


import json
from typing import Optional
import pytest

def parse(l):
    return json.loads(l)

sfn = parse(sample)
#print(sfn)

def explodeAny(sfn, path):
    """Search (recursively) for any exploding sfn. 
    Returns the path (sequence of L/R) to the node (a pair) which explodes,
    as well as the (a,b) literals of the node.
    If no node explodes in this subtree, returns None.
    """
    match sfn:
        case [a, b]:
            #print(f'recurse')
            if len(path) >= 4:
                # this one explodes. replace it with zero.
                return (path, (a, b))
            return explodeAny(a, path + 'L') or explodeAny(b, path + 'R')
        case l:
            #print(f"l={l}")
            return None


def ixPath(c):
    """Returns the index in a pair corresponding to L or R."""
    assert len(c) == 1
    return 0 if c == 'L' else 1


def replacePath(sfn, path, f):
    """Replace the value at any path, by calling f with the current value. Mutates sfn."""
    while len(path) > 1:
        sfn = sfn[ixPath(path[0])]
        path = path[1:]

    # ok we're on the last path component, replace it
    oldval = sfn[ixPath(path[0])]
    sfn[ixPath(path[0])] = f(oldval)


def advancePath(sfn, path: str, direction: str) -> Optional[str]:
    """Find leaf node in sfn starting from `path` and moving either left or right 
    by one leaf, indicated by direction.
    
    Returns new path, or None if path cannot be incremented/decremented.
    
    Strategy for moving rightwards: Find the rightmost 'L' and change to an 'R', 
    then trace down the tree 'holding left'. Vice versa if direction is leftwards.
    """
    opposite = 'L' if direction == 'R' else 'R'
    if opposite not in path:
        # we're at the end of the line
        return None
    ri = path.rindex(opposite)
    startpath = path[:ri] + direction
    return traverseFromPathToLeaf(sfn, startpath, opposite)


def traverseFromPathToLeaf(sfn, path: str, holding: str) -> str:
    """Starting at path, traverse sfn holding either 'L' or 'R' to always go left or right.
    Returns the path to the leaf node.
    [[[1,1],[1,1]],1]
    LLL LLR LRL LRR R
    """
    assert len(holding) == 1
    for i in range(len(path)):
        sfn = sfn[ixPath(path[i])]

    while type(sfn) != int:
        sfn = sfn[ixPath(holding)]
        path = path + holding

    return path

def tryExplode(sfn):
    match explodeAny(sfn, ""):
        case (expath, (a,b)):
            #print(expath, (a,b))

            # First, we replace the exploded pair with a regular number, zero
            replacePath(sfn, expath, lambda _: 0)

            advr = advancePath(sfn, expath, 'R')
            if advr:
                replacePath(sfn, advr, lambda x: x+b)
            else:
                #print(f"{b} falls off to the right (expath={expath})")
                pass

            advl = advancePath(sfn, expath, 'L')
            if advl:
                replacePath(sfn, advl, lambda x: x+a)
            else:
                pass
                #print(f"{a} falls off to the left (expath={expath})")

            #print(sfn)
            return 'Explode'

        case _:
            return False


def trySplit(sfn):
    """Attempt to mutate sfn by splitting any splittable literal in sfn. 
    
    Returns True if any action was taken, False otherwise."""
    match sfn:
        case [int(a), _] if a >= 10:
            (s,rem) = divmod(a, 2)
            sfn[0] = [s, s+rem]
            return 'split'
        
        case [a, _] if result := trySplit(a):
            # left subtree successfully split - we're done matching
            return result

        case [_, int(b)] if b >= 10:
            (s,rem) = divmod(b, 2)
            sfn[1] = [s, s+rem]
            return 'split'

        case [_,b]:
            return trySplit(b)

        case _:
            return False

def step(sfn):
    return tryExplode(sfn) or trySplit(sfn)

def reduce(sfn):
    steps = []
    while kind := step(sfn):
        #print(f"reduce: {kind}\n{sfn}")
        steps.append(kind)
    #print(f"reduce: steps ({len(steps)})={steps}")

def mag(sfn):
    match sfn:
        case [a, b]:
            return 3*mag(a) + 2*mag(b)
        case int(x):
            return x

def assertExplodesTo(s1, s2):
    sfn = parse(s1)
    assert tryExplode(sfn)
    assert sfn == parse(s2)

def assertSplitsTo(s1, s2):
    sfn = parse(s1)
    assert trySplit(sfn)
    assert sfn == parse(s2)

def assertReducesTo(s1, s2):
    sfn = parse(s1)
    reduce(sfn)
    assert sfn == parse(s2)


def testExplode():
    assertExplodesTo('[[[[[9,8],1],2],3],4]', '[[[[0,9],2],3],4]')
    assertExplodesTo('[7,[6,[5,[4,[3,2]]]]]', '[7,[6,[5,[7,0]]]]')
    assertExplodesTo('[[6,[5,[4,[3,2]]]],1]', '[[6,[5,[7,0]]],3]')
    assertExplodesTo('[[3,[2,[1,[7,3]]]],[6,[5,[4,[3,2]]]]]', '[[3,[2,[8,0]]],[9,[5,[4,[3,2]]]]]')
    assertExplodesTo('[[3,[2,[8,0]]],[9,[5,[4,[3,2]]]]]', '[[3,[2,[8,0]]],[9,[5,[7,0]]]]')

def testSplits():
    assertSplitsTo('[[[[0,7],4],[15,[0,13]]],[1,1]]', '[[[[0,7],4],[[7,8],[0,13]]],[1,1]]')
    assertSplitsTo('[[[[0,7],4],[[7,8],[0,13]]],[1,1]]', '[[[[0,7],4],[[7,8],[0,[6,7]]]],[1,1]]')

def testSplit1():
    assertSplitsTo('[[22, 0], 15]', '[[[11,11],0],15]')

def testReduce1():
    assertReducesTo('[[[[[4,3],4],4],[7,[[8,4],9]]],[1,1]]', '[[[[0,7],4],[[7,8],[6,0]]],[8,1]]')

def testReduce2():
    assertReducesTo('[[[[[7,0],[7,7]],[[7,7],[7,8]]],[[[7,7],[8,8]],[[7,7],[8,7]]]],[7,[5,[[3,8],[1,4]]]]]', '[[[[7,7],[7,8]],[[9,5],[8,7]]],[[[6,8],[0,8]],[[9,9],[9,0]]]]')

def testReduce3():
    assertReducesTo('[[[[[7,7],[7,8]],[[9,5],[8,7]]],[[[6,8],[0,8]],[[9,9],[9,0]]]],[[2,[2,2]],[8,[8,1]]]]','[[[[6,6],[6,6]],[[6,0],[6,7]]],[[[7,7],[8,9]],[8,[8,1]]]]')

def testReduce4():
    assertReducesTo('[[[[[6,6],[6,6]],[[6,0],[6,7]]],[[[7,7],[8,9]],[8,[8,1]]]],[2,9]]', '[[[[6,6],[7,7]],[[0,7],[7,7]]],[[[5,5],[5,6]],9]]')

def testReduce5():
    assertReducesTo('[[[[[6,6],[7,7]],[[0,7],[7,7]]],[[[5,5],[5,6]],9]],[1,[[[9,3],9],[[9,0],[0,7]]]]]', '[[[[7,8],[6,7]],[[6,8],[0,8]]],[[[7,7],[5,0]],[[5,5],[5,6]]]]')

def testReduce6():
    assertReducesTo('[[[[[7,8],[6,7]],[[6,8],[0,8]]],[[[7,7],[5,0]],[[5,5],[5,6]]]],[[[5,[7,4]],7],1]]', '[[[[7,7],[7,7]],[[8,7],[8,7]]],[[[7,0],[7,7]],9]]')

def testReduce7():
    assertReducesTo('[[[[[7,7],[7,7]],[[8,7],[8,7]]],[[[7,0],[7,7]],9]],[[[[4,2],2],6],[8,7]]]', '[[[[8,7],[7,7]],[[8,6],[7,7]]],[[[0,7],[6,6]],[8,7]]]')

def testMag():
    assert mag(parse('[9,1]')) == 29
    assert mag(parse('[[9,1],[1,9]]')) == 129
    assert mag(parse('[[[[5,0],[7,4]],[5,5]],[6,6]]')) == 1137
    assert mag(parse('[[[[8,7],[7,7]],[[8,6],[7,7]]],[[[0,7],[6,6]],[8,7]]]')) == 3488

def part01(lines):

    curr = parse(lines[0])
    for nextLine in lines[1:]:
        next = parse(nextLine)
        print(f"curr {curr} + next {next} =")
        sfn = json.loads(json.dumps([curr, next]))
        reduce(sfn)
        print(sfn)
        curr = sfn

    print('-----')
    print(curr)
    print(mag(curr))

def part02(lines):
    # parse them all
    sfns = [parse(l) for l in lines]
    # generate all pairs
    bestMagnitude = 0
    for i in range(len(sfns)):
        for j in range(len(sfns)):
            if i != j:
                pair = json.loads(json.dumps([sfns[i], sfns[j]]))
                reduce(pair)
                result = mag(pair)
                if result > bestMagnitude:
                    bestMagnitude = result

    print(f'best mag={bestMagnitude}')


def main():
    #lines = sampleLines.split('\n')
    lines = open('in18.txt').read().split('\n')

    part01(lines)
    part02(lines)

main()
