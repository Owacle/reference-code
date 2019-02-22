#!/bin/env python
###############################################################################
#
# Copyright (c) 2013 Goldtooth Creative
# All Rights Reserved.
#
# This file contains unpublished confidential and proprietary information
# of Goldtooth Creative.  The contents of this file may not be copied
# or duplicated, in whole or in part, by any means, electronic or hardcopy,
# without the express prior written permission of Goldtooth Creative.
#
#    $HeadURL: $
#    $Revision: $
#    $Author: $
#    $Date: $
#
###############################################################################

"""
Info Node Plugin to represent Assets in maya.
"""
# This code was highjacked from the Autodesk
# Development toolkit. This will create a transformation
# node with custom attributes what will integrate with
# shotgun and other asset pipeline tools.

# Modified by : Nathan Breton

# Usage:
# import maya.cmds
# maya.cmds.loadPlugin("gtInfoNode.py")
# maya.cmds.createNode("gtInfoNode")
#

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import sys

# ------------------------------------------------------------------------------
# Globals
# ------------------------------------------------------------------------------
gtInfoNodeTransformPluginName = "gtInfoNode"
gtInfoNodeTransformNodeName = "gtInfoNodePlugin"
gtInfoNodeTransformNodeID = OpenMaya.MTypeId(0x886745)
gtInfoNodeTransformMatrixID = OpenMaya.MTypeId(0x886746)

## Attributes
ATTRIBUTES = ['Character', 'Prop', 'Environment', 'Vehicle', 'FX', 'Camera', 'Light']

# keep track of instances of infoTransformMatrix to get around script limitation
# with proxy classes of base pointers that actually point to derived
# classes
kTrackingDictionary = {}


class infoTransformMatrix(OpenMayaMPx.MPxTransformationMatrix):

		def __init__(self):
				OpenMayaMPx.MPxTransformationMatrix.__init__(self)
				kTrackingDictionary[OpenMayaMPx.asHashable(self)] = self

		def __del__(self):
				del kTrackingDictionary[OpenMayaMPx.asHashable(self)]

class infoTransformNode(OpenMayaMPx.MPxTransform):
		aId = OpenMaya.MObject()
		aParentId = OpenMaya.MObject()
		aClass = OpenMaya.MObject()
		aType = OpenMaya.MObject()
		aDate = OpenMaya.MObject()

		fiAttr = OpenMaya.MObject()

		def __init__(self, transform=None):
				if transform is None:
						OpenMayaMPx.MPxTransform.__init__(self)
				else:
						OpenMayaMPx.MPxTransform.__init__(self, transform)

		def createTransformationMatrix(self):
				return OpenMayaMPx.asMPxPtr( infoTransformMatrix() )

		def className(self):
				return gtInfoNodeTransformNodeName


# create/initialize node and matrix
def matrixCreator():
		return OpenMayaMPx.asMPxPtr( infoTransformMatrix() )

def nodeCreator():
		return OpenMayaMPx.asMPxPtr( infoTransformNode() )

def nodeInitializer():
		# Class Enum Attribute
		eAttr = OpenMaya.MFnEnumAttribute()
		infoTransformNode.aClass = eAttr.create('Class', 'class', 0)
		for index, value in enumerate( ATTRIBUTES ):
			eAttr.addField(value, index)
		infoTransformNode.addAttribute(infoTransformNode.aClass)

		# Id Int Attribute
		numId = OpenMaya.MFnNumericAttribute()
		infoTransformNode.aId = numId.create("ID", "id", OpenMaya.MFnNumericData.kInt, 0)
		infoTransformNode.addAttribute(infoTransformNode.aId)

		# ParentId Int Attribute
		numParentId = OpenMaya.MFnNumericAttribute()
		infoTransformNode.aParentId = numParentId.create("ParentID", "ParentId", OpenMaya.MFnNumericData.kInt, 0)
		infoTransformNode.addAttribute(infoTransformNode.aParentId)

		# Type String Attribute
		tAttr = OpenMaya.MFnTypedAttribute()
		stringSave = OpenMaya.MFnStringData()
		stringSaveCreator = stringSave.create('')
		infoTransformNode.aType = tAttr.create('Type', 'type', OpenMaya.MFnStringData.kString, stringSaveCreator)
		infoTransformNode.addAttribute(infoTransformNode.aType)

		# Comment String Attribute
		cAttr = OpenMaya.MFnTypedAttribute()
		stringComment = OpenMaya.MFnStringData()
		stringCommentCreator = stringComment.create('')
		infoTransformNode.aDate = cAttr.create('PublishDate', 'publishDate', OpenMaya.MFnStringData.kString, stringCommentCreator)
		infoTransformNode.addAttribute(infoTransformNode.aDate)

		return

# initialize the script plug-in
def initializePlugin(mobject):
		mplugin = OpenMayaMPx.MFnPlugin(mobject)

		try:
				mplugin.registerTransform( gtInfoNodeTransformPluginName, gtInfoNodeTransformNodeID, \
																nodeCreator, nodeInitializer, matrixCreator, gtInfoNodeTransformMatrixID )
		except:
				sys.stderr.write( "Failed to register transform: %s\n" % gtInfoNodeTransformPluginName )
				raise

# uninitialize the script plug-in
def uninitializePlugin(mobject):
		mplugin = OpenMayaMPx.MFnPlugin(mobject)

		try:
				mplugin.deregisterNode( gtInfoNodeTransformNodeID )
		except:
				sys.stderr.write( "Failed to unregister node: %s\n" % gtInfoNodeTransformPluginName )
				raise
