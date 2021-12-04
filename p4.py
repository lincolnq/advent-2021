from dataclasses import dataclass

from typing import List

test = """7,4,9,5,11,17,23,2,0,14,21,24,10,16,13,6,15,25,12,22,18,20,8,19,3,26,1

22 13 17 11  0
 8  2 23  4 24
21  9 14 16  7
 6 10  3 18  5
 1 12 20 15 19

 3 15  0  2 22
 9 18 13 17  5
19  8  7 25 23
20 11 10 24  4
14 21 16 12  6

14 21 17 24  4
10 16 15  9 19
18  8 23 26 20
22 11 13  6  5
 2  0 12  3  7
"""

#data = test
data = open('in4.txt').read()

sections = data.strip().split('\n\n')
def parseFirstline(l):
    return [int(x) for x in l.split(',')]

@dataclass
class Board:
    # shape is implicitly 5x5. they appear in `nums` start from top left corner,
    # and working across rows.
    nums: List[int]
    markings: List[bool]

def parseboard(bstr):
    nums = [int(n) for line in bstr.split('\n') for n in line.split()]
    markings = [False] * len(nums)
    return Board(nums, markings)

(firstline, boards) = parseFirstline(sections[0]), [parseboard(x) for x in sections[1:]]

print(firstline, boards)

# returns new board if number was found in board.nums
def markBoard(number, board: Board):
    try:
        ix = board.nums.index(number)
        newmarkings = board.markings[:]
        newmarkings[ix] = True
        return Board(board.nums, newmarkings)
    except ValueError:
        return board

def isWinner(b: Board):
    # true if b has a bingo in its markings
    rowWins = [slice(5*x, 5*(x+1),1) for x in range(5)]
    colWins = [slice(x, x+25, 5) for x in range(5)]
    #diagWins = [slice(0, 25, 6), slice(4,24,4)]
    diagWins = []

    return any(
        all(x for x in b.markings[s]) 
        for s in rowWins + colWins + diagWins
        )

class WinnerException(Exception): pass

def step(num, boards):
    # mark all boards with num
    # then check for winners
    newboards = [markBoard(num, b) for b in boards]

    oldwins = [isWinner(x) for x in boards]
    wins = [isWinner(x) for x in newboards]
    if all(wins) and not all(oldwins):
        # ok, we have the last to win
        loserIx = oldwins.index(False)
        raise WinnerException(newboards[loserIx])

    return newboards

def boardScore(b):
    # assuming b is a winning board: find sum of unmarked nums
    # then multiply by num
    unmarkedsum = sum(x for i,x in enumerate(b.nums) if not b.markings[i])
    return unmarkedsum


try:
    for num in firstline:
        boards = step(num, boards)
        print(f"drew {num}, no winner yet")
        print(boards[0])
except WinnerException as e:
    winboard = e.args[0]
    print(f"drew {num}, winner is: {winboard}\nboardscore = {boardScore(winboard)} * {num} = {boardScore(winboard) * num}")

