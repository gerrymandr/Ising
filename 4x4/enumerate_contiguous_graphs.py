#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 11:55:41 2018

@author: Eug
"""
import numpy as np
import networkx as nx

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
