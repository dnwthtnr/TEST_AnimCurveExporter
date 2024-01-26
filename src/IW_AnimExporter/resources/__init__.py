import json, os, sys

currentDir = os.path.dirname(__file__)

packageDir = os.path.dirname(os.path.dirname(os.path.dirname(currentDir)))

appconfig = os.path.join(currentDir, r"appconfig.json")

def readJson(filepath):
    with open(filepath, "r") as file:
        data = json.load(file)
        return data

def _appconfig():
    return readJson(appconfig)

def _interfacemodes():
    return _appconfig().get(f"InterfaceModes")

class InterfaceModes:
    Mode1 = "Export"
    Mode2 = "Import"


    @staticmethod
    def getInterfaceModeName(interfaceMode):
        _modeDict = _interfacemodes().get(interfaceMode)
        return _modeDict.get("ModeName")


    @staticmethod
    def getInterfaceModeCommitButtonText(interfaceMode):
        _modeDict = _interfacemodes().get(interfaceMode)
        return _modeDict.get("ModeCommitButtonText")


    @staticmethod
    def getInterfaceControllerPortMethod(interfaceMode):
        _modeDict = _interfacemodes().get(interfaceMode)
        return _modeDict.get("ControllerPortMethod")


    @staticmethod
    def getInterfaceControllerObjectFilterMethod(interfaceMode):
        _modeDict = _interfacemodes().get(interfaceMode)
        return _modeDict.get("ControllerObjectFilterMethod")


    @staticmethod
    def getInterfaceModeAnimationDataDefaults(interfaceMode):
        _modeDict = _interfacemodes().get(interfaceMode)
        return _modeDict.get("ModeAnimationDataDefaults")

def defaultName():
    return _appconfig().get("DefaultName")

def fileExt():
    return _appconfig().get("FileExt")

def applicationName():
    return _appconfig().get("AppName")

def windowSize():
    return _appconfig().get("WindowSize")
