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

"""

.. moduleauthor:: Mihai Andrei <mihai.andrei@codemart.ro>


This script maps each vertex of a surface to a region.

"""

from tvb_data.regionMapping.for_toronto_parcelation_96.svmap import load_nii, load_region_id_to_index_map
from tvb_data.regionMapping.for_toronto_parcelation_96.svmap import load_region_centers, load_vertices, Mapper


def view_sections(voxels, x, y, z):
    import matplotlib.pyplot as plt

    plt.figure()
    plt.title('voxels[:, :, %d]' % z)
    plt.imshow(voxels[:, :, z], origin="lower")
    plt.figure()
    plt.title('voxels[:, %d, :]' % y)
    plt.imshow(voxels[:, y, :], origin="lower")
    plt.figure()
    plt.title('voxels[%d, :, :]' % x)
    plt.imshow(voxels[x, :, :], origin="lower")
    plt.show()


def _write_file(pth, seq, sep=' '):
    with open(pth, 'w') as f:
        for v in seq:
            f.write('{0}{1}'.format(v, sep))


def save_data_for_viewer(m):
    """to be viewed by webgl"""
    raw_mapping = m.mapping()
    dots, vox = m.voxels2vertices()

    with open('viewerdata/nii_points.txt', 'w') as f:
        for i in range(0, len(dots), 3):
            f.write(' '.join(str(v) for v in dots[i: i + 3]))
            f.write('\n')

    _write_file('viewerdata/nii_raw_voxels.txt', vox, sep='\n')
    _write_file('viewerdata/nii_raw_mapping_distc.txt', raw_mapping)


def write_regionmap(m, pth):
    raw_mapping = m.mapping()
    m.evaluate_mapping_correctness(raw_mapping)
    _write_file(pth, m.mapping2regionmap(raw_mapping))


def write_heuristic_map(m, pth):
    raw_mapping = m.heuristic_mapping()
    m.evaluate_mapping_correctness(raw_mapping)
    _write_file(pth, m.mapping2regionmap(raw_mapping))


VOXELS_PTH = '_rm+thal&bg_1mm_20111013_uint8.nii'
VERTICES_PTH = '_surface_80k_vertices.txt'
REGION_ID2IDX_PTH = '_connectivity_96_to_pipeline_idx.txt'
REGION_CENTERS = '_connectivity_96_positions.txt'


def main():
    voxels, affine = load_nii(VOXELS_PTH)
    vertices = load_vertices(VERTICES_PTH)
    region_id_to_idx = load_region_id_to_index_map(REGION_ID2IDX_PTH)
    centers = load_region_centers(REGION_CENTERS)
    m = Mapper(voxels, vertices, affine, region_id_to_idx, centers)
    #m.stats()
    write_regionmap(m, 'connectivity96_to_srf80k_map.txt')
    #write_heuristic_map(m, '96connectivity_to_srf_80k_heuristic_map.txt')


if __name__ == '__main__':
    main()
