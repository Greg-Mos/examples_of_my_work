# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 08:42:15 2020

@author: Greg.Moschonas
"""
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import rasterio as rio
from rasterio.transform import Affine
import numpy as np
# import pandas as pd
# from datetime import datetime
import cartopy
import cartopy.crs as ccrs
import earthpy.spatial as es
# import earthpy.plot as ep
from typing import List
from pyproj import CRS
from pyproj import Transformer
from skimage import exposure
import urllib.request

class ModisMultispectralHdf():
    '''
    Operations for importing and plotting MODIS multispectral surface reflectance
    LPDACC products. These products can be downloaded from 
    https://earthexplorer.usgs.gov/
    
    Examples
    # read the hdf file
    >>> d = ModisMultispectralHdf.from_hdf("MOD09A1.A2020145.h17v03.006.2020154051217.hdf")

    # quasi true color image
    >>> d.quick_plot_rgb_bands(rgb_bands=['sur_refl_b01', 'sur_refl_b04', 'sur_refl_b03'])
    
    # false color image - vegetation and bare ground
    >>> d.quick_plot_rgb_bands(rgb_bands=['sur_refl_b07', 'sur_refl_b02', 'sur_refl_b01'])

    # false color image - vegetation and water
    >>> d.quick_plot_rgb_bands(rgb_bands=['sur_refl_b01', 'sur_refl_b02', 'sur_refl_b01'], str_clip=None)
    
    # false color image - vegetation, snow, water
    >>> d.quick_plot_rgb_bands(rgb_bands=['sur_refl_b03', 'sur_refl_b06', 'sur_refl_b07'])

    # cartopy plots - not quick, takes a few minutes
    >>> d.plot_rgb_bands_with_cartopy(rgb_bands=['sur_refl_b01', 'sur_refl_b04', 'sur_refl_b03'])
    >>> d.plot_rgb_bands_with_cartopy(rgb_bands=['sur_refl_b01', 'sur_refl_b04', 'sur_refl_b03'], projection=ccrs.Orthographic(-3, 55), global_axes=True)
    
    # Info on products and useful band combinations
    https://earthdata.nasa.gov/earth-observation-data/near-real-time/download-nrt-data/modis-nrt
    '''
    
    def __init__(self, data:xr.Dataset):
        '''
        Parameters
        ----------
        data : xr.Dataset
            an xarray dataset with nasa oceandata chlor_a data.

        Returns
        -------
        None.

        '''
        self.data = data
     
    @classmethod
    def from_hdf(cls, hdf_file_path: str, band_substring: str='sur_refl') -> xr.Dataset:
        '''
        Converts an hdf file to an xr dataset usign rasterio
    
        Parameters
        ----------
        hdf_file_path : str
            The file path of the hdf file.
        band_substring : str
            Only band names that contain the substring are loaded.
            The default is 'sur_refl'.
    
        Returns
        -------
        cls.
    
        '''
        var_map = {}
        with rio.open(hdf_file_path) as dataset:
            for name in dataset.subdatasets:
                if band_substring in name:
                    with xr.open_rasterio(name) as subdataset:
                        var_map[name.split(sep=':')[-1]] = subdataset
        return cls(xr.Dataset(var_map).squeeze('band').drop('band'))
    
    @staticmethod
    def get_modis_tile_bounds() -> pd.DataFrame:
        '''
        Downloads the tile bounds from 
        https://modis-land.gsfc.nasa.gov/pdf/sn_bound_10deg.txt
        and puts them in a dataframe. 
    
        Returns
        -------
        pandas.DataFrame.
    
        '''
        url = 'https://modis-land.gsfc.nasa.gov/pdf/sn_bound_10deg.txt'
        with urllib.request.urlopen(url) as webpage:
            sin_grid_bounds_str = str(webpage.read()).split('\\r')[6:-3]
            sin_grid_bounds_dict = {}
        for heading in sin_grid_bounds_str[0].strip().split():
            sin_grid_bounds_dict[heading] = []
        for line in sin_grid_bounds_str[1:]:
            line_split = line.strip().split()
            sin_grid_bounds_dict['iv'].append(int(line_split[0]))
            sin_grid_bounds_dict['ih'].append(int(line_split[1]))    
            sin_grid_bounds_dict['lon_min'].append(float(line_split[2])) 
            sin_grid_bounds_dict['lon_max'].append(float(line_split[3]))  
            sin_grid_bounds_dict['lat_min'].append(float(line_split[4]))  
            sin_grid_bounds_dict['lat_max'].append(float(line_split[5]))
        sin_grid_bounds = pd.DataFrame(sin_grid_bounds_dict)
        return sin_grid_bounds
    
    @staticmethod
    def get_modis_tiles_from_coord_pair(lon: float, lat: float) -> pd.DataFrame:
        '''
        Takes a pair of coordinates and returns the MODIS sinusoidal projection
        tile(s) number(s) that contain the coordinate pair.

        Parameters
        ----------
        lon : float
            The longitude.
        lat : float
            The latitude.

        Returns
        -------
        pd.DataFrame.

        '''
        sgb = ModisMultispectralHdf.get_modis_tile_bounds()
        return sgb[((sgb.lon_min <= lon) & (sgb.lon_max >= lon) & 
            (sgb.lat_min <= lat) & (sgb.lat_max >= lat))]
    
    def add_coordinates_in_crs(self, crs_epsg: int):
        '''
        Parameters
        ----------
        crs_epsg : int
            The epsg number of the crs coordinates to be added.

        Returns
        -------
        ModisMultispectralHdf with added coordinates.

        '''
        crs_src = CRS.from_proj4('''+proj=sinu +lon_0=0 +x_0=0 +y_0=0 
                                  +R=6371007.181 +units=m +no_defs=True''')
        crs_dst = CRS.from_epsg(crs_epsg)
        transformer = Transformer.from_crs(crs_src, crs_dst, always_xy=True)
        X, Y = np.meshgrid(self.data.x.values, self.data.y.values)
        x, y = transformer.transform(X, Y)
        xname = 'x_' + str(crs_epsg)
        yname = 'y_' + str(crs_epsg)
        return ModisMultispectralHdf(self.data.assign_coords({xname:(['y', 'x'], x), 
                                        yname:(['x', 'y'], y)}))
    
    def combine_rgb_bands_into_dataarray(self, rgb_bands: List[str]) -> xr.DataArray:
        '''
        Combines 3 bands into a dataarray

        Parameters
        ----------
        rgb_bands : List[str]
            The names of the bands in sequence [r, g, b].
            e.g. ['sur_refl_b01', 'sur_refl_b04', 'sur_refl_b03']

        Returns
        -------
        xr.DataArray.

        '''
        arrays = []
        for band in rgb_bands:
            arrays.append(self.data[band])   
        band_stack = xr.concat(arrays, pd.Index(rgb_bands, name='band'))
        return band_stack.rename('rgb_bands')
    
    def bytescale_array_from_rgb_bands(self, rgb_bands: List[str]):
        '''
        Converts rgb bands to bytescale (0-255)

        Parameters
        ----------
        rgb_bands : List[str]
            The names of the bands in sequence [r, g, b].
            e.g. ['sur_refl_b01', 'sur_refl_b04', 'sur_refl_b03']

        Returns
        -------
        np.ndarray.

        '''
        band_stack = self.combine_rgb_bands_into_dataarray(rgb_bands) * 0.0001
        for band in band_stack: 
            band.values[np.isnan(band_stack).max('band')] = np.nan
        rgb = es.bytescale(band_stack.values,
                           cmin=float(band_stack.min()), 
                           cmax=float(band_stack.max()))
        return rgb
    
    def rgb_bands_to_georaster(self, tiff_path: str, rgb_bands: List[str]):
        '''
        Takes 3 bands, bytescales them and saves them as a geotiff

        Parameters
        ----------
        tiff_path : str
            The path of the geotiff raster.
        rgb_bands : List[str]
            The names of the bands in sequence [r, g, b].
            e.g. ['sur_refl_b01', 'sur_refl_b04', 'sur_refl_b03']

        Returns
        -------
        None.

        '''
        y_max = float(self.data.y.max())
        y_min = float(self.data.y.min())    
        x_max = float(self.data.x.max())
        x_min = float(self.data.x.min())
        res_x = (x_max - x_min) / (len(self.data.x) - 1)
        res_y = (y_max - y_min) / (len(self.data.y) - 1)
        transform = Affine.translation(x_min - res_x / 2, y_min - res_y / 2) \
            * Affine.scale(res_x, res_y)
        
        rgb = self.bytescale_array_from_rgb_bands(rgb_bands)
        
        new_dataset = rio.open(
                tiff_path,
                'w',
                driver='GTiff',
                height=rgb[0].shape[0],
                width=rgb[0].shape[1],
                count=3,
                dtype=rgb.dtype,
                crs=rio.crs.CRS.from_proj4(self.data[rgb_bands[0]].attrs['crs']),
                transform=transform)
        new_dataset.write(np.flipud(rgb[0]), 1)
        new_dataset.write(np.flipud(rgb[1]), 2)
        new_dataset.write(np.flipud(rgb[2]), 3)
        new_dataset.close()
    
    @staticmethod
    def stretch_im(arr, str_clip):
        """
        Stretch an image in numpy ndarray format using a specified clip value.
        GM copied and modified (to ignore NaN values) from 
        https://earthpy.readthedocs.io/en/latest/_modules/earthpy/plot.html#plot_rgb
        on 22-05-2020
    
        Parameters
        ----------
        arr: numpy array
            N-dimensional array in rasterio band order (bands, rows, columns)
        str_clip: int
            The % of clip to apply to the stretch. Default = 2 (2 and 98)
    
        Returns
        ----------
        arr: numpy array with values stretched to the specified clip %
    
        """
        s_min = str_clip
        s_max = 100 - str_clip
        arr_rescaled = np.zeros_like(arr)
        for ii, band in enumerate(arr):
            lower, upper = np.nanpercentile(band, (s_min, s_max))
            arr_rescaled[ii] = exposure.rescale_intensity(
                band, in_range=(lower, upper)
            )
        return arr_rescaled.copy()
    
    def quick_plot_rgb_bands(self, rgb_bands: List[str], str_clip: int=2,):
        '''
        Parameters
        ----------
        rgb_bands : List[str]
            The names of the bands in sequence [r, g, b].
            e.g. ['sur_refl_b01', 'sur_refl_b04', 'sur_refl_b03']
        str_clip : int, optional
            The % of clip to apply to the stretch. Default = 2 (2 and 98)

        Returns
        -------
        axis.

        '''
        fig1 = plt.figure(figsize=(12,12))
        ax1 = plt.axes()
        
        rgb = self.bytescale_array_from_rgb_bands(rgb_bands)
        
        if str_clip is not None:
            image = self.stretch_im(rgb, str_clip).transpose([1, 2, 0])
            image = exposure.adjust_log(image)
        else:
            image = rgb.transpose([1, 2, 0])
        
        ax1.imshow(image)
        return ax1
        
     
    def plot_rgb_bands_with_cartopy(self, 
                          rgb_bands: List[str],
                          str_clip: int=2,
                          projection: cartopy.crs=ccrs.OSGB(approx=False),
                          global_axes:bool=False):
        '''
        Parameters
        ----------
        rgb_bands : List[str]
            The names of the bands in sequence [r, g, b].
            e.g. ['sur_refl_b01', 'sur_refl_b04', 'sur_refl_b03'] 
        str_clip : int, optional
            The % of clip to apply to the stretch. Default = 2 (2 and 98)
        projection : cartopy.crs, optional
            https://scitools.org.uk/cartopy/docs/latest/crs/projections.html. 
            The default is cartopy.crs.OSGB(approx=False).
        global_axes : bool, optional
            whether to display the entire projection 
            (e.g. entire globe for cartopy.crs.Orthographic) or only the part 
            covered by the chl data. The default is False.

        Returns
        -------
        axis

        '''
        
        fig1 = plt.figure(figsize=(12,12))
        ax1 = plt.axes(projection=projection)

        ax1.coastlines()
        ax1.gridlines()
        if global_axes:
            ax1.set_global()
        
        rgb = self.bytescale_array_from_rgb_bands(rgb_bands)
        
        if str_clip is not None:
            image = self.stretch_im(rgb, str_clip).transpose([1, 2, 0])
        else:
            image = rgb.transpose([1, 2, 0])
        
        color_tuple = image.reshape((image.shape[0]*image.shape[1]),image.shape[2]) / 255
        
        self.data[rgb_bands[0]].plot(ax=ax1,  
                                    color=color_tuple, add_colorbar=False,
                                    transform=ccrs.Sinusoidal().MODIS)
        
        return ax1
    
    
 
    