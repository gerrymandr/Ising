import numpy as np
import math
import matplotlib as mpl
import matplotlib.pyplot as plt
import copy
import random
import networkx as nx
import csv

# create n x n square grid graph
def create_square_grid_graph(n, diagonals):
    G = nx.Graph()
    for i in range(n ** 2):
        # the nodes are indexed row first (1st row is indices 0 through 9, 2nd row is indices 10 through 19, etc.)
        row = i // n # result of division is floored
        col = i % n
        # compute indices of relevant adjacent nodes and add edges
        # no need to add W, N, NE, NW because we already visited those nodes
        east  = i + 1
        south = i + n
        if row < n - 1:
            G.add_edge(i, south)
        if col < n - 1:
            G.add_edge(i, east)
        if diagonals:
            southwest = i + n - 1
            southeast = i + n + 1
            if row < n - 1 and col > 0:
                G.add_edge(i, southwest)
            if row < n - 1 and col < n - 1:
                G.add_edge(i, southeast)
    return G

# create an initial block-layout districting
def create_block_districting(block_width, block_height, num_blocks_across, num_blocks_down):
    num_vertices_across = block_width * num_blocks_across
    num_vertices_down = block_height * num_blocks_down
    num_vertices = num_vertices_across ** 2
    districting = [0] * num_vertices
    for i in range(num_vertices):
        row = i // num_vertices_down
        col = i % num_vertices_across
        block_row = row // block_height
        block_col = col // block_width
        block_index = block_row * num_blocks_across + block_col
        districting[i] = int(block_index)
    return districting

# remove all edges connected to vertex v in graph G
def remove_edges_from_vertex(G, v):
    neighbors = list(nx.all_neighbors(G, v))
    for neighbor in neighbors:
        G.remove_edge(v, neighbor)

# look at edges from vertex v in graph G_full
# and add to graph G_d those which connect v to a vertex
# in the same district, according to the district list
def connect_vertex_to_neighbors_in_district(G_d, v, districting, G_full):
    neighbors = list(nx.all_neighbors(G_full, v))
    for neighbor in neighbors:
        if districting[v] == districting[neighbor]:
            G_d.add_edge(v, neighbor)

# create subgraph of G w/ edges only between vertices in same district
def create_district_subgraph(G, districting):
    G_d = G.copy()
    G_d_edges = list(G_d.edges())
    for edge in G_d_edges:
        v1 = edge[0]
        v2 = edge[1]
        if districting[v1] != districting[v2]:
            G_d.remove_edge(v1, v2)
    return G_d

def update_district_subgraph_after_flip(G, G_d, v_flip, new_districting):
    remove_edges_from_vertex(G_d, v_flip)
    connect_vertex_to_neighbors_in_district(G_d, v_flip, new_districting, G)

# search for initial rectangular block districting
def create_seed_districting(grid_size, num_districts):
    num_blocks_across = math.ceil(math.sqrt(num_districts))
    num_blocks_down = None
    still_searching = True
    while num_blocks_across > 0 and still_searching:
        num_blocks_across -= 1
        if num_districts % num_blocks_across == 0:
            num_blocks_down = num_districts / num_blocks_across
            if grid_size % num_blocks_across == 0 and \
               grid_size % num_blocks_down == 0:
                   still_searching = False
    # ensure configuration was found
    assert num_blocks_down != None

    block_width = int(grid_size / num_blocks_across)
    block_height = int(grid_size / num_blocks_down)
    return create_block_districting(
        block_width,
        block_height,
        num_blocks_across,
        num_blocks_down
    )


def generate_district_ensemble(
    grid_size,
    num_districts,
    ensemble_size=10000,
    adjacency_type='rook',
    unique_districtings=False
):
    if adjacency_type not in ['rook', 'queen']:
        raise ValueError('invalid adjacency type')
    if (grid_size ** 2) % num_districts != 0:
        raise ValueError('grid size is not divisible by number of districts')
    num_nodes_per_district = (grid_size ** 2) / num_districts

    if adjacency_type == 'rook':
        G = create_square_grid_graph(grid_size, diagonals=False)
    elif adjacency_type == 'queen':
        G = create_square_grid_graph(grid_size, diagonals=True)
    G_edges = list(G.edges())
    num_G_edges = len(G_edges) # number of edges in the grid graph

    current_districting = create_seed_districting(grid_size, num_districts)
    districtings = [current_districting]

    # Find the initial size of each district
    district_sizes = [0] * num_districts
    for i in current_districting:
        district_sizes[int(i)] += 1

    # G_d (G_district) is the subgraph of G where edges connect nodes in the same district
    # G_d should have one connected component per district
    G_d = create_district_subgraph(G, current_districting)

    while len(districtings) < ensemble_size:
        # search for conflicting edge to swap
        still_searching = True
        while still_searching:
            r = random.randint(0, num_G_edges - 1)
            edge = G_edges[r]

            # the base vertex will remain unchanged
            # while the flip vertex will be flipped
            if random.randint(0,1) == 0:
                v_base = edge[0]
                v_flip = edge[1]
            else:
                v_base = edge[1]
                v_flip = edge[0]

            # only make flip if it won't unbalance the districting
            base_district_size = district_sizes[int(current_districting[v_base])]
            flip_district_size = district_sizes[int(current_districting[v_flip])]
            if base_district_size > num_nodes_per_district:
                continue
            if flip_district_size < num_nodes_per_district:
                continue
            if current_districting[v_base] != current_districting[v_flip]:
                still_searching = False

        # save the original district of v_flip in case the flip isn't accepted
        # flip the district of v_flip to that of v_base
        # update the district graph G_d:
        # - remove all edges connected to v_flip
        # - add edges to v_flip based on new districting
        old_district = current_districting[v_flip]
        district_sizes[int(current_districting[v_base])] += 1
        district_sizes[int(current_districting[v_flip])] -= 1
        current_districting[v_flip] = current_districting[v_base]
        update_district_subgraph_after_flip(G, G_d, v_flip, current_districting)

        # if the new districting is valid, add it to the list
        # otherwise undo the changes
        if nx.number_connected_components(G_d) == num_districts:
            districtings.append(tuple(current_districting))
        else:
            current_districting[v_flip] = old_district
            district_sizes[int(current_districting[v_flip])] += 1
            district_sizes[int(current_districting[v_base])] -= 1
            update_district_subgraph_after_flip(G, G_d, v_flip, current_districting)

    result = set(districtings) if unique_districtings else districtings
    return result

def save_csv(ensemble, file_name):
    outfile = open(file_name, 'w')
    writer = csv.writer(outfile, delimiter=',', quoting=csv.QUOTE_NONE)
    for districting in ensemble:
        writer.writerow(districting)
    outfile.close()


'''
this code is only needed if this file is run by itself

ensemble = generate_district_ensemble(
    grid_size=18,
    num_districts=6,
    ensemble_size=100000,
    adjacency_type='rook',
    unique_districtings=False
)

save_csv(ensemble, 'results/100000_18_by_18_rook_districtings.csv')
'''
