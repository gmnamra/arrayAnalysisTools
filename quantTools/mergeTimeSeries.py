#!/usr/bin/env python
#
# Merge time series data of a tile into a single file
#
# Anthony Ho, ahho@stanford.edu, 1/22/2015
# Last update 1/26/2015


## Import libraries
import os, sys
import argparse
import glob
import pandas as pd
from numpy import pi
import numpy as np


## Parse timestamp from the last part of the filename as datetime64[ns] objects
def parseTimeFromFilename(fileFullPath):
    (dirPath, filename) = os.path.split(fileFullPath)
    (fileBasename, fileExt) = os.path.splitext(filename)
    timestampStr = fileBasename.split('_')[-1]
    timestamp = pd.to_datetime(timestampStr, format='%Y.%m.%d-%H.%M.%S.%f')
    return timestamp


## Concatenate designated columns of a datadrame into a series of 
## strings, separated by separator
def concatDFColumnsIntoSeries(df, columnsLabels, separator):
    s = pd.Series(df[columnsLabels[0]].map(str))
    for currCol in columnsLabels[1:]:
        s = s+separator+df[currCol].map(str)
    return s    


## Concatenate designated elements of a series into a string
## separated by separator
def concatSeriesIntoString(series, indexLabels, separator):
    string = str(series[indexLabels[0]])
    for currElement in indexLabels[1:]:
        string = string+separator+str(series[currElement])
    return string


def main():

    ## Get options and arguments from command line
    parser = argparse.ArgumentParser(description="merge time series data of a tile into a single file")
    parser.add_argument('-r', '--refTime', help="start time of the experiment. If not provided, the start time will be set to the first time point")
    parser.add_argument('numTimepoints', help="number of timepoints")
    parser.add_argument('CPfluorFilePattern', help="pattern of the path to the input CPfluor files. Replace timepoint number with {} and timestamp with *")
    parser.add_argument('outputFilePathNoExt', help="basename of the output files with no extensions")
    args = parser.parse_args()

    ## Initialization 

    twoPi = 2 * pi
    
    numTimepoints = int(args.numTimepoints)
    replaceToTimepoint = '{}'

    clusterIDColLabels = ['instrumentID', 'runID', 'flowcellID', 'flowcellSide', 'tileID', 'x-pos', 'y-pos']
    fitResultsColLabels = ['fitted', 'amp', 'sigma', 'fittedX', 'fittedY']
    CPfluorColLabels = clusterIDColLabels + fitResultsColLabels

    CPsignals = pd.DataFrame()
    CPsigmas = pd.DataFrame()
    CPtimes = pd.Series()
    
    CPsignalTime = pd.DataFrame(columns=['clusterID','signals','times'])
    CPsigmaTime = pd.DataFrame(columns=['clusterID','sigmas','times'])

    refTime = pd.to_datetime(args.refTime, format='%Y.%m.%d-%H.%M.%S.%f')

    ## Output files
    CPsignalTimeFilePath = args.outputFilePathNoExt+".CPsignalTime"
    CPsigmaTimeFilePath = args.outputFilePathNoExt+".CPsigmaTime"


    ## Go through all time points
    for timepoint in range(1,numTimepoints+1):
        
        # Get the path to the current CPfluor file
        currTimepoint = str(timepoint)
        currCPfluorFilePattern = args.CPfluorFilePattern.replace(replaceToTimepoint, currTimepoint)
        listOfCurrCPfluorMatchingPattern = glob.glob(currCPfluorFilePattern)

        if len(listOfCurrCPfluorMatchingPattern) > 1:
            # Check if more than one CPfluor file matching pattern exists
            # If so, quit
            print "More than one CPfluor file found in current timepoint!"
            print currCPfluorFilePattern
            print "Quitting now..."
            return 0
        elif len(listOfCurrCPfluorMatchingPattern) == 1:
            # If a unique CPfluor file exists for the current timepoint, proceed
            
            # Get the path to the current CPfluor file
            currCPfluorFile = listOfCurrCPfluorMatchingPattern[0]
            # Load CPfluor file
            currCPfluorData = pd.read_csv(currCPfluorFile, sep=':', names=CPfluorColLabels)
            # Add data from current timepoint to the dataframes
            # If cluster is not fitted, replace value with NaN
            CPsignals[currTimepoint] = ((twoPi * currCPfluorData.amp * currCPfluorData.sigma**2) 
                                        / currCPfluorData.fitted).replace([np.inf, -np.inf], np.nan)
            CPsigmas[currTimepoint] = (currCPfluorData.sigma / currCPfluorData.fitted).replace([np.inf, -np.inf], np.nan)
            # Parse timestamp from CPfluor filename
            CPtimes[currTimepoint] = parseTimeFromFilename(currCPfluorFile)


    ## Compute timepoints relative to the reference timepoint and convert to float64
    if args.refTime == None:
        CPtimes = (CPtimes - CPtimes.iloc[0]).apply(lambda x: x / np.timedelta64(1, 's'))
    else:
        CPtimes = (CPtimes - refTime).apply(lambda x: x / np.timedelta64(1, 's'))

    ## Get list of columns/indices labels
    listCPsignalsColLabels = list(CPsignals.columns.values)
    listCPsigmasColLabels = list(CPsigmas.columns.values)
    listCPtimesIndLabels = list(CPtimes.index.values)

    ## Making CPsignalTime dataframe
    CPsignalTime['clusterID'] = concatDFColumnsIntoSeries(currCPfluorData, clusterIDColLabels, ':')
    CPsignalTime['signals'] = concatDFColumnsIntoSeries(CPsignals, listCPsignalsColLabels, ':')
    CPtimesInStr = concatSeriesIntoString(CPtimes, listCPtimesIndLabels, ':')
    CPsignalTime['times'] = [ CPtimesInStr ]*len(CPsignalTime.index)

    ## Making CPsigmaTime dataframe
    CPsigmaTime['clusterID'] = CPsignalTime['clusterID']
    CPsigmaTime['sigmas'] = concatDFColumnsIntoSeries(CPsigmas, listCPsigmasColLabels, ':')
    CPsigmaTime['times'] = CPsignalTime['times']

    ## Writing dataframes to files
    CPsignalTime.to_csv(CPsignalTimeFilePath, sep='\t', index=False)
    CPsigmaTime.to_csv(CPsigmaTimeFilePath, sep='\t', index=False)

    return 1 

if __name__ == "__main__":
    main()
