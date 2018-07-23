# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 19:49:47 2018

@author: Sloan
"""
import matplotlib.pyplot as plt
import numpy as np
import pickle
from scipy import stats

grid_size = 20
num_vertices = grid_size ** 2
num_districts = 4
ensemble = pickle.load(open('20x20 into 4 ensemble.p', 'rb'))
ensemble = ensemble[0::800]
ensemble2 = []
for plan in ensemble:
    plan = np.array(plan).reshape((grid_size, grid_size))
    ensemble2.append(plan.flatten()) # original plan
    ensemble2.append(np.rot90(plan, 1).flatten()) # rot 90
    ensemble2.append(np.rot90(plan, 2).flatten()) # rot 180
    ensemble2.append(np.rot90(plan, 3).flatten())
ensemble = ensemble2

num_city_vertices = int(num_vertices * 0.2)
num_rural_vertices = num_vertices - num_city_vertices

city_mask = np.zeros((grid_size, grid_size))
(I, J) = np.mgrid[0:grid_size,0:grid_size]

fig = plt.figure()
city_mask_ax = fig.add_subplot(211)
img = city_mask_ax.imshow(city_mask, extent=[0, grid_size, 0, grid_size])
city_mask_ax.xaxis.set_visible(False)
city_mask_ax.yaxis.set_visible(False)
seats_vs_p_ax = fig.add_subplot(212)

def get_dem_seat_share(config, plan):
    num_districts = int(max(plan)) + 1
    seats = 0
    for d in range(num_districts):
        dem_count = np.sum(config[plan == d])
        vertex_count = np.sum(plan == d)
        if dem_count > vertex_count * 0.5:
            seats += 1
        # add half a seat in the case of a tie
        elif dem_count == vertex_count * 0.5:
            seats += 0.5
    return seats

def get_expected_dem_seat_share(config):
    seats = 0
    for plan in ensemble:
        seats += get_dem_seat_share(config, np.array(plan))
    seats /= len(ensemble)
    return seats

def onclick(event):
    global city
    if event.inaxes and event.inaxes == city_mask_ax:
        x = event.xdata
        y = event.ydata
        j = int(x)
        i = grid_size - 1 - int(y)
        dI2 = np.power(I - i, 2)
        dJ2 = np.power(J - j, 2)
        d = dI2 + dJ2
        near_indices = np.argsort(d, axis=None)
        unraveled_near_indices = np.unravel_index(near_indices, d.shape)
        city_i, city_j = unraveled_near_indices[0:num_city_vertices]
        city_mask = np.zeros((grid_size, grid_size))
        for a in range(num_city_vertices):
            city_mask[city_i[a], city_j[a]] = 1

        plt.pause(0.05)
        
        p_city_list = []
        configs = []
        for t in np.arange(-0.1, 0.9, 0.02):
            p_city = 0.9 - t # dem city proportion
            p_rural = 0.4 + 0.25 * t # dem rural proportion
            
            #city = np.ones(num_city_vertices) * p_city
            #rural = np.ones(num_rural_vertices) * p_rural
            
            city = np.zeros(num_city_vertices)
            city[0:int(p_city * num_city_vertices)] = 1
            rural = np.zeros(num_rural_vertices)
            rural[0:int(p_rural * num_rural_vertices)] = 1
            np.random.shuffle(city)
            np.random.shuffle(rural)
            
            config = np.zeros(num_vertices)
            city_indices = near_indices[0:num_city_vertices]
            rural_indices = near_indices[num_city_vertices:]
            for c in range(num_city_vertices):
                config[city_indices[c]] = city[c]
            for r in range(num_rural_vertices):
                config[rural_indices[r]] = rural[r]
            configs.append(config)
            p_city_list.append(p_city)
        seats_list = []
        for config in configs:
            seats_list.append(get_expected_dem_seat_share(config))
        seats_vs_p_ax.clear()
        seats_vs_p_ax.scatter(p_city_list, seats_list)
        seats_vs_p_ax.set_ylim([1.5, 2.5])
        plt.draw()
        plt.pause(0.05)
        city_mask = configs[0].reshape((grid_size, grid_size))
        city_mask_ax.imshow(city_mask, extent=[0, grid_size, 0, grid_size])
        plt.draw()
        plt.pause(0.05)
        slope, intercept, r_value, p_value, std_err = stats.linregress(p_city_list, seats_list)
        print(slope)
cid = fig.canvas.mpl_connect('button_press_event', onclick)

plt.show()

