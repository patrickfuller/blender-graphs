Graphs in Blender
=================

Produces high-quality 3D visualizations of network data.

######For interactive 3D graph visualization, check out the [igraph](https://github.com/patrickfuller/igraph) project.

Examples
--------

**Quinoline reaction pathway in a flask**

![](http://i.imgur.com/gRpBs9X.png)

**Breadth-first search depiction**

![](http://i.imgur.com/Ll0AMBU.png)

Usage
-----

To use standard parameters for everything, simply run

```bash
sh draw_network.sh *adjacency_list*
```

where *adjacency_list* is either a file or a string containing a json adjacency
list of the format

```json
[["source_1", "target_1"], ["source_2", "target_2"], ...]
```

The node identifiers can be anything, so long as they are self consistent.
For example,

```bash
sh draw_network.sh "[[1,2],[2,3],[3,4],[4,1],[2,5],[5,4]]"
```

will open blender with a 3D visualization of this network (see the "pinwheel" sample).

Advanced Usage
--------------

For more control, you can break the process into two parts. Running

```bash
python force_directed_layout.py "[[1,2],[2,3],[3,4]]" > network.json
```

produces a `network.json` file containing

```json
{
    "edges": [
        { "source": "1", "target": "2" },
        { "source": "2", "target": "3" },
        { "source": "3", "target": "4" }
    ],
    "nodes": {
        "1": { "location": [ -3.290, -6.258, -8.930 ] },
        "2": { "location": [ -1.115, -2.167, -3.103 ] },
        "3": { "location": [ 1.188, 2.173, 3.096 ] },
        "4": { "location": [ 3.348, 6.252, 8.937 ] }
    }
}
```

If you want to run your own location-generating code, the Blender script will
run on any `network.json` file with this format (Note: make sure the file
is called "network.json"!). For some control of colors, you can specify a few
common options directly in the .json by specifying a `"color"` property for each
node. For example, you can edit the above to:

```json
{
    "edges": [
        { "source": "1", "target": "2" },
        { "source": "2", "target": "3" },
        { "source": "3", "target": "4" }
    ],
    "nodes": {
        "1": { "location": [ -3.290, -6.258, -8.930 ], "color": "red" },
        "2": { "location": [ -1.115, -2.167, -3.103 ], "color": "gray" },
        "3": { "location": [ 1.188, 2.173, 3.096 ], "color": "blue" },
        "4": { "location": [ 3.348, 6.252, 8.937 ], "color": "purple" }
    }
}
```

If color is not specified, random colors will be chosen. For more control, open
the `network_to_blender.py` file directly and edit this logic yourself. It's a
very short script, so you should have no problem editing it. The `network_to_blender.py`
script can also be easily edited to change node shapes and sizes, or to disable edge arrows.

Once you're happy with your coloring, run

```bash
blender -P network_to_blender.py
```

which will open a blender gui with the chosen graph.

Splitting this process into two commands gives you access to some additional
graph-generation parameters.

```bash
python force_directed_layout.py --force-strength 10 --2D "[[1,2],[2,3],[3,4]]"
```

 * `--force-strength` determines the separation between nodes
 * `--2D` confines the network layout to two dimensions

Random layout is a useful starting point in cases where you
want to create your own layout for artistic reasons. 

```bash
python random_layout.py --edge-length 15 --separation 3 --density 60 --concentric --2D "[[1,2],[2,3],[3,4]]"
```

 * `--edge-length` is the maximum length of a network edge
 * `--separation` is the minimum distance between any two nodes
 * `--density` attempts to compact the nodes spherically if non-zero
 * `--concentric` places the root node at the center of the network
 * `--2D` confines the network layout to two dimensions

Layered layout will arrange the network according to distance from a designated node. See the [subfolder](./ecoli-metabolism-example/) for usage. 
