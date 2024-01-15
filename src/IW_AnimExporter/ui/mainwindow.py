from PySide2 import QtGui, QtCore, QtWidgets


class Layout(QtWidgets.QWidget):

    def __init__(self, layoutOrientation, margins=[0, 0, 0, 0], spacing=0):
        super().__init__()
        _layout = QtWidgets.QVBoxLayout() if layoutOrientation == QtCore.Qt.Vertical else QtWidgets.QHBoxLayout()

        self.stretch = False

        _layout.setContentsMargins(
            margins[0],
            margins[1],
            margins[2],
            margins[3]
        ) if isinstance(
            margins,
            list
        ) else _layout.setContentsMargins(
            margins,
            margins,
            margins,
            margins
        )
        _layout.setSpacing(spacing)
        self.setLayout(_layout)

    def children(self):
        _returnList = []
        for index in range(0, self.layout().count()):
            _widgetItem = self.layout().itemAt(index)
            _widget = _widgetItem.widget()
            if _widget is not None:
                _returnList.append(_widget)
        return _returnList

    def paintEvent(self, event):
        self.setAutoFillBackground(True)

        super().paintEvent(event)

    def addStretch(self, stretch):
        self.layout().addStretch(stretch)
        self.stretch = True

    def addWidget(self, widget, *args, **kwargs):
        if self.stretch is True:
            self.insertWidget(0, widget)
            return
        self.layout().addWidget(widget, *args, **kwargs)

    def addWidgets(self, widgets, *args, **kwargs):
        [self.addWidget(_widget, *args, **kwargs) for _widget in widgets]

    def insertWidget(self, index, widget):
        self.layout().insertWidget(index, widget)

    def addSpacerItem(self, spaceritem):
        self.layout().addSpacerItem(spaceritem)

    def insertSpacerItem(self, index, spaceritem):
        self.layout().insertSpacerItem(index, spaceritem)

    def clearAndAddWidget(self, widget, *args, **kwargs):
        self.clear_layout()
        self.layout().addWidget(widget, *args, **kwargs)

    def clearAndAddWidgets(self, widgets, *args, **kwargs):
        self.clear_layout()
        self.addWidgets(widgets, *args, **kwargs)

    def clear_layout(self):
        if len(self.children()) > 0:
            for _child in self.children():
                self.disown_child(_child)

    def childCount(self):
        return len(self.children())

    def disown_child(self, child_widget):
        child_widget.setParent(None)
        del child_widget

    def get_child_at_position(self, localPoint):
        """
        If there is one will return the layouts child widget containing the given point

        Parameters
        ----------
        localPoint : QtCore.QPointF
            The point

        Returns
        -------
        QtWidgets.QObject or None
            The child object or None if there isnt one at the given point

        """
        if self.childCount() == 0:
            return None

        for _child in self.children():
            _child_geometry = _child.geometry()
            if _child_geometry.contains(localPoint.x(), localPoint.y()):
                return _child

        return None

    def get_widget_index(self, widget):
        """
        Get a widgets index in the layout

        Parameters
        ----------
        widget

        Returns
        -------

        """
        for i, _widget in self.layout().children():
            if _widget == widget:
                return i

    def replace_widget(self, widget, newWidget):
        """
        Replace the given widget in the layout

        Parameters
        ----------
        widget
        newWidget

        Returns
        -------

        """
        _widget_index = self.get_widget_index(widget)

        self.disown_child(widget)

        self.insertWidget(_widget_index, newWidget)


class VLayout(Layout):

    def __init__(self, margins=[0, 0, 0, 0], spacing=0, *args, **kwargs):
        super().__init__(layoutOrientation=QtCore.Qt.Vertical, margins=margins, spacing=spacing)


class HLayout(Layout):

    def __init__(self, margins=[0, 0, 0, 0], spacing=0, *args, **kwargs):
        super().__init__(layoutOrientation=QtCore.Qt.Horizontal, margins=margins, spacing=spacing)
        print(self.stretch)


class ObjectListWidget(VLayout):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def populateObjectList(self, objectNames):
        for name in objectNames:
            _entry = self.makeObjectEntry(name)
            self.addWidget(_entry)

    def makeObjectEntry(self, objectName):
        objectEntry = HLayout()
        objectNameLabel = QtWidgets.QLabel(text=objectName)
        objectEntry.addWidget(objectNameLabel)
        return objectEntry


class ObjectExportWidget(VLayout):
    ExportObjectAnimation = QtCore.Signal(str, float, float)
    ImportObjectAnimation = QtCore.Signal(str, float)

    def __init__(self):
        super().__init__()
        self.setEmptyData()
        _export = QtWidgets.QPushButton(text="Export")
        _export.clicked.connect(self.emitExportObjectAnimation)
        _import = QtWidgets.QPushButton(text="Import")
        _import.clicked.connect(self.emitImportObjectAnimation)
        self.addWidgets([_export, _import])


    def populateObjectData(self, objectName, objectData):
        self.objectName = objectName
        _objectNameLabel = QtWidgets.QLabel(text=objectName)
        self.addWidget(_objectNameLabel, alignment=QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        return

    def buildDataDisplay(self, objectDataDict):
        for key, value in objectDataDict.items():
            _row = HLayout()
            _nameLabel = QtWidgets.QLabel(key)
            _dataLabel = QtWidgets.QLabel(value)
            _row.addWidgets([_nameLabel, _dataLabel])
            self.addWidget(_row)

    def clearObjectData(self):
        self.clear_layout()
        self.objectName = None
        self.setEmptyData()
        return

    def setEmptyData(self):
        emptyLabel = QtWidgets.QLabel(text='No Data To Display')
        self.addWidget(emptyLabel, alignment=QtCore.Qt.AlignCenter)

    def emitExportObjectAnimation(self):
        self.ExportObjectAnimation.emit(self.objectName, 0, 100)
        return

    def emitImportObjectAnimation(self):
        self.ImportObjectAnimation.emit(self.objectName, 0)
        return


class MainWindow(QtWidgets.QMainWindow):

    ObjectSelected = QtCore.Signal(str)
    ExportObjectAnimation = QtCore.Signal(str, float, float)
    ImportObjectAnimation = QtCore.Signal(str, float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _centralWidget = HLayout()
        self.setCentralWidget(_centralWidget)
        self.objectEntryList = ObjectListWidget()

        self.objectDataDisplay = ObjectExportWidget()
        self.objectDataDisplay.ExportObjectAnimation.connect(self.ExportObjectAnimation.emit)
        self.objectDataDisplay.ImportObjectAnimation.connect(self.ImportObjectAnimation.emit)

        _centralWidget.addWidget(self.objectEntryList)
        _centralWidget.addWidget(self.objectDataDisplay)

    def populateAnimatedObjects(self, animatedObjectsList):
        print(animatedObjectsList)
        self.objectEntryList.populateObjectList(animatedObjectsList)

    def emitObjectSelected(self, objectName):
        self.ObjectSelected.emit(objectName)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = ObjectListWidget()
    window.populateObjectList(['name', 'name1'])
    window.show()
    sys.exit(app.exec_())
