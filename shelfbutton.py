import sys


import importlib

reloadList = []

sys.path.append(r"[THIS FILE'S DIRECTORY]\src")

packages = ['ui', 'exportapi', 'IW_AnimExporter', 'resources']

for modName in sys.modules.keys():
    for package in packages:
        if modName == package:
            reloadList.append(modName)
            continue
        elif f"{package}." in modName:
            reloadList.append(modName)
            continue


for modName in reloadList:
    try:
        if modName not in sys.modules:
            continue
        if sys.modules[modName] is not None:
            del(sys.modules[modName])
    except Exception as e:
        continue
        
import IW_AnimExporter
IW_AnimExporter.main()


