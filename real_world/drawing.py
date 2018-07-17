import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib import animation, cm
from JSAnimation import IPython_display

def draw_state(dual_graph, demvec, repvec, pos, node_size):
    value_map = []
    for i in range(dual_graph.number_of_nodes()):
        if demvec[i] == 0 and repvec[i] == 0:
            value_map.append(0.5)
        else:
            value_map.append((repvec[i]/(demvec[i] + repvec[i])))
    value_map = np.array(value_map)
    plt.figure(num=None, figsize=(6, 3), dpi=300, facecolor='w', edgecolor='k')

    nx.draw_networkx(dual_graph, pos=pos, node_size=node_size, with_labels=False, cmap=plt.get_cmap('bwr'), \
                     node_color=value_map, vmin=0, vmax=1, width=0.1)
    plt.show()

def update_func(step, dual_graph, demvec, repvec, nodes):
    # the step parameter is mandatory for matplotlib
    # Set new value for figure data
    # update node color here
	value_map = []
	for i in range(dual_graph.number_of_nodes()):
		if demvec[step][i] == 0 and repvec[step][i] == 0:
			value_map.append(0.5)
		else:
			value_map.append((repvec[step][i]/(demvec[step][i] + repvec[step][i])))
	value_map = cm.bwr(np.array(value_map).astype(float))
	nodes.set_color(value_map)
	return nodes

def ising_anim(dual_graph, demvecs, repvecs, pos, node_size):
	fig = plt.figure(num=None, figsize=(6, 3), dpi=300, facecolor='w', edgecolor='k')
	demvec = demvecs[0]
	repvec = repvecs[0]
	value_map = []
	for i in range(dual_graph.number_of_nodes()):
		if demvec[i] == 0 and repvec[i] == 0:
			value_map.append(0.5)
		else:
			value_map.append((repvec[i]/(demvec[i] + repvec[i])))
	value_map = np.array(value_map)
	nodes = nx.draw_networkx_nodes(dual_graph, pos, node_size=node_size, cmap=plt.get_cmap('bwr'), node_color=value_map, vmin=0, vmax=1, width=0.1)
    nx.draw_networkx_edges(dual_graph)
	return animation.FuncAnimation(fig, update_func, frames=range(len(demvecs)), fargs=(dual_graph, demvecs, repvecs, nodes))