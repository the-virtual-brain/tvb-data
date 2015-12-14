#!/usr/bin/env python

"""

Script for converting a Volume Mapping in Nifti format with indices values in FSL atlas,
into TVB connectivity indices space (Cocomac derived).

File 'mapping.txt' has been produced manually (as a temporary solution) to have some base for the mapping.

"""

import numpy
import nibabel

src = nibabel.load('aparc+aseg.nii.gz')
src_data = src.get_data()

map = numpy.loadtxt('mapping.txt', dtype=numpy.str, usecols=(0, 2))
map = {int(row[0]): int(row[1]) for row in map}

for i in xrange(src_data.shape[0]):
    for j in xrange(src_data.shape[1]):
        for k in xrange(src_data.shape[2]):
            val = src_data[i][j][k]
            src_data[i][j][k] = map.get(val, -1)

print src_data.min(), src_data.max()
dst = nibabel.Nifti1Image(src_data, src.get_affine(), src.get_header())
nibabel.save(dst, 'tvb_ready.nii.gz')
