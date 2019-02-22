
import sys, os, re

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx


# cmd name
kPluginCmdName="gtSceneSetup"

# cmd args
kReadFlag = "-r"
kReadLongFlag = "-read"
kWriteFlag = "-w"
kWriteLongFlag = "-write"
kResyncFlag = "-rs"
kResyncLongFlag = "-resync"

# cb ids
afterNewId = 0
afterNewIdSet = False

afterOpenId = 0
afterOpenIdSet = False

afterSaveId = 0
afterSaveIdSet = False

def fileAfterNewCallback(clientData):
	try:
		from sceneSetup import sceneSetup as Ss
	except ImportError:
		sys.stderr.write("%s: Unable to load sceneSetup python module for command execution\n" % kPluginCmdName)
	except:
		sys.stderr.write("%s: Unknown error on import of sceneSetup python module. Exiting\n" % kPluginCmdName)
		raise
	try:
		Ss.afterNewSceneSetup()
	except:
		sys.stderr.write("%s: Failed to execute fileAfterNewCallback\n" % kPluginCmdName)

def fileAfterOpenCallback(clientData):
  try:
    from sceneSetup import sceneSetup as Ss
  except ImportError:
    sys.stderr.write("%s: Unable to load sceneSetup python module for command execution\n" % kPluginCmdName)
  except:
    sys.stderr.write("%s: Unknown error on import of sceneSetup python module. Exiting\n" % kPluginCmdName)
    raise
  try:
    Ss.afterOpenSceneSetup()
  except:
    sys.stderr.write("%s: Failed to execute fileAfterOpenCallback\n" % kPluginCmdName)

def fileAfterSaveCallback(clientData):
  try:
    from sceneSetup import sceneSetup as Ss
  except ImportError:
    sys.stderr.write("%s: Unable to load sceneSetup python module for command execution\n" % kPluginCmdName)
  except:
    sys.stderr.write("%s: Unknown error on import of sceneSetup python module. Exiting\n" % kPluginCmdName)
    raise
  try:
    Ss.afterSaveSceneSetup()
  except:
    sys.stderr.write("%s: Failed to execute fileAfterSaveCallback\n" % kPluginCmdName)

def removeCallback(id):
	try:
		OpenMaya.MMessage.removeCallback( id )
	except:
		sys.stderr.write( "%s: Failed to remove callback\n" % kPluginCmdName)
		raise

def createCallback(clientData, type):
	# global declares module level variables that will be assigned
	global afterNewIdSet
	global afterOpenIdSet
	global afterSaveIdSet

	if type == "afterNew":
		try:
			id = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterNew, fileAfterNewCallback, clientData)
		except:
			sys.stderr.write("%s: Failed to install scene new callback\n" % kPluginCmdName)
			afterNewIdSet = False
		else:
			afterNewIdSet = True
		return id
	if type == "afterOpen":
		try:
			id = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterOpen, fileAfterOpenCallback, clientData)
		except:
			sys.stderr.write("%s: Failed to install scene open callback\n" % kPluginCmdName)
			afterOpenIdSet = False
		else:
			afterOpenIdSet = True
		return id
	if type == "afterSave":
		try:
			id = OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterSave, fileAfterSaveCallback, clientData)
		except:
			sys.stderr.write("%s: Failed to install scene save callback\n" % kPluginCmdName)
			afterSaveIdSet = False
		else:
			afterSaveIdSet = True
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
			from sceneSetup import sceneSetup as Ss
		except ImportError:
			sys.stderr.write("%s: Unable to load sceneSetup python module for command execution\n" % kPluginCmdName)
		except:
			sys.stderr.write("%s: Unknown error on import of sceneSetup python module. Exiting\n" % kPluginCmdName)
			raise
		
		if argData.isFlagSet(kReadFlag):
			try:
				Ss.read(argData.flagArgumentString(kReadFlag, 0))
			except:
				sys.stderr.write("%s: Unable to execute read directive for command\n" % kPluginCmdName)
			finally:
				return
			
		if argData.isFlagSet(kWriteFlag):
			try:
				Ss.write(argData.flagArgumentString(kWriteFlag, 0))
			except:
				sys.stderr.write("%s: Unable to execute write directive for command\n" % kPluginCmdName)
			finally:
				return
			
		if argData.isFlagSet(kResyncFlag):
			try:
				Ss.resync()
			except:
				sys.stderr.write("%s: Unable to execute resync directive for command\n" % kPluginCmdName)
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
  syntax.addFlag(kSyncFlag, kSyncLongFlag, OpenMaya.MSyntax.kBoolean)
  return syntax

# Initialize the script plug-in
def initializePlugin(mobject):
	global afterNewId
	global afterOpenId
	global afterSaveId

	mplugin = OpenMayaMPx.MFnPlugin(mobject, "Goldtooth Creative", "1.0", "Any")
	try:
		mplugin.registerCommand( kPluginCmdName, cmdCreator, syntaxCreator)
	except:
		sys.stderr.write( "Failed to register command: %s\n" % kPluginCmdName )
		raise

	#set up callbacks
	if not afterNewIdSet:
		print "Installing After New callback"
		afterNewId = createCallback("_noData_", "afterNew")
	if not afterOpenIdSet:
		print "Installing After Open callback"
		afterOpenId = createCallback("_noData_", "afterOpen")
	if not afterSaveIdSet:
		print "Installing After Save callback"
		afterSaveId = createCallback("_noData_", "afterSave")

# Uninitialize the script plug-in
def uninitializePlugin(mobject):
	global afterNewId
	global afterOpenId
	global afterSaveId
	global afterNewIdSet
	global afterOpenIdSet
	global afterSaveIdSet
	
	# Remove the callback
	if (afterNewIdSet):
		removeCallback(afterNewId)
		afterNewId = None
		afterNewIdSet = False
	if (afterOpenIdSet):
		removeCallback(afterOpenId)
		afterOpenId = None
		afterOpenIdSet = False
	if (afterSaveIdSet):
		removeCallback(afterSaveId)
		afterSaveId = None
		afterSaveIdSet = False
		
	# Remove the plug-in command
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.deregisterCommand(kPluginCmdName)
	except:
		sys.stderr.write("Failed to unregister command: %s\n" % kPluginCmdName)
		raise	

 
