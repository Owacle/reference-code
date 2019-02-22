'''
Created on Jan 22, 2013

@author: Bill
'''

import maya.OpenMaya as om
import maya.cmds as cmds
import GenAPI

class ShapeTool():
    
    '''
    class for editing meshes 
    '''
    
    def __init__(self,shape):
        
        self.shape = shape
        self.shapePath = GenAPI.getDagPath(shape)
        
        geoItr = om.MItGeometry(self.shapePath)
        pointArray = om.MPointArray()
        geoItr.allPositions(pointArray, om.MSpace.kWorld)
        
        self.origPointArray = pointArray
        
    def getPointArray(self):
        
        '''
        method gathers point array from verts
        output pointArray(mPointArray)
        '''
        
        geoItr = om.MItGeometry(self.shapePath)
        pointArray = om.MPointArray()
        
        geoItr.allPositions(pointArray, om.MSpace.kWorld)
        
        return pointArray
    
    def setPointArray(self,pointArray):
        
        '''
        method sets positions of verts
        input pointArray(mPointArray)
        '''
        
        geoItr = om.MItGeometry(self.shapePath)
        geoItr.setAllPositions(pointArray, om.MSpace.kWorld)
        
      
    def getTranslationVectors(self,fromMesh):
        
        '''
        method build an array of vectors for trnaslation
        input fromMesh (python string)
        '''
        
        fromMeshPath = GenAPI.getDagPath(fromMesh)
        geoItr = om.MItGeometry(fromMeshPath)
        pointArrayA = om.MPointArray()
        geoItr.allPositions(pointArrayA, om.MSpace.kWorld)
        
        pointArrayB = self.getPointArray()

        if pointArrayA.length() == pointArrayB.length():
 
            outVectorArray = om.MVectorArray()
            itr = 0
             
            while itr <= pointArrayA.length():
                 
                vectorA = pointArrayA[itr]
                vectorB = pointArrayB[itr]
                vectorC = vectorA - vectorB
    
                outVectorArray.append(vectorC)
                itr += 1
                
        return  outVectorArray
    
    @staticmethod
    def setTranslation(mesh,vectorArray):
        
        meshPath = GenAPI.getDagPath(mesh)
        
        vertItr = om.MItMeshVertex(meshPath)
        
        while not vertItr.isDone():
            
            index = vertItr.index()
            vertItr.translateBy(vectorArray[index],om.MSpace.kWorld)
            vertItr.next()
            
    
            
def createParamTracker(selection = [],name = '',startVector = [1,0,0]):
    
    if not len(selection) == 2:
        om.MGlobal.displayError('Wrong Selection: select parent and driver.')
        
    else:
        parentObj = selection[0]
        drivingObj = selection[1]
        
        position = cmds.xform(drivingObj,q = True, ws = True,rp = True)
        rotation = cmds.xform(drivingObj,q = True, ws = True,rotation = True)
        
        paramTrackerGrp = cmds.group(empty = True,name = '%s_Grp'%name)
        cmds.move(position[0],position[1],position[2],paramTrackerGrp,ws = True)
        
        cmds.parentConstraint(parentObj,paramTrackerGrp,mo = True)
        
        null = cmds.group(name = '%s_Tracking_Null'%name,empty = True)
        nullGrp = cmds.group(n = '%s_Tracking_Grp'%name,empty = True)
        cmds.move(position[0],position[1],position[2],nullGrp,ws = True)
        #cmds.move(startVector[0],startVector[1],startVector[2],nullGrp,os = True)
        cmds.parent(null,nullGrp)
        cmds.parent(nullGrp, paramTrackerGrp)
        locator = cmds.spaceLocator(n = '%s_Tracking_Loc'%name)[0]
        cmds.parent(locator,nullGrp)
        pointOnSurfaceNode = cmds.createNode('closestPointOnSurface',name = '%s_POS'%name)
        plane = cmds.nurbsPlane(n = '%s_Tracking_Surface'%name,w = 2)[0]
        cmds.rotate(rotation[0],rotation[1],rotation[2],plane,ws = True)
        planeShape = cmds.listRelatives(plane,type = 'shape')[0]
        
        cmds.parent(null,paramTrackerGrp,r = True)
        cmds.parent(plane,paramTrackerGrp,r = True)
        
        cmds.move(startVector[0],startVector[1],startVector[2],null,os = True)
        cmds.parentConstraint(drivingObj,null,mo = True)
        
        cmds.connectAttr('%s.worldSpace[0]'%planeShape,'%s.inputSurface'%pointOnSurfaceNode)
        
        cmds.addAttr(locator,ln = 'uValue',at = 'double')
        cmds.setAttr('%s.uValue'%locator,e = True,keyable = True)
        
        cmds.addAttr(locator,ln = 'vValue',at = 'double')
        cmds.setAttr('%s.vValue'%locator,e = True,keyable = True)
        
        cmds.connectAttr('%s.parameterU'%pointOnSurfaceNode,'%s.uValue'%locator)
        cmds.connectAttr('%s.parameterV'%pointOnSurfaceNode,'%s.vValue'%locator)
        
        decomposeMatrix = cmds.createNode('decomposeMatrix',n = '%s_DM'%name)
        cmds.connectAttr('%s.worldMatrix[0]'%locator,'%s.inputMatrix'%decomposeMatrix)
        cmds.connectAttr('%s.outputTranslate'%decomposeMatrix,'%s.inPosition'%pointOnSurfaceNode)
        
        rivetNodes = cmds.kSurfaceRivetCmd(s = planeShape)
        cmds.rename(rivetNodes[0],'%s_Rivet'%name)
        cmds.rename(rivetNodes[1],'%s_Rivet_Loc'%name)
        
        rivetNodes[0] = '%s_Rivet'%name
        rivetNodes[1] = '%s_Rivet_Loc'%name
        closestPointOnSurface = cmds.createNode('closestPointOnSurface',n = '%s_CPS'%name)
        cmds.connectAttr('%s.outputTranslate'%decomposeMatrix, '%s.inPosition'%closestPointOnSurface)
        cmds.connectAttr('%s.worldSpace[0]'%planeShape,'%s.inputSurface'%closestPointOnSurface)
        cmds.connectAttr('%s.result.parameterU'%closestPointOnSurface,'%s.uValue'%rivetNodes[0])
        cmds.connectAttr('%s.result.parameterV'%closestPointOnSurface,'%s.vValue'%rivetNodes[0])

  