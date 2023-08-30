import boto3
from copy import deepcopy
import numpy as np
import pandas as pd
import xarray as xr

from typing import Generator


from abstract.tiles_pointcloud_data_process import TilesPointCloudDataProcess

class RadRangeTilesPointCloudDataProcess(TilesPointCloudDataProcess):
  def __init__(self):
    self.url = ''
    self.to_rad = np.pi / 180
    self.to_deg = 180 / np.pi
  
  def ingest(self, url: str) -> xr.Dataset:
    self.url = url
    s3_client = boto3.client('s3')
    [bucket_name, objectKey] = self._get_s3_details(url)
    
    s3_file = s3_client.get_object(Bucket=bucket_name, Key=objectKey)
    file = s3_file['Body'].read()
    
    data = self._generator_to_np(file)
    return data
  
  def preprocess(self, data: xr.Dataset) -> pd.DataFrame:
    cleaned_data = self._cleaning(data)
    transformed_data = self._transformation(cleaned_data)
    integrated_data = self._integration(transformed_data)
    return integrated_data

  def prep_visualization(self, data: pd.DataFrame) -> str:
    return data

  # data preprocessing steps

  def _cleaning(self, data: xr.Dataset) -> xr.Dataset:
    # data extraction
    # scrape necessary data columns 
    extracted_data = data[['timed', 'zku', 'lat', 'lon', 'altitude', 'roll', 'pitch', 'head', 'range']]
    return extracted_data

  def _transformation(self, data: xr.Dataset) -> xr.Dataset:
    return data
    #  transform the data to a suitable data formatting
    hour = data.data_vars['timed'].values
    lat = data.data_vars['lat'].values
    lon = data.data_vars['lon'].values
    alt = data.data_vars['altitude'].values # altitude of aircraft in meters
    roll = data.data_vars["roll"].values
    pitch = data.data_vars["pitch"].values
    head = data.data_vars["head"].values
    ref = data.data_vars['zku'].values #CRS radar reflectivity #2d data
    rad_range = data["range"].values # has lower count than ref
    
    # time correction and conversion:
    base_time = self._get_date_from_url(self.url)
    hour = self._add24hr(hour)
    delta = (hour * 3600).astype('timedelta64[s]') + base_time
    time = (delta - np.datetime64('1970-01-01')).astype('timedelta64[s]').astype(np.int64)

    # transform:
    num_col = ref.shape[0] # number of cols
    num_row = ref.shape[1] # number of rows

    time = np.repeat(time, num_row)
    lon = np.repeat(lon, num_row)
    lat = np.repeat(lat, num_row)
    alt = np.repeat(alt, num_row)
    roll = np.repeat(roll * self.to_rad, num_row)
    pitch = np.repeat(pitch * self.to_rad, num_row)
    head = np.repeat(head * self.to_rad, num_row)
    rad_range = np.tile(rad_range, num_col)
    ref = ref.flatten()
  
  def _integration(self, data: pd.DataFrame) -> pd.DataFrame:
    # data from multiple sources can be integrated into intermediate file format, e.g. zarr file. The intermeidate format should be compatible with viz prepration step
    return data

  # utils

  def _get_s3_details(self, url) -> list:
    url = url.replace("s3://", "")
    temp_url = url.split("/")
    bucket_name = temp_url[0]
    
    temp_url = url.split(bucket_name+"/")
    objectKey = temp_url[1]  # key should not start with /
    return [bucket_name, objectKey]
  
  def _generator_to_np(self, infile: Generator) -> xr.Dataset:
    # As the data in netcdf format, to put it inside numpy array, we need to read it first.
    with xr.open_dataset(infile, decode_cf=False) as ds:
      # data columns extract
      return ds
  
  def _add24hr(self, hour: np.ndarray) -> np.ndarray:
    # time correction
    # time in CRS for going over the next day in UTC
    # so add 24 hours to the time to get the correct time"""
    mask = np.where(hour < hour[0])
    hour[mask] = hour[mask] + 24
    return hour
  
  def _get_date_from_url(self, url: str) -> np.datetime64:
    # get date from url
    # date is in the format of YYYYMMDD
    # eg. 20190801
    date = url.split("olympex_CRS_")[1].split("_")[0]
    np_date = np.datetime64('{}-{}-{}'.format(date[:4], date[4:6], date[6:]))
    return np_date