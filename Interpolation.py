
# coding: utf-8



import networkx as nx
import numpy as np
import random
import matplotlib.pyplot as plt 
import matplotlib.cbook as cb
from matplotlib import gridspec
import cvxpy as cp




def earthmove(G):
    #G has weights d/r
    D = dist_m(G);
    E = make_A(m, n)
    flows = linprog(d, A_ub = E, b_ub = b, bounds = None)
    return 0;

def src_weights(G):
    return 0;

def dist_bulk(G, v, sinks):
    visited, queue, distq = set(), [v], [0]
    dists = {}
    while queue:
        vertex = queue.pop(0)
        currdist = distq.pop(0)
        if vertex in sinks:
            dists[vertex] = currdist;
        if vertex not in visited:
            for n in nx.all_neighbors(G, vertex):
                if n not in visited: 
                    queue.append(n)
                    distq.append(currdist+1)
            visited.add(vertex)
    dist_final = []
    for i in sinks:
        dist_final.append(dists[i]);
    return dist_final
    #store pointers?

def dist_m(G, srcs, sinks):
    assert(nx.isConnected(G))
    dists = []
    for i in srcs:
        dists.append(dist_bulk(G, i, sinks))
    return dists;
    

def make_A(m, n):
    dimension = (2*m+2*n+m*n, m*n)
    E = np.zeros(dimension)
    for i in range(m):
        for j in range(n):
            E[i, i*n+j]=1
    for i in range(m):
        for j in range(n):
            E[m+i, i*n+j]=-1
    for i in range(n):
        for j in range(m):
            E[2*m+i, j*n+i]=1
    for i in range(n):
        for j in range(m):
            E[2*m+n+i, j*n+i]=-1
    for i in range(m*n):
        E[i+2*m+2*n,i] = -1
    return E;

#print(make_A(3,5))




def display_l(G, weights_l):
    pos = nx.spring_layout(G)
    print("start:")
    display(G, weights_l[0], pos)
    print("end:")
    display(G, weights_l[-1], pos)
    print("steps:")
    for i in range(len(weights_l)):
        display(G, weights_l[i], pos)
    return 0;

def display_l_file(G, weights_l):
    pos = nx.spring_layout(G)
    for i in range(len(weights_l)):
        save_file_display(G, weights_l[i], pos, "interpol"+str(i))
    return 0;

def display(G, weights, pos):
    plt.plot()
    norm_weights = list(w/max(weights) for w in weights)
    nx.draw(G, pos, node_color=norm_weights, width=4.0, edge_cmap=plt.cm.Blues)
    plt.show()
    
def save_file_display(G, weights, pos, filename):
    plt.plot()
    norm_weights = list(w/max(weights) for w in weights)
    nx.draw(G, pos, node_color=norm_weights, width=4.0, edge_cmap=plt.cm.Blues)
    plt.savefig(filename+".png")

"""
these are the two functions you'll need:
w0, w1 - list of initial and end weights/votes 
steps - number of interpolations you want
dists - 2d array of costs such that the cost to get from node i to j is dist[i, j]
        (this can be set to nx.floyd_warshall_numpy(G) to get shortest walk distance between all nodes)
congestion_ub_ratio - bound the maximum flow on any intermediate node by some fraction of the total population; optional argument defaulting to 1

both return a list of intermediate weights 
"""
    
def interpolate_barycenter(w0, w1, dists, steps, congestion_ub_ratio = 1):
    n = len(w1)
    cost = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            cost[i, j] = dists[i, j]**2
    
    ts = np.linspace(0, 1, num = steps)
    population_size = sum(w0)
    
    weight_steps = []
    for i in range(steps):
        T0 = cp.Variable(n,n)
        T1 = cp.Variable(n,n)
        p = cp.Variable(n,1)
        
        
        constraints = [T0 >= 0, 
                       T1 >= 0,
                       cp.sum_entries(T0, axis = 1) == w0,
                       cp.sum_entries(T1, axis = 0).T == w1,
                       cp.sum_entries(T0, axis = 0).T == p,
                       cp.sum_entries(T1, axis = 1) == p,
                       p <= population_size * congestion_ub_ratio,
                       
                      ]
        objective = cp.Minimize(
                        cp.sum_entries(
                            cp.mul_elemwise(cost, T0 * (1-ts[i]) + T1 * ts[i])))
        problem = cp.Problem(objective, constraints)
        result = problem.solve();
        weight_steps.append(p.value.flatten().tolist()[0])            
    
    
    return weight_steps

def interpolate_simple(w0, w1, steps):
    assert(len(w0) == len(w1))
    need_to_move = []
    need_to_get = []
    total_moves = 0
    for i in range(len(w0)):
        if w0[i] > w1[i]:
            need_to_move.append([i, w0[i] - w1[i]])
            total_moves += w0[i] - w1[i]
        elif w0[i] < w1[i]:
            need_to_get.append([i, w1[i] - w0[i]])
    step_size = total_moves//steps 
    #weightsteps = [w0.copy()]
    weightsteps = []
    curr_weights = w0.copy()
    for i in range(total_moves):
        if len(need_to_move) == 0:
            break;
        if i % step_size == step_size-1:
            weightsteps.append(curr_weights.copy());
        r_src = random.choice(range(len(need_to_move)))
        r_targ = random.choice(range(len(need_to_get)))
        curr_weights[need_to_move[r_src][0]] -= 1;
        curr_weights[need_to_get[r_targ][0]] += 1;
        need_to_move[r_src][1] -=1 ;
        need_to_get[r_targ][1] -=1 ;
        if need_to_move[r_src][1] == 0:
            need_to_move.pop(r_src)
        if need_to_get[r_targ][1] == 0:
            need_to_get.pop(r_targ)
    #weightsteps.append(w1.copy())
    return weightsteps;


def demo(G, steps, typ):
    dists = nx.floyd_warshall_numpy(G)

    init_weights = list(random.randint(1, 20) for i in range(len(G.nodes)))
    end_weights = init_weights.copy()
    random.shuffle(init_weights)
    
    if typ == "bary":
        inter_weights_bary = interpolate_barycenter(init_weights, end_weights, dists, steps)
        display_l(G, inter_weights_bary)
    
    if typ == "simple":
        inter_weights_simp = interpolate_simple(init_weights, end_weights, steps)
        display_l(G, inter_weights_simp)

#demo(nx.tutte_graph(), 10, "simple")

