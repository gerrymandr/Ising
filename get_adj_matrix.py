#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 11:12:54 2018

@author: hannah
"""
import networkx as nx
import pandas as pd
import pickle as serializer
#from osgeo import ogr
#import gdal
#import graphviz as pgv
G=nx.read_shp('/home/hannah/Desktop/2016 Santa Clara Blocks Buffered/SC_Blocks_Buffered_Adj.shp')
A = nx.adjacency_matrix(G)
Adj = A.todense()
file = open('adj_mat_SC', 'w')
file.write(Adj)   
file.close() 
