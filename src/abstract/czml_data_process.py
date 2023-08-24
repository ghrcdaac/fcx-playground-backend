from abc import abstractmethod
from typing import string, Array
import numpy as np

from data_process import DataProcess

class CZMLDataProcess(DataProcess):
  @abstractmethod
  def ingest(self, url: string) -> Array[np.array]:
    print("get czml data from data source. Data source may be any of http or ftp")
    # czml data can be in any file format. eg. txt, nc, uf etc.
    # use appropriate library to read the file and return the data as numpy arrays
  
  @abstractmethod
  def preprocess(self):
    print("preprocess czml data to be ready for vizualization")
    # pre process of czml can go through various stages like
    # cleaning: scrape the necessary data columns, 
    # integration: data from multiple sources can be integrated into intermediate format, e.g. numpy arrays. The intermeidate format should be compatible with viz prepration step
    
  @abstractmethod
  def prep_visualization(self):
    print("After preprocessing, prepare czml data to be visualized in Cesium using CZML writer")
    # czml writer a util class can be used to write czml data from numpy arrays as input