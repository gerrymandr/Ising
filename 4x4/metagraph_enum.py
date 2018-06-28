'''
Eug
VRDI 
Jun 25, 2018
'''

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import copy

# Creates a graph showing who is neighbors with who in the grid
def create_neighbors_grid_graph(n, queen):
    # First, create the grid graph
    G = nx.grid_graph([n,n])
    
    # By default grid_graphs are rook contiguous. If want a queen graph, add
    # the appropriate edges
    if queen:
        for k in G.nodes():
            i = k[0]
            j = k[1]
            
            if i < (n - 1):
                # If can, add southeast edge
                if j < (n - 1):
                    G.add_edge((i, j), (i + 1, j + 1))
                # If can, add southwest edge
                if j > 0:
                    G.add_edge((i, j), (i + 1, j - 1))   
    return G

# Comparing two plans to see if they are neighbors
def compare(A, B):
    # Must compare A against all permutations of labelings of B
    for p in perms:
        # Create a copy of B and permute the labeling
        B_curr = copy.deepcopy(B)
        for i in range(n):
            for j in range(n):
                # Sorry for the messy notation but ising_enumeration labels
                # 1, 2, 3, 4 and perms_of_4.csv uses 0, 1, 2, 3
                B_curr[i, j] = p[int(B[i, j])]
                
        #Count how many discrepancies there are between the two plans
        num_diff = []
        for i in range(n):
            for j in range(n):
                if A[i, j] != B_curr[i, j]:
                    num_diff.append((i, j))
        
        if swap:
            # If more than two differences, would need more than one swap.
            # If less than two differences, not enough change for one swap.
            if len(num_diff) != 2:
                continue
        else:
            # If not swap must be a flip, so can only have one difference
            if len(num_diff) == 1:
                return True
            else: 
                continue

        # Verify the changes represent a swap
        p1 = num_diff[0]
        p2 = num_diff[1]
    
        # Only need to find one labeling that shows they are neighbors
        if A[p1] == B_curr[p2] and A[p2] == B_curr[p1]:
            if allow_teleport:
                return True
            else:
                if p2 in under_G.has_edge(p1, p2):
                    return  True

        
    # Only if all labelings fail do we know that they are not neighbors
    return False

dist_file_name = '4x4_r_35'
dist_file_ending = '.csv'
dist_file_folder = 'data/'
perms_file = 'perms_of_4.csv'
allow_teleport = True
swap = True
queen = False
n = 4
num_perms = 24
num_districts = 1953
plot_title = '4 x 4 metagraph'
out_folder = 'results/'

# Read in enumeration of district plans
districts_file = dist_file_folder + dist_file_name + dist_file_ending
D = np.genfromtxt(districts_file, delimiter=",")
D = np.reshape(D, (num_districts,n,n))

# Read in all possible permutation of 0, 1, 2, 3
perms = np.genfromtxt(perms_file, delimiter=',')
perms = np.reshape(perms, (num_perms, n))

# Create the underlying graph of neighbors
under_G = create_neighbors_grid_graph(n, queen)

# Create basis of meta adjacency graph
meta_adjacency = np.ndarray((len(D), len(D)))

# Set all values to the default of 0
for k in range(len(D)):
    for l in range(len(D)):
        meta_adjacency[k, l] = 0

# Check every plan against every other.  If they are neighbors add edges to
# meta adjacency graph
total_comparisons = 0
for k in range(len(D)):
    for l in range(k, len(D)):
        neighbors = compare(D[k], D[l])
        total_comparisons += 1
        if total_comparisons % 100000 == 0:
            print('Finished another 10,000 comparisons')
        if neighbors:
            meta_adjacency[k, l] = 1
            meta_adjacency[l, k] = 1

# A sanity check, count the number of edges in the graph
num_edges = 0
for k in range(num_districts):
    for l in range(num_districts):
        num_edges += meta_adjacency[k, l]
print('number of edges: ' + str(num_edges))

# Make pretty picture
G = nx.from_numpy_matrix(meta_adjacency)
plt.title(plot_title)
nx.draw(G, node_size=5)
print('Connected? ' + str(nx.is_connected(G)))
print('Number of connected components = ' + str(nx.number_connected_components(G)))

# Time to save all of our hard work
# First make the name of the file. The adjacency graph is dependent on the 
# order the districts were read in. Also want to encode decisions made.

settings = str(int(allow_teleport)) + str(int(swap)) + str(int(queen))
output_file = out_folder + 'meta_adj_' + settings + '_from_' + dist_file_name
np.save(output_file, meta_adjacency, allow_pickle=False)
