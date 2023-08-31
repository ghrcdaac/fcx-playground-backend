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
    self.OPENED_FILE_REF = None
  
  def ingest(self, url: str) -> xr.Dataset:
    self.url = url
    s3_client = boto3.client('s3')
    [bucket_name, objectKey] = self._get_s3_details(url)
    
    s3_file = s3_client.get_object(Bucket=bucket_name, Key=objectKey)
    file = s3_file['Body'].read()
    
    data = self._generator_to_xr(file)
    return data
  
  def preprocess(self, data: xr.Dataset) -> xr.Dataset:
    cleaned_data = self._cleaning(data)
    transformed_data = self._transformation(cleaned_data)
    integrated_data = self._integration(transformed_data)
    self.OPENED_FILE_REF.close()
    return integrated_data

  def prep_visualization(self, data: pd.DataFrame) -> str:
    return data

  # data preprocessing steps

  def _cleaning(self, data: xr.Dataset) -> xr.Dataset:
    # data extraction
    # scrape necessary data columns 
    extracted_data = data[['timed', 'zku', 'lat', 'lon', 'altitude', 'roll', 'pitch', 'head', 'range']]
    return extracted_data

  def _transformation(self, data: xr.Dataset) -> pd.DataFrame:
    #  transform the data to a suitable data formatting
    hour = data['timed'].values
    lat = data['lat'].values
    lon = data['lon'].values
    alt = data['altitude'].values # altitude of aircraft in meters
    roll = data["roll"].values
    pitch = data["pitch"].values
    head = data["head"].values
    ref = data['zku'].values #CRS radar reflectivity #2d data
    rad_range = data["range"].values # has lower count than ref
    
    # time correction and conversion:
    base_time = self._get_date_from_url(self.url)
    hour = self._add24hr(hour)
    delta = (hour * 3600).astype('timedelta64[s]') + base_time
    time = (delta - np.datetime64('1970-01-01')).astype('timedelta64[s]').astype(np.int64)

    # transform ref to 1d array and repeat other columns to match data dimension

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

    # curtain creation

    x, y, z = self._down_vector(roll, pitch, head)
    x = np.multiply(x, np.divide(rad_range, 111000 * np.cos(lat * self.to_rad)))
    y = np.multiply(y, np.divide(rad_range, 111000))
    z = np.multiply(z, rad_range)
    lon = np.add(-x, lon)
    lat = np.add(-y, lat)
    alt = np.add(z, alt)

    # sort by time

    sort_idx = np.argsort(time)
    lon = lon[sort_idx]
    lat = lat[sort_idx]
    alt = alt[sort_idx]
    ref = ref[sort_idx]
    time = time[sort_idx]

    print("time", len(time))
    print("lon", len(lon))
    print("lat", len(lat))
    print("alt", len(alt))
    print("ref", len(ref))
    print("roll", len(roll))
    print("pitch", len(pitch))
    print("head", len(head))
    print("rad_range", len(rad_range))

    df = pd.DataFrame(data = {
      'time': time,
      'lon': lon,
      'lat': lat,
      'alt': alt,
      'roll': roll,
      'pitch': pitch,
      'head': head,
      'rad_range': rad_range,
      'ref': ref
    })
    return df
  
  def _integration(self, data: pd.DataFrame) -> pd.DataFrame:
    # data from multiple sources can be integrated into intermediate file format, e.g. zarr file. The intermeidate format should be compatible with viz prepration step
    time = data['time']
    ref = data['ref']
    lon = data['lon']
    lat = data['lat']
    alt = data['alt']
    roll = data['roll']
    pitch = data['pitch']
    head = data['head']
    rad_range = data['rad_range']

    # remove nan and infinite using mask (dont use masks filtering for values used for curtain creation)
    mask = np.logical_and(np.isfinite(ref), alt > 0)
    time = time[mask]
    ref = ref[mask]
    lon = lon[mask]
    lat = lat[mask]
    alt = alt[mask]

    return data

  # utils

  def _get_s3_details(self, url) -> list:
    url = url.replace("s3://", "")
    temp_url = url.split("/")
    bucket_name = temp_url[0]
    
    temp_url = url.split(bucket_name+"/")
    objectKey = temp_url[1]  # key should not start with /
    return [bucket_name, objectKey]
  
  def _generator_to_xr(self, infile: Generator) -> xr.Dataset:
    # As the data in netcdf format, to put it inside numpy array, we need to read it first.
    ds = xr.open_dataset(infile, decode_cf=False) # dont close opened dataset just yet
    self.OPENED_FILE_REF = ds # close later, after data preprocessing.
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

  def _down_vector(self, roll, pitch, head):
    x = np.sin(roll) * np.cos(head) + np.cos(roll) * np.sin(pitch) * np.sin(head)
    y = -np.sin(roll) * np.sin(head) + np.cos(roll) * np.sin(pitch) * np.cos(head)
    z = -np.cos(roll) * np.cos(pitch)
    return (x, y, z)