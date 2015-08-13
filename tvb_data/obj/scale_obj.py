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
This script takes a file named: face_surface_original.obj as input,
and generated another one named: face_surface.obj,
after applying a rotation and a translation on the vertices in the input file.

The rotation and translation is hard-coded here, and found from visual inspection,
to align the face with the cortical surface of TVB.

.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""

import math
import numpy as np


def scaling_matrix(a, b, c):
    return np.array([[ a, 0, 0],
                     [ 0, b, 0],
                     [ 0, 0, c]])


def rotation_matrix(axis, theta):
    axis = np.array(axis)
    axis /= math.sqrt(np.dot(axis, axis))
    a = math.cos(theta / 2)
    b, c, d = -axis * math.sin(theta / 2)
    return np.array([[a * a + b * b - c * c - d * d, 2 * (b * c - a * d), 2 * (b * d + a * c)],
                     [2 * (b * c + a * d), a * a + c * c - b * b - d * d, 2 * (c * d - a * b)],
                     [2 * (b * d - a * c), 2 * (c * d + a * b), a * a + d * d - b * b - c * c]])


def vertex_transform1(vertex):
    """
    This transform was applied on the original surface.
    """
    return np.dot(rotation_matrix(np.array([0.0, 0.0, 1.0]), math.pi),
                  np.dot(rotation_matrix(np.array([1.0, 0.0, 0.0]), -math.pi / 1.6),
                         np.array([float(x) / 1.5 for x in vertex[:3]]) + np.array([0.0, -40.0, 20.0])))


def vertex_transform2(vertex):
    """
    This transform was applied on the surface created by `vertex_transform1`.
    This was required by TVB-1397: eliminating special transformation of faces by the viewer.
    """
    vertex = [float(x) for x in vertex[:3]]
    rotation = rotation_matrix([0.0, 0.0, 1.0], math.pi)

    return rotation.dot(np.array(vertex[:3]) * 1.08 + np.array([1.0, 2.0, -10.0]))


def vertex_transform3(vertex):
    """
    After recent changes in the received OBJ files (28 Nov 2014),
    we need to rotate with 92 degrees and do a small translation for  good match with the default cortex.
    """
    vertex = np.array([float(x) * 10 for x in vertex[:3]]) + np.array([0.0, -60.0, 30.0])
    rotation = rotation_matrix([1.0, 0.0, 0.0], - math.pi / 1.8)
    return np.dot(rotation, vertex)



if __name__ == "__main__":

    for name in ["eeg_cap", "face_surface"]:
        with open("%s_original.obj" % name) as obj_file:
            with open("%s.obj" % name, "w") as result_file:

                for line_nr, line in enumerate(obj_file):
                    line = line.strip()

                    if line == "" or line[0] == '#':
                        result_file.write(line + "\n")
                        continue

                    tokens = line.split()
                    line_type = tokens[0]

                    if line_type != "v":
                        result_file.write(line + "\n")
                        continue

                    new_vertex = vertex_transform3(tokens[1:])
                    result_file.write("v %f %f %f \n" % tuple(new_vertex.tolist()))


