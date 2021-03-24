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
import pdb
from sets import Set
import copy
import random
import operator
from collections import defaultdict

def main(gcovr_dir):
    fuzzers = []
    branch_dict = dict()
    #iterate through all gcovr reports
    for reportFileName in sorted(os.listdir(gcovr_dir)):
        if reportFileName.endswith(".txt"):
            fuzzer = reportFileName.split(".")[0].split("-")[-1]
            # print fuzzer
            fuzzers.append(fuzzer)
            f = open(os.path.join(gcovr_dir, reportFileName), "r")
            for line in f:
                tmpStrList = re.split('\s+', line.strip())
                # Only process covered source files and ignore files with 0% coverage
                if len(tmpStrList) == 5:
                    fileName = tmpStrList[0]
                    coveredBranches = tmpStrList[4].strip().split(",")
                    for branch in coveredBranches:
                        # fuzzer_cov_dict = defaultdict(list)
                        assert len(branch.split("-")) == 2
                        branch_location, branch_id = branch.split("-")
                        branch_location = fileName + ":" + branch_location
                        if branch_location not in branch_dict:
                            branch_dict[branch_location] = defaultdict(list)
                        branch_dict[branch_location][fuzzer].append(int(branch_id))
            f.close()
        else:
            continue

    # print branch_dict
    # print fuzzers
    print "Branches\t\t\t" + "".join(["{:>18}".format(fuzzer) for fuzzer in fuzzers])
    branch_locations = sorted(branch_dict.keys(), key=lambda x: (x.split(":")[0], int(x.split(":")[1])))
    for branch_location in branch_locations:
        fuzzers_ids = [branch_dict[branch_location][fuzzer] for fuzzer in fuzzers]
        if all(fuzzer_ids == fuzzers_ids[0] for fuzzer_ids in fuzzers_ids):
            continue
        line = "{:<25}".format(branch_location)
        for fuzzer in fuzzers:
            ids = [str(i) for i in sorted(branch_dict[branch_location][fuzzer])]
            line += "{:>18}".format(",".join(ids) if ids else "-")
        print line

    return 0


# Parse the input arguments
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--gcovr_dir',type=str,required=True,help="Full path to the folder keeping all gcovr reports (gcovr_report-*.txt)")
    args = parser.parse_args()
    main(args.gcovr_dir)
