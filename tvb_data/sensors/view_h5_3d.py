import numpy
import h5py
from mayavi import mlab 

"""
View data stored in tvb h5 files directly. 
Used for debugging purposes. It does not use tvb.
"""

def show_sensors(pth, red=None, green=None):
    """ 
    show sensors stored in a h5. 
    :param red: a list of labels to be shown in red    
    """
    if red is None:
        red = []
    if green is None:
        green = []

    mlab.figure()
    sensors = h5py.File(pth)
    d = numpy.array(sensors['locations'])    
    labels = list(sensors['labels'])    
    highlight = numpy.ones(d.shape[0])

    for i, l in enumerate(labels):
        if l in red:
            highlight[i] = 5.0
        elif l in green:
            highlight[i] = 7.0
        else:
            highlight[i] = 2.0    

    mlab.points3d(d[:,0], d[:,1], d[:,2], highlight, scale_mode='none')
    mlab.axes()


def show_surface(pth):
    """
    show surface from a h5
    """
    mlab.figure()
    cap = h5py.File(pth)
    v = numpy.array(cap['vertices'])
    t = numpy.array(cap['triangles'])

    mlab.triangular_mesh(v[:,0], v[:,1], v[:,2], t)
    mlab.axes()


def _rotate_eeg_sensors(pth):
    """ rotate a eeg sensor from a h5 by -90 along +z. results to stdout """
    rot = numpy.array([[ 0, 1, 0], 
                       [-1, 0, 0], 
                       [ 0, 0, 1]])

    sensors = h5py.File(pth)
    d = numpy.array(sensors['locations'])
    d = rot.dot(d.T).T    
    
    for i, l in enumerate(sensors['labels']):
        print "%-4s % .16f  % .16f  % .16f" % (l, d[i][0], d[i][1], d[i][2])


import os.path
proj_pth = os.path.expanduser('~/TVB/PROJECTS/Default_Project_admin/')
#show_sensors(proj_pth + sensors_pth, red=['Fp1','Fp2'], green=['POz', 'O1', 'O2'])
mlab.show()
