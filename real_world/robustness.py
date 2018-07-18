
# coding: utf-8

# In[28]:


from pyemd import emd
from networkx import floyd_warshall_numpy
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import random 
import math

get_ipython().run_line_magic('matplotlib', 'inline')


# In[29]:


#In general, some things to be careful about:
#1) 0 probabilities involved in the KL divergence calculation, and the data assumptions that come along with this 
#2) Having fractional vote shares for modelling purposes when the perturbations are performed 


# In[30]:


#In this cell, we define distance metrics that are variants of KL Divergence 

#D is the vector of initial Democratic votes (absolute numbers, not percentages), represented as a 1D numpy array 
#Dp is the vector of perturbed Democratic votes, represented as a 1D numpy array 
#R is the vector of initial Republican votes, represented as a 1D numpy array
#Rp is the vector of perturbed Republican votes, represented as a 1D numpy array 


#DO DEFENSIVE PROGRAMMING AND THROW AN EXCEPTION IF ASSUMPTIONS ABOUT 0s ARE VIOLATED 

#This metric is minority-KL-divergence, which is simply the quantity KL(D,Dp) where D is the initial minority 
#distribution and Dp is the perturbed minority distribution 
def min_KL(D, Dp):
    P = np.array(D)/np.sum(D)
    Q = np.array(Dp)/np.sum(Dp)
    logpart = np.log(P[np.logical_and(P>0, Q>0)]/ Q[np.logical_and(P>0, Q>0)])
    return np.dot(P[np.logical_and(P>0, Q>0)], logpart)          

#This metric is minority-majority-KL-divergence, which is the quantity KL(D, Dp) + KL(R, Rp) where D is the
#initial minority distribution, Dp is the perturbed minority distribution, R is the initial majority distribution, 
#and Rp is the perturbed majority distribution 
def min_maj_KL(D, Dp, R, Rp):
    return minKL(D, Dp) + minKL(R, Rp)

#This metric is symmetric-minority-KL-divergence, which is the sum of KL(D, Dp)+KL(Dp,D) where D is the 
#initial minority distribution, and Dp is the perturbed minority distribution 
def sym_min_KL(D, Dp):
    return minKL(D, Dp) + minKL(Dp, D)

#This metric is symmetric-minority-majority-KL-divergence, which is the sum KL(D,Dp)+KL(Dp,D) + 
#KL(R,Rp)+KL(Rp,R) where D is the initial minority distribution, Dp is the perturbed minority distribution, 
#R is the initial majority distribution, and Rp is the perturbed majority distribution 
def sym_min_maj_KL(D, Dp, R, Rp):
    return symminKL(D, Dp) + symminKL(R, Rp)
    


# In[31]:


#In this cell, we define distance metrics that are variants of Earth-Mover's Distance 

#D is the vector of initial Democratic votes (absolute numbers, not percentages), represented as a 1D numpy array 
#Dp is the vector of perturbed Democratic votes, represented as a 1D numpy array 
#D and Dp can be thought of as histograms in the context of EMD
#R is the vector of initial Republican votes, represented as a 1D numpy array
#Rp is the vector of perturbed Republican votes, represented as a 1D numpy array 
#distance_matrix is a 2D numpy array storing the pairwise distances between histogram bins 

#This metric is minority-EMD, which is simply the quantity EMD(D,Dp,disatnce_matrix) where D is the initial minority 
#distribution and Dp is the perturbed minority distribution 
def EMD_min(D, Dp, distance_matrix):
    return emd(D, Dp, distance_matrix)

#This metric is minority-majority-EMD, which is simply the quantity EMD(D,Dp,distance_matrix)+EMD(R,Rp,distance_matrix), 
#where D is the initial minority distribution, Dp is the perturbed minority distribution, R is the initial majority 
#distribution and Rp is the perturbed majority distribution 
def EMD_min_maj(D, Dp, R, Rp, distance_matrix):
    return emd(D, Dp, distance_matrix) + emd(R, Rp, distance_matrix)


# In[32]:


#In this cell, we define the L1 distance metric...this should be normalized 

#This is a naive measure of distance that measures how much the perturbed distribution of democrats deviated from 
#the initial distribution of democrats, by summing the percent change in democratic votes over all precincts 
def L1_dist_min(D, Dp):
    return (Dp-D) / D

#This is a naive measure of distance that measures how much the perturbed distributions of democrats and republicans
#deviated from the initial distribution of democrats and republicans, by summing the percent change in democratic 
#votes over all precincts, and the percent change in republican votes over all precincts
def L1_dist_min_maj(D, Dp, R, Rp):
    return L1_dist_min(D, Dp) + L1_dist_min(R, Rp)


# In[33]:


#Conduct the pertubations 

#Perturbation type 1:
#For each precinct
#Change the proportion democrat of a vtd by a random (but small, bounded) amount 
#For theoretical purposes, not rounding 

#take in democratic vote share data, republican vote share data, total vote share data, indexed by precincts
#as 1-dimensional numpy arrays 
def perturb_min(dems, repubs, totals, minority_change_threshold):
    perturbed_dems = np.array(dems)
    perturbed_repubs = np.array(repubs)
    perturbed_totals = np.array(totals)
    
    for i in range(len(totals)):
        if totals[i]==0:
            perturbed_dems[i]=0
            perturbed_repubs[i]=0
        else:
            precinct_min_prop = dems[i]/totals[i]
            new_proportion = precinct_min_prop + random.uniform(-minority_change_threshold, minority_change_threshold)
            perturbed_dems[i] = new_proportion*perturbed_totals[i]
            perturbed_repubs[i] = perturbed_totals[i]-perturbed_dems[i]

    return np.column_stack((perturbed_dems, perturbed_repubs, perturbed_totals))

#Perturbation type 2:
#For each precinct
#Change the population of a vtd by a random (but small, bounded) amount 

#take in democratic vote share data, republican vote share data, total vote share data, indexed by precincts
#as 1-dimensional numpy arrays 
#take in population_change_threshold as a percentage; this indicates the percentage by which you allow precinct 
#population to deviate from the original 
def perturb_pop(dems, repubs, totals, population_change_threshold):
    perturbed_dems = np.array(dems)
    perturbed_repubs = np.array(repubs)
    perturbed_totals = np.array(totals)
    
    for i in range(len(totals)):
        total_precinct_pop = totals[i]
        population_change = total_precinct_pop*random.uniform(-population_change_threshold, population_change_threshold)
        perturbed_totals[i] = totals[i] + population_change 
    
    return np.column_stack((perturbed_dems, perturbed_repubs, perturbed_totals))

#Perturbation type 3: 
#For each precinct 
#Change the population of the vtd by a random (but small, bounded) amount 
#Change the proportion democrat of a vtd by a random (but small, bounded) amount 

#take in democratic vote share data, republican vote share data, and total vote share data, indexed by precincts
#as 1-dimensional numpy array 
#take in population_change_threshold as a percentage; this indicates the percentage by which you allow precinct 
#population to deviate from the original 
#take in minority_change_threshold as a percentage; this indicates the percentage by which you allow precinct 
#minority proportion to deviate from the original 
def perturb_min_and_pop(dems, repubs, totals, population_change_threshold, minority_change_threshold):
    perturbed_dems = np.array(dems)
    perturbed_repubs = np.array(repubs)
    perturbed_totals = np.array(totals)
    
    for i in range(len(totals)):
        total_precinct_pop = totals[i]
        population_change = total_precinct_pop*random.uniform(-population_change_threshold, population_change_threshold)
        perturbed_totals[i] = totals[i] + population_change 
        if perturbed_totals[i]==0:
            perturbed_dems[i]=0
            perturbed_repubs[i]=0
        else:
            precinct_min_prop = dems[i]/totals[i]
            new_proportion = precinct_min_prop + random.uniform(-minority_change_threshold, minority_change_threshold)
            perturbed_dems[i] = new_proportion*perturbed_totals[i]
            perturbed_repubs[i] = perturbed_totals[i]-perturbed_dems[i]
    
    return np.column_stack((perturbed_dems, perturbed_repubs, perturbed_totals))
        


# In[34]:


#In this cell, we construct different distance matrices of a graph, which are needed for the EMD calculation 

#takes in a networkx object graph G and returns a matrix of graph distances between pairs of vertices 
def graph_distance_matrix(G):
    return floyd_warshall_numpy(G)

#takes in a networkx object graph G and returns a matrix in which every pair of distinct vertices is assigned
#the same distance (i.e. treats the graph as a complete graph)
def teleport_distance_matrix(G):
    H = nx.complete_graph(nx.number_of_nodes(G))
    return graph_distance_matrix(H)


# In[77]:


#In this cell, we calculate seat share given vote share data and a districting plan, and statistics 
#related to seat share 

#This method calculates the number of seats that Republicans win 
#dems is a 1-dimensional numpy array of democratic votes, indexed by precincts
#repubs is a 1-dimensional numpy array of republican votes, indexed by precincts
#districts is a 1-dimensional numpy array of the district assignments, indexed by precincts 
def repubs_seat_share(dems, repubs, districtings):
    seats = 0
    for i in np.unique(districtings):
        result = np.sum(repubs[districtings == i] - dems[districtings == i])
        if result > 0:
            seats +=1.0
        elif result == 0:
            seats += 0.5
    return seats
    
#This method calculates the number of seats that Democrats win 
#dems is a 1-dimensional numpy array of democratic votes, indexed by precincts
#repubs is a 1-dimensional numpy array of republican votes, indexed by precincts
#districts is a 1-dimensional numpy array of the district assignments, indexed by precincts     
def dems_seat_share(dems, repubs, districtings):
    return repubs_seat_share(repubs, dems, districtings)
    
#This method calculates the number of toss-up seats for republicans, up to a specified epsilon 
#(seats that are won with 0.5+epsilon of the votes)
def repubs_tossup_seats(dems, repubs, districtings, epsilon):
    if epsilon > 0.5:
        raise "epsilon must be less than or equal to 0.5"
    count = 0 
    for i in np.unique(districtings):
        result = np.sum(repubs[districtings == i]) / np.sum(repubs[districtings == i] + dems[districtings == i])
        if result <= 0.5 + epsilon and result >= 0.5: 
            count += 1.0 
    return count
            
#This method calculates the number of toss-up seats for democrats, up to a specified epsilon 
#(seats that are won with 0.5+epsilon of the votes)
def dems_tossup_seats(dems, repubs, districtings, epsilon):
    return repubs_tossup_seats(repubs, dems, districtings, epsilon) 
            
#This method calculates the number of nearly guaranteed seats for republicans, up to a specified epsilon 
#(seats that are won with 1-epsilon of the votes)
def repubs_guaranteed_seats(dems, repubs, districtings, epsilon):
    if epsilon > 0.5:
        raise "epsilon must be less than or equal to 0.5"
    count = 0 
    for i in np.unique(districtings):
        result = np.sum(repubs[districtings == i]) / np.sum(repubs[districtings == i] + dems[districtings == i])
        if result >= 1 - epsilon:
            count += 1.0 
    return count 

#This method calculates the number of nearly guaranteed seats for democrats, up to a specified epsilon 
#(seats that are won with 1-epsilon of the votes)
def dems_guaranteed_seats(dems, repubs, districtings, epsilon):
    return repubs_guaranteed_seats(repubs, dems, districtings, epsilon)



