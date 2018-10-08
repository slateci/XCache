from fractions import Fraction


class ServerPlacement():

    MAX_HASH = pow(2, 32)

    def __init__(this, servers):
        this.servers = servers
        this.fraction = []
        this.ranges=[]
        this.calculateFractions()

    def calculateFractions(this):
        print('Initializing. Servers:', this.servers )
        res = [[(0, Fraction(1, 1))]]  # server index, fraction
        for i in range(1, this.servers):
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

        ul = 0
        f=res[-1]
        for i in f:
            ul += i[1]
            this.ranges.append([i[0], ul])
        print('pieces:', len(f), '\nfractions:', f, '\nranges:', this.ranges)

    def getServer(this, fileHash):
        ff = Fraction(fileHash, this.MAX_HASH)
        ul = 0
        # print(ranges)
        for i in this.ranges:
            if ff < i[1]:
                # print(ff, i, float(ff))
                return i[0]
