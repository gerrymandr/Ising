#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 20:15:48 2018

@author: caranix
"""

file_to_check = "test18by18.csv"
file_to_write_to = "output_matrix.csv" 

# Every line in the file represents one map, so split each line and sum the 
# number of members of each district, ultimately the sum in each plan of the 
# members of each district is stored in an array inside the totals array
file = open(file_to_check, 'r')
ofile= open(file_to_write_to, 'w')
for line in file: #list as csv
    for j in range(0,323,18):
        #print(list(range(0,343,18)))
        ofile.write( line[j: j+36] + '\n')    
ofile.close() 
file.close()
    


#range(0,343,18)
#for j in range(1,16,4)
#j, j+4 
#print ns[j-1,j+3]
    
