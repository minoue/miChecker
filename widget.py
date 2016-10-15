from Qt import QtWidgets


class CustomBoxLayout(QtWidgets.QBoxLayout):
    """ Custom layout with less spacing between widgets """

    def __init__(self, parent=None):
        super(CustomBoxLayout, self).__init__(parent)

        self.setSpacing(2)
        self.setContentsMargins(2, 2, 2, 2)


class CustomLabel(QtWidgets.QLabel):
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
