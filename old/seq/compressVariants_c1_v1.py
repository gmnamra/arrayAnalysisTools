#!/usr/bin/env python
#
# Group and analyze sequences by sequence variant blocks
#
# Anthony Ho, 7/9/2014

## Import libraries
import os, sys
import argparse
import numpy as np
import Levenshtein
from collections import Counter

def main():

    ## Get options and arguments from command line
    parser = argparse.ArgumentParser(description="Group and analyze sequences by sequence variant blocks")
    parser.add_argument("inputFile", help="input file to be analyzed")
    args = parser.parse_args()

    ## Open file for writing
    statFileName = args.inputFile+".stat"

    ## Initialization
    numSeqs = 0 
    lineCount = 0

    seqBlock = []

    ## Initial counting
    with open(args.inputFile,"r") as r:
        for line in r:
            numSeqs += 1
            if numSeqs == 1:
                lastSeq = line.rstrip().split('\t')[1]

    ## Going through the input file
    with open(args.inputFile, "r") as r, open(statFileName, "w") as w:
        for line in r:

            # Reading line by line
            lineCount += 1
            if lineCount % 1000 == 0:
                print "Processing the "+str(lineCount) +"th sequence" 
            seqLine = line.rstrip().split('\t')
            seq = seqLine[1]

            # At the beginning of each SV block, 
            # and do it for the very last line instead of the very first line
            if seq != lastSeq or lineCount == numSeqs:
                
                # Add in the very last line to the SV block
                # Append sequence to the SV block
                if lineCount == numSeqs:
                    seqBlock.append(seq)

                # Analyze SV block here
                degeneracy = len(seqBlock)
                w.write(str(degeneracy)+"\n")
                
                # Initialize for the next SV block
                seqBlock = []

            # Append sequence to the SV block
            seqBlock.append(seq)

            # Make the current barcode the new last barcode
            lastSeq = seq
               
    ## Printing summary
    print "\nTotal number of sequences analyzed:", str(numSeqs), "(100%)"

    r.close()
    w.close()
    
    return 1

if __name__ == "__main__":
    main()

