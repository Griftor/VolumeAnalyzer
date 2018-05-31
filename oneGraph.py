import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import sys

if len(sys.argv) < 2:
    print("USAGE: %s input-file" % (sys.argv[0]))
    sys.exit(1)

BUCKETSIZE = timedelta(minutes=5)
FIVEHOURS = timedelta(hours=5)
ONEDAY = timedelta(days=1)
CSVFILE = sys.argv[1]

def toDateTime(myString):
    return datetime.strptime(myString, '%Y-%m-%d %H:%M:%S.%f')

df = pd.read_csv(CSVFILE, header=None, names=['CT', 'ST', 'Seq', 'Type', 'Market', 'Price', 'Size', 'Feed_Type', 'Side'])

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
volOverTime = pd.DataFrame(priceList, columns=['Time', 'Volume'])

fig, ax = plt.subplots()
ax.plot(volOverTime['Time'], volOverTime['Volume'], marker='', linestyle='-')
plt.show()