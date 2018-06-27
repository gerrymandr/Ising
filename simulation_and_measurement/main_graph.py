# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 14:17:36 2018

@author: Sloan
"""
from districting_ensemble_generator_graph import generate_district_ensemble
from ising_simulation_graph import generate_voter_configurations_with_energies
import numpy as np
import networkx as nx
import pickle
from seat_shares_graph import get_expected_minority_seat_shares
from animations import generate_energy_seats_curve_animation, \
                       generate_votes_seats_curve_animation

graph = nx.grid_graph([18,18])
'''
uncomment to recreate ensemble

ensemble = generate_district_ensemble(graph=graph,
                                      num_districts=6,
                                      ensemble_size=100000,
                                      unique_districtings=False,
                                      verbose=True)
pickle.dump(ensemble, open('ensemble.p', 'wb'))
'''


# load ensemble from storage and sample sparsely to improve speed
ensemble = pickle.load(open('ensemble.p', 'rb'))
ensemble = ensemble[0::200]


'''
uncomment to create (config, proportion, energy, seats) data points

drange=[0,1]
points = []
for p in np.arange(0.02, 0.51, 0.01):
    print('Creating configurations and calculating energies for p = %0.2f' % p)
    (configs, energies) = generate_voter_configurations_with_energies(
        graph=graph,
        minority_proportion=p,
        energy_type='normalized-gamma',
        target_energy_range=np.linspace(0, 1, 30),
        temperature=.25,
        num_samples_per_energy=20,
        num_initial_iterations=3000
    )

    seats = get_expected_minority_seat_shares(configs, ensemble)
    proportions = [p] * len(seats)
    new_points = list(zip(configs, proportions, energies, seats))
    points.extend(new_points)
pickle.dump(points, open('points.p', 'wb'))
'''

load (config, proportion, energy, seats) data points from storage
points = pickle.load(open('points.p', 'rb'))

# create energy-seats curve animation and save to mp4
energy_seats_anim = generate_energy_seats_curve_animation(data=points,
                                                          num_districts=6,
                                                          energy_limits=drange,
                                                          expected_seats_limits=[0, 4],
                                                          duration=10.0,
                                                          outfile=None)
# create votes-seats curve animation and save to mp4
votes_seats_anim = generate_votes_seats_curve_animation(data=points,
                                                        num_districts=6,
                                                        minority_proportion_limits=[0, 0.5],
                                                        expected_seats_limits=[0, 3.5],
                                                        energy_limits=drange,
                                                        energy_cross_section_width=0.05,
                                                        num_frames=100,
                                                        duration=5.0,
                                                        outfile=None)