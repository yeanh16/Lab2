import random
import time
import argparse
import signal
import math
import csv
import argparse

parser = argparse.ArgumentParser(description="MaxSat")
parser.add_argument("-question",type=int)
parser.add_argument("-clause")
parser.add_argument("-assignment")
parser.add_argument("-wdimacs")
parser.add_argument("-time_budget", type=int)
parser.add_argument("-repetitions", type=int)
args = parser.parse_args()


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

def tournSelection(k, poplist):
        tournSet = []
        for i in range(0,k):
                tournSet.append(poplist[random.randint(0,len(poplist)-1)])
        maximum = 0
        winner = ""
        for i in range(0,k):
                if tournSet[i][1] >= maximum:
                        winner = tournSet[i][0]
                        maximum = tournSet[i][1]
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

def flipbit(bit):
    if bit == '0':
        return "1"
    else:
        return "0"

##def localsearch(assignment, clauses, attempts):    
##    ibaseScore = maxsatcheck(clauses, assignment)
##    bits = list(assignment)
##    original = bits
##    for i in range(0, attempts):
##        bits = original
##        bits[random.randint(0,len(bits)-1)] = flipbit(bits[random.randint(0,len(bits)-1)])
##        if maxsatcheck(clauses, ("".join(bits)) ) >= ibaseScore:
##            return "".join(bits)
##    #none better found
##    return assignment

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

    populationSize = 50
    tournSize = 2
    chi = 0.6
    elitismpc = 0.1
    #localsearchattempts = 0
    for r in range(0, repetitions):
        #start timer
        timeup = False
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(time_budget)
        try:
            satbest = 0
            xbest = ""
            t = 1
            #generate random population
            poplist = []
            for i in range(0, populationSize):
                newmember = generateRandomBitString(int(n))
                inewmembersat = maxsatcheck(clauses, newmember)
                if inewmembersat >= satbest:
                    satbest = inewmembersat
                    xbest = newmember
                poplist.append((newmember, inewmembersat))
            
            while not timeup:
                newpoplist = []
                
                #elitism members go through to next gen
                poplist.sort(key=lambda x: x[1]) #sort poplist by second tuple member (sat score)
                nofElites = math.floor(elitismpc * populationSize)
                if nofElites != 0:
                    newpoplist += poplist[-nofElites:]
                                  
                
                for i in range(0, (populationSize - nofElites)):
                       x = tournSelection(tournSize, poplist)
                       y = tournSelection(tournSize, poplist)
                       mx = mutate(x, chi)
                       my = mutate(y, chi)
                       child = crossover(mx, my)
                       #child = localsearch(prechild, clauses, localsearchattempts)
                       ichildsatcheck = maxsatcheck(clauses, child)
                       if ichildsatcheck >= satbest:
                           satbest = ichildsatcheck
                           xbest = child
                       newpoplist.append((child, ichildsatcheck))
                t += 1
                poplist = newpoplist
                
        except StopIteration:
            timeup = True
            print(str(populationSize*t) + "\t" + str(satbest) + "\t" + str(xbest))

def maxsatgaResults(wdimacs, testvariable, value):
    rawfile = open(wdimacs, "r")
    file = rawfile.read()
    filelines = file.splitlines()
    clauses = []
    for i in range(0, len(filelines)):
         lline = filelines[i].split(" ")
         if lline[0] == 'c': 
                continue
         elif lline[0] == 'p':
                n = int(lline[2])
                m = int(lline[3])
         else:
                clauses.append(filelines[i])
                
    repetitions = 100
    time_budget = 20
    populationSize = 50
    tournSize = 2
    chi = 0.6
    elitismpc = 0.1
    if testvariable == "pop":
        populationSize = value
    elif testvariable == "chi":
        chi = value
    else:
        elitismpc = value

    resultsArray = []
        
    for r in range(0, repetitions):
        #start timer
        timeup = False
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(time_budget)
        try:
            satbest = 0
            xbest = ""
            t = 1
            #generate random population
            poplist = []
            for i in range(0, populationSize):
                newmember = generateRandomBitString(n)
                inewmembersat = maxsatcheck(clauses, newmember)
                if inewmembersat >= satbest:
                    satbest = inewmembersat
                    xbest = newmember
                poplist.append((newmember, inewmembersat))
            
            while not timeup:
                newpoplist = []
                
                #elitism members go through to next gen
                poplist.sort(key=lambda x: x[1]) #sort poplist by second tuple member (sat score)
                nofElites = math.floor(elitismpc * populationSize)
                if nofElites != 0:
                    newpoplist += poplist[-nofElites:]
                                  
                
                for i in range(0, (populationSize - nofElites)):
                       x = tournSelection(tournSize, poplist)
                       y = tournSelection(tournSize, poplist)
                       mx = mutate(x, chi)
                       my = mutate(y, chi)
                       child = crossover(mx, my)
                       #child = localsearch(prechild, clauses, localsearchattempts)
                       ichildsatcheck = maxsatcheck(clauses, child)
                       if ichildsatcheck >= satbest:
                           satbest = ichildsatcheck
                           xbest = child
                       newpoplist.append((child, ichildsatcheck))
                t += 1
                poplist = newpoplist
                
        except StopIteration:
            timeup = True
            resultsArray.append(round(satbest/m, 2))
            print(str(round(satbest/m, 2)))
            
    return resultsArray


def maxsatgaAutomater(wdimacs):
    timebudget = 30
    repetitions = 100
    defaultPopSize = 100
    defaultChi = 0.6
    defaultElitePc = 0.1
    populationSizesArray = [10,20,30,40,50,60,70,80,90,100]
    chiArray = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.9, 1, 2, 5, 10]
    elitismpcArray = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

##    with open("Niso2Pop.csv", 'w', newline='') as csvfile:
##        csvwriter = csv.writer(csvfile, delimiter=' ', quoting=csv.QUOTE_MINIMAL)
##        for value in populationSizesArray:
##            print("Population value: " + str(value))
##            csvwriter.writerow(maxsatgaResults(wdimacs, "pop", value))
##
##    with open("Niso2Chi.csv", 'w', newline='') as csvfile:
##        csvwriter = csv.writer(csvfile, delimiter=' ', quoting=csv.QUOTE_MINIMAL)
##        for value in chiArray:
##            print("Chi value: " + str(value))
##            csvwriter.writerow(maxsatgaResults(wdimacs, "chi", value))

    with open("Niso2Elite.csv", 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=' ', quoting=csv.QUOTE_MINIMAL)
        for value in elitismpcArray:
            print("Elitism value: " + str(value))
            csvwriter.writerow(maxsatgaResults(wdimacs, "el", value))
    



def signal_handler(signum, frame):
    raise StopIteration("Time up")
    

if args.question == 1:
    print(satcheck(args.assignment, args.clause))
elif args.question == 2:
    print(dimacs(args.wdimacs, args.assignment))
elif args.question ==3:
    maxsatga(args.wdimacs, args.time_budget, args.repetitions)
    
                       
