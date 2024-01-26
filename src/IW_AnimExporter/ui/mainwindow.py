import os, sys, pathlib

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import shiboken2
from PySide2 import QtGui, QtCore, QtWidgets

# region Local Imports
parentPackageDir = os.path.dirname(os.path.dirname(__file__))
if parentPackageDir not in sys.path:
    sys.path.append(parentPackageDir)

import resources

from . import style
# endregion


def generateUniqueFilepath(filepath):
    _returnPath = filepath
    _path = pathlib.Path(filepath)
    dir = _path.parent
    name = _path.stem
    suffix = _path.suffix
    count = 0
    while os.path.exists(_returnPath):
        _returnPath = os.path.join(dir, f"{name}_{count}.{suffix}")
        count += 1

    return _returnPath


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
        self.setFocusPolicy(QtCore.Qt.NoFocus)

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


class FileSaver(HLayout):
    DirectorySelected = QtCore.Signal(str)

    def __init__(self, directory=None, default_name=None, fileExt='json', allow_pasting=True, *args, **kwargs):
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
        if not directory:
            directory = resources.packageDir
        if not default_name:
            default_name = resources.defaultName()

        self.fileExt = fileExt
        super().__init__(spacing=0, *args, **kwargs)
        self.allowPasting = allow_pasting

        self.buildWidget(directory, default_name)

    def buildWidget(self, directory, default_name):
        """
        BInstantiates and sets up the widgets that make up the FileSelector
        Parameters
        ----------
        filepath: str
            Preexisting filepath to display

        """
        self.dirSelectionLineedit = self.buildFileSelection(directory)
        self.button = self.build_button()

        self.buttonLayout = HLayout()
        self.buttonLayout.addWidget(self.button)

        self.fileNameLineEdit = self.buildFileNameLineEdit(default_name)

        self.addWidget(self.dirSelectionLineedit, stretch=1)
        self.addWidget(self.fileNameLineEdit, alignment=QtCore.Qt.AlignRight)
        self.addWidget(self.buttonLayout, alignment=QtCore.Qt.AlignRight)


    def buildFileNameLineEdit(self, default_name):
        widget = QtWidgets.QLineEdit(text=default_name)
        return widget


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
        self.DirectorySelected.connect(_line_edit.setText)
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
        _selection_item = _file_browser.getExistingDirectory(
            self,
            ("Select Directory"),
            "/home",
            QtWidgets.QFileDialog.ShowDirsOnly
        )
        _selected_file = _selection_item

        if os.path.exists(_selected_file) is False:
            return

        self.dirSelectionLineedit.setText(_selected_file)

    def filepath(self):
        _directory = self.dirSelectionLineedit.text()
        _filename = self.fileNameLineEdit.text()

        if self.fileExt not in _filename:
            _filename = f"{_filename}.{self.fileExt}"

        filepath = os.path.join(_directory, _filename)
        if os.path.exists(filepath):
            filepath = generateUniqueFilepath(filepath)

        return filepath


class ToggleButton(QtWidgets.QPushButton):
    StateChanged = QtCore.Signal(bool)
    TextChanged = QtCore.Signal(str)

    def __init__(self, enabled_text='Enabled', disabled_text="Disabled", state_auto_update=True):
        super().__init__()
        self.stateAutoUpdate = state_auto_update
        self.enabledText = enabled_text
        self.disabledText = disabled_text
        self.setText(enabled_text)
        self.clicked.connect(self.switchToggleState)

    def switchToggleState(self, *args):
        if not self.stateAutoUpdate:
            return
        if self.text() == self.enabledText:
            self.setText(self.disabledText)
            self.TextChanged.emit(self.disabledText)
            self.StateChanged.emit(False)
            return
        self.setText(self.enabledText)
        self.TextChanged.emit(self.enabledText)
        self.StateChanged.emit(True)

    def setToggleState(self, stateBool):
        if stateBool:
            self.setText(self.enabledText)
            return

        self.setText(self.disabledText)

    def toggleState(self):
        return self.text() == self.enabledText


class Checklist(VLayout):

    def __init__(self, items=None):
        super().__init__()
        if items is None:
            items = []
        self.setItems(items)

    def addItem(self, text):
        item = QtWidgets.QCheckBox(text=text)
        self.addWidget(item)

    def setItems(self, items):
        self.clear_layout()
        self.addStretch(1)
        for item in items:
            self.addItem(item)

    def removeItem(self, index):
        if not isinstance(index, int):
            raise TypeError
        if index > self.childCount():
            raise ValueError

        targetChild = self.children()[index]
        self.disown_child(targetChild)

    def checkedItems(self):
        checkedItems = []
        for child in self.children():
            if not isinstance(child, QtWidgets.QCheckBox):
                continue
            if child.isChecked():
                checkedItems.append(child.text())

        return checkedItems



# region AttributeEditor

#   This set of classes are designed to only get a result value from a user's selection from a queried data set.
#   in the current state it is not designed to return data that is correctly representative of the state of the
#   originally supplied data set and thus the result dict from an 'AttributeEditorHolder' can not be used again to
#   repopulate the widget to the state it was at when the result was derived

class AttributeEditor(HLayout):

    def __init__(self, attribute_name, attribute_value, attribute_name_label_width=100):
        super().__init__()

        self._attributeNameLabel = self._buildAttributeNameLabel(attribute_name)
        self._attributeNameLabel.setFixedWidth(attribute_name_label_width)

        self._attributeEditorWidget = self.buildEditorWidget()
        self.setAttributeValue(attribute_value)

        self.addWidget(self._attributeNameLabel, alignment=QtCore.Qt.AlignTop)
        self.addWidget(self._attributeEditorWidget)

    def attributeName(self):
        return self._attributeNameLabel.text()

    def attributeValue(self):
        return self.getEditorValue(self._attributeEditorWidget)

    def setAttributeValue(self, value):
        if not self.valueValidator(value):
            raise TypeError
        self.setEditorValue(self._attributeEditorWidget, value)


    def _buildAttributeNameLabel(self, attribute_name):
        label = QtWidgets.QLabel(text=attribute_name)
        return label


    # region REIMPLEMENTED

    def getEditorValue(self, attribute_editor):
        raise NotImplementedError("Must implement this method")

    def setEditorValue(self, attribute_editor, value):
        raise NotImplementedError("Must implement this method")

    def setReadOnly(self, enabled):
        _attr = getattr(self._attributeEditorWidget, "setReadOnly", None)
        if not callable(_attr):
            return
        self._attributeEditorWidget.setReadOnly(enabled)

    def buildEditorWidget(self):
        raise NotImplementedError("Must implement this method")

    @staticmethod
    def valueValidator(self, test_value):
        """

        Parameters
        ----------
        test_value

        Returns
        -------
        bool
            Whether test value is of the valid type description

        """
        raise NotImplementedError("Must implement this method")

    # endregion

class AttributeEditorChecklist(AttributeEditor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def valueValidator(self, test_value):

        # In it's current serialization this datatype being a plain

        if not isinstance(test_value, list):
            return False
        if len(test_value) < 2:
            return False

        return True

    def getEditorValue(self, attribute_editor):
        return attribute_editor.checkedItems()

    def buildEditorWidget(self):
        editor = Checklist()
        return editor

    def setEditorValue(self, attribute_editor, value):
        attribute_editor.setItems(value)

class AttributeEditorStringDisplay(AttributeEditor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def valueValidator(self, test_value):

        # In it's current serialization this datatype being a plain

        if not isinstance(test_value, str):
            return False

        return True

    def getEditorValue(self, attribute_editor):
        return attribute_editor.text()

    def buildEditorWidget(self):
        editor = QtWidgets.QLineEdit()
        return editor

    def setEditorValue(self, attribute_editor, value):
        attribute_editor.setText(value)

class AttributeEditorIntDisplay(AttributeEditor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def valueValidator(self, test_value):

        # In it's current serialization this datatype being a plain

        if not isinstance(test_value, int):
            return False

        return True

    def getEditorValue(self, attribute_editor):
        return attribute_editor.value()

    def buildEditorWidget(self):
        editor = QtWidgets.QSpinBox()
        return editor

    def setEditorValue(self, attribute_editor, value):
        attribute_editor.setValue(value)

class AttributeEditorFileSaveDisplay(AttributeEditor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def valueValidator(self, test_value):

        # In it's current serialization this datatype being a plain

        if not isinstance(test_value, str):
            return False

        if test_value != "file//SAVE//json":
            return False

        return True

    def getEditorValue(self, attribute_editor):
        return attribute_editor.filepath()

    def buildEditorWidget(self):
        editor = FileSaver()
        return editor

    def setEditorValue(self, attribute_editor, value):
       pass

class AttributeEditorFileSelectDisplay(AttributeEditor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def valueValidator(self, test_value):

        # In it's current serialization this datatype being a plain

        if not isinstance(test_value, str):
            return False

        if test_value != "file//SELECT//json":
            return False

        return True

    def getEditorValue(self, attribute_editor):
        return attribute_editor.filepath()

    def buildEditorWidget(self):
        editor = FileSelector()
        return editor

    def setEditorValue(self, attribute_editor, value):
       pass

class AttributeEditorHolder(VLayout):

    def __init__(self, attribute_editor_selection, locked_attributes=None, hidden_attributes=None, attribute_name_label_width=50, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not locked_attributes:
            locked_attributes = []
        if not hidden_attributes:
            hidden_attributes = []
        self.attributeNameLabelWidth = attribute_name_label_width
        self.lockedAttributes = locked_attributes
        self.hiddenAttributes = hidden_attributes
        self.attributeEditorSelection = attribute_editor_selection

    def buildAttributeEditors(self, attribute_editor_selection, attribute_dictionary):
        for attributeName, attributevalue in attribute_dictionary.items():
            _editor = self.retreiveAttributeEditor(attributeName, attributevalue, attribute_editor_selection)
            if _editor is None:
                continue
            if attributeName in self.lockedAttributes:
                _editor.setReadOnly(True)
            if attributeName in self.hiddenAttributes:
                _editor.setVisible(False)
            self.addWidget(_editor)

        self.addStretch(1)

    def retreiveAttributeEditor(self, attributeName, attributeValue, attribute_editor_selection):
            for attributeEditor in attribute_editor_selection:
                if not attributeEditor.valueValidator(self, attributeValue):
                    continue

                _editor = attributeEditor(
                    attribute_name=attributeName,
                    attribute_value = attributeValue,
                    attribute_name_label_width=self.attributeNameLabelWidth
                )
                return _editor

    def setAttributes(self, attribute_dictionary):
        self.clear_layout()
        self.buildAttributeEditors(self.attributeEditorSelection, attribute_dictionary)

    def attributeDictionary(self):
        attributeDictionary = {}
        for child in self.children():
            attributeName = child.attributeName()
            attributeValue = child.attributeValue()
            attributeDictionary[attributeName] = attributeValue
        return attributeDictionary

# endregion

class ObjectListPanel(VLayout):
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


class ObjectPortPanel(VLayout):
    # ExportObjectAnimation = QtCore.Signal(str, str, object, object)
    # ImportObjectAnimation = QtCore.Signal(str, str, float)

    CommitButtonClicked = QtCore.Signal(dict)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.dataDisplay = self.buildDataDisplay()
        self.commitButton = self.buildCommitButton("Export")

        self.addWidget(self.dataDisplay)
        self.addWidget(self.commitButton, alignment=QtCore.Qt.AlignBottom)

        self.setEmptyData()

    def buildCommitButton(self, button_text):
        button = QtWidgets.QPushButton(text=button_text)
        button.setStyleSheet(style.maya_button)
        button.setMinimumSize(100, 35)
        button.clicked.connect(self.emitCommitButtonClicked)
        return button

    def emitCommitButtonClicked(self):
        self.CommitButtonClicked.emit(self.dataDisplay.attributeDictionary())

    def setCommitButtonText(self, text):
        self.commitButton.setText(text)

    def emitCommitButtonClicked(self):
        _data = self.dataDisplay.attributeDictionary()

        self.CommitButtonClicked.emit(_data)


    def buildDataDisplay(self):
        widget = AttributeEditorHolder(
            attribute_editor_selection=[
                AttributeEditorFileSaveDisplay,
                AttributeEditorFileSelectDisplay,
                AttributeEditorIntDisplay,
                AttributeEditorChecklist,
                AttributeEditorStringDisplay
            ],
            attribute_name_label_width=150,
            spacing=5
        )
        return widget


    def populateObjectData(self, objectData):
        self.dataDisplay.setAttributes(objectData)
        # self.titleLabel = QtWidgets.QLabel(text=objectName)
        # self.dataDisplay.addWidget(self.titleLabel, alignment=QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.commitButton.setEnabled(True)

        return

    def setEmptyData(self):
        self.dataDisplay.clear_layout()
        emptyLabel = QtWidgets.QLabel(text='No Data To Display')
        self.dataDisplay.addWidget(emptyLabel, alignment=QtCore.Qt.AlignCenter)
        self.commitButton.setEnabled(False)

    def emitExportObjectAnimation(self, filepath):
        self.ExportObjectAnimation.emit(self.objectName, filepath, None, None)
        return

    def emitImportObjectAnimation(self, filepath):
        self.ImportObjectAnimation.emit(self.objectName, filepath, 0)
        return


class MainWindow(QtWidgets.QMainWindow):

    ObjectSelected = QtCore.Signal(str)
    PortCommitButtonClicked = QtCore.Signal(dict)
    InterfaceModeChanged = QtCore.Signal(str)


    def __new__(cls, *args, **kwargs):
        if hasattr(cls, 'instance'):
            shiboken2.delete(cls.instance)
        cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buildMainWindow()

    def buildMainWindow(self):

        self.toolModeButton = self._buildInterfaceModeButton()

        modeLabel = QtWidgets.QLabel(text="Interface Mode: ")
        modeLayout = HLayout(spacing=10)
        modeLayout.addWidget(modeLabel)
        modeLayout.addWidget(self.toolModeButton)


        self.sceneObjectList = ObjectListPanel()
        self.sceneObjectList.SelectionChanged.connect(self.emitObjectSelected)
        self.sceneObjectList.setStyleSheet(style.maya_outliner)



        self.objectPortPanel = ObjectPortPanel(margins=8)
        self.objectPortPanel.CommitButtonClicked.connect(self.PortCommitButtonClicked.emit)

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self.sceneObjectList)
        splitter.addWidget(self.objectPortPanel)
        splitter.setStyleSheet(style.maya_splitter)

        _centralWidget = VLayout(margins=10, spacing=8)
        _centralWidget.addWidget(modeLayout, alignment=QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        _centralWidget.addWidget(splitter, stretch=1)

        self.setCentralWidget(_centralWidget)
        self.setMinimumSize(*resources.windowSize())
        self.setWindowTitle(resources.applicationName())
        self.setStyleSheet(style.maya_widget)
        splitter.setSizes([300, 700])


    def _buildInterfaceModeButton(self):
        button = ToggleButton(
            enabled_text=resources.InterfaceModes.getInterfaceModeName(resources.InterfaceModes.Mode1),
            disabled_text=resources.InterfaceModes.getInterfaceModeName(resources.InterfaceModes.Mode2)
        )
        button.setMinimumSize(150, 30)
        button.TextChanged.connect(self.InterfaceModeChanged.emit)
        button.setStyleSheet(style.maya_button)
        return button


    def finishInitialization(self):
        exportMode = self.toolModeButton.toggleState()
        if exportMode:
            self.InterfaceModeChanged.emit(resources.InterfaceModes.Mode1)
            return
        self.InterfaceModeChanged.emit(resources.InterfaceModes.Mode2)
        return

    @QtCore.Slot()
    def populateObjectData(self, objectData):
        """
        Populates the ObjectExportWidget with the given data and object name

        Parameters
        ----------
        objectName: str
            Name of the object
        objectData: dict
            Data to display for the given object

        """
        self.objectPortPanel.populateObjectData(objectData)

    @QtCore.Slot()
    def setPortCommitButtonText(self, text):
        self.objectPortPanel.setCommitButtonText(text)

    @QtCore.Slot()
    def emptyPortPanelData(self):
        self.objectPortPanel.setEmptyData()

    @QtCore.Slot()
    def populateAnimatedObjects(self, animatedObjectsList):
        self.sceneObjectList.populateObjectList(animatedObjectsList)

    def emitObjectSelected(self, objectName):
        self.ObjectSelected.emit(objectName)
