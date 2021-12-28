pps = [4,8]
#pps = [7,1]
pscore = [0,0]

rollcount = 0
def roll():
    # returns sum of next 3 dice, mod 10
    # for rollcounts: 0, 3, 6, 9, 12, 15, 18:
    # returns: 6, 5, 4, 3, 2, 1, 0, 9, 8...
    global rollcount
    rollcount += 3
    ix = rollcount // 3
    six_minus_ix = (7 - ix) % 10
    return six_minus_ix

def mod10_1(i):
    return (i - 1) % 10 + 1

def part1():
    for i in range(1000):
        playerix = i % 2
        playerno = playerix + 1
        r = roll()
        pps[playerix] = mod10_1(pps[playerix] + r)
        pscore[playerix] += pps[playerix]
        print(f"Player {playerno} rolls {r} and moves to space {pps[playerix]} for a total score of {pscore[playerix]}")

        if pscore[playerix] >= 1000:
            print(f"Player {playerno} wins with score of {pscore[playerix]} after {rollcount} rolls: {pscore[(playerix+1)%2] * rollcount}")
            break

from collections import defaultdict
from dataclasses import dataclass
from functools import total_ordering
from typing import Tuple, Dict
import heapq

@total_ordering
@dataclass(frozen=True)
class Universe:
    nextp: int                  # 0 or 1
    pps: Tuple[int, int]        # pos on track for each player [1 to 10]
    pscore: Tuple[int, int]     # score for each player

    def ended(self):
        return self.pscore[0] >= 21 or self.pscore[1] >= 21
    
    def sortkey(self):
        return self.pscore[self.nextp]

    def __lt__(self, other):
        return self.sortkey() < other.sortkey()


u0 = Universe(0, (7,1), (0,0))

ucounts: Dict[Universe, int] = defaultdict(lambda: 0)
upq = []

def roll3():
    """Returns the number of successor universes to this one for each possible roll result."""
    #from collections import Counter
    #return sorted(Counter(i+j+k for i in range(1,4) for j in range(1,4) for k in range(1,4)).items())
    return [(3, 1), (4, 3), (5, 6), (6, 7), (7, 6), (8, 3), (9, 1)]

def tuprep(t, ix, newval):
    if ix == 0:
        return (newval, t[1])
    else:
        return (t[0], newval)

def advance(u: Universe, posadv: int):
    """Apply the roll and subsequent scoring to this Universe, returning a new Universe."""
    me = u.nextp
    newpp = tuprep(u.pps, me, mod10_1(u.pps[me] + posadv))
    newscore = tuprep(u.pscore, me, u.pscore[me] + newpp[me])
    return Universe((me + 1) % 2, newpp, newscore)

def advanceAll(u: Universe):
    """Advance this Universe to all successors, modifying ucounts and upq."""

    rolls = roll3()
    count = ucounts[u]

    #print(f"advancing {count} universes like {u}")

    # consume all identical universes:
    assert count > 0
    ucounts[u] = 0

    for posadv, n in rolls:
        u1 = advance(u, posadv)
        if not u1.ended():
            if u1 not in ucounts:
                # new universe never seen
                #print(f" new universe never seen: {u1}")
                heapq.heappush(upq, u1)
                
            elif ucounts[u1] == 0:
                # 0-count universe, we've seen it before but already processed
                #print(f" 0-count universe: {u1}")
                heapq.heappush(upq, u1)
        else:
            #print(f" ended universe: {u1}")
            pass


        ucounts[u1] += n * count


def part2():
    ucounts[u0] = 1
    heapq.heappush(upq, u0)
    iters = 0

    while len(upq):
        if iters % 100 == 0:
            print(f"{iters}: qlen={len(upq)}")
        iters += 1
        u1 = heapq.heappop(upq)
        advanceAll(u1)

        #if iters > 100:
        #    break

    return iters

iters = part2()
#print(ucounts)

p1win = 0
p2win = 0
for (u, count) in ucounts.items():
    if count > 0:
        if u.ended():
            winp = (u.nextp + 1) % 2
            #print(f"universe {u} is a win for player {winp+1} with count {count}")
            if winp == 0:
                p1win += count
            else:
                p2win += count

        else:
            print(f"universe {u} is un-ended with count {count}")

print(f"{p1win} for player 1, {p2win} for player 2, the answer is {max(p1win, p2win)}, iters={iters}")