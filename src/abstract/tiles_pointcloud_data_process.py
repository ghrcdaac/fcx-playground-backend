from abc import abstractmethod
import numpy as np
import pandas as pd

from .data_process import DataProcess

class TilesPointCloudDataProcess(DataProcess):
  @abstractmethod
  def ingest(self, url: str) -> pd.DataFrame:
    print("get raw data from data source. Data source may be any of http or ftp")
    # raw data can be in any file format. eg. txt, nc, uf etc.
    # use appropriate library to read the file and return the data as pandas dataframe
  
  @abstractmethod
  def preprocess(self):
    print("preprocess raw data to be ready for vizualization")
    # pre process of raw data can go through various stages like
    # cleaning: scrape the necessary data columns,
    # transformation: transform the data to a suitable data formatting
    # integration: data from multiple sources can be integrated into intermediate file format, e.g. zarr file. The intermeidate format should be compatible with viz prepration step
    
  @abstractmethod
  def prep_visualization(self):
    print("After preprocessing, prepare tileset.json data to be visualized in Cesium using tileset writer")
    # tileset writer a util class can be used to write tileset json data from zarr file as input