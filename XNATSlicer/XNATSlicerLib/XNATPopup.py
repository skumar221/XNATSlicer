from __main__ import vtk, qt, ctk, slicer


"""
from: http://harmattan-dev.nokia.com/docs/library/html/qt4/qt.html#WindowModality-enum

Qt::NonModal	0	The window is not modal and does not block input to other windows.
Qt::WindowModal	1	The window is modal to a single window hierarchy and blocks input to its parent window, all grandparent windows, and all siblings of its parent and grandparent windows.
Qt::ApplicationModal	2	The window is modal to the application and blocks input to all windows.
"""

        
class XNATPopup(object):
    
    def __init__(self, browser, title = "XNATPopup", modality = 2):
        
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



        

class XNATDownloadPopup(XNATPopup):


    def __init__(self, browser, title = "XNAT Download", memDisplay = "MB"):
        
        super(XNATDownloadPopup, self).__init__(browser = browser, title = title)

        self.memDisplay = memDisplay
        self.downloadFileSize = None

        #
        # Window size
        #
        self.window.setFixedWidth(500)

        #
        # Line text
        #
        textDisp = [
            "Downloading 'foo'",
            '[Unknown amount] ' +  self.memDisplay + ' out of [Unknown total] ' + self.memDisplay,
        ]
        self.lines = [qt.QLabel(i) for i in textDisp]

        #
        # Prog bar
        #
        self.progBar = qt.QProgressBar()
        self.progBar.setMinimum(0)
        self.progBar.setMaximum(0)
        self.progBar.setFixedHeight(17)

        #
        # Add widgets to layout
        #
        for l in self.lines:
            self.layout.addRow(l)
        self.layout.addRow(self.progBar)

        

        
    def setDownloadFilename(self, filename):
        self.downloadedBytes = 0
        self.progBar.setMaximum(0)
        # Truncate filename
        filename = '...' + filename.split('/experiments')[1] if len(filename) > 33 else filename
        self.lines[0].setText(self.lines[0].text.replace('foo', filename))


        
        
    def setDownloadFileSize(self, size):
        if size:
            self.downloadFileSize = size
            self.progBar.setMinimum(0)
            self.progBar.setMaximum(100)
            if (self.memDisplay.lower() == 'mb'):
                size = self.browser.utils.bytesToMB(size)
            self.lines[1].setText(self.lines[1].text.replace('[Unknown total]', str(size)))


            
        
    def update(self, downloadedBytes):
        if downloadedBytes > 0:
            self.downloadedBytes += int(downloadedBytes)
            size = self.downloadedBytes
            print "%s %s"%(self.browser.utils.lf(), size)
            if (self.memDisplay.lower() == 'mb'):
                size = self.browser.utils.bytesToMB(downloadedBytes)
            self.lines[1].setText(self.lines[1].text.replace('[Unknown amount]', str(size)))
        
        if self.downloadFileSize:
            self.progBar.setValue((self.downloadedBytes / self.downloadFileSize) * 100)
            

        
        
        
    

