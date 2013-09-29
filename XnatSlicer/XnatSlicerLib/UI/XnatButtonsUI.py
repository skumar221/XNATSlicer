from __main__ import vtk, ctk, qt, slicer


import os


def generateButton(XnatButtons = None, iconFile="", toolTip="", font = qt.QFont('Arial', 10, 10, False),  size =  qt.QSize(30, 30), enabled=False):
    """ Creates an empty button.
    """
    
    button = qt.QPushButton()
    button.setIcon(qt.QIcon(os.path.join(XnatButtons.browser.utils.iconPath, iconFile)))
    button.setToolTip(toolTip)
    button.setFont(font)
    button.setFixedSize(size)

    button.setEnabled(enabled) 
    
    return button



def makeButtons(XnatButtons):

    buttons = {}
    
    buttons['load'] = generateButton(XnatButtons = XnatButtons, iconFile = 'load.png', 
                                               toolTip = "Load file, image folder or scene from Xnat to Slicer.", 
                                               font = XnatButtons.browser.utils.labelFont,
                                               size = XnatButtons.browser.utils.buttonSizeMed, 
                                               enabled = False)
    
    
    buttons['save'] = generateButton(XnatButtons = XnatButtons, iconFile = 'save.png', 
                                               toolTip ="Upload current scene to Xnat.", 
                                               font = XnatButtons.browser.utils.labelFont,
                                               size = XnatButtons.browser.utils.buttonSizeMed, 
                                               enabled = False)
    
    buttons['delete'] = generateButton(XnatButtons = XnatButtons, iconFile = 'delete.png', 
                                                 toolTip = "Delete Xnat file or folder.", 
                                                 font = XnatButtons.browser.utils.labelFont,
                                                 size = XnatButtons.browser.utils.buttonSizeSmall, 
                                                 enabled = False)
    
    buttons['addProj'] = generateButton(XnatButtons = XnatButtons, iconFile = 'addproj.png', 
                                                  toolTip = "Add Project, Subject, or Experiment to Xnat.", 
                                                  font = XnatButtons.browser.utils.labelFont,
                                                  size = XnatButtons.browser.utils.buttonSizeSmall, 
                                                  enabled = False)


    buttons['test'] = generateButton(XnatButtons = XnatButtons, iconFile = 'test.png', 
                                                  toolTip = "Run XNATSlicer tests...", 
                                                  font = XnatButtons.browser.utils.labelFont,
                                                  size = XnatButtons.browser.utils.buttonSizeSmall, 
                                                  enabled = False)

    return buttons
