import maya.OpenMaya as OpenMaya


def get_selectionlist(clear=True):
    """ Get selection list. """

    slist = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(slist)

    if clear is True:
        OpenMaya.MGlobal.clearSelectionList()
    else:
        pass

    return slist


def select_triangles():
    """ Select triangles """

    slist = get_selectionlist()
    for i in range(slist.length()):
        m_dagpath = OpenMaya.MDagPath()
        m_obj = OpenMaya.MObject()
        slist.getDagPath(i, m_dagpath, m_obj)
        edge_list = OpenMaya.MIntArray()
        try:
            iter_faces = OpenMaya.MItMeshPolygon(m_dagpath)
            while not iter_faces.isDone():
                iter_faces.getEdges(edge_list)
                edge_count = edge_list.length()
                if edge_count == 3:
                    component = iter_faces.currentItem()
                    OpenMaya.MGlobal.select(m_dagpath, component)
                iter_faces.next()
        except RuntimeError:
            OpenMaya.MGlobal.displayInfo(
                "Selected object is not mesh.")
            return None


def select_ngons():
    """ Select n-sided faces. """

    slist = get_selectionlist()
    for i in range(slist.length()):
        m_dagpath = OpenMaya.MDagPath()
        m_obj = OpenMaya.MObject()
        slist.getDagPath(i, m_dagpath, m_obj)
        edge_list = OpenMaya.MIntArray()
        try:
            iter_faces = OpenMaya.MItMeshPolygon(m_dagpath)
            while not iter_faces.isDone():
                iter_faces.getEdges(edge_list)
                edge_count = edge_list.length()
                if edge_count >= 5:
                    component = iter_faces.currentItem()
                    OpenMaya.MGlobal.select(m_dagpath, component)
                iter_faces.next()
        except RuntimeError:
            OpenMaya.MGlobal.displayInfo(
                "Selected object is not mesh.")
            return None


def select_lamina_faces():
    """ Select lamina faces. """

    slist = get_selectionlist()
    for i in range(slist.length()):
        m_dagpath = OpenMaya.MDagPath()
        m_obj = OpenMaya.MObject()
        slist.getDagPath(i, m_dagpath, m_obj)
        iter_faces = OpenMaya.MItMeshPolygon(m_dagpath)
        try:
            while not iter_faces.isDone():
                lamina_checker = iter_faces.isLamina()
                if lamina_checker is True:
                    component = iter_faces.currentItem()
                    OpenMaya.MGlobal.select(m_dagpath, component)
                iter_faces.next()
        except RuntimeError:
            OpenMaya.MGlobal.displayInfo(
                "Selected object is not mesh.")
            return None


def select_concave_faces():
    """ Select concave faces. """

    slist = get_selectionlist()
    for i in range(slist.length()):
        m_dagpath = OpenMaya.MDagPath()
        m_obj = OpenMaya.MObject()
        slist.getDagPath(i, m_dagpath, m_obj)
        try:
            iter_faces = OpenMaya.MItMeshPolygon(m_dagpath)
            while not iter_faces.isDone():
                convex_checker = iter_faces.isConvex()
                if convex_checker is False:
                    component = iter_faces.currentItem()
                    OpenMaya.MGlobal.select(m_dagpath, component)
                iter_faces.next()
        except RuntimeError:
            OpenMaya.MGlobal.displayInfo(
                "Selected object is not mesh.")
            return None


def select_badextraordianry_vtx():
    """ Select badextraordianry vertices. """

    slist = get_selectionlist()
    utils = OpenMaya.MScriptUtil()
    ptr_int = utils.asIntPtr()
    m_dagpath = OpenMaya.MDagPath()
    for i in range(slist.length()):
        m_obj = OpenMaya.MObject()
        slist.getDagPath(i, m_dagpath, m_obj)
        try:
            iter_verts = OpenMaya.MItMeshVertex(m_dagpath)
            while not iter_verts.isDone():
                iter_verts.numConnectedEdges(ptr_int)
                edge_count = utils.getInt(ptr_int)
                if edge_count > 5:
                    component = iter_verts.currentItem()
                    OpenMaya.MGlobal.select(m_dagpath, component)
                iter_verts.next()
        except RuntimeError:
            OpenMaya.MGlobal.displayInfo(
                "Selected object is not mesh.")
            return None


def select_non_planar_faces():
    """ Select holes. This is slow. Shouldn't be used."""

    slist = get_selectionlist()
    for i in range(slist.length()):
        m_dagpath = OpenMaya.MDagPath()
        m_obj = OpenMaya.MObject()
        slist.getDagPath(i, m_dagpath, m_obj)
        try:
            iter_faces = OpenMaya.MItMeshPolygon(m_dagpath)
            while not iter_faces.isDone():
                planar_checker = iter_faces.isPlanar()
                if planar_checker is True:
                    component = iter_faces.currentItem()
                    OpenMaya.MGlobal.select(m_dagpath, component)
                iter_faces.next()
        except RuntimeError:
            OpenMaya.MGlobal.displayInfo(
                "Selected object is not mesh.")
            return None
