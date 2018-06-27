'''
Eug
VRDI 
Jun 25, 2018
'''

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# Comparing two plans to see if they are neighbors
def compare(A, B):
    # Must compare A against all permutations of labelings of B
    for p in perms:
        # Create a copy of B and permute the labeling
        B_curr = copy.deepcopy(B)
        for i in range(4):
            for j in range(4):
                # Sorry for the messy notation but ising_enumeration labels
                # 1, 2, 3, 4 and perms_of_4.csv uses 0, 1, 2, 3
                B_curr[i, j] = p[int(B[i, j]) - 1] + 1
                
        #Count how many discrepancies there are between the two plans
        num_diff = []
        for i in range(4):
            for j in range(4):
                if A[i, j] != B_curr[i, j]:
                    num_diff.append((i, j))
            
        # If more than two differences, would need more than one swap.
        # If less than two differences, not enough change for one swap.
        if len(num_diff) != 2:
            continue

        # Verify the changes represent a swap
        p1 = num_diff[0]
        p2 = num_diff[1]
    
        # Only need to find one labeling that shows they are neighbors
        if A[p1] == B_curr[p2] and A[p2] == B_curr[p1]:
            return True
        else:
            continue
        
    # Only if all labelings fail do we know that they are not neighbors
    return False
    
# Read in enumeration of district plans
D = np.genfromtxt("ising_enumeration_complete.csv", delimiter=",")
D = np.reshape(D, (117,4,4))

# Read in all possible permutation of 0, 1, 2, 3
perms = np.genfromtxt('perms_of_4.csv', delimiter=',')
perms = np.reshape(perms, (24, 4))

# Create basis of meta adjacency graph
meta_adjacency = np.ndarray((len(D), len(D)))

# Set all values to the default of 0
for k in range(len(D)):
    for l in range(len(D)):
        meta_adjacency[k, l] = 0

# Check every plan against every other.  If they are neighbors add edges to
# meta adjacency graph
for k in range(len(D)):
    for l in range(k, len(D)):
        neighbors = compare(D[k], D[l])
        if neighbors:
            meta_adjacency[k, l] = 1
            meta_adjacency[l, k] = 1

# A sanity check, count the number of edges in the graph
num_edges = 0
for k in range(117):
    for l in range(117):
        num_edges += meta_adjacency[k, l]
print(num_edges)

# Make pretty picture
G = nx.from_numpy_matrix(meta_adjacency)
plt.title('4 x 4 metagraph')
nx.draw_networkx(G, node_size=30)

