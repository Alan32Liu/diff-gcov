#! /usr/bin/env python3
import os
import pathlib
import sys

sys.path.insert(0,
                f"{'/'.join(str(pathlib.Path(__file__).parent.parent.absolute()).split('/')[:-1])}"
                f"/VisualiseTree")
from visualise_tree import Node as TreeNode

aflnet_dir = sys.argv[1]
legion_dir = sys.argv[2]
aflnet_report = sys.argv[3]


def collect_sequence(result_dir):
    sequences = []
    for file_name in os.listdir(result_dir):
        prefix, sequence = file_name.split(":")[:2]
        assert prefix == "id"
        sequences.append([int(state) for state in sequence.split("-") if state])
    return sequences


def collect_each_selection_stats(stats_file):
    with open(stats_file, 'r') as stats_file:
        for line in stats_file:
            if line[:len("[SELECTION]")] != "[SELECTION]":
                continue
            states = [int(state) for state in line[:-1].split(":")[-1].split(" ") if state]
            is_missing_from_log = True
            for sequence in aflnet_sequences_log:
                if states == sequence[:len(states)]:
                    is_missing_from_log = False
                    break
            if is_missing_from_log:
                print(f"Missing from log: {states}")
                AFLNet_ROOT.add_trace(trace=states)

            is_missing_from_dir = True
            for sequence in aflnet_sequences_dir:
                if states == sequence[:len(states)]:
                    is_missing_from_dir = False
                    break
            if is_missing_from_dir:
                print(f"Missing from dir: {states}")
                # AFLNet_ROOT.add_trace(trace=states)

            AFLNet_ROOT.record_selection_trace(trace=states)


def collect_each_execution_stats(stats_file):
    sequences = []
    with open(stats_file, 'r') as stats_file:
        for line in stats_file:
            if line[:len("[Execution]")] != "[Execution]":
                continue
            states = [int(state) for state in line[:-1].split(":")[-1].split(" ") if state]
            if states in sequences:
                # print(f"Sequence exits: {states}")
                continue
            AFLNet_ROOT.add_trace(trace=states)
            sequences.append(states)
    return sequences


aflnet_sequences_dir = collect_sequence(aflnet_dir)


AFLNet_ROOT: TreeNode = TreeNode(0)


aflnet_sequences_log = collect_each_execution_stats(stats_file=aflnet_report)
collect_each_selection_stats(stats_file=aflnet_report)


only_in_log_counter = 0
for sequence in aflnet_sequences_log:
    if sequence not in aflnet_sequences_dir:
        only_in_log_counter += 1
        print(f"Only in log ({only_in_log_counter}): {sequence}")

only_in_dir_counter = 0
for sequence in aflnet_sequences_dir:
    if sequence not in aflnet_sequences_log:
        only_in_dir_counter += 1
        print(f"Only in dir ({only_in_dir_counter}): {sequence}")


print(AFLNet_ROOT.tree_repr())
