#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 14:42:31 2018

@author: Eug
"""

import numpy as np
import math
import matplotlib as mpl
import matplotlib.pyplot as plt
import copy
import random
import networkx as nx

# create n x n board with n^2*p nodes assigned -1 and the rest 1
def gen_board(n, p):
    B = np.ones(n*n)
    B[1:math.floor(n*n*p)] = -1
    np.random.shuffle(B)
    B = B.reshape((n,n))
    return B

def draw_board(B):
    cmap = mpl.colors.ListedColormap(['white', 'black'])
    plt.imshow(B, cmap=cmap, interpolation='none') 
    
def bond_energy(x, B, n):
    i = x[0]
    j = x[1]
    up    = B[i-1, j] if (i > 0) else 0
    down  = B[i+1, j] if (i < n-1) else 0
    left  = B[i, j-1] if (j > 0) else 0
    right = B[i, j+1] if (j < n-1) else 0
    sum_of_neighbors = up + down + left + right
    return -B[i,j] * sum_of_neighbors

def total_energy(B, n):
    E = 0
    for i in range(n):
        for j in range(n):
            E += bond_energy((i,j), B, n)/2
    return E

def energy_diff_from_swap(x, y, B, n):
    return -2 * (bond_energy(x, B, n) + bond_energy(y, B, n))

def are_adjacent(x, y, n):
    i1 = x[0]
    i2 = y[0]
    i_diff1 = abs(i1 - i2)
    i_diff2 = n - i_diff1
    i_diff = min(i_diff1, i_diff2)
    
    j1 = x[1]
    j2 = y[1]
    j_diff1 = abs(j1 - j2)
    j_diff2 = n - j_diff1
    j_diff = min(j_diff1, j_diff2)
    
    return (i_diff == 0 and j_diff == 1) or (i_diff == 1 and j_diff == 0)

def swap(x, y, B):
    temp = B[x[0], x[1]]
    B[x[0], x[1]] = B[y[0], y[1]]
    B[y[0], y[1]] = temp

def metropolis_update(B, n, t):
    global E
    x = np.random.choice(n, 2)
    y = np.random.choice(n, 2)
    if (B[x[0], x[1]] == B[y[0], y[1]]) or are_adjacent(x, y, n): # retry if two positions have same spin or are adjacent
        return metropolis_update(B, n, t)
    dE = energy_diff_from_swap(x, y, B, n)
    if dE <= 0 or (np.random.rand() < math.exp(-dE / t)):
        swap(x, y, B)
        E += dE
        E_history.append(E)
        
def evenly_sample():
    
    # Make the board B really clumped
    E_history = []
    global E
    t = 0
    B = gen_board(n, p)
    E = total_energy(B, n)
    for j in range(10000):
        metropolis_update(B, n, t)
        
    # Unclump the board, sampling along the way
    # Set the temperature high to ensure energy keeps moving up
    t = 10 
    
    # Calculate how many sample distribution to take
    e_min = E
    e_max = 0
    e_period = 16
    num_e_bins = math.floor( - e_min / e_period)
    
    filled = [False] * num_e_bins 
    configs = [None] * num_e_bins
    energies = [None] * num_e_bins
    for j in range(1000000):
        metropolis_update(B, n, t)
        curr_e_bin = math.floor(- E / e_period)
        if not filled[curr_e_bin - 1]:
            configs[curr_e_bin - 1] = copy.deepcopy(B)
            energies[curr_e_bin - 1] = E
            filled[curr_e_bin -1]
    
    plt.plot(energies)
    
n = 18 # board size
p = 0.25 # proportion of states which are spin up
energies = []
configs = []
E = None

evenly_sample()

B = gen_board(m, p)
