#!/usr/bin/env python
#
# Fit single clusters, given fit func and fit params as specified in fitParamFile
#
# Anthony Ho, ahho@stanford.edu, 2/3/2015
# Last update 8/10/2016


# Import libraries
import os, sys
import argparse
import pandas as pd
import numpy as np
from itertools import izip
import fitlib
import parselib
import parlib
from joblib import Parallel, delayed
import multiprocessing


def main():

    # Get options and arguments from command line
    parser = argparse.ArgumentParser(description="fit single clusters")
    parser.add_argument('-n', '--numCores', type=int, default=1, help="number of cores to use (default=1)")
    parser.add_argument('-v', '--verbose', type=int, default=0, help="verbosity of progress. 0 = no verbosity. (default=0)")
    parser.add_argument('fitParamFilePath', help="path to the file that specifies fitting parameters")
    parser.add_argument('inputFilePath', help="path to the file containing the raw signals of the clusters to be fitted")
    parser.add_argument('outputFilePath', help="path to the output file")
    args = parser.parse_args()

    # Define default attributes from the fit result to write to the output file
#    outputAttrs = ['params',
#                   'paramSEs',
#                   'paramTvals',
#                   'paramPvals',
#                   'RSS',
#                   'reChi2',
#                   'SER',
#                   'nit',
#                   'status']

    # Import fit parameters from fitParamFile
    fitParamDict, x, outputAttrs = fitlib.lsqcurvefit.parseFitParamFromFile(args.fitParamFilePath)

    # Read inputFile as Pandas dataframe
    allClusters = pd.read_csv(args.inputFilePath, sep='\t')
    allSignals = parselib.splitConcatedDFColumnIntoNDarray(allClusters['signals'], ':')
    if isinstance(x, str):
        allIndepVar = parselib.splitConcatedDFColumnIntoNDarray(allClusters[x], ':')

    # Fit single clusters
    if isinstance(x, str):
        fitResults = Parallel(n_jobs=args.numCores, verbose=args.verbose)(delayed(fitlib.lsqcurvefit)(x=indepVar, y=signal, **fitParamDict)
                                                                          for indepVar, signal in izip(allIndepVar, allSignals))
    else:
        fitResults = Parallel(n_jobs=args.numCores, verbose=args.verbose)(delayed(fitlib.lsqcurvefit)(x=x, y=signal, **fitParamDict)
                                                                          for signal in allSignals)

    # Add attributes as defined in outputAttrs as columns in the allClusters dataframe
    for attr in outputAttrs:
        val0 = getattr(fitResults[0], attr)
        if not isinstance(val0, np.ndarray):
            allClusters[attr] = [getattr(r, attr) for r in fitResults]
        else:
            attrNames = [attr+str(i+1) for i in range(len(val0))]
            allClusters = allClusters.join(pd.DataFrame([getattr(r, attr) for r in fitResults], columns=attrNames))

    allClusters.to_csv(args.outputFilePath, sep='\t', index=False)

    return 1

if __name__ == "__main__":
    main()
