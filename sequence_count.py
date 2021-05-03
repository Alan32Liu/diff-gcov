#! /usr/bin/env python3
import os
import pathlib
import sys

import pygraphviz as pg

sys.path.insert(0, f"{pathlib.Path(__file__).parent.parent.absolute()}/VisualiseTree")
from visualise_tree import Node as TreeNode

aflnet_dir = sys.argv[1]
legion_dir = sys.argv[2]
aflnet_report = sys.argv[3]


def collect_sequence(result_dir):
    sequences = []
    for file_name in os.listdir(result_dir):
        # print(file_name)
        # prefix, sequence, suffix = file_name.split(":")
        # assert prefix == "id" and suffix == "new"
        prefix, sequence = file_name.split(":")[:2]
        assert prefix == "id"
        sequences.append([int(state) for state in sequence.split("-") if state])
    return sequences


# def collect_overall_selection_stats(stats_file):
#     with open(stats_file, 'r') as stats_file:
#         for line in stats_file:
#             if line[:5] != "State":
#                 continue
#             state, sel = [int(word) for word in line.split() if word.isdigit()]
#             assert state not in stats
#             stats[state] = sel


def collect_each_selection_stats(stats_file):
    with open(stats_file, 'r') as stats_file:
        for line in stats_file:
            if line[:len("[SELECTION]")] != "[SELECTION]":
                continue
            states = [int(state) for state in line[:-1].split(":")[-1].split(" ") if state]
            is_missing = True
            for sequence in aflnet_sequences:
                if states == sequence[:len(states)]:
                    is_missing = False
                    break
            if is_missing:
                print(f"Adding missing sequence to aflnet_sequences: {states}")
                AFLNet_ROOT.add_trace(trace=states)
            AFLNet_ROOT.record_selection_trace(trace=states)


def draw_tree(sequences, tree_name):
    def build_trace():
        for i in range(1, len(sequence)):
            print(Node(sequence[:i-1], sequence[i-1]), Node(sequence[:i], sequence[i]))
            tree.add_edge(Node(sequence[:i-1], sequence[i-1]), Node(sequence[:i], sequence[i]))

    tree = pg.AGraph(directed=True, strict=True)

    for sequence in sequences:
        build_trace()

    tree.write('{}.dot'.format(tree_name))
    tree.layout(prog='dot')


class Node:
    def __init__(self, sequence, name):
        self.sequence = sequence
        self.name = name

    def __eq__(self, other: "Node"):
        return self.sequence == other.sequence

    def __repr__(self):
        return self.name

    def __str__(self):
        # return (str(hash(tuple(self.sequence[:-1])))
        #         + ","
        #         + str(self.sequence[-1])) if self.sequence else "[]"
        return str(self.name)


aflnet_sequences = collect_sequence(aflnet_dir)
legion_sequences = collect_sequence(legion_dir)

AFLNet_ROOT: TreeNode = TreeNode(0)
Legion_ROOT: TreeNode = TreeNode(0)

# draw_tree(aflnet_sequences, "AFLNet_Tree")
# draw_tree(legion_sequences, "Legion_Tree")

for sequence in aflnet_sequences:
    AFLNet_ROOT.add_trace(trace=sequence)
    print(sequence)

collect_each_selection_stats(stats_file=aflnet_report)

# stats = {}
# collect_selection_stats(stats_file=aflnet_report)
# for state, sel in stats.items():
#     AFLNet_ROOT.update_attr_in_subtree(condition=lambda x: x.code == state,
#                                        attr_name='sel',
#                                        attr_value=sel)



print(AFLNet_ROOT.tree_repr())


# for sequence in legion_sequences:
#     Legion_ROOT.add_trace(trace=sequence)
#
# print(Legion_ROOT.tree_repr())

# print(aflnet_sequences)
# print(legion_sequences)



