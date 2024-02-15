#!/usr/bin/python3
import codecs

###############################################################################
#      Needs to be used with SY85 Bulk dump SYNTH dump only!                 ##
#                                                                            ##
#                                                                            ##
#
#
# Two Required lines to use as  a library in another program :
#
# xmlout2 = (BankPrint (sysexfile))
# savemidnam(xmlout2,"test.midnam")
#
#Enter name of sysex file 85, must be an SY85 SYNTH BULK DUMP
#
#sysexfile = "vintage1_Synthall.syx"
#
#sysexfile = "vintage2.syx"
#sysexfile = "factory.syx"
# Set name of sysex file here.

sysexfile = "vintage1_synthAll.syx"       #name of SY85 Synth Bulk Sysex Dump
midnamoutfile = "patchoutput.midnam"      #name of output file
BANK_PREFIX = "Vintage 1"                 #Bank Name should be name of floppy disk set or similar


patchxmlinfo=""
# Load SY85 Synth  Sysex file as bytearray

BANKS =("V1", "V2", "V3", "V4", "P1", "P2")# change to more appropriate later
BANK_CODE = ("00","03", "06", "09", "40", "43") #Hex for LSB of v1, v2,... ...p1, p2
BANKS_VERBOSE=( "Voice 1", "Voice 2", "Voice 3", "Voice 4", "Performance 1", "Performance 2")

PATCHBANK_HEADER = "<PatchBank Name=\"" +patchxmlinfo + "\">" # needs bank prefix and bank suffix from v1, v2, etc.
#Define Global Bank Variable
BP = list() 

#slice for presets
voice1slice =slice(0,64)
voice2slice =slice(64,128)
voice3slice= slice(128, 192)
voice4slice=slice(192,256)
perf1slice=slice(256,320)
perf2slice=slice(320,384)

BANK_SLICES =(voice1slice, voice2slice, voice3slice, voice4slice, perf1slice, perf2slice)

#Create array for patch numbers to resemble SY85 selectors
def createBankArray():
    bankfirst=list()
    for x in "ABCDEFGH":
        for y in "12345678":
          bankfirst.append(x + y)
    return bankfirst

#load a sysex file and return byte array
def loadSysex(filename):
    try:
       with open(sysexfile, 'rb') as filebin:
         newarray=filebin.read()
         filebin.close()
    except FileNotFoundError:
      print("File not found!")
      quit()
    return newarray

#save midnam clippet
def savemidnam(outputxml, filename):
  try:
       with open (filename, 'w') as outfile:
        outfile.write(outputxml)
        outfile.close()
       print("File Saved!")
  except Exception as e : 
    print(e)
    return -1
	
#decode byte array ascii
def pprint (byteAscii):
    return  (codecs.decode(byteAscii, "utf-8"))

##returns a list of Start and stop points of syssec blocks
def findStart (sysex):
  sysStart =240
  searray =list()
  sysEnd = 247
  startpos = 0
  binPos =0 
  while binPos < len(sysex):
      getSysStart = sysex.find(sysStart, binPos)   
      getSysEnd = sysex.find (sysEnd, binPos)
      binPos = getSysEnd+1
      searray.append ((getSysStart, getSysEnd))
  return tuple(searray)

#prints Yamaha SY85 Sysex Block type 
def getType(sysBlock):
  return pprint (sysBlock[10:16])

#prints Yamaha SY85 Sysex Block name for 0065VC and 0065PF  
def getNamePV(sysBlock):
   return pprint(sysBlock[105:113])

#Prints all names of SysEx Block
def printNames(sysex):
  se=findStart(sysex)
  counter = 0
  for x in se:
    start=x[0]
    end=x[1]
    BP.append ( getNamePV(sysex[start:end]))
    print (getType(sysex[start:end]))
    print (getNamePV(sysex[start:end]))
  return BP

#Gets All patch names from sysex and returns list
def GetPatchNames(sysex):
  se=findStart(sysex)
  counter = 0
  for x in se:
    start=x[0]
    end=x[1]
    BP.append ( getNamePV(sysex[start:end]))
  return BP

def PatchNamesToXML(patchesList):
   counter = 0
   for x in patchesList:
      output = "<Patch Number=\""+( str(counter+1).zfill(2))+"\" Name=\""+ patchesList[counter]+"\" ProgramChange="+ str(counter)+"/>" # Change=0 needs fixing
      print (output)
      counter = counter + 1

def BankPrint(sysexfilename): # main meat and potatoes
  sysex = loadSysex(sysexfilename)
  patchlist = GetPatchNames(sysex)
  pnum=createBankArray()
  patchheaders = list()
  patchesXMLoutput=list()
  xmloutput = str() 
  bankcounter=0
  patchnumber =1

  for x in BANKS:
    patchnumber=1
    bankname = BANK_PREFIX + ": " + x
    for patch in patchlist[BANK_SLICES[bankcounter]]:
      needs = pnum[patchnumber -1]+"\""+ " Name=\"" +patch +" "
      #@TODO UPDATE patchnumber to contain A1, A2, ..., B1, B2, ... , ect..
      #needs = str(patchnumber)+"\""+ " Name=\"" +patch +" "
      #needs = BANK_PREFIX + ": " + BANKS[bankcounter] + " " +str(patchnumber).zfill(2) + " " +patch
      xmlout = "     <Patch Number=\""+ needs +"\" ProgramChange=\""+ str(patchnumber-1)+"\"/>\n"
      patchesXMLoutput.append(xmlout)
      print (needs)
      patchnumber =patchnumber+1
    bankcounter=bankcounter+1

  counter = 0
  for x in BANKS:
     sp = (0, 64, 128, 192, 256, 320) # Bank Start positions
     lsbBankswitch = ("")
     header1 =      "\n\n\n<PatchBank Name = \""+BANK_PREFIX+" "+ BANKS[counter]+"\">\n"
     Mcommands =    "  <MIDICommands>\n"
     cchangemsb =   "     <ControlChange Control = \"0\" Value = \"0\"/>\n"
     cchangelsb =   "     <ControlChange Control = \"32\" Value = \""+BANK_CODE[counter]+"\" />\n" #needs variable for lsb
     Mccomandsend = "</MIDICommands>\n"
     patchnamestart = "  <PatchNameList>\n"
     bankheader = header1 + Mcommands + cchangemsb + cchangelsb + Mccomandsend + patchnamestart
     patchheaders.append(bankheader)
     counter=counter + 1
  #Properly create block of patch names with proper header
  pcounter = 0
  for x in sp:
     pblock = slice (x, x+64)
     xmloutput = xmloutput + str(patchheaders[pcounter])
     for y in patchesXMLoutput[pblock]:
        xmloutput =xmloutput + y
     pcounter = pcounter + 1
     xmloutput = xmloutput + ("    </PatchNameList>\n  </PatchBank>\n")   
  return xmloutput

  
xmlout2 = (BankPrint (sysexfile))
print ("Data wrote to file : ")
#print (xmlout2)

savemidnam(xmlout2,midnamoutfile)