import numpy as np
import json
from datetime import datetime, timedelta
from copy import deepcopy

from .czml_model import *

class FlightTrackCzmlWriter:
    
    def __init__(self, length, plane):
        self.model = deepcopy(model)
        if (plane == 'P3B') : self.model['model'] = modelP3B
        if (plane == 'ER2') : self.model['model'] = modelER2
        self.length = length
        self.czml_head = deepcopy(czml_head)
        self.model['name'] = plane
        self.model['path']['material']['solidColor']['color']['rgba'] = TrackColor[plane]
        self.model['position']['cartographicDegrees'] = [0] * 4 * length
        self.model['properties']['roll']['number'] = [0] * 2 * length
        self.model['properties']['pitch']['number'] = [0] * 2 * length
        self.model['properties']['heading']['number'] = [0] * 2 * length

    def set_with_df(self, df):
        self._set_time(df)
        self._set_position(df['lon'], df['lat'], df['alt'])
        self._set_orientation(df['roll'], df['pitch'], df['heading'])

    def _set_time(self, df):
        Cdate=datetime.strptime('2020'+str(df.Jday[0]).zfill(3),"%Y%j")
        time = [ Cdate + timedelta(seconds=s) for s in df.Time_s]
        time_window = [time[0].strftime('%Y-%m-%dT%H:%M:%SZ'), 
                    time[-1].strftime('%Y-%m-%dT%H:%M:%SZ')]
        epoch = time_window[0]
        end = time_window[1]
        self.model['availability'] = "{}/{}".format(epoch, end)
        self.model['position']['epoch'] = epoch
        self.model['position']['cartographicDegrees'][0::4] = df['time_steps']
        self.model['properties']['roll']['epoch'] = epoch
        self.model['properties']['pitch']['epoch'] = epoch
        self.model['properties']['heading']['epoch'] = epoch
        self.model['properties']['roll']['number'][0::2] = df['time_steps']
        self.model['properties']['pitch']['number'][0::2] = df['time_steps']
        self.model['properties']['heading']['number'][0::2] = df['time_steps']

    def _set_position(self, longitude, latitude, altitude):
        self.model['position']['cartographicDegrees'][1::4] = longitude
        self.model['position']['cartographicDegrees'][2::4] = latitude
        self.model['position']['cartographicDegrees'][3::4] = altitude

    def _set_orientation(self, roll, pitch, heading):
        self.model['properties']['roll']['number'][1::2] = roll
        self.model['properties']['pitch']['number'][1::2] = pitch
        self.model['properties']['heading']['number'][1::2] = heading

    def get_czml_string(self):
        return json.dumps([self.czml_head, self.model])
