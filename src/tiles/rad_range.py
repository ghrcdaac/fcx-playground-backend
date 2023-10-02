import os
import shutil
import boto3
import numpy as np
import pandas as pd
import xarray as xr
import zarr

from typing import Generator

from abstract.tiles_pointcloud_data_process import TilesPointCloudDataProcess
from utils.tiles_writer import write_tiles

class RadRangeTilesPointCloudDataProcess(TilesPointCloudDataProcess):
  def __init__(self):
    self.url = None
    self.OPENED_FILE_REF = None

    self.campaign = 'Olympex'
    self.collection = "AirborneRadar"
    self.dataset = "gpmValidationOlympexcrs"
    self.variables = ["zku"]
    self.renderers = ["point_cloud"]

    self.chunk = 262144
    self.to_rad = np.pi / 180
    self.to_deg = 180 / np.pi

  def ingest(self, url: str, type: str = "local") -> xr.Dataset:
    """Returns a numpy array representing the raw data file.

    Keyword arguments:
    url -- the path of the raw data file.
    type -- either s3 or local (default local).
    """
    if (type == "s3"):
      return self._ingest_from_s3(url)
    else:
      return self._ingest_from_local(url)
  
  def preprocess(self, data: xr.Dataset) -> str:
    cleaned_data = self._cleaning(data)
    transformed_data = self._transformation(cleaned_data)
    integrated_data = self._integration(transformed_data)
    self.OPENED_FILE_REF.close()
    return integrated_data

  def prep_visualization(self, zarr_data_path: str) -> str:
    point_cloud_folder = zarr_data_path+"_point_cloud"
    write_tiles("ref", 0, 1000000000000, zarr_data_path, point_cloud_folder)
    return point_cloud_folder

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

    # remove nan and infinite using mask (dont use masks filtering for values used for curtain creation)

    mask = np.logical_and(np.isfinite(ref), alt > 0)
    time = time[mask]
    ref = ref[mask]
    lon = lon[mask]
    lat = lat[mask]
    alt = alt[mask]


    df = pd.DataFrame(data = {
      'time': time,
      'lon': lon,
      'lat': lat,
      'alt': alt,
      'ref': ref
    })

    return df
  
  def _integration(self, data: pd.DataFrame) -> str:
    # data from multiple sources can be integrated into intermediate file format, e.g. zarr file. The intermeidate format should be compatible with viz prepration step
    time = data['time'].values
    ref = data['ref'].values
    lon = data['lon'].values
    lat = data['lat'].values
    alt = data['alt'].values

    # path creation
    zarr_path = self._create_zarr_dir()

    # create a ZARR directory in the path provided
    store = zarr.DirectoryStore(zarr_path)
    root = zarr.group(store=store)

    # Create empty rows for modified data inside zarr
    z_chunk_id = root.create_dataset('chunk_id', shape=(0, 2), chunks=None, dtype=np.int64)
    z_location = root.create_dataset('location', shape=(0, 3), chunks=(self.chunk, None), dtype=np.float32)
    z_time = root.create_dataset('time', shape=(0), chunks=(self.chunk), dtype=np.int32)
    z_vars = root.create_group('value')
    z_ref = z_vars.create_dataset('ref', shape=(0), chunks=(self.chunk), dtype=np.float32)
    n_time = np.array([], dtype=np.int64)

    # Now populate (append) the empty rows in ZARR dir with preprocessed data
    z_location.append(np.stack([lon, lat, alt], axis=-1))
    z_ref.append(ref)
    n_time = np.append(n_time, time)

    idx = np.arange(0, n_time.size, self.chunk)
    chunks = np.zeros(shape=(idx.size, 2), dtype=np.int64)
    chunks[:, 0] = idx
    chunks[:, 1] = n_time[idx]
    z_chunk_id.append(chunks)

    epoch = np.min(n_time)
    n_time = (n_time - epoch).astype(np.int32)
    z_time.append(n_time)

    # save it.
    root.attrs.put({
        "campaign": self.campaign,
        "collection": self.collection,
        "dataset": self.dataset,
        "variables": self.variables,
        "renderers": self.renderers,
        "epoch": int(epoch)
    })

    return zarr_path

  # ingesting variations

  def _ingest_from_local(self, path: str) -> xr.Dataset:
    data = self._generator_to_xr(path)
    return data

  def _ingest_from_s3(self, url: str) -> xr.Dataset:
    self.url = url
    s3_client = boto3.client('s3')
    [bucket_name, objectKey] = self._get_s3_details(url)

    s3_file = s3_client.get_object(Bucket=bucket_name, Key=objectKey)
    file = s3_file['Body'].read()

    data = self._generator_to_xr(file)
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

  def _create_zarr_dir(self):
    """Create a directory to hold zarr file
    """
    date = self._get_date_from_url(self.url)
    tempdir = 'temp/' + str(date) + '/zarr'
    if os.path.exists(tempdir):
        shutil.rmtree(tempdir)
    os.makedirs(tempdir)
    return tempdir