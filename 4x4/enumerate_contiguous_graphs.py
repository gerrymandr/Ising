#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 11:55:41 2018

@author: Eug
"""
import numpy as np
import networkx as nx

# Enumerates the set partitions with k subsets of an input list. If the length 
# of the input list is n, this should generate S(n,k) partitions, the Stirling 
# numbers of the second kind. 
# Input: a_list - a Python list
# Input: k - the number of desired subsets in the partition. Should have k >= 0. 
def k_list_partitions(a_list, k):
    # Cast in case the input is something like a dataframe instead of a list. 
    a_list = list(a_list)
    n = len(a_list)
    if k > n: 
        print("Invalid input: had k > n. Returning null partition.")
        yield [] 
    elif n < 0 or k < 0: 
        print("Invalid input: either n < 0 or k < 0. Returning null partition.")
        yield []
    # Hardcoding of edge values. 
    elif k == 0:
        if n == 0:
            yield [[]]
        else:
            yield []
    elif k == 1: 
        yield [a_list]
    elif n == k: 
        yield [[elt] for elt in a_list]
    # Uses standard recursion S(n,k) = k*S(n-1,k) + S(n-1,k-1) - first element 
    # can either be a singleton for S(n-1,k-1) partitions, or can be placed into
    # one of k other sets for k*S(n-1,k) partitions. 
    else:
        for partition in k_list_partitions(a_list[1:], k-1):
            # Put in first element as singleton set.
            partition.append([a_list[0]])
            yield partition
        for partition in k_list_partitions(a_list[1:], k):
            # Put first element into another subset. 
            for subset in partition: 
                subset.append(a_list[0])
                yield copy.deepcopy(partition) 
                subset.remove(a_list[0])

# Enumerates all possible partitions of a given graph into k subgraphs. 
# Input: G - a NetworkX graph
def k_graph_partitions(G, k): 
    vertex_partitions = k_list_partitions(nx.nodes(G), k)
    for vertex_partition in vertex_partitions:
        graph_partition = []
        for subset in vertex_partition: 
            subgraph = G.subgraph(subset)
            graph_partition.append(subgraph)
        yield graph_partition

# Enumerates all possible partitions of a given graph into k connected subgraphs.
# Input: G - a NetworkX graph 
def k_connected_graph_partitions(G, k):
    partitions = []
    for partition in k_graph_partitions(G, k):
        valid = True
        for subgraph in partition: 
            if not nx.is_connected(subgraph):
                valid = False
                break
        if not valid:
            continue
        else: 
            partitons.append(partition)
    return partitions
            
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

G = create_square_grid_graph(4, True)
partitions = k_connected_graph_partitions(G, 4)

output_file = '4x4_queen.txt'
outfile = open(output_file, 'w')
outfile.write(str(partitions))