import maya.cmds as cmds
import json
from . import keys

def isAnimatedAtrribute(attribute):
    return cmds.keyframe(attribute, query=True, keyframeCount=True) > 0

def getAnimatedObjectAttributes(objectName):
    """

    Parameters
    ----------
    objectName

    Returns
    -------
    list[str]

    """
    objectKeyableAttributes = cmds.listAttr(objectName, keyable=True)
    animatedAttributes = [attr for attr in objectKeyableAttributes if cmds.keyframe(objectName, attribute=attr, query=True, keyframeCount=True) > 0]
    return animatedAttributes

def getKeyframeCurveData(objectName, keyframeTime, attribute):
    """

    Parameters
    ----------
    objectName
    keyframeTime
    attribute

    Returns
    -------
    dict

    """
    attributeValue = cmds.getAttr(f"{objectName}.{attribute}", time=keyframeTime[0])

    keyInTangentType    = cmds.keyTangent(objectName, attribute=attribute, time=keyframeTime, query=True, inTangentType=True)
    keyInAngle          = cmds.keyTangent(objectName, attribute=attribute, time=keyframeTime, query=True, inAngle=True)
    keyInWeight         = cmds.keyTangent(objectName, attribute=attribute, time=keyframeTime, query=True, inWeight=True)


    keyOutTangentType   = cmds.keyTangent(objectName, attribute=attribute, time=keyframeTime, query=True, outTangentType=True)
    keyOutAngle         = cmds.keyTangent(objectName, attribute=attribute, time=keyframeTime, query=True, outAngle=True)
    keyOutWeight        = cmds.keyTangent(objectName, attribute=attribute, time=keyframeTime, query=True, outWeight=True)

    returnDict = {}
    returnDict[keys.attributeValue]       = attributeValue
    returnDict[keys.keyInTangentType]     = keyInTangentType[0]
    returnDict[keys.keyInAngle]           = keyInAngle[0]
    returnDict[keys.keyInWeight]          = keyInWeight[0]
    returnDict[keys.keyOutTangentType]    = keyOutTangentType[0]
    returnDict[keys.keyOutAngle]          = keyOutAngle[0]
    returnDict[keys.keyOutWeight]         = keyOutWeight[0]

    return returnDict

def getAttributeAnimationData(objectName, attribute, startFrame=None, endFrame=None):
    """

    Parameters
    ----------
    objectName
    attribute

    Returns
    -------
    dict

    """
    attributeCurveData = {}

    # get attr keyframes
    keyframeTimes = cmds.keyframe(objectName, attribute=attribute, query=True)


    for keyframeTime in keyframeTimes:
        if startFrame != None and keyframeTime < startFrame:
            continue
        if endFrame != None and keyframeTime > endFrame:
            continue

        # get curve data
        curveData = getKeyframeCurveData(
            objectName=objectName,
            attribute=attribute,
            keyframeTime=(keyframeTime, keyframeTime)
        )

        attributeCurveData[keyframeTime] = curveData

    return attributeCurveData



def writeJson(filepath, data):
    with open(filepath, "w") as file:
        data = json.dumps(data, indent=4)
        file.write(data)

def readJson(filepath):
    with open(filepath, "r") as file:
        data = json.load(file)
        return data

class AnimationPort(object):

    def __init__(self, objectName):
        """
        Facilitates the importing and exporting of animation curves for the provided object

        Parameters
        ----------
        objectName: str
            The unique name for the target object
        """
        super().__init__()
        print(objectName)
        self._targetObject = objectName

    def targetObject(self):
        return self._targetObject

    def setTargetObject(self, objectName):
        self._targetObject = objectName

    def exportCurveData(self, filepath, startFrame=None, endFrame=None, attributes=None):
        animatedAttributes = getAnimatedObjectAttributes(self.targetObject())

        animationCurveData = {}
        for attr in animatedAttributes:
            attributeCurveData = getAttributeAnimationData(self.targetObject(), attr)
            animationCurveData[attr] = attributeCurveData

        writeJson(filepath, animationCurveData)

    def importCurveData(self, filepath, keyframeOffset=0, attributes=None):
        animationCurveData = readJson(filepath)
        objectName = self.targetObject()
        for attr, animData in animationCurveData.items():
            for keyframeTime, keyframeData in animData.items():
                attrValue = keyframeData.get(keys.attributeValue)
                cmds.setKeyframe(objectName, attribute=attr, value=attrValue, time=keyframeTime)
                cmds.keyTangent(
                    objectName,
                    attribute=attr,
                    time=(keyframeTime, keyframeTime),
                    inTangentType=keyframeData.get(keys.keyInTangentType),
                    inAngle=keyframeData.get(keys.keyInAngle),
                    inWeight=keyframeData.get(keys.keyInWeight),
                    outTangentType=keyframeData.get(keys.keyOutTangentType),
                    outAngle=keyframeData.get(keys.keyOutAngle),
                    outWeight=keyframeData.get(keys.keyOutWeight)
                )
        return

    def applyCurveData(self, keyframeOffset=0, attributes=None):

        return

scheme = {
    "attr1": [ [1, 15.2], [2, 123.55] ]
}