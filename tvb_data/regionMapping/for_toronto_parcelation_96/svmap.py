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
.. moduleauthor:: Mihai Andrei <mihai.andrei@codemart.ro>
"""

import numpy as np
import nibabel
from collections import Counter


def load_nii(pth):
    img = nibabel.load(pth)
    h = img.get_header()
    voxels = img.get_data()
    # affine = h.get_base_affine()
    affine = h.get_best_affine()
    return voxels, affine


def load_vertices(pth):
    with open(pth) as f:
        return np.loadtxt(f)


def load_region_id_to_index_map(pth):
    region_id_to_region_idx = {}
    with open(pth) as f:
        for idx, line in enumerate(f):
            rid, name = line.split()
            region_id_to_region_idx[int(rid)] = idx
    return region_id_to_region_idx


def load_region_centers(pth):
    ret = []
    with open(pth) as f:
        next(f)
        for idx, line in enumerate(f):
            name, x, y, z = line.split()
            ret.append((float(x), float(y), float(z)))
    return ret


def _cube_neighborhood(radius=2):
    d = []
    r = range(-radius, radius + 1)
    for i in r:
        for j in r:
            for k in r:
                d.append((i, j, k))
    return d


class Mapper(object):
    """
    maps each vertex of a surface to a region.

    voxels
        Volumetric data mapping a voxel to a region code.
    vertices
        Vertices assumed to be from a surface that is compatible with the
        volume described by voxels
    affine
        affine matrix from voxel index space to 3d
    region_id_to_region_idx
        mapping from region id to idx
    centers
        positions of theregion centers
    """
    def __init__(self, voxels, vertices, affine, region_id_to_region_idx, centers):
        self.voxels = voxels
        self.vertices = vertices
        self.region_id_to_region_idx = region_id_to_region_idx
        self.region_idx_to_region_id = dict((v, k) for k, v in region_id_to_region_idx.iteritems())
        self.centers = centers

        # ajust the affine
        #sx = sy = sz = 0.99
        #ajusting = np.array(
        #    [[sx,  0.0,  0.0,   0.01],
        #     [0.0,  sy,  0.0,   0.0],
        #     [0.0,  0.0,  sz,   0.0],
        #     [0.0,  0.0,  0.0,  1.0]])
        #self.affine = ajusting.dot(affine)
        self.affine = affine
        self.invaffine = np.linalg.inv(self.affine)

    def stats(self):
        print 'vertices shape    : ' + str(self.vertices.shape)
        print 'voxels shape      : ' + str(self.voxels.shape)
        print 'nonzero voxels    : %s' % np.count_nonzero(self.voxels)
        print
        print '==voxels=='
        counts = Counter(self.voxels.flat)
        print 'unique values %s' % len(counts)
        print counts
        print 'voxel positions after affine transform'
        print '000 - %s' % self.affine.dot([0, 0, 0, 1])
        print '111 - %s' % self.affine.dot(list(self.voxels.shape) + [1])
        print
        print '==vertices positions=='
        print 'x y z mins %s' % np.min(self.vertices, axis=0)
        print 'x y z maxs %s' % np.max(self.vertices, axis=0)
        print
        print '==surface bbox min xyz max xyz=='
        print ['%.1f' % q for q in self.bbox_surface()]
        print
        print '==voxel trimmed !=0 planes. Plane indices'
        mins, maxs = self.bbox_voxels()
        print 'min ijk', mins
        print 'max ijk', maxs
        print
        print 'these through the affine'
        print 'min %s' % self.affine.dot(list(mins) + [1])
        print 'max %s' % self.affine.dot(list(maxs) + [1])
        print '==the affine=='
        print self.affine

    def bbox_surface(self):
        minx = miny = minz = 1e10
        maxx = maxy = maxz = -1e10
        for x, y, z in self.vertices:
            minx = min(minx, x)
            maxx = max(maxx, x)
            miny = min(miny, y)
            maxy = max(maxy, y)
            minz = min(minz, z)
            maxz = max(maxz, z)            
        return minx, miny, minz, maxx, maxy, maxz

    def bbox_voxels(self):
        """
        trim 0 planes in index space
        this is less relevant if the affine has a non 90 rotation
        but that is uncommon and this case is easy to implement
        """
        dx, dy, dz = self.voxels.shape
        imin = imax = jmin = jmax = kmin = kmax = None

        for i in xrange(dz):
            if np.count_nonzero(self.voxels[:, :, i]) != 0:
                kmin = i
                break
        for i in xrange(dz):                
            if np.count_nonzero(self.voxels[:, i, :]) != 0:
                jmin = i
                break
        for i in xrange(dz):        
            if np.count_nonzero(self.voxels[i, :, :]) != 0:
                imin = i
                break
        for i in xrange(dz):        
            if np.count_nonzero(self.voxels[:, :, -i - 1]) != 0:
                kmax = dz - i - 1
                break
        for i in xrange(dz):        
            if np.count_nonzero(self.voxels[:, -i - 1, :]) != 0:
                jmax = dy - i - 1
                break
        for i in xrange(dz):        
            if np.count_nonzero(self.voxels[-i - 1, :, :]) != 0:
                imax = dx - i - 1
                break
        return (imin, jmin, kmin), (imax, jmax, kmax)

    def vertices2voxel_indices(self):
        """
        Transforms vertices coordinates from 3d space to voxel index space
        """
        onecolumn = np.ones((self.vertices.shape[0], 1))
        # we add a homogen coord 2 all vertices
        affine_vertices = np.hstack((self.vertices, onecolumn))
        # transform all vertices 2 voxel index space
        # affint.T so that each column is a vertex, then matrix mul will multiply all
        findices = self.invaffine.dot(affine_vertices.T).T
        # to index we need ints
        int_indices = np.round(findices).astype(int)
        #and cut the homog coord
        return int_indices[:, :-1]

    def voxels2vertices(self):
        """
        transforms voxels coordinates from index space to 3d space
        returns pointxyz, voxelvalue
        iteration order is z first then y finally x
        """
        nx, ny, nz = self.voxels.shape
        # is there a simple way to vectorize this?
        # besides constructing a k, j, i matrix ?

        # some optimizations
        affine = self.affine
        voxels = self.voxels
        dots = [0] * nx * ny * nz * 3
        vals = [0] * nx * ny * nz
        idx = 0

        for i in xrange(nx):
            for j in xrange(ny):
                for k in xrange(nz):
                    vox = voxels[i, j, k]
                    if vox:
                        vals[idx] = vox
                        tr = affine.dot([i, j, k, 1])
                        dots[3 * idx] = tr[0]
                        dots[3 * idx + 1] = tr[1]
                        dots[3 * idx + 2] = tr[2]
                        idx += 1

        return dots[:3 * idx], vals[:idx]

    _neigh2 = _cube_neighborhood(radius=2)
    _neigh4 = _cube_neighborhood(radius=4)

    def _sample_neighbourhood(self, neigh, i, j, k):
        """
        what is the most common value at index i,j,k in the given neighborhood
        """
        vals = []

        for di, dj, dk in neigh:
            v = self.voxels[i + di, j + dj, k + dk]
            if v != 0:
                vals.append(v)

        if vals:
            return Counter(vals).most_common()[0][0]
        else:
            return 0

    def _sample_distance2centers(self, vertex):
        """
        what is the value of the closest region center
        """
        vx, vy, vz = vertex

        def dist(c):
            cx, cy, cz = c[1]
            return (cx - vx) ** 2 + (cy - vy) ** 2 + (cz - vz) ** 2

        closest_center = max(enumerate(self.centers), key=dist)
        return self.region_idx_to_region_id[closest_center[0]]

    def mapping(self):
        """
        vertex 2 voxel value
        Vertices that map to 0 are assigend the value of the closest region center
        """
        voxel_indices = self.vertices2voxel_indices()
        vertex_voxel_values = []

        for vertex_id, voxel_idx in enumerate(voxel_indices):
            i, j, k = tuple(voxel_idx)
            v = self.voxels[i, j, k]

            # to see unmapped vertices disable the sampling and
            # in mapping2regionmap assign 0 to a new region
            if v == 0:
                v = self._sample_distance2centers(self.vertices[vertex_id])
            vertex_voxel_values.append(v)

        return vertex_voxel_values

    def heuristic_mapping(self):
        """
        First look at voxels in the neighborhood then fall back to distance to centers
        """
        voxel_indices = self.vertices2voxel_indices()
        vertex_voxel_values = []

        for vertex_id, voxel_idx in enumerate(voxel_indices):
            i, j, k = tuple(voxel_idx)

            # sample for all points
            v = self._sample_neighbourhood(self._neigh2, i, j, k)

            if v == 0:
                v = self._sample_neighbourhood(self._neigh4, i, j, k)
            if v == 0:
                v = self._sample_distance2centers(self.vertices[vertex_id])

            vertex_voxel_values.append(v)

        return vertex_voxel_values

    def mapping2regionmap(self, mapping):
        """
        translate from region id's to indices
        """
        id_to_index = self.region_id_to_region_idx
        ret = []
        for v in mapping:
            ret.append(id_to_index[v])
        return ret

    def evaluate_mapping_correctness(self, region_map):
        c = Counter(region_map)
        mapped2zero = c[0]
        mapped_ok = len(self.vertices) - mapped2zero
        ok_avg = mapped_ok / (len(c) - 1)
        print 'number of regions mapped       : %s' % (len(c) - 1)
        print 'total vertices                 : %s' % len(self.vertices)
        print 'vertices mapped to zero region : %s' % mapped2zero
        print 'average number of vertices '
        print '    per non-zero region        : %s ' % ok_avg
        
        if mapped2zero > 0.20 * ok_avg:
            print 'this looks bad:\n bads are more than 20% of goods'
        print c

        # print non-mapped vertices
        #for i in xrange(len(region_map)):
        #    if region_map[i] == 0:
        #        print "%s " % self.vertices[i]
