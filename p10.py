sample = '''[({(<(())[]>[[{[]{<()<>>
[(()[<>])]({[<{<<[]>>(
{([(<{}[<>[]}>{[]{[(<()>
(((({<>}<{<{<>}{[]{[]{}
[[<[([]))<([[{}[[()]]]
[{[{({}]{}}([{[{{{}}([]
{<[[]]>}<{[{[{[]{()[[[]
[<(<(<(<{}))><([]([]()
<{([([[(<>()){}]>(<<{{
<{([{{}}[<[[[<>{}]]]>[]]
'''

#data = sample
data = open('in10.txt').read()

lines = data.strip().split('\n')

delim_match = {
    '{': '}',
    '[': ']',
    '(': ')',
    '<': '>',
}

delim_points = {
    ')': 1,
    ']': 2,
    '}': 3,
    '>': 4,
}



class Corruption(Exception): pass

def parse(s, stack=''):
    if len(s) == 0:
        # no corruptions, return closing chars in order
        print(f"finishing line with stack {stack}")
        return stack

    c = s[0]
    if c in delim_match.keys():
        # push and recur
        return parse(s[1:], delim_match[c] + stack)
    else:
        # it's a closing bracket, pop accordingly and stop if it's invalid
        expected_c = stack[0]
        if c == expected_c:
            return parse(s[1:], stack[1:])
        else:
            # corrupt
            print(f"corruption on {c} with remaining string {s[1:]}")
            raise Corruption()

parse(lines[0])

def finish_points(chars):
    total = 0
    for c in chars:
        total *= 5
        total += delim_points[c]

    return total

finishes = []
for line in lines:
    try:
        charsToFinish = parse(line)
    except Corruption:
        continue
    score = finish_points(charsToFinish)
    print(f"total to finish {charsToFinish} = {score}")
    finishes.append(score)

finishes.sort()
print(f"middle score = {finishes[len(finishes)//2]}")

