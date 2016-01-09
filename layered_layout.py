"""
Generates network coordinates using a layered layout.

adapted from force_directed_layout.py
by
Karthik Sekar (karsekar@gmail.com)

The input arguments require a starting node that is assigned to
the starting layer (layer 0). Nodes are arranged by their distance
from this starting node.

January 2, 2015

"""

from random import uniform
from math import sqrt
from itertools import combinations, repeat
import numpy as np
from operator import add
import sys
import json
import json_formatter

def pol2cart(rho, phi):
#converts radial coordinates to cartesian
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return [x, y]


def runForcing(edges, nodes, iterations=1000, force_strength=5.0, dampening=0.05,
        max_velocity=2.0, max_distance=50, is_3d=False):
    """Runs a force-directed-layout algorithm on the input graph.

    iterations - Number of FDL iterations to run in coordinate generation
    force_strength - Strength of Coulomb and Hooke forces
                     (edit this to scale the distance between nodes)
    dampening - Multiplier to reduce force applied to nodes
    max_velocity - Maximum distance a node can move in one step
    max_distance - The maximum distance considered for interactions
    """

    # Get a list of node ids from the edge data
    #nodes = set(e["source"] for e in edges) | set(e["target"] for e in edges)

    # Convert to a data-storing object and initialize some values
    d = 3 if is_3d else 2
    nodes = {n: {"velocity": nodes[n]["location"], "force": [0.0] * d} for n in nodes}

    # Repeat n times (is there a more Pythonic way to do this?)
    for _ in repeat(None, iterations):

        # Add in Coulomb-esque node-node repulsive forces
        for node1, node2 in combinations(nodes.values(), 2):
            _coulomb(node1, node2, force_strength, max_distance)

        # And Hooke-esque edge spring forces
        for edge in edges:
            _hooke(nodes[edge["source"]], nodes[edge["target"]],
                   force_strength, max_distance)

        # Move by resultant force
        for node in nodes.values():
            # Constrain the force to the bounds specified by input parameter
            force = [_constrain(dampening * f, -max_velocity, max_velocity)
                     for f in node["force"]]
            # Update velocities and reset force
            node["velocity"] = [v + dv
                                for v, dv in zip(node["velocity"], force)]
            node["force"] = [0] * d

    # Clean and return
    for node in nodes.values():
        del node["force"]
        node["location"] = node["velocity"]
        del node["velocity"]
        # Even if it's 2D, let's specify three dimensions
        if not is_3d:
            node["location"] += [0.0]
    return nodes

def layer(edges, available_nodes, start_node="1", depth=0, xycoor = [0.0, 0.0], separation=10.0, rdistance=20.0,
        max_velocity=2.0, max_distance=50, is_3d=True):
    """Runs a layered-layout algorithm on the input graph.This a recursive function that will run on each child node.

    Parameters to mess with:
    separation - the separation between the layers in terms of the z axis
    rdistance - if there is more than one child node, they are arrange radially from the parent.
    If running the spacing algorithm, ultimately this will not matter too much.
    """

    # Convert to a data-storing object and initialize some values
    d = 3 if is_3d else 2

    # initialize the locations and convert the nodes to a dictionary of dictionaries
    child_nodes = []
    nodes={}

    #remove the current node from the list of available ones
    available_nodes.remove(start_node)

    # set the parent node higher
    nodes[start_node]={}
    nodes[start_node]["depth"]=depth
    nodes[start_node]["location"] = xycoor + [-1*separation*depth]

    # get the children of the parent
    for e in edges:
        if e["source"] == start_node:
            child_nodes.append(e["target"])
        if e["target"] == start_node:
            child_nodes.append(e["source"])

    # set the children equidistant from each other for initial positioning and layer from them
    if len(child_nodes) > 1:
        angle_btw = [2 * np.pi / len(child_nodes) * i for i in range(0,len(child_nodes))]
        for i in range(0,len(child_nodes)):
            if(child_nodes[i] in available_nodes):
                location_vector = map(add,pol2cart(rdistance, angle_btw[i]),xycoor) #center around the parent node
                nodes.update(layer(edges, available_nodes, child_nodes[i], depth+1, location_vector))
    elif len(child_nodes) == 1:
        if(child_nodes[0] in available_nodes):
            nodes.update(layer(edges, available_nodes, child_nodes[0], depth+1, xycoor))

    return nodes

def space(input_nodes, nodes_of_interest, force_iter=10):
    """
    This function is designed to space the crowded layers. It is very hacked, and improved solutions would be welcomed.

    The general premise is to treat the nodes in a given layer as a subnetwork and make fake connections. Using the
    fake connections, the forcing code written by Pat Fuller is applied.

    Parameters -
    force_iter - changes the magnitude of the force applied to the particles
    """

    #get the locations of the nodes of interest in 2-D
    #makes a subdictionary for the particular layer
    nodes = dict((k,input_nodes[k]) for k in nodes_of_interest if k in input_nodes)

    #a matrix to store distances
    dist_mat = np.zeros(shape=(len(nodes.keys()),len(nodes.keys())))

    #store the distances in the matrix
    for node1, node2 in combinations(nodes.keys(), 2):
        delta = [x2 - x1 for x1, x2 in zip(nodes[node1]["location"], nodes[node2]["location"])]
        distance = sqrt(sum(d ** 2 for d in delta))
        dist_mat[nodes_of_interest.index(node1), nodes_of_interest.index(node2)] = distance
        dist_mat[nodes_of_interest.index(node2), nodes_of_interest.index(node1)] = distance

    #find the two furthest nodes
    [max_loc,temp] = np.where(dist_mat == dist_mat.max())
    [forward_node, reverse_node] = max_loc

    #create edges starting from the terminal nodes
    temp_edges = []
    forward_mat = dist_mat.copy()
    reverse_mat = dist_mat.copy()

    #walk through the network and makes temporary connections
    for i in range(0,len(nodes.keys())):
        next_node = forward_mat[forward_node,:].argsort()[1]
        forward_mat[forward_node,:]=dist_mat.max()+1
        forward_mat[:,forward_node]=dist_mat.max()+1
        temp_edges.append({"source": nodes_of_interest[forward_node], "target": nodes_of_interest[next_node]})
        forward_node = next_node

        next_node = reverse_mat[reverse_node,:].argsort()[1]
        reverse_mat[reverse_node,:]=dist_mat.max()+1
        reverse_mat[:,reverse_node]=dist_mat.max()+1
        temp_edges.append({"source": nodes_of_interest[reverse_node], "target": nodes_of_interest[next_node]})
        reverse_node = next_node

    nodes = runForcing(temp_edges, nodes, iterations=force_iter)

    #update the x,y values for the forced nodes
    for node in nodes.keys():
        input_nodes[node]["location"][0:2] = nodes[node]["location"][0:2]

    return input_nodes

def _coulomb(n1, n2, k, r):
    """Calculates Coulomb forces and updates node data."""
    # Get relevant positional data
    delta = [x2 - x1 for x1, x2 in zip(n1["velocity"], n2["velocity"])]
    distance = sqrt(sum(d ** 2 for d in delta))

    # If the deltas are too small, use random values to keep things moving
    if distance < 0.1:
        delta = [uniform(0.1, 0.2) for _ in repeat(None, 3)]
        distance = sqrt(sum(d ** 2 for d in delta))

    # If the distance isn't huge (ie. Coulomb is negligible), calculate
    if distance < r:
        force = (k / distance) ** 2
        n1["force"] = [f - force * d for f, d in zip(n1["force"], delta)]
        n2["force"] = [f + force * d for f, d in zip(n2["force"], delta)]


def _hooke(n1, n2, k, r):
    """Calculates Hooke spring forces and updates node data."""
    # Get relevant positional data
    delta = [x2 - x1 for x1, x2 in zip(n1["velocity"], n2["velocity"])]
    distance = sqrt(sum(d ** 2 for d in delta))

    # If the deltas are too small, use random values to keep things moving
    if distance < 0.1:
        delta = [uniform(0.1, 0.2) for _ in repeat(None, 3)]
        distance = sqrt(sum(d ** 2 for d in delta))

    # Truncate distance so as to not have crazy springiness
    distance = min(distance, r)

    # Calculate Hooke force and update nodes
    force = (distance ** 2 - k ** 2) / (distance * k)
    n1["force"] = [f + force * d for f, d in zip(n1["force"], delta)]
    n2["force"] = [f - force * d for f, d in zip(n2["force"], delta)]


def _constrain(value, min_value, max_value):
    """Constrains a value to the inputted range."""
    return max(min_value, min(value, max_value))


if __name__ == "__main__":
    threshold_for_spacing = 20 #threshold for the number of nodes in a given layer for spacing algorithm to be used

    try:
        with open(sys.argv[-1]) as in_file:
            edges = json.load(in_file)
    except IOError:
        edges = json.loads(sys.argv[-1])

    #get the starting node
    starting_node = sys.argv[-2]


    # Convert to internal representation
    edges = [{"source": str(s), "target": str(t)} for s, t in edges]

    # Handle additional args (Will need to change)
    kwargs = {"force_strength": 5.0, "is_3d": True}
    for i, arg in enumerate(sys.argv):
        if arg == "--force-strength":
            kwargs["force_strength"] = float(sys.argv[i + 1])
    #    elif arg == "--2D":   #currently not designed for 2d network generation, but hey, you can do that! I believe in you
    #        kwargs["is_3d"] = False

    # Handle additional args
    kwargs = {"separation": 5.0, "is_3d": True}

    # generate the available nodes
    available_nodes = set(e["source"] for e in edges) | set(e["target"] for e in edges)

    #creates the initial arrangement for the nodes based on the starting node
    master_nodes = layer(edges, available_nodes, start_node=starting_node,depth=0)

    #get the range of depth and counts for each layer
    depth_count = {}
    for node in master_nodes.keys():
        if master_nodes[node]["depth"] in depth_count.keys():
            depth_count[master_nodes[node]["depth"]] = depth_count[master_nodes[node]["depth"] ] + 1
        else:
            depth_count[master_nodes[node]["depth"] ] = 1

    #space out particular layers based on how many nodes are in a particular layer
    for layer_of_interest,count in depth_count.items():
        if count > threshold_for_spacing:
            nodes_of_interest = []
            for node in master_nodes.keys():
                if master_nodes[node]["depth"] == layer_of_interest:
                    nodes_of_interest.append(node)

            master_nodes = space(master_nodes, nodes_of_interest, force_iter=10)

    # Convert to json and print
    print json_formatter.dumps({"edges": edges, "nodes": master_nodes})
