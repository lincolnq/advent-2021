sample='''target area: x=20..30, y=-10..-5
'''
official = '''target area: x=288..330, y=-96..-50
'''

#xtarget = (20,30)
#ytarget = (-10,-5)
xtarget, ytarget = ((288,330),(-96,-50))

def sim(vel):
    """returns list of positions, if it hits the target area before its y coordinate goes below the ymin.
    otherwise returns None."""
    t=0
    pos = (0,0)
    poss = []
    while True:
        poss.append(pos)
        if xtarget[0] <= pos[0] <= xtarget[1] and ytarget[0] <= pos[1] <= ytarget[1]:
            return poss

        if pos[1] < ytarget[0]:
            return False
        if pos[0] > xtarget[1]:
            return False

        t += 1
        pos = (pos[0] + vel[0], pos[1] + vel[1])
        vel = (vel[0] - 1 if vel[0] > 0 else vel[0] + 1 if vel[0] < 0 else 0, vel[1] - 1)


print(sim((6,9)))

# compute min x velocity based on the drag
dist = xtarget[0]
# solve: v0 + (v0-1) + (v0-2) + ... + 1 = dist
# v0*(v0+1)/2 = dist
# v0^2/2 + v0/2 - dist = 0
# -1/2 +/- sqrt(1/4 + 2dist)
import math
minxvel = math.ceil(math.sqrt(0.25 + dist * 2) - 0.5)
print(minxvel)

allvels = set()
for yvel in range(-100,950):
    if yvel % 100 == 0:
        print(yvel)
    for xvel in range(minxvel, minxvel+1000):
        poss = sim((xvel, yvel))
        if poss:
            #print(f"found a solution for {(xvel, yvel)})")
            allvels.add((xvel, yvel))

print(len(allvels))