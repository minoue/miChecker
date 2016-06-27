import maya.OpenMaya as OpenMaya
import maya.cmds as cmds
from collections import Counter


# DataDict structure (dict)
# Key : fullpath of each node
# item : dict of errors:
#        key : name of error
#        item : list of components
#
# For example,
# {u'|group3|group1|pSphere1':
#     {'laminaFaces': [],
#      'smoothPreview': [],
#      'intermediateObject': [],
#      'nonManifoldEdges': [],
#      'opposite': [],
#      'shapeNames': [u'|group3|group1|pSphere1'],
#      'lockedChannels': [],
#      'duplicateNames': [],
#      'transform': [u'|group3|group1|pSphere1'],
#      'keyframes': [],
#      'defaultShader': [],
#      'nGons': [],
#      'intermediateObj': [],
#      'concaveFaces': [],
#      'doubleSided': [],
#      'geoSuffix': [],
#      'history':[u'group1|pSphere1|pSphereShape1', u'polySphere1'],
#      'badExtraordinaryVtx': []],
#      'triangles': []],
#      'nonManifoldVtx': []},
#  u'|group3|group1|pSphere2':
#     {'laminaFaces': [],
#      'smoothPreview': [],
#      'intermediateObject': [],
#      ...


# nodeList : List of all shape and transform nodes


def extend_to_shape(path):

    slist = OpenMaya.MSelectionList()
    dagpath = OpenMaya.MDagPath()
    slist.add(path)
    slist.getDagPath(0, dagpath)
    try:
        dagpath.extendToShape()
        fullpath = dagpath.fullPathName()
        return fullpath
    except RuntimeError:
        return None


def get_selection_list(nodeList):
    slist = OpenMaya.MSelectionList()
    for i in nodeList:
        slist.add(i)
    return slist


def check_mesh(dagpath):
    """ Check if current item is mesh. """

    pass


def get_history(dataDict, nodeList, badNodeList, *args):
    for i in nodeList:
        hist = cmds.listHistory(i)
        if len(hist) == 1:
            dataDict[i]['history'] = []
        else:
            dataDict[i]['history'] = hist
            badNodeList.append(i)


def get_transform(dataDict, nodeList, badNodeList, *args):

    zeros = [(0.0, 0.0, 0.0)]
    zeros_s = [(1.0, 1.0, 1.0)]

    for i in nodeList:
        trans = cmds.getAttr(i + ".translate")
        rotation = cmds.getAttr(i + ".rotate")
        scale = cmds.getAttr(i + ".scale")
        if (trans == zeros and rotation == zeros and scale == zeros_s):
            dataDict[i]['transform'] = []
        else:
            dataDict[i]['transform'] = [i]
            badNodeList.append(i)


def get_badextraordianry_vtx(dataDict, nodeList, badNodeList, *args):
    """ Store a list of badextravtx to the dict """

    slist = get_selection_list(nodeList)

    utils = OpenMaya.MScriptUtil()
    ptr_int = utils.asIntPtr()

    m_dagpath = OpenMaya.MDagPath()

    for i in range(slist.length()):
        slist.getDagPath(i, m_dagpath)
        vlist = []

        try:
            iter_verts = OpenMaya.MItMeshVertex(m_dagpath)
        except RuntimeError:
            # If it's not mesh
            continue

        while not iter_verts.isDone():
            iter_verts.numConnectedEdges(ptr_int)
            edge_count = utils.getInt(ptr_int)
            index = iter_verts.index()
            if edge_count > 5:
                fullpath = m_dagpath.fullPathName() + ".vtx[%s]" % index
                vlist.append(fullpath)
            iter_verts.next()
        if len(vlist) != 0:
            badNodeList.append(m_dagpath.fullPathName())

        dataDict[m_dagpath.fullPathName()]['badExtraordinaryVtx'] = vlist


def get_triangles(dataDict, nodeList, badNodeList, *args):
    """ Store a list of triangles to the dict """

    slist = get_selection_list(nodeList)

    for i in range(slist.length()):
        m_dagpath = OpenMaya.MDagPath()
        slist.getDagPath(i, m_dagpath)
        edge_list = OpenMaya.MIntArray()
        flist = []

        try:
            iter_faces = OpenMaya.MItMeshPolygon(m_dagpath)
        except RuntimeError:
            # If it's not mesh
            continue

        iter_faces = OpenMaya.MItMeshPolygon(m_dagpath)
        while not iter_faces.isDone():
            iter_faces.getEdges(edge_list)
            edge_count = edge_list.length()
            index = iter_faces.index()
            if edge_count == 3:
                fullpath = m_dagpath.fullPathName() + ".f[%s]" % index
                flist.append(fullpath)
            iter_faces.next()
        if len(flist) != 0:
            badNodeList.append(m_dagpath.fullPathName())

        dataDict[m_dagpath.fullPathName()]['triangles'] = flist


def get_ngons(dataDict, nodeList, badNodeList, *args):
    """ Store a list of ngons to the dict """

    slist = get_selection_list(nodeList)

    for i in range(slist.length()):
        m_dagpath = OpenMaya.MDagPath()
        slist.getDagPath(i, m_dagpath)
        edge_list = OpenMaya.MIntArray()
        flist = []

        try:
            iter_faces = OpenMaya.MItMeshPolygon(m_dagpath)
        except RuntimeError:
            # If it's not mesh
            continue

        while not iter_faces.isDone():
            iter_faces.getEdges(edge_list)
            edge_count = edge_list.length()
            index = iter_faces.index()
            if edge_count >= 5:
                fullpath = m_dagpath.fullPathName() + ".f[%s]" % index
                flist.append(fullpath)
            iter_faces.next()

        if len(flist) != 0:
            badNodeList.append(m_dagpath.fullPathName())

        dataDict[m_dagpath.fullPathName()]['nGons'] = flist


def get_lamina_faces(dataDict, nodeList, badNodeList, *args):
    """ Store a list of lamina faces to the dict """

    slist = get_selection_list(nodeList)

    for i in range(slist.length()):
        m_dagpath = OpenMaya.MDagPath()
        slist.getDagPath(i, m_dagpath)
        flist = []

        try:
            iter_faces = OpenMaya.MItMeshPolygon(m_dagpath)
        except RuntimeError:
            # If it's not mesh
            continue

        while not iter_faces.isDone():
            lamina_checker = iter_faces.isLamina()
            index = iter_faces.index()
            if lamina_checker is True:
                fullpath = m_dagpath.fullPathName() + ".f[%s]" % index
                flist.append(fullpath)
            iter_faces.next()
        if len(flist) != 0:
            badNodeList.append(m_dagpath.fullPathName())

        dataDict[m_dagpath.fullPathName()]['laminaFaces'] = flist


def get_concave_faces(dataDict, nodeList, badNodeList, *args):
    """ Store a list of lamina faces to the dict """

    slist = get_selection_list(nodeList)

    for i in range(slist.length()):
        m_dagpath = OpenMaya.MDagPath()
        slist.getDagPath(i, m_dagpath)
        flist = []

        try:
            iter_faces = OpenMaya.MItMeshPolygon(m_dagpath)
        except RuntimeError:
            # If it's not mesh
            continue

        iter_faces = OpenMaya.MItMeshPolygon(m_dagpath)
        while not iter_faces.isDone():
            convex_checker = iter_faces.isConvex()
            index = iter_faces.index()
            if convex_checker is False:
                fullpath = m_dagpath.fullPathName() + ".f[%s]" % index
                flist.append(fullpath)
            iter_faces.next()

        if len(flist) != 0:
            badNodeList.append(m_dagpath.fullPathName())

        dataDict[m_dagpath.fullPathName()]['concaveFaces'] = flist


def get_nonmanifold_vertices(dataDict, nodeList, badNodeList, *args):
    """ Store a list of non manifold vertices. """

    for i in nodeList:
        verts = cmds.polyInfo(i, nonManifoldVertices=True)
        dataDict[i]['nonManifoldVtx'] = verts

        if verts is not None:
            badNodeList.append(i)

        dataDict[i]['nonManifoldVtx'] = []


def get_nonmanifold_edges(dataDict, nodeList, badNodeList, *args):
    """ Store a list of non manifold edges. """

    for i in nodeList:
        edges = cmds.polyInfo(i, nonManifoldEdges=True)
        dataDict[i]['nonManifoldEdges'] = edges

        if edges is not None:
            badNodeList.append(i)

        dataDict[i]['nonManifoldEdges'] = []


def get_opposite(dataDict, nodeList, badNodeList, *args):

    for i in nodeList:
        shape = extend_to_shape(i)
        if shape is None:
            continue
        else:
            oppositeStatus = cmds.getAttr(i + ".opposite")
            if oppositeStatus is True:
                dataDict[i]['opposite'] = [i]
                badNodeList.append(i)
            else:
                dataDict[i]['opposite'] = []


def get_doublesided(dataDict, nodeList, badNodeList, *args):

    for i in nodeList:
        shape = extend_to_shape(i)
        if shape is None:
            continue
        else:
            oppositeStatus = cmds.getAttr(i + ".doubleSided")
            if oppositeStatus is True:
                dataDict[i]['doubleSided'] = []
            else:
                dataDict[i]['doubleSided'] = [i]
                badNodeList.append(i)


def get_intermediate_obj(dataDict, nodeList, badNodeList, *args):

    for i in nodeList:
        shape = extend_to_shape(i)
        if shape is None:
            continue
        else:
            oppositeStatus = cmds.getAttr(i + ".intermediateObject")
            if oppositeStatus is True:
                dataDict[i]['intermediateObject'] = [i]
                badNodeList.append(i)
            else:
                dataDict[i]['intermediateObject'] = []


def get_bad_shapenames(dataDict, nodeList, badNodeList, *args):

    for i in nodeList:
        shape = extend_to_shape(i)
        if shape is None:
            continue
        else:
            shape = shape.split("|")[-1]

        rightShape = i.split("|")[-1] + "Shape"
        if shape == rightShape:
            dataDict[i]['shapeNames'] = []
        else:
            dataDict[i]['shapeNames'] = [i]
            badNodeList.append(i)


def get_duplicated_names(dataDict, nodeList, badNodeList, *args):
    shortNames = [i.split("|")[-1] for i in nodeList]
    collection = Counter(shortNames)
    duplicateNamesList = [i for i in collection if collection[i] > 1]

    for i in nodeList:
        dataDict[i]['duplicateNames'] = duplicateNamesList
        badNodeList.append(i)


def get_smooth_mesh(dataDict, nodeList, badNodeList, *args):

    for i in nodeList:
        shape = extend_to_shape(i)
        if shape is None:
            pass
        else:
            smoothMesh = cmds.getAttr(i + ".displaySmoothMesh")
            if smoothMesh == 1:
                dataDict[i]['smoothPreview'] = [i]
                badNodeList.append(i)
            elif smoothMesh == 2:
                dataDict[i]['smoothPreview'] = [i]
                badNodeList.append(i)
            else:
                dataDict[i]['smoothPreview'] = []


def get_shader(dataDict, nodeList, badNodeList, *args):
    for i in nodeList:
        shape = extend_to_shape(i)
        if shape is None:
            pass
        else:
            try:
                sg = cmds.listConnections(shape, type='shadingEngine')[0]
                if sg == 'initialShadingGroup':
                    dataDict[i]['defaultShader'] = []
                else:
                    dataDict[i]['defaultShader'] = [sg]
                    badNodeList.append(i)
            except TypeError:
                # INTERMEDIATE OBJECT CAN'T GET SHADINIG GROUP
                # NEED TO REMOVE INTERMEDIATE OBJECT FIRST
                pass


def get_geo_suffix(dataDict, nodeList, badNodeList, suffix):

    for i in nodeList:
        currentSuffix = "_" + i.split("_")[-1]
        if currentSuffix in suffix:
            pass
        else:
            dataDict[i]['geoSuffix'] = [i]
            badNodeList.append(i)


def get_locked_channels(dataDict, nodeList, badNodeList, *args):
    for i in nodeList:
        attrs = cmds.listAttr(i)
        for att in attrs:
            try:
                lockState = cmds.getAttr(i + "." + att, lock=True)
                if lockState is True:
                    dataDict[i]['lockedChannels'] = [i]
                    badNodeList.append(i)
                    return
                else:
                    pass
            except ValueError:
                pass


def get_keyframes(dataDict, nodeList, badNodeList, *args):
    for i in nodeList:
        attrs = cmds.listAttr(i)
        for att in attrs:
            try:
                keyState = cmds.keyframe(i + "." + att, q=True)
                if keyState is None:
                    pass
                else:
                    dataDict[i]['keyframes'] = [i]
                    badNodeList.append(i)
                    return
            except ValueError:
                pass
