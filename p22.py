sample1='''on x=10..12,y=10..12,z=10..12
on x=11..13,y=11..13,z=11..13
off x=9..11,y=9..11,z=9..11
on x=10..10,y=10..10,z=10..10
'''

sample2='''on x=-20..26,y=-36..17,z=-47..7
on x=-20..33,y=-21..23,z=-26..28
on x=-22..28,y=-29..23,z=-38..16
on x=-46..7,y=-6..46,z=-50..-1
on x=-49..1,y=-3..46,z=-24..28
on x=2..47,y=-22..22,z=-23..27
on x=-27..23,y=-28..26,z=-21..29
on x=-39..5,y=-6..47,z=-3..44
on x=-30..21,y=-8..43,z=-13..34
on x=-22..26,y=-27..20,z=-29..19
off x=-48..-32,y=26..41,z=-47..-37
on x=-12..35,y=6..50,z=-50..-2
off x=-48..-32,y=-32..-16,z=-15..-5
on x=-18..26,y=-33..15,z=-7..46
off x=-40..-22,y=-38..-28,z=23..41
on x=-16..35,y=-41..10,z=-47..6
off x=-32..-23,y=11..30,z=-14..3
on x=-49..-5,y=-3..45,z=-29..18
off x=18..30,y=-20..-8,z=-3..13
on x=-41..9,y=-7..43,z=-33..15
on x=-54112..-39298,y=-85059..-49293,z=-27449..7877
on x=967..23432,y=45373..81175,z=27513..53682
'''

from typing import List, Tuple
from helpers import *
from dataclasses import dataclass

@dataclass
class Command:
    on: bool
    xmin: int
    xmax: int
    ymin: int
    ymax: int
    zmin: int
    zmax: int

    @classmethod
    def parse(cls, args):
        return cls(
            args[0] == 'on', 
            int(args[1]), int(args[2]),
            int(args[3]), int(args[4]),
            int(args[5]), int(args[6]))


parser = (Lines() ** Re('$$ x=%%..%%,y=%%..%%,z=%%..%%')) ** Command.parse
commands: List[Command] = parser.parse(open('in22.txt').read())


@dataclass(frozen=True)
class Cube:
    # lo is the minimum x/y/z coord.
    # hi is the maximum plus one; e.g., these are Integer Cubes and we use the
    # idiomatic Python "zero:Length" ranging schema
    lo: numpy.ndarray       # 3-vector
    hi: numpy.ndarray       # 3-vector

    def __post_init__(self):
        if (self.hi < self.lo).any():
            raise ValueError(f"invalid cube initialized: {self}")

    def __len__(self):
        """Volume of this Cube"""
        #print(f"computing len of cube {self}")
        return numpy.product(self.hi - self.lo)

    def __bool__(self):
        """This Cube is truthy if it has any volume"""
        return len(self) > 0

    def __mul__(self, rhs):
        """Intersect"""
        return intersectCubes(self, rhs)

    def __sub__(self, rhs):
        """Subtract"""
        return subtractCubes(self, rhs)

    def __add__(self, rhs):
        """Union"""
        return unionCubes(self, rhs)
    
    def __eq__(self, rhs):
        return (self.lo == rhs.lo).all() and (self.hi == rhs.hi).all()        

Zero = Cube(numpy.zeros(3, dtype=numpy.int32), numpy.zeros(3, dtype=numpy.int32))


def intersectCubes(cube1: Cube, cube2: Cube) -> Cube:
    """Returns the Cube which is the intersection of the 2 cubes.
    
    Returns Zero if the cubes do not overlap. If the cubes touch but don't intersect,
    we don't return Zero - but instead a zero-volume cube representing the touchpoint(s)
    """
    try:
        return Cube(numpy.fmax(cube1.lo, cube2.lo),
                    numpy.fmin(cube1.hi, cube2.hi))

    except ValueError:  # cube's post_init catches an invalid cube
        return Zero
    

def divideCube(c: Cube, dim: int, value: int) -> 'Tuple[Cube, Cube]':
    """Returns two Cubes created by dividing c along dimension 0/1/2 [x/y/z]
    at the given break point.

    If one of the cubes would be of zero size (because the value is outside the range)
    then the corresponding result Cube is Zero.

    Always returns the cubes in the "correct order".
    """
    lo,hi = c.lo[dim], c.hi[dim]
    if value <= lo:
        return (Zero, c)
    if value >= hi:
        return (c, Zero)
    
    lo1 = c.lo.copy()
    hi1 = c.hi.copy()
    lo2 = c.lo.copy()
    hi2 = c.hi.copy()

    hi1[dim] = value
    lo2[dim] = value

    return (Cube(lo1, hi1), Cube(lo2, hi2))


def subtractCubes(base: Cube, subtrahend: Cube) -> List[Cube]:
    """Returns a list of non-overlapping Cubes with total volume <= base.
    """
    
    intersection = intersectCubes(base, subtrahend)
    # ok, so we really only need to subtract the intersection from base.
    # if no intersection, we are done
    if not intersection:
        return [base]

    doneCubes = []

    # divide by lo and hi along each axis in turn
    for axis in range(3):
        # split base along this axis for both the lo and hi of the intersection
        before, rest = divideCube(base, axis, intersection.lo[axis])
        mid, after = divideCube(rest, axis, intersection.hi[axis])

        # ok, before and after are untouched and we can simply output them
        if before:
            doneCubes.append(before)
        if after:
            doneCubes.append(after)

        # 'mid' is the remaining cube, which will be subdivided along a different
        # axis in future iterations, or (if this is the last iteration) simply dropped
        base = mid

    return doneCubes



# for part1
Cube50 = Cube(numpy.fromiter([-50,-50,-50], dtype=numpy.int32), numpy.fromiter([51,51,51], dtype=numpy.int32))

cubelist = []

for cmd in commands:
    print(cmd)
    # strategy: subtract from all existing cubes, then if cube is 'on', add ours to the end

    newcubelist = []
    newcube = Cube(numpy.fromiter([cmd.xmin, cmd.ymin, cmd.zmin], dtype=numpy.int32), 
        numpy.fromiter([cmd.xmax + 1, cmd.ymax + 1, cmd.zmax + 1], dtype=numpy.int32))

    #newcube = newcube * Cube50
    if not newcube:
        continue

    for c in cubelist:
        newcubelist.extend(c - newcube)
    
    if cmd.on:
        newcubelist.append(newcube)

    cubelist = newcubelist

vol={sum(len(x) for x in cubelist)}
print(f"total vol={vol}")