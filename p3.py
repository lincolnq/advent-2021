test = '''00100
11110
10110
10111
10101
01111
00111
11100
10000
11001
00010
01010
'''

#lines = test.strip().split()
lines = open('in3.txt').read().strip().split()

def mostpop(lines):
    print(lines)
    count_1s = [sum(1 if s[i] == '1' else 0 for s in lines) for i in range(len(lines[0]))]
    thresh = len(lines) / 2
    return ['E' if x == thresh else True if x > len(lines) / 2 else False for x in count_1s]

digits = mostpop(lines)

def dig2bin(line):
    result = 0
    for b in line:
        result *= 2
        result += int(b)
    return result

def inv(digits):
    return [not x for x in digits]

def select(lines, bitpos, value):
    return [x for x in lines if x[bitpos] == ('1' if value else '0')]


def gen(lines, keepfn):
    for bitpos in range(len(lines[0])):
        popdig = mostpop(lines)[bitpos]
        keepval = keepfn(popdig)
        lines = select(lines, bitpos, keepval)
        print(f'selected {lines}')
        if len(lines) == 1:
            return lines[0]



o2 = dig2bin(gen(lines, lambda popdig: True if popdig == 'E' else popdig))
co2 = dig2bin(gen(lines, lambda popdig: False if popdig == 'E' else (not popdig)))

print(f"{o2} * {co2} = {o2*co2}")