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
.. moduleauthor:: Dan Pop <dan.pop@codemart.ro>
"""

import networkx
import tempfile
import os
import shutil
from cfflib import load, save_to_cff

OLD_CFF = 'connectivities.cff'
NEW_CFF = 'connectivities.cff'
TEMP_FOLDER = "cff_data\\"


def _store_intermediate_nodes_and_edges(net, data_file, name):
    """
    from a given Graph object store nodes and edges in separate files preparing them for loading in 2.0
    :param net: Graph stored in version 1.1
    :param data_file: temp_folder: path to folder where intermediate results will be stored
    :param name: name of the network
    """
    data_file += name
    networkx.write_gpickle(net.edges(data=True), data_file + "_edges" + ".gpickle")
    networkx.write_gpickle(net.nodes(data=True), data_file + "_nodes" + ".gpickle")


def _build_and_store_new_graph(data_file, name=""):
    """
    Reads the nodes and edges files stored in the 1.1 version and build a new Graph compatible with 2.0
    :param data_file: path to temporary directory
    :param name: name of the network
    :return: new Graph compatible with version 2.0
    """
    data_file += name
    edges = networkx.read_gpickle(data_file + "_edges" + ".gpickle")
    nodes = networkx.read_gpickle(data_file + "_nodes" + ".gpickle")
    net = networkx.Graph()
    net.add_nodes_from(nodes)
    net.add_edges_from(edges)
    return net


def store_with_version_1(old_cff_path, temp_folder):
    """
    Given a cff file path load all networks and store intermediate nodes and edges for each of them
    :param old_cff_path: path to cff file from version 1.1
    :param temp_folder: path to folder where intermediate results will be stored
    :return: store all intermediate nodes and graphs in separate files
    """
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    cff_obj = load(old_cff_path)
    networks = cff_obj.get_connectome_network()
    if networks:
        for net in networks:
            net.load()
            _store_intermediate_nodes_and_edges(net.data, temp_folder, net.name)


def create_new_version(old_cff_path, temp_folder, new_cff_path):
    """
    Given a cff file path load the cff object, store the new network data and save to a new cff file
    :param old_cff_path: path to cff file from version 1.1
    :param temp_folder: path to folder where intermediate results are stored
    :param new_cff_path: path where new cff file is stored
    """
    cff_obj = load(old_cff_path)
    networks = cff_obj.get_connectome_network()
    if networks:
        for net in networks:
            net.data = _build_and_store_new_graph(temp_folder, name=net.name)
            tmpdir = tempfile.gettempdir()
            net.tmpsrc = tmpdir + "\\cff_data"
    save_to_cff(cff_obj, new_cff_path)
    shutil.rmtree(temp_folder)


def main():
    if float(networkx.__version__) == 1.1:
        store_with_version_1(OLD_CFF, TEMP_FOLDER)
    elif float(networkx.__version__) >= 2.0:
        create_new_version(OLD_CFF, TEMP_FOLDER, NEW_CFF)


if __name__ == "__main__":
    main()
