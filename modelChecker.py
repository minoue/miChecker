from PyQt4 import QtCore, QtGui
from functools import partial
import maya.OpenMayaUI as mui
import maya.cmds as cmds
import sys
import command
reload(command)
import sip
# import shiboken


def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    # return shiboken.wrapInstance(long(ptr), QtGui.QMainWindow)
    return sip.wrapinstance(long(ptr), QtCore.QObject)


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

        # Command class setup
        self.cmd = command.Commands(self.checkList)

        # Create GUI
        self.createUI()


    def createUI(self):
        ######################
        """ Create Widgets """
        ######################

        """ Top Area Widgets """
        self.selectedLE = QtGui.QLineEdit()
        self.selectedLE.setText('')
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
        self.resetButton.clicked.connect(self.resetSetting)

        """ Bad nodes list widget """
        self.badNodeListWidget = QtGui.QListWidget()
        self.badNodeListWidget.currentItemChanged.connect(self.itemClicked)

        """ error list widgets """
        for i in self.checkList:
            exec("self.%sListWidget = QtGui.QListWidget()" % i)
            exec("self.%sListWidget.currentItemChanged.connect(self.errorClicked)" % i)
            exec("self.%sListWidget.itemClicked.connect(self.errorClicked)" % i)
            exec("self.%sListWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)" % i)

        self.searchButton = QtGui.QPushButton('SEARCH')
        self.searchButton.setFixedHeight(150)
        self.searchButton.clicked.connect(self.search)

        """ result label wigets """
        for i in self.checkList:
            exec("self.%sResultLabel = CustomLabel('%s')" % (i, i))

        """ fix button widgets """
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

        """ progress bar """
        self.progressBar = QtGui.QProgressBar()

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
            selectedItems = [i.text() for i in args[0].listWidget().selectedItems()]
            cmds.select(selectedItems, r=True)
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
            ifblock = """
%sResult = [self.dataDict[child]['%s'] for child in self.children]\n
if self.%sCheckBox.checkState() == 2:
    if %sResult.count([]) == len(%sResult):\n
        self.%sResultLabel.toGreen()\n
    else:\n
        self.%sResultLabel.toRed()\n
else:
    self.%sResultLabel.toDefault()\n

            """ % (i, i, i, i, i, i, i, i)
            exec(ifblock)

    def search(self):
        """ Search all error """

        self.initData()
        self.badNodeListWidget.clear()

        # List for adding to badnodelistwidget
        self.badNodeList = []

        if self.historyCheckBox.checkState() == 2:
            # Init progress bar
            self.progressBar.reset()
            self.progressBar.setRange(1, len(self.allShapes))
            self.statusBar.showMessage('Searching history...')
            for mesh in self.allShapes:
                # Find history and store to self.datadict
                history = self.cmd.searchHistory(mesh)
                self.dataDict[mesh]['history'] = history
                # If history detected, add to badgeo list
                if history != []:
                    self.badNodeList.append(mesh)
                # Update progressbar
                value = self.progressBar.value()
                value += 1
                self.progressBar.setValue(value)
                QtCore.QCoreApplication.processEvents()

        if self.transformCheckBox.checkState() == 2:
            self.progressBar.reset()
            self.progressBar.setRange(1, len(self.allTransforms))
            self.statusBar.showMessage('Searching transforms...')
            for transform in self.allTransforms:
                transformList = self.cmd.searchTransformations(transform)
                self.dataDict[transform]['transform'] = transformList
                if transformList != []:
                    self.badNodeList.append(transform)
                value = self.progressBar.value()
                value += 1
                self.progressBar.setValue(value)
                QtCore.QCoreApplication.processEvents()

        if self.trianglesCheckBox.checkState() == 2:
            self.progressBar.reset()
            self.progressBar.setRange(1, len(self.allShapes))
            self.statusBar.showMessage('Searching triangles...')
            for mesh in self.allShapes:
                triangles = self.cmd.searchTriangles(mesh)
                self.dataDict[mesh]['triangles'] = triangles
                if triangles != []:
                    self.badNodeList.append(mesh)
                value = self.progressBar.value()
                value += 1
                self.progressBar.setValue(value)
                QtCore.QCoreApplication.processEvents()

        if self.nGonsCheckBox.checkState() == 2:
            self.progressBar.reset()
            self.progressBar.setRange(1, len(self.allShapes))
            self.statusBar.showMessage('Searching nGons...')
            for mesh in self.allShapes:
                nGons = self.cmd.searchNgons(mesh)
                self.dataDict[mesh]['nGons'] = nGons
                if nGons != []:
                    self.badNodeList.append(mesh)
                value = self.progressBar.value()
                value += 1
                self.progressBar.setValue(value)
                QtCore.QCoreApplication.processEvents()

        if self.nonManifoldVtxCheckBox.checkState() == 2:
            self.progressBar.reset()
            self.progressBar.setRange(1, len(self.allShapes))
            self.statusBar.showMessage('Searching nonManifold vertices...')
            for mesh in self.allShapes:
                nonManifoldVtx = self.cmd.searchNonManifoldVtx(mesh)
                self.dataDict[mesh]['nonManifoldVtx'] = nonManifoldVtx
                if nonManifoldVtx != []:
                    self.badNodeList.append(mesh)
                value = self.progressBar.value()
                value += 1
                self.progressBar.setValue(value)
                QtCore.QCoreApplication.processEvents()

        if self.nonManifoldEdgesCheckBox.checkState() == 2:
            self.progressBar.reset()
            self.progressBar.setRange(1, len(self.allShapes))
            self.statusBar.showMessage('Searching nonManifold edges...')
            for mesh in self.allShapes:
                nonManifoldEdges = self.cmd.searchnonManifoldEdges(mesh)
                self.dataDict[mesh]['nonManifoldEdges'] = nonManifoldEdges
                if nonManifoldEdges != []:
                    self.badNodeList.append(mesh)
                value = self.progressBar.value()
                value += 1
                self.progressBar.setValue(value)
                QtCore.QCoreApplication.processEvents()

        if self.laminaFacesCheckBox.checkState() == 2:
            self.progressBar.reset()
            self.progressBar.setRange(1, len(self.allShapes))
            self.statusBar.showMessage('Searching lamina faces...')
            for mesh in self.allShapes:
                laminaFaces = self.cmd.searchLaminaFaces(mesh)
                self.dataDict[mesh]['laminaFaces'] = laminaFaces
                if laminaFaces != []:
                    self.badNodeList.append(mesh)
                value = self.progressBar.value()
                value += 1
                self.progressBar.setValue(value)
                QtCore.QCoreApplication.processEvents()

        if self.concaveFacesCheckBox.checkState() == 2:
            self.progressBar.reset()
            self.progressBar.setRange(1, len(self.allShapes))
            self.statusBar.showMessage('Searching concave faces...')
            for mesh in self.allShapes:
                concaveFaces = self.cmd.searchConcaveFaces(mesh)
                self.dataDict[mesh]['concaveFaces'] = concaveFaces
                if concaveFaces != []:
                    self.badNodeList.append(mesh)
                value = self.progressBar.value()
                value += 1
                self.progressBar.setValue(value)
                QtCore.QCoreApplication.processEvents()

        if self.badExtraordinaryVtxCheckBox.checkState() == 2:
            self.progressBar.reset()
            self.progressBar.setRange(1, len(self.allShapes))
            self.statusBar.showMessage('Searching bad extraordinary vertices...')
            for mesh in self.allShapes:
                badExtraordinaryVtxList = self.cmd.searchBadExtraordinaryVtx(mesh)
                self.dataDict[mesh]['badExtraordinaryVtx'] = badExtraordinaryVtxList
                if badExtraordinaryVtxList != []:
                    self.badNodeList.append(mesh)
                value = self.progressBar.value()
                value += 1
                self.progressBar.setValue(value)
                QtCore.QCoreApplication.processEvents()

        if self.oppositeCheckBox.checkState() == 2:
            self.progressBar.reset()
            self.progressBar.setRange(1, len(self.allShapes))
            self.statusBar.showMessage('Searching opposite shape...')
            for mesh in self.allShapes:
                opposite = self.cmd.searchOpposite(mesh)
                self.dataDict[mesh]['opposite'] = opposite
                if opposite != []:
                    self.badNodeList.append(mesh)
                value = self.progressBar.value()
                value += 1
                self.progressBar.setValue(value)
                QtCore.QCoreApplication.processEvents()

        if self.doubleSidedCheckBox.checkState() == 2:
            self.progressBar.reset()
            self.progressBar.setRange(1, len(self.allShapes))
            self.statusBar.showMessage('Searching doubleSided shape...')
            for mesh in self.allShapes:
                doubleSided = self.cmd.searchOpposite(mesh)
                self.dataDict[mesh]['doubleSided'] = doubleSided
                if doubleSided != []:
                    self.badNodeList.append(mesh)
                value = self.progressBar.value()
                value += 1
                self.progressBar.setValue(value)
                QtCore.QCoreApplication.processEvents()

        if self.intermediateObjCheckBox.checkState() == 2:
            self.progressBar.reset()
            self.progressBar.setRange(1, len(self.allTransforms))
            self.statusBar.showMessage('Searching intermediate objects...')
            for mesh in self.allShapes:
                intermediateObj = self.cmd.searchIntermediateObj(mesh)
                self.dataDict[mesh]['intermediateObj'] = intermediateObj
                if intermediateObj != []:
                    self.badNodeList.append(mesh)
                value = self.progressBar.value()
                value += 1
                self.progressBar.setValue(value)
                QtCore.QCoreApplication.processEvents()

        if self.shapeNamesCheckBox.checkState() == 2:
            self.progressBar.reset()
            self.progressBar.setRange(1, len(self.allShapes))
            self.statusBar.showMessage('Searching bad shape names...')
            for mesh in self.allShapes:
                shapeNames = self.cmd.searchBadShapeName(mesh)
                self.dataDict[mesh]['shapeNames'] = shapeNames
                if shapeNames != []:
                    self.badNodeList.append(mesh)
                value = self.progressBar.value()
                value += 1
                self.progressBar.setValue(value)
                QtCore.QCoreApplication.processEvents()

        if self.duplicateNamesCheckBox.checkState() == 2:
            self.progressBar.reset()
            self.progressBar.setRange(1, len(self.children))
            self.statusBar.showMessage('Searching duplicate names...')
            duplicateNames = self.cmd.searchDuplicateNames(self.children)
            duplicateNamesShort = [i.split("|")[-1] for i in duplicateNames]
            for child in self.children:
                duplicatedTwo = []
                for name in duplicateNames:
                    if child.split("|")[-1] == name.split("|")[-1]:
                        duplicatedTwo.append(name)
                        duplicatedTwo.append(child)
                self.dataDict[child]['duplicateNames'] = list(set(duplicatedTwo))
                value = self.progressBar.value()
                value += 1
                self.progressBar.setValue(value)
                QtCore.QCoreApplication.processEvents()
            else:
                self.dataDict[child]['duplicateNames'] = []
            if duplicatedTwo != []:
                self.badNodeList.extend(duplicateNames)
            
        if self.smoothPreviewCheckBox.checkState() == 2:
            self.progressBar.reset()
            self.progressBar.setRange(1, len(self.allShapes))
            self.statusBar.showMessage('Searching smooth preview mesh...')
            for mesh in self.allShapes:
                smoothMesh = self.cmd.searchSmoothPreviewed(mesh)
                self.dataDict[mesh]['smoothPreview'] = smoothMesh
                if smoothMesh != []:
                    self.badNodeList.append(mesh)
                value = self.progressBar.value()
                value += 1
                self.progressBar.setValue(value)
                QtCore.QCoreApplication.processEvents()

        if self.defaultShaderCheckBox.checkState() == 2:
            self.progressBar.reset()
            self.progressBar.setRange(1, len(self.allShapes))
            self.statusBar.showMessage('Searching non default shaders...')
            for mesh in self.allShapes:
                defaultShader = self.cmd.searchNonDefaultShaders(mesh)
                self.dataDict[mesh]['defaultShader'] = defaultShader
                if defaultShader != []:
                    self.badNodeList.append(mesh)
                value = self.progressBar.value()
                value += 1
                self.progressBar.setValue(value)
                QtCore.QCoreApplication.processEvents()

        if self.geoSuffixCheckBox.checkState() == 2:
            self.progressBar.reset()
            self.progressBar.setRange(1, len(self.children))
            self.statusBar.showMessage('Searching bad suffix...')
            suffixList = self.suffixList()
            for child in self.children:
                badSuffixList = self.cmd.searchBadSuffix(child, suffixList)
                self.dataDict[child]['geoSuffix'] = badSuffixList
                if badSuffixList != []:
                    self.badNodeList.append(child)
                value = self.progressBar.value()
                value += 1
                self.progressBar.setValue(value)
                QtCore.QCoreApplication.processEvents()

        if self.lockedChannelsCheckBox.checkState() == 2:
            self.progressBar.reset()
            self.progressBar.setRange(1, len(self.children))
            self.statusBar.showMessage('Searching locked channels...')
            for child in self.children:
                lockedChannelList = self.cmd.searchLockedChannels(child)
                self.dataDict[child]['lockedChannels'] = lockedChannelList
                if lockedChannelList != []:
                    self.badNodeList.append(child)
                value = self.progressBar.value()
                value += 1
                self.progressBar.setValue(value)
                QtCore.QCoreApplication.processEvents()

        if self.keyframesCheckBox.checkState() == 2:
            self.progressBar.reset()
            self.progressBar.setRange(1, len(self.children))
            self.statusBar.showMessage('Searching keyframes...')
            for child in self.children:
                keyframeList = self.cmd.searchKeyframes(child)
                self.dataDict[child]['keyframes'] = keyframeList
                if keyframeList != []:
                    self.badNodeList.append(child)
                value = self.progressBar.value()
                value += 1
                self.progressBar.setValue(value)
                QtCore.QCoreApplication.processEvents()

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
    checkerWin = ModelChecker()
    checkerWin.show()
    checkerWin.raise_()


if __name__ == '__main__':
    main()
