import sys, os
from PySide2 import QtWidgets, QtCore
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance



if os.path.dirname(__file__) not in sys.path:
    sys.path.append(os.path.dirname(__file__))

import ui, exportapi

file = r"Q:\__packages\_GitHub\IW_AnimExporter\testscene.mb"

def inMayaUi():
    try:
        import maya.standalone
        maya.standalone.initialize()
        return False
    except Exception as e:
        return True

def setupWindow(inMayaUi):

    if inMayaUi:
        mayaWindowPtr = omui.MQtUtil.mainWindow()
        mayaWindow = wrapInstance(int(mayaWindowPtr), QtWidgets.QWidget)
        window = ui.mainwindow.MainWindow(parent=mayaWindow)
    else:
        window = ui.mainwindow.MainWindow()

    controller = exportapi.scenedatacontroller.SceneDataController()

    controller.ObjectNamesGathered.connect(window.populateAnimatedObjects)
    controller.ObjectAnimationData.connect(window.populateObjectData)
    controller.SetCommitButtonText.connect(window.setPortCommitButtonText)
    controller.InterfaceModeChanged.connect(window.emptyPortPanelData)

    window.ObjectSelected.connect(controller.emitObjectAnimationData)
    window.PortCommitButtonClicked.connect(controller.portObjectAnimationData)
    window.InterfaceModeChanged.connect(controller.setInterfaceMode)

    window.controller = controller  # keep instance
    window.finishInitialization()
    return window

def main():
    isInMaya = inMayaUi()

    if not isInMaya:

        cmds.file(file, open=True, force=True)
        app = QtWidgets.QApplication(sys.argv)
        window = setupWindow(isInMaya)
        window.show()
        sys.exit(app.exec_())

    else:
        window = setupWindow(isInMaya)
        window.show()

if __name__ == "__main__":
    main()

