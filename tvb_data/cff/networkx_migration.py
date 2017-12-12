import networkx
import tempfile
import os
import shutil
from cfflib import load
from cfflib import save_to_cff

old_cff_path = 'connectivities.cff'
new_cff_path = 'connectivities.cff'
temp_folder = "cff_data\\"


# from a given Graph object store nodes and edges in separate files preparing them for loading in 2.0
def _store_intermediate_nodes_and_edges(net, data_file, name):
    """
    :param net: Graph stored in version 1.1
    :param data_file: temp_folder: path to folder where intermediate results will be stored
    :param name: name of the network
    """
    data_file += name
    networkx.write_gpickle(net.edges(data=True), data_file + "_edges" + ".gpickle")
    networkx.write_gpickle(net.nodes(data=True), data_file + "_nodes" + ".gpickle")


# Reads the nodes and edges files stored in the 1.1 version and build a new Graph compatible with 2.0
def _build_and_store_new_graph(data_file, name=""):
    """
    :param data_file: path to temporary directory
    :param name: name of the network
    :return: new Graph compatible with version 2.0
    """
    data_file += name
    GE = networkx.read_gpickle(data_file + "_edges" + ".gpickle")
    GN = networkx.read_gpickle(data_file + "_nodes" + ".gpickle")
    net = networkx.Graph()
    net.add_nodes_from(GN)
    net.add_edges_from(GE)
    return net


# This method will be called from an evironment with networkX 1.1 version installed
# Given a cff file path load all networks and store intermediate nodes and edges for each of them
def store_with_version_1(old_cff_path, temp_folder):
    """
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


# This method will be called from an evironment with networkX 2.0 version installed
# Given a cff file path load the cff object, store the new network data and save to a new cff file
def create_new_version(old_cff_path, temp_folder, new_cff_path):
    """
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
    if (float(networkx.__version__) == 1.1):
        store_with_version_1(old_cff_path, temp_folder)
    elif (float(networkx.__version__) >= 2.0):
        create_new_version(old_cff_path, temp_folder, new_cff_path)


if __name__ == "__main__":
    main()
