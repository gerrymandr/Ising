#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 11:12:54 2018

@author(s): hannah & cara
"""
import networkx as nx
import pandas as pd
import pickle as serializer


#import pandas as pd 
#from osgeo import ogr
#import gdal
#import graphviz as pgv
G=nx.read_shp("/Users/caranix/miniconda3/envs/vrdi/vrdi_data/SC/SC_Blocks_Buffered_Adj.shp")
A = nx.adjacency_matrix(G)
df = pd.DataFrame(A.toarray())
dd = pd.DataFrame(df)
dd.to_csv("adj_matrix.csv")

