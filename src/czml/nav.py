from typing import string, Array
import boto3
from copy import deepcopy
import numpy as np
import pandas as pd
from abstract.czml_data_process import CZMLDataProcess
from utils.czml_writer_nav import NavCzmlWriter

class NavCZMLDataProcess(CZMLDataProcess):
  def ingest(self, url: string) -> Array[np.array]:
    super().ingest()
    s3_client = boto3.client('s3')
    [bucket_name, objectKey] = self._get_s3_details(url)
    s3_file = s3_client.get_object(Bucket=bucket_name, Key=objectKey)

    file = s3_file['Body'].iter_lines()
    data = np.loadtxt(file, delimiter=',', converters=self.converters)
    return data
  
  def preprocess(self, data: Array[np.array]) -> pd.DataFrame:
    super().preprocess()
    cleaned_data = self._cleaning(data)
    transformed_data = self._transformation(cleaned_data)
    integrated_data = self._integration(transformed_data)
    return integrated_data

  def prep_visualization(self, data: pd.DataFrame) -> string:
    super().prep_visualization()
    nav_czml_writer = NavCzmlWriter(data["length"], data["time_window"], data["time_steps"], data["longitude"], data["latitude"], data["altitude"], data["roll"], data["pitch"], data["heading"])
    nav_czml_str = nav_czml_writer.get_czml_string()
    return nav_czml_str


  # data preprocessing steps

  def _cleaning(self, data: Array[np.array]) -> Array[np.array]:
    col_index_map = self._get_col_index_map()
    data = deepcopy(data)

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
    
    # apply masks
    time = time[mask].astype('datetime64[s]')
    time_window = time[[0, -1]].astype(np.string_)
    time_window = np.core.defchararray.add(time_window, np.string_('Z'))
    
    f_time_window = np.core.defchararray.decode(time_window, 'UTF-8')
    f_time_steps = (time - time[0]).astype(int).tolist()[::5]
    f_latitude = latitude[mask][::5]
    f_longitude = longitude[mask][::5]
    f_altitude = altitude[mask][::5]
    f_heading = heading[mask][::5]
    f_pitch = pitch[mask][::5]
    f_roll = roll[mask][::5]
    f_length = mask[mask][::5].size
    
    return np.hstack((f_time_window, f_time_steps, f_latitude, f_longitude, f_altitude, f_heading, f_pitch, f_roll, f_length))
  
  def _transformation(self, data: Array[np.array]) -> Array[np.array]:
    #  no transformation needed
    return data
  
  def _integration(self, data: Array[np.array]) -> pd.DataFrame:
    # use data and create a dataframe
    return pd.DataFrame(data=data, columns= ["time_window", "time_steps", "latitude", "longitude", "altitude", "heading", "pitch", "roll", "length"])

  # utils

  def _get_s3_details(url):
    url = url.replace("s3://", "")
    url = url.split("/")
    bucket_name = url[0]
    objectKey = url[1]
    return [bucket_name, objectKey]
  
  def _get_col_index_map():
    return {
        "time": 1,
        "latitude": 2,
        "longitude": 3,
        "altitude": 4,
        "heading": 14,
        "pitch": 16,
        "roll": 17
    }