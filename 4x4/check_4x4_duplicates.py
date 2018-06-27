#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 19:03:33 2018

@author: Eug
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# Comparing two plans to see if they are equivalent
def are_equal(A, B):
    
    #Count how many discrepancies there are between the two plans
    num_diff = []
    for i in range(4):
        for j in range(4):
            if A[i, j] != B[i, j]:
                num_diff.append((i, j))
    
    # If no discrepancies then they are equal.  Otherwise they are not
    if len(num_diff) == 0:
        return True
    else:
        return False
 
# Read in enumeration of district plans
D = np.genfromtxt("ising_enumeration_complete.csv", delimiter=",")
D = np.reshape(D, (117,4,4))

# Create basis of equivalency adjacency graph
equivalents = np.ndarray((len(D), len(D)))

# Set all values to the default of 0
for k in range(len(D)):
    for l in range(len(D)):
        equivalents[k, l] = 0

# Check every plan against every other.  If they are equal add edges to
# equivalences adjacency graph
duplicates = []
for k in range(len(D)):
    for l in range(k + 1, len(D)):
        equivalent = are_equal(D[k], D[l])
        if equivalent:
            duplicates.append((k, l))
            equivalents[k, l] = 1
            equivalents[l, k] = 1

# A sanity check, count the number of edges in the graph
num_equal = 0
for k in range(117):
    for l in range(117):
        num_equal += equivalents[k, l]
print(num_equal)
print(duplicates)


