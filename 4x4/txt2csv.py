#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 10:39:30 2018

@author: Eug
"""

import ast
import numpy as np

enumeration_file = '4x4partitions.txt'
output_file = '4x4partitions.csv'

infile = open(enumeration_file, 'r')
raw_enum = infile.read()
ast_enum = ast.literal_eval(raw_enum)
infile.close()

all_plans = []
for i in range(len(ast_enum)):
    all_plans.append(np.ndarray((4, 4)))

for k in range(len(ast_enum)):
    for l in range(len(ast_enum[k])):
        for m in ast_enum[k][l]:
            all_plans[k][m] = l
     
outfile = open(output_file, 'w')
for i in all_plans:
    for j in i:
        line = ''
        for k in range(len(j)):
            line += str(int(j[k]))
            if k != len(j) - 1:
                line += ','
        line += '\n'
        outfile.write(line)
outfile.close()