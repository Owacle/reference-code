
import sys, os, re

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx


# cmd name
kPluginCmdName="gtRenderSetup"

# cmd args
kReadFlag = "-r"
kReadLongFlag = "-read"
kWriteFlag = "-w"
kWriteLongFlag = "-write"
kResyncFlag = "-rs"
kResyncLongFlag = "-resync"
kRenderFlag = "-rn"
kRenderLongFlag = "-render"

# cb ids
sceneNewId = 0
sceneNewIdSet = False

sceneOpenId = 0
sceneOpenIdSet = False


def fileAfterNewCallback(clientData):
	try:
		from renderSetup import renderSetup as Rs
	except ImportError:
		sys.stderr.write("%s: Unable to load renderSetup python module for command execution\n" % kPluginCmdName)
	except:
		sys.stderr.write("%s: Unknown error on import of renderSetup python module. Exiting\n" % kPluginCmdName)
		raise
	try:
		Rs.createNewRenderSetup()
	except:
		sys.stderr.write("%s: Failed to execute fileAfterNewCallback\n" % kPluginCmdName)

def fileAfterOpenCallback(clientData):
  try:
    from renderSetup import renderSetup as Rs
  except ImportError:
    sys.stderr.write("%s: Unable to load renderSetup python module for command execution\n" % kPluginCmdName)
  except:
    sys.stderr.write("%s: Unknown error on import of renderSetup python module. Exiting\n" % kPluginCmdName)
    raise
  try:
    Rs.afterOpenRenderSetup()
  except:
    sys.stderr.write("%s: Failed to execute fileAfterOpenCallback\n" % kPluginCmdName)

def removeCallback(id):
	try:
		OpenMaya.MMessage.removeCallback( id )
	except:
		sys.stderr.write( "%s: Failed to remove callback\n" % kPluginCmdName)
		raise

def createCallback(clientData, type):
	# global declares module level variables that will be assigned
	global sceneNewIdSet
	global sceneOpenIdSet

	if type == "sceneNew":
		try:
			id = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterNew, fileAfterNewCallback, clientData)
		except:
			sys.stderr.write("%s: Failed to install scene new callback\n" % kPluginCmdName)
			sceneNewIdSet = False
		else:
			sceneNewIdSet = True
		return id
	if type == "sceneOpen":
		try:
			id = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterOpen, fileAfterOpenCallback, clientData)
		except:
			sys.stderr.write("%s: Failed to install scene open callback\n" % kPluginCmdName)
			sceneOpenIdSet = False
		else:
			sceneOpenIdSet = True
		return id

#command
class scriptedCommand(OpenMayaMPx.MPxCommand):
	def __init__(self):
		OpenMayaMPx.MPxCommand.__init__(self)

	def doIt(self,argList):		
		try:
			argData = OpenMaya.MArgDatabase(self.syntax(),argList)
		except RuntimeError, inp:
			OpenMaya.MGlobal.displayError(" ".join(("Invalid Argument", str(inp))))
			return

		try:
			from renderSetup import renderSetup as Rs
		except ImportError:
			sys.stderr.write("%s: Unable to load renderSetup python module for command execution\n" % kPluginCmdName)
		except:
			sys.stderr.write("%s: Unknown error on import of renderSetup python module. Exiting\n" % kPluginCmdName)
			raise
		
		if argData.isFlagSet(kReadFlag):
			try:
				Rs.read(argData.flagArgumentString(kReadFlag, 0))
			except:
				sys.stderr.write("%s: Unable to execute read directive for command\n" % kPluginCmdName)
			finally:
				return
			
		if argData.isFlagSet(kWriteFlag):
			try:
				Rs.write(argData.flagArgumentString(kWriteFlag, 0))
			except:
				sys.stderr.write("%s: Unable to execute write directive for command\n" % kPluginCmdName)
			finally:
				return
			
		if argData.isFlagSet(kResyncFlag):
			try:
				Rs.resync()
			except:
				sys.stderr.write("%s: Unable to execute resync directive for command\n" % kPluginCmdName)
				pass
			finally:
				return
			
		if argData.isFlagSet(kRenderFlag):
			try:
				Rs.render(argData.flagArgumentString(kRenderFlag, 0))
			except:
				sys.stderr.write("%s: Unable to execute render directive for command\n" % kPluginCmdName)
				pass
			finally:
				return
			
		# main command
		sys.stdout.write("%s: Command ran successfully" % kPluginCmdName)
		
		return
		
# Creator
def cmdCreator():
  # Create the command
  return OpenMayaMPx.asMPxPtr(scriptedCommand())

# Syntax creator
def syntaxCreator():
  syntax = OpenMaya.MSyntax()
  syntax.addFlag(kReadFlag, kReadLongFlag, OpenMaya.MSyntax.kString)
  syntax.addFlag(kWriteFlag, kWriteLongFlag, OpenMaya.MSyntax.kString)
  syntax.addFlag(kResyncFlag, kResyncLongFlag, OpenMaya.MSyntax.kBoolean)
  syntax.addFlag(kRenderFlag, kRenderLongFlag, OpenMaya.MSyntax.kString)
  return syntax

# Initialize the script plug-in
def initializePlugin(mobject):
	global sceneNewId
	global sceneOpenId

	mplugin = OpenMayaMPx.MFnPlugin(mobject, "Goldtooth Creative", "1.0", "Any")
	try:
		mplugin.registerCommand( kPluginCmdName, cmdCreator, syntaxCreator)
	except:
		sys.stderr.write( "Failed to register command: %s\n" % kPluginCmdName )
		raise

	#set up callbacks
	if not sceneNewIdSet:
		print "Installing Scene New callback"
		sceneNewId = createCallback("_noData_", "sceneNew")
	if not sceneOpenIdSet:
		print "Installing Scene Open callback"
		sceneOpenId = createCallback("_noData_", "sceneOpen")

# Uninitialize the script plug-in
def uninitializePlugin(mobject):
	global sceneNewId
	global sceneOpenId
	global sceneNewIdSet
	global sceneOpenIdSet
	
	# Remove the callback
	if (sceneNewIdSet):
		removeCallback(sceneNewId)
		sceneNewId = None
		sceneNewIdSet = False
	if (sceneOpenIdSet):
		removeCallback(sceneOpenId)
		sceneOpenId = None
		sceneOpenIdSet = False
		
	# Remove the plug-in command
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.deregisterCommand(kPluginCmdName)
	except:
		sys.stderr.write("Failed to unregister command: %s\n" % kPluginCmdName)
		raise	

