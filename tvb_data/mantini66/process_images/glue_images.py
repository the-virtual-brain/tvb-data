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

import Image

WIDTH = 1550
HEIGHT = 985
GLUE_DEFINITION = [{"suffix": "RI", "position": (0, 0)},
                   {"suffix": "LI", "position": (WIDTH, 0)},
                   {"suffix": "RO", "position": (0, HEIGHT)},
                   {"suffix": "LO", "position": (WIDTH, HEIGHT)}]
BRANDING_BAR_PATH = "../framework_tvb/tvb/core/services/resources/branding_bar.png"



def glue_4_images(path_prefix):

    final_image = Image.new("RGBA", (2 * WIDTH, 2 * HEIGHT))

    for i in xrange(4):
        image_path = path_prefix + "_" + GLUE_DEFINITION[i]["suffix"] + ".png"
        img = Image.open(image_path)
        final_image.paste(img, GLUE_DEFINITION[i]["position"], img)

    branding_bar = Image.open(BRANDING_BAR_PATH)
    final_image.paste(branding_bar, (0, final_image.size[1] - branding_bar.size[1]), branding_bar)

    final_path = path_prefix + ".png"
    final_path = final_path.replace("ExportedRaw", "Glued")
    final_image.save(final_path, "PNG")

    print "Saved image:", final_path



def glue_6_images(path_prefix):

    final_image = Image.new("RGBA", (2 * WIDTH, 12 * HEIGHT))

    for i in range(1, 7):
        image_path = path_prefix + str(i) + ".png"
        img = Image.open(image_path)
        final_image.paste(img, (0, (i - 1) * 2 * HEIGHT), img)

    branding_bar = Image.open(BRANDING_BAR_PATH)
    final_image.paste(branding_bar, (0, final_image.size[1] - branding_bar.size[1]), branding_bar)

    final_path = path_prefix + "Group.png"
    final_image.save(final_path, "PNG")

    print "Saved image:", final_path


def glue_2_images(image1, image2, final_path):

    final_image = Image.new("RGB", (4 * WIDTH, 12 * HEIGHT))

    img = Image.open(image1)
    final_image.paste(img, (0, 0), img)
    img = Image.open(image2)
    final_image.paste(img, (2 * WIDTH, 0), img)

    branding_bar = Image.open(BRANDING_BAR_PATH)
    final_image.paste(branding_bar, (0, final_image.size[1] - branding_bar.size[1]), branding_bar)

    final_image.save(final_path, "PNG")
    print "Saved image:", final_path


if __name__ == "__main__":

    for i in range(1, 7):
        glue_4_images("/Users/lia.domide/Downloads/Mantini/Images_ExportedRaw_Empiric/MantiniNet" + str(i))

    #glue_6_images("/Users/lia.domide/Downloads/Mantini/Images_Glued_Empiric/MantiniNet")

    for i in range(1, 7):
        glue_4_images("/Users/lia.domide/Downloads/Mantini/Images_ExportedRaw_Simulation/Measure" + str(i))

    #glue_6_images("/Users/lia.domide/Downloads/Mantini/Images_Glued_Simulation/Measure")

    #glue_2_images("/Users/lia.domide/Downloads/Mantini/Images_Glued_Empiric/MantiniNetGroup.png",
    #              "/Users/lia.domide/Downloads/Mantini/Images_Glued_Simulation/MeasureGroup.png",
    #              "/Users/lia.domide/Downloads/Mantini/Mantini.png")
