# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 16:19:51 2020

@author: Greg.Moschonas
"""

from typing import List
import re

def convert_dms_string_to_dd_float(lon: str , lat: str) -> List[float]:
    ''' 
    Parameters
    ----------
    lon : str
        The longitude
    
    lat : str
        The latitude
        
    Returns
    -------
    List[float]
        The coordinates in decimal degrees format as floats in a list 
        [lon, lat]
        
    Note
    As long as the coordinate parts are in the right order (D M S) in the 
    strings, the algorithm can handle several different formats and 
    idiosyncracies. See examples. 
    
    Examples
    >>> convert_dms_string_to_dd_float("122° 36' 52.5\\" W", "32° 18' 23.1\\" N")
    [-122.61458333333333, 32.306416666666664]
    
    >>> convert_dms_string_to_dd_float("122°36'52.5\\"W", "32°18'23.1\\"N")
    [-122.61458333333333, 32.306416666666664]
    
    >>> convert_dms_string_to_dd_float("122 36 52.5 W", "32 18 23.1 N")
    [-122.61458333333333, 32.306416666666664]
    
    >>> convert_dms_string_to_dd_float("-122 36 52.5", "32 18 23.1")
    [-122.61458333333333, 32.306416666666664]
    
    >>> convert_dms_string_to_dd_float("122° 36.875' W", "32° 18.385' N")
    [-122.61458333333333, 32.306416666666664]
    
    >>> convert_dms_string_to_dd_float("122°36.875'W", "32°18.385'N")
    [-122.61458333333333, 32.306416666666664]
    
    >>> convert_dms_string_to_dd_float("122 36.875 W", "32 18.385 N")
    [-122.61458333333333, 32.306416666666664]   
    
    >>> convert_dms_string_to_dd_float("-122 36.875", "32 18.385")
    [-122.61458333333333, 32.306416666666664]
    
    >>> convert_dms_string_to_dd_float("122.61458° W", "32.30642° N")
    [-122.61458, 32.30642]
    
    >>> convert_dms_string_to_dd_float("122.61458W", "32.30642N")
    [-122.61458, 32.30642]
    
    >>> convert_dms_string_to_dd_float("-122.61458", "32.30642")
    [-122.61458, 32.30642]
    
    >>> convert_dms_string_to_dd_float("122°.18'W", "32°18.'N")
    [-122.003, 32.3]
    
    >>> convert_dms_string_to_dd_float("122°.18'W", "32°18.'.18\\"N")
    [-122.003, 32.30005]
    
    >>> convert_dms_string_to_dd_float("- 122degrees 0.18mins ", "32 deg18.min .18 seconds north")
    [-122.003, 32.30005]
    
    >>> convert_dms_string_to_dd_float("122degrees west 0.18mins ", "32 deg18.min .18 seconds north")
    [-122.003, 32.30005]
    '''
    # find the degrees and minutes part of the coordinates
    # re explanation
    # two options: 
    # 1.number {one or more times}, followed by dot {zero or one times},
    # followed by number {zero or more times}
    # 2.dot followed by number {one or more times}
    dms_lat = re.findall("\d+\.?\d*|\.\d+", lat)
    dms_lon = re.findall("\d+\.?\d*|\.\d+", lon)

    # find the sign of the coordinates

    if re.search("^\+|North|north|[^a-zA-Z]N$|[^a-zA-Z]n$", lat.strip()):
        sign_lat = '+'
    elif re.search("^\-|South|south|[^a-zA-Z]S$|[^a-zA-Z]s$", lat.strip()):
        sign_lat = '-'
    else:
        sign_lat = '+'
    
    if re.search("^\+|East|east|[^a-zA-Z]E$|[^a-zA-Z]e$", lon.strip()):
        sign_lon = '+'
    elif re.search("^\-|West|west|[^a-zA-Z]W$|[^a-zA-Z]w$", lon.strip()):
        sign_lon = '-'
    else:
        sign_lon = '+'

    # convert degrees and minutes to floats, divide minutes by 60, add
    # to degree and then apply appropriate sign
    d_lat = float(dms_lat[0])
    if len(dms_lat) > 1:
        m_lat = float(dms_lat[1])
    else:
        m_lat = 0
    if len(dms_lat) > 2:
        s_lat = float(dms_lat[2])
    else:
        s_lat = 0  
        
    d_lon = float(dms_lon[0])
    if len(dms_lon) > 1:
        m_lon = float(dms_lon[1])
    else:
        m_lon = 0
    if len(dms_lon) > 2:
        s_lon = float(dms_lon[2])
    else:
        s_lon = 0
        
    if sign_lat == '-':
        dd_lat = -1 * (d_lat + m_lat / 60 + s_lat / 3600)
    elif sign_lat == '+':
        dd_lat = +1 * (d_lat + m_lat / 60 + s_lat / 3600)
        
    if sign_lon == '-':
        dd_lon = -1 * (d_lon + m_lon / 60 + s_lon / 3600)
    elif sign_lon == '+':
        dd_lon = +1 * (d_lon + m_lon / 60 + s_lon / 3600)
    # return the pair of coordinates
    return [dd_lon, dd_lat]