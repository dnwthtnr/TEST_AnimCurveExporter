import sys, os

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from PySide2 import QtCore
from . import exporthandler

# region Local Imports
parentPackageDir = os.path.dirname(os.path.dirname(__file__))
if parentPackageDir not in sys.path:
    sys.path.append(parentPackageDir)

from resources import InterfaceModes
# endregion


class SceneDataController(QtCore.QObject):
    AnimatedObjectsList = QtCore.Signal(list)
    ObjectAnimationData = QtCore.Signal(dict)
    ObjectNamesGathered = QtCore.Signal(list)

    SetCommitButtonText = QtCore.Signal(str)
    InterfaceModeChanged = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self._interfaceMode = None

    @QtCore.Slot()
    def setInterfaceMode(self, interfaceMode):
        self._interfaceMode = interfaceMode

        _commitButtonText = InterfaceModes.getInterfaceModeCommitButtonText(interfaceMode)

        _methodName = InterfaceModes.getInterfaceControllerObjectFilterMethod(interfaceMode)
        if not hasattr(self, _methodName):
            return

        objectListMethod = getattr(self, _methodName)
        objectListMethod()


        self.InterfaceModeChanged.emit()
        self.SetCommitButtonText.emit(_commitButtonText)

    def interfaceMode(self):
        return self._interfaceMode

    @QtCore.Slot()
    def emitObjectAnimationData(self, objectName):
        objectDataDict = {}
        objectDataDict["Object Name"] = objectName
        objectDataDict["Attributes"] = exporthandler.getAnimatedObjectAttributes(objectName)

        animationDataDefaults = InterfaceModes.getInterfaceModeAnimationDataDefaults(self.interfaceMode())
        objectDataDict.update(animationDataDefaults)


        self.ObjectAnimationData.emit(objectDataDict)
        return


    def _emitAnimatedObjects(self):
        _animatedObjects = exporthandler.getAnimatedSceneObjects()
        self.ObjectNamesGathered.emit(_animatedObjects)


    def _emitAnimatableObjects(self):
        _animatableObjects = exporthandler.getAnimatableSceneObjects()
        self.ObjectNamesGathered.emit(_animatableObjects)



    @QtCore.Slot()
    def portObjectAnimationData(self, animationData):
        _methodName = InterfaceModes.getInterfaceControllerPortMethod(self.interfaceMode())
        if not hasattr(self, _methodName):
            return

        portMethod = getattr(self, _methodName)
        portMethod(animationData)

    def _exportObjectAnimationData(self, animationData):

        objectName = animationData.get("Object Name")
        filepath = animationData.get("File Save Location")
        selected_attributes = animationData.get("Attributes")
        startFrame = animationData.get("Start Frame")
        endFrame = animationData.get("End Frame")

        exportHandler = exporthandler.AnimationPort(objectName=objectName)
        exportHandler.exportCurveData(filepath=filepath, startFrame=startFrame, endFrame=endFrame, attributes=selected_attributes)
        return

    def _importObjectAnimationData(self, animationData):
        objectName = animationData.get("Object Name")
        filepath = animationData.get("Animation File")
        selected_attributes = animationData.get("Attributes")
        keyframeOffset = animationData.get("Frame Offset")
        portHandler = exporthandler.AnimationPort(objectName=objectName)
        portHandler.importCurveData(filepath=filepath, keyframeOffset=keyframeOffset, attributes=selected_attributes)
        print("\n\nImport Complete\n\n")
