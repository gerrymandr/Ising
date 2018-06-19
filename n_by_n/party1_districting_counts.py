#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
party1_districting_counts.py

Reads
    *_parties_*.csv     contains distribution of party1 in grid
    *_districtings.csv  contains districtings, one per row

outputs

    outfile.csv containing one row per districting of form

        District #, District party1 totals, District party 1 seats, Total party 1 seats

    e.g., in 18x18 with 6 districts, could be

        0,      5, 18, 27, 30, 15, 0,       0, 0, 0.5, 1, 0, 0,     1.5


"""

import math
import numpy as np
import copy
import random
from collections import Counter
import csv # used for reading initial districting and party assignments file
import pandas as pd
from matplotlib import pyplot as plt


import time #checking for runtime
start_time = time.time()

#### Used to read *_parties_*.csv file
def read_csv(csv_file, data):
    # Read values from csv_file  into table
    #  then flatten table and convert to integer values
    infile = open(csv_file, 'r')
    table = [row for row in csv.reader(infile)]
    infile.close()
    flat_list = [item for sublist in table for item in sublist]
    # may be necessary to clear out BOM if csv file exported from Excel
    flat_list[0] = flat_list[0].replace('\xef\xbb\xbf', '')
    flat_list[0] = flat_list[0].replace('\ufeff', '')
    data = list(map(int, flat_list))
    return data

if __name__ == '__main__':
    districtings_file="run5_18x18_unique_districtings.csv"
#    districtings_file="toy_districtings.csv"
#    parties_file="18x18_parties_uniform.csv"
#    parties_file="18x18_parties_striped.csv"
    parties_file="18x18_parties_clustered.csv"

    counts_outfile="run5_18x18_unique_clustered_party_counts.csv"

    # Read file containing party assignment for each district
    party_assignment=[]
    party_assignment=read_csv(parties_file,party_assignment)

    # Read through districtings_file into districtings[]
    districtings=[]
    infile = open(districtings_file, 'r')
    districtings = [row for row in csv.reader(infile)]
    infile.close()

    # Determine number of districts
    m=len(set(districtings[0]))
    district_size=18*18/6       # Can change later

    # Count party 1 seats and write out file
    outfile = open(counts_outfile,"w")
    writer=csv.writer(outfile,delimiter=',',quoting=csv.QUOTE_NONE)

    data = []

    for k in range(len(districtings)):
        party_counts=np.zeros(m,dtype=np.int)

        districting=list(map(int, districtings[k]))
        for i in range(len(districting)):
            party=party_assignment[i]
            district=districting[i]
            party_counts[district]+=party       # Adding 0 or 1 to party_counts

        party_wins=np.zeros(m,dtype=np.single)

        for i in range(m):
            if party_counts[i]>district_size/2:
                party_wins[i]+=1
            elif party_counts[i]==district_size/2:
                party_wins[i]+=0.5

        total_wins=[sum(party_wins)]
        
        data.append(total_wins[0])

        outrow=[k]+list(party_counts)+list(party_wins)+list(total_wins)

        writer.writerow(outrow)

    outfile.close()



    print("--- %s seconds ---" % (time.time() - start_time)) # Show runtime
     
#bins = np.arange(0,3) # fixed bin size

plt.xlim([min(data)-0.5, max(data)+0.5])

plt.hist(data, bins=5, alpha=0.5)
plt.title('Green Wins')
plt.xlabel('Seats')
plt.ylabel('Frequenncy')

plt.show()

    #
    #
    #
    #
    # districtings=[]
    # tmp_districting=copy.deepcopy(districting) # Not certain if this is strictly necessary
    # districtings.append(tmp_districting)
    #
    # # G3 is the subgraph of G where edges connect nodes in the same district
    # # G3 should have m connected components, one corresponding to each district
    # G3=G.copy()
    # G3_edges=list(G3.edges())
    # for edge in G3_edges:
    #     a=edge[0]
    #     b=edge[1]
    #     if districting[a]!=districting[b]:
    #         G3.remove_edge(edge[0],edge[1])
    #
    # # Keep track of district populations to determine if switch is valid
    # district_populations=sum_district_data(districting,node_total_populations)
    #
    #
    # for k in range(num_proposals):
    #     # 'districting' is the current districting plan
    #     # propose a change to the current districting
    #     # What I am doing here is choosing a random edge until I find a
    #     # conflicted edge
    #     conflicted_edge_not_found=True
    #     while(conflicted_edge_not_found):
    #         r=random.randint(0,num_G_edges-1)
    #         edge=all_edges[r]
    #         r_a=edge[0]
    #         r_b=edge[1]
    #         if(districting[r_a]!=districting[r_b]):
    #             conflicted_edge_not_found=False
    #
    #
    #     # First check if swapping r_a for r_b gets populations outside of range before checking if connected
    #     # We'll use these values later if the swap is valid
    #     new_r_b_pop=district_populations[districting[r_a]] - node_total_populations[r_a] + node_total_populations[r_b]
    #     new_r_a_pop=district_populations[districting[r_b]] - node_total_populations[r_b] + node_total_populations[r_a]
    #     if (min_district<=new_r_a_pop<=max_district) and (min_district<=new_r_b_pop<=max_district):
    #         # To swap districts, swap districting[r_a] and districting[r_b]
    #         #       Then remove all edges in G3 connected to r_a or r_b
    #         #       Then add edges for r_a or r_b to G3 based on districting
    #         swap_districts(districting,r_a,r_b)
    #         remove_all_edges(G3,r_a)
    #         remove_all_edges(G3,r_b)
    #         add_district_edges(G3,r_a,districting,G)
    #         add_district_edges(G3,r_b,districting,G)
    #
    #         # If the new districting is valid, then add it to the list of districtings and update populations
    #         # Otherwise, undo the changes to G3 and revert to previous state
    #         if(nx.number_connected_components(G3)==m):
    #             tmp_districting=copy.deepcopy(districting) # I believe this is necessary because of the way python deals with arrays
    #             districtings.append(tmp_districting)
    #             district_populations[districting[r_a]]=new_r_a_pop # Note we've already swapped districting[r_a] and districting[r_b]
    #             district_populations[districting[r_b]]=new_r_b_pop
    #         else:
    #             swap_districts(districting,r_a,r_b)
    #             remove_all_edges(G3,r_a)
    #             remove_all_edges(G3,r_b)
    #             add_district_edges(G3,r_a,districting,G)
    #             add_district_edges(G3,r_b,districting,G)
    #
    # # Run through all districts and determine which fall within final districting margin of error
    # # Not strictly necessary to build separate list, but may be useful to have for analysis later
    # num_plans=len(districtings)
    # valid_districtings=[]
    #
    # max_district=(total_population)*(1+final_district_moe)/m
    # min_district=(total_population)*(1-final_district_moe)/m
    #
    # for j in range(num_plans):
    #     districting=districtings[j]
    #
    #     # Check if district populations fall within desired bounds
    #     district_populations=sum_district_data(districting,node_total_populations)
    #
    #     districting_is_valid=True
    #     for i in range(m):
    #         if (district_populations[i]<min_district) or (district_populations[i]>max_district):
    #             districting_is_valid=False
    #
    #     if districting_is_valid==True:
    #         tmp_districting=copy.deepcopy(districting) # Not certain if this is strictly necessary
    #         valid_districtings.append(tmp_districting)
    #
    #         # Could either do analysis of valid districtings here or run through valid_districtings[] later
    #         #district_cvap=sum_district_data(districting,node_cvap)
    #         #district_group1=sum_district_data(districting,node_group1)
    #
    #
    # # Now let's check how many unique valid districtings we have
    # # because it is possible to create duplicates
    # valid_districtings=sorted(valid_districtings)
    # unique_valid_districtings=[]
    # for j in range(len(valid_districtings)-1):
    #     if valid_districtings[j]!=valid_districtings[j+1]:
    #         tmp_districting=copy.deepcopy(valid_districtings[j]) # Not certain if this is necessary
    #         unique_valid_districtings.append(tmp_districting)
    # tmp_districting=copy.deepcopy(valid_districtings[j+1]) # Not certain if this is necessary
    # unique_valid_districtings.append(tmp_districting)
    #
    # # Natural place to do analysis of unique_valid_districtings
    # # district_cvap=sum_district_data(districting,node_cvap)
    # # district_group1=sum_district_data(districting,node_group1)
    #
    # # Write all districtings to csv file
    # # First row contains the node labels
    # # Each subsequent row corresponds to a valid districting
    # outfile = open(districtings_out_file,"wb")
    # writer=csv.writer(outfile,delimiter=',',quoting=csv.QUOTE_NONE)
    # writer.writerow(node_labels)
    # for j in range(len(unique_valid_districtings)):
    #     writer.writerow(unique_valid_districtings[j])
    # outfile.close()
    #
    #
    # print "Initially found %d districtings with MOE +/- %d %%" % (num_plans, 100*district_moe)
    # print "      %d districtings with final MOE +/- %d %%" % (len(valid_districtings), 100*final_district_moe)
    # print "         %d of these were unique" % len(unique_valid_districtings)
    # print("--- %s seconds ---" % (time.time() - start_time)) # Show runtime
    #plt.show()
    #   Just for now
