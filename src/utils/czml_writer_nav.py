import numpy as np
import json

from copy import deepcopy
from .czml_model import model, czml_head

class NavCzmlWriter:
    """
    A class for generating CZML (Cesium Markup Language) data for navigation visualization.

    Args:
        length (int): The length of data points to be generated.
        time_window (tuple): A tuple containing the start and end time of the data.
        time_steps (numpy.ndarray): An array of time steps for the generated data.
        longitude (numpy.ndarray): An array of longitudes for the generated data.
        latitude (numpy.ndarray): An array of latitudes for the generated data.
        altitude (numpy.ndarray): An array of altitudes for the generated data.
        roll (numpy.ndarray): An array of roll values for the generated data.
        pitch (numpy.ndarray): An array of pitch values for the generated data.
        heading (numpy.ndarray): An array of heading values for the generated data.

    Attributes:
        model (dict): A CZML model containing position and orientation data.

    Methods:
        __init__(length, time_window, time_steps, longitude, latitude, altitude, roll, pitch, heading):
            Initializes the NavCzmlWriter instance and sets up the CZML model.
        
        _set_with_df(df):
            Sets the CZML data using a DataFrame containing navigation data.

        _set_time(time_window, time_steps):
            Sets the time-related properties in the CZML model.
        
        _set_position(longitude, latitude, altitude):
            Sets the position-related properties in the CZML model.
        
        _set_orientation(roll, pitch, heading):
            Sets the orientation-related properties in the CZML model.
        
        _get_time_info(time):
            Converts the time data into CZML-compatible time window and time steps.
        
        get_czml_string():
            Returns the CZML data as a JSON string.
    """
    def __init__(self, length, time_window, time_steps, longitude, latitude, altitude, roll, pitch, heading):
    # def __init__(self, length):
        self.model = deepcopy(model)
        self.length = length
        self.model['position']['cartographicDegrees'] = [0] * 4 * length
        self.model['properties']['roll']['number'] = [0] * 2 * length
        self.model['properties']['pitch']['number'] = [0] * 2 * length
        self.model['properties']['heading']['number'] = [0] * 2 * length
        
        self._set_time(time_window, time_steps)
        self._set_position(longitude, latitude, altitude)
        self._set_orientation(roll, pitch, heading)

    def _set_with_df(self, df):
        self._set_time(*self._get_time_info(df['timestamp']))
        self._set_position(df['longitude'], df['latitude'], df['altitude'])
        self._set_orientation(df['roll'], df['pitch'], df['heading'])

    def _set_time(self, time_window, time_steps):
        epoch = time_window[0]
        end = time_window[1]
        self.model['availability'] = "{}/{}".format(epoch, end)
        self.model['position']['epoch'] = epoch
        self.model['position']['cartographicDegrees'][0::4] = time_steps
        self.model['properties']['roll']['epoch'] = epoch
        self.model['properties']['pitch']['epoch'] = epoch
        self.model['properties']['heading']['epoch'] = epoch
        self.model['properties']['roll']['number'][0::2] = time_steps
        self.model['properties']['pitch']['number'][0::2] = time_steps
        self.model['properties']['heading']['number'][0::2] = time_steps

    def _set_position(self, longitude, latitude, altitude):
        self.model['position']['cartographicDegrees'][1::4] = longitude
        self.model['position']['cartographicDegrees'][2::4] = latitude
        self.model['position']['cartographicDegrees'][3::4] = altitude

    def _set_orientation(self, roll, pitch, heading):
        self.model['properties']['roll']['number'][1::2] = roll
        self.model['properties']['pitch']['number'][1::2] = pitch
        self.model['properties']['heading']['number'][1::2] = heading

    def _get_time_info(self, time):
        time_window = time[[0, -1]].astype(np.string_)
        time_window = np.core.defchararray.add(time_window, np.string_('Z'))
        time_window = np.core.defchararray.decode(time_window, 'UTF-8')
        time_steps = (time - time[0]).astype(int)
        return time_window, time_steps

    def get_czml_string(self):
        return json.dumps([czml_head, model])
