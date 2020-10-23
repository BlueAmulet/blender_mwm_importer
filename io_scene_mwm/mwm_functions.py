#!/usr/bin/env python
from . import byte_functions as read
from . import mwm_datatypes as mwm
import time
import traceback


def seek_if_exists(section, index_dict, file):
    if section in index_dict:
        seek_loc = index_dict[section]
        file.seek(seek_loc)
        return True
    return False


def load_mesh_sections(file):
    params = {}

    # RescaleToLengthInMeters param
    key = read.read_string(file)
    value = read.read_bool(file)
    params[key] = value

    # LengthInMeters param
    key = read.read_string(file)
    value = read.read_float(file)
    params[key] = value

    # RescaleFactor param
    key = read.read_string(file)
    value = read.read_float(file)
    params[key] = value

    # Centered param
    key = read.read_string(file)
    value = read.read_bool(file)
    params[key] = value

    # UseChannelTextures param
    key = read.read_string(file)
    value = read.read_bool(file)
    params[key] = value

    # SpecularShininess param
    key = read.read_string(file)
    value = read.read_float(file)
    params[key] = value

    # SpecularPower param
    key = read.read_string(file)
    value = read.read_float(file)
    params[key] = value

    # BoundingBox param
    key = read.read_string(file)

    x = read.read_float(file)
    y = read.read_float(file)
    z = read.read_float(file)
    min = (x, y, z)

    x = read.read_float(file)
    y = read.read_float(file)
    z = read.read_float(file)
    max = (x, y, z)

    value = mwm.BoundingBox(min, max)
    params[key] = value

    # BoundingSphere param
    key = read.read_string(file)

    x = read.read_float(file)
    y = read.read_float(file)
    z = read.read_float(file)
    pos = (x, y, z)
    radius = read.read_float(file)

    value = mwm.BoundingSphere(pos, radius)
    params[key] = value

    # SwapWindingOrder param
    key = read.read_string(file)
    value = read.read_bool(file)
    params[key] = value

    return params


def load_mesh_sections_new(index_dict, file):
    params = {}

    if seek_if_exists('UseChannelTextures', index_dict, file):
        key = read.read_string(file)
        value = read.read_bool(file)
        params[key] = value

    if seek_if_exists('BoundingBox', index_dict, file):
        key = read.read_string(file)

        x = read.read_float(file)
        y = read.read_float(file)
        z = read.read_float(file)
        min = (x, y, z)

        x = read.read_float(file)
        y = read.read_float(file)
        z = read.read_float(file)
        max = (x, y, z)

        value = mwm.BoundingBox(min, max)
        params[key] = value

    if seek_if_exists('BoundingSphere', index_dict, file):
        key = read.read_string(file)

        x = read.read_float(file)
        y = read.read_float(file)
        z = read.read_float(file)
        pos = (x, y, z)
        radius = read.read_float(file)

        value = mwm.BoundingSphere(pos, radius)
        params[key] = value

    if seek_if_exists('RescaleFactor', index_dict, file):
        key = read.read_string(file)
        value = read.read_float(file)
        params[key] = value

    if seek_if_exists('SwapWindingOrder', index_dict, file):
        key = read.read_string(file)
        value = read.read_bool(file)
        params[key] = value

    if seek_if_exists('BlendIndices', index_dict, file):
        key = read.read_string(file)
        nBlendIndices = read.read_long(file)

        blend_indices = []
        for i in range(nBlendIndices):
            x = read.read_long(file) & 0xFF
            y = read.read_long(file) & 0xFF
            z = read.read_long(file) & 0xFF
            w = read.read_long(file) & 0xFF
            blend_indices.append((x, y, z, w))

        params[key] = blend_indices

    if seek_if_exists('BlendWeights', index_dict, file):
        key = read.read_string(file)
        nBlendWeights = read.read_long(file)

        blend_weights = []
        for i in range(nBlendWeights):
            x = read.read_float(file)
            y = read.read_float(file)
            z = read.read_float(file)
            w = read.read_float(file)
            blend_weights.append((x, y, z, w))

        params[key] = blend_weights

    if seek_if_exists('Bones', index_dict, file):
        key = read.read_string(file)
        nBones = read.read_long(file)
        print("%s bones" % nBones)

        bones = []
        for index in range(nBones):
            name = read.read_string(file)
            parent = read.read_long(file)
            transform = load_matrix(file)
            bone = mwm.Bone(name, parent, transform)
            bones.append(bone)

        params[key] = bones

    if seek_if_exists('BoneMapping', index_dict, file):
        key = read.read_string(file)
        nBoneMap = read.read_long(file)

        bone_map = []
        for i in range(nBoneMap):
            x = read.read_float(file)
            y = read.read_float(file)
            z = read.read_float(file)
            bone_map.append((x, y, z))

        params[key] = bone_map

    return params


def load_mesh_data(file):
    vertices = load_vertices(file)
    normals = load_normals(file)
    uv_coords = load_uv_coords(file)
    binormals = load_binormals(file)
    tangents = load_tangents(file)
    tex_coords = load_text_coord(file)

    return mwm.VertexData(vertices, normals, uv_coords, binormals, tangents, tex_coords)


def load_mesh_data_new(index_dict, file):
    file.seek(index_dict['Vertices'])
    vertices = load_vertices(file)
    file.seek(index_dict['Normals'])
    normals = load_normals(file)
    file.seek(index_dict['TexCoords0'])
    uv_coords = load_uv_coords(file)
    file.seek(index_dict['Binormals'])
    binormals = load_binormals(file)
    file.seek(index_dict['Tangents'])
    tangents = load_tangents(file)
    file.seek(index_dict['TexCoords1'])
    tex_coords = load_text_coord(file)

    return mwm.VertexData(vertices, normals, uv_coords, binormals, tangents, tex_coords)


# Check for class "MyMeshPartInfo" in SE Code, should be in
# Sources/VRage.Render/Import/MyImportUtils.cs
def load_mesh_parts(file, version):
    section = read.read_string(file)
    nParts = read.read_long(file)
    print("%s mesh parts" % nParts)

    parts = []
    for i in range(nParts):
        part = load_part(file, version)
        parts.append(part)

    return parts


def load_part(file, version):
    m_MaterialHash = read.read_long(file)

    if version < 1052001:
        print("Older part version detected")
        draw_technique = read.read_long(file)

    count = read.read_long(file)
    print("Count is %s" % count)
    face_count = int(count / 3)
    print("Got %s faces." % face_count)

    indices = []
    used_indices = set()
    for i in range(count):
        index = read.read_long(file)
        indices.append(index)
        used_indices.add(index)
    used_indices = sorted(used_indices)

    vertex_map = {}
    for i, index in enumerate(used_indices):
        vertex_map[index] = i

    faces = []
    for i in range(face_count):
        try:
            x = indices[i * 3 + 0]
            y = indices[i * 3 + 1]
            z = indices[i * 3 + 2]
            faces.append((vertex_map[x], vertex_map[y], vertex_map[z]))
        except:
            print("%s / %s" % (i, face_count))
            traceback.print_exc()
            exit(1)

    hasMaterial = read.read_bool(file)
    material = None
    if (hasMaterial):
        material = load_material(file, version)

    return mwm.MeshPart(vertex_map, faces, material)


def load_material(file, version):
    name = read.read_string(file)
    params = {}

    if version < 1052002:
        diffuse_texture = read.read_string(file)
        normal_texture = read.read_string(file)
        if diffuse_texture:
            params['DiffuseTexture'] = diffuse_texture
        if normal_texture:
            params['NormalTexture'] = normal_texture
    else:
        nParams = read.read_long(file)
        for i in range(nParams):
            key = read.read_string(file)
            value = read.read_string(file)
            params[key] = value

    if version >= 1068001:
        user_data = {}
        nUserData = read.read_long(file)
        for i in range(nUserData):
            key = read.read_string(file)
            value = read.read_string(file)
            user_data[key] = value

    if version < 1157001:
        glossiness = read.read_float(file)

        x = read.read_float(file)
        y = read.read_float(file)
        z = read.read_float(file)
        diffuse_color = (x, y, z)

        x = read.read_float(file)
        y = read.read_float(file)
        z = read.read_float(file)
        specular_color = (x, y, z)
    else:
        # TODO: How does this work in newer versions?
        print("TODO: New version MWM missing material parameters?")
        # Assume some defaults for now
        glossiness = 1.
        diffuse_color = (1., 1., 1.)
        specular_color = (1., 1., 1.)

    if version < 1052001:
        # TODO: Convert this to a string using a lookup table
        technique = read.read_long(file)
        print("TODO: Legacy technique value %s" % technique)
    else:
        technique = read.read_string(file)

    if technique == 'GLASS':
        if version >= 1043001:
            glass_cw = read.read_string(file)
            glass_ccw = read.read_string(file)
            smooth_normals = read.read_bool(file)
            if glass_ccw:
                # TODO: If the current material isn't transparent and the glass_ccw material is transparent, set name = glass_ccw
                print("TODO: Possibly correct material name: %s" % glass_ccw)
        else:
            # TODO: What are these obsolete values?
            read.read_float(file)
            read.read_float(file)
            read.read_float(file)
            read.read_float(file)
            glass_cw = "GlassCW"
            glass_ccw = "GlassCCW"

    return mwm.Material(name, params, glossiness, diffuse_color, specular_color, technique)


def load_tangents(file):
    section = read.read_string(file)
    nTang = read.read_long(file)

    tangents = []
    for i in range(nTang):
        file.read(4)

    return tangents


def load_text_coord(file):
    section = read.read_string(file)
    nTextCoord = read.read_long(file)

    for i in range(nTextCoord):
        file.read(4)

    return None


def load_binormals(file):
    section = read.read_string(file)
    nBinormals = read.read_long(file)

    binormals = []
    for i in range(nBinormals):
        file.read(4)  # 4 bytes of data, Don;t know what type

    return binormals


def load_uv_coords(file):
    section = read.read_string(file)
    nUvs = read.read_long(file)

    uv_coords = []
    for i in range(nUvs):
        u = read.read_hfloat(file)
        v = read.read_hfloat(file)
        uv_coords.append((u, v))

    return uv_coords


def load_normals(file):
    section = read.read_string(file)
    nNormals = read.read_long(file)

    normals = []
    for i in range(nNormals):
        file.read(4)  # 4 bytes of data, Don't know what type

    return normals


def load_vertices(file):
    section = read.read_string(file)
    nPositions = read.read_long(file)

    positions = []
    for i in range(nPositions):
        x = read.read_hfloat(file)
        y = read.read_hfloat(file)
        z = read.read_hfloat(file)
        w = read.read_hfloat(file)

        positions.append((x, z, y))

    return positions


def load_dummies(file):
    section = read.read_string(file)
    nDummies = read.read_long(file)

    dummies = []
    for i in range(nDummies):
        dummy = load_dummy(file)
        dummies.append(dummy)

    return dummies


def load_dummy(file):
    name = read.read_string(file)
    matrix = load_matrix(file)

    nParams = read.read_long(file)

    params = {}
    for i in range(nParams):
        key = read.read_string(file)
        value = read.read_string(file)
        params[key] = value

    return mwm.Dummy(name, matrix, params)


def load_matrix(file):
    mat = [[0 for x in range(4)] for x in range(4)]

    mat[0][0] = read.read_float(file)
    mat[0][1] = read.read_float(file)
    mat[0][2] = read.read_float(file)
    mat[0][3] = read.read_float(file)

    mat[1][0] = read.read_float(file)
    mat[1][1] = read.read_float(file)
    mat[1][2] = read.read_float(file)
    mat[1][3] = read.read_float(file)

    mat[2][0] = read.read_float(file)
    mat[2][1] = read.read_float(file)
    mat[2][2] = read.read_float(file)
    mat[2][3] = read.read_float(file)

    mat[3][0] = read.read_float(file)
    mat[3][1] = read.read_float(file)
    mat[3][2] = read.read_float(file)
    mat[3][3] = read.read_float(file)

    return mat


def load_mwm_header(file):
    # reading the headder
    section = read.read_string(file)
    print("Section: %s" % section)
    flag = read.read_long(file)
    print("Flag: %s" % flag)
    if flag == 0:
        return 0
    version = read.read_string(file)
    if version[:8] != "Version:":
        time.sleep(0.25)
        err_msg = "Uht-oh.  Version string did not parse.\n" \
                  "Expected value to start with Version: instead got:\n%s" \
                  % version
        raise ValueError(err_msg)
    version_number = int(version[8:])
    return version_number


def load_index(file):
    total_items = read.read_long(file)
    item_dictionary = dict()
    item_count = 0
    print("Item count: %s" % total_items)
    while item_count < total_items:
        tagName = read.read_string(file)
        index = read.read_long(file)
        item_dictionary[tagName] = index
        item_count += 1

    return item_dictionary

