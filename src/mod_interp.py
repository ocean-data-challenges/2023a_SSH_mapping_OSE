import datetime
import logging
from datetime import timedelta

import numpy
import pandas
import pyinterp
import pyinterp.backends.xarray
import xarray as xr


class TimeSeries:
    """
    Manage a time series composed of a grid stack.

    Parameters
    ----------
    ds : xarray.Dataset
        Input dataset containing the time series data.

    Attributes
    ----------
    ds : xarray.Dataset
        Input dataset containing the time series data.
    series : pandas.Series
        Time series data loaded from the dataset.
    dt : datetime.timedelta
        Time step duration between consecutive data points in the series.

    Methods
    -------
    _is_sorted(array)
        Check if an array is sorted.
    _load_ts()
        Load the time series data into memory.
    _load_dataset(self, varname, start, end)
        Loading the time series into memory for the defined period.
    """

    def __init__(self, ds):
        """
        Initialize a TimeSeries object.

        Parameters
        ----------
        ds : xarray.Dataset
            Input dataset containing the time series data.
        """
        
        self.ds = ds
        self.series, self.dt = self._load_ts()

    @staticmethod
    def _is_sorted(array):
        """
        Check if an array is sorted.

        Parameters
        ----------
        array : numpy.ndarray
            Input array to check.

        Returns
        -------
        bool
            True if the array is sorted, False otherwise.
        """
        
        indices = numpy.argsort(array)
        return numpy.all(indices == numpy.arange(len(indices)))

    def _load_ts(self):
        """
        Load the time series data into memory.

        Returns
        -------
        pandas.Series
            Loaded time series data.
        datetime.timedelta
            Time step duration between consecutive data points in the series.
        """
        time = self.ds.time
        assert self._is_sorted(time)

        series = pandas.Series(time)
        frequency = set(
            numpy.diff(series.values.astype("datetime64[s]")).astype("int64"))
        if len(frequency) != 1:
            raise RuntimeError(
                "Time series does not have a constant step between two "
                f"grids: {frequency} seconds")
        #return series, datetime.timedelta(seconds=float(frequency.pop()))
        return series, timedelta(seconds=float(frequency.pop()))

    def _load_dataset(self, varname, start, end):
        """
        Loading the time series into memory for the defined period.
        
        Parameters
        ----------
        varname: str
            Name of the variable to be loaded into memory.
        start: datetime.datetime
               Date of the first map to be loaded.
        end: datetime.datetime
               Date of the last map to be loaded.
        
        Returns
        ------- 
        pyinterp.backends.xarray.Grid3D: 
                The interpolator handling the interpolation of the grid series.
        """
        
        if start < self.series.min():
            start = self.series.min()
        if end > self.series.max():
            end = self.series.max()
        
        #if start < self.series.min() or end > self.series.max():
        #    raise IndexError(
        #        f"period [{start}, {end}] out of range [{self.series.min()}, "
        #        f"{self.series.max()}]")
            
        first = start - self.dt
        last = end + self.dt

        selected = self.series[(self.series >= first) & (self.series < last)]
        logging.info("fetch data from %s to %s",selected.min(), selected.max())

        data_array = self.ds[varname].isel(time=selected.index)
        return pyinterp.backends.xarray.Grid3D(data_array)
    
    
def periods(df, time_series, var_name="sla_unfiltered", frequency='W'):
    """
    Return the list of periods covering the time series loaded in memory.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing time series data.
    time_series : TimeSeries
        Time series data and properties.
    var_name : str, optional
        Name of the variable to consider, by default "sla_unfiltered".
    frequency : str, optional
        Frequency for period grouping, by default 'W' (weekly).

    Yields
    ------
    tuple
        A tuple containing the start and end timestamps of each period.
    """
    period_start = df.groupby(
        df.index.to_period(frequency))[var_name].count().index

    for start, end in zip(period_start, period_start[1:]):
        start = start.to_timestamp()
        if start < time_series.series[0]:
            start = time_series.series[0]
        end = end.to_timestamp()
        yield start, end
    yield end, df.index[-1] + time_series.dt
    
    

def interpolate(df, time_series, start, end):
    """
    Interpolate the time series over the defined period.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing time series data.
    time_series : TimeSeries
        Time series data and properties.
    start : pandas.Timestamp
        Start timestamp of the interpolation period.
    end : pandas.Timestamp
        End timestamp of the interpolation period.
    """
    interpolator = time_series._load_dataset("sla", start, end)
    mask = (df.index >= start) & (df.index < end)
    selected = df.loc[mask, ["longitude", "latitude"]]
    df.loc[mask, ["msla_interpolated"]] = interpolator.trivariate(
        dict(longitude=selected["longitude"].values,
             latitude=selected["latitude"].values,
             time=selected.index.values),
        interpolator="inverse_distance_weighting",
        num_threads=0)
    
    
def run_interpolation(ds_maps, ds_alongtrack, frequency='M'):
    """
    Interpolate time series data over specified periods.

    Parameters
    ----------
    ds_maps : xarray.Dataset
        Input dataset containing maps data.
    ds_alongtrack : xarray.Dataset
        Input dataset containing along-track data.
    frequency : str, optional
        Frequency for period grouping, by default 'M' (monthly).

    Returns
    -------
    xarray.Dataset
        Interpolated dataset.
    """
    
    time_series = TimeSeries(ds_maps)
    
    df = ds_alongtrack.to_dataframe()

    for start, end in periods(df, time_series, frequency=frequency):
        interpolate(df, time_series, start, end)
        
    ds = df.to_xarray()
        
    return ds


def interpolate_current(df, time_series, start, end):
    """
    Interpolate the current time series over the defined period.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing time series data.
    time_series : TimeSeries
        Time series data and properties.
    start : pandas.Timestamp
        Start timestamp of the interpolation period.
    end : pandas.Timestamp
        End timestamp of the interpolation period.
    """
    interpolator = time_series._load_dataset("ugos", start, end)
    mask = (df.index >= start) & (df.index < end)
    selected = df.loc[mask, ["longitude", "latitude"]]
    df.loc[mask, ["ugos_interpolated"]] = interpolator.trivariate(
        dict(longitude=selected["longitude"].values,
             latitude=selected["latitude"].values,
             time=selected.index.values),
        interpolator="inverse_distance_weighting",
        num_threads=0)
    
    interpolator = time_series._load_dataset("vgos", start, end)
    mask = (df.index >= start) & (df.index < end)
    selected = df.loc[mask, ["longitude", "latitude"]]
    df.loc[mask, ["vgos_interpolated"]] = interpolator.trivariate(
        dict(longitude=selected["longitude"].values,
             latitude=selected["latitude"].values,
             time=selected.index.values),
        interpolator="inverse_distance_weighting",
        num_threads=0)


def reformat_drifter_dataset(ds):
    """
    Reformat a drifter dataset, extracting relevant variables.

    Parameters
    ----------
    ds : xarray.Dataset
        Input drifter dataset.

    Returns
    -------
    xarray.Dataset
        Reformatted drifter dataset.
    """
    
    ds = ds.isel(DEPTH=1)
    lat = ds['LATITUDE'].values
    lon = ds['LONGITUDE'].values
    drop_vars = ['TIME_QC', 'POSITION_QC', 'DEPH_QC', 'EWCT_QC', 'NSCT_QC', 'EWCT_WS_QC', 'NSCT_WS_QC', 'WS_TYPE_OF_PROCESSING', 'TEMP', 'TEMP_QC', 'LONGITUDE', 'LATITUDE']
    ds = ds.drop_vars(drop_vars)
    ds = ds.rename({'TIME':'time'})
    ds['longitude'] = (("time"), lon)
    ds['latitude'] = (("time"), lat)
    ds['sensor_id'] = (("time"), ds.platform_code*numpy.ones(ds['time'].size))
    return ds
 

def run_interpolation_drifters(ds_maps, ds_drifter, time_min, time_max, frequency='M'):
    """
    Interpolate drifters data over specified periods.

    Parameters
    ----------
    ds_maps : xarray.Dataset
        Input dataset containing maps data.
    ds_drifter : xarray.Dataset
        Input dataset containing drifter data.
    time_min : numpy.datetime64
        Minimum time for interpolation.
    time_max : numpy.datetime64
        Maximum time for interpolation.
    frequency : str, optional
        Frequency for period grouping, by default 'M' (monthly).

    Returns
    -------
    xarray.Dataset
        Interpolated drifter dataset.
    """
 
    time_series = TimeSeries(ds_maps)
    
    # Convert to dataframe and interpolate
    df = ds_drifter.to_dataframe()
    for start, end in periods(df, time_series, var_name='NSCT', frequency=frequency):
        interpolate_current(df, time_series, start, end)
        
    ds = df.to_xarray()
    
    return ds
