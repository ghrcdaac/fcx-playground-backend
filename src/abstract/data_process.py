# abc: abstract base class
from abc import ABC, abstractmethod

class DataProcess(ABC):
  
  @abstractmethod
  def ingest(self):
    print('get data from various sources to be preprocessed and visualized in Cesium')
    pass
  
  @abstractmethod
  def preprocess(self):
    print('with the data, preprocess it to be ready for vizualization')
    print('can go through multiple steps of preprocessing like cleaning, transformation, integration.')
    pass
  
  @abstractmethod
  def prep_visualizion(self):
    print('After preprocessing, prepare data to be visualized in Cesium')
    pass