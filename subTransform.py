#!/usr/bin/python

'''
@author: guyadini, 2012
Used to sync srts by finding a reasonable affine transformation.
Some typical usage examples:
1. subTransform -i <filename>: will calculate the a,b parameters of the affine transform, by asking the user
    to give the correct time of the first and last subtitles of the input srt file in the video.
2. subTransform -i <filename> -o <synced srt file>: will calculate a,b as before, and sync the input file, writing
    the result to the outfile.
3. subTransform -a <a as float> -b <b as float> --applyTo '<some pattern>' --prefix <some_prefix>: apply the calculated
    transformation to multiple files (any files which match the input pattern), and append the prefix to the names
    of the output files.
'''

import sys
import argparse
import numpy as np
import re
import glob

class Subtitle(object):
    def __init__(self):
        self.txt = ""
    def __str__(self):
        return '%d\n%s --> %s \n%s' %(self.idx, tupleToStr(self.start), tupleToStr(self.end), self.txt)
    def __repr__(self):
        return self.__str__()
    def applyTransform(self,a,b):
        '''apply a mSecs --> a*mSecs +b transform to the times'''
        trans = lambda t: millisecsToTuple ( round(a * tupleToMillisecs(t) + b))
        self.start = map(int,trans(self.start))
        self.end = map(int,trans(self.end))


def toTuple(s):
    '''return hours, minutes, seconds,millisecs
    if s is of the '00:45:18,000' formatting'''
    t, ms = s.split(',')
    return [int(x) for x in t.split(':')] + [int(ms)]

def fromTuple(t):
    '''returns h:m:s,ms, as a string from corresponding tuple'''
    return '%d:%d:%d,%03d' %t

def tupleToMillisecs(t):
    return t[3] + t[2] *1000 + t[1] *1000 * 60 + t[0] * 1000 * 36000

def millisecsToTuple(n):
    return ( n/ (1000*60*60), n/ (1000*60) % 60 , n/1000 % 60 , n %1000)



def parseTimes(line):
    sp = map(toTuple,line.split('-->'))
    start = sp[0]
    end = sp[-1]
    return (start, end)

def tupleToStr(t):
    s = '%d:%d:%d,%d' %tuple(t)
    return s


def parseSrt(fn):
    subs = []
    sub = Subtitle()
    state = 0
    with open(fn) as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        if not line:
            state = 0
            if sub and sub.txt:
                subs.append(sub)
            sub = Subtitle()
            continue
        state += 1
        if state == 1:
            sub.idx = int(line)
        if state == 2:
            times = parseTimes(line)
            sub.start = times[0]
            sub.end = times[1]
        if state > 2:
            sub.txt += line + '\n'
    if sub not in subs: subs.append(sub)
    return subs



def printSubsToOutfile(subs, outFile):
    with open(outFile,'w') as f:
            f.write('\n'.join( [str(sub) for sub in subs]))
        

def transformSubs(subs,a,b):        
    for sub in subs:
        if re.search('\<.*\>', sub.txt):
             continue
        sub.applyTransform(a,b)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest = 'filename', default = None )
    parser.add_argument('-a', dest = 'a', default = None)
    parser.add_argument('-b', dest = 'b', default = None)
    parser.add_argument('-o', dest = 'outFile', default = 'out.srt')
    parser.add_argument('--applyTo', dest = 'applyTo', default = None)
    parser.add_argument('--prefix', dest = 'prefix', default = 'synced_')
    args = parser.parse_args()
  
    #If a and b aren't given, they must be calculated from the .srt file 
    if args.a is None or args.b is None:
        if not args.filename:
            print 'Please use -i <filename> to set the input to learn the a and b parameters from, or -a <val> -b <val> to set them manually'
        fn =  args.filename
        subs = parseSrt(fn)
        sortedSubs = sorted(subs, key = lambda x: tupleToMillisecs(x.start))
        sortedSubs = [s for s in sortedSubs if re.search('\<.*\>', s.txt) is None]
        first, last = ( sortedSubs[0], sortedSubs[-1])
        inFirst = raw_input('Please enter the time of the first subtitle in hours:minutes:seconds. It should read:\n %s' 
            % first.txt)
        inLast = raw_input('Please enter the time of the last subtitle in hours:minutes:seconds. It should read:\n %s' \
            % last.txt)
        try:
            firstT = toTuple(inFirst.strip()+',000')
            lastT = toTuple(inLast.strip()+',000')
            startTimes = [ first.start, last.start ]
            knownTimes = [ firstT, lastT ]
        except Exception as e:
            print 'Bad input'
            sys.exit(1)
        
        mSecStarts = np.array(map(tupleToMillisecs,startTimes))
        mSecKnowns = np.array(map(tupleToMillisecs,knownTimes))
        #Set as a matrix: sMat * X = kMat, where X is the 
        sMat = np.array( [ [x,1] for x in mSecStarts ] )
        kMat = mSecKnowns
        #find best fit for ax +b 
        a, b = np.linalg.lstsq(sMat, kMat)[0]
        print 'Calculated: a = %f, b=%f' %(a,b)
    else:
        a = float(args.a)
        b = float(args.b)
   
    #apply to each file matching the pattern
    if args.applyTo:
        for fn in glob.glob(args.applyTo):
            print 'Opening ' + fn + ' ...'
            subs = parseSrt(fn)
            transformSubs(subs,a,b)
            printSubsToOutfile(subs, args.prefix+fn)
            print 'Done'
        
    #apply to the input file
    elif args.outFile:
        transformSubs(subs,a,b)
        printSubsToOutfile(subs, args.outFile) 
    


