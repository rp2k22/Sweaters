# -*- coding: utf-8 -*-
"""
Created on Fri Jun  4 15:32:36 2021
A first take on a python program that does what my excel spreadsheet does, but better.
Takes in human body measurements, spits out a readable/usable pattern for my knitting machine.

Cheers!
@author: rpric
"""
import pprint
import importlib
from math import floor, ceil

dpdr = 2

stOnly = ["CAST ON", "HANG STITCHES OUT OF WORK", "BIND OFF", "-_-", "HANG STITCHES", "PUT STITCHES OUT OF WORK"]
rOnly = ["|R|", "||"]
Both = ["/|", "|\\", "/\\", "\\/", "SlvDecError"] # Have yet to remember the distinction between |\\ and ||/ etc.
Marginal = ["INC", "DEC"]

SleeveDec = ["/|", "|\\", "/\\", "\\/"]
Increase = ["\\/"]
Decrease = ["/\\", "/|", "|\\"] #?? Might have to refenagle these commands.

"""
Standard organization: 
        Inputs = {
                    "Name":"OrderID", 
                    "Style":"std001", 
                    "Units":"cm",
                    "Measurements":{
                        "WaistC":43*cm
                        ,"NeckC":21*cm
                        ,"ArmL":25*cm
                        ,"TotalHt":25*cm
                        ,"WristC":7*cm
                        ,"ShoulderC":16*cm
                        ,"SeamAllowance":0.5*cm
                    },
                    "FabricData":{
                        "stPcm":6.4/cm
                        ,"rPcm":8.89/cm
                        ,"stPg":100
                        ,"Flavor":"YSG"
                        ,"Tension":3
                        ,"Fabric":"Stockinette"
                    }
                  }
"""

"""
OUT order: [B, F, N, S]
"""

#Step 1: Geometry

def Step1(Inputs):
    #Do the unit conversion here!! Everything after this point should use cm
    moduleName = Inputs["Style"]
    Style = importlib.import_module(moduleName)
    
    S1Out = Style.Step1(Inputs)
    return S1Out
    
#Step 2: Convert units to st / r

def Step2(Inputs, S1Out):
    global dpdr
    S2Out = S1Out.copy()
    FabricData = Inputs["FabricData"]
    for piece in S1Out.keys():
        piece2 = []
        for step in S1Out[piece]:
            step2 = TranslateS2(step, FabricData)
            piece2.append(step2)
        S2Out[piece] = piece2
    return S2Out


def TranslateS2(step, FabricData):
    global stOnly, rOnly, Both, dpdr
    """
    THINGS TO HANDLE:
    
    INST, text
    OBS, numSteps
    
    CAST ON, st
    HANG STITCHES OUT OF WORK, st
    HANG STITCHES, st
    BIND OFF, st
    -_-, st

    |R|, r  
    ||, r

    /|, (st, r)
    |\\, (st, r)
    /\\, (st, r)
    \\/, (st, r)
    
    """
    CMD = step[0]
    PRM = step[1]
    
    #if there are multiple sub-steps on the same row
    if type(CMD)!=str:
        OUT = []
        if step[-1] == "ref":
            for i in range(len(step) -1):
                OUT.append(TranslateS2(step[i], FabricData))
            for i in range(len(step)-2, -1, -1):
                OUT.append(TranslateS2(step[i], FabricData))
        else:
            for i in range(len(step)):
                OUT.append(TranslateS2(step[i], FabricData))
        return OUT
    
    #INST
    if CMD == "INST": return step
    if CMD == "OBS" : return step
    
    # stich Only
    if CMD in stOnly:
        if PRM == "*": return step
        return (CMD, PRM*FabricData["stPcm"])
    
    # row Only
    if CMD in rOnly:
        return (CMD, PRM*FabricData["rPcm"])
    
    # both
    if CMD in Both:
        if "*" not in PRM:
            OUT = (CMD, (PRM[0]*FabricData["stPcm"], PRM[1]*FabricData["rPcm"]))
        elif PRM[0] == "*":
            y = PRM[1]*FabricData["rPcm"]
            OUT = (CMD, (y, y))
        else:
            y = PRM[0]*FabricData["stPcm"]
            OUT = (CMD, (y, y))  

    if CMD in SleeveDec:
        return SleeveDecrease(OUT, dpdr)
    else: return OUT


def SleeveDecrease(step, dpdr):
    global Increase, Decrease
    #just don't pass in any compound steps. That's fine.
    # dpdr stands for delta per delta row :/
    #this is a mess oops I'll do the math later; Use my SleeveDecrease alg from excel
    #OUT = [(numSets, SetSize, stDecPerDecR), (), ...]
    # so you do numSets sets where you knit SetSize-1 normal rows, then 1 Decrease Row
    #On which you decrease stDecPerDecR stitches.
    
    CMD = step[0]
    PRM = step[1]
    st = PRM[0]
    r = PRM[1]
    
    OUT = [("INST", step)]

    
    if CMD in Increase: 
        dStep = ("INC", dpdr)
        sign = -1
    if CMD in Decrease: 
        dStep = ("DEC", dpdr)
        sign = 1
    
    decr = st / dpdr
    ndecr = r - decr
    
    #Step 1
    groups = floor(decr)
    N = ceil(ndecr/groups)
    
    rremainder = r - groups*N
    decrremainder = decr - groups
    ndecrremainder = ndecr - groups*(N-1)
    
    #Step 2
    g1 = floor(ndecrremainder)
    N1 = N + 1
    
    g2 = groups - g1
    N2 = N
    
    rError = r - (g1*N1 + g2*N2)
    stError = st - (g1+g2)*dpdr
    
    #Report out. These should be separate methods but I am already in it.
    for i in range(g1):
        OUT.append(dStep)
        OUT.append(("||", N1-1))
    for i in range(g2):
        OUT.append(dStep)
        OUT.append(("||", N2-1))
    OUT.append(("SlvDecError", (sign*stError, rError)))
    
    return OUT

#Step 3: Translate to end-user language (So far just throwing it into a .txt file.)

def Step3(Inputs, S2Out):
    filename = Inputs["Name"]
    file = open(filename + ".txt", 'a')
    file.write(filename + "\n\n\n")
    file.write(pprint.pformat(Inputs))
    file.write("\n\n\n")
    
    #Go through each part, type steps along the way
    for partName in S2Out.keys():
        WritePartToFile(partName, S2Out[partName], file) 
    file.close()

 
def WritePartToFile(StepName, part, file):
    global SleeveDec, dpdr
    file.write(StepName + "\n\n")
    stepcount = 1
    for step in part:
        string = WriteStepAsString(step, stepcount) + "\n"
        file.write(string)
        stepcount = stepcount + 1
    file.write("\n\n")

def WriteStepAsString(step, stepcount):
    global stOnly, rOnly, Both 
    
    CMD = step[0]
    PRM = step[1]
    
    if stepcount == "SKIP": ct = ""
    else: ct = str(stepcount) + ":\n"
    
    #if there are multiple sub-steps on the same row
    if type(CMD)!=str:
        OUT = ct
        #if we're doing a sleeve decrease row
        if type(CMD) == tuple and len(CMD[1])==2:
            #now we are going to check for multiples.
            prev = [0]*2
            counter = 1
            prevIndex = 0
            for i in range(len(step)):
                OUTA = WriteStepAsString(step[i], "SKIP") + ";\n\t"
                if step[i] in prev:
                    counter = counter + 1
                else:
                    if counter>1:
                        OUT = OUT + "REPEAT  "+str(counter)+"  TIMES:"+"\n\t\t"+str(prev[0])+"\n\t\t"+str(prev[1]) + "\n\t" + OUTA
                        prev = [0, step[i]]
                    else:
                        prev[prevIndex] = step[i]
                        OUT = OUT + OUTA
                    counter = 1
                if prevIndex == 1: prevIndex = 0
                else: prevIndex = 1
                # print(prev)
            # print(OUT)
        else:
            if step[-1] == "ref":
                for i in range(len(step) -1):
                    OUT = OUT + WriteStepAsString(step[i], "SKIP") + ";\n\t"
                for i in range(len(step)-2, -1, -1):
                    OUT = OUT + WriteStepAsString(step[i], "SKIP") + ";\n\t"
            else:
                for i in range(len(step)):
                    OUT = OUT + WriteStepAsString(step[i], "SKIP") + ";\n\t"
        # print(OUT)
        return OUT
    
    numformat = "\t{: 3.2f}"
    
    if type(PRM) == float: PRMO = numformat.format(PRM)
    elif type(PRM) == tuple:
        PRMO = ""
        if type(PRM[0] != float) or type(PRM[1] != float):
            PRMO = PRMO + str(PRM[0]) + ": " + str(PRM[1])
        else:
            PRMO = PRMO + numformat.format(PRM[0]) + numformat.format(PRM[1])
    else: PRMO = "\t" + str(PRM)
    
    
    return ct + CMD + PRMO


#Step 4 ish: Yarn Estimation Tool
def YarnEstimationTool(Inputs, S2Out):
    """
    Parameters
    ----------
    Inputs : DICT
        Standard Inputs for Sweaters.py
    S2Out : list
        Output of Step2(Inputs)

    Returns
    -------
    None. Prints out an analysis of how many stitches required to make a sweater
    up to this spec, broken down by part; Interprets total grams yarn required.
    
    Assumes cast on, cast off, ribbed stitches == normal stitches, which is probably shenaniganous.
    """
    
    stPg = Inputs["FabricData"]["stPg"]
    numformat = "{:> 10.2f}"
    
    
    SCL = {} #Stitch Count List
    for i in S2Out.keys():
        # print("\n\n", i)
        SCL[i] = PartStitchCount(S2Out[i])
        # print(SCL[i])
    
    print("\n\n\nStitch Count Analysis:")
    print("Name: "+ Inputs["Name"] + "\n")
    print("PART\t\tSt\t\t\tg")
    for i in S2Out.keys():
        outstr = i +"\t" + numformat.format(SCL[i]) +"\t"  + numformat.format(SCL[i]/stPg)
        print(outstr)
    totalSt = sum(SCL.values())
    if "Sleeve" in S2Out.keys():
        totalSt += SCL["Sleeve"]
    totalG = totalSt/stPg
    print("TOTAL" +"\t" +numformat.format(totalSt) +"\t" +numformat.format(totalG))
    
def PartStitchCount(part):
    stCt = 0
    StOnNeedles = 0
    for step in part:
        counter = 0
        if step[0] == "OBS":
            a = 2
            counter = step[1]
            continue
        if counter == 0: a = 1
        stInc, StOnNeedles = StepStitchCount(step, StOnNeedles)
        # print(step, stInc, StOnNeedles)
        stCt += stInc*a
        counter += -1
    return stCt


#NOT DONE
def StepStitchCount(step, StOnNeedles):
    global stOnly, rOnly, Marginal   

    CMD = step[0]
    PRM = step[1]
    
    #if there are multiple sub-steps on the same row
    if type(CMD)!=str:
        OUT = [0, StOnNeedles]
        SON1 = StOnNeedles
        if step[-1] == "ref":

            for i in range(len(step) -1):
                fish = StepStitchCount(step[i], SON1)
                SON1 = fish[1]
                OUT[0] = OUT[0] + fish[0]
                OUT[1] = fish[1]
            for i in range(len(step)-2, -1, -1):
                fish = StepStitchCount(step[i], SON1)
                SON1 = fish[1]
                OUT[0] = OUT[0] + fish[0]
                OUT[1] = fish[1]
        else:
            for i in range(len(step)):
                fish = StepStitchCount(step[i], SON1)
                SON1 = fish[1]
                OUT[0] = OUT[0] + fish[0]
                OUT[1] = fish[1]
                # print(OUT)
        return OUT
    
    if CMD == "INST": return [0, StOnNeedles]
    
    if CMD in stOnly:
        if CMD in ["CAST ON", "HANG STITCHES"]: 
            return [0, StOnNeedles + PRM]
        elif CMD == "HANG STITCHES OUT OF WORK":
            return [0, StOnNeedles]
        else:
            if PRM == '*': return [0, 0]
            else:
#- (should be fine)
                return [0, StOnNeedles - PRM]

    if CMD in rOnly: return [StOnNeedles*PRM, StOnNeedles]

    if CMD in Marginal:

        if CMD == "INC":
            return [StOnNeedles+PRM,  StOnNeedles+PRM]
        if CMD == "DEC":
            return [StOnNeedles-PRM,  StOnNeedles-PRM]

    if CMD == "SlvDecError":
        # print(StOnNeedles, StOnNeedles+PRM[0])
        return [(StOnNeedles+PRM[0])*PRM[1], StOnNeedles+PRM[0]]
    
    print("ERROR SOMEWHERE", step)

"""
=======================================================
TEST STUFF HERE
=======================================================
"""
cm = 2.54
# Inputs = {
#                     "Name":"txtTest004", 
#                     "Style":"std002", 
#                     "Units":"cm",
#                     "Measurements":{
#                         "WaistC":43*cm
#                         ,"NeckC":21*cm
#                         ,"ArmL":25*cm
#                         ,"TotalHt":25*cm
#                         ,"WristC":7*cm
#                         ,"ShoulderC":16*cm
#                         ,"SeamAllowance":0.5*cm
#                     },
#                     "FabricData":{
#                         "stPcm":6.4/cm
#                         ,"rPcm":8.888889/cm
#                         ,"stPg":100
#                         ,"Flavor":"YSG"
#                         ,"Tension":3
#                         ,"Fabric":"Stockinette"
#                     }
#                   }

## Has FA data !!
Inputs = {
            "Name":"Test17Oct2021_FA", 
            "Style":"std002", 
            "Units":"cm",
            "Measurements":{
                "ChestC":41*cm
                ,"WaistC":39*cm
                ,"HipC" :40*cm
                ,"HWh" :8*cm
                ,"HCh" :18*cm
                ,"NeckC":21*cm
                ,"ArmL":25*cm
                ,"TotalHt":27*cm
                ,"WristC":7*cm
                ,"ShoulderC":16*cm
                ,"SeamAllowance":0.5*cm
            },
            "FabricData":{
                "stPcm":6.667/cm
                ,"rPcm":11.43/cm
                ,"stPg":254.4
            }
          }

fish = Step1(Inputs) # Step 1 works!!
sturgeon = Step2(Inputs, fish)

Step3(Inputs, sturgeon)

#This won't give accurate results yet, but it WILL give formatting info which I need.
YarnEstimationTool(Inputs, sturgeon)

# squirrel = SleeveDecrease(("/\\", (123, 140)), 2)


"""
=======================================================
END OF TESTING STUFF
=======================================================
"""