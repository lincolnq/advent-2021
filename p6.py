test = """3,4,3,1,2
"""

data = test
data = open('in6.txt').read()
maxlen = 9
days = 256
fish_counts_by_age = []

def extend():
    while len(fish_counts_by_age) < 9:
        fish_counts_by_age.append(0)

extend()

fishages = [int(x) for x in data.strip().split(',')]
for age in fishages:
    fish_counts_by_age[age] += 1

def step():
    count0 = fish_counts_by_age.pop(0)
    print(f'step popping {count0}')
    extend()
    fish_counts_by_age[6] += count0
    fish_counts_by_age[8] += count0

for i in range(days):
    print(fish_counts_by_age)
    print(f'{sum(fish_counts_by_age)} fish @ day {i}')
    step()

print(f'{sum(fish_counts_by_age)} fish @ day {days}')
