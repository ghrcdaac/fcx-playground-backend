from abc import abstractmethod
import numpy as np
import pandas as pd

from .data_process import DataProcess

class CZMLDataProcess(DataProcess):
  @abstractmethod
  def ingest(self, url: str) -> np.array:
    # print("get raw data from data source. Data source may be any of http or ftp")
    # raw data can be in any file format. eg. txt, nc, uf etc.
    # use appropriate library to read the file and return the data as numpy arrays
    pass

  @abstractmethod
  def preprocess(self) -> pd.DataFrame:
    # print("preprocess raw data to be ready for vizualization")
    # pre process of raw data can go through various stages like
    # cleaning: scrape the necessary data columns,
    # transformation: transform the data to a suitable data formatting
    # integration: data from multiple sources can be integrated into intermediate format, e.g. numpy arrays. The intermeidate format should be compatible with viz prepration step
    pass
    
  @abstractmethod
  def prep_visualization(self) -> str:
    # print("After preprocessing, prepare czml data to be visualized in Cesium using CZML writer")
    # czml writer a util class can be used to write czml data from numpy arrays as input
    pass