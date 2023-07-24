# -*- coding: utf-8 -*-

import numpy as np


def correct_order(subject_prefix="QL_", region_mapping="../QL_20120814/QL_20120814_RegionMapping.txt"):
    good_order = np.loadtxt("centres.txt", dtype=np.str_, usecols=(0,))
    good_order = [el[2:] for el in good_order]
    good_order = np.array(good_order[:34])

    good_locations = np.loadtxt(subject_prefix + "centres.txt", dtype=np.float64, usecols=(1, 2, 3))
    bad_order = np.loadtxt(subject_prefix + "centres.txt", dtype=np.str_, usecols=(0,))
    good_locations_map = {}  # label: center x,y,z
    previous_order = {}  # label: old_order_idx
    for idx, node in enumerate(bad_order):
        good_locations_map[node] = good_locations[idx]
        previous_order[node] = idx

    old_to_new_order = {}
    with open(subject_prefix + "good_centres.txt", "w") as res:
        idx = 0
        for node in good_order:
            node_label = node + "_R"
            node_position = good_locations_map[node_label]
            res.write(f"{node_label} {node_position[0]:9.4f} {node_position[1]:9.4f} {node_position[2]:9.4f}\n")
            old_to_new_order[previous_order[node_label]] = idx
            idx += 1

        for node in good_order:
            node_label = node + "_L"
            node_position = good_locations_map[node_label]
            res.write(f"{node_label} {node_position[0]:9.4f} {node_position[1]:9.4f} {node_position[2]:9.4f}\n")
            old_to_new_order[previous_order[node_label]] = idx
            idx += 1

    rm = np.loadtxt(region_mapping, dtype=np.int32)
    for idx, val in enumerate(rm):
        rm[idx] = old_to_new_order[val]
    np.savetxt(subject_prefix + "good_rm.txt", rm, fmt="%d", delimiter="\n")


if __name__ == "__main__":
    correct_order()
    correct_order("DH_", region_mapping="../DH_20120806/DH_20120806_RegionMapping.txt")
