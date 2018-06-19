#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 16:01:38 2018

@author: Eugene Henninger-Voss

18 x 18 graph check

checks to see if every 18 x 18 graph split into 6 districts has 54 members of 
each district
"""

file_to_check = "run5_18x18_unique_districtings.csv"

# Every line in the file represents one map, so split each line and sum the 
# number of members of each district, ultimately the sum in each plan of the 
# members of each district is stored in an array inside the totals array
file = open(file_to_check, 'r')
totals = [[]]*6
for line in file:
    values = line.split(',')
    values[-1] = values[-1][0]
    district_members = [0] * 6
    for i in values:
        if i == '0':
            district_members[0] += 1
        if i == '1':
            district_members[1] += 1
        if i == '2':
            district_members[2] += 1
        if i == '3':
            district_members[3] += 1
        if i == '4':
            district_members[4] += 1
        if i == '5':
            district_members[5] += 1
    for i in range(len(district_members)):
        totals[i].append(district_members[i])
        
file.close()

# Go through totals and make sure every district's members always sum to 54
fiftyfour = [True] * 6
for i in totals:
    for j in i:
        if not j == 54:
            fiftyfour[i] = False
            
print(fiftyfour)

    
        
            
