# -*- coding: utf-8 -*-
#
#
# TheVirtualBrain-Framework Package. This package holds all Data Management, and 
# Web-UI helpful to run brain-simulations. To use it, you also need do download
# TheVirtualBrain-Scientific Package (for simulators). See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2017, Baycrest Centre for Geriatric Care ("Baycrest") and others
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.
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

import numpy
import nibabel as nib


def alter_tracts_and_weights():
    tract_lengths = numpy.loadtxt("Connectivity/tract_lengths.txt")
    weights = numpy.loadtxt("Connectivity/weights.txt")

    # add row of 0's at index 83
    tract_lengths = numpy.vstack((tract_lengths, numpy.zeros((1, 82))))
    weights = numpy.vstack((weights, numpy.zeros((1, 82))))

    # add row of 0's at index 41
    tract_lengths = numpy.vstack((tract_lengths[:41, ], numpy.zeros((1, 82)), tract_lengths[41:, ]))
    weights = numpy.vstack((weights[:41, ], numpy.zeros((1, 82)), weights[41:, ]))

    # add column of 0's at index 83
    tract_lengths = numpy.hstack((tract_lengths, numpy.zeros((84, 1))))
    weights = numpy.hstack((weights, numpy.zeros((84, 1))))

    # add column of 0's at index 41
    tract_lengths = numpy.hstack((tract_lengths[:, :41], numpy.zeros((84, 1)), tract_lengths[:, 41:]))
    weights = numpy.hstack((weights[:, :41], numpy.zeros((84, 1)), weights[:, 41:]))

    return tract_lengths, weights


def prepare_rm():
    original_rm = numpy.loadtxt("RM/surf_labels.txt")
    labels_map = numpy.loadtxt("RM/TVBmacaque_RM_LUT.txt", skiprows=1, usecols=[0], dtype=numpy.int)
    labels_text = numpy.loadtxt("RM/TVBmacaque_RM_LUT.txt", skiprows=1, usecols=[1], dtype=numpy.str)
    vertices_x = numpy.loadtxt("Surface/vertices.txt", usecols=[0], dtype=numpy.float)

    reverted_map = dict()
    for i in range(labels_map.size):
        reverted_map[labels_map[i]] = i
    print(reverted_map)

    n_surface = original_rm.size
    print(n_surface, original_rm.shape)
    print(numpy.count_nonzero(original_rm < 2))

    # values that don't belong to any region will be assigned to the unknown regions
    final_rm = []
    for i in range(n_surface):
        if int(original_rm[i]) in reverted_map:
            final_rm.append(reverted_map[int(original_rm[i])])
        else:
            # if the Y coordinate of the vertex is positive, we will assign it to the unknown right region, otherwise to the left one
            if (vertices_x[i] > 0):
                final_rm.append(41)
            else:
                final_rm.append(83)

    print(numpy.min(final_rm), numpy.max(final_rm))
    final_rm = numpy.array(final_rm, dtype=numpy.int)
    numpy.savetxt("RM/regionMapping_147k_84.txt", final_rm)

    maps = []
    for i in range(labels_map.size):
        maps.append((labels_map[i], labels_text[i], i))
    maps = numpy.array(maps, dtype=numpy.str)
    numpy.savetxt("mapping_FS_84.txt", maps, delimiter=" ", fmt="%s")

    # alter and save weights and tract_lengths adjacency matrices
    tract_lengths, weights = alter_tracts_and_weights()
    numpy.savetxt("tract_lengths_new.txt", tract_lengths, delimiter=" ")
    numpy.savetxt("weights_new.txt", weights, delimiter=" ")


if __name__ == "__main__":
    prepare_rm()
