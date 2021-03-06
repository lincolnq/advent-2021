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

#rawscans = parser.parse(open('sample19b.txt').read())
rawscans = parser.parse(open('in19.txt').read())
#print(rawscans)

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
    beaconDiffs: T.Dict[T.Tuple, T.Tuple[int,int]] = None


@dataclass
class AlignedScan:
    scan: Scan

    # the 3d matrix representing the orientation of the scanner
    rot: numpy.ndarray
    # the 3-vector representing the position of the scanner
    pos: BeaconPos

    # to produce the true origin position of a beacon scanned by this scanner,
    # we multiply its position by rot and then add pos
    def transform(self, pos: BeaconPos) -> BeaconPos:
        return pos @ self.rot + self.pos

    def transformedBeacons(self) -> T.List[BeaconPos]:
        result = []
        for b in self.scan.beacons:
            result.append(self.transform(b))
        return result


def allRots():
    """Returns all 24 3d axis-aligned rotation matrices.
    
    Naively, you can compute that there are
    3! orderings of the 3 axes, times each one can be 
    positive or negative. But in fact some of these include
    reflections too; we drop those by checking the determinant.
    """
    ident = numpy.identity(3, dtype=numpy.int32)
    axis_orderings = [numpy.roll(ident, i, 0) for i in range(3)]
    identswap = ident.copy()
    identswap[[1,0]] = identswap[[0,1]]
    axis_orderings.extend([numpy.roll(identswap, i, 0) for i in range(3)])

    # ok, now we're going to negate each row of each of the 6 axis orderings
    # this will produce all 48 orderings
    reflections_and_rotations = axis_orderings
    for axis in range(3):
        negator = numpy.identity(3, dtype=numpy.int32)
        negator[axis,axis] = -1
        reflections_and_rotations.extend([r @ negator for r in reflections_and_rotations])

    # now toss out the reflections (where det < 0)
    reflections_and_rotations = [x for x in reflections_and_rotations if numpy.linalg.det(x) > 0]
    
    #for i,m in enumerate(reflections_and_rotations):
    #    print(f"{i}:{m}")
    
    return reflections_and_rotations

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
    #for axis in range(len(beacons[0])):

    diffs = {}
    for (a,b) in allBeaconPairs:
        diffs[tuple(sorted(abs(b - a)))] = (a,b)

    return Scan(
        scanno=rawscan['title'][0],
        beacons=beacons,
        beaconDiffs=diffs
    )


scans = [preprocessScan(r) for r in rawscans]
print(scans[0].beaconDiffs)

print(len(scans[0].beaconDiffs))

def alignScans(scans: T.List[Scan]) -> T.List[AlignedScan]:
    scans = scans[:]
    orig = scans.pop(0)
    print(f"starting with scan {orig.scanno} to the group!")

    oaligned = AlignedScan(orig, numpy.identity(3, dtype=numpy.int32), numpy.zeros(3, dtype=numpy.int32))
    aligned = [oaligned]
    lastScans = 0

    while len(scans):
        for (nextScanIx, alignerIx) in findNextToAlign(scans, aligned):

            nextScan = scans[nextScanIx]

            print(f"Attempt to align scan {nextScan.scanno}...")
            naligned = alignScan(nextScan, aligned[alignerIx])
            if naligned:
                print(f"Aligned scan {nextScan.scanno} to the group! {naligned.pos} @ {naligned.rot}")
                aligned.append(naligned)
                scans.pop(nextScanIx)
                break
            else:
                print(f"Couldn't align {nextScan.scanno} and {aligned[alignerIx].scan.scanno}")
                # skip.append(nextScan)
        
        if len(scans) == lastScans and lastScans > 0:
            # we are looping
            break
            #assert False, "we ran out of things to align"

        lastScans = len(scans)
        
    return aligned

def findNextToAlign(
    scans: T.List[Scan], 
    alreadyAligned: T.List[AlignedScan]
    ) -> T.Iterable[T.Tuple[int, int]]:
    """Search for a plausible pair of indexes in `scans` and `alreadyAligned`
    to align. Iterable, in case the alignment fails you can try again!"""
    
    bestDiff = 0
    bestIxs = None

    for ixs, scan1 in enumerate(scans):
        for ixa, ascan2 in enumerate(alreadyAligned):
            intersection = scan1.beaconDiffs.keys() & ascan2.scan.beaconDiffs.keys()
            print(f"compare {scan1.scanno} vs {ascan2.scan.scanno}: difflen={len(intersection)}")
            if len(intersection) > 50:
                # it's a good intersection, we can stop searching and just align these scans
                yield (ixs, ixa)
            elif len(intersection) > bestDiff:
                bestDiff = len(intersection)
                bestIxs = (ixs, ixa)

    #assert False, "unable to find an alignment"
    assert bestIxs is not None, "didn't have best ixs?!"
    if bestIxs:
        yield bestIxs


def alignScan(scan: Scan, toAligned: AlignedScan) -> AlignedScan:
    if scan.scanno == 4 and toAligned.scan.scanno == 1:
        #breakpoint()
        pass
    intersection = scan.beaconDiffs.keys() & toAligned.scan.beaconDiffs.keys()

    def testAllAlignments(beacon1, beacon2, toAligned: AlignedScan, anchor1, anchor2) -> T.Optional[AlignedScan]:
        # run through all the different rotation possibilities when aligning
        target = toAligned.transform(anchor1)

        for rot in allRots():
            # ok, so we assume 'rot' is correct. we assume that beacon1 and anchor1
            # correspond, i.e., `target` is the True Position of beacon1.
            # If target = self.transform(beacon1)
            #    target = beacon1 @ rot + self.pos
            # then we compute self.pos = target - beacon1 @ rot
            selfpos = target - beacon1 @ rot
            # then we can try transforming beacon2 according to this and hope it is right
            testScan = AlignedScan(scan, rot, selfpos)
            tb2 = testScan.transform(beacon2)
            if (tb2 == toAligned.transform(anchor2)).all():
                #success!
                print(f"Success!")
                return testScan

    result = None

    while len(intersection) and result is None:
        # pick any intersection and try to align using it
        k = intersection.pop()
        (beacon1, beacon2), (anchor1, anchor2) = scan.beaconDiffs[k], toAligned.scan.beaconDiffs[k]

        # ok, we assume that (beacon1,beacon2)=(anchor1,anchor2) or vice versa
        
        # e.g. if beacon1=anchor1 then scan's alignment needs to be whatever
        # it takes to make beacon1 @ scan1 come out to anchor1 @ toAligned
        print(f"Aligning {scan.scanno} and {toAligned.scan.scanno}: {beacon1},{beacon2} to {anchor1, anchor2}")

        #if beacon1[2] == 682:
        #    breakpoint()

        result = (
               testAllAlignments(beacon1, beacon2, toAligned, anchor1, anchor2)
            or testAllAlignments(beacon2, beacon1, toAligned, anchor1, anchor2)
        )

    return result

alignedScans = alignScans(scans)

allBeacons = set()
for ascan in alignedScans:
    allBeacons.update(tuple(x) for x in ascan.transformedBeacons())

print(f"Aligned {len(alignedScans)} scans with {len(allBeacons)} unique beacons")

bestdist = 0
for s1 in alignedScans:
    for s2 in alignedScans:
        md = mandist(s2.pos, s1.pos)
        if md > bestdist:
            print(f"New bestdist is {md}")
            bestdist = md

