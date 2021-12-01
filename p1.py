test = """
199
200
208
210
200
207
240
269
260
263"""

def parse(s):
    return [int(x) for x in s.split()]

#xs = parse(test)
xs = parse(open('in1.txt').read())

prev = None
increaseCount = 0
for i,x in enumerate(xs[:-2]):
    window = sum(xs[i:i+3])
    if prev is not None and window > prev:
        increaseCount += 1
    prev = window

print(increaseCount)