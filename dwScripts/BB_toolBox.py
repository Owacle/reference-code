import sys
import os
import maya.mel as mel



path = 'T:/dwtv/hub/Tools/Rig/scripts/bb/mel/'
melFiles = os.listdir('T:/dwtv/hub/Tools/Rig/scripts/bb/mel')


for file in melFiles:
    mel.eval( 'source "%s%s"'%(path,file))

file = __file__
filePath = os.path.split(file)
bb = os.path.split(filePath[0])
scripts = os.path.split(bb[0])
Rig = os.path.split(scripts[0])
Tools = Rig[0]


sys.path.append(Tools)

from PySide import QtCore,QtGui,shiboken

from py import UILib
reload(UILib)

windowVar = ''
def open_win():
    global windowVar
    try:
        windowVar.close()  # @UndefinedVariable
    except:
        pass
            
    toolWin = UILib.ToolBoxWin()
    toolWin.show()
    windowVar = toolWin


