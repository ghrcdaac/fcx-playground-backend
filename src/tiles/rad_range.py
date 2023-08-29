import boto3
from copy import deepcopy
import numpy as np
import pandas as pd
import xarray as xr

from typing import Generator


from abstract.tiles_pointcloud_data_process import TilesPointCloudDataProcess

class RadRangeTilesPointCloudDataProcess(TilesPointCloudDataProcess):
  def __init__(self):
    pass
  
  def ingest(self, url: str) -> pd.DataFrame:
    s3_client = boto3.client('s3')
    [bucket_name, objectKey] = self._get_s3_details(url)
    
    s3_file = s3_client.get_object(Bucket=bucket_name, Key=objectKey)
    file = s3_file['Body'].read()
    
    data = self._generator_to_np(file)
    return data
  
  def preprocess(self, data: np.array) -> pd.DataFrame:
    pass

  def prep_visualization(self, data: pd.DataFrame) -> str:
    pass

  # data preprocessing steps

  def _cleaning(self, data: np.array) -> pd.DataFrame:
    pass

  def _transformation(self, data: pd.DataFrame) -> pd.DataFrame:
    #  no transformation needed
    return data
  
  def _integration(self, data: pd.DataFrame) -> pd.DataFrame:
    # no integration needed
    return data

  # utils

  def _get_s3_details(self, url) -> list:
    url = url.replace("s3://", "")
    temp_url = url.split("/")
    bucket_name = temp_url[0]
    
    temp_url = url.split(bucket_name+"/")
    objectKey = temp_url[1]  # key should not start with /
    return [bucket_name, objectKey]
  
  def _generator_to_np(self, infile: Generator) -> pd.DataFrame:
    # As the data in netcdf format, to put it inside numpy array, we need to read it first.
    with xr.open_dataset(infile, decode_cf=False) as ds:
      # data columns extract
      time = ds['timed'].values
      ref = ds['zku'].values # radar reflectivity
      rad_range = ds["range"].values # radar range
      lat = ds['lat'].values
      lon = ds['lon'].values
      alt = ds['altitude'].values # altitude of aircraft in meters
      roll = ds["roll"].values
      pitch = ds["pitch"].values
      head = ds["head"].values

    # create dataframe
    
    df = pd.DataFrame(data = {"time": time, "ref": ref, "rad_range": rad_range, "lat": lat, "lon": lon, "alt": alt, "roll": roll, "pitch": pitch, "head": head})
    return df
