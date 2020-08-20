# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 09:16:14 2020

@author: Greg.Moschonas
"""

import geopandas as gpd

def distance_matrix(source_layer: gpd.GeoDataFrame, 
                    target_layer: gpd.GeoDataFrame,
                    target_layer_attribute_name: str) -> gpd.GeoDataFrame:
    '''
    Creates a table that contains a distance matrix with distances between all 
    geometries in two geospatial layers. Unit for distances is the unit used 
    by the layers' CRS. Both layers should have the same CRS. 
    Returns the distance matrix table as a geodataframe.
    
    Parameters
    ----------
    source_layer : gpd.GeoDataFrame
        The geospatial layer whose attribute fields will be the table row names.
    target_layer : gpd.GeoDataFrame
        The gaospatial layer whose specified attribute field will be the
        table column names.
    target_layer_attribute_name : str
        The name of the target layer attribute whose field will be the table 
        column names.

    Returns
    -------
    gpd.GeoDataFrame.

    '''
    # Loop through the individual shapes in the target layer. For each shape, 
    # calculate the distance to each shape in the source layer, using the
    # geodataframe method "distance". 
    distance_matrix = source_layer.copy()
    for index, row in target_layer.iterrows():
        distance = source_layer.distance(row['geometry'])
        distance_matrix[row[target_layer_attribute_name]] = distance.copy()
    # Return the distance matrix
    return distance_matrix
        


