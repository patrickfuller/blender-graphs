"""
Blender script. Draws a node-and-edge network in blender, randomly distributed
spherically.

14 Sept 2011: Added collision detection between nodes

30 Nov 2012: Rewrote. Switched to JSON, and large Blender speed boosts.

Written by Patrick Fuller, patrickfuller@gmail.com, 11 Sept 11
"""

import bpy
from math import acos, degrees, pi
from mathutils import Vector

import json
from random import choice

# Colors to turn into materials
colors = {"purple": (178, 132, 234), "gray": (11, 11, 11),
          "green": (114, 195, 0), "red": (255, 0, 75),
          "blue": (0, 131, 255), "clear": (0, 131, 255),
          "yellow": (255, 187, 0), "light_gray": (118, 118, 118)}

# Normalize to [0,1] and make blender materials
for key, value in colors.items():
    value = [x / 255.0 for x in value]
    bpy.data.materials.new(name=key)
    bpy.data.materials[key].diffuse_color = value
    bpy.data.materials[key].specular_intensity = 0.5

    # Don't specify more parameters if these colors
    if key == "gray" or key == "light_gray":
        continue

    # Transparency parameters
    bpy.data.materials[key].use_transparency = True
    bpy.data.materials[key].transparency_method = "RAYTRACE"
    bpy.data.materials[key].alpha = 0.1 if key == "clear" else 0.95
    bpy.data.materials[key].raytrace_transparency.fresnel = 0.1
    bpy.data.materials[key].raytrace_transparency.ior = 1.15


def draw_network(network, edge_thickness=0.25, node_size=3, directed=True):
    """ Takes assembled network/molecule data and draws to blender """

    # Add some mesh primitives
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.mesh.primitive_uv_sphere_add()
    sphere = bpy.context.object
    bpy.ops.mesh.primitive_cylinder_add()
    cylinder = bpy.context.object
    cylinder.active_material = bpy.data.materials["light_gray"]
    bpy.ops.mesh.primitive_cone_add()
    cone = bpy.context.object
    cone.active_material = bpy.data.materials["light_gray"]

    # Keep references to all nodes and edges
    shapes = []
    # Keep separate references to shapes to be smoothed
    shapes_to_smooth = []

    # Draw nodes
    for key, node in network["nodes"].items():

        # Coloring rule for nodes. Edit this to suit your needs!
        col = node.get("color", choice(list(colors.keys())))

        # Copy mesh primitive and edit to make node
        # (You can change the shape of drawn nodes here)
        node_sphere = sphere.copy()
        node_sphere.data = sphere.data.copy()
        node_sphere.location = node["location"]
        node_sphere.dimensions = [node_size] * 3
        node_sphere.active_material = bpy.data.materials[col]
        bpy.context.scene.objects.link(node_sphere)
        shapes.append(node_sphere)
        shapes_to_smooth.append(node_sphere)

    # Draw edges
    for edge in network["edges"]:

        # Get source and target locations by drilling down into data structure
        source_loc = network["nodes"][edge["source"]]["location"]
        target_loc = network["nodes"][edge["target"]]["location"]

        diff = [c2 - c1 for c2, c1 in zip(source_loc, target_loc)]
        cent = [(c2 + c1) / 2 for c2, c1 in zip(source_loc, target_loc)]
        mag = sum([(c2 - c1) ** 2
                  for c1, c2 in zip(source_loc, target_loc)]) ** 0.5

        # Euler rotation calculation
        v_axis = Vector(diff).normalized()
        v_obj = Vector((0, 0, 1))
        v_rot = v_obj.cross(v_axis)
        angle = acos(v_obj.dot(v_axis))

        # Copy mesh primitive to create edge
        edge_cylinder = cylinder.copy()
        edge_cylinder.data = cylinder.data.copy()
        edge_cylinder.dimensions = [edge_thickness] * 2 + [mag - node_size]
        edge_cylinder.location = cent
        edge_cylinder.rotation_mode = "AXIS_ANGLE"
        edge_cylinder.rotation_axis_angle = [angle] + list(v_rot)
        bpy.context.scene.objects.link(edge_cylinder)
        shapes.append(edge_cylinder)
        shapes_to_smooth.append(edge_cylinder)

        # Copy another mesh primitive to make an arrow head
        if directed:
            arrow_cone = cone.copy()
            arrow_cone.data = cone.data.copy()
            arrow_cone.dimensions = [edge_thickness * 4.0] * 3
            arrow_cone.location = cent
            arrow_cone.rotation_mode = "AXIS_ANGLE"
            arrow_cone.rotation_axis_angle = [angle + pi] + list(v_rot)
            bpy.context.scene.objects.link(arrow_cone)
            shapes.append(arrow_cone)

    # Remove primitive meshes
    bpy.ops.object.select_all(action='DESELECT')
    sphere.select = True
    cylinder.select = True
    cone.select = True

    # If the starting cube is there, remove it
    if "Cube" in bpy.data.objects.keys():
        bpy.data.objects.get("Cube").select = True
    bpy.ops.object.delete()

    # Smooth specified shapes
    for shape in shapes_to_smooth:
        shape.select = True
    bpy.context.scene.objects.active = shapes_to_smooth[0]
    bpy.ops.object.shade_smooth()

    # Join shapes
    for shape in shapes:
        shape.select = True
    bpy.context.scene.objects.active = shapes[0]
    bpy.ops.object.join()

    # Center object origin to geometry
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="MEDIAN")

    # Refresh scene
    bpy.context.scene.update()

# If main, load json and run
if __name__ == "__main__":
    with open("network.json") as network_file:
        network = json.load(network_file)
    draw_network(network)
