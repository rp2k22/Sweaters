# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 17:19:35 2021
A version of my original standard sweater pattern but developed ENTIRELY for this Python stuff!
Exciting!!

Units: cm

@author: rpric
"""
from numpy import sqrt
"""
Standard organization: 
        Inputs = {
                    "Name":"OrderID", 
                    "Style":"std001", 
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
                        "stPcm":6.4/cm
                        ,"rPcm":8.89/cm
                        ,"stPg":100
                    }
                  }
"""
alpha = {"ChestC":-6
        ,"WaistC":-8
        ,"HipC" :-8
        ,"HWh" :0
        ,"HCh" :0
        ,"NeckC":0
        ,"ArmL":-5
        ,"TotalHt":8
        ,"WristC":3
        ,"ShoulderC":8
        ,"SeamAllowance":1.5
        }

#QOL fns:
def Hptns(a, b):
    c = sqrt(a**2 + b**2)
    return c


def Step1(Inputs):
    M = Adjust(Inputs)
    Dims = GetDims(M)
    
    OUT = {}
    OUT["Back"] = Back(Dims)
    OUT["Front"] = Front(Dims)
    OUT["Neck"] = Neck(Dims)
    OUT["Sleeve"] = Sleeve(Dims)
    
    return OUT


#Alpha will probably still be additive, but I would like to give scaling designs a shot l8r
#Also the translation from Inputs+Alpha should happen in its own function????? duh?
def Adjust(Inputs):
    global alpha
    #ADDITIVE ALPHA
    M = {}
    if Inputs["Units"] == "cm":
        for i in Inputs["Measurements"].keys():
            M[i] = Inputs["Measurements"][i] + alpha.get(i, 0)
    elif Inputs["Units"] == "in":
        cm = 2.54
        for i in Inputs["Measurements"].keys():
            M[i] = Inputs["Measurements"][i]*cm + alpha.get(i, 0)
    else:
            print("Error: Incompatible input unit! Use \"in\" or (better yet) \"cm\" !")
    
    return M

def GetDims(M):
    Dims = {}
    cm = 2.54   #The cost of being a fool
    
    #Stuff that isn't affected by M:
    # (Hem Lengths should be TWICE the desired finished lengths!)
    Dims["WaistHemLength"] = 4*cm
    Dims["NeckHemLength"] = 1*cm
    Dims["CuffHemLength"] = 1.5*cm
    
    #Sweater Widths (Width of 1 panel, so 1/2 circumference)
    Dims["ChestWidth"] = (2*M["SeamAllowance"] + .5*M["ChestC"])
    Dims["WaistWidth"] = (2*M["SeamAllowance"] + .5*M["WaistC"])
    Dims["HipWidth"]   = (2*M["SeamAllowance"] + .5*M["HipC"])
    
    #Sweater Heights (These are consecutive ! Not cumulative !!)
    Dims["WaistHeight"] = M["HWh"] - Dims["WaistHemLength"]
    Dims["ChestHeight"] = M["HCh"] - Dims["WaistHemLength"]
    
    #Sleeve Dims
    Dims["SleeveLength"] = M["ArmL"] - Dims["CuffHemLength"] # CUFF LENGTH IS INCLUDED IN SLEEVE LENGTH ALREADY
    Dims["SleeveWidthMax"] = M["ShoulderC"] + 2*M["SeamAllowance"]
    Dims["SleeveWidthMin"] = M["WristC"] + 2*M["SeamAllowance"]
    
    #Neck Dims
    Dims["NeckBack"] = .5*M["NeckC"]
    Dims["NeckBottom"] = .25*M["NeckC"]
    Dims["NeckHeight"] = M["TotalHt"] - .125*M["NeckC"]
    
    #I don't remember what these were supposed to do,,,
    # Dims["NeckDiagR"] = .25*M["NeckC"] # This is trig inspired !!
    # Dims["NeckDiagSt"] = .5*.866*M["NeckC"]
    
    #Implied stuff
    Dims["SleeveIn"] = 1*cm #Not actually implied but maybe it is later, and the other related stuff is right here also

    Dims["ShoulderR"] = 1*cm #I made these up. No clue if they're good !! ! 
    Dims["ShoulderSt"] = 2*cm
    
    Dims["SleeveDiagR"]  = 1.5*cm #Same here.
    Dims["SleeveDiagSt"] = 1.5*cm
    
    Dims["SleeveHeight"] = .5*Dims["SleeveWidthMax"] -Dims["SleeveIn"] - Hptns(Dims["SleeveDiagR"], Dims["SleeveDiagSt"])
    
    return Dims

#The Stuff!!
def Back(Dims):
    OUT = [""]*10
    
    OUT[0] = ("CAST ON", Dims["HipWidth"])
    OUT[1] = ("|R|", Dims["WaistHemLength"])
    OUT[2] = ("INST", "TURN HEM" )

    if Dims["HipWidth"]<Dims["WaistWidth"]:
        CMD1 = "\\/"
    else: CMD1 = "/\\"
    PRM1 = [0, 0]
    PRM1[0] = abs(Dims["HipWidth"]-Dims["WaistWidth"])
    PRM1[1] = Dims["WaistHeight"]

    OUT[3] = (CMD1, (PRM1[0], PRM1[1]))

    if Dims["WaistWidth"]<Dims["ChestWidth"]:
        CMD2 = "\\/"
    else: CMD2 = "/\\"
    PRM2 = [0,0]
    PRM2[0] = abs(Dims["HipWidth"]-Dims["ChestWidth"])
    PRM2[1] = Dims["ChestHeight"]
    
    OUT[4] = (CMD2, (PRM2[0], PRM2[1]))
    
    OUT[5] = ("BIND OFF", Dims["SleeveIn"])
    OUT[6] = ("/\\", (Dims["ShoulderSt"], Dims["ShoulderR"]))
    #FRONT stops being the same here.
    OUT[7] = ("||", Dims["SleeveHeight"])
    OUT[8] = ("/\\", (2, "*")) #Maybe adjust this later? This is supposed to be the taper on the shoulders.
    OUT[9] = ("INST", "Take off on waste yarn!")
    
    return OUT

def Front(Dims):
    OUT = [""]*12
    
    OUT[0] = ("CAST ON", Dims["HipWidth"])
    OUT[1] = ("|R|", Dims["WaistHemLength"])
    OUT[2] = ("INST", "TURN HEM" )

    if Dims["HipWidth"]<Dims["WaistWidth"]:
        CMD1 = "\\/"
    else: CMD1 = "/\\"
    PRM1 = [0,0]
    PRM1[0] = abs(Dims["HipWidth"]-Dims["WaistWidth"])
    PRM1[1] = Dims["WaistHeight"]

    OUT[3] = (CMD1, (PRM1[0], PRM1[1]))

    if Dims["WaistWidth"]<Dims["ChestWidth"]:
        CMD2 = "\\/"
    else: CMD2 = "/\\"
    PRM2 = [0,0]
    PRM2[0] = abs(Dims["HipWidth"]-Dims["ChestWidth"])
    PRM2[1] = Dims["ChestHeight"]
    
    OUT[4] = (CMD2, (PRM2[0], PRM2[1]))
    
    OUT[5] = ("BIND OFF", Dims["SleeveIn"])
    OUT[6] = ("/\\", (Dims["ShoulderSt"], Dims["ShoulderR"]))
    #BACK stops being the same here.
    ## This part has not been done ! ! ! ! ! !!! ! ! ! ! ! !  ! 
    OUT[7] = ("||", Dims["NeckHeight"])
    OUT[8] = ("-_-", Dims["NeckBottom"])
    
    OUT[9] = ("OBS", 3) #change number when done ; number of steps to do on both sides.
    OUT[10] = ("|\\", (.5*Dims["NeckBottom"]-2, "*")) # NOT sure
    OUT[11] = ("/\\", (2, "*"))
    return OUT
    
def Neck(Dims):
    OUT = [("INST", "Hold OFF")]*5
    OUT[0] = ("INST", "SEAM SHOULDERS ON ONE SIDE")
    OUT[1] = ("HANG STITCHES", 2*Dims["NeckBack"])
    OUT[2] = ("|R|", Dims["NeckHemLength"])
    OUT[3] = ("INST", "TURN HEM")
    OUT[4] = ("BIND OFF", "*")
    return OUT
    
def Sleeve(Dims):
    OUT = [("INST", "Hold OFF")]*6
    
    OUT[0] =  ("HANG STITCHES OUT OF WORK", Dims["SleeveWidthMax"])
    OUT[1] = ("\\/", (Dims["SleeveWidthMax"], "*"))
    OUT[2] = (("/\\", (Dims["SleeveWidthMin"] , Dims["SleeveLength"]) ))
    OUT[3] = ("|R|", Dims["CuffHemLength"])
    OUT[4] = ("INST", "TURN HEM")
    OUT[5] = ("BIND OFF", "*")
    
    
    return OUT
        
