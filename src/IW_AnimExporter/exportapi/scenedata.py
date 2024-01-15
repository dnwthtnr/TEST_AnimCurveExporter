import maya.cmds as cmds

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



