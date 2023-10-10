import numpy as np
import pandas as pd
import glob

from abstract.czml_data_process import CZMLDataProcess
from utils.czml_writer_nav import FlightTrackCzmlWriter

class NavCZMLDataProcess(CZMLDataProcess):
  def __init__(self):    
    pass
  
  def ingest(self):
    #replace this with the correct .ict file path 
    infile = glob.glob('../../IMPACTS_MetNav_P3B_20220203_R0.ict')[0]
    return infile
  
  def preprocess(self, data) -> pd.DataFrame:
    cleaned_data = self._cleaning(data, 'P3B')
    transformed_data = self._transformation(cleaned_data)
    integrated_data = self._integration(transformed_data)
    return integrated_data

  def prep_visualization(self, data: pd.DataFrame) -> str:
    # the dataframe needs these features/cols: timestamp, longitude, latitude, altitude, roll, pitch, heading
    length = len(data)
    nav_czml_writer = FlightTrackCzmlWriter(length, 'P3B')
    nav_czml_writer.set_with_df(data)
    nav_czml_str = nav_czml_writer.get_czml_string()
    return nav_czml_str


  # data preprocessing steps

  def _cleaning(self, file, plane, nskip=1) -> pd.DataFrame:
    if (plane=='ER2'): cols=[0,1,2,3,4,10,13,14]
    if (plane=='P3B'): cols=[0,1,2,3,4,12,15,16]
    with open(file) as f:
            lines = f.readlines()
            for il,line in enumerate(lines):
                if('Time_Start,Day_Of_Year,' in line):
                    break
    self.infile = file
    self.hlines = il
    self.useCols = cols
    self.plane = plane
    
    df = pd.read_csv(file,index_col=None,usecols=self.useCols, skiprows=self.hlines)
    df.columns = ['Time_s','Jday', 'lat','lon','alt','heading','pitch','roll']
    headingCorrection = -90 # for both p3B and ER2 model
    pitchCorrection = 0 # initial value
    if (self.plane == 'P3B'):
        pitchCorrection = +90 # pitch correction only for P3B model
    df['heading'] = [ h if h<=180 else h-360 for h in df.heading]
    df['heading'] = [ (h+headingCorrection) * np.pi / 180. for h in df.heading]
    df['pitch'] = [ (p+pitchCorrection) * np.pi / 180. for p in df.pitch]
    df['roll'] = [ r * np.pi / 180. for r in df.roll]
    df['time_steps'] = [(t - df.Time_s[0]) for t in df.Time_s]
          
    df = df[df['Time_s']%(nskip+1) == 0]  #keep every nskip+1 s
    df = df.reset_index(drop=True)
          
    return df
  
  def _transformation(self, data: pd.DataFrame) -> pd.DataFrame:
    #  no transformation needed
    return data
  
  def _integration(self, data: pd.DataFrame) -> pd.DataFrame:
    # no integration needed
    return data