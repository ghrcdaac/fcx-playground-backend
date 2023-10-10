import numpy as np
import pandas as pd
import glob
import h5py
from datetime import datetime

from abstract.tiles_pointcloud_data_process import TilesPointCloudDataProcess
from utils.tiles_writer import *
from utils.tiles_point_cloud import *

class RadRangeTilesPointCloudDataProcess(TilesPointCloudDataProcess):
  def __init__(self):
    self.Bands = 'W'
    self.Vars = ['dBZe','Vel']
    self.fdate = '2020-02-27'
    self.outDir0 = '/Users/Indhuja/Documents/IMPACTS_CRS/'
    self.tInstr = {'2020-02-27':'T07:43:30Z'}
  
  def ingest(self):
    #replace this with the correct .h5 file path 
    infile = glob.glob('../../IMPACTS_CRS_*.h5')[0]
    return infile
  
  def preprocess(self, infile):
    cleaned_data, ncol, nrow, rad_range, data = self._cleaning(infile)
    transformed_data = self._transformation(cleaned_data, ncol, nrow, rad_range)
    integrated_data = self._integration(transformed_data, data)
    return cleaned_data, transformed_data, integrated_data

  def prep_visualization(self, RADs) -> str:  #RADs = integrated_data
    for bandSel in self.Bands:
        print('\n*Processing data for band:',bandSel)
        
        RAD = RADs[bandSel]

        #----------Make pointcloud ----------
        # Cesium use Epoch time (secs since 1970) for visualization
        #        use seconds relative to the Epoch time within a module/tile
        #-------------------------------

        #----Set time, range, steps in pointcloud tileset
        t1970 = datetime(1970,1,1)
        t0 = datetime.strptime(self.fdate,"%Y-%m-%d")
        tFlight = datetime.strptime(self.fdate + self.tInstr[self.fdate], "%Y-%m-%dT%H:%M:%SZ")

        SecS = (tFlight - t1970).total_seconds()  #to be consistent with across all ER-2 measurements, 
        #SecS = RAD['Time'].min()                   #use RAD['Time'].min() for stand-alone
        SecE = RAD['Time'].max()
        RAD['timeP'] = RAD['Time'] - SecS         #time is counted from SecS in visualization

        lonw, lone = RAD['lon'].min()-0.2, RAD['lon'].max()+0.2
        lats, latn = RAD['lat'].min()-0.2, RAD['lat'].max()+0.2
        altb, altu = RAD['alt'].min(),RAD['alt'].max()
        bigbox = [lonw, lats, lone, latn, altb, altu] #*to_rad

        nPoints = len(RAD)
        Tsize = 500000
        nTile = nPoints//Tsize
        print(nPoints, nTile)
        if(nPoints%Tsize > 0): nTile += 1
        print(' Valid data points:',nPoints)
        for vname in self.Vars:
            print(' -Making pointcloud tileset for',vname)
            folder= self.outDir0+ '/'+bandSel+'_'+vname
            mkfolder(folder)

            tileset = Tileset(bandSel+'_'+vname, bigbox, SecS)

            for tile in range (nTile):
                if(tile ==0):
                    epoch = SecS         #--epoch and end are seconds from (1970,1,1)
                else:
                    epoch =  RAD['Time'][tile*Tsize]   #SecS + tile*Tsize
                end = RAD['Time'][min((tile+1)*Tsize, nPoints-1)]
                #subset of rows whose time>epoch and time<end
                subset = RAD[(RAD['Time'] >= epoch) & (RAD['Time'] < end)]
                make_pcloudTile(vname, tile, tileset, subset, epoch, end, folder)

  # data preprocessing steps

  def _cleaning(self, Hfile):
    with h5py.File(Hfile, 'r') as fh5:
        nav = fh5['Navigation/Data']
        Tepoch = fh5['Time/Data/TimeUTC'][()]
        rad_range = fh5['Products/Information/Range'][()]
        rad_range = rad_range.reshape(rad_range.size)
        lat, lon, alt = nav['Latitude'][()], nav['Longitude'][()], nav['Height'][()]
        roll, pitch, head = nav['Roll'][()], nav['Pitch'][()], nav['Heading'][()]
        band = fh5['Products/Data']
        data={'W':{'dBZe': band['dBZe'][()],
                    'LDR': band['LDR'][()],
                    'Vel': band['Velocity_corrected'][()],
                    'spW': band['SpectrumWidth'][()]  } }
        ncol = Tepoch.size
        nrow = rad_range.size
        df = pd.DataFrame(data = {
            'time': Tepoch,
            'lon': lon,
            'lat': lat,
            'alt': alt,
            'roll': roll,
            'pitch': pitch,
            'head': head,
        })
    return df, ncol, nrow, rad_range, data

  def _transformation(self, data, ncol, nrow, rad_range) -> pd.DataFrame:
    #---Track data
    RAD0 = pd.DataFrame()
    RAD0['Time'] = np.repeat(data['time'], nrow) # Use Epoch time (seconds since 1970)
    RAD0['Lon'] = np.repeat(data['lon'], nrow)
    RAD0['Lat'] = np.repeat(data['lat'], nrow)
    RAD0['Alt'] = np.repeat(data['alt'], nrow)
    RAD0['roll'] = np.repeat(data['roll'] * to_rad, nrow)
    RAD0['pitch'] = np.repeat(data['pitch'] * to_rad, nrow)
    RAD0['head'] = np.repeat(data['head'] * to_rad, nrow)
    RAD0['Zdist'] = np.tile(rad_range, ncol)

    RAD0['lon'], RAD0['lat'], RAD0['alt'] = proj_LatLonAlt(RAD0)

    RAD0 = RAD0.drop(['roll','pitch','head','Zdist','Lon','Lat','Alt'], axis=1 )
                  
    return RAD0
  
  def _integration(self, RAD0, data) -> str:
    #---Product data
    RADs={}
    bandSel = 'W'
    Vars = ['dBZe','Vel']
    print('\n*Processing data for band:',bandSel)

    RAD = RAD0.copy()
    for vname in Vars: RAD[vname] = data[bandSel][vname].flatten()

    #---initial clean up and processing
    print(' Original data points:',len(RAD))
    RAD.dropna(subset=Vars, how='all', inplace=True)
    RAD = RAD.fillna(-999)
    RAD = RAD[(RAD['alt'] >= 0) & (RAD['alt'] <= 18000)] #<--mid_lat winter storm (12000 would do)
    RAD = RAD.reset_index(drop=True)
    print(' In range data points:',len(RAD))
    RADs[bandSel] = RAD      
    return RADs
