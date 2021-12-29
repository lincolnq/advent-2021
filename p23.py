#config = 'BCBDADCA'
config = 'ADABCCDB'

from dataclasses import dataclass
from typing import List, Optional, Tuple

@dataclass(frozen=True)
class State:
    hallway: str  # length 11
    rooms: str    # length 8 -- 1st row then 2nd row

    def is_won(self):
        return self == S_DEFAULT

room_to_hall = {0: 2, 1: 4, 2: 6, 3: 8}
valid_hallslots = [0,1,3,5,7,9,10]
movecost = {'A': 1, 'B': 10, 'C': 100, 'D': 1000}
home_rooms = {'A': 0, 'B': 1, 'C': 2, 'D': 3}

def step_room_to_hall(s: State, roomslot: int, hallslot: int) -> Optional[int]:
    """Returns None if no path found, otherwise returns number of steps to get there.

    Checks for emptiness along the path, but not at start/end.
    
    Roomslot must be on range(8)
    Hallslot must be on range(11) but not be 2/4/6/8.

    Note that since we don't examine the start or end square, this function 
    works just fine regardless of whether you are travelling from "roomslot" 
    to "hallslot" or vice versa
    """
    steps = 0
    if roomslot >= 4:
        # pod is in 2nd row, first row must be free
        roomslot = roomslot % 4
        if s.rooms[roomslot] != ' ':
            return None

        # ok, we can reach hallway
        steps += 1
    
    # now add the steps for moving to that hallslot
    steps_r = hallslot - room_to_hall[roomslot]
    assert steps_r != 0, f"step_room_to_hall called with invalid hallslot {hallslot}"
    # dir is 1 if right and -1 if left
    dir = steps_r//abs(steps_r)

    # check hallslots for emptiness and add 1 step each square
    for hs in range(hallslot - steps_r, hallslot, dir):
        if s.hallway[hs] != ' ':
            return None
        steps += 1

    return steps+1  # we (intentionally) didn't check final square in hall


def strrepl(s: str, i: int, c: str):
    """Replace s's character at 'i' with char c, returning the rest of s unchanged"""
    return s[:i] + c + s[i+1:]


def is_home_slot(s: State, c: str, roomslot: int) -> bool:
    """Returns true if, in state s, c is "home" in the given roomslot
    and would never need to move again.
    
    This is true if the roomslot % 4 matches the home room for that type,
    as long as (if roomslot < 4) we won't have to move.
    """
    if home_rooms[c] != roomslot % 4:
        return False
    
    if roomslot >= 4:
        # it's bottom row - we're happy
        return True
    else:
        # we're on the top row. check our buddy
        buddy = s.rooms[roomslot + 4]
        # if buddy is not same type or is empty, we'll have to move, so
        # we aren't home yet.
        return buddy == c

def get_home_dest(s: State, c: str) -> int:
    """Returns the home roomslot for this c in state s.
    
    This is defined as the "inner" roomslot, unless that inner
    roomslot is already occupied by our matching buddy, then the outer one.

    Note that this doesn't ever fail - so you still have to check
    whether that roomslot is empty before trying to move someone there.
    """
    dest = home_rooms[c] + 4
    if s.rooms[dest] != c:
        return dest
    else:
        return dest - 4


def room_to_room_dist(roomslot1: int, roomslot2: int) -> int:
    """Min steps to get between 2 roomslots (not in same room)"""
    # start with hallway dist
    dist = hall_to_room_dist(room_to_hall[roomslot1 % 4], roomslot2)
    if roomslot1 >= 4:
        dist += 1
    return dist + 1

def hall_to_room_dist(hallslot: int, roomslot: int) -> int:
    """Min steps to get from hallway to room"""
    dist = abs(hallslot - room_to_hall[roomslot % 4])
    if roomslot >= 4:
        dist += 1
    return dist + 1

def adj(s: State) -> List[Tuple[State, int]]:
    """Return adjacent States, with their costs."""

    result = []

    # first consider all moves of apods from rooms to the hallway
    for roomslot,c in enumerate(s.rooms):
        if c == ' ':
            continue
        # skip apods who are "home"
        if is_home_slot(s, c, roomslot):
            continue

        for hallslot in valid_hallslots:
            # skip non-empty hallslots
            if s.hallway[hallslot] != ' ':
                continue

            steps = step_room_to_hall(s, roomslot, hallslot)
            if steps is not None:
                s1 = State(strrepl(s.hallway, hallslot, c), strrepl(s.rooms, roomslot, ' '))
                cost = steps * movecost[c]
                result.append((s1, cost))

    # then consider all moves of apods from hallway to destination room
    for hallslot in valid_hallslots:
        c = s.hallway[hallslot]
        if c == ' ':
            continue

        # see if we can move this apod home
        dest_roomslot = get_home_dest(s, c)
        if s.rooms[dest_roomslot] == ' ':
            steps = step_room_to_hall(s, dest_roomslot, hallslot)
            if steps is not None:
                s1 = State(strrepl(s.hallway, hallslot, ' '), strrepl(s.rooms, dest_roomslot, c))
                cost = steps * movecost[c]
                result.append((s1, cost))


    return result

S_DEFAULT = State(' ' * 11, 'ABCDABCD')

import heapq

def printstate(s: State):
    print('#' * 13)
    print('#' + s.hallway + '#')
    print(f'###{s.rooms[0]}#{s.rooms[1]}#{s.rooms[2]}#{s.rooms[3]}###')
    print(f'  #{s.rooms[4]}#{s.rooms[5]}#{s.rooms[6]}#{s.rooms[7]}#')
    print('  ' + '#'*9)

from functools import total_ordering


@total_ordering
@dataclass(frozen=True)
class SearchState:
    cost: int
    s: State
    hist: List[State]

    def verb_heuristic(self):
        # compute a minimum cost if we could just move everything to its desired destination immediately

        # first, figure out who is already home
        has_home = [0, 0, 0, 0]
        for roomslot, c in enumerate(self.s.rooms):
            if c == ' ':
                continue
            if is_home_slot(self.s, c, roomslot):
                has_home[roomslot % 4] += 1
        
        estcost = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        # ok, now do another pass to figure out distances to home through rooms
        for roomslot, c in enumerate(self.s.rooms):
            if c == ' ':
                continue
            if is_home_slot(self.s, c, roomslot):
                continue
            dest_roomslot = get_home_dest(self.s, c)
            if dest_roomslot % 4 == roomslot % 4:
                # FIXME(lincoln): account for we have to move ourselves out of the way... 
                estcost[c] += 0
            else:
                # ok, we have to move to another room
                am_2nd_home = has_home[dest_roomslot % 4] > 0
                target = dest_roomslot % 4 if am_2nd_home else dest_roomslot
                estcost[c] += room_to_room_dist(roomslot, target)
                if target >= 4:
                    # and mark that we "took up" this homeslot so the next guy coming home
                    # takes the 2nd slot
                    has_home[dest_roomslot % 4] += 1
        
        # lastly, do a pass for the hallway guys
        for hallslot, c in enumerate(self.s.hallway):
            if c == ' ':
                continue

            dest_roomslot = get_home_dest(self.s, c)
            am_2nd_home = has_home[dest_roomslot % 4] > 0
            target = dest_roomslot % 4 if am_2nd_home else dest_roomslot
            estcost[c] += hall_to_room_dist(hallslot, target)
            if target >= 4:
                # again, mark that we "took up" this homeslot
                has_home[dest_roomslot % 4] += 1

        return estcost
    
    def heuristic(self):
        estcost = self.verb_heuristic()
        return sum(steps * movecost[c] for (c, steps) in estcost.items()) + self.cost

    def __lt__(self, rhs):
        return self.heuristic() < rhs.heuristic()

def solve(s: State) -> Tuple[State, int]:
    searchstates = []
    best_seen_states = {}

    heapq.heappush(searchstates, SearchState(0, s, []))

    iter = 0

    bestcost = 99999

    try:
        while True:
            iter += 1
            ss = heapq.heappop(searchstates)
            if ss.s.is_won():
                if ss.cost < bestcost:
                    print(f"found a solution after {iter}, new best cost={ss.cost}")
                    bestcost = ss.cost


            #if iter > 10:
            #    break

            if iter % 1000 == 0:
                print(f"iter {iter}, cost={ss.cost}")
                printstate(ss.s)
                

            for (s1, costdelta) in adj(ss.s):
                c1 = costdelta + ss.cost
                if s1 in best_seen_states and c1 > best_seen_states[s1]:
                    # we've already been to this state with a worse cost. let's not visit it again.
                    continue
                best_seen_states[s1] = c1


                heapq.heappush(searchstates, SearchState(c1, s1, ss.hist + [s1]))
    except KeyboardInterrupt:
        pass


    print(f"finished after {iter}, cost={ss.cost}")
    for s1 in ss.hist:
        printstate(s1)
#    printstate(ss.s)
    print(f"bestcost={bestcost}")

solve(State(' ' * 11, config))


def test_step_room_to_hall_empty():
    s = State(' ' * 11, 'ABCDABCD')

    assert 3 == step_room_to_hall(s,0,0)
    assert 2 == step_room_to_hall(s,0,1)
    assert 2 == step_room_to_hall(s,0,3)
    assert 4 == step_room_to_hall(s,0,5)
    assert 9 == step_room_to_hall(s,0,10)
    assert 3 == step_room_to_hall(s,3,10)
    assert 2 == step_room_to_hall(s,3,9)
    assert 2 == step_room_to_hall(s,3,7)
    assert 4 == step_room_to_hall(s,3,5)

def test_step_room_to_hall_2nd_row():
    s = State(' ' * 11, '    ABCD')
    assert 6 == step_room_to_hall(s,5,8)
    assert 5 == step_room_to_hall(s,7,5)
    assert 3 == step_room_to_hall(s,5,3)


def test_step_room_to_hall_blocked_exit():
    s = State(' ' * 11, 'ABCD    ')
    assert None == step_room_to_hall(s, 4, 1)
    assert None == step_room_to_hall(s, 5, 3)
    assert None == step_room_to_hall(s, 6, 9)
    assert None == step_room_to_hall(s, 7, 10)

def test_step_room_to_hall_blocked_hallway():
    s = State('   B       ', '    ABCD')
    assert step_room_to_hall(s, 4, 1) is not None
    assert step_room_to_hall(s, 4, 5) is None
    assert step_room_to_hall(s, 5, 1) is None
    assert step_room_to_hall(s, 5, 5) is not None
    assert step_room_to_hall(s, 5, 10) is not None

def test_step_room_to_hall_doesnt_check_source_or_dest():
    """It's ok if there's a guy at the starting/ending position"""
    s = State('   B       ', '    ABCD')
    assert step_room_to_hall(s, 5, 3) is not None
    assert step_room_to_hall(s, 4, 3) is not None


def assert_heuristic(s, a, b, c, d):
    assert {'A': a, 'B': b, 'C': c, 'D': d} == SearchState(0, s, []).verb_heuristic()

def test_heuristic():
    s = S_DEFAULT
    assert_heuristic(s, 0, 0, 0, 0)


    """
#############
#       D   #
###A#B#C# ###
  #A#B#C#D#
  ######### """
    s = State('       D   ', 'ABC ABCD')
    assert_heuristic(s, 0, 0, 0, 2)

    """
#############
#       D  B#
###A# #C# ###
  #A#B#C#D#
  ######### """
    s = State('       D  B', 'A C ABCD')
    assert_heuristic(s, 0, 7, 0, 2)

    """
#############
#       D  B#
###A#C# # ###
  #A#B#C#D#
  ######### """
    s = State('       D  B', 'AC  ABCD')
    assert_heuristic(s, 0, 7, 4, 2)

def test_heuristic_fancy():
    """
#############
#...........#
###A#D#A#B###
  #C#C#D#B#
  #########"""
    s = State(' ' * 11, 'ADABCCDB')
    assert_heuristic(s, 7, 14, 6+7, 6+6)


print(adj(S_DEFAULT))