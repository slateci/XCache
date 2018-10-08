import random
from fractions import Fraction

MAX_HASH = pow(2, 32)
FILES_TO_SIMULATE = 100000
MAX_SERVERS = 10


def generate_fraction(servs):
    res = [[(0, Fraction(1, 1))]]  # server index, fraction
    for i in range(1, servs):
        rn = []
        fraction_to_subtract = {}
        for si in range(0, i):
            fraction_to_subtract[si] = Fraction(1, i * (i + 1))
        # print('to subtract per server:', fraction_to_subtract)
        # take a part from each previous server.
        for piece in res[i - 1]:

            # print('starting:', piece, end='\t')
            si = piece[0]
            fr = piece[1]

            if (not fr > fraction_to_subtract[si]):
                # print('giving it all to nfew server')
                rn.append([i, fr])
                fraction_to_subtract[si] -= fr
            else:
                if si % 2:  # makes similar parts sit together
                    # rewriting old one but now its fraction decreases
                    rn.append([si, fr - fraction_to_subtract[si]])
                    # adding new one
                    rn.append([i, fraction_to_subtract[si]])
                else:
                    rn.append([i, fraction_to_subtract[si]])
                    rn.append([si, fr - fraction_to_subtract[si]])
                fraction_to_subtract[si] = Fraction(0, 1)

        # connect pieces siting next to each other
        r = []
        p = [-1, Fraction(1, 1)]
        # print('rn:', rn)
        for j in rn:
            if j[0] != p[0]:
                r.append(j)
            else:
                r[-1] = ([j[0], j[1] + p[1]])
            p = j
        # print(r)
        res.append(r)
    return res


fractions = generate_fraction(MAX_SERVERS)
ranges = []
for s, f in enumerate(fractions):
    ul = 0
    rang = []
    for i in f:
        ul += i[1]
        rang.append([i[0], ul])
    print(rang)
    ranges.append(rang)
    print('servers:', s + 1, '\tpieces:', len(f), '\nfractions:', f, '\nranges:', rang)


def algo1(fm, servers):
    return fm % servers


def algo2(fm, servers):
    fr = (MAX_HASH - 1) / servers
    return int(fm / fr)


def algo3(fm, servers):
    ff = Fraction(fm, MAX_HASH)
    ul = 0
    # print(ranges[servers])
    for i in ranges[servers]:
        if ff < i[1]:
            # print(ff, i, float(ff))
            return i[0]


print("=======================================")

matches = [0] * (MAX_SERVERS - 1)
for files in range(FILES_TO_SIMULATE):
    fm = random.randint(0, MAX_HASH)
    endup = []
    for servers in range(0, MAX_SERVERS):
        s = algo3(fm, servers)
        endup.append(s)
    # print('-' * 30)
    # print(fm, endup)

    l = endup[0]
    for i, e in enumerate(endup[1:]):
        if e == l:
            matches[i] += 1
        l = e
print('=' * 30)
print('reused from total of', FILES_TO_SIMULATE, 'files')
print(matches)
