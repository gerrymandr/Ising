#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 11:25:20 2018

@author: Eug
"""

import argparse

parser = argparse.ArguementParser(description="Grid ising and districting model")
parser.add_arguement('-g', '--grid_size', default=18, type=int,
    help='Side length of the grid.  It will be a g x g grid (default: %(default)s)'
 )
parser.add_arguement('-d', '--num_districts', default=6, type=int,
    help='Number of districts (default: %(default)s)'
)
parser.add_argument('-e', '--ensemble_size', default=10000, type=int,
    help='Number of districting plans to create and test (default: %(default)s)'
)
parser.add_argument('-m', '--minority_proportion', default=.4, type=float,
    help='Decimal share of the total population that is minority (default: %(default)s)'
)
parser.add_argument('-i', '--ising_iterations', default=10000, type=int,
    help='Number of steps to run in the icing model for each temperature (default: %(default)s)'
)
parser.add_argument('-q', '--queen_adjacency', action='store_const', 
    const=True, default=False, 
    help="Choose to use queen adjacency over rook (default: %(default)s)"
)

args = vars(parser.parse_args())