import random
import time
import argparse
import signal

def satcheck(assignment, clause):
    literals = clause.split(" ")
    lassignment = list(assignment)
    for i in range(1, len(literals)-1 ):
        if (int(literals[i]) > 0 and int(lassignment[int(literals[i])-1]) == 1):
            return 1
        elif (int(literals[i]) < 0 and int(lassignment[abs(int(literals[i]))-1]) == 0):
            return 1
    return 0

def dimacs(wdimacs, assignment):
    rawfile = open(wdimacs, "r")
    file = rawfile.read()
    filelines = file.splitlines()
    sats = 0
    for i in range(0, len(filelines)):
        lline = filelines[i].split(" ")
        if lline[0] == 'c': #comment line
            continue
        elif lline[0] == 'p':
            n = lline[2]
            m = lline[3]
            #x = lline[4]
        else:
            sats += satcheck(assignment, filelines[i])
    return sats

def maxsatcheck(clauses, assignment):
    sat = 0
    for i in range(0,len(clauses)):
        sat += satcheck(assignment, clauses[i])
    return sat

def tournSelection(k, poplist, clauses):
        tournSet = []
        for i in range(0,k):
                tournSet.append(poplist[random.randint(0,len(poplist)-1)])
        maximum = 0
        winner = ""
        for i in range(0,k):
                if maxsatcheck(clauses, tournSet[i]) >= maximum:
                        winner = tournSet[i]
                        maximum = maxsatcheck(clauses, tournSet[i])
        return winner
    
def crossover(bits_x, bits_y):
        lbits_x = list(bits_x)
        lbits_y = list(bits_y)
        bits = lbits_x
        for j in range(0, len(lbits_x)):
                       if bits_x[j] != bits_y[j]:
                               bits[j] = randomBit()
        return "".join(bits)
    
def mutate(bits_x, chi):
        bits = list(bits_x)
        mutationRate = chi/float(len(str(bits_x)))
        for i in range(0, len(str(bits_x))):
                if (random.uniform(0,1) < mutationRate):
                        if (int(bits[i]) == 1):
                                bits[i] = '0'
                        else:
                                bits[i] = '1'
        return "".join(bits)
    
def randomBit():
        if random.uniform(0,1) < 0.5 :
                return '1'
        else:
                return '0'
            
def generateRandomBitString(nbits):
        bitString = ""
        for i in range(0, nbits):
                if (random.uniform(0,1) < 0.5):
                        bitString += "0"
                else:
                        bitString += "1"
        return bitString

def maxsatga(wdimacs, time_budget, repetitions):
    rawfile = open(wdimacs, "r")
    file = rawfile.read()
    filelines = file.splitlines()
    clauses = []
    for i in range(0, len(filelines)):
         lline = filelines[i].split(" ")
         if lline[0] == 'c': 
                continue
         elif lline[0] == 'p':
                n = lline[2]
                m = lline[3]
         else:
                clauses.append(filelines[i])

    populationSize = 100
    tournSize = 2
    chi = 0.6
    satbest = 0
    xbest = ""
    for r in range(0, repetitions):
         t = 0
         #generate random population
         poplist = []
         for i in range(0, populationSize):
             poplist.append(generateRandomBitString(int(n)))

        
         signal.signal(signal.SIGALRM, signal_handler)
         signal.alarm(time_budget)
         try:
             newpoplist = []
             for i in range(0, populationSize):
                    x = tournSelection(tournSize, poplist, clauses)
                    y = tournSelection(tournSize, poplist, clauses)
                    mx = mutate(x, chi)
                    my = mutate(y, chi)
                    child = crossover(mx, my)
                    if maxsatcheck(clauses, child) >= satbest:
                        satbest = maxsatcheck(clauses, child)
                        xbest = child
                    newpoplist.append(child)
             t += 1
             poplist = newpoplist
         except Exception:
             print(str(populationSize*t) + "\t" + str(satbest) + "\t" + str(xbest))
         print(str(populationSize*t) + "\t" + str(satbest) + "\t" + str(xbest))

def signal_handler(signum, frame):
    raise Exception("Time's up")

    
                       
