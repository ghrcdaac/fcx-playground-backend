import os
import numpy as np
from datetime import datetime

to_rad = np.pi / 180.0
to_deg = 180.0 / np.pi

def down_vector(roll, pitch, head):
    x = np.sin(roll) * np.cos(head) + np.cos(roll) * np.sin(pitch) * np.sin(head)
    y = -np.sin(roll) * np.sin(head) + np.cos(roll) * np.sin(pitch) * np.cos(head)
    z = -np.cos(roll) * np.cos(pitch)
    return (x, y, z)

def proj_LatLonAlt(DF):
    """Zdist is distance from Aircraft"""
    
    x, y, z = down_vector(DF['roll'], DF['pitch'], DF['head'])
    x = np.multiply(x, np.divide(DF['Zdist'], 111000 * np.cos(DF['Lat'] * to_rad)))
    y = np.multiply(y, np.divide(DF['Zdist'], 111000))
    z = np.multiply(z, DF['Zdist'])

    lon = np.add(-x, DF['Lon'])
    lat = np.add(-y, DF['Lat'])
    alt = np.add(z,  DF['Alt'])
    return lon,lat,alt

def mkfolder(folder):
    if(not os.path.exists(folder)): 
        try:
            os.makedirs(folder)
            print('Success to create folder %s' % folder)    
        except OSError:
            print('Failed to create folder %s' % folder)
            quit()
    else:
        print('%s already exists' % folder)

def sec2Z(t): 
    return "{}Z".format(datetime.utcfromtimestamp(t).isoformat())