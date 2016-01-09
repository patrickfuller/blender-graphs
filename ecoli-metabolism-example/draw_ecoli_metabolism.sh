# Generate network json from connectivity file. 219 is the glucose node. Layering a network with glucose at the top.
python ../layered_layout.py 219 connectivity.json > networkPreColor.json

#Color the network according to KEGG categorization
python ../color_network.py networkPreColor.json > network.json

# Run in blender
if [ $(uname -s) == "Darwin" ]; then
    # Mac version, assumes no blender link
    /Applications/blender.app/Contents/MacOS/./blender -P ../network_to_blender.py
else
    blender -P ../network_to_blender.py
fi