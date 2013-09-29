from __main__ import vtk, qt, ctk, slicer



comment =  """

XnatPopup and its children are used for any needed popup interaction with Xnat.


QT specific issues:


from: http://harmattan-dev.nokia.com/docs/library/html/qt4/qt.html#WindowModality-enum

Qt::NonModal	0	The window is not modal and does not block input to other windows.
Qt::WindowModal	1	The window is modal to a single window hierarchy and blocks input to its parent window, all grandparent windows, and all siblings of its parent and grandparent windows.
Qt::ApplicationModal	2	The window is modal to the application and blocks input to all windows.
"""




class XnatPopup(object):
    """ Popup class for Xnat-relevant interactions
    """



    
    def __init__(self, browser, title = "XnatPopup", modality = 2):
        """Descriptor
        """
        self.browser = browser
        self.spacer = qt.QLabel("\n\n\n")

        self.window = qt.QWidget()
        self.window.windowTitle = title
                
        self.window.setWindowModality(modality)
        self.window.hide()
        
        self.layout = qt.QFormLayout()
        self.window.setLayout(self.layout)
        self.window.hide()


        
        
    def show(self, position = True):
        """Descriptor
        """
        self.window.show()
        
        if position:
            self.window.show()
            mainWindow = slicer.util.mainWindow()
            screenMainPos = mainWindow.pos
            x = screenMainPos.x() + mainWindow.width/2 - self.window.width/2
            y = screenMainPos.y() + mainWindow.height/2 - self.window.height/2
            self.window.move(qt.QPoint(x,y))
        
        self.window.raise_()
        

        
        
    def hide(self):
        self.window.hide()



        

        
class XnatDownloadPopup(XnatPopup):
    """ Subclass of the Xnat Popup class
    """



    
    def __init__(self, browser, title = "Xnat Download", memDisplay = "MB"):
        """ Descriptor
        """
        super(XnatDownloadPopup, self).__init__(browser = browser, title = title)

        
        # Params
        self.memDisplay = memDisplay
        self.downloadFileSize = None

        
        # Window size
        self.window.setFixedWidth(500)

    
        # Line text
        self.textDisp = ['', '[Unknown amount] ' +  self.memDisplay + ' out of [Unknown total] ' + self.memDisplay]
        self.lines = [qt.QLabel('') for x in range(0,2)]
        
        
        # Prog bar
        self.progBar = qt.QProgressBar()
        self.progBar.setFixedHeight(17)


        # Cancel button
        self.cancelButton = qt.QPushButton()
        self.cancelButton.setText("Cancel")
        self.cancelButton.connect('pressed()', self.browser.XnatCommunicator.cancelDownload)
        self.cancelButton.setFixedWidth(60)
        
        
        # Add widgets to layout
        for l in self.lines:
            self.layout.addRow(l)
        self.layout.addRow(self.progBar)
        self.layout.addRow(self.cancelButton)

        
        # Clear all
        self.reset()


        
        
    def reset(self):
        """ Resets tracked parameters
        """
        self.lines[0].setText(self.textDisp[0])
        self.lines[1].setText(self.textDisp[1])

        self.progBar.setMinimum(0)
        self.progBar.setMaximum(0)       

        self.downloadFileSize = 0
        self.downloadedBytes = 0
        
        
    def setDownloadFilename(self, filename):
        """ Descriptor
        """
        
        # Truncate filename
        filename = '...' + filename.split('/experiments')[1] if len(filename) > 33 else filename
        
        # Update Display
        self.lines[0].setText("Downloading: '%s'"%(filename))

        


    def recalcMem(self, size):
        """ For toggling between MB display and byte
        display.
        """
        if (self.memDisplay.lower() == 'mb'):
            return self.browser.utils.bytesToMB(size) 
        return size      



    
    def setDownloadFileSize(self, size):
        """ Descriptor
        """
        if size:
            self.downloadFileSize = size
            self.progBar.setMinimum(0)
            self.progBar.setMaximum(100)

            # Memory display
            size = self.recalcMem(size)

            # Update display
            self.lines[1].setText(self.lines[1].text.replace('[Unknown total]', str(size)))



            
        
    def update(self, downloadedBytes):
        """ Updates the progress bar in the popup accordingly with 
            downloadedBytes param.
        """

        if downloadedBytes > 0:
            self.downloadedBytes = int(downloadedBytes)
            size = self.downloadedBytes

            # Memory display
            size = self.recalcMem(size)
                
            # Update display
            self.lines[1].setText('%s MB out '%(str(size)) + self.lines[1].text.split('out')[1][1:])


        # If we know the size of downloaded files
        if self.downloadFileSize:
            
            # Calculate download pct
            pct = float(float(self.downloadedBytes) / float(self.downloadFileSize))

            # Output to Python command prompt
            #print "%s %s Downloaded: %s\tDownloadSize: %s\tPct: %s"%(self.browser.utils.lf(), self.lines[0].text, self.downloadedBytes , self.downloadFileSize, pct)

            # Update progress bar
            self.progBar.setValue(pct * 100)
            

        
        
        
    

