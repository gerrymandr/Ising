#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 29 11:56:03 2018

@author: Eug
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 19:01:44 2018

@author: Eug
"""
import numpy as np
import random
import matplotlib.pyplot as plt
import math


# Create minority distribution
# Taken from Sloan's code
def gen_board(n, p):
    B = np.ones(n*n)
    B[1:math.floor(n*n*p)] = -1
    np.random.shuffle(B)
    return B

# Taken from Sloan's code
def get_minority_seat_share(config, districting):
    """Get minority seat share for voter configuration wrt districting plan.

    Parameters
    ----------
    config : numpy.array (1 x num vertices)
        voter configuration from Ising simulation, -1 = minority
    districting : numpy.array(1 x num vertices)
        assignment of each vertex to a district label

    Returns
    -------
    seats : int
        # of districts in which minority voters have a majority
    """
    seats = 0
    for d in range(num_districts):
        vote_diff = np.sum(config[districting == d])
        if vote_diff < 0:
            seats += 1
        # add half a seat in the case of a tie
        elif vote_diff == 0:
            seats += 0.5
    return seats


def setup(input_file):
    # Load up the data, in this case an adjacency matrix
    adj = np.load(input_file)

    # Load the districts
    D = np.genfromtxt(dist_infile, delimiter=",")
    D = np.reshape(D, (num_plans, n ** 2))

    # Create a minority distribution to test against
    config = gen_board(n, minority_proportion)

    # Create lists of neighbors
    all_neighbors = []
    for i in adj:
        neighbors = []
        for j in range(len(i)):
            if i[j] == 1:
                neighbors.append(j)
        all_neighbors.append(neighbors)

    # Find the number of seats for each districting plan
    true_seats = []
    for i in D:
        true_seats.append(get_minority_seat_share(config, i))

    # Create a list of the stationary probability
    stationary = [0] * (num_districts * 2 + 1)
    for i in true_seats:
        stationary[int(i * 2)] += 1
    for i in range(len(stationary)):
        stationary[i] = stationary[i] / num_plans

    return (adj, config, D, stationary, all_neighbors)

# Make one step in the metagraph
def make_step(curr_vert, steps, seats, seat_freq, adj, all_neighbors):
    # Now randomly choose an adjacent vertex and say you are going there
    next_step = random.randint(0, len(all_neighbors[curr_vert]) - 1)
    new_vert = all_neighbors[curr_vert][next_step]
    steps.append(new_vert)
    return new_vert


# Calculate the sum of how far the current probability is away from the stationary
def calc_unstationary(seat_freq, stationary, steps):
    # First calculate the current probability
    time_elapsed = len(steps)
    curr_prob = []
    for i in seat_freq:
        curr_prob.append(i / time_elapsed)

    # Then find how much that differs from stationary
    total_diff = 0
    for i in range(num_districts):
        total_diff += abs(curr_prob[i] - stationary[i])
    return total_diff

def mix_well(adj, config, D, stationary, all_neighbors):
    # Create lists where one stores the history of the MCMC
    steps = []
    diffs = []
    seats = []

    # Create a list to store each the number of times each vertex is visited
    seat_freq = [0] * ((num_districts * 2) + 1)

    # Need to have a starting point and a starting difference between stationary
    # and current probability
    curr_vert = random.randint(0, num_plans - 1)

    # Get things ready for the walk
    steps.append(curr_vert)
    curr_seats = get_minority_seat_share(config, D[curr_vert])
    seats.append(curr_seats)
    seat_freq[int(curr_seats * 2)] += 1
    diff = calc_unstationary(seat_freq, stationary, steps)
    diffs.append(diff)

    # Keep stepping until the current probability is close the stationary
    while diff > target_difference:
        # Keep the audience in hte loop
        if len(steps) % 100000 == 0:
            print(len(steps),' steps down!')
            if len(steps) % 1000000 == 0:
                print('The differences currently sum to ',diff)

        # Make a step
        curr_vert = make_step(curr_vert, steps, seats, seat_freq, adj, all_neighbors)
        
        # Record the current difference
        if len(steps) % diff_interval == 0:
            diff = calc_unstationary(seat_freq, stationary, steps)
            diffs.append(diff)

    # Report the findings
    print('Steps needed to reach target difference: ', str(len(steps)))
    history = [steps, diffs]
    return history

# Exactly like mix_well but goes for a set number of steps
def mix_time(adj, config, D, stationary, all_neighbors):
    # Create lists where one stores the history of the MCMC
    steps = []
    diffs = []
    seats = []

    # Create a list to store each the number of times each vertex is visited
    seat_freq = [0] * ((num_districts * 2) + 1) 

    # Need to have a starting point and a starting difference between stationary
    # and current probability
    curr_vert = random.randint(0, num_plans - 1)

    # Get things ready for the walk
    steps.append(curr_vert)
    curr_seats = get_minority_seat_share(config, D[curr_vert])
    seats.append(curr_seats)
    seat_freq[int(curr_seats * 2)] += 1
    diff = calc_unstationary(seat_freq, stationary, steps)
    diffs.append(diff)

    # Keep stepping until the current probability is close the stationary
    while len(steps) < target_time:
        # Keep the audience in hte loop
        if len(steps) % 100000 == 0:
            print(len(steps),' steps down!')
            if len(steps) % 1000000 == 0:
                print('The differences currently sum to ',diff)

        # Make a step
        curr_vert = make_step(curr_vert, steps, seats, seat_freq, adj, all_neighbors)
        
        # Record the current difference and the seat share
        if len(steps) % diff_interval == 0:
            diff = calc_unstationary(seat_freq, stationary, steps)
            diffs.append(diff)
            
            curr_seats = get_minority_seat_share(config, D[curr_vert])
            seats.append(curr_seats)
            seat_freq[int(curr_seats * 2 )] += 1

    # Report the findings
    if mix_style == 'well':
        print('Steps needed to reach target difference: ', str(len(steps)))
    if mix_style == 'time':
        print('Total diff reached = ', str(diffs[target_time - 1]))
    history = [steps, diffs, seats]
    return history

# These are the constants you change
input_file_name = 'meta_adj_110_from_4x4partitions'
input_file_ending = '.npy'
input_file_folder = 'results/'
dist_infile = 'data/4x4partitions.csv'
num_plans = 117
n = 4
num_districts = 4
minority_proportion = .4
target_difference = .001
target_time = 10000000
diff_interval = 1
output_folder = 'results/'
mix_style = 'time'
plot_title = 'Metagraph Walk'
iteration = '14'

# Conglomerate input file parts into a useable string
input_file = input_file_folder + input_file_name + input_file_ending

# Set up the needed data and then mix the metagraph
adj, config, D, stationary, all_neighbors = setup(input_file)
if mix_style == 'well':
    history = mix_well(adj, config, D, stationary, all_neighbors)
if mix_style == 'time':
    history = mix_time(adj, config, D, stationary, all_neighbors)

# Lets get ourselves a nice visual
story = history[1]
for i in range(len(story)):
    if story[i] > 0:
        story[i] = None
    else:
        break
 
fig1 = plt.figure(1)
plt.plot(story)
plt.title('Diff at each step')
plt.show()

# Save the data for posterity
output_file = output_folder + 'mix_hist_of_' + input_file_name + iteration
np.save(output_file, history, )

output_file = output_file + '_config'
np.save(output_file, config)

'''
fig2 = plt.figure(2)
plt.plot(history[0::100000])
plt.title('Diff at every 1,000,000 steps, starting at 1,000,000')
plt.show()
'''