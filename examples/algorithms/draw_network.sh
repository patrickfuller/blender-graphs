# Generate network json
# $1 - One of the example files.
cp $1 network.json

# Run in blender
if [ $(uname -s) == "Darwin" ]; then
    # Mac version, assumes no blender link
    /Applications/blender.app/Contents/MacOS/./blender network.blend -P ../../network_to_blender.py
else
    blender network.blend -P ../../network_to_blender.py
fi
