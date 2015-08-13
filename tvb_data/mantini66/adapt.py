# -*- coding: utf-8 -*-
#
#
# TheVirtualBrain-Framework Package. This package holds all Data Management, and 
# Web-UI helpful to run brain-simulations. To use it, you also need do download
# TheVirtualBrain-Scientific Package (for simulators). See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2013, Baycrest Centre for Geriatric Care ("Baycrest")
#
# This program is free software; you can redistribute it and/or modify it under 
# the terms of the GNU General Public License version 2 as published by the Free
# Software Foundation. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details. You should have received a copy of the GNU General 
# Public License along with this program; if not, you can download it here
# http://www.gnu.org/licenses/old-licenses/gpl-2.0
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

"""
Adapt mantini signal and other needed data so that it can be viewed by TVB

The 68 connectivity is extended with a 'unmapped' node for unmapped vertices
A region mapping from the 68+1 connectivity to Epfl hi-res surface exists
The 68+1 connectivity uses the region ordering from Hagman 68

Signal 66 nodes, custom region ordering, called `mantini` in this file.
A csv file translates the mantini ordering to Hagman 66
Another from Hagman 66 to Hagman 68.

The Hagman 68 adapted data we can then visualize.

This leaves 2 regions in Hagman 68 with no data.
They are assigned min signal.

.. moduleauthor:: Mihai Andrei <mihai.andrei@codemart.ro>
"""
import numpy
import os.path
import scipy.io
import tvb_data.connectivity.epfl
import tvb_data.regionMapping.epfl_ph0036
from tvb.adapters.uploaders.abcuploader import ABCUploader
from tvb.core.entities.file.files_helper import FilesHelper

CONNECTIVITY_BASE = os.path.dirname(tvb_data.connectivity.epfl.__file__)
REGION_MAP_BASE = os.path.dirname(tvb_data.regionMapping.epfl_ph0036.__file__)


def convert_mat_regionmap_to_txt(dest_pth, pathl, pathr=None):
    """
    Reads a region mapping from a mat array and writes it as a space separated txt file
    The 2 parameter version will concatenate the region mapping data.
    This function expects the data to be compatible with a surface.
    The region indices should be 1-based.
    :param pathl: path to a mat file containing the whole mapping or the mapping for the left hemisphere
    :param pathr: path to a mat file containing the mapping for the right hemisphere
    """
    lh = scipy.io.loadmat(pathl).values()[0]
    if pathr is None:
        data = lh
    else:
        rh = scipy.io.loadmat(pathr).values()[0]
        data = numpy.hstack([numpy.ravel(lh), numpy.ravel(rh)])

    numpy.savetxt(dest_pth, data[None, :], delimiter=' ', fmt='%d')


def introduce_unmapped_node(out_pth, conn_zip_pth):
    """
    Creates a connectivity with one extra node in the first position.
    This node represents the unmapped regions.
    :param out_pth: destination path
    :param conn_zip_pth: connectivity zip path.
    """
    fh = FilesHelper()
    tmp_pth = os.path.splitext(out_pth)[0]
    fh.check_created(tmp_pth)
    files = fh.unpack_zip(conn_zip_pth, tmp_pth)
    for file_name in files:
        file_name_low = file_name.lower()
        if "centres" in file_name_low:
            with open(file_name) as f:
                lines = f.readlines()
            with open(file_name, 'w') as f:
                f.write("None  0.000000  0.000000  0.000000\n")
                f.writelines(lines)
        elif "weight" in file_name_low or "tract" in file_name_low:
            with open(file_name) as f:
                lines = f.readlines()
                nr_regions = len(lines)
            with open(file_name, 'w') as f:
                f.write("   0.0000000e+00" * (nr_regions + 1) + '\n')
                for line in lines:
                    f.write("   0.0000000e+00" + line)
        else:
            raise Exception("this transformation does not support the file " + file_name)

    fh.zip_folder(out_pth, tmp_pth)
    fh.remove_folder(tmp_pth)


def parse_region_correspondence_csv(csv_path, expected_course_len, expected_fine_len, reverse=False):
    """
    Take a region map and add some more regions keeping the others unchanged.
    Then a mapping from the original to the bigger one exists.
    This remains true if you permute the region id's.
    Such a mapping is read from a csv file.
    The reverse mapping does not exists as the new regions do not map to anything.
    :param expected_course_len: the expected len of the destination connectivity.
    :param reverse: If the inverse mapping should be read. Use this if the finer region map is in the 1'st column.
    :returns: a dict from course_region_map_id to fine_region_map_id
    """
    data = numpy.genfromtxt(csv_path, delimiter=',', usecols=(0, 3), skiprows=2)

    d = {}
    for course_idx, fine_idx in data:
        if reverse:
            fine_idx, course_idx = course_idx, fine_idx
        if not numpy.isnan(course_idx):  # missing values are read as nan
            d[int(course_idx)] = int(fine_idx)

    # some checks
    max_region = max(d.keys())

    if max_region != expected_course_len:
        raise ValueError("csv file course connectivity length is %d, expected %d"
                         % (max_region, expected_course_len))

    if len(data) != expected_fine_len:
        raise ValueError("csv file fine connectivity length is %d, expected %d"
                         % (len(data), expected_fine_len))

    return d


def adapt_signal_to_parcelation(signals, correspondence, connectivity_len, fill_missing):
    """
    Adapts a signal to a new connectivity.
    :param signals: the signal to adapt
    :param correspondence: a map from course_region_map_id to fine_region_map
    :return: new signals
    """
    nr_sig, len_sign = signals.shape
    # the new signal has the len of the new connectivity
    len_new_sign = connectivity_len
    new_signals = numpy.ones((nr_sig, len_new_sign))
    new_signals *= fill_missing

    for i in xrange(nr_sig):
        for j in xrange(len_sign):
            # region_index is region_id - 1
            old_region_id = j + 1
            new_region_id = correspondence[old_region_id]
            new_signals[i, new_region_id - 1] = signals[i, j]

    return new_signals


def signal_add_unmapped_node(signals, fill_missing):
    unmapped_col = numpy.ones((len(signals), 1)) * fill_missing
    return numpy.hstack((unmapped_col, signals))


def adapt_66_signal_file_to_68(src_pth, dest_pth, region2region, fill_missing=None):
    signals66 = ABCUploader.read_matlab_data(src_pth, 'M')
    if fill_missing is None:
        fill_missing = numpy.min(signals66)
    signals68 = adapt_signal_to_parcelation(signals66, region2region, 68, fill_missing)
    #introduce zero region in signals
    signals69 = signal_add_unmapped_node(signals68, fill_missing)
    scipy.io.savemat(dest_pth, {'M': signals69})


def compose_mappings(a, b):
    ret = {}
    for k in a:
        ret[k] = b[a[k]]
    return ret


def main():
    print "introducing 0 node in 68 connectivity"

    conn_68 = os.path.join(CONNECTIVITY_BASE, 'low_resolution_parcellation', 'subcortical_false',
                           'epfl_ph0036_hemisphere_both_subcortical_false_regions_68_TVB.zip')

    introduce_unmapped_node('epfl_ph0036_regions_68+1_TVB.zip', conn_68)

    print "convert 68+1 region mapping to txt"

    convert_mat_regionmap_to_txt(
        'region_mapping_ph0036_68+1_TVB.txt',
        os.path.join(REGION_MAP_BASE, 'RegionMapping_PH0036_lh_aparc_68.mat'),
        os.path.join(REGION_MAP_BASE, 'RegionMapping_PH0036_rh_aparc_68.mat')
    )

    print "adapt 66 signals to 68+1"

    mantini66_2_hagman66 = parse_region_correspondence_csv('mantini66_to_hagmann66.csv', 66, 66)
    hagman66_2_hagman68 = parse_region_correspondence_csv('Hagmann68_to_Hagmann66.csv', 66, 68, reverse=True)

    mantini_2_hagman = compose_mappings(mantini66_2_hagman66, hagman66_2_hagman68)
    adapt_66_signal_file_to_68('mantini_networks.mat', 'mantini_networks_adapted_69.mat',
                               mantini_2_hagman, fill_missing=None)

    adapt_66_signal_file_to_68('model_networks.mat', 'model_networks_adapted_69.mat',
                               mantini_2_hagman, fill_missing=None)



if __name__ == '__main__':
    main()