from PySide2 import QtGui, QtCore, QtWidgets
import os
from functools import partial


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


class ObjectListModel(QtCore.QAbstractItemModel):

    def __init__(self, objectList):
        """

        Parameters
        ----------
        objectList: list[str]
        """
        super().__init__()
        self.objectList = objectList

    def rowCount(self, parent=None, *args, **kwargs):
        """
        The amount of rows in the model

        Parameters
        ----------
        parent : QModelIndex
            Parent index
        args :
        kwargs :

        Returns
        -------
        int
            The amount of rows

        """
        return len(self.objectList)

    def columnCount(self, parent=None, *args, **kwargs):
        return 1

    def parent(self, index):
        return QtCore.QModelIndex()

    def index(self, row, column, parent=None, *args, **kwargs):
        return self.createIndex(row, column, parent)

    def objectForRow(self, row):
        return self.objectList[row-1]

    def data(self, index, role=None):
        """
        Returns the data for the given index and role

        Parameters
        ----------
        index : QtCore.QModelIndex
            The index to get data for
        role : QtCore.Qt.Role
            The role to get data for

        Returns
        -------
        object
            The data for the given row and role

        """
        if role == QtCore.Qt.DisplayRole:
            _row = index.row()
            _key_for_row = self.objectForRow(_row)
            return _key_for_row

    def headerData(self, section, orientation, role=None):
        """
        Returns the header data for the given index and role

        Parameters
        ----------
        section : int
            The index to get header data for.
        orientation : QtCore.Qt.Orientation
            The orientation of the header to get data for.
        role : QtCore.Qt.Role
            The role to get header data for.

        Returns
        -------
        object
            The header data for the given header index and row

        """
        if role != QtCore.Qt.DisplayRole or orientation == QtCore.Qt.Vertical:
            return None
        else:
            return "Animated Objects"

class ListItemSelectionView(QtWidgets.QListView):
    SelectionChanged = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self.setSelectionMode(QtWidgets.QListView.SingleSelection)

    def setModel(self, model):
        super().setModel(model)
        self.selectionModel().currentRowChanged.connect(self.selectionChanged)

    def selectionChanged(self, selected, deselected):
        """
        When selectio nchanges emit necessary data
        Parameters
        ----------
        selected
        deselected

        Returns
        -------

        """
        if not isinstance(selected, QtCore.QItemSelection):
            return
        if len(selected.indexes()) == 0:
            return

        selectedIndex = selected.indexes()[0]
        selectedData = self.model().data(selectedIndex, role=QtCore.Qt.DisplayRole)

        self.SelectionChanged.emit(selectedData)


class ObjectListWidget(VLayout):
    SelectionChanged = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listSelectionView = ListItemSelectionView()
        self.listSelectionView.SelectionChanged.connect(self.emitSelection)
        self.addWidget(self.listSelectionView)

    def populateObjectList(self, objectNames):
        _model = ObjectListModel(objectNames)
        self.listSelectionView.setModel(_model)

    def emitSelection(self, selectionData):
        self.SelectionChanged.emit(selectionData)

class FileSelector(HLayout):
    FileSelected = QtCore.Signal(str)

    def __init__(self, filepath="", allow_pasting=True, *args, **kwargs):
        """
        Facilitates the selection of a file

        Parameters
        ----------
        filepath: str
            Preexisting filepath to display
        allow_pasting: bool
            Whether to enable pasting of text into the file selection line edit
        args
        kwargs
        """
        super().__init__(*args, **kwargs)
        self.allowPasting = allow_pasting

        self.buildWidget(filepath)

    def buildWidget(self, filepath):
        """
        BInstantiates and sets up the widgets that make up the FileSelector
        Parameters
        ----------
        filepath: str
            Preexisting filepath to display

        """
        self.fileSelectionLineedit = self.buildFileSelection(filepath)
        self.button = self.build_button()

        self.buttonLayout = HLayout()
        self.buttonLayout.addWidget(self.button)

        self.addWidget(self.fileSelectionLineedit, stretch=1)
        self.addWidget(self.buttonLayout, alignment=QtCore.Qt.AlignRight)


    def buildFileSelection(self, filepath):
        """
        Builds a line edit to display a selected filepath
        Parameters
        ----------
        filepath: str
            Preexisting filepath to display

        Returns
        -------
        QtWidgets.QLineEdit

        """
        filepath = filepath if os.path.exists(filepath) else ""
        _line_edit = QtWidgets.QLineEdit(text=filepath)
        _line_edit.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        if not self.allowPasting:
            _line_edit.setReadOnly(True)
        self.FileSelected.connect(_line_edit.setText)
        return _line_edit

    def build_button(self):
        """
        builds a tool button with a file icon

        Returns
        -------
        QtWidgets.QToolButton

        """
        _button = QtWidgets.QToolButton()
        _button.setIcon(QtGui.QIcon(f"{os.path.dirname(__file__)}\open_file.svg"))
        _button.clicked.connect(self.openFileDialog)
        return _button

    def openFileDialog(self):
        """
        Opens file selection dialog

        """
        _file_browser = QtWidgets.QFileDialog()
        _selection_item = _file_browser.getOpenFileName(
            parent=self,
            caption=("Select File"),
            dir="/home"
        )
        _selected_file = _selection_item[0]

        if os.path.exists(_selected_file) is False:
            return

        self.fileSelectionLineedit.setText(_selected_file)

    def filepath(self):
        return self.fileSelectionLineedit.text()

class FilepathSelectionWindow(VLayout):
    SelectionCommited = QtCore.Signal(str)

    def __init__(self, display_text="Select a filepath", commit_button_text="Select",  *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fileSelector = FileSelector()
        self.fileSelector.setFixedWidth(250)

        titleLabel = QtWidgets.QLabel(text=display_text)

        commitSelectionButton = QtWidgets.QPushButton(commit_button_text)
        commitSelectionButton.clicked.connect(self.commitSelection)

        cancelButton = QtWidgets.QPushButton("Cancel")
        cancelButton.clicked.connect(self.cancel)

        buttonLayout = HLayout(spacing=5)
        buttonLayout.addWidgets([cancelButton, commitSelectionButton])

        self.addWidget(titleLabel, alignment=QtCore.Qt.AlignHCenter)
        self.addWidget(self.fileSelector, alignment=QtCore.Qt.AlignCenter)
        self.addWidget(buttonLayout, alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight)

        self.setFixedSize(270, 160)

    def commitSelection(self):
        self.SelectionCommited.emit(self.fileSelector.filepath())
        self.close()

    def cancel(self):
        self.close()



class ObjectExportWidget(VLayout):
    ExportObjectAnimation = QtCore.Signal(str, str, object, object)
    ImportObjectAnimation = QtCore.Signal(str, str, float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.dataDisplay = VLayout()

        self.buttonLayout = HLayout()
        exportButton = QtWidgets.QPushButton(text="Export")
        exportButton.clicked.connect(partial(self.openPortFialog, 'export'))
        importButton = QtWidgets.QPushButton(text="Import")
        importButton.clicked.connect(partial(self.openPortFialog, 'import'))
        self.buttonLayout.addWidgets([exportButton, importButton])

        self.addWidget(self.dataDisplay)
        self.addWidget(self.buttonLayout, alignment=QtCore.Qt.AlignBottom)

        self.setEmptyData()

    def openPortFialog(self, portMode='export'):
        if portMode == "export":
            self.selectionWindow = FilepathSelectionWindow(display_text="Select a filepath to export to", parent=self, margins=15, spacing=10)
            self.selectionWindow.SelectionCommited.connect(self.emitExportObjectAnimation)
        else:
            self.selectionWindow = FilepathSelectionWindow(display_text="Select a file to import", parent=self, margins=15, spacing=10)
            self.selectionWindow.SelectionCommited.connect(self.emitImportObjectAnimation)

        self.selectionWindow.setWindowFlag(QtCore.Qt.Tool, True)
        self.selectionWindow.show()


    def populateObjectData(self, objectName, objectData):
        self.dataDisplay.clear_layout()
        self.objectName = objectName
        _objectNameLabel = QtWidgets.QLabel(text=objectName)
        self.dataDisplay.addWidget(_objectNameLabel, alignment=QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.buttonLayout.setEnabled(True)

        return

    def buildDataDisplay(self, objectDataDict):
        for key, value in objectDataDict.items():
            _row = HLayout()
            _nameLabel = QtWidgets.QLabel(key)
            _dataLabel = QtWidgets.QLabel(value)
            _row.addWidgets([_nameLabel, _dataLabel])
            self.addWidget(_row)

    def setEmptyData(self):
        self.dataDisplay.clear_layout()
        self.objectName = None
        emptyLabel = QtWidgets.QLabel(text='No Data To Display')
        self.dataDisplay.addWidget(emptyLabel, alignment=QtCore.Qt.AlignCenter)
        self.buttonLayout.setEnabled(False)

    def emitExportObjectAnimation(self, filepath):
        self.ExportObjectAnimation.emit(self.objectName, filepath, None, None)
        return

    def emitImportObjectAnimation(self, filepath):
        self.ImportObjectAnimation.emit(self.objectName, filepath, 0)
        return

class ToggleButton(QtWidgets.QPushButton):
    StateChanged = QtCore.Signal(bool)

    def __init__(self, enabled_text='Enabled', disabled_text="Disabled"):
        super().__init__()
        self.enabledText = enabled_text
        self.disabledText = disabled_text
        self.setText(disabled_text)
        self.clicked.connect(self.toggleState)

    def toggleState(self):
        if self.text() == self.enabledText:
            self.setText(self.disabledText)
            self.StateChanged.emit(False)
            return
        self.setText(self.enabledText)
        self.StateChanged.emit(True)

    def toggleState(self):
        return self.text() == self.enabledText


class MainWindow(QtWidgets.QMainWindow):

    ObjectSelected = QtCore.Signal(str)
    ExportObjectAnimation = QtCore.Signal(str, str, object, object)
    ImportObjectAnimation = QtCore.Signal(str, str, float)

    ExportModeEnabled = QtCore.Signal()
    ImportModeEnabled = QtCore.Signal()


    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _centralWidget = VLayout(margins=10)

        self.toolModeButton = ToggleButton(enabled_text="Import", disabled_text="Export")
        self.toolModeButton.StateChanged.connect(self.setExportMode)

        _centralWidget.addWidget(self.toolModeButton, alignment=QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)

        splitter = QtWidgets.QSplitter()
        _centralWidget.addWidget(splitter, stretch=1)
        self.setCentralWidget(_centralWidget)

        self.objectEntryList = ObjectListWidget(margins=5)
        self.objectEntryList.SelectionChanged.connect(self.emitObjectSelected)

        self.objectDataDisplay = ObjectExportWidget(margins=5)
        self.objectDataDisplay.ExportObjectAnimation.connect(self.ExportObjectAnimation.emit)
        self.objectDataDisplay.ImportObjectAnimation.connect(self.ImportObjectAnimation.emit)

        splitter.addWidget(self.objectEntryList)
        splitter.addWidget(self.objectDataDisplay)

    def finishInitialization(self):
        exportMode = self.toolModeButton.toggleState()
        if exportMode:
            self.ExportModeEnabled.emit()
            return
        self.ImportModeEnabled.emit()
        return

    def populateObjectData(self, objectName, objectData):
        """
        Populates the ObjectExportWidget with the given data and object name

        Parameters
        ----------
        objectName: str
            Name of the object
        objectData: dict
            Data to display for the given object

        """
        self.objectDataDisplay.populateObjectData(objectName, objectData)

    def setExportMode(self, export):
        if export:
            self.ExportModeEnabled.emit()
            return

        self.ImportModeEnabled.emit()

    def populateAnimatedObjects(self, animatedObjectsList):
        self.objectEntryList.populateObjectList(animatedObjectsList)

    def emitObjectSelected(self, objectName):
        self.ObjectSelected.emit(objectName)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = ObjectListWidget()
    window.populateObjectList(['name', 'name1'])
    window.show()
    print('n')
    sys.exit(app.exec_())
