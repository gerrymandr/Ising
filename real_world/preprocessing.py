import configparser
import networkx as nx
import numpy as np
from make_graph import construct_graph_from_file
import geopandas as gpd
import matplotlib.pyplot as plt
import shapefile as shp

def get_data(config_file):	
	########## Inputs ##########
	# read in config file
	config = configparser.ConfigParser()
	config.read(config_file)

	# shapefile and unique ID info
	shapefile = config['shapefile']['fname']
	geoid = config['shapefile']['geoid']

	# get column names from votes and districtings to read
	cols = []
	columns = config['columns']
	for key in columns:
		cols.append(columns[key])

	# optional demographic data
	if 'demographics' in config:
		for key in config['demographics']:
			cols.append(config['demographics'][key])

	# make dual graph
	dual_graph = construct_graph_from_file(shapefile, geoid, cols)
	num_nodes = dual_graph.number_of_nodes()

	# get vote assignments and district assignments
	repvote = np.zeros((num_nodes,1))
	demvote = np.zeros((num_nodes,1))
	dists = np.zeros((num_nodes,1))

	repatt = nx.get_node_attributes(dual_graph, columns['repvote'])
	dematt = nx.get_node_attributes(dual_graph, columns['demvote'])
	distsatt = nx.get_node_attributes(dual_graph, columns['districtings'])

	# assign attributes in order of nodes to match adjacency matrix

	# get position data for drawing nodes at centroids
	df_vtd = gpd.read_file(shapefile)
	vtd_centroids = df_vtd.centroid
	vtd_x = vtd_centroids.x
	vtd_y = vtd_centroids.y

	inverse = {}
	sf = shp.Reader(shapefile)
	for i in range(len(sf.fields)):
		if sf.fields[i][0] == geoid:
			idx = i-1
			break
	records = sf.records()
	for i in range(len(records)):
		inverse[records[i][idx]] = i

	pos = {}
	count = 0 
	for node in dual_graph.nodes():
		repvote[count] = repatt[node]
		demvote[count] = dematt[node]
		dists[count] = distsatt[node]
		pos[node] = (vtd_x[inverse[node]], vtd_y[inverse[node]])
		count += 1

	node_size = [(repvote[i] + demvote[i])/500 for i in range(dual_graph.number_of_nodes())]

	return dual_graph, repvote, demvote, dists, pos, node_size

