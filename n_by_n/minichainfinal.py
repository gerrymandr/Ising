"""
n by n toy examples with m districts where m | n^2

June 19 Revisions

You can run for different scenarios by modifying the variables
    n                   grid size is n x n
    m                   number of districts
    num_proposals       number of swaps between districts to try in building new districting
    party_file      a csv file that contains the party assignment for each cells, either 0 or 1
                        the program counts the number of seats won by party 1
    district_file   a csv file that contains the initial district assignment of each cell
    last_district_outfile       csv file that contains the last districting found


Based on code by Christy Graves
Modified by Tommy Ratliff
Combined into one module at VRDI

Code should be fairly easily generalized to work for any graph
party1_districting_counts.py

Reads
    *_parties_*.csv     contains distribution of party1 in grid
    *_districtings.csv  contains districtings, one per row

outputs

    outfile.csv containing one row per districting of form

        District #, District party1 totals, District party 1 seats, Total party 1 seats

    e.g., in 18x18 with 6 districts, could be

        0,      5, 18, 27, 30, 15, 0,       0, 0, 0.5, 1, 0, 0,     1.5
        
        Runs the same ensemble against three different distrobutions, outputs
        one histogram
        

"""

import networkx as nx
import math
import numpy as np
import copy
import random
import matplotlib.pyplot as plt # only used for the histogram at the end
import matplotlib.mlab as mlab
from collections import Counter
import csv # used for reading initial districting and party assignments files

import time #checking for runtime
start_time = time.time()

def create_graph_n_by_n(n):
    G=nx.Graph()
    for i in range(n**2):
        # compute index of my neighbor in each direction (north, northeast, etc.)
        # the nodes are indexed by row first (1st row is indices 0 through 9, 2nd row is indices 10 through 19, etc.)
        my_row=int(math.floor(i/n))
        my_column=i%n
        west=i-1
        east=i+1
        north=i-n
        south=i+n
        northwest=i-n-1
        northeast=i-n+1
        southwest=i+n-1
        southeast=i+n+1
        if(my_row>0):
            G.add_edge(i,north)
        if(my_row<(n-1)):
            G.add_edge(i,south)
        if(my_column>0):
            G.add_edge(i,west)
        if(my_column<(n-1)):
            G.add_edge(i,east)
        if(my_row>0 and my_column>0):
            G.add_edge(i,northwest)
        if(my_row>0 and my_column<(n-1)):
            G.add_edge(i,northeast)
        if(my_row<(n-1) and my_column>0):
            G.add_edge(i,southwest)
        if(my_row<(n-1) and my_column<(n-1)):
            G.add_edge(i,southeast)
    return G

#### Used to read Districting and Party Affiliation files
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

# Swap districts in district list
def swap_districts(districting1,r1,r2):
    tmp=districting1[r1]
    districting1[r1]=districting1[r2]
    districting1[r2]=tmp

# Remove all edges connected to vertex nd in graph Gr
def remove_all_edges(Gr,nd):
    list_neighbors=list(nx.all_neighbors(Gr, nd))
    for q in list_neighbors:
        Gr.remove_edge(nd,q)

# Look at all possible edges to nd in graph Gfull
# and add those to graph Gr that connect nd to another vertex
# in the same district based on labeling in districting1
def add_district_edges(Gr,nd,districting1,Gfull):
        list_neighbors=list(nx.all_neighbors(Gfull,nd))
        for q in list_neighbors:
            if(districting1[nd]==districting1[q]):
                Gr.add_edge(nd,q)

if __name__ == '__main__':
    num_proposals=100000 # number of proposal steps to try
    n=18 # length/width of grid
    m=6 # number of districts
#    party_file="18x18_parties_uniform.csv"  # csv file that contains party assignments
#    party_file="18x18_parties_striped.csv"  # csv file that contains party assignments
#    party_file="18x18_parties_clustered.csv"  # csv file that contains party assignments

    district_file="18x18_districts_rectangles.csv" # csv file that contains district assignments
    districtings_outfile="run5_18x18_all_districtings.csv" # csv file that contains the last districting found
    unique_districtings_outfile="run5_18x18_unique_districtings.csv" # csv file that contains the last districting found

    district_size=n*n / m #number of cells in each district
    G=create_graph_n_by_n(n)
    all_edges=list(G.edges())
    num_G_edges=len(all_edges) # number of edges

    districtings=[]
    districting=[]
    districting=read_csv(district_file,districting)
    tmp_districting=copy.deepcopy(districting) # Not certain if this is strictly necessary
    districtings.append(tmp_districting)

    # G3 is the subgraph of G where edges connect nodes in the same district
    # G3 should have m connected components, one corresponding to each district
    G3=G.copy()
    G3_edges=list(G3.edges())
    for edge in G3_edges:
        a=edge[0]
        b=edge[1]
        if districting[a]!=districting[b]:
            G3.remove_edge(edge[0],edge[1])

    for k in range(num_proposals):
        # 'districting' is the current districting plan
        # propose a change to the current districting
        # What I am doing here is choosing a random edge until I find a
        # conflicted edge
        conflicted_edge_not_found=True
        while(conflicted_edge_not_found):
            r=random.randint(0,num_G_edges-1)
            edge=all_edges[r]
            r_a=edge[0]
            r_b=edge[1]
            if(districting[r_a]!=districting[r_b]):
                conflicted_edge_not_found=False

        # TR modification:
        # Change the graph G3 directly rather than building from scratch each iteration
        # We want to swap districts for r_a and r_b
        #       Then remove all edges connected to r_a or r_b
        #       Then add edges to r_a or r_b based on districting
        swap_districts(districting,r_a,r_b)
        remove_all_edges(G3,r_a)
        remove_all_edges(G3,r_b)
        add_district_edges(G3,r_a,districting,G)
        add_district_edges(G3,r_b,districting,G)

        # If the new districting is valid, then add it to the list of districtings
        # Otherwise, undo the changes to G3 and revert to previous state
        if(nx.number_connected_components(G3)==m):
            tmp_districting=copy.deepcopy(districting) # I believe this is necessary because of the way python deals with arrays
            districtings.append(tmp_districting)
        else:
            swap_districts(districting,r_a,r_b)
            remove_all_edges(G3,r_a)
            remove_all_edges(G3,r_b)
            add_district_edges(G3,r_a,districting,G)
            add_district_edges(G3,r_b,districting,G)

    # Write all districtings to csv file
    outfile = open(districtings_outfile,"w")
    writer=csv.writer(outfile,delimiter=',',quoting=csv.QUOTE_NONE)
    for j in range(len(districtings)):
        writer.writerow(districtings[j])
    outfile.close()

    # Now write out unique districtings
    districtings=sorted(districtings)
    unique_districtings=[]
    for j in range(len(districtings)-1):
        if districtings[j]!=districtings[j+1]:
            tmp_districting=copy.deepcopy(districtings[j]) # Not certain if this is necessary
            unique_districtings.append(tmp_districting)
    tmp_districting=copy.deepcopy(districtings[j+1]) # Not certain if this is necessary
    unique_districtings.append(tmp_districting)

    outfile = open(unique_districtings_outfile,"w")
    writer=csv.writer(outfile,delimiter=',',quoting=csv.QUOTE_NONE)
    for j in range(len(unique_districtings)):
        writer.writerow(unique_districtings[j])
    outfile.close()

#    plt.hist(num_party1_seats) # the histogram it makes is ugly, but you get the idea
    print ("%d districtings found" %len(districtings))
    print ("%d unique districtings found" %len(unique_districtings))
    print("--- %s seconds ---" % (time.time() - start_time)) # Show runtime
    #plt.show()
    #   Just for now


    #!/usr/bin/env python2
# -*- coding: utf-8 -*-

#Now this part compares the ensemble to distrobutions of green/red voters

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
    parties_file3="18x18_parties_uniform.csv"
    parties_file2="18x18_parties_striped.csv"
    parties_file="18x18_parties_clustered.csv"

    counts_outfile="run5_18x18_unique_clustered_party_counts.csv"
    counts2_outfile= "run5_18x18_unique_striped_party_counts.csv"
    counts3_outfile = "run5_18x18_unique_uniform_party_counts.csv"


def helper_function(input_file,output_file):
    parties_file = input_file
    counts_outfile = output_file
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

    for k in range(len(districtings)):
        party_counts=np.zeros(m,dtype=np.int)

        districting= list(map(int, districtings[k]))
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

        outrow=[k]+list(party_counts)+list(party_wins)+list(total_wins)

        writer.writerow(outrow)

    outfile.close()

    print("--- %s seconds ---" % (time.time() - start_time)) # Show runtime

helper_function(parties_file,counts_outfile)
helper_function(parties_file2,counts2_outfile)
helper_function(parties_file3,counts3_outfile)



open('outputtest.txt', 'w').close()




def read_csv_stats(csv_input, name, picture_file):
    masterlist =[]
    zeroct=0
    onect=0
    halfct=0
    twoct=0
    three_halvesct=0
    newfile = open ('outputtest.txt', 'a')
    infile = open(csv_input, 'r')
    for line in infile.readlines():
        #print(line)

        col= line.split (',')
        #print(col)
        if col[13] == '0.0\n':
            zeroct=zeroct+1
            masterlist.append(0)

        if col[13] == '1.0\n':
            onect+=1
            masterlist.append(1)

        if col[13] == '0.5\n':
            halfct=halfct+1
            masterlist.append(.5)

        if col[13] == '2.0\n':
            twoct+=1
            masterlist.append(2)

        if col[13] =='1.5\n':
            three_halvesct+=1
            masterlist.append(1.5)


    newfile.write(name +"\n")
    newfile.write("Seats  won  by  Party  1" +"\n")
    newfile.write("Number of 0's: " + str(zeroct) +"\n")
    newfile.write("Number of .5's: " + str(halfct)+"\n")
    newfile.write("Number of 1's: " + str(onect)+"\n")
    newfile.write("Number of 1.5's: " + str(three_halvesct)+"\n")
    newfile.write("Number of 2's: " + str(twoct)+"\n" +"\n")
    
    newfile.close()
    infile.close()


    return masterlist




results_clustered = read_csv_stats(counts_outfile, "Clustered", "clustered.png")
#read_csv_stats('run5_18x18_unique_clustered_party_counts.csv')
results_striped = read_csv_stats(counts2_outfile,"Striped", "striped.png" )
results_uniform = read_csv_stats(counts3_outfile, "Uniform", "uniform.png")

fig = plt.figure()
x = [results_clustered, results_striped, results_uniform]
num_bins = [0,.5,1,1.5,2,2.5]
#plt.xlim([min(masterlist)-0.5, max(masterlist)+0.5])
#plt.hist(masterlist, bins=5, alpha=0.5)


#n, bins =
n, bins, pathces = plt.hist(x, num_bins)
plt.title('Green Wins')
plt.xlabel('Seats')
plt.ylabel('Frequency')
print("n = ")
print(n)
plt.show()
fig.savefig("combined_hist.png")






















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
