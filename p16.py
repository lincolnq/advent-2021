sample = '''D8005AC2A8F0
'''

#data = sample.strip()
data = open('in16.txt').read().strip()

def hexToBinary(x):
    # yields sequence of true/false
    for c in x:
        i = int(c, 16)
        for b in range(3,-1,-1):
            yield (i >> b) % 2 == 1

dataBin = list(hexToBinary(data))
print(''.join('1' if x else '0' for x in dataBin))

def b2i(bs):
    result = 0
    for b in bs:
        result *= 2
        result += 1 if b else 0
    return result

def isTrue(bs):
    return bs[0]

def read(count, l, parser=lambda x: x):
    result = l[:count]
    l = l[count:]
    return (parser(result), l)

def readLiteral(l):
    cont = True
    result = 0
    while cont:
        (cont,l) = read(1, l, isTrue)
        (bytes4,l) = read(4, l, b2i)
        result *= 16
        result += bytes4
    return (result,l)

TYP_LITERAL = 4
TYP_SUM = 0
TYP_PROD = 1
TYP_MIN = 2
TYP_MAX = 3
TYP_GT = 5
TYP_LT = 6
TYP_EQ = 7

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Packet:
    version: int
    typ: int
    literal_val: Optional[int]
    subpackets: List['Packet']

def readPacket(l):
    """Returns this packet subtree as well as any remaining l data"""
    version, l = read(3, l, b2i)
    typ, l = read(3, l, b2i)
    subpackets = []

    print(f"found a packet with v{version}, typ {typ}")
    if typ == TYP_LITERAL:
        lit, l = readLiteral(l)
        print(f" it's a lit {lit}")
    else:
        # it's an operator
        lit = None
        length_type_id, l = read(1, l, isTrue)
        print(f" it's an operator with LT {length_type_id}")

        if length_type_id == False:
            # next 15 bits are a number
            subpacketBits,l = read(15, l, b2i)
            subpacketData,l = read(subpacketBits, l)
            print(f" bits mode - consuming {subpacketBits} bits and reading packets...")

            # parse packets out of subpacketData
            while subpacketData:
                p, subpacketData = readPacket(subpacketData)
                subpackets.append(p)
        else:
            subpacketCount,l = read(11, l, b2i)
            print(f" count mode - consuming {subpacketCount} subpackets...")

            for _ in range(subpacketCount):
                p, l = readPacket(l)
                subpackets.append(p)

    return Packet(version, typ, lit, subpackets), l

def versionSum(pk):
    return pk.version + sum(versionSum(x) for x in pk.subpackets)

import functools
import operator

def val(pk: Packet):
    if pk.typ == TYP_LITERAL:
        return pk.literal_val

    PK_OPS = {
        TYP_SUM: sum,
        TYP_PROD: lambda l: functools.reduce(operator.mul, l, 1),
        TYP_MIN: min,
        TYP_MAX: max,
        TYP_GT: lambda l: 1 if l[0] > l[1] else 0,
        TYP_LT: lambda l: 1 if l[0] < l[1] else 0,
        TYP_EQ: lambda l: 1 if l[0] == l[1] else 0,
    }

    return PK_OPS[pk.typ](list(val(p) for p in pk.subpackets))

pks,l = readPacket(dataBin)
print(versionSum(pks))
print(val(pks))