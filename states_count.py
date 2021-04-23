import re
import sys
import pdb
import matplotlib.pyplot as plt
import numpy as np

from collections import defaultdict

states_file = sys.argv[1]

aflnet = defaultdict(int)
legion = defaultdict(int)
either = []

with open(states_file, 'r') as states_count:
    for line in states_count:
        if line == '\n':
            continue
        state, count = (int(v) for v in re.search(r".*?State ([0-9]*) selected ([0-9]*) times", line).groups())
        if line[0] == 'S':
            assert state not in aflnet
            aflnet[state] = count
        else:
            # if state in legion:
            #     print(state, legion[state])
            #     pdb.set_trace()
            assert state not in legion
            legion[state] = count
        
        either.append(state)

either.sort()

for state in either:
    print(state, aflnet[state], legion[state])

x = np.arange(len(either))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()

# p1 = ax.bar([i for i in range(len(either))], [aflnet[s] for s in either], 0.5, label='aflnet')
# p2 = ax.bar([i for i in range(len(either))], [legion[s] for s in either], 0.5, label='legion')

p1 = ax.bar(x-width/2, [aflnet[s] for s in either], width, label='aflnet')
p2 = ax.bar(x+width/2, [legion[s] for s in either], width, label='legion')

ax.axhline(0, color='grey', linewidth=0.8)
ax.set_ylabel('State Count')
ax.set_title('State count by aflnet and legion')
ax.set_xticks(x)
ax.set_xticklabels(either)
ax.legend()

# ax.bar_label(p1, label_type='center')
# ax.bar_label(p2, label_type='center')
ax.bar_label(p1, padding=3)
ax.bar_label(p2, padding=3)

fig.tight_layout()

# TODO: sum up the total number of selections of each tool
# TODO: some targets terminated in seconds, find out why
# TODO: why 150 showed up twice?

plt.show()