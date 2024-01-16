from PySide2 import QtCore

from . import scenedata, exporthandler


class SceneDataController(QtCore.QObject):
    AnimatedObjectsList = QtCore.Signal(list)
    ObjectAnimationData = QtCore.Signal(str, dict)
    ObjectNamesGathered = QtCore.Signal(list)

    def __init__(self):
        super().__init__()

    def initialize(self):
        self.emitAnimatedObjects()


    def emitAnimatedObjects(self):
        _animatedObjects = exporthandler.getAnimatedSceneObjects()
        self.ObjectNamesGathered.emit(_animatedObjects)


    def emitAnimatableObjects(self):
        _animatableObjects = exporthandler.getAnimatableSceneObjects()
        self.ObjectNamesGathered.emit(_animatableObjects)

    def emitObjectAnimationData(self, objectName):
        objectDataDict = {}
        objectDataDict["Animated Attributes"] = exporthandler.getAnimatedObjectAttributes(objectName)

        self.ObjectAnimationData.emit(objectName, objectDataDict)
        return

    def exportObjectAnimationData(self, objectName, filepath, startFrame, endFrame):
        exportHandler = exporthandler.AnimationPort(objectName=objectName)
        exportHandler.exportCurveData(filepath)
        return

    def importObjectAnimationData(self, objectName, filepath, keyframeOffset=0):
        portHandler = exporthandler.AnimationPort(objectName=objectName)
        portHandler.importCurveData(filepath=filepath)
        return
