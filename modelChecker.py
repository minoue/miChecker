from PySide import QtCore, QtGui
from collections import OrderedDict
import maya.OpenMayaUI as mui
import maya.cmds as cmds
import textwrap
import checker
reload(checker)
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
        self.setStyleSheet("""
            background-color: darkred;
            border-radius: 4px;
            border-width: 1px;
            border-color: gray;
            border-style: solid""")

    def toGreen(self):
        self.setStyleSheet("""
            background-color: green;
            border-radius: 4px;
            border-width: 1px;
            border-color: gray;
            border-style: solid""")

    def toDefault(self):
        self.setStyleSheet("""
            background-color:;
            border-radius: 4px;
            border-width: 1px;
            border-color: gray;
            border-style: solid""")


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

        self.functionList = [
            checker.get_history,
            checker.get_transform,
            checker.get_triangles,
            checker.get_ngons,
            checker.get_nonmanifold_vertices,
            checker.get_nonmanifold_edges,
            checker.get_lamina_faces,
            checker.get_concave_faces,
            checker.get_badextraordianry_vtx,
            checker.get_opposite,
            checker.get_doublesided,
            checker.get_intermediate_obj,
            checker.get_bad_shapenames,
            checker.get_duplicated_names,
            checker.get_smooth_mesh,
            checker.get_shader,
            checker.get_geo_suffix,
            checker.get_locked_channels,
            checker.get_keyframes]

        self.checkListDict = [
            ('history', True),
            ('transform', True),
            ('triangles', True),
            ('nGons', True),
            ('nonManifoldVtx', True),
            ('nonManifoldEdges', True),
            ('laminaFaces', True),
            ('concaveFaces', True),
            ('badExtraordinaryVtx', True),
            ('opposite', True),
            ('doubleSided', True),
            ('intermediateObj', True),
            ('shapeNames', True),
            ('duplicateNames', True),
            ('smoothPreview', True),
            ('defaultShader', True),
            ('geoSuffix', True),
            ('lockedChannels', True),
            ('keyframes', True)]

        self.checkList = OrderedDict(self.checkListDict)

        # Command class setup
        self.cmd = command.Commands(self.checkList)

        # Create GUI
        self.createUI()
        self.layoutUI()

    def createUI(self):
        """ Create UI """

        # Top Area Widgets
        self.selectedLE = QtGui.QLineEdit()
        self.selectedLE.setText(self.initialSelection)
        self.selectBTN = QtGui.QPushButton('Select')
        self.selectBTN.clicked.connect(self.select)

        for i in self.checkList:
            exec("self.%sCheckBox = QtGui.QCheckBox('%s')" % (i, i))
            exec("self.%sCheckBox.setCheckState(QtCore.Qt.Checked)" % i)
            if self.checkList[i] is False:
                exec("self.%sCheckBox.setCheckState(QtCore.Qt.Unchecked)" % i)

            exec("self.%sListWidget = QtGui.QListWidget()" % i)
            exec("self.%sListWidget.currentItemChanged.connect(self.errorClicked)" % i)
            exec("self.%sListWidget.itemClicked.connect(self.errorClicked)" % i)
            exec("self.%sListWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)" % i)

            exec("self.%sResultLabel = CustomLabel('%s')" % (i, i))

            exec("self.%sFixButton = QtGui.QPushButton()" % i)
            exec("self.%sFixButton.setFixedWidth(100)" % i)

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

        self.searchButton = QtGui.QPushButton('SEARCH')
        self.searchButton.setFixedHeight(150)
        self.searchButton.clicked.connect(self.search)

        # fix button widgets
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
        self.intermediateObjFixButton.clicked.connect(
            self.cmd.fixIntermediateObj)
        self.shapeNamesFixButton.setText('Fix All')
        self.shapeNamesFixButton.clicked.connect(self.cmd.fixShapeNames)
        self.duplicateNamesFixButton.setEnabled(False)
        self.smoothPreviewFixButton.setText('Fix All')
        self.smoothPreviewFixButton.clicked.connect(self.cmd.fixSmoothPreview)
        self.defaultShaderFixButton.setText('Set Lambert1')
        self.defaultShaderFixButton.clicked.connect(self.cmd.fixShader)
        self.geoSuffixFixButton.setEnabled(False)
        self.lockedChannelsFixButton.setText('Unlock All')
        self.lockedChannelsFixButton.clicked.connect(
            self.cmd.fixLockedChannels)
        self.keyframesFixButton.setText('Delete All')
        self.keyframesFixButton.clicked.connect(self.cmd.fixKeyframes)

        # progress bar
        self.progressBar = QtGui.QProgressBar()

        # status bar
        self.statusBar = QtGui.QStatusBar()
        self.statusBar.showMessage("")

    def layoutUI(self):
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

        sel = self.selectedLE.text()
        self.children = cmds.listRelatives(
            sel,
            ad=True,
            fullPath=True,
            type="transform")

        if self.children is None:
            self.children = []
        self.children.append(sel)

        self.dataDict = {}
        for item in self.children:
            self.dataDict[item] = {}
            for check in self.checkList:
                self.dataDict[item][check] = []

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

    def getSuffixList(self):
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

    def clear(self):
        """ Clear all list widgets """

        self.badNodeListWidget.clear()
        for i in self.checkList:
            c = "self.%sListWidget" % i
            exec("%s.clear()" % c)

    def search(self):
        """ Search all error """

        self.initData()
        self.badNodeListWidget.clear()

        # List for adding to badnodelistwidget
        badNodeList = []

        # Number of checks
        num = len([i for i in self.checkList if self.checkList[i] is True])

        self.progressBar.reset()
        self.progressBar.setRange(1, num)

        for name, func in zip(self.checkList, self.functionList):
            if self.checkList[name] is True:
                self.statusBar.showMessage('Searching %s...' % name)
                suffix = self.getSuffixList()
                func(self.dataDict, self.children, badNodeList, suffix)
                self.incrementProgressbar()

        # Remove duplicate items and add to list widget
        badNodeList = list(set(badNodeList))
        self.badNodeListWidget.addItems(badNodeList)

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
