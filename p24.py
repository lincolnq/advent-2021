sample = '''inp w
add z w
mod z 2
div w 2
add y w
mod y 2
div w 2
add x w
mod x 2
div w 2
mod w 2
'''

from helpers import *
parser = Lines() ** Split(' ')
#instrs = parser.parse(sample)
instrs = parser.parse(open('in24.txt').read())

def isConst(s):
    try:
        int(s)
        return True
    except (ValueError, TypeError):
        return False

def possibleValueSet(s):
    if s == '1_to_9':
        return set(range(1,10))
    elif isConst(s):
        return set([int(s)])
    else:
        return None

def evalArg(arg, knownValues):
    """If arg is a constant, returns its value.
    If it is a var, returns knownValues.get(arg) (which can be a string).
    Returns None if nothing is known about the arg!
    """
    if isConst(arg):
        return int(arg)
    elif arg in knownValues:
        return knownValues[arg]
    else:
        return None

def foldInstrs(instrs):
    """Perform constant folding on the program."""

    knownValues = {'w': 0, 'x': 0, 'y': 0, 'z': 0}
    result = []

    for (i, dest, *args) in instrs:
        newInstr = [i, dest, *args]
        if i == 'inp':
            knownValues[dest] = '1_to_9'

        elif i == 'const':
            # setting a constant; passthrough
            knownValues[dest] = int(args[0])

        elif i == 'mul' and isConst(evalArg(args[0], knownValues)) and evalArg(args[0], knownValues) == 0:
            # multiplying by 0 always sets the value to zero
            knownValues[dest] = 0
            newInstr = ['const', dest, '0']

        elif i in ('add', 'mul', 'div', 'mod', 'eql'):

            if (isConst(knownValues.get(dest)) 
                and (isConst(evalArg(args[0], knownValues)))):
                # The main case: we have an arithmetic operation with lhs known, and rhs
                # either known or constant.
                # fold!
                lhs = int(knownValues.get(dest))
                rhs = evalArg(args[0], knownValues)

                if i == 'add':
                    knownValues[dest] = lhs + rhs
                elif i == 'mul':
                    knownValues[dest] = lhs * rhs
                elif i == 'div':
                    knownValues[dest] = lhs // rhs
                elif i == 'mod':
                    knownValues[dest] = lhs % rhs
                elif i == 'eql':
                    knownValues[dest] = 1 if lhs == rhs else 0
                
                newInstr = ['const', dest, knownValues[dest]]

            elif i == 'eql':
                # maybe we can prove inequality
                lhsSet = possibleValueSet(knownValues.get(dest))
                rhsSet = possibleValueSet(evalArg(args[0], knownValues))
                
                if lhsSet is not None and rhsSet is not None and len(lhsSet & rhsSet) == 0:
                    newInstr = ['const', dest, '0']
                    knownValues[dest] = 0

            else:
                # it's not a constant, so we are no longer constrained
                knownValues[dest] = None

        result.append(newInstr)
    
    return result


#def elimDeadCode(instrs):


def compileInstrs(instrs):
    """Create a Python function from the instructions."""

    text = "def aluProgram(input):\n"
    def addLine(s):
        nonlocal text
        text += '    ' + s + '\n'

    addLine('w = x = y = z = 0')

    inputConsumed = 0

    for (i, dest, *args) in instrs:
        if i == 'inp':
            addLine(f'{dest} = int(input[{inputConsumed}])')
            inputConsumed += 1
        elif i == 'add':
            addLine(f'{dest} += {args[0]}')
        elif i == 'mul':
            addLine(f'{dest} *= {args[0]}')
        elif i == 'div':
            addLine(f'{dest} //= {args[0]}')
        elif i == 'mod':
            addLine(f'{dest} %= {args[0]}')
        elif i == 'eql':
            addLine(f'{dest} = 1 if {dest} == {args[0]} else 0')
        elif i == 'const':
            addLine(f'{dest} = {args[0]}')
    
    addLine('return (w,x,y,z)')

    return text

# the original alu program in in24.txt:
"""
def monad(input):
    w = x = y = z = 0
    w = int(input[0])
    x *= 0
    x += z
    x %= 26
    z //= 1
    x += 11
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y *= 0
    y += 25
    y *= x
    y += 1
    z *= y
    y *= 0
    y += w
    y += 1
    y *= x
    z += y
    w = int(input[1])
    x *= 0
    x += z
    x %= 26
    z //= 1
    x += 11
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y *= 0
    y += 25
    y *= x
    y += 1
    z *= y
    y *= 0
    y += w
    y += 11
    y *= x
    z += y
    w = int(input[2])
    x *= 0
    x += z
    x %= 26
    z //= 1
    x += 14
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y *= 0
    y += 25
    y *= x
    y += 1
    z *= y
    y *= 0
    y += w
    y += 1
    y *= x
    z += y
    w = int(input[3])
    x *= 0
    x += z
    x %= 26
    z //= 1
    x += 11
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y *= 0
    y += 25
    y *= x
    y += 1
    z *= y
    y *= 0
    y += w
    y += 11
    y *= x
    z += y
    w = int(input[4])
    x *= 0
    x += z
    x %= 26
    z //= 26
    x += -8
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y *= 0
    y += 25
    y *= x
    y += 1
    z *= y
    y *= 0
    y += w
    y += 2
    y *= x
    z += y
    w = int(input[5])
    x *= 0
    x += z
    x %= 26
    z //= 26
    x += -5
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y *= 0
    y += 25
    y *= x
    y += 1
    z *= y
    y *= 0
    y += w
    y += 9
    y *= x
    z += y
    w = int(input[6])
    x *= 0
    x += z
    x %= 26
    z //= 1
    x += 11
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y *= 0
    y += 25
    y *= x
    y += 1
    z *= y
    y *= 0
    y += w
    y += 7
    y *= x
    z += y
    w = int(input[7])
    x *= 0
    x += z
    x %= 26
    z //= 26
    x += -13
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y *= 0
    y += 25
    y *= x
    y += 1
    z *= y
    y *= 0
    y += w
    y += 11
    y *= x
    z += y
    w = int(input[8])
    x *= 0
    x += z
    x %= 26
    z //= 1
    x += 12
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y *= 0
    y += 25
    y *= x
    y += 1
    z *= y
    y *= 0
    y += w
    y += 6
    y *= x
    z += y
    w = int(input[9])
    x *= 0
    x += z
    x %= 26
    z //= 26
    x += -1
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y *= 0
    y += 25
    y *= x
    y += 1
    z *= y
    y *= 0
    y += w
    y += 15
    y *= x
    z += y
    w = int(input[10])
    x *= 0
    x += z
    x %= 26
    z //= 1
    x += 14
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y *= 0
    y += 25
    y *= x
    y += 1
    z *= y
    y *= 0
    y += w
    y += 7
    y *= x
    z += y
    w = int(input[11])
    x *= 0
    x += z
    x %= 26
    z //= 26
    x += -5
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y *= 0
    y += 25
    y *= x
    y += 1
    z *= y
    y *= 0
    y += w
    y += 1
    y *= x
    z += y
    w = int(input[12])
    x *= 0
    x += z
    x %= 26
    z //= 26
    x += -4
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y *= 0
    y += 25
    y *= x
    y += 1
    z *= y
    y *= 0
    y += w
    y += 8
    y *= x
    z += y
    w = int(input[13])
    x *= 0
    x += z
    x %= 26
    z //= 26
    x += -8
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y *= 0
    y += 25
    y *= x
    y += 1
    z *= y
    y *= 0
    y += w
    y += 6
    y *= x
    z += y
    return (w,x,y,z)
"""

exec(compileInstrs(instrs))
origProgram = aluProgram

#exec(prog)

print(origProgram('13579246899999'))


#def checkmonad(input):
#    return monad(input)[3] == 0

#print(checkmonad('3' * 14))

#instrs2 = foldInstrs(instrs)
#compiled = compileInstrs(instrs2)
#exec(compiled)
#print(aluProgram('13579246899999'))

#print(compiled)
#print(f'compiled to {len(instrs2)} instrs from {len(instrs)}!')
def aluProgram(input):
    w = x = y = z = 0
    w = int(input[0])
    x = 0
    x = 0
    x = 0
    z = 0
    x = 11
    x = 0
    x = 1
    y = 0
    y = 25
    y = 25
    y = 26
    z = 0
    y = 0
    y += w
    y += 1   
    y *= x
    z += y


    # 1,1,2,2 or 2,1,3,3... for input 1 or 2
    #return (w,x,y,z)

    
    w = int(input[1])
    x = 0
    x += z
    x %= 26
    z //= 1
    x += 11
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    print(f"at in1 x={x}")
    y = 0
    y = 25
    y *= x
    y += 1
    z *= y
    y = 0
    y += w
    y += 11
    y *= x
    z += y
    w = int(input[2])
    x = 0
    x += z
    x %= 26
    z //= 1
    x += 14
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    print(f"at in2 x={x}")

    y = 0
    y = 25
    y *= x
    y += 1
    z *= y
    y = 0
    y += w
    y += 1
    y *= x
    z += y
    w = int(input[3])
    x = 0
    x += z
    x %= 26
    z //= 1
    x += 11
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    print(f"at in3 x={x}")
    y = 0
    y = 25
    y *= x
    y += 1
    z *= y
    y = 0
    y += w
    y += 11
    y *= x
    z += y
    w = int(input[4])
    x = 0
    x += z
    x %= 26
    z //= 26
    x += -8
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    print(f"at in4 x={x}")
    y = 0
    y = 25
    y *= x
    y += 1
    z *= y
    y = 0
    y += w
    y += 2
    y *= x
    z += y
    w = int(input[5])
    x = 0
    x += z
    x %= 26
    z //= 26
    x += -5
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y = 0
    y = 25
    y *= x
    y += 1
    z *= y
    y = 0
    y += w
    y += 9
    y *= x
    z += y

    w = int(input[6])
    x = 0
    x += z
    x %= 26
    z //= 1
    x += 11
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y = 0
    y = 25
    y *= x
    y += 1
    z *= y
    y = 0
    y += w
    y += 7
    y *= x
    z += y
    w = int(input[7])
    x = 0
    x += z
    x %= 26
    z //= 26
    x += -13
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y = 0
    y = 25
    y *= x
    y += 1
    z *= y
    y = 0
    y += w
    y += 11
    y *= x
    z += y
    w = int(input[8])
    x = 0
    x += z
    x %= 26
    z //= 1
    x += 12
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y = 0
    y = 25
    y *= x
    y += 1
    z *= y
    y = 0
    y += w
    y += 6
    y *= x
    z += y
    w = int(input[9])
    x = 0
    x += z
    x %= 26
    z //= 26
    x += -1
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y = 0
    y = 25
    y *= x
    y += 1
    z *= y
    y = 0
    y += w
    y += 15
    y *= x
    z += y
    w = int(input[10])
    x = 0
    x += z
    x %= 26
    z //= 1
    x += 14
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y = 0
    y = 25
    y *= x
    y += 1
    z *= y
    y = 0
    y += w
    y += 7
    y *= x
    z += y
    w = int(input[11])
    x = 0
    x += z
    x %= 26
    z //= 26
    x += -5
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y = 0
    y = 25
    y *= x
    y += 1
    z *= y
    y = 0
    y += w
    y += 1
    y *= x
    z += y
    w = int(input[12])
    x = 0
    x += z
    x %= 26
    z //= 26
    x += -4
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y = 0
    y = 25
    y *= x
    y += 1
    z *= y
    y = 0
    y += w
    y += 8
    y *= x
    z += y
    w = int(input[13])
    x = 0
    x += z
    x %= 26
    z //= 26
    x += -8
    x = 1 if x == w else 0
    x = 1 if x == 0 else 0
    y = 0
    y = 25
    y *= x
    y += 1
    z *= y  ## if x 'matches' w in some way then z is multiplied by 1 here
    y = 0
    y += w
    y += 6
    y *= x ## if x 'matches' w in some way then y is 0 here
    z += y
    return (w,x,y,z)


#print(aluProgram('1579246899999'))

def breakdownz(z):
    result = []
    while z > 0:
        result.append(z % 26)
        z //= 26
    return result

def myAluProgram(input):

    def next(inpix: int, zdiv: int, xdelt: int, ydelt: int, wxyz, forcesolve=False, override=None):
        w,x,y,z = wxyz

        if forcesolve:
            solution = (z % 26) + xdelt
            w = int(input[inpix])
            if w == solution:
                pass
            elif 1 <= solution <= 9:
                print(f"solving char {inpix}={solution}")
                w = solution
            else:
                raise Exception(f"unable to solve @ {inpix} because xdelt={xdelt} and z={z} leaving {z%26 + xdelt}")

        elif override is not None:
            w = int(override)
        else:
            w = int(input[inpix])

        x = 0
        x += z
        x %= 26
        z //= zdiv
        x += xdelt  # NOTE: xdelt only used for below test. otherwise ignored.
        #print(f"looking for {x}")
        x = 1 if x == w else 0
        x = 1 if x == 0 else 0
        y = 0
        y = 25
        y *= x
        y += 1      # Y is always 26 (if test fails and we are pushing) or 1 (if passes and we are popping)
        z *= y
        y = 0
        y += w
        y += ydelt  # NOTE: ydelt only used if above test fails (to push onto zstack)
        y *= x
        z += y

        
        print(f"after char {inpix}, z={z}, breakdown={breakdownz(z)}")

        return w,x,y,z
    
    stack = []

    def push(inpix, delta, wxyz):
        stack.insert(0, (delta, input[inpix]))
        return next(inpix, 1, 11, delta, wxyz)
    
    def pop(inpix, delta, wxyz):
        (priord, priorc) = stack.pop(0)
        myc = input[inpix]
        print(f"Pop: {priord} ({priorc}) + {delta} ({myc}) = {priord+delta} ({int(myc) - int(priorc)})")
        return next(inpix, 26, delta, 0, wxyz, forcesolve=True)

    wxyz = (0,0,0,0)
    wxyz = push(0, 1, wxyz)     # A
    wxyz = push(1, 11, wxyz)    # B
    wxyz = push(2, 1, wxyz)     # C
    wxyz = push(3, 11, wxyz)    # D
    wxyz = pop(4, -8, wxyz)     # -D [CBA]
    wxyz = pop(5, -5, wxyz)     # -C [BA]
    wxyz = push(6, 7, wxyz)     # E
    wxyz = pop(7, -13, wxyz)    # -E [BA]
    wxyz = push(8, 6, wxyz)     # F
    wxyz = pop(9, -1, wxyz)     # -F [BA]
    wxyz = push(10, 7, wxyz)    # G
    wxyz = pop(11, -5, wxyz)    # -G
    wxyz = pop(12, -4, wxyz)    # -B
    wxyz = pop(13, -8, wxyz)    # -A

    return wxyz
    

#print(myAluProgram('9296xx7x4x7xxx'))
x = '92969593497992' # biggest
print(myAluProgram(x))
x = '81514171161381' # smallest
print(myAluProgram(x))
#    ABCDdcEeFfGgba
# A: -7
# B: 7
# C: -4
# D: 3
# E: -6
# F: 5
# G: 2

#print(myAluProgram('11111111111111'))

## SUCCESS (but not the biggest):
# print(origProgram( '92969571497992'))
