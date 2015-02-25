import maya.cmds as cmds
import maya.mel as mel
import pymel.all as pm
from collections import Counter


class Commands(object):

    def __init__(self, checkList):
        super(Commands, self).__init__()
        self.checkList = checkList

        self.rootPath = None
        self.children = None
        self.allTransforms = None
        self.allShapes = None

    def initData(self, path):
        self.rootPath = str(path)
        self.children = cmds.listRelatives(self.rootPath, ad=True, path=True, fullPath=True)
        self.allTransforms = cmds.listRelatives(self.rootPath, ad=True, path=True, fullPath=True, type='transform')
        self.allShapes = cmds.listRelatives(self.rootPath, ad=True, path=True, fullPath=True, type='mesh')
        if self.children is None:
            self.children = []
        self.children.append(self.rootPath)
        if self.allTransforms is None:
            self.allTransforms = []
        if self.allShapes is None:
            self.allShapes = []
        
        dataDict = {}
        for item in self.children:
            dataDict[item] = {}
            for check in self.checkList:
                dataDict[item][check] = []

        self.dataDict = dataDict

        return dataDict, self.children, self.allTransforms, self.allShapes

    def searchHistory(self, mesh):
        historyList = cmds.listHistory(mesh)
        idGroup = [i for i in historyList if cmds.nodeType(i) == "groupId"]
        objectSet = [i for i in historyList if cmds.nodeType(i) == "objectSet"]
        historyList = [i for i in historyList if i not in idGroup]
        historyList = [i for i in historyList if i not in objectSet]
        if len(historyList) == 1:
            historyList = []
        return historyList

    def searchTransformations(self, transform):
        transformList = []
        tx = cmds.getAttr(transform + ".translateX")
        ty = cmds.getAttr(transform + ".translateY")
        tz = cmds.getAttr(transform + ".translateZ")
        rx = cmds.getAttr(transform + ".rotateX")
        ry = cmds.getAttr(transform + ".rotateY")
        rz = cmds.getAttr(transform + ".rotateZ")
        sx = cmds.getAttr(transform + ".scaleX")
        sy = cmds.getAttr(transform + ".scaleY")
        sz = cmds.getAttr(transform + ".scaleZ")
        tlist = [tx, ty, tz].count(0.0)
        rlist = [rx, ry, rz].count(0.0)
        slist = [sx, sy, sz].count(1.0)
        if [tlist, rlist, slist] == [3, 3, 3]:
            transformList = []
        else:
            transformList = [transform]
        return transformList

    def searchTriangles(self, mesh):
        trianglesList = []
        faceCount = cmds.polyEvaluate(mesh, face=True)
        allFaces = [mesh + ".f[%s]" % num for num in range(faceCount)]
        for face in allFaces:
            edges = cmds.polyInfo(
                face, faceToEdge=True)[0].split(":")[-1].split()
            if len(edges) == 3:
                trianglesList.append(face)
        return trianglesList

    def searchNgons(self, mesh):
        ngonsList = []
        faceCount = cmds.polyEvaluate(mesh, face=True)
        allFaces = [mesh + ".f[%s]" % num for num in range(faceCount)]
        for face in allFaces:
            edges = cmds.polyInfo(
                face, faceToEdge=True)[0].split(":")[-1].split()
            if len(edges) >= 5:
                ngonsList.append(face)
        return ngonsList

    def searchNonManifoldVtx(self, mesh):
        nonManifoldVtxList = cmds.polyInfo(mesh, nonManifoldVertices=True)
        if nonManifoldVtxList is None:
            nonManifoldVtxList = []
        return nonManifoldVtxList

    def searchnonManifoldEdges(self, mesh):
        nonManifoldEdgesList = cmds.polyInfo(mesh, nonManifoldEdges=True)
        if nonManifoldEdgesList is None:
            nonManifoldEdgesList = []
        return nonManifoldEdgesList

    def searchLaminaFaces(self, mesh):
        laminaFacesList = cmds.polyInfo(mesh, laminaFaces=True)
        if laminaFacesList is None:
            laminaFacesList = []
        return laminaFacesList

    def searchConcaveFaces(self, mesh):
        cmds.select(mesh, r=True)
        mel.eval("PolySelectConvert 1")
        cmds.polySelectConstraint(mode=3, convexity=1, type=8)
        cmds.polySelectConstraint(mode=0, convexity=0, type=8)
        concaveFacesList = cmds.ls(sl=True, fl=True, r=True)
        cmds.select(d=True)
        return concaveFacesList

    def searchBadExtraordinaryVtx(self, mesh):
        try:
            cmds.select(mesh, r=True)
            mel.eval('PolySelectConvert 3')
            selected = pm.selected(fl=True)
            badExtraordinaryVtx = [i for i
                                   in selected
                                   if len(i.connectedEdges()) > 6]
            cmds.select(d=True)
            if badExtraordinaryVtx == []:
                badExtraordinaryVtxList = []
            else:
                badExtraordinaryVtxList = [str(i) for i in badExtraordinaryVtx]
        except AttributeError:
            # PYMEL COMMAND GETS ERROR IF MESH IS INTERMEDIATE OBJECT
            # TEMPORARILIY SEND WITH EMPTY LIST BUT NEED TO RE-CHECK
            # ONCE INTERMEDIATE OBJECT IS CHECKED OF OR REMOVED
            badExtraordinaryVtxList = []
        return badExtraordinaryVtxList

    def searchOpposite(self, mesh):
        oppositeList = []
        oppositeStatus = cmds.getAttr(mesh + ".opposite")
        if oppositeStatus is True:
            oppositeList = [mesh]
        else:
            oppositeList = []
        return oppositeList

    def searchDoubleSided(self, mesh):
        doubleSidedList = []
        doubleSidedStatus = cmds.getAttr(mesh + ".doubleSided")
        if doubleSidedStatus is True:
            doubleSidedList = [mesh]
        else:
            doubleSidedList = []
        return doubleSidedList

    def searchIntermediateObj(self, mesh):
        intermediateObjList = []
        intermediateObjStatus = cmds.getAttr(
            mesh + ".intermediateObject")
        if intermediateObjStatus is True:
            intermediateObjList = [mesh]
        else:
            intermediateObjList = []
        return intermediateObjList

    def searchBadShapeName(self, mesh):
        badShapeNodeList = []
        meshNameShort = mesh.split("|")[-1]
        parent = cmds.listRelatives(mesh, parent=True, type='transform')[0]
        if meshNameShort == parent + "Shape":
            badShapeNodeList = []
        else:
            badShapeNodeList.append(mesh)
        return badShapeNodeList
            
    def searchDuplicateNames(self, children):
        itemName = [i.split("|")[-1] for i in children]
        collection = Counter(itemName)
        duplicateNamesList = [i for i in collection if collection[i] > 1]
        return duplicateNamesList

    def searchSmoothPreviewed(self, mesh):
        smoothPreviewList = []
        smoothPreviewStatus = cmds.getAttr(mesh + ".displaySmoothMesh")
        if smoothPreviewStatus == 0:
            smoothPreviewList = []
        elif smoothPreviewStatus == 1:
            smoothPreviewList = [mesh]
        elif smoothPreviewStatus == 2:
            smoothPreviewList = [mesh]
        else:
            pass
        return smoothPreviewList

    def searchNonDefaultShaders(self, mesh):
        nonDefaultShaderList = []
        try:
            shadingEngine = cmds.listConnections(
                mesh, type='shadingEngine')[0]
            if shadingEngine == 'initialShadingGroup':
                nonDefaultShaderList = []
            else:
                nonDefaultShaderList = [mesh]
        except TypeError:
            # INTERMEDIATE OBJECT CAN'T GET SHADINIG GROUP
            # NEED TO REMOVE INTERMEDIATE OBJECT FIRST
            nonDefaultShaderList = []
        return nonDefaultShaderList

    def searchBadSuffix(self, child, suffixList):
        geoSuffixList = []
        itemSuffix = "_" + child.split("_")[-1]
        if itemSuffix in suffixList:
            geoSuffixList = []
        else:
            geoSuffixList = [child]
        return geoSuffixList

    def searchLockedChannels(self, child):
        attrs = cmds.listAttr(child)
        lockedAttributes = []
        for att in attrs:
            try:
                lockState = cmds.getAttr(child + "." + att, lock=True)
                if lockState is True:
                    lockedAttributes.append(att)
                else:
                    pass
            except ValueError:
                pass
        return lockedAttributes

    def searchKeyframes(self, child):
        attrs = cmds.listAttr(child)
        keyedAttributes = []
        for att in attrs:
            try:
                keyState = cmds.keyframe(child + "." + att, q=True)
                if keyState is None:
                    pass
                else:
                    keyedAttributes.append(att)
            except ValueError:
                pass
        return keyedAttributes

    def fixHistory(self):
        for i in self.allShapes:
            try:
                cmds.delete(i, ch=True)
            except ValueError:
                pass

    def fixTransform(self):
        for i in self.allTransforms:
            try:
                cmds.makeIdentity(i, apply=True, t=1, r=1, s=1, n=0)
            except ValueError:
                pass

    def fixOpposite(self):
        for i in self.allShapes:
            try:
                cmds.setAttr(i + ".opposite", 0)
            except ValueError:
                pass

    def fixDoubleSided(self):
        for i in self.allShapes:
            try:
                cmds.setAttr(item + ".doubleSided", 1)
            except ValueError:
                pass

    def fixIntermediateObj(self):
        for i in self.allShapes:
            try:
                if cmds.getAttr(i + ".intermediateObject") == True:
                    cmds.delete(i)
            except ValueError:
                pass

    def fixShapeNames(self):
        for i in self.allShapes:
            if cmds.getAttr(i + ".intermediateObject") == True:
                # Ignore if it's intermediateobj
                pass
            else:
                parent = cmds.listRelatives(i, parent=True, type='transform')[0]
                if i == parent + "Shape":
                    pass
                else:
                    cmds.rename(i, parent + "Shape")

    def fixSmoothPreview(self):
        for i in self.allShapes:
            try:
                cmds.setAttr(i + ".displaySmoothMesh", 0)
            except ValueError:
                pass

    def fixShader(self):
        for i in self.allShapes:
            try:
                cmds.sets(i, forceElement='initialShadingGroup', edit=True)
            except ValueError:
                pass

    def fixLockedChannels(self):
        for i in self.children:
            allAttributes = cmds.listAttr(child)
            for att in allAttributes:
                try:
                    cmds.setAttr(child + "." + att, lock=False)
                except:
                    pass

    def fixKeyframes(self):
        for i in self.allTransforms:
            try:
                cmds.cutKey(i)
            except:
                pass

