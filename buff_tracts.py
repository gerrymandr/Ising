#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 11:00:14 2018

@author: hannah
"""
from qgis.utils import iface
from PyQt4.QtCore import QVariant
import numpy
import csv

# Replace the values below with values from your layer.
# For example, if your identifier field is called 'XYZ', then change the line
# below to _NAME_FIELD = 'XYZ'
LAYER_NAME = "Lowell_Tracts"
FILEPATH='/home/hannah/Desktop/Mass/'
_NAME_FIELD = 'GEOID10'
_POP_FIELDS = {'tot_pop': 'DP0080001', 'white' : 'DP0080003', 'black' : 'DP0080004', 'asian' : 'DP0080006'}
ADJ_LAYER_NAME = LAYER_NAME+"_Adj"

# choose a layer
layers = qgis.utils.iface.legendInterface().layers()
for layerQ in layers:
    if layerQ.name() == LAYER_NAME:
        layer=layerQ

#start editing layer
layer.startEditing()
if not "NEIGHBORS" in [field.name() for field in layer.pendingFields()]:
    layer.dataProvider().addAttributes([QgsField(NEIGHBORS, QVariant.String),])
    layer.updateFields()
    
## Create a dictionary of all nodes
nodes = [node for node in layer.getFeatures()]
map = {node.id(): node for node in nodes}

# Build a spatial index
index = QgsSpatialIndex()
for node in nodes():
    index.insertFeature(node)

# create a new memory layer
v_layer = QgsVectorLayer("LineString", ADJ_LAYER_NAME, "memory")
pr = v_layer.dataProvider()
for node in nodes.values():
    Feature_List.append(int(nodes[_NAME_FIELD]))
    geom = nodes.geometry()
    rad = numpy.sqrt(geom.area())/5
    start_pt = geom.centroid().asPoint()
    # Find all features that intersect the bounding box of the current feature.
    # We use spatial index to find the features intersecting the bounding box
    # of the current feature. This will narrow down the features that we need
    # to check neighboring features.
    neighbors = index.intersects(geom.buffer(rad,2).boundingBox())
    # Initalize neighbors list and sum
    edges = []
    for neighbors in neighbors:
        # Look up the feature from the dictionary
        intersecting_node = nodes[neighbors]
        intersecting_buff=intersecting_node.geometry().buffer(rad,2)

        # For our purpose we consider a feature as 'neighbor' if it touches or
        # intersects a feature. We use the 'disjoint' predicate to satisfy
        # these conditions. So if a feature is not disjoint, it is a neighbor.
        #if (f != intersecting_f and myAdj(intersecting_f.geometry(),geom)):
        if (node != intersecting_node and intersecting_buff.intersects(geom)):
            #neighbors.append(int(intersecting_f[_NAME_FIELD]))
            Feature_Edges.append([int(node[_NAME_FIELD]),int(intersecting_node[_NAME_FIELD])])
            end_pt=intersecting_node.geometry().centroid().asPoint()
            line=QgsGeometry.fromPolyline([start_pt,end_pt])
            # create a new feature
            seg = QgsFeature()
            # add the geometry to the feature, 
            seg.setGeometry(QgsGeometry.fromPolyline([start_pt, end_pt]))
            # ...it was here that you can add attributes, after having defined....
            # add the geometry to the layer
            pr.addFeatures( [ seg ] )
            # update extent of the layer (not necessary)
            v_layer.updateExtents()
#    f[_NEW_NEIGHBORS_FIELD] = ''.join(str(x) for x in neighbors)
    #Feature_NBS.append(neighbors)
    # Update the layer with new attribute values.
    layer.updateFeature(f)
layer.commitChanges()
print ('Processing complete.')

QgsMapLayerRegistry.instance().addMapLayers([v_layer])

numpy.savetxt(FILEPATH+'\\SC_Buff_List_2010.txt',Feature_List , fmt='%d')