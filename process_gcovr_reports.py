#!/usr/bin/env python

###
#
# call graph clustering using k-means
# Author: Van-Thuan Pham
#
###

import re
import sys
import argparse
import os
from sets import Set
import copy
import random
import operator

def main(gcovr_dir):
  fuzzer_cov_dict = dict()
  #iterate through all gcovr reports
  for reportFileName in os.listdir(gcovr_dir):
    if reportFileName.endswith(".txt"): 
      bSet = Set([])
      f = open(os.path.join(gcovr_dir, reportFileName), "r")
      for line in f:
        tmpStrList = re.split('\s+', line.strip())
        # Only process covered source files and ignore files with 0% coverage
        if len(tmpStrList) == 5:
          fileName = tmpStrList[0]
          coveredBranches = tmpStrList[4].strip().split(",")
          for branch in coveredBranches:
            bSet.add(fileName + ":" + branch)
      fuzzer_cov_dict[reportFileName] = bSet
      f.close()
    else:
        continue
  
  hash_dict = dict()
  for key in fuzzer_cov_dict:
    fout = open(key + ".hash",'w')
    hSet = Set([])
    for data in fuzzer_cov_dict[key]:
      hSet.add(hash(data))
      fout.write(str(hash(data)) + '\n')
    fout.close()
    hash_dict[key] = hSet

  print "Double check: #items in hash set should equal to #items in non-hash set"
  for key in hash_dict:
    print key
    print len(hash_dict[key])
    print len(fuzzer_cov_dict[key])

  return 0
# Parse the input arguments
if __name__ == '__main__':
    parser = argparse.ArgumentParser()    
    parser.add_argument('-d','--gcovr_dir',type=str,required=True,help="Full path to the folder keeping all gcovr reports (gcovr_report_*.txt)") 
    args = parser.parse_args()
    main(args.gcovr_dir)
