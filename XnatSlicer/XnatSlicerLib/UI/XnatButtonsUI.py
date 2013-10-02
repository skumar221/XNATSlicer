from __main__ import vtk, ctk, qt, slicer


import os


def generateButton(XnatButtons = None, iconOrLabel="", toolTip="", font = qt.QFont('Arial', 10, 10, False),  size = qt.QSize(30, 30), enabled=False):
    """ Creates an empty button.
    """
    
    button = qt.QPushButton()

    # Set either Icon or label, depending on
    # whehter the icon file exists.
    iconPath = os.path.join(XnatButtons.browser.utils.iconPath, iconOrLabel)
    if os.path.exists(iconPath):
        button.setIcon(qt.QIcon(iconPath))
    else:
        button.setText(iconOrLabel)

        
    button.setToolTip(toolTip)
    button.setFont(font)
    button.setFixedSize(size)
    button.setEnabled(enabled) 
    
    return button



def makeButtons_io(XnatButtons):

    buttons = {}
    buttons = {}
    
    buttons['load'] = generateButton(XnatButtons = XnatButtons, iconOrLabel = 'load.png', 
                                               toolTip = "Load file, image folder or scene from Xnat to Slicer.", 
                                               font = XnatButtons.browser.utils.labelFont,
                                               size = qt.QSize(30, 80), 
                                               enabled = False)
    
    
    buttons['save'] = generateButton(XnatButtons = XnatButtons, iconOrLabel = 'save.png', 
                                               toolTip ="Upload current scene to Xnat.", 
                                               font = XnatButtons.browser.utils.labelFont,
                                               size = qt.QSize(30, 80),
                                               enabled = False)
    
    buttons['delete'] = generateButton(XnatButtons = XnatButtons, iconOrLabel = 'delete.png', 
                                                 toolTip = "Delete Xnat file or folder.", 
                                                 font = XnatButtons.browser.utils.labelFont,
                                                 size = XnatButtons.browser.utils.buttonSizeSmall, 
                                                 enabled = False)
    
    buttons['addProj'] = generateButton(XnatButtons = XnatButtons, iconOrLabel = 'addproj.png', 
                                                  toolTip = "Add Project, Subject, or Experiment to Xnat.", 
                                                  font = XnatButtons.browser.utils.labelFont,
                                                  size = XnatButtons.browser.utils.buttonSizeSmall, 
                                                  enabled = False)


    buttons['test'] = generateButton(XnatButtons = XnatButtons, iconOrLabel = 'test.png', 
                                                  toolTip = "Run XNATSlicer tests...", 
                                                  font = XnatButtons.browser.utils.labelFont,
                                                  size = XnatButtons.browser.utils.buttonSizeSmall, 
                                                  enabled = False)

    return buttons



def makeButtons_filter(XnatButtons):
    
    buttons = {}
    buttons = {}
    
    buttons['all'] = generateButton(XnatButtons = XnatButtons, iconOrLabel = 'All', 
                                              toolTip = "All projects available to user.", 
                                              font = XnatButtons.browser.utils.labelFont,
                                              size = qt.QSize(50, 20), 
                                              enabled = True)

    
    buttons['accessed'] = generateButton(XnatButtons = XnatButtons, iconOrLabel = 'Accessed', 
                                                   toolTip = "Projects accessed by current user.", 
                                                   font = XnatButtons.browser.utils.labelFont,
                                                   size = qt.QSize(50, 20), 
                                                   enabled = True)
    

    #
    # Allows you to treat them as toggle buttons
    #
    for key in buttons:
        buttons[key].setCheckable(True)


    return buttons
