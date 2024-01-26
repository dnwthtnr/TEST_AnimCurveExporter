import json

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import maya.cmds as cmds


# region KEYS

attributeValueKey      = "value"
keyInTangentTypeKey    = "inTangentType"
keyInAngleKey          = "inAngle"
keyInWeightKey         = "inWeight"
keyOutTangentTypeKey   = "outTangentType"
keyOutAngleKey         = "outAngle"
keyOutWeightKey        = "outWeight"


# endregion


def getAnimatedSceneObjects():
    """
    Gets animated object names in current scene

    Returns
    -------
    list[str]
        The animated object names in the current scene

    """
    objects = cmds.ls(transforms=True, objectsOnly=True)
    animatedObjects = [object for object in objects if cmds.keyframe(object, query=True, keyframeCount=True) > 0]
    return animatedObjects

def getAnimatableSceneObjects():
    """
    Gets animatable object names in current scene

    Returns
    -------
    list[str]
        The animatable object names in the current scene

    """
    objects = cmds.ls(transforms=True, objectsOnly=True)
    animatedObjects = [object for object in objects if len(cmds.listAnimatable(object)) > 0]
    return animatedObjects

def isAnimatedAttribute(attribute):
    """
    Whether attribute is animated
    Parameters
    ----------
    attribute: str
        Attribute to check

    Returns
    -------
    bool
        Whether attribute is animated

    """
    return cmds.keyframe(attribute, query=True, keyframeCount=True) > 0

def getAnimatedObjectAttributes(objectName):
    """
    Gets attributes for the given object that are aniamted

    Parameters
    ----------
    objectName: str
        Object to get animated attributes of

    Returns
    -------
    list[str]
        Attributes for the object that are animated

    """
    objectKeyableAttributes = cmds.listAttr(objectName, keyable=True)
    animatedAttributes = [attr for attr in objectKeyableAttributes if cmds.keyframe(objectName, attribute=attr, query=True, keyframeCount=True) > 0]
    return animatedAttributes

def getKeyframeCurveData(objectName, keyframeTime, attribute):
    """
    Queries and collects the animation keyframe tangent data for the given object, keyframe, and attribute.

    Parameters
    ----------
    objectName: str
        Object to get data from
    keyframeTime: tuple(float)
        Range that the keyframe falls into (Typically 2 of the same float)
    attribute: str
        Attribute to get the keyframe curve data of

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
    returnDict[attributeValueKey]       = attributeValue
    returnDict[keyInTangentTypeKey]     = keyInTangentType[0]
    returnDict[keyInAngleKey]           = keyInAngle[0]
    returnDict[keyInWeightKey]          = keyInWeight[0]
    returnDict[keyOutTangentTypeKey]    = keyOutTangentType[0]
    returnDict[keyOutAngleKey]          = keyOutAngle[0]
    returnDict[keyOutWeightKey]         = keyOutWeight[0]

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
        if startFrame != None and keyframeTime < float(startFrame):
            continue
        if endFrame != None and keyframeTime > float(endFrame):
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
        self._targetObject = objectName

    def targetObject(self):
        return self._targetObject

    def setTargetObject(self, objectName):
        self._targetObject = objectName

    def exportCurveData(self, filepath, startFrame=None, endFrame=None, attributes=None):
        animatedAttributes = getAnimatedObjectAttributes(self.targetObject())

        if attributes is None:
            attributes = animatedAttributes

        animationCurveData = {}
        for attr in attributes:
            attributeCurveData = getAttributeAnimationData(
                objectName=self.targetObject(),
                startFrame=startFrame,
                endFrame=endFrame,
                attribute=attr
            )
            animationCurveData[attr] = attributeCurveData

        writeJson(filepath, animationCurveData)
        print("\n\nExport Complete\n\n")

    def importCurveData(self, filepath, keyframeOffset=0, attributes=None):
        animationCurveData = readJson(filepath)
        objectName = self.targetObject()
        for attr, animData in animationCurveData.items():
            if isinstance(attr, list) and attr not in attributes:
                continue
            for keyframeTime, keyframeData in animData.items():
                attrValue = keyframeData.get(attributeValueKey)
                keyframeTime = float(keyframeTime) + float(keyframeOffset)
                cmds.setKeyframe(objectName, attribute=attr, value=attrValue, time=keyframeTime)
                cmds.keyTangent(
                    objectName,
                    attribute=attr,
                    time=(keyframeTime, keyframeTime),
                    inTangentType=keyframeData.get(keyInTangentTypeKey),
                    inAngle=keyframeData.get(keyInAngleKey),
                    inWeight=keyframeData.get(keyInWeightKey),
                    outTangentType=keyframeData.get(keyOutTangentTypeKey),
                    outAngle=keyframeData.get(keyOutAngleKey),
                    outWeight=keyframeData.get(keyOutWeightKey)
                )
        return