#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 10:07:46 2018

@author: Eug

Zach to Marshall style data
"""
import numpy as np
import csv
import ast

input_file = 'data/parts_4-4_w35_rc.csv'
output_file = 'data/4x4_r_35.csv'
n = 4

with open(input_file,'r') as f:
    reader = csv.reader(f)
    l = list(reader)
        
partitions = [[ast.literal_eval(t) for t in a] for a  in l]

plans = []
for k in partitions:
    plan = np.ndarray((n,n))
    for l in range(len(k)):
        for i in range(len(k[l])):
            for j in range(len(k[l][i])):
                if k[l][i][j] == 1:
                    plan[i, j] = l
    plans.append(plan)
    
outfile = open(output_file, 'w')
for i in plans:
    for j in i:
        line = ''
        for k in range(len(j)):
            line += str(int(j[k]))
            if k != len(j) - 1:
                line += ','
        line += '\n'
        outfile.write(line)
outfile.close()

print(str(len(plans)))
        