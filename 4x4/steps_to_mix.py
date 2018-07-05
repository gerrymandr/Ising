#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 19:01:44 2018

@author: Eug
"""
import numpy as np
import random
import matplotlib.pyplot as plt

def setup(input_file):
    # Load up the data, in this case an adjacency matrix
    adj = np.load(input_file)
        
    # Create lists of neighbors
    all_neighbors = []
    for i in adj:
        neighbors = []
        for j in range(len(i)):
            if i[j] == 1:
                neighbors.append(j)
        all_neighbors.append(neighbors)
                
        
    # Calculating this once will save us time later
    num_vertices = len(all_neighbors)
        
    # Create a list of the stationary probability of each vertex
    stationary = []
    total_edges = 0
    for i in all_neighbors:
        total_edges += len(i)
    for i in range(num_vertices):
        stationary.append(len(all_neighbors[i])/ total_edges)
    
    return (adj, num_vertices, stationary, all_neighbors)

# Make one step in the metagraph
def make_step(curr_vert, steps, visits, adj, all_neighbors):
    # Now randomly choose an adjacent vertex and say you are going there
    next_step = random.randint(0, len(all_neighbors[curr_vert]) - 1)
    new_vert = all_neighbors[curr_vert][next_step]
    visits[new_vert] += 1
    steps.append(new_vert)
    return new_vert

# Calculate the sum of how far the current probability is away from the stationary
def calc_unstationary(visits, num_vertices, stationary, steps):
    # First calculate the current probability
    time_elapsed = len(steps)
    curr_prob = []
    for i in visits:
        curr_prob.append(i / time_elapsed)
    
    # Then find how much that differs from stationary
    total_diff = 0
    for i in range(num_vertices):
        total_diff += abs(curr_prob[i] - stationary[i])
    return total_diff

def mix_well(adj, num_vertices, stationary, all_neighbors):
    # Create lists where one stores the history of the MCMC
    steps = []
    diffs = []
    
    # Create a list to store each the number of times each vertex is visited
    visits = [0] * num_vertices
    
    # Need to have a starting point and a starting difference between stationary 
    # and current probability
    curr_vert = random.randint(0, num_vertices - 1)
    
    # Keep stepping until the current probability is close the stationary
    steps.append(curr_vert)
    visits[curr_vert] += 1
    diff = calc_unstationary(visits, num_vertices, stationary, steps)
    diffs.append(diff)
    
    # Keep stepping until the current probability is close the stationary
    while diff > target_difference:
        # Keep the audience in hte loop
        if len(steps) % 100000 == 0:
            print(len(steps),' steps down!')
            if len(steps) % 1000000 == 0:
                print('The differences currently sum to ',diff)
            
        # Make a step
        curr_vert = make_step(curr_vert, steps, visits, adj, all_neighbors)
        
        # Record the current difference
        if len(steps) % diff_interval == 0:
            diff = calc_unstationary(visits, num_vertices, stationary, steps)
            diffs.append(diff)
    
    # Report the findings
    print('Steps needed to reach target difference: ', str(len(steps)))
    history = [steps, diffs]
    return history

# Exactly like mix_well but goes for a set number of steps
def mix_time(adj, num_vertices, stationary, all_neighbors):
    # Create lists where one stores the history of the MCMC
    steps = []
    diffs = []
    
    # Create a list to store each the number of times each vertex is visited
    visits = [0] * num_vertices
    
    # Need to have a starting point and a starting difference between stationary 
    # and current probability
    curr_vert = random.randint(0, num_vertices - 1)
    
    # Keep stepping for the entire time
    steps.append(curr_vert)
    visits[curr_vert] += 1
    diff = calc_unstationary(visits, num_vertices, stationary, steps)
    diffs.append(diff)
    
    # Keep stepping for the entire sentence
    while len(steps) < target_time:
        # Keep the audience in hte loop
        if len(steps) % 100000 == 0:
            print(len(steps),' steps down!')
            if len(steps) % 1000000 == 0:
                print('The differences currently sum to ',diff)
            
        # Make a step
        curr_vert = make_step(curr_vert, steps, visits, adj, all_neighbors)
        
        # Record the current difference
        if len(steps) % diff_interval == 0:
            diff = calc_unstationary(visits, num_vertices, stationary, steps)
            diffs.append(diff)
    
    # Report the findings
    print('Final difference after ', target_time, ' steps: ', diffs[-1])
    history = [steps, diffs]
    return history

# These are the constants you change 
input_file_name = 'meta_adj_111_from_4x4_q'
input_file_ending = '.npy'
input_file_folder = 'results/'
target_difference = .001
target_time = 1000000
diff_interval = 10000
output_folder = 'results/'
mix_style = 'time'

plot_title = 'Metagraph Walk'

# Conglomerate input file parts into a useable string
input_file = input_file_folder + input_file_name + input_file_ending

# Set up the needed data and then mix the metagraph
adj, num_vertices, stationary, all_neighbors = setup(input_file)
if mix_style == 'well':
    history = mix_well(adj, num_vertices, stationary, all_neighbors)
if mix_style == 'time':
    history = mix_time(adj, num_vertices, stationary, all_neighbors)

# Lets get ourselves a nice visual
plt.plot(history[1])

# Save the data for posterity
output_file = output_folder + 'mix_hist_of_' + input_file_name
#np.save(output_file, history, allow_pickle=False)



