# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 08:42:15 2020

@author: Greg.Moschonas
"""
from datetime import datetime, timedelta
import xarray as xr
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
#from mowi import environment
#from mowi.utility import path

from bokeh.plotting import figure, output_file, show, reset_output
from bokeh.models import (BasicTicker, ColorBar, 
                          LinearColorMapper, HoverTool,
                          ColumnDataSource, Title)
from bokeh.tile_providers import get_provider, Vendors
from bokeh.palettes import Greens6
import numpy as np
# import pandas as pd
# from datetime import datetime
import cartopy
import cartopy.crs as ccrs
from pyproj import CRS
from pyproj import Transformer

class NasaOceandataChla:
    '''
    Operations for importing and plotting satellite L3 chlor_a data from 
    https://oceandata.sci.gsfc.nasa.gov/opendap/
    
    Examples
    >>> chl = NasaOceandataChla.single_day_from_nasa_oceandata_opendap(date=datetime(2020, 4, 29), mission='VIIRSJ1', lat_min=55, lat_max=59, lon_min=-9, lon_max=-4)

    >>> chl.data
    <xarray.Dataset>
    Dimensions:  (lat: 97, lon: 121, time: 1)
    Coordinates:
      * lat      (lat) float32 59.020832 58.979164 58.9375 ... 55.0625 55.020832
      * lon      (lon) float32 -9.020828 -8.979161 ... -4.0624948 -4.0208282
      * time     (time) datetime64[ns] 2020-04-29
    Data variables:
        chlor_a  (time, lat, lon) float32 nan nan 1.0637656 ... nan nan nan
    
    >>> chl.plot_time_average_with_cartopy()
    
    >>> chl2 = NasaOceandataChla.range_of_days_from_nasa_oceandata_opendap(end_date=datetime.today(), n_days=7, mission='MODISA', **NasaOceandataChla.swc_bounds)
    
    >>> chl2.data
    <xarray.Dataset>
    Dimensions:  (lat: 97, lon: 121, time: 6)
    Coordinates:
      * lon      (lon) float32 -9.020828 -8.979161 ... -4.0624948 -4.0208282
      * lat      (lat) float32 59.020832 58.979164 58.9375 ... 55.0625 55.020832
      * time     (time) datetime64[ns] 2020-05-08T12:43:00.038509 ... 2020-05-13T12:43:00.038509
    Data variables:
        chlor_a  (time, lat, lon) float32 nan nan nan nan nan ... nan nan nan nan
    
    >>> chl2.plot_time_average_with_cartopy()
    
    # Change the projection of the plot - example April chlorophyll dataset
    chl_april.plot_time_average_with_cartopy(projection=ccrs.Orthographic(-3, 55), vmax_quantile=0.99)
    '''
    swc_bounds = {'lat_min':55, 'lat_max':59, 'lon_min':-9, 'lon_max':-4}
    
    def __init__(self, data:xr.Dataset, mission: str='unspecified',
                 time_coordinate:datetime = None):
        '''
        Parameters
        ----------
        data : xr.Dataset
            an xarray dataset with nasa oceandata chlor_a data.
        mission : str, optional
            the mission from which the data was sourced. 
            The default is 'unspecified'.

        Returns
        -------
        None.

        '''
   
        self.data = data
        self.mission = mission
        if time_coordinate is not None:
            self.data['chlor_a'] = self.data.chlor_a.expand_dims(dim={'time': [time_coordinate]})
        
    @staticmethod
    def construct_opendap_url(date: datetime,
                              mission: str='VIIRSJ1',
                              lat_min: float=-90,
                              lat_max: float=90,
                              lon_min: float=-180,
                              lon_max: float=180,) -> str:
        '''
        Parameters
        ----------
        date : datetime
            the date for which you wish to download chlorophyll a data.
        mission : str, optional
            one of {MODISA, MODIST, VIIRSJ1}. The default is 'VIIRSJ1'.
        lat_min : float, optional
            the minimum latitude. The default is -90.
        lat_max : float, optional
            the maximum latitude. The default is 90.
        lon_min : float, optional
            the minimum longitude. The default is -180.
        lon_max : float, optional
            the maximum longitude. The default is 180.

        Returns
        -------
        str
            the opendap url.

        '''
        # construct the url from date and mission
        first_part = 'https://oceandata.sci.gsfc.nasa.gov:443/opendap/'
        second_part = mission + '/L3SMI/'
        year = str(date.year)
        jday = '{0:03d}'.format(date.timetuple().tm_yday)
        third_part = year + '/' + jday + '/'
        if mission == 'MODISA':
            fname_start = 'A'
            m = ''
        elif mission == 'MODIST':
            fname_start = 'T'
            m = ''
        else:
            fname_start = 'V'
            m = 'JPSS1_'
        fourth_part = fname_start + year + jday + '.L3m_DAY_' + m + 'CHL_chlor_a_4km.nc'
        lat1 = int((90-lat_min)/ 0.0416666679)
        lat2 = int((90-lat_max)/ 0.0416666679)
        lon1 = int((180+lon_min)/ 0.0416666679)
        lon2 = int((180+lon_max)/ 0.0416666679)
        lat = '[{0}:1:{1}]'.format(min(lat1, lat2), max(lat1, lat2))
        lon = '[{0}:1:{1}]'.format(min(lon1, lon2), max(lon1, lon2))
        fifth_part = '?chlor_a' + lat + lon + ',lat' + lat + ',lon' + lon
        url = first_part + second_part + third_part + fourth_part + fifth_part
        # return url
        return url
        
    @classmethod
    def single_day_from_nasa_oceandata_opendap(cls,
                                                date: datetime,
                                                mission: str='VIIRSJ1',
                                                lat_min: float=-90,
                                                lat_max: float=90,
                                                lon_min: float=-180,
                                                lon_max: float=180,):
        '''
        Parameters
        ----------
        date : datetime
            the date for which you wish to download chlorophyll a data.
        mission : str, optional
            one of {MODISA, MODIST, VIIRSJ1}. The default is 'VIIRSJ1'.
        lat_min : float, optional
            the minimum latitude. The default is -90.
        lat_max : float, optional
            the maximum latitude. The default is 90.
        lon_min : float, optional
            the minimum longitude. The default is -180.
        lon_max : float, optional
            the maximum longitude. The default is 180.
    
        Returns
        -------
        NasaOceandataChla.
    
        '''
        # get the opendap url
        url = cls.construct_opendap_url(date, mission, lat_min, lat_max, 
                                         lon_min, lon_max)
        # download the data into an xarray dataset
        try:
            remote_data = xr.open_dataset(url,decode_times=False)
            remote_data['chlor_a'] = remote_data.chlor_a.expand_dims(dim={'time': [date]})
            # return the dataset
            return cls(remote_data.chlor_a.to_dataset(), mission=mission)
        except:
            return cls(None)
        
    @classmethod
    def latest_day_from_nasa_oceandata_opendap(cls,
                                               mission: str='VIIRSJ1',
                                               lat_min: float=-90,
                                               lat_max: float=90,
                                               lon_min: float=-180,
                                               lon_max: float=180,):
        '''
        Checks for up to ten days in the past. If it does not find any 
        data, it assumes that the dataset has been discontinued and aborts

        Parameters
        ----------
        mission : str, optional
            one of {MODISA, MODIST, VIIRSJ1}. The default is 'VIIRSJ1'.
        lat_min : float, optional
            the minimum latitude. The default is -90.
        lat_max : float, optional
            the maximum latitude. The default is 90.
        lon_min : float, optional
            the minimum longitude. The default is -180.
        lon_max : float, optional
            the maximum longitude. The default is 180.

        Returns
        -------
        NasaOceandataChla.

        '''
        
        date = datetime.now()
        # get the opendap url
        url = cls.construct_opendap_url(date, mission, lat_min, lat_max, 
                                         lon_min, lon_max)
        # download the data into an xarray dataset
        retry = True
        count = 0
        while retry and count<10:
            try:
                url = cls.construct_opendap_url(date, mission, lat_min, lat_max, 
                                         lon_min, lon_max)
                remote_data = xr.open_dataset(url,decode_times=False)
                remote_data['chlor_a'] = remote_data.chlor_a.expand_dims(dim={'time': [date]})
                # return the dataset
                retry = False
                return cls(remote_data.chlor_a.to_dataset(), mission=mission)
            except:
                count = count + 1  
                date = date - timedelta(days=1)
                if count == 10:
                    print('Checked 10 days. Aborting.')

    @classmethod
    def range_of_days_from_nasa_oceandata_opendap(cls,
                                                  end_date: datetime,
                                                  n_days:int=7,
                                                  mission: str='VIIRSJ1',
                                                  lat_min: float=-90,
                                                  lat_max: float=90,
                                                  lon_min: float=-180,
                                                  lon_max: float=180,):
        '''
        Parameters
        ----------
        end_date : datetime
            the last date in the range.
        n_days : int, optional
            the number of days. The default is 7.
        mission : str, optional
            one of {MODISA, MODIST, VIIRSJ1}. The default is 'VIIRSJ1'.
        lat_min : float, optional
            the minimum latitude. The default is -90.
        lat_max : float, optional
            the maximum latitude. The default is 90.
        lon_min : float, optional
            the minimum longitude. The default is -180.
        lon_max : float, optional
            the maximum longitude. The default is 180.

        Returns
        -------
        NasaOceandataChla.

        '''
        daterange = pd.date_range(end=end_date, periods=n_days)
        all_data = []
        for date in daterange:
            chl = cls.single_day_from_nasa_oceandata_opendap(date, mission, 
                                                               lat_min, lat_max, 
                                                               lon_min, lon_max)
            data = chl.data
            if data is not None:
                all_data.append(data.copy())
        assembled = xr.concat(all_data, 'time')
        return cls(assembled, mission=mission)
    
    def to_netcdf(self, out_path: str):
        '''
        Parameters
        ----------
        out_path : str
            the path of the .nc file to be written.

        Returns
        -------
        None.

        '''
        self.data.to_netcdf(out_path)
    
    def plot_time_average_with_cartopy(self, 
                                       projection: cartopy.crs=ccrs.OSGB(),
                                       global_axes:bool=False,
                                       vmax_quantile: float=0.95):
        '''
        Uses cartopy coastlines and crs conversions to generate a map

        Parameters
        ----------
        projection : cartopy.crs, optional
            Any cartopy projection - 
            https://scitools.org.uk/cartopy/docs/latest/crs/projections.html. 
            The default is cartopy.crs.OSGB().
        global_axes : bool, optional
            whether to display the entire projection 
            (e.g. entire globe for cartopy.crs.Orthographic) or only the part 
            covered by the chl data. The default is False.
        vmax_quantile : float, optional
            the quantile that will be the maximum chla value in the legend.
            The default is 0.95.

        Returns
        -------
        axis : matplotlib.axes._subplots.AxesSubplot
            the matplotlib axis.

        '''
        fig1 = plt.figure(figsize=(12,12))
        ax1 = plt.axes(projection=projection)
        
        ax1.coastlines()
        ax1.gridlines()
        if global_axes:
            ax1.set_global()
        
        vmax = self.data.chlor_a.mean('time').quantile(vmax_quantile)
        chl_plt = self.data.chlor_a.mean('time').plot(ax=ax1, vmax=vmax,
                                                      transform=ccrs.PlateCarree(),
                                                      cmap=plt.cm.get_cmap('Spectral').reversed(),
                                                      cbar_kwargs={'shrink': 0.7, 'label': 'chlorophyll_a (mg m-3)'})    
        
        start_date = self.data.time.min()
        end_date = self.data.time.max()
        start_date_str = '{0}-{1}-{2}'.format(str(start_date.dt.day.values),
                                              str(start_date.dt.month.values),
                                              str(start_date.dt.year.values))
        end_date_str = '{0}-{1}-{2}'.format(str(end_date.dt.day.values),
                                            str(end_date.dt.month.values),
                                            str(end_date.dt.year.values))
        title = 'Average chl_a concentration between ' + start_date_str + \
            ' and ' + end_date_str + '\nSource: ' + self.mission
        ax1.set(title=title)
        
        return ax1
    
    def bokeh_plot_time_average_with_land(self, save_path: str=None, 
                                          vmax_quantile: float=0.95):
        '''
        Parameters
        ----------
        save_path : str, optional
            the path of the .html file to be saved. 
            The default is None, which does not save a file
        vmax_quantile : float, optional
            the quantile that will be the maximum chla value in the legend. 
            The default is 0.95.

        Returns
        -------
        None.

        '''
        crs_src = CRS.from_epsg(4326)
        crs_dst = CRS.from_epsg(3857)
        
        #prepare the chlorophyll a data
        plot_data = np.flipud(self.data.chlor_a.mean('time').values)
        transformer = Transformer.from_crs(crs_src, crs_dst, always_xy=True)
        x_min, y_min = transformer.transform(self.data.lon.values.min(),
                                             self.data.lat.values.min())
        x_max, y_max = transformer.transform(self.data.lon.values.max(),
                                             self.data.lat.values.max())
        x_range = [x_min, x_max]
        y_range = [y_min, y_max]
        dw = x_max - x_min
        dh = y_max - y_min
        
        
        # prepare the title
        start_date = self.data.time.min()
        end_date = self.data.time.max()
        start_date_str = '{0}-{1}-{2}'.format(str(start_date.dt.day.values),
                                              str(start_date.dt.month.values),
                                              str(start_date.dt.year.values))
        end_date_str = '{0}-{1}-{2}'.format(str(end_date.dt.day.values),
                                            str(end_date.dt.month.values),
                                            str(end_date.dt.year.values))
        title1 = 'Average chl_a concentration between ' + start_date_str + \
            ' and ' + end_date_str + '\t' + self.mission
        # title2 = chl.mission
        
        # initialise the figure
        p = figure(x_axis_type="mercator", 
                   y_axis_type="mercator",
                   match_aspect=True,
                   x_range=x_range, 
                   y_range=y_range,
                   plot_height = 700)
        
        # add a title
        # p.add_layout(Title(text=title2), 'above')
        p.add_layout(Title(text=title1), 'above')
        
        # add land
        p.add_tile(get_provider(Vendors.STAMEN_TONER_BACKGROUND))
        
        # add the chlorophyll plot
        color_mapper = LinearColorMapper(palette=list(reversed(Greens6)), low=np.nanmin(plot_data), 
                                         high=np.nanquantile(plot_data, vmax_quantile),
                                         nan_color='rgba(0, 0, 0, 0)')
        chl_plot = p.image(image=[plot_data], x=[x_min], y=[y_min], 
                dw=[dw], dh=[dh], color_mapper=color_mapper)
        
        # add hover tool for chl plot
        image_hover = HoverTool(renderers=[chl_plot])
        image_hover.tooltips = [("chl_a", "@image")]
        p.add_tools(image_hover)
        
        # add a color bar
        color_bar = ColorBar(color_mapper=color_mapper, ticker=BasicTicker(),
                             label_standoff=12, border_line_color=None, location=(0,0),
                             title = 'mg m-3')
        p.add_layout(color_bar, 'right')
        
        # remove grid
        p.grid.visible = False
        # p.grid.grid_line_width = 1
        # p.grid.grid_line_color = 'white'
        
        reset_output()
        if save_path is not None:
            # save file
            output_file(save_path, 
                        title=('chla ' + start_date_str + ' to ' + end_date_str 
                               + ' ' + self.mission))
        # show plot
        show(p)
 
    