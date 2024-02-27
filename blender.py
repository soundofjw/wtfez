"""
FEZ Level Importer
kinda crude
kinda awesome

1) save this script into a blender file
2) set the relative path in FEZ_BASE below
3) go to the end and change the level you want to load
4) execute

have fun.

written by josh whelchel
https://github.com/soundofjw/wtfez

support me by listening to my music on bandcamp/spotify thanks

https://open.spotify.com/artist/04028XCsu1NbFcypg2g559?si=V-uLJ_yvTES3SmjaXf2row
https://soundofjw.bandcamp.com/

incredible thanks to polytron and everyone for the journey

sorry for my grotesque python
"""

import bpy
import os
import imbuf
from bpy_extras.object_utils import object_data_add
from mathutils import Vector
import math

import xml.etree.ElementTree as ET

FEZ_BASE = "//../FEZ_xnb_content_rips"

TRILE_SETS = bpy.path.abspath(FEZ_BASE + "/" + "trile sets")
LEVELS = bpy.path.abspath(FEZ_BASE + "/" + "levels")
ART_OBJECTS = bpy.path.abspath(FEZ_BASE + "/" + "art objects")
BACKGROUND_PLANES = bpy.path.abspath(FEZ_BASE + "/" + "background planes")

ctx = bpy.context.copy()

def clearData():

    # only worry about data in the startup scene
    for bpy_data_iter in (
            bpy.data.objects,
            bpy.data.meshes,
            bpy.data.cameras,
            bpy.data.materials,
            bpy.data.node_groups,
            bpy.data.images,
            bpy.data.collections,
    ):
        for id_data in bpy_data_iter:
            if getattr(id_data, "name", None) != "grain_manager":  # i wanted to preserve this in my tests
                bpy_data_iter.remove(id_data)

radPi = math.pi / 180
orientations = [180, 270, 0, 90]
orientations = [orientations[o] * radPi for o in range(len(orientations))]

normals = [
    (0, -1, 0),
    (0, 0, -1),
    (-1, 0, 0),
    (0, 1, 0),
    (0, 0, 1),
    (1, 0, 0),
]

def openTrileSet(trileSetName):
    print("Loading Trile Set: " + trileSetName)
    trileImagePath = TRILE_SETS + "/" + trileSetName.lower() + ".png"

    trileXml = ET.parse(TRILE_SETS + "/" + trileSetName.lower() + ".xml").getroot()
    tEntries = {}
    for entryXml in trileXml.findall('Triles/TrileEntry'):
        tEntry = {'key': entryXml.attrib['key']}

        trileXml = entryXml.find('Trile')
        atlasOffsetXml = trileXml.find('AtlasOffset/Vector2')
        tEntry['atlasOffset'] = vec2(atlasOffsetXml)
        vertices, indices, edges = readGeometry(trileXml.find('Geometry'))

        obj_name = trileXml.attrib['name']
        mesh = bpy.data.meshes.new(obj_name)

        verts = [v['position'] for v in vertices]
        mesh.from_pydata(verts, [], indices)
        mesh.validate(verbose=True)
        mesh.flip_normals()

        uv_layer = mesh.uv_layers.new(name="uv_" + obj_name)
        for loop in mesh.loops:
            uv_layer.data[loop.index].uv = vertices[loop.vertex_index]['textureCoord']

        tEntry['mesh'] = mesh
        tEntry['mesh_name'] = obj_name

        tEntries[tEntry['key']] = tEntry

    return tEntries, trileImagePath

art_object_cache = {}

def buildArtObject(artObjectName):
    print("Loading AO: " + artObjectName)
    if artObjectName in art_object_cache:
        return art_object_cache[artObjectName]

    artObjectPath = ART_OBJECTS + "/" + artObjectName.lower() + ".xml"
    artObjectImagePath = ART_OBJECTS + "/" + artObjectName[:-2].lower() + ".png"
    aoXml = ET.parse(artObjectPath).getroot()

    vertices, indices, edges = readGeometry(aoXml)

    obj_name = aoXml.attrib['name']
    mesh = bpy.data.meshes.new('AO-' + obj_name)

    verts = [v['position'] for v in vertices]
    normals = [v['normal'] for v in vertices]
    mesh.from_pydata(verts, [], indices)
    mesh.validate(verbose=True)

    uv_layer = mesh.uv_layers.new(name="uv_" + obj_name)
    for loop in mesh.loops:
        uv_layer.data[loop.index].uv = vertices[loop.vertex_index]['textureCoord']

#    indexedNormals = []
#    for loop in mesh.loops:
#        indexedNormals.append(normals[loop.vertex_index])
#    mesh.normals_split_custom_set(indexedNormals)
    mesh.flip_normals()

    aoMaterial = buildMaterial(name='ao: ' + artObjectName, image=artObjectImagePath, nodeGroup='art object')
    art_object_cache[artObjectName] = (mesh, aoMaterial)
    return mesh, aoMaterial

def buildAnimatedBackgroundPlane(bgPlane, bgScale):
    textureName = bgPlane.attrib['textureName']
    animatedXmlPath = BACKGROUND_PLANES + "/" + textureName.replace("\\", "/").lower() + ".xml"
    bgAnimatedXml = ET.parse(animatedXmlPath).getroot()
    width = int(bgAnimatedXml.attrib['width'])
    height = int(bgAnimatedXml.attrib['height'])
    actualWidth = int(bgAnimatedXml.attrib['actualWidth'])
    actualHeight = int(bgAnimatedXml.attrib['actualHeight'])
    frames = []
    for frame in bgAnimatedXml.findall("Frames/Frame"):
        frames.append({'duration': int(frame.attrib['duration'])})

    mesh, texCoords = buildBackgroundPlaneMesh(textureName, actualWidth, actualHeight)
    framePadding = (actualHeight / height)
    frameBasis = 1.0 / len(frames)
    frameDelta = frameBasis - (frameBasis * (1.0 - framePadding))
    framePadding = frameBasis * (1.0 - framePadding)
    texCoords[0] = (0, bgScale[2] * (frameDelta + framePadding))
    texCoords[1] = (1, bgScale[2] * (frameDelta + framePadding))
    texCoords[2] = (1, bgScale[2] * (framePadding))
    texCoords[3] = (0, bgScale[2] * (framePadding))
    uv_layer = mesh.uv_layers["uv_" + textureName]
    for loop in mesh.loops:
        uv_layer.data[loop.index].uv = texCoords[loop.vertex_index]

    return mesh, frames, frameBasis


def buildBackgroundPlaneMesh(textureName, sizeX, sizeY):
    scaleX = sizeX / 16.0
    scaleY = sizeY / 16.0
    offset = 0.08

    verts = [
        (offset, -0.5 * scaleX,  0.5 * scaleY),
        (offset, 0.5 * scaleX,  0.5 * scaleY),
        (offset, 0.5 * scaleX, -0.5 * scaleY),
        (offset, -0.5 * scaleX, -0.5 * scaleY),
    ]

    texCoords = [
        (0, 1),
        (1, 1),
        (1, 0),
        (0, 0),
    ]

    indices = [(0, 1, 2), (2, 3, 0)]

    mesh = bpy.data.meshes.new('BPLANE-' + textureName)
    mesh.from_pydata(verts, [], indices)
    mesh.validate(verbose=True)
    mesh.flip_normals()

    uv_layer = mesh.uv_layers.new(name="uv_" + textureName)
    for loop in mesh.loops:
        uv_layer.data[loop.index].uv = texCoords[loop.vertex_index]

    return mesh, texCoords

TIME_CONSTANT = 10000000.0
FPS = 24

def buildBackgroundPlane(bgPlane, bgScale):
    textureName = bgPlane.attrib['textureName']

    if bgPlane.attrib['animated'] == "True":
        print("Reading animated BG: " + bgPlane.attrib['textureName'])
        imagePath = BACKGROUND_PLANES + "/" + textureName.replace("\\", "/").lower() + ".ani.png"
        image = bpy.data.images.load(imagePath)
        mesh, frames, frameBasis = buildAnimatedBackgroundPlane(bgPlane, bgScale)
    else:
        imagePath = BACKGROUND_PLANES + "/" + textureName.replace("\\", "/").lower() + ".png"
        image = bpy.data.images.load(imagePath)
        mesh, _ = buildBackgroundPlaneMesh(textureName, image.size[0], image.size[1])

    bgMaterial, texImage = buildMaterial('bplane: ' + textureName, image, returnTexNode=True)
    if bgPlane.attrib['doubleSided'] != "True":
        bgMaterial.use_backface_culling = True

    if bgPlane.attrib['animated'] == "True":
        mappingNode = bgMaterial.node_tree.nodes.new("ShaderNodeMapping")
        coordNode = bgMaterial.node_tree.nodes.new("ShaderNodeTexCoord")
        bgMaterial.node_tree.links.new(coordNode.outputs[2], mappingNode.inputs[0]) # UV -> Vector
        bgMaterial.node_tree.links.new(mappingNode.outputs[0], texImage.inputs[0]) # Mapping -> Tex
        path_from_id = mappingNode.inputs[1].path_from_id("default_value")
        driver = bgMaterial.node_tree.driver_add(path_from_id, 1).driver
        duration_in_seconds = frames[0]['duration'] / TIME_CONSTANT
        frame_dividend = duration_in_seconds * FPS
        driver.expression = "floor(frame / " + str(frame_dividend) + ") * -" + str(frameBasis)

    return bgMaterial, mesh


nodeGroups = {}
def buildMaterial(name, image, nodeGroup='fez', returnTexNode=False):

    mat = bpy.data.materials.get(name)
    if mat is not None:
        if returnTexNode:
            #texImage = mat.node_tree.nodes.get('ShaderNodeTexImage')
            # Iterate through each node in the node tree
            texImage = None
            for node in mat.node_tree.nodes:
                # Check if the node is a texture image node
                if node.type == 'TEX_IMAGE':
                    texImage = node
                    break
            return mat, texImage
        return mat

    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True

    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.interpolation = 'Closest'
    if isinstance(image, str):
        texImage.image = bpy.data.images.load(image)
    else:
        texImage.image = image

    nodeGroupNode = mat.node_tree.nodes.new('ShaderNodeGroup')
    if nodeGroup not in nodeGroups:
        nodeTree = bpy.data.node_groups.new(name=nodeGroup, type='ShaderNodeTree')

        bsdf = nodeTree.nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.inputs[7].default_value = 1

        nodeTree.interface.new_socket(name="Color", in_out='INPUT', socket_type="NodeSocketColor")
        nodeTree.interface.new_socket(name="Alpha", in_out='INPUT', socket_type="NodeSocketFloat")
        roughness = nodeTree.interface.new_socket(name="Roughness", in_out='INPUT', socket_type="NodeSocketFloat")

        roughness.default_value = 1.0

        inputNode = nodeTree.nodes.new('NodeGroupInput')

        nodeTree.links.new(bsdf.inputs['Base Color'], inputNode.outputs[0])
        nodeTree.links.new(bsdf.inputs['Alpha'], inputNode.outputs[1])
        nodeTree.links.new(bsdf.inputs['Roughness'], inputNode.outputs[2])

        nodeTree.interface.new_socket(name="Shader", in_out='OUTPUT', socket_type="NodeSocketShader")
        outputNode = nodeTree.nodes.new('NodeGroupOutput')

        nodeTree.links.new(bsdf.outputs['BSDF'], outputNode.inputs[0])
        nodeGroups[nodeGroup] = nodeTree

    nodeGroupNode.node_tree = nodeGroups[nodeGroup]

    mat.node_tree.nodes.remove(mat.node_tree.nodes.get('Principled BSDF'))

    mat.node_tree.links.new(nodeGroupNode.inputs[0], texImage.outputs['Color'])
    mat.node_tree.links.new(nodeGroupNode.inputs[1], texImage.outputs['Alpha'])

    output = mat.node_tree.nodes["Material Output"]
    mat.node_tree.links.new(output.inputs[0], nodeGroupNode.outputs[0])

    mat.blend_method = 'CLIP'

    if returnTexNode:
        return mat, texImage
    return mat

def addAo(aoName):
    aoName = aoName + "ao"
    mesh, aoMaterial = buildArtObject(aoName)
    obj = bpy.data.objects.new(aoName, mesh)
    obj.active_material = aoMaterial
    bpy.context.scene.collection.objects.link(obj)
    return obj

def buildLevel(index, levelName):
    levelPath = LEVELS + "/" + levelName.lower() + ".xml"
    levelXml = ET.parse(levelPath).getroot()

    trileSetName = levelXml.attrib['trileSetName']
    trileSet, trileImage = openTrileSet(trileSetName)
    trileMaterial = buildMaterial(name='trile: ' + trileSetName, image=trileImage, nodeGroup='trile')

    trileCollection = bpy.data.collections.new(name='{:02} {}: triles'.format(index, levelName))
    bpy.context.scene.collection.children.link(trileCollection)
    aoCollection = bpy.data.collections.new(name='{:02} {}: art objects'.format(index, levelName))
    bpy.context.scene.collection.children.link(aoCollection)
    bgCollection = bpy.data.collections.new(name='{:02} {}: bg planes'.format(index, levelName))
    bpy.context.scene.collection.children.link(bgCollection)

    print("Building triles...")
    for trile in levelXml.findall('Triles/Entry'):
        position = vec3(trile.find('TrileEmplacement'))
        instanceXml = trile.find('TrileInstance')

        trileId = instanceXml.attrib['trileId']
        orientation = int(instanceXml.attrib['orientation'])
        trilePosition = vec3(instanceXml.find('Position/Vector3'))

        if int(trileId) < 0:
            continue

        tData = trileSet[trileId]
        if 'Collision' in tData['mesh_name']:
            continue

        obj = bpy.data.objects.new(tData['mesh_name'], tData['mesh'])
        obj.location = trilePosition
        obj.rotation_euler = (0, 0, orientations[orientation])
        trileCollection.objects.link(obj)
        obj.active_material = trileMaterial

    print("Building art objects...")
    for aoXml in levelXml.findall('ArtObjects/Entry/ArtObjectInstance'):
        mesh, aoMaterial = buildArtObject(aoXml.attrib['name'])

        aoPosition = v3d(vec3(aoXml.find('Position/Vector3')), -0.5)
        aoRotation = vec4(aoXml.find('Rotation/Quaternion'))
        aoScale = vec3(aoXml.find('Scale/Vector3'))
        aoOrigin = vec3(aoXml.find('ArtObjectActorSettings/RotationCenter/Vector3'))

        obj = bpy.data.objects.new(aoXml.attrib['name'], mesh)
        obj.location = aoPosition
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = aoRotation
        obj.scale = aoScale

        aoCollection.objects.link(obj)
        obj.active_material = aoMaterial

    camera_data = bpy.data.cameras.new(name='Camera')
    camera = bpy.data.objects.new("Camera", camera_data)
    camera.location = (10, -12, 18)
    camera.rotation_euler = (90 * radPi, 0, 0)
    bpy.context.scene.collection.objects.link(camera)
    bpy.context.scene.camera = camera

    print("Building background planes...")
    for bgPlane in levelXml.findall('BackgroundPlanes/Entry/BackgroundPlane'):
        texName = bgPlane.attrib['textureName']
        opacity = bgPlane.attrib['opacity']

        bgPosition = v3d(vec3(bgPlane.find('Position/Vector3')), -0.5)
        bgRotation = vec4(bgPlane.find('Rotation/Quaternion'))
        bgScale = vec3(bgPlane.find('Scale/Vector3'))

        bgMaterial, bgMesh = buildBackgroundPlane(bgPlane, bgScale)
        if bgMesh is None:
            continue

        obj = bpy.data.objects.new(texName, bgMesh)
        obj.location = bgPosition
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = bgRotation
        obj.scale = bgScale

        if bgPlane.attrib['billboard'] == "True":
            constraint = obj.constraints.new(type='TRACK_TO')
            constraint.target = camera
            constraint.track_axis = "TRACK_NEGATIVE_X"
            constraint.up_axis = "UP_Z"

            constraint = obj.constraints.new(type='LIMIT_ROTATION')
            constraint.use_limit_y = True

        bgCollection.objects.link(obj)
        obj.active_material = bgMaterial



def vec2(root):
    return (float(root.attrib['x']), float(root.attrib['y']))

def vec3(root):
    return (float(root.attrib['z']), float(root.attrib['x']), float(root.attrib['y']))

def vec4(root):
    return (float(root.attrib['w']), float(root.attrib['z']), float(root.attrib['x']), float(root.attrib['y']))

def v3d(v3, d):
    return (v3[0] + d, v3[1] + d, v3[2] + d)

def flip2(v2):
    return (v2[0], 1.0 - v2[1])

def readGeometry(root):
    shaderXml = root.find('ShaderInstancedIndexedPrimitives')
    verts = []
    for ntex in shaderXml.findall('Vertices/VertexPositionNormalTextureInstance'):
        prim = {}
        prim['position'] = vec3(ntex.find('Position/Vector3'))
        prim['normal'] = normals[int(ntex.find('Normal').text)]
        prim['textureCoord'] = flip2(vec2(ntex.find('TextureCoord/Vector2')))
        verts.append(prim)

    indices = []
    for indexXml in shaderXml.findall('Indices/Index'):
        indices.append(int(indexXml.text))

    formattedIndices = list(map(list, zip(*[iter(indices)]*3)))
    return verts, formattedIndices, []

#clearData()
#addAo("letter_cube")
buildLevel(1, "waterfall")
