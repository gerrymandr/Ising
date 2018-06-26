#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 11:25:20 2018

@author: Eug
"""

import argparse
import pickle
import time
import numpy as np

from districting_ensemble_generator import generate_district_ensemble as gen_dists
from ising_simulation import generate_voter_configurations_with_energies as gen_configs


# define the parser object
parser = argparse.ArgumentParser(description="Grid ising and districting model")
parser.add_argument('-g', '--grid_size', default=18, type=int,
    help='Side length of the grid.  It will be a g x g grid (default: %(default)s)'
 )
parser.add_argument('-d', '--num_districts', default=6, type=int,
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
parser.add_argument('--dist_infile', type=str,
    help='''name of file where desired districtings are stored\n
    must be a pickled list of districts, each represented as a list of ints\n
    (default: generates new districts)''',
)
parser.add_argument('--dist_outfile', type=str,
    help='''name of file where the district plans created are stored \n
    (default: "data/distrs_" + time stamp))'''
)

# args = vars(parser.parse_args())

# test code
args = vars(parser.parse_args('-g 18 -d 6 -m .9'.split(' ')))
print(args)

# unpack necessary arguements from args
grid_size = args['grid_size']
num_districts = args['num_districts']
ensemble_size = args['ensemble_size']
minority_proportion = args['minority_proportion']
ising_iterations = args['ising_iterations']
queen_adjacency = args['queen_adjacency']

if queen_adjacency:
    adjacency_type = 'queen'
else: 
    adjacency_type = 'rook'

# Try reading in dist_infile and check that it is of the right format
if 'dist_infile' in args:
    try:
        infile = open(args['dist_infile'], 'r')
        ensemble = pickle.load(infile)
        infile.close()
    except FileNotFoundError:
        raise FileNotFoundError('dist_infile not found')
    except TypeError:
        raise TypeError('dist_file must be a pickled object')
    try:
        int(ensembel[0][0])
    except ValueError:
        raise ValueError('Wrong data format: dist_infile')
    except TypeError:
        raise TypeError('Wrong data format: dist_infile')
    for plan in ensemble:
        if len(plan) != grid_size * grid_size:
            raise ValueError('"districts" in dist_infile not grid_size^2 long')
 
# If not reading in districts from a file need to create new ones       
else:
    ensemble = gen_dists(
        grid_size,
        num_districts,
        ensemble_size=10,
        adjacency_type='rook',
        unique_districtings=False
    )
    
    # save the districts created so they can easily be used later without needing 
    # to recalculate all of them
    if 'dist_outfile' in args:
        file_name = args['dist_outfile']
    else:
        file_name = 'data/dists_' + str(time.time)
    dist_save_file = open(file_name, 'w')
    pickle.dump(ensemble, dist_save_file)
    dist_save_file.close()


configs_and_engergies = gen_configs(
    grid_size, 
    minority_proportion,
    energy_type='normalized-gamma',
    energy_range=np.linspace(0, 1, num=20),
    temperature=0.25,
    num_initial_iterations=1000,
    num_samples_per_energy=40,
    iterations_between_samples=100
 )