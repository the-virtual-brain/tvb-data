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

#
# This entire folder is now deprecated.
# It will become part of tvb_recon
#

import nibabel
import numpy


def _correct(data, mapping_file, conn_regions):
    assert (len(data.shape) == 3)
    mapping_data = numpy.loadtxt(mapping_file, dtype=numpy.str, usecols=(0, 2))
    mapping_data = {int(row[0]): int(row[1]) for row in mapping_data}

    not_matched = set()
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            for k in range(data.shape[2]):
                val = data[i][j][k]
                if not mapping_data.has_key(val):
                    not_matched.add(val)
                data[i][j][k] = mapping_data.get(val, -1)

    print("Now values are in interval [%d - %d]" % (data.min(), data.max()))
    if not_matched:
        print("Not matched regions will be considered background: %s" % not_matched)

    assert (data.min() >= -1 and data.max() < conn_regions)
    return data


def pre_process(nii_file, mapping_file, conn_regions_no):
    nifti_image = nibabel.load(nii_file)
    nifti_data = nifti_image.get_data()

    corrected_data = _correct(nifti_data, mapping_file, conn_regions_no)

    new_file_name = nii_file.replace(".nii", "-cor.nii")
    new_nifti = nibabel.Nifti1Image(corrected_data, nifti_image.get_affine(), header=nifti_image.get_header())
    nibabel.save(new_nifti, new_file_name)


if __name__ == "__main__":
    in_nii = "aparc+aseg-in-surf.nii.gz"
    in_mapping = "mapping_FS_84.txt"
    pre_process(in_nii, in_mapping, 84)


## Part of the surface
# mri_info --vox2ras $SUBJ_DIR/mri/T1.mgz --o SURFACE/vox2ras.txt
