import os
import sys

import pygraphviz as pg

aflnet_dir = sys.argv[1]
legion_dir = sys.argv[2]


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


def build_tree(sequences, tree_name):

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
        return (str(hash(tuple(self.sequence[:-1]))) + "," + str(self.sequence[-1])) if self.sequence else "[]"


aflnet_sequences = collect_sequence(aflnet_dir)
legion_sequences = collect_sequence(legion_dir)

build_tree(aflnet_sequences, "AFLNet_Tree")
build_tree(legion_sequences, "Legion_Tree")

# print(aflnet_sequences)
# print(legion_sequences)



