from PySide import QtCore, QtGui
from functools import partial
import maya.OpenMayaUI as mui
import maya.cmds as cmds
import sys
import shiboken
import command
reload(command)


def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return shiboken.wrapInstance(long(ptr), QtGui.QWidget)


class CustomBoxLayout(QtGui.QBoxLayout):
    def __init__(self, parent=None):
        super(CustomBoxLayout, self).__init__(parent)

        self.setSpacing(2)
        self.setContentsMargins(2, 2, 2, 2)


class ModelChecker(QtGui.QDialog):
    """ Main UI class """

    def closeExistingWindow(self):
        for qt in QtGui.QApplication.topLevelWidgets():
            try:
                if qt.__class__.__name__ == self.__class__.__name__:
                    qt.close()
            except:
                pass

    def __init__(self, parent=getMayaWindow()):
        self.closeExistingWindow()
        super(ModelChecker, self).__init__(parent)

        self.setWindowTitle('Model Checker')
        self.setWindowFlags(QtCore.Qt.Tool)

        self.checkList = [
            'history',
            'transform',
            'triangles',
            'nGons',
            'nonManifoldVtx',
            'nonManifoldEdges',
            'laminaFaces',
            'concaveFaces',
            'badExtraordinaryVtx',
            'opposite',
            'doubleSided',
            'intermediateObj',
            'shapeNames',
            'duplicateNames',
            'smoothPreview',
            'defaultShader',
            'geoSuffix',
            'lockedChannels',
            'keyframes']

        self.createUI()

        self.cmd = command.Commands(self.checkList)

    def createUI(self):
        ######################
        """ Create Widgets """
        ######################

        """ Top Area Widgets """
        self.selectedLE = QtGui.QLineEdit()
        self.selectedLE.setText('model_GRP')
        self.selectBTN = QtGui.QPushButton('Select')
        self.selectBTN.clicked.connect(self.select)

        """ Check box widgets """
        for i in self.checkList:
            exec("self.%sCheckBox = QtGui.QCheckBox('%s')" % (i, i))
            exec("self.%sCheckBox.setCheckState(QtCore.Qt.Checked)" % i)
        self.badExtraordinaryVtxCheckBox.setCheckState(QtCore.Qt.Unchecked)
        self.lockedChannelsCheckBox.setCheckState(QtCore.Qt.Unchecked)
        self.keyframesCheckBox.setCheckState(QtCore.Qt.Unchecked)
        self.geoSuffixLineEdit01 = QtGui.QLineEdit("_GEP")
        self.geoSuffixLineEdit02 = QtGui.QLineEdit("_GES")
        self.geoSuffixLineEdit03 = QtGui.QLineEdit("_NRB")
        self.geoSuffixLineEdit04 = QtGui.QLineEdit("_GRP")
        self.geoSuffixLineEdit05 = QtGui.QLineEdit("_LOC")
        self.geoSuffixLineEdit06 = QtGui.QLineEdit("_PLY")
        self.resetButton = QtGui.QPushButton("Reset")
        self.resetButton.setFixedHeight(40)

        """ Bad nodes list widget """
        self.badNodeListWidget = QtGui.QListWidget()
        self.badNodeListWidget.currentItemChanged.connect(self.itemClicked)

        """ error list widgets """
        for i in self.checkList:
            exec("self.%sListWidget = QtGui.QListWidget()" % i)
            exec("self.%sListWidget.currentItemChanged.connect(self.errorClicked)" % i)
            exec("self.%sListWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)" % i)


        self.searchButton = QtGui.QPushButton()
        self.searchButton.setFixedSize(150, 150)
        self.searchButton.clicked.connect(self.search)

        """ result label wigets """
        for i in self.checkList:
            exec("self.%sResultLabel = QtGui.QLabel('%s')" % (i, i))

        """ fix button widgets """
        for i in self.checkList:
            exec("self.%sFixButton = QtGui.QPushButton()" % i)
            exec("self.%sFixButton.setFixedWidth(100)" % i)
        self.historyFixButton.setText('Delete All')
        self.transformFixButton.setText('Freeze All')
        self.trianglesFixButton.setEnabled(False)
        self.nGonsFixButton.setEnabled(False)
        self.nonManifoldVtxFixButton.setEnabled(False)
        self.nonManifoldEdgesFixButton.setEnabled(False)
        self.laminaFacesFixButton.setEnabled(False)
        self.concaveFacesFixButton.setEnabled(False)
        self.badExtraordinaryVtxFixButton.setEnabled(False)
        self.oppositeFixButton.setText('Fix All')
        self.doubleSidedFixButton.setText('Fix All')
        self.intermediateObjFixButton.setText('Delete All')
        self.shapeNamesFixButton.setText('Fix All')
        self.duplicateNamesFixButton.setEnabled(False)
        self.smoothPreviewFixButton.setText('Fix All')
        self.defaultShaderFixButton.setText('Set Lambert1')
        self.geoSuffixFixButton.setEnabled(False)
        self.lockedChannelsFixButton.setText('Unlock All')
        self.keyframesFixButton.setText('Delete All')

        """ status bar """
        self.statusBar = QtGui.QStatusBar()
        self.statusBar.showMessage("")

        #########################
        """ Layout Management """
        #########################
        topLayout = CustomBoxLayout(QtGui.QBoxLayout.LeftToRight)
        topLayout.addWidget(self.selectedLE)

        midLayout = CustomBoxLayout(QtGui.QBoxLayout.LeftToRight)

        checkBoxLayout = CustomBoxLayout(QtGui.QBoxLayout.TopToBottom)
        for i in self.checkList:
            exec("checkBoxLayout.addWidget(self.%sCheckBox)" % i)
        for num in range(6):
            exec("checkBoxLayout.addWidget(self.geoSuffixLineEdit0%s)" % str(num + 1))
        checkBoxLayout.addWidget(self.resetButton)

        scrollArea = QtGui.QScrollArea(self)
        scrollArea.setWidgetResizable(True)
        scrollAreaWidgetContents = QtGui.QWidget(scrollArea)
        scrollArea.setWidget(scrollAreaWidgetContents)
        errorListLayout = QtGui.QVBoxLayout(scrollAreaWidgetContents)
        for i in self.checkList:
            errorListLayout.addWidget(QtGui.QLabel(i))
            exec("errorListLayout.addWidget(self.%sListWidget)" % i)

        rightLayout = CustomBoxLayout(QtGui.QBoxLayout.TopToBottom)
        rightLayout.addWidget(self.searchButton)
        for i in self.checkList:
            subLayout = CustomBoxLayout(QtGui.QBoxLayout.LeftToRight)
            exec("subLayout.addWidget(self.%sResultLabel)" % i)
            exec("subLayout.addWidget(self.%sFixButton)" % i)
            exec("rightLayout.addLayout(subLayout)")

        midLayout.addLayout(checkBoxLayout)
        midLayout.addWidget(self.badNodeListWidget)
        midLayout.addWidget(scrollArea)
        midLayout.addLayout(rightLayout)

        topLayout.addWidget(self.selectBTN)

        mainLayout = CustomBoxLayout(QtGui.QBoxLayout.TopToBottom)
        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(midLayout)
        mainLayout.addWidget(self.statusBar)

        self.setLayout(mainLayout)

    def initData(self):
        """
        dataDict is a dictionary to store all nodes and their errors
        children is all decendents under selected node
        allTransforms is all transform nodes
        allShapes is all shape nodes
        """
        sel = self.selectedLE.text()
        self.dataDict, self.children, self.allTransforms, self.allShapes = self.cmd.initData(sel)

    def select(self):
        sel = cmds.ls(sl=True, fl=True)[0]
        self.selectedLE.setText(sel)

    def itemClicked(self, index):
        if index is None:
            return

        currentItem = index.text()
        cmds.select(currentItem, r=True)

        for check in self.checkList:
            exec("self.%sListWidget.clear()" % check)
            exec("self.%sListWidget.addItems(self.dataDict[currentItem][check])" % check)

    def errorClicked(self, *args):
        if args[0] is None:
            return

        selectedItems = [i.text() for i in args[0].listWidget().selectedItems()]
        cmds.select(selectedItems, r=True)

    def suffixList(self):
        suffix1 = self.geoSuffixLineEdit01.text()
        suffix2 = self.geoSuffixLineEdit02.text()
        suffix3 = self.geoSuffixLineEdit03.text()
        suffix4 = self.geoSuffixLineEdit04.text()
        suffix5 = self.geoSuffixLineEdit05.text()
        suffix6 = self.geoSuffixLineEdit06.text()
        suffixList = [
            suffix1,
            suffix2,
            suffix3,
            suffix4,
            suffix5,
            suffix6,
            suffix1 + "Shape",
            suffix2 + "Shape",
            suffix3 + "Shape",
            suffix4 + "Shape",
            suffix5 + "Shape",
            suffix6 + "Shape"]
        return suffixList

    def search(self):
        self.initData()
        self.badNodeListWidget.clear()

        # List for adding to badnodelistwidget
        self.badNodeList = []

        if self.trianglesCheckBox.checkState() == 2:
            for mesh in self.allShapes:
                triangles = self.cmd.searchTriangles(mesh)
                self.dataDict[mesh]['triangles'] = triangles
                self.badNodeList.append(mesh)

        if self.nGonsCheckBox.checkState() == 2:
            for mesh in self.allShapes:
                nGons = self.cmd.searchNgons(mesh)
                self.dataDict[mesh]['nGons'] = nGons
                self.badNodeList.append(mesh)

        if self.nonManifoldVtxCheckBox.checkState() == 2:
            for mesh in self.allShapes:
                nonManifoldVtx = self.cmd.searchNonManifoldVtx(mesh)
                self.dataDict[mesh]['nonManifoldVtx'] = nonManifoldVtx
                self.badNodeList.append(mesh)

        if self.nonManifoldEdgesCheckBox.checkState() == 2:
            for mesh in self.allShapes:
                nonManifoldEdges = self.cmd.searchnonManifoldEdges(mesh)
                self.dataDict[mesh]['nonManifoldEdges'] = nonManifoldEdges
                self.badNodeList.append(mesh)

        if self.laminaFacesCheckBox.checkState() == 2:
            for mesh in self.allShapes:
                laminaFaces = self.cmd.searchLaminaFaces(mesh)
                self.dataDict[mesh]['laminaFaces'] = laminaFaces
                self.badNodeList.append(mesh)

        if self.concaveFacesCheckBox.checkState() == 2:
            for mesh in self.allShapes:
                concaveFaces = self.cmd.searchConcaveFaces(mesh)
                self.dataDict[mesh]['concaveFaces'] = concaveFaces
                self.badNodeList.append(mesh)

        if self.badExtraordinaryVtxCheckBox.checkState() == 2:
            for mesh in self.allShapes:
                badExtraordinaryVtxList = self.cmd.searchBadExtraordinaryVtx(mesh)
                self.dataDict[mesh]['badExtraordinaryVtx'] = badExtraordinaryVtxList
                self.badNodeList.append(mesh)

        if self.oppositeCheckBox.checkState() == 2:
            for mesh in self.allShapes:
                opposite = self.cmd.searchOpposite(mesh)
                self.dataDict[mesh]['opposite'] = opposite
                self.badNodeList.append(mesh)

        if self.doubleSidedCheckBox.checkState() == 2:
            for mesh in self.allShapes:
                doubleSided = self.cmd.searchOpposite(mesh)
                self.dataDict[mesh]['doubleSided'] = doubleSided
                self.badNodeList.append(mesh)

        if self.intermediateObjCheckBox.checkState() == 2:
            for mesh in self.allShapes:
                intermediateObj = self.cmd.searchIntermediateObj(mesh)
                self.dataDict[mesh]['intermediateObj'] = intermediateObj
                self.badNodeList.append(mesh)

        if self.shapeNamesCheckBox.checkState() == 2:
            for transform in self.allTransforms:
                shapeNames = self.cmd.searchBadShapeName(transform)
                self.dataDict[transform]['shapeNames'] = shapeNames
                self.badNodeList.append(transform)

        if self.duplicateNamesCheckBox.checkState() == 2:
            duplicateNames = self.cmd.searchDuplicateNames(self.children)
            duplicateNamesShort = [i.split("|")[-1] for i in duplicateNames]
            for child in self.children:
                duplicatedTwo = []
                for name in duplicateNames:
                    if child.split("|")[-1] == name.split("|")[-1]:
                        duplicatedTwo.append(name)
                        duplicatedTwo.append(child)
                self.dataDict[child]['duplicateNames'] = list(set(duplicatedTwo))
            else:
                self.dataDict[child]['duplicateNames'] = []
            self.badNodeList.extend(duplicateNames)
            
        if self.smoothPreviewCheckBox.checkState() == 2:
            for mesh in self.allShapes:
                smoothMesh = self.cmd.searchSmoothPreviewed(mesh)
                self.dataDict[mesh]['smoothPreview'] = smoothMesh
                self.badNodeList.append(mesh)

        if self.defaultShaderCheckBox.checkState() == 2:
            for mesh in self.allShapes:
                defaultShader = self.cmd.searchNonDefaultShaders(mesh)
                self.dataDict[mesh]['defaultShader'] = defaultShader
                self.badNodeList.append(mesh)

        if self.geoSuffixCheckBox.checkState() == 2:
            suffixList = self.suffixList()
            for child in self.children:
                c = self.cmd.searchBadSuffix(child, suffixList)
                self.dataDict[child]['geoSuffix'] = c
                self.badNodeList.append(child)

        # Remove duplicate items and add to list widget
        self.badNodeList = list(set(self.badNodeList))
        self.badNodeListWidget.addItems(self.badNodeList)


def main():
    global checkerWin
    try:
        checkerWin.close()
    except:
        pass
    # app = QtGui.QApplication(sys.argv)
    checkerWin = ModelChecker()
    checkerWin.show()
    checkerWin.raise_()
    # sys.exit(app.exec_())


if __name__ == '__main__':
    main()
