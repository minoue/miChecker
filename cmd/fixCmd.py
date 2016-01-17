import maya.cmds as cmds
import maya.OpenMaya as OpenMaya


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


def delete_history(nodeList):
    for i in nodeList:
        try:
            cmds.delete(i, ch=True)
        except ValueError:
            pass


def freeze_transform(nodeList):
    print nodeList
    for i in nodeList:
        cmds.makeIdentity(i, apply=True, t=1, r=1, s=1, n=0)


def fix_opposite(nodeList):
    for i in nodeList:
        shape = extend_to_shape(i)
        if shape is None:
            continue
        else:
            cmds.setAttr(i + ".opposite", 0)


def fix_doublesided(nodeList):
    for i in nodeList:
        shape = extend_to_shape(i)
        if shape is None:
            continue
        else:
            cmds.setAttr(i + ".doubleSided", 1)


def delete_intermediate_obj(nodeList):
    for i in nodeList:
        shape = extend_to_shape(i)
        if shape is None:
            continue
        else:
            if cmds.getAttr(shape + ".intermediateObject") is True:
                cmds.delete(shape)


def fix_shape_names(nodeList):
    for i in nodeList:
        shape = extend_to_shape(i)
        if shape is None:
            continue
        else:
            newShapeName = i.split("|")[-1] + "Shape"
            cmds.rename(shape, newShapeName)


def fix_smooth_preview(nodeList):
    for i in nodeList:
        shape = extend_to_shape(i)
        if shape is None:
            continue
        else:
            cmds.setAttr(i + ".displaySmoothMesh", 0)


def assign_default_shader(nodeList):
    for i in nodeList:
        try:
            cmds.sets(i, forceElement='initialShadingGroup', edit=True)
        except ValueError:
            pass


def unlock_channels(nodeList):
    for i in nodeList:
        allAttributes = cmds.listAttr(i)
        for att in allAttributes:
            try:
                cmds.setAttr(i + "." + att, lock=False)
            except:
                pass


def delete_keyframes(nodeList):
    for i in nodeList:
        try:
            cmds.cutKey(i)
        except:
            pass
