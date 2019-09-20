import os, sys, csv
import numpy as np
from scipy import stats

'''
Author : Sara Willis
Date   : September 20, 2019

A basic python script to read raw cyberduck gui csv files and 
print the means and standard errors of each filesize transfer
'''

# Raw trials file
filename = 'CyberduckGUITest_GdriveToHPC.csv'

outputFilename = filename.replace('.csv','_means.csv')


outputFile = open(outputFilename,'w')
outputFile.write('FileSize,Speed_Mean,Speed_SE\n')

Header = True

TrueFileSizes_MB = {'1M':1,'10M':10.5,'100M':104.9,'1G':1100,'10G':10700,'100G':107400}

TransferStats = {'1M':[],
                 '10M':[],
                 '100M':[],
                 '1G':[],
                 '10G':[],
                 '100G':[]}


with open(filename,'r') as f:
    reader = csv.reader(f, delimiter =',')
    for row in reader:
        if Header == True:
            Header = False
        else:
            FileSize,Time = row
            if Time != '':
                TransferStats[FileSize].append(float(Time))
                
for FileSize,Times in TransferStats.items():
    if len(Times) != 0:
        Speeds = [TrueFileSizes_MB[FileSize]/i for i in Times]
        if len(Speeds) != 1:
            Speed_Mean, Speed_SE = np.mean(Speeds), stats.sem(Speeds)
        else:
            Speed_Mean, Speed_SE = Speeds[0], 0
        outputFile.write('%s,%s,%s\n'%(FileSize,Speed_Mean,Speed_SE))
    else:
        outputFile.write('%s,,\n'%FileSize)

outputFile.close()
