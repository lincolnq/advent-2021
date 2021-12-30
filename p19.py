"""Strategy:

a) 
Within each scanner's beacons, find the Manhattan distance between all pairs 
of beacons.

Arbitrarily designate the 2 beacons with the shortest distance as the AB pair.

Find the midpoint between those 2 beacons, and use that as the Center.

Now find the Manhattan distance between the Center and all remaining 
beacons. Sort the beacons based on their distance to Center.

See what scanner distances look like; we can probably see correspondences
from this point on.


NOTES: strategy a didn't work too well - at least, of the 5 scanners in 
sample19b, it was only able to match 2 of them based on the AB pair.
It might be revivable, but let's look at some other options.


Strategy b:
For each axis: Pick out the values of all beacons along this axis.
Subtract from each other axis of each other beacon, and look for the most
common value in the result. If there are lets say 12 of the same, then
they are prob overlapping.

lets look at 
[1,3,5]
vs
[99,103,105]

transform to 
set{0,2,4}
set{0,4,6}
intersect: {0,4} size 2

that's pretty good

but what if we pick an outlier that's not part of the overlap and so
the offsets are wrong?
we have no overlap

So, we will just take all pairs diffs along the axis. Create a set of those diffs.
Intersect the set with each axis for other beacons. If the % match is high
enough then the axes probably match. Then try to align the axes.


"""

from helpers import *
from dataclasses import dataclass
import typing as T
import numpy


parser = Split('\n\n') ** (
    Sections('-\n',
        title=Re('--- scanner $$ --') ** int,
        body=Lines() ** Tuple() ** int
    ))

rawscans = parser.parse(open('sample19b.txt').read())
print(rawscans)

# By convention, a BeaconPos is a 3d vector of ints.
BeaconPos = numpy.ndarray

@dataclass
class Scan:
    scanno: int
    beacons: T.List[BeaconPos]

    # process1 helpers
    keyBeacons: T.Optional[T.Tuple[BeaconPos, BeaconPos]] = None
    center: T.Optional[BeaconPos] = None

    def fingerprint(self):
        # returns list of beacons distances only
        return [x[0] for x in self.beacons]


    # process2 helpers
    beaconAxisDiffs: T.Optional[T.List[T.Set[int]]] = None

def mandist(a: BeaconPos, b: BeaconPos):
    """Manhattan distance between a and b"""
    return sum(abs(b-a))

def preprocessScan1(rawscan):
    """Convert a rawscan into a Scan by following the first steps 
    of the strategy."""

    beacons = [numpy.fromiter(v, dtype=int) for v in rawscan['body']]
    # print(beacons)

    allBeaconPairs = [(a,b) for (ai, a) in enumerate(beacons) for b in beacons[ai+1:]]
    minpair = None
    minmd = 99999999
    for (a,b) in allBeaconPairs:
        md = mandist(a,b)
        if md == minmd:
            print(f"md from {a} to {b} = {md}, equals {minmd} prior")
        if md < minmd:
            minmd = md
            minpair = (a,b)
    
    (ca, cb) = minpair
    centerpoint = (ca+cb)/2
    #print(centerpoint)

    dists_and_beacons = [(mandist(b, centerpoint), b) for b in beacons]

    result = Scan(
        scanno=rawscan['title'][0],
        beacons=dists_and_beacons, #FIXME
        keyBeacons=(ca, cb),
        center=centerpoint
    )
    return result

def preprocessScan(rawscan):
    beacons = [numpy.fromiter(v, dtype=int) for v in rawscan['body']]
    
    allBeaconPairs = [(a,b) for (ai, a) in enumerate(beacons) for b in beacons[ai+1:]]
    sets = []
    for axis in range(len(beacons[0])):
        axisSet = set()
        for (a,b) in allBeaconPairs:
            axisSet.add(abs(b[axis] - a[axis]))
        sets.append(axisSet)

    return Scan(
        scanno=rawscan['title'][0],
        beacons=beacons,
        beaconAxisDiffs=sets
    )


scans = [preprocessScan(r) for r in rawscans]
print(len(scans[0].beaconAxisDiffs))
for ixs, scan1 in enumerate(scans):
    for scan2 in scans[ixs+1:]:
        intcs = []
        for set1 in scan1.beaconAxisDiffs:
            for set2 in scan2.beaconAxisDiffs:
                intc = len(set1 & set2)
                intcs.append(intc)
        print(f"compare {scan1.scanno} vs {scan2.scanno}: ints={sorted(intcs)}")


#    print(s.fingerprint())
