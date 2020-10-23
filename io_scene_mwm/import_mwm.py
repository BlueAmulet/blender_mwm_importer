import struct
import importlib.util
import os.path
from . import mwm_functions as mwm

bpy_spec = importlib.util.find_spec("bpy")
if bpy_spec is not None:
    is_blender = True
    import bpy
    from bpy.types import Operator
    from bpy.props import StringProperty
    from bpy_extras.io_utils import ImportHelper
else:
    # We're probably not in Blender if bpy cannot be imported.
    is_blender = False


def load(operator, context):
    file = open(operator.filepath, "rb")

    name = os.path.splitext(os.path.basename(operator.filepath))[0]

    version_number = mwm.load_mwm_header(file)

    print("Version: %s" % version_number)

    if version_number > 1066002:
        print("This is at least version 1066002")
        load_current(operator, context, file, version_number, name)
    else:
        print("Model format is older than 1066002")
        load_classic(operator, context, file, version_number, name)

    file.close()
    return {'FINISHED'}


def load_current(operator, context, file, version, name):
    index = mwm.load_index(file)

    print("Loading vertex data")
    vertex_data = mwm.load_mesh_data_new(index, file)

    print("Loading model parameters")
    model_params = mwm.load_mesh_sections_new(index, file)

    print("Loading model parts")
    file.seek(index['MeshParts'])
    model_parts = mwm.load_mesh_parts(file, version)

    load_blender(context, vertex_data, model_params, model_parts, name)


def load_classic(operator, context, file, version, name):
    dummies = mwm.load_dummies(file)

    print("Loading vertex data")
    vertex_data = mwm.load_mesh_data(file)

    print("Loading model parameters")
    model_params = mwm.load_mesh_sections(file)

    print("Loading model parts")
    model_parts = mwm.load_mesh_parts(file, version)

    load_blender(context, vertex_data, model_params, model_parts, name)


def load_blender(context, vertex_data, model_params, model_parts, name):
    for model_part in model_parts:
        profile_mesh = bpy.data.meshes.new("%s_Data" % name)
        profile_object = bpy.data.objects.new(name, profile_mesh)
        profile_object.data = profile_mesh

        used_positions = [vertex for idx, vertex in enumerate(vertex_data.positions) if idx in model_part.vertex_map]
        profile_mesh.from_pydata(used_positions, [], model_part.faces)
        profile_mesh.polygons.foreach_set('use_smooth', (True,)*len(model_part.faces))

        profile_mesh.update()

        scene = context.scene
        scene.objects.link(profile_object)
        profile_object.select = True
