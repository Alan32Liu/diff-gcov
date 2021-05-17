#! /usr/bin/env python3
import os
import pathlib
import re
import sys
import pdb

sys.path.insert(0,
                f"{'/'.join(str(pathlib.Path(__file__).parent.parent.absolute()).split('/')[:-1])}"
                f"/VisualiseTree")
from visualise_tree import Node as TreeNode


def collect_aflnet_sequence_dir(result_dir):
    if not result_dir:
        return []
    sequences = []
    for file_name in os.listdir(result_dir):
        prefix, sequence = file_name.split(":")[:2]
        assert prefix == "id"
        sequences.append([int(state) for state in sequence.split("-") if state])
    return sequences


def construct_aflnet_tree():
    def record_execution():
        if line[:len("[Execution]")] != "[Execution]":
            return
        cur_execution_path = [int(state) for state in line[:-1].split(":")[-1].split(" ") if state]
        AFLNet_ROOT.record_simulation_trace(execution_trace=cur_execution_path,
                                            selection_trace=cur_selection_path)
        all_execution_path.append(cur_execution_path)

    def record_selection():
        nonlocal cur_selection_path
        if line[:len("[SELECTION]")] != "[SELECTION]":
            return
        cur_selection_path = [int(state) for state in line[:-1].split(":")[-1].split(" ") if state]
        AFLNet_ROOT.record_selection_trace(trace=cur_selection_path)

    with open(aflnet_report_file, 'r') as aflnet_stats:
        cur_selection_path = [0]    # Assuming the credit of seed inputs goes to the root
        all_execution_path = []
        for line in aflnet_stats:
            record_execution()
            record_selection()
    return all_execution_path


def compare_aflnet_dir_log(aflnet_dir, aflnet_sequences_log):
    aflnet_sequences_dir = collect_aflnet_sequence_dir(aflnet_dir)
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


def parse_legion_log(max_depth):

    def parse_tree_line(line):
        # if "000:" in line:
        #     pdb.set_trace()

        intermediate_line_matched = re.search(r".*?[a-zA-Z]:[0-9]*:\s*([|].*)\n", line)
        if intermediate_line_matched:
            # Tree deeper than needed
            if intermediate_line_matched.group(1)[max_depth*3] == "|":
                return None, False
            return intermediate_line_matched.group(1), False
        starting_line_matched = re.search(r".*?[a-zA-Z]:[0-9]*:\s*(\x1b\[1;37m 000:.*)\n", line)
        if starting_line_matched:
            return starting_line_matched.group(1), True
        return None, False

    logs = []
    with open(legion_report_file, "r") as legion_report:
        logs = legion_report.readlines()

    tree_repr = []
    while logs:
        line = logs.pop()
        tree_line, tree_root = parse_tree_line(line)
        if tree_line:
            # print(tree_line)
            tree_repr.append(tree_line)
        if tree_root:
            break

    # tree_start_index = None
    # for i in range(len(logs)-1, 0, -1):
    #     # print(logs[i])
    #     if "000:" in logs[i]:
    #         print(logs[i])
    #         pdb.set_trace()
    #     if re.search(r":\s000:\sinf", logs[i]):
    #         tree_start_index = i
    #         break
    # assert tree_start_index is not None
    #
    # tree_repr = []
    # for i in range(tree_start_index, len(logs)):
    #     tree_line = parse_line(logs[i])
    #     if tree_line:
    #         tree_repr.append(tree_line)

    return tree_repr[::-1]


def construct_legion_tree():
    def record_execution():
        if "State seq has" not in line:
            return
        cur_execution_path = [int(state) for state in line.split(":")[-1].split(",") if state]
        Legion_ROOT.record_simulation_trace(execution_trace=cur_execution_path,
                                            selection_trace=cur_selection_path)
        all_execution_path.append(cur_execution_path)

    def record_selection():
        nonlocal cur_selection_path
        if "Selection path" not in line:
            return
        cur_selection_path = [int(state) for state in line.split(":")[-1].split(",") if state]
        Legion_ROOT.record_selection_trace(trace=cur_selection_path)

    with open(legion_report_file, 'r') as legion_stats:
        cur_selection_path = [0]    # Assuming the credit of seed inputs goes to the root
        all_execution_path = []
        for line in legion_stats:
            record_execution()
            record_selection()
    return all_execution_path


if __name__ == '__main__':
    tree_depth = int(sys.argv[1])
    aflnet_report_file = sys.argv[2]
    # aflnet_dir = sys.argv[2] if len(sys.argv) > 2 else None
    legion_report_file = sys.argv[3]

    AFLNet_ROOT: TreeNode = TreeNode(0)
    aflnet_sequences_log = construct_aflnet_tree()
    AFLNet_ROOT.tree_repr(max_depth=tree_depth)

    Legion_ROOT: TreeNode = TreeNode(0)
    legion_sequences_log = construct_legion_tree()
    Legion_ROOT.tree_repr(max_depth=tree_depth)

    # print("\n".join(tree_line for tree_line in parse_legion_log(max_depth=tree_depth)))

