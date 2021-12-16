# -*- coding: utf-8 -*-
"""
Created on Fri Jun  4 16:04:01 2021
A python recreation of the pattern in my "GeneratingSweaterPatterns1" spreadsheet.

This one takes data in cm, spits out in cm.
CONVENTION: (Stitch, Row)
@author: rpric
"""


"""
OK A FEW ISSUES
Back, steps 1, 4, 7 are off by a LOT
Back, step 5 should make sure it's a number of stitches on EITHER side
yet to check out F, N, S
F: All the Back problems, step 10 is WAY high
N: Should be good?
S: RIGHT ON ! :)

I'm willing to just leave it as is, because I really wasn't planning to use
this style for sales anyways; I'd rather just design std002 and use that.

"""


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
                    }
                  }
"""
#Values in inches
cm = 2.54 #the cost of being a fool.
alpha = {"WaistC":-3*cm,
        "NeckC":0,
        "ArmL":-2*cm,
        "TotalHt":3*cm,
        "WristC":1*cm,
        "ShoulderC":3*cm}

def Step1(Inputs):
    OUT = {}
    OUT["Back"] = Back(Inputs)
    OUT["Front"] = Front(Inputs)
    OUT["Neck"] = Neck(Inputs)
    OUT["Sleeve"] = Sleeve(Inputs)
    
    return OUT
    
    
def Back(Inputs):
    global alpha, cm
    M = {}
    for i in Inputs["Measurements"].keys():
        M[i] = Inputs["Measurements"][i] + alpha.get(i, 0)
    
    output = [("CAST ON", 0.5*(M["WaistC"] + 4*M["SeamAllowance"]))]
    output.append(("|R|", 4*cm)) #2in ribbed hem
    output.append(("INST", "TURN HEM" ))
    #This next line is up 1 row, but these are all in cm. I don't think being up 1 row is ever going to be an issue, so I'm leaving it.
    output.append(("||", M["TotalHt"] - .5*M["ShoulderC"] -2*cm - (.25*(.5*M["WaistC"] - .5*M["NeckC"]))))    
    output.append(("BIND OFF", 1*cm))
    output.append((("/|", (2*cm, "*")), ("ref"))) #  * means do 1 st/row for as many of the other given.
    Y = 2*cm*Inputs["FabricData"]["stPcm"]/Inputs["FabricData"]["rPcm"]
    output.append(("||", M["TotalHt"]-3*cm - (M["TotalHt"] - .5*M["ShoulderC"] -2*cm - (.25*(.5*M["WaistC"] - .5*M["NeckC"]))) - (Y) - .5*.25*(.5*M["WaistC"]-.5*M["NeckC"]) ))
    output.append(("/\\", (.25*(.5*M["WaistC"]-.5*M["NeckC"]), "*" ) ))
    output.append(("INST","REMOVE ON WASTE YARN"))
    
    return output
    
def Front(Inputs):
    global alpha, cm
    M = {}
    for i in Inputs["Measurements"].keys():
        M[i] = Inputs["Measurements"][i] + alpha.get(i, 0)
    
    output = [("CAST ON", .5*(M["WaistC"] + 4*M["SeamAllowance"]))]
    output.append(("|R|", 4*cm)) #2in ribbed hem
    output.append(("INST", "TURN HEM" ))    
    #This next line is up 1 row, but these are all in cm. I don't think being up 1 row is ever going to be an issue, so I'm leaving it.
    output.append(("||", M["TotalHt"] - .5*M["ShoulderC"] -2*cm - (.25*(.5*M["WaistC"] - .5*M["NeckC"]))))    
    output.append(("BIND OFF", 1*cm))
    output.append((("/|", (2*cm, "*")), ("ref"))) #  * means do 1 st/row for as many of the other given.
    Y = M["TotalHt"] - 3*cm - (M["TotalHt"] - .5*M["ShoulderC"] - 2*cm) -2*cm - .5*(.25*(.5*M["WaistC"]-.5*M["NeckC"]))
    output.append(("||", Y))
    output.append(("-_-", .25*M["NeckC"]))
    output.append(("OBS",3))
    output.append(("|\\", (M["NeckC"]/8, "*")))
    Z = (M["WaistC"] - 3*cm - M["NeckC"]/4)/2 - M["NeckC"]/8
    output.append(("/|", (Z, "*")))
    output.append(("INST","REMOVE ON WASTE YARN"))
    
    return output

def Neck(Inputs):
    global alpha, cm
    
    M = {}
    for i in Inputs["Measurements"].keys():
        M[i] = Inputs["Measurements"][i] + alpha.get(i, 0)
    
    outputs = [("INST", "SEAM SHOULDERS ON ONE SIDE")]
    outputs.append(("HANG STITCHES", M["NeckC"]))
    outputs.append(("|R|", 2*cm))
    outputs.append(("INST", "TURN HEM"))
    outputs.append(("BIND OFF", "*"))
    
    return outputs
    
def Sleeve(Inputs):
    global alpha, cm
    
    M = {}
    for i in Inputs["Measurements"].keys():
        M[i] = Inputs["Measurements"][i] + alpha.get(i, 0)
        
    outputs = [("HANG STITCHES OUT OF WORK", M["ShoulderC"])]
    outputs.append(("\\/", (M["ShoulderC"], "*")))
    outputs.append((("/\\", (M["ShoulderC"] - M["WristC"] + 2*M["SeamAllowance"] , M["ArmL"]-2*cm)) ))
    outputs.append(("|R|", 4*cm))
    outputs.append(("INST", "TURN HEM"))
    outputs.append(("BIND OFF", "*"))
        
    return outputs