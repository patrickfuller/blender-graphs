Networks in Blender
============================

Produces visualizations of network data.

Usage
-----

```bash
sh draw_network.sh *adjacency_list*
```

where *adjacency_list* is either a file or a string containing a json adjacency
list of the format `[["source_1", "target_1"], ["source_2", "target_2"], ...]`.
The node identifiers can be anything, so long as they are self consistent.
For example,

```bash
sh draw_network.sh "[[1,2],[2,3],[3,4]]"
```

will open blender with a 3D visualization of this network. For more control,
you can break the process into two parts. Running

```bash
python generate_network.py "[[1,2],[2,3],[3,4]]" > network.json
```

produces a `network.json` file containing

```json
{
    "edges": [
        {
            "source": 1, 
            "target": 2
        }, 
        {
            "source": 2, 
            "target": 3
        }, 
        {
            "source": 3, 
            "target": 4
        }
    ], 
    "nodes": {
        "1": {
            "location": [ 9.339, -17.667, -2.138 ]
        }, 
        "2": {
            "location": [ 8.877, -7.235, -10.665 ]
        }, 
        "3": {
            "location": [ 3.765, -0.434, -19.326 ]
        }, 
        "4": {
            "location": [ 0, 0, 0 ]
        }
    }
}
```

If you want to run your own location-generating code, the Blender script will
run on any `network.json` file with this format. Then, run

```bash
blender network.blend -P network_to_blender.py
```

which will open a blender gui with the chosen network. Splitting gives you
access to some additional network-generation parameters, ie.

```bash
python generate_network.py --edge-length 15 --separation 3 --density 60 --concentric --2D "[[1,2],[2,3],[3,4]]"
```

`--edge-length` is the maximum length of a network edge
`--separation` is the minimum distance between any two nodes
`--density` attempts to compact the nodes spherically if non-zero
`--concentric` places the root node at the center of the network
`--2D` confines the network layout to two dimensions

`network_to_blender.py` can also be easily edited to change node shapes and
sizes or to disable edge arrows.

Samples
-------

####TODO add samples
