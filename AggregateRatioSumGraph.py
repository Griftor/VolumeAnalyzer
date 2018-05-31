import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import sys
import os
from functools import reduce

if len(sys.argv) < 4:
    print("USAGE: %s input-folder1 input-folder2 symbol" % (sys.argv[0]))
    sys.exit(1)

BUCKETSIZE = timedelta(minutes=5)
FIVEHOURS = timedelta(hours=5)
ONEDAY = timedelta(days=1)
CSVFILE = sys.argv[1]

def toDateTime(myString):
    return datetime.strptime(myString, '%Y-%m-%d %H:%M:%S.%f')

def makePriceListForPlotting(fileName, col2Name):
    df = pd.read_csv(fileName, header=None,
                     names=['CT', 'ST', 'Seq', 'Type', 'Market', 'Price', 'Size', 'Feed_Type', 'Side'])

    volDf = df[df['Type'] == 'T']

    priceList = []
    startTime = toDateTime(volDf.iat[0, 1])
    bucket = startTime + BUCKETSIZE
    currentVolume = 0
    totalVol = 0

    for index, row in volDf.iterrows():
        if toDateTime(row['CT']) > bucket:
            # Shift by five hours to get into UTC time zone
            secs = ((bucket - BUCKETSIZE) - startTime).total_seconds() / 3600
            priceList.append([secs, currentVolume])
            currentVolume = 0
            bucket += BUCKETSIZE

        currentVolume += int(row['Size'])
        totalVol += int(row['Size'])

    # One last time to get the last of the data
    secs = ((bucket - BUCKETSIZE) - startTime).total_seconds() / 3600
    priceList.append([secs, currentVolume])

    return totalVol, pd.DataFrame(priceList, columns=['Time', col2Name])

def join_dfs(ldf, rdf):
    return pd.merge(ldf, rdf, how='outer', on='Time')

# START OF MAIN
# For each Folder, loop through and create a Volume DataFrame
myListOfDfs1 = []
numDfs = 0
dfAvgVol1 = 0
for filename in os.listdir(sys.argv[1]):
    if '.txt' in filename:
        volSum, dailyVolume = makePriceListForPlotting(sys.argv[1] + "\\" + filename, filename + "_Volume")
        myListOfDfs1.append(dailyVolume)
        numDfs += 1
        dfAvgVol1 += volSum

dfAvgVol1 /= numDfs

# Combine the Dataframes and create an average column (this one using the ratio of the bucket size)
ultimateTable1 = reduce(join_dfs, myListOfDfs1)
ultimateTable1 = ultimateTable1.fillna(0)
ultimateTable1['avg'] = ultimateTable1.drop('Time', axis=1).mean(axis=1) / dfAvgVol1

totalVolPercent = 0
totalVolList1 = []
for index, row in ultimateTable1.iterrows():
    totalVolPercent += float(row['avg'])
    totalVolList1.append(totalVolPercent)

ultimateTable1['avgSum'] = totalVolList1

myListOfDfs2 = []
numDfs = 0
dfAvgVol2 = 0
for filename in os.listdir(sys.argv[2]):
    if '.txt' in filename:
        volSum, dailyVolume = makePriceListForPlotting(sys.argv[2] + "\\" + filename, filename + "_Volume")
        myListOfDfs2.append(dailyVolume)
        numDfs += 1
        dfAvgVol2 += volSum

dfAvgVol2 /= numDfs

ultimateTable2 = reduce(join_dfs, myListOfDfs2)
ultimateTable2 = ultimateTable2.fillna(0)
ultimateTable2['avg'] = ultimateTable2.drop('Time', axis=1).mean(axis=1) / dfAvgVol2

totalVolPercent = 0
totalVolList2 = []
for index, row in ultimateTable2.iterrows():
    totalVolPercent += float(row['avg'])
    totalVolList2.append(totalVolPercent)

ultimateTable2['avgSum'] = totalVolList2

fig = plt.figure()
ax1 = fig.add_subplot(111)
ax1.plot(ultimateTable1['Time'], ultimateTable1['avgSum'], 'b-', ultimateTable2['Time'], ultimateTable2['avgSum'], 'r-')

plt.title(sys.argv[3] + ' Holiday vs One Week Later Avg 2014-2018')
plt.grid()
plt.show()
