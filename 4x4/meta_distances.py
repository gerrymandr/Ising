#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 16:53:52 2018

@author: Eug
"""

import numpy as np
import queue
import random
import math
import matplotlib.pyplot as plt

# Calculate the distance between a given point and all other point using BFS
def calc_distances(adj_list, start, num_vertices):
    # Set up lists for storing the distance to points and whether or not the
    # vertex has been seen yet
    distance = [0] * num_vertices
    visited = [False] * num_vertices
    # Initialize the queue
    q = queue.Queue(num_vertices)
    # Set up queue in its inititial state
    q.put(start)
    visited[start] = True
    # These next variables are all to keep track of how far from the start 
    # we are
    curr_distance = 0
    # By 'ring' I mean everything equidistant from the start point
    left_in_ring = 0
    in_next_ring = 0
    
    # Run a BFS
    while not q.empty():
        # Take the next vertex
        curr = q.get()
        for i in adj_list[curr]:
            if not visited[i]:
                # If its neighbors haven't been looked at yet, look at them
                q.put(i)
                visited[i] = True
                distance[i] = curr_distance + 1
                in_next_ring += 1
        # Keep track of how far away from the start
        if left_in_ring > 1:
            left_in_ring -= 1
        else:
            left_in_ring = in_next_ring
            in_next_ring = 0
            curr_distance += 1
    
    # Sanity check
    if len(distance) < 20:
        print(distance)
    return(distance)
    
# Calculate entropy between two plans
def calc_entropy(v1, v2, D, n):
    # First find how similar two plans are
    Plist = np.zeros((n, n))
    for i in range(len(D[v1])):
        Plist[int(D[v1][i]), int(D[v2][i])] += 1 / (len(D[v1]) / n)
        
    # Now find entropy
    entropy = 0
    for k in range(n):
        for l in range(n):
            if not math.isclose(Plist[k, l], 0):
                entropy += Plist[k, l] * math.log(1/Plist[k, l])
                
    return entropy
                
def calc_diameter(distances):
    curr_max = 0
    for i in distances:
        temp_max = max(i)
        if temp_max > curr_max:
            curr_max = temp_max
    return curr_max
    

        
    
    
ensemble_file = 'data/4x4_r_35.csv'
metagraph_file = 'results/meta_adj_110_from_4x4_r_35.npy'
num_districts = 4
num_nodes = 16



# Load in the input
adj = np.load(metagraph_file)
num_vertices = len(adj)
D = np.genfromtxt(ensemble_file, delimiter=",")
D = np.reshape(D, (num_vertices, num_nodes))

# Create lists of neighbors
adj_list = []
for i in adj:
    neighbors = []
    for j in range(len(i)):
        if i[j] == 1:
            neighbors.append(j)
    adj_list.append(neighbors)


# Find the distances between all points
distances = []
for i in range(num_vertices):
    distances.append(calc_distances(adj_list, i, num_vertices))
    
# Find the entropy between all vertices
entropies = np.zeros((num_vertices, num_vertices))
for i in range(len(entropies)):
    for j in range(i, len(entropies)):
        entropy = calc_entropy(i, j, D, num_districts)
        entropies[i, j] = entropy
        entropies[j, i] = entropy
 
# Find diameter
diameter = calc_diameter(distances)
print('The diameter is: ', diameter)

# Make picture
fig = plt.figure()
# Make data arrays
x_data = np.reshape(distances, num_vertices**2)
y_data = np.reshape(entropies, num_vertices**2)
# Make lables
x_label = 'Metagraph distance'
y_label = 'Entropy'
title = 'Comparisons of distances of\n' + metagraph_file
plt.xlabel(x_label)
plt.ylabel(y_label)
plt.title(title)
# Show the graph
plt.scatter(x_data, y_data)
plt.show()




'''
Aidan's Entrpy code

n = 10000
k = 4
Plist = np.zeros((n, k, k))
for i in range(n):
    A = D[random.randint(0,len(D) - 1)]
    B = D[random.randint(0,len(D) - 1)]
    for j in range(len(A)):
        Plist[i][int(A[j])][int(B[j])] += 1/(len(A)/k)
    
    entropy = 0
    for m in range(k):
        for l in range(k):
            if not math.isclose(Plist[i][m][l], 0):
                entropy += Plist[i][m][l] * math.log(1 / Plist[i][m][l])
    print('entropy of ' + str(A) + ' and ' + str(B) + ' = ' + str(entropy))
'''