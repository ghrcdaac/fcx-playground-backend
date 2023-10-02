import boto3
from copy import deepcopy
import numpy as np
import pandas as pd
from typing import Generator

from abstract.czml_data_process import CZMLDataProcess
from utils.czml_writer_nav import NavCzmlWriter

class NavCZMLDataProcess(CZMLDataProcess):
  def __init__(self):    
    pass
  
  def ingest(self, url: str, type: str = "local") -> np.array:
    """Returns a numpy array representing the raw data file.

    Keyword arguments:
    url -- the path of the raw data file.
    type -- either s3 or local (default local).
    """
    if (type == "s3"):
      return self._ingest_from_s3(url)
    else:
      return self._ingest_from_local(url)
  
  def preprocess(self, data: np.array) -> pd.DataFrame:
    cleaned_data = self._cleaning(data)
    transformed_data = self._transformation(cleaned_data)
    integrated_data = self._integration(transformed_data)
    return integrated_data

  def prep_visualization(self, data: pd.DataFrame) -> str:
    # the dataframe needs these features/cols: timestamp, longitude, latitude, altitude, roll, pitch, heading
    length = data.shape[0]
    nav_czml_writer = NavCzmlWriter(length)
    nav_czml_writer.set_with_df(data)
    nav_czml_str = nav_czml_writer.get_czml_string()
    return nav_czml_str


  # data preprocessing steps

  def _cleaning(self, data: np.array) -> pd.DataFrame:
    col_index_map = self._get_col_index_map()
    data = deepcopy(data)

    # data extraction
    # scrape necessary data columns 
    time = data[:, col_index_map["time"]]
    latitude = data[:, col_index_map["latitude"]]
    longitude = data[:, col_index_map["longitude"]]
    altitude = data[:, col_index_map["altitude"]]
    heading = data[:, col_index_map["heading"]] * np.pi / 180. - np.pi / 2.
    pitch = data[:, col_index_map["pitch"]] * np.pi / 180.
    roll = data[:, col_index_map["roll"]] * np.pi / 180.
    
    # data masks
    # remove nan values
    mask = np.logical_not(np.isnan(latitude))
    mask = np.logical_and(mask, np.logical_not(np.isnan(longitude)))
    mask = np.logical_and(mask, np.logical_not(np.isnan(altitude)))
    mask = np.logical_and(mask, np.logical_not(np.isnan(heading)))
    mask = np.logical_and(mask, np.logical_not(np.isnan(pitch)))
    mask = np.logical_and(mask, np.logical_not(np.isnan(roll)))
    
    # remove duplicate time values
    _, unique_idx = np.unique(time, return_index=True)
    unique = np.copy(mask)
    unique[:] = False
    unique[unique_idx] = True
    mask = np.logical_and(mask, unique)
    
    # apply masks/filter and sample data
    f_time = time[mask].astype('datetime64[s]')[::5]
    f_latitude = latitude[mask][::5]
    f_longitude = longitude[mask][::5]
    f_altitude = altitude[mask][::5]
    f_heading = heading[mask][::5]
    f_pitch = pitch[mask][::5]
    f_roll = roll[mask][::5]

    filtered_data = pd.DataFrame(data = {"timestamp": f_time, "latitude": f_latitude, "longitude": f_longitude, "altitude": f_altitude, "heading": f_heading, "pitch": f_pitch, "roll": f_roll})
    return filtered_data
  
  def _transformation(self, data: pd.DataFrame) -> pd.DataFrame:
    #  no transformation needed
    return data
  
  def _integration(self, data: pd.DataFrame) -> pd.DataFrame:
    # no integration needed
    return data


  # ingestion variations

  def _ingest_from_s3(self, url: str) -> np.array:
    s3_client = boto3.client('s3')
    [bucket_name, objectKey] = self._get_s3_details(url)
    s3_file = s3_client.get_object(Bucket=bucket_name, Key=objectKey)

    file = s3_file['Body'].iter_lines()

    data = self._generator_to_np(file)
    return data

  def _ingest_from_local(self, path: str) -> np.array:
    data = self._generator_to_np(path)
    return data


  # utils

  def _get_s3_details(self, url) -> list:
    url = url.replace("s3://", "")
    temp_url = url.split("/")
    bucket_name = temp_url[0]
    
    temp_url = url.split(bucket_name+"/")
    objectKey = temp_url[1]  # key should not start with /
    return [bucket_name, objectKey]
  
  def _get_col_index_map(self):
    # represents the column number for each key, inside the input csv type file.
    return {
        "time": 1,
        "latitude": 2,
        "longitude": 3,
        "altitude": 4,
        "heading": 14,
        "pitch": 16,
        "roll": 17
    }
    
  def _generator_to_np(self, infile: Generator) -> np.array:
    # As the data in txt is all string, to put it inside numpy array, we need to convert it to appropirate types
    
    # create null converters
    converters = {}
    for i in range(33): # 33 cols/feature data
      converters[i] = lambda _: np.nan 
    
    # upadate converters for appropriate faeture/cols with appropriate functions
    col_index_map = self._get_col_index_map()
    converters[col_index_map["time"]] = lambda x: np.datetime64(x, 's').astype(np.int64)
    converters[col_index_map["latitude"]] = self._string_to_float
    converters[col_index_map["longitude"]] = self._string_to_float
    converters[col_index_map["altitude"]] = self._string_to_float
    converters[col_index_map["heading"]] = self._string_to_float
    converters[col_index_map["pitch"]] = self._string_to_float
    converters[col_index_map["roll"]] = self._string_to_float
    
    # apply converter during txt load
    return np.loadtxt(infile, delimiter=',', converters=converters)
  
  def _string_to_float(self, str: str) -> np.float64:
        value = np.nan
        try:
            value = float(str)
        except:
            pass
        return value