from PySide2 import QtCore

from . import scenedata, exporthandler


class SceneDataController(QtCore.QObject):
    AnimatedObjectsList = QtCore.Signal(list)
    ObjectAnimationData = QtCore.Signal(str, dict)

    def __init__(self):
        super().__init__()

    def initialize(self):
        self.emitAnimatedObjects()


    def emitAnimatedObjects(self):
        _animatedObjects = scenedata.getAnimatedSceneObjects()
        self.AnimatedObjectsList.emit(_animatedObjects)

    def emitObjectAnimationData(self, objectName):
        return

    def exportObjectAnimationData(self, objectName, startFrame, endFrame):
        objectName = 'pCube1'
        exportHandler = exporthandler.AnimationPort(objectName=objectName)
        exportHandler.exportCurveData(r"Q:\__packages\_GitHub\IW_AnimExporter\testdata.json")
        return

    def importObjectAnimationData(self, objectName, keyframeOffset=0):
        objectName = 'pCube1'
        portHandler = exporthandler.AnimationPort(objectName=objectName)
        portHandler.importCurveData(filepath=r"Q:\__packages\_GitHub\IW_AnimExporter\testdata.json")
        return
