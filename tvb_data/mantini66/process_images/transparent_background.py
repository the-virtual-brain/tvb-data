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

import os
import Image



def process_image(image_path, result_path, discrepancy):
    img = Image.open(image_path)
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        if 255 - item[0] < discrepancy and 255 - item[1] < discrepancy and 255 - item[2] < discrepancy:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    img.save(result_path, "PNG")



def process_folder(root_folder, discrepancy):

    count = 0
    for dir_path, _, file_names in os.walk(root_folder):
        for file_name in file_names:
            if file_name.endswith("png") and "_tr.png" not in file_name:
                original_png_path = os.path.join(dir_path, file_name)
                result_png_path = original_png_path.replace(".png", "_tr.png")
                process_image(original_png_path, result_png_path, discrepancy)
                count += 1
    print str(count) + " images were transformed in folder " + root_folder



if __name__ == "__main__":

    #process_folder("brain-collage/hotcold-connectivity", 10)
    #process_folder("brain-collage/hotcold-persp", 10)
    #process_folder("brain-collage/hotcold-side", 10)

    #process_folder("brain-collage/tvb-side", 10)
    #process_folder("brain-collage/tvb-top", 10)
    process_folder("brain-collage/tvb-persp", 10)
