'''
Written by Andre Renault, 2022-09-14.
This is a script to convert Solinst .csv files into .xle files.
This allows for compensation of Levelogger data by Barologger data.
Lots of loose ends, particularly in the header section, to be tied up.
For instance, start and stop times should be the first and last times in the csv.
But this is good enough for now I think.
'''

def cleanuptime(toClean):
    oldDigs = str(toClean[:2])
    if toClean[-2:] == 'pm':
        if oldDigs == '12':
            newDigs = oldDigs
        else:
            newDigs = str(int(oldDigs)+12)
    elif oldDigs == '12':
        newDigs = '00'
    else:
        newDigs = oldDigs
    newStr = newDigs + toClean[2:-3]
    return newStr

def cleanupdate(toClean):
	mdy = re.findall(r'\b\d+\b', toClean)
	if int(mdy[0]) > 40: return toClean
	if int(mdy[0]) < 10: mdy[0] = '0'+mdy[0]
	if int(mdy[1]) < 10: mdy[1] = '0'+mdy[1]
	ymd = "{}-{}-{}".format(mdy[2],mdy[0],mdy[1])
	return ymd


import re
import argparse

parser = argparse.ArgumentParser(description='Extract position data from ADVfiles.')
parser.add_argument('input', help = 'input filename(s)', nargs='+')
#parser.add_argument('output', help = 'output filename')
args = parser.parse_args()

for i in args.input:
	inFileName = i
	#outFileName = args.output
	outFileName = inFileName.replace("csv","xle")
	print("Opening " + inFileName)
	'''
	file1 = open(inFileName, 'r')
	Lines = file1.readlines()
	Nums = []
	'''
	if "BL" in inFileName:
		modelNumber = "M1.5"
	elif "LV" in inFileName:
		modelNumber = "M5"
	else:
		modelNumber = "M10"

	outFileObj = open(outFileName, 'w', encoding="utf8", errors='ignore')
	inFileObj = open(inFileName, 'r', encoding="utf8", errors='ignore')
	myline = inFileObj.readline()
	myline = inFileObj.readline()
	Serial_number = myline.split(",")
	myline = inFileObj.readline()
	myline = inFileObj.readline()
	Project_ID = myline.split(",")
	myline = inFileObj.readline()
	myline = inFileObj.readline()
	Location = myline.split(",")
	myline = inFileObj.readline()
	myline = inFileObj.readline()
	FUNIT = myline.split(": ")
	levelUnit = str(FUNIT[1]).strip()
	myline = inFileObj.readline()
	if myline[0:7] == "Offset:":
		Offset = str(re.findall(r'\b\d+\b',myline))
		myline = inFileObj.readline()
	else:
		Offset = "0.0000"
	myline = inFileObj.readline()
	TUNIT = myline.split(": ")
	tempUnit = str(TUNIT[-1]).strip()
	myline = inFileObj.readline()

	outFileObj.write("<?xml version=\"1.0\" ?>"+'\n')
	outFileObj.write("<Body_xle>"+'\n')
	outFileObj.write("    <Data>"+'\n')

	# Now the fun begins
	counter = 0
	myline = inFileObj.readline()
	while myline:
		counter += 1
		myline_s = myline.rstrip()
		values = myline_s.split(",")
		theDate = cleanupdate(str(values[0]))
		theTime = cleanuptime(str(values[1]))
		if counter == 1:
			startDate = theDate
			startTime = theTime
		outFileObj.write("         <Log id=\""+str(counter)+"\">"+'\n')
		outFileObj.write("             <Date>"+theDate+"</Date>"+'\n')
		outFileObj.write("             <Time>"+theTime+"</Time>"+'\n')
		if len(values) == 5:
			outFileObj.write("             <ms>"+str(values[-3])+"</ms>"+'\n')
		outFileObj.write("            <ch1>"+str(values[-2])+"</ch1>"+'\n')
		outFileObj.write("            <ch2>"+str(values[-1])+"</ch2>"+'\n')
		outFileObj.write("        </Log>"+'\n')
		stopDate = theDate
		stopTime = theTime
		myline = inFileObj.readline()
	inFileObj.close()   
	outFileObj.write("    </Data>"+'\n')

	# This is all kind of boilerplate and I couldn't be bothered to deal with it
	# Further experimentation will deal with leaving out these variables entirely
	outFileObj.write("    <File_info>"+'\n')
	outFileObj.write("        <Company></Company>"+'\n')
	outFileObj.write("        <LICENCE></LICENCE>"+'\n')
	outFileObj.write("        <Date>"+theDate+"</Date>"+'\n')
	outFileObj.write("        <Time>"+theDate+"</Time>"+'\n')
	outFileObj.write("        <FileName>"+inFileName+"</FileName>"+'\n')
	outFileObj.write("        <Created_by>Version 4.6.2</Created_by>"+'\n')
	outFileObj.write("        <Downloaded_by>Version 4.6.2</Downloaded_by>"+'\n')
	outFileObj.write("        <Program_by>PC Software 4.6.2</Program_by>"+'\n')
	outFileObj.write("        <Interface>Desktop Reader (513755)</Interface>"+'\n')
	outFileObj.write("    </File_info>"+'\n')
	outFileObj.write("    <Instrument_info>"+'\n')
	outFileObj.write("        <Instrument_type>L5_LT</Instrument_type>"+'\n')
	outFileObj.write("        <Model_number>"+modelNumber+"</Model_number>"+'\n')
	outFileObj.write("        <Instrument_state>Stopped</Instrument_state>"+'\n')
	outFileObj.write("        <Serial_number>"+str(Serial_number[0]).strip()+"</Serial_number>"+'\n')
	outFileObj.write("        <Battery_voltage>0.0000</Battery_voltage>"+'\n')
	outFileObj.write("        <Battery_charge>0.00</Battery_charge>"+'\n')
	outFileObj.write("        <Channel>2</Channel>"+'\n')
	outFileObj.write("        <Firmware>1.005</Firmware>"+'\n')
	outFileObj.write("    </Instrument_info>"+'\n')
	outFileObj.write("    <Instrument_info_data_header>"+'\n')
	outFileObj.write("        <Project_ID>"+str(Project_ID[0]).strip()+"</Project_ID>"+'\n')
	outFileObj.write("        <Location>"+str(Location[0]).strip()+"</Location>"+'\n')
	outFileObj.write("        <Latitude>0.000</Latitude>"+'\n')
	outFileObj.write("        <Longtitude>0.000</Longtitude>"+'\n')
	outFileObj.write("        <Sample_rate>30000</Sample_rate>"+'\n')
	outFileObj.write("        <Sample_mode>0</Sample_mode>"+'\n')
	outFileObj.write("        <!--Linear-->"+'\n')
	outFileObj.write("        <Memory_mode>Slate</Memory_mode>"+'\n')
	outFileObj.write("        <Event_ch>1</Event_ch>"+'\n')
	outFileObj.write("        <Event_threshold>0.000000</Event_threshold>"+'\n')
	outFileObj.write("        <Schedule />"+'\n')
	outFileObj.write("        <Start_time>"+startDate+" "+startTime+"</Start_time>"+'\n')
	outFileObj.write("        <Stop_time>"+stopDate+" "+stopTime+"</Stop_time>"+'\n')
	outFileObj.write("        <Num_log>"+str(counter)+"</Num_log>"+'\n')
	outFileObj.write("    </Instrument_info_data_header>"+'\n')
	outFileObj.write("    <Ch1_data_header>"+'\n')
	outFileObj.write("        <Identification>LEVEL</Identification>"+'\n')
	outFileObj.write("        <Unit>"+levelUnit+"</Unit>"+'\n')
	outFileObj.write("        <Parameters>"+'\n')
	outFileObj.write("            <Offset Val=\""+Offset+"\" Unit=\""+levelUnit+"\" />"+'\n')
	outFileObj.write("        </Parameters>"+'\n')
	outFileObj.write("    </Ch1_data_header>"+'\n')
	outFileObj.write("    <Ch2_data_header>"+'\n')
	outFileObj.write("        <Identification>TEMPERATURE</Identification>"+'\n')
	outFileObj.write("        <Unit>"+tempUnit+"</Unit>"+'\n')
	outFileObj.write("        <Parameters />"+'\n')
	outFileObj.write("    </Ch2_data_header>"+'\n')

	outFileObj.write("</Body_xle>"+'\n')
	print("Closing " + outFileName)
	outFileObj.close()   
