# A script to automate the whole process of importing holiday data, sorting it, and then building graphs with the avgs
# Will generate 1 graph per run, so use for 1 holiday (over several years)
# Takes 6 Parameters - Symbol, DeliveryMonthCode, Database, DateFileName, HeaderLine, and Units
# The File needs to be in this format exactly:
#   Two chunks, each with lines of dates. The first will be the Holiday dates, the second, Normal Days
#   In between the two chunks should be an empty line
import sys
import os
from shutil import copyfile
from subprocess import check_output
from datetime import datetime
from datetime import timedelta

if len(sys.argv) < 7:
    print("USAGE: %s Symbol DeliveryMonthCode Database DateFileName HeaderLine(Probably 2) Holiday" % (sys.argv[0]))
    sys.exit(1)

symbol = sys.argv[1]
deliveryMonth = sys.argv[2]
dbNum = sys.argv[3]
dateFileName = sys.argv[4]
headerLine = sys.argv[5]
units = 'cents'

if not '@' in symbol:
    print('You might need to append an @ to the beginning of your Symbol. I just noticed you didn\'t have one, is all.')

dirName = symbol + "WorkFolder"
os.makedirs(dirName)
copyfile('generateVolData.bat', dirName + '\\' + 'generateVolData.bat')
copyfile('AggregateRatioSumGraph.py', dirName + '\\' + 'AggregateRatioSumGraph.py')
copyfile('tick.sh', dirName + '\\tick.sh')
copyfile('OneTickToLSS.py', dirName + '\\OneTickToLSS.py')
copyfile('moveFiles.bat', dirName + '\\moveFiles.bat')
copyfile(dateFileName, dirName + '\\' + dateFileName)
os.chdir(dirName)

# So now everything is copied in, and we can get cracking
# Read in the file
dateFile = open(dateFileName, 'r')

listOfDates = [[], []]
mode = 0

for line in dateFile:
    line = line.rstrip()
    if line == '':
        mode = 1
    else:
        listOfDates[mode].append(line)

os.makedirs('Holiday')
os.makedirs('NextDay')
copyfile('generateVolData.bat', 'Holiday\\generateVolData.bat')
copyfile('tick.sh', 'Holiday\\tick.sh')
copyfile('tick.sh', 'NextDay\\tick.sh')
copyfile('moveFiles.bat', 'Holiday\\moveFiles.bat')
copyfile('moveFiles.bat', 'NextDay\\moveFiles.bat')
copyfile('generateVolData.bat', 'NextDay\\generateVolData.bat')
copyfile('OneTickToLSS.py', 'Holiday\\OneTickToLSS.py')
copyfile('OneTickToLSS.py', 'NextDay\\OneTickToLSS.py')

print('Files Successfully Copied')


def stringToDateTime(myString):
    return datetime.strptime(myString, '%Y%m%d')

def dateTimeToString(myDateTime):
    return myDateTime.strftime('%Y%m%d')

def runDataScript(listy):
    for myStr in listy:
        myDateTime = stringToDateTime(myStr)
        myYear = str(myDateTime.year % 10)
        togetherSymbol = symbol + myYear + deliveryMonth
        dayZero = myDateTime - timedelta(days=1)
        myDateTime = dateTimeToString(myDateTime)
        dayZero = dateTimeToString(dayZero)
        print('Trying', togetherSymbol)
        mycmd = ' '.join(["generateVolData.bat", togetherSymbol, dbNum, dayZero, myDateTime, headerLine, units])
        check_output(mycmd)
        print('\n\n\n\n\n\n\n\n\n')

def pullDataIntoMain():
    # Pull the files into the folder, delete the other files, then the other folders
    # I'll leave the subfolders just because I don't want to deal with it
    check_output('moveFiles.bat')

os.chdir('Holiday')
runDataScript(listOfDates[0])
pullDataIntoMain()
print('Done With the Holidays :(')

os.chdir('..')
os.chdir('NextDay')
runDataScript(listOfDates[1])
pullDataIntoMain()
os.chdir('..')
print('Done with the Normal Days')

print('And now to run the big boi')
check_output(' '.join(['python AggregateRatioSumGraph.py', 'NextDay', 'Holiday', symbol[1:]]))
print('Thanks for using the Automator! May your volumes profile.')