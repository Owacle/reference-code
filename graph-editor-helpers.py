def getDisplayedGraphEditorAttrs():
    '''
    Returns a list of attributes displayed in the graph editor
    '''
    # get the displayed animation curves from graph editor
    displayedCurves = cmds.selectionConnection('graphEditor1FromOutliner', q=True, object=True)
    
    # get the displayed attributes from graph editor
    displayedAttrs = []
    for displayedCurve in displayedCurves:
        displayedAttrs.append(displayedCurve.split('.')[1])
    return displayedAttrs

def displaySimilarAttrs():
    '''
    Addes similar attributes to displayed graph editor attributes
    '''
    selectedCtrls = cmds.ls(selection=True)
    displayedAttrs = getDisplayedGraphEditorAttrs()
    for selectedCtrl in selectedCtrls:
        for displayedAttr in displayedAttrs:
            cmds.selectionConnection('graphEditor1FromOutliner', e=True, select='%s.%s' %(selectedCtrl, displayedAttr))
