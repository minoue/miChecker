from PySide import QtCore, QtGui
from functools import partial
import maya.OpenMayaUI as mui
import maya.cmds as cmds
import textwrap
import sys
import command
reload(command)
import shiboken


def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return shiboken.wrapInstance(long(ptr), QtGui.QMainWindow)


class CustomBoxLayout(QtGui.QBoxLayout):
    """ Custom layout with less spacing between widgets """

    def __init__(self, parent=None):
        super(CustomBoxLayout, self).__init__(parent)

        self.setSpacing(2)
        self.setContentsMargins(2, 2, 2, 2)


class CustomLabel(QtGui.QLabel):
    """ Custom QLabel to show green/red color """

    def __init__(self, parent=None):
        super(CustomLabel, self).__init__(parent)

    def toRed(self):
        self.setStyleSheet('background-color: darkred; border-radius: 4px; border-width: 1px; border-color: gray; border-style: solid')

    def toGreen(self):
        self.setStyleSheet( 'background-color: green; border-radius: 4px; border-width: 1px; border-color: gray; border-style: solid')

    def toDefault(self):
        self.setStyleSheet( 'background-color:; border-radius: 4px; border-width: 1px; border-color: gray; border-style: solid')


class ModelChecker(QtGui.QDialog):
    """ Main UI class """

    def closeExistingWindow(self):
        for qt in QtGui.QApplication.topLevelWidgets():
            try:
                if qt.__class__.__name__ == self.__class__.__name__:
                    qt.close()
            except:
                pass

    def __init__(self, initialSelection, parent=getMayaWindow()):
        self.closeExistingWindow()
        super(ModelChecker, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.initialSelection = initialSelection

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

        # Command class setup
        self.cmd = command.Commands(self.checkList)

        # Create GUI
        self.createUI()

    def createUI(self):
        """ Create UI """

        # Top Area Widgets
        self.selectedLE = QtGui.QLineEdit()
        self.selectedLE.setText(self.initialSelection)
        self.selectBTN = QtGui.QPushButton('Select')
        self.selectBTN.clicked.connect(self.select)

        # Check box widgets
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
        self.resetButton.clicked.connect(self.resetSetting)

        # Bad nodes list widget
        self.badNodeListWidget = QtGui.QListWidget()
        self.badNodeListWidget.currentItemChanged.connect(self.itemClicked)

        # error list widgets
        for i in self.checkList:
            exec("self.%sListWidget = QtGui.QListWidget()" % i)
            exec("self.%sListWidget.currentItemChanged.connect(self.errorClicked)" % i)
            exec("self.%sListWidget.itemClicked.connect(self.errorClicked)" % i)
            exec("self.%sListWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)" % i)

        self.searchButton = QtGui.QPushButton('SEARCH')
        self.searchButton.setFixedHeight(150)
        self.searchButton.clicked.connect(self.search)

        # result label wigets
        for i in self.checkList:
            exec("self.%sResultLabel = CustomLabel('%s')" % (i, i))

        # fix button widgets
        for i in self.checkList:
            exec("self.%sFixButton = QtGui.QPushButton()" % i)
            exec("self.%sFixButton.setFixedWidth(100)" % i)
            # exec("self.%sFixButton.setEnabled(False)" % i)
        self.historyFixButton.setText('Delete All')
        self.historyFixButton.clicked.connect(self.cmd.fixHistory)
        self.transformFixButton.setText('Freeze All')
        self.transformFixButton.clicked.connect(self.cmd.fixTransform)
        self.trianglesFixButton.setEnabled(False)
        self.nGonsFixButton.setEnabled(False)
        self.nonManifoldVtxFixButton.setEnabled(False)
        self.nonManifoldEdgesFixButton.setEnabled(False)
        self.laminaFacesFixButton.setEnabled(False)
        self.concaveFacesFixButton.setEnabled(False)
        self.badExtraordinaryVtxFixButton.setEnabled(False)
        self.oppositeFixButton.setText('Fix All')
        self.oppositeFixButton.clicked.connect(self.cmd.fixOpposite)
        self.doubleSidedFixButton.setText('Fix All')
        self.doubleSidedFixButton.clicked.connect(self.cmd.fixDoubleSided)
        self.intermediateObjFixButton.setText('Delete All')
        self.intermediateObjFixButton.clicked.connect(self.cmd.fixIntermediateObj)
        self.shapeNamesFixButton.setText('Fix All')
        self.shapeNamesFixButton.clicked.connect(self.cmd.fixShapeNames)
        self.duplicateNamesFixButton.setEnabled(False)
        self.smoothPreviewFixButton.setText('Fix All')
        self.smoothPreviewFixButton.clicked.connect(self.cmd.fixSmoothPreview)
        self.defaultShaderFixButton.setText('Set Lambert1')
        self.defaultShaderFixButton.clicked.connect(self.cmd.fixShader)
        self.geoSuffixFixButton.setEnabled(False)
        self.lockedChannelsFixButton.setText('Unlock All')
        self.lockedChannelsFixButton.clicked.connect(self.cmd.fixLockedChannels)
        self.keyframesFixButton.setText('Delete All')
        self.keyframesFixButton.clicked.connect(self.cmd.fixKeyframes)

        # progress bar
        self.progressBar = QtGui.QProgressBar()

        # status bar
        self.statusBar = QtGui.QStatusBar()
        self.statusBar.showMessage("")

        # #### Layout Management #### #
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
        mainLayout.addWidget(self.progressBar)
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
        sel = cmds.ls(sl=True, fl=True, long=True)[0]
        self.selectedLE.setText(sel)

    def itemClicked(self, index):
        if index is None:
            return

        currentItem = str(index.text())
        cmds.select(currentItem, r=True)

        for check in self.checkList:
            exec("self.%sListWidget.clear()" % check)
            exec("self.%sListWidget.addItems(self.dataDict[currentItem][check])" % check)

    def errorClicked(self, *args):
        if args[0] is None:
            return
        try:
            selectedItems = ["*" + i.text() for i in args[0].listWidget().selectedItems()]
            cmds.select(selectedItems, r=True)
            cmds.setFocus("MayaWindow")
        except ValueError:
            """ When channels/attributes/etc are selected, do not try to select """
            pass

    def resetSetting(self):
        self.badNodeListWidget.clear()
        for i in self.checkList:
            exec("self.%sListWidget.clear()" % i)
            exec("self.%sCheckBox.setCheckState(QtCore.Qt.Checked)" % i)
            exec("self.%sResultLabel.toDefault()" % i)
        self.badExtraordinaryVtxCheckBox.setCheckState(QtCore.Qt.Unchecked)
        self.lockedChannelsCheckBox.setCheckState(QtCore.Qt.Unchecked)
        self.keyframesCheckBox.setCheckState(QtCore.Qt.Unchecked)
        self.geoSuffixLineEdit01.setText("_GEP")
        self.geoSuffixLineEdit02.setText("_GES")
        self.geoSuffixLineEdit03.setText("_NRB")
        self.geoSuffixLineEdit04.setText("_GRP")
        self.geoSuffixLineEdit05.setText("_LOC")
        self.geoSuffixLineEdit06.setText("_PLY")
        self.progressBar.reset()

    def suffixList(self):
        suffix1 = str(self.geoSuffixLineEdit01.text())
        suffix2 = str(self.geoSuffixLineEdit02.text())
        suffix3 = str(self.geoSuffixLineEdit03.text())
        suffix4 = str(self.geoSuffixLineEdit04.text())
        suffix5 = str(self.geoSuffixLineEdit05.text())
        suffix6 = str(self.geoSuffixLineEdit06.text())
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

    def changeLabelColorbyResult(self):
        """ Check each and make labels green if it's ok, otherwise red """

        for i in self.checkList:
            ifblock = """\
            %sResult = [self.dataDict[child]['%s'] for child in self.children]\n
            if self.%sCheckBox.checkState() == 2:
                if %sResult.count([]) == len(%sResult):\n
                    self.%sResultLabel.toGreen()\n
                else:\n
                    self.%sResultLabel.toRed()\n
            else:
                self.%sResultLabel.toDefault()\n
            """ % (i, i, i, i, i, i, i, i)
            exec(textwrap.dedent(ifblock))

    def incrementProgressbar(self):
        # current value 
        value = self.progressBar.value()

        # increment
        value += 1

        # Update
        self.progressBar.setValue(value)
        QtCore.QCoreApplication.processEvents()

    def initProgressbar(self, list, word):
        self.progressBar.reset()
        self.progressBar.setRange(1, len(list))
        self.statusBar.showMessage('Searching %s...' % word)

    def search(self):
        """ Search all error """

        self.initData()

        # Clear all list widgets
        self.badNodeListWidget.clear()
        for i in self.checkList:
            c = "self.%sListWidget" % i
            exec("%s.clear()" % c)

        # List for adding to badnodelistwidget
        self.badNodeList = []

        if self.historyCheckBox.checkState() == 2:
            self.initProgressbar(self.allShapes, 'history')
            for mesh in self.allShapes:
                # Find history and store to self.datadict
                history = self.cmd.searchHistory(mesh)
                self.dataDict[mesh]['history'] = history
                # If history detected, add to badgeo list
                if history != []:
                    self.badNodeList.append(mesh)
                # Update progressbar
                self.incrementProgressbar()

        if self.transformCheckBox.checkState() == 2:
            self.initProgressbar(self.allTransforms, 'transform')
            for transform in self.allTransforms:
                transformList = self.cmd.searchTransformations(transform)
                self.dataDict[transform]['transform'] = transformList
                if transformList != []:
                    self.badNodeList.append(transform)
                self.incrementProgressbar()

        if self.trianglesCheckBox.checkState() == 2:
            self.initProgressbar(self.allShapes, 'triangles')
            for mesh in self.allShapes:
                triangles = self.cmd.searchTriangles(mesh)
                self.dataDict[mesh]['triangles'] = triangles
                if triangles != []:
                    self.badNodeList.append(mesh)
                self.incrementProgressbar()

        if self.nGonsCheckBox.checkState() == 2:
            self.initProgressbar(self.allShapes, 'nGons')
            for mesh in self.allShapes:
                nGons = self.cmd.searchNgons(mesh)
                self.dataDict[mesh]['nGons'] = nGons
                if nGons != []:
                    self.badNodeList.append(mesh)
                self.incrementProgressbar()

        if self.nonManifoldVtxCheckBox.checkState() == 2:
            self.initProgressbar(self.allShapes, 'nonManifold vertices')
            for mesh in self.allShapes:
                nonManifoldVtx = self.cmd.searchNonManifoldVtx(mesh)
                self.dataDict[mesh]['nonManifoldVtx'] = nonManifoldVtx
                if nonManifoldVtx != []:
                    self.badNodeList.append(mesh)
                self.incrementProgressbar()

        if self.nonManifoldEdgesCheckBox.checkState() == 2:
            self.initProgressbar(self.allShapes, 'nonManifold edges')
            for mesh in self.allShapes:
                nonManifoldEdges = self.cmd.searchnonManifoldEdges(mesh)
                self.dataDict[mesh]['nonManifoldEdges'] = nonManifoldEdges
                if nonManifoldEdges != []:
                    self.badNodeList.append(mesh)
                self.incrementProgressbar()

        if self.laminaFacesCheckBox.checkState() == 2:
            self.initProgressbar(self.allShapes, 'lamina faces')
            for mesh in self.allShapes:
                laminaFaces = self.cmd.searchLaminaFaces(mesh)
                self.dataDict[mesh]['laminaFaces'] = laminaFaces
                if laminaFaces != []:
                    self.badNodeList.append(mesh)
                self.incrementProgressbar()

        if self.concaveFacesCheckBox.checkState() == 2:
            self.initProgressbar(self.allShapes, 'concave faces')
            for mesh in self.allShapes:
                concaveFaces = self.cmd.searchConcaveFaces(mesh)
                self.dataDict[mesh]['concaveFaces'] = concaveFaces
                if concaveFaces != []:
                    self.badNodeList.append(mesh)
                self.incrementProgressbar()

        if self.badExtraordinaryVtxCheckBox.checkState() == 2:
            self.initProgressbar(self.allShapes, 'bad extraordinary vertices')
            for mesh in self.allShapes:
                badExtraordinaryVtxList = self.cmd.searchBadExtraordinaryVtx(mesh)
                self.dataDict[mesh]['badExtraordinaryVtx'] = badExtraordinaryVtxList
                if badExtraordinaryVtxList != []:
                    self.badNodeList.append(mesh)
                self.incrementProgressbar()

        if self.oppositeCheckBox.checkState() == 2:
            self.initProgressbar(self.allShapes, 'opposite shape')
            for mesh in self.allShapes:
                opposite = self.cmd.searchOpposite(mesh)
                self.dataDict[mesh]['opposite'] = opposite
                if opposite != []:
                    self.badNodeList.append(mesh)
                self.incrementProgressbar()

        if self.doubleSidedCheckBox.checkState() == 2:
            self.initProgressbar(self.allShapes, 'doublesided shape')
            for mesh in self.allShapes:
                doubleSided = self.cmd.searchOpposite(mesh)
                self.dataDict[mesh]['doubleSided'] = doubleSided
                if doubleSided != []:
                    self.badNodeList.append(mesh)
                self.incrementProgressbar()

        if self.intermediateObjCheckBox.checkState() == 2:
            self.initProgressbar(self.allTransforms, 'intermediate objects')
            for mesh in self.allShapes:
                intermediateObj = self.cmd.searchIntermediateObj(mesh)
                self.dataDict[mesh]['intermediateObj'] = intermediateObj
                if intermediateObj != []:
                    self.badNodeList.append(mesh)
                self.incrementProgressbar()

        if self.shapeNamesCheckBox.checkState() == 2:
            self.initProgressbar(self.allShapes, 'bad shape names')
            for mesh in self.allShapes:
                shapeNames = self.cmd.searchBadShapeName(mesh)
                self.dataDict[mesh]['shapeNames'] = shapeNames
                if shapeNames != []:
                    self.badNodeList.append(mesh)
                self.incrementProgressbar()

        if self.duplicateNamesCheckBox.checkState() == 2:
            self.initProgressbar(self.children, 'duplicate names')
            duplicateNames = self.cmd.searchDuplicateNames(self.children)
            dupList = []
            for child in self.children:
                shortName = child.split("|")[-1]
                if shortName in duplicateNames:
                    self.dataDict[child]['duplicateNames'] = [shortName]
                    self.badNodeList.append(child)
                else:
                    self.dataDict[child]['duplicateNames'] = []
                self.incrementProgressbar()

        if self.smoothPreviewCheckBox.checkState() == 2:
            self.initProgressbar(self.allShapes, 'smooth preview mesh')
            for mesh in self.allShapes:
                smoothMesh = self.cmd.searchSmoothPreviewed(mesh)
                self.dataDict[mesh]['smoothPreview'] = smoothMesh
                if smoothMesh != []:
                    self.badNodeList.append(mesh)
                self.incrementProgressbar()

        if self.defaultShaderCheckBox.checkState() == 2:
            self.initProgressbar(self.allShapes, 'non default shaders')
            for mesh in self.allShapes:
                defaultShader = self.cmd.searchNonDefaultShaders(mesh)
                self.dataDict[mesh]['defaultShader'] = defaultShader
                if defaultShader != []:
                    self.badNodeList.append(mesh)
                self.incrementProgressbar()

        if self.geoSuffixCheckBox.checkState() == 2:
            self.initProgressbar(self.children, 'bad suffix')
            suffixList = self.suffixList()
            for child in self.children:
                badSuffixList = self.cmd.searchBadSuffix(child, suffixList)
                self.dataDict[child]['geoSuffix'] = badSuffixList
                if badSuffixList != []:
                    self.badNodeList.append(child)
                self.incrementProgressbar()

        if self.lockedChannelsCheckBox.checkState() == 2:
            self.initProgressbar(self.children, 'locked channel')
            for child in self.children:
                lockedChannelList = self.cmd.searchLockedChannels(child)
                self.dataDict[child]['lockedChannels'] = lockedChannelList
                if lockedChannelList != []:
                    self.badNodeList.append(child)
                self.incrementProgressbar()

        if self.keyframesCheckBox.checkState() == 2:
            self.initProgressbar(self.children, 'keyframes')
            for child in self.children:
                keyframeList = self.cmd.searchKeyframes(child)
                self.dataDict[child]['keyframes'] = keyframeList
                if keyframeList != []:
                    self.badNodeList.append(child)
                self.incrementProgressbar()

        # Remove duplicate items and add to list widget
        self.badNodeList = list(set(self.badNodeList))
        self.badNodeListWidget.addItems(self.badNodeList)

        self.statusBar.showMessage('Searching finished...')

        self.changeLabelColorbyResult()


def main():
    global checkerWin
    try:
        checkerWin.close()
    except:
        pass

    sel = cmds.ls(sl=True, long=True)
    if len(sel) == 0:
        sel = ""
    else:
        sel = sel[0]

    checkerWin = ModelChecker(sel)
    checkerWin.show()
    checkerWin.raise_()


if __name__ == '__main__':
    main()
