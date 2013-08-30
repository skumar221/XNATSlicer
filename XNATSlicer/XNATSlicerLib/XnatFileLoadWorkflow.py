from XnatLoadWorkflow import *






class XnatFileLoadWorkflow(XnatLoadWorkflow):
        
    def setup(self):
        pass
    
    def load(self, args):
        """Iterates through the various types of Slicer nodes by attempting to load fileName
           and reading whether or not the loadNodeFromFile method returns True or False.  
           Also updates the UI locking and Status components."""

           
        # Call parent
        super(XnatFileLoadWorkflow, self).load(args)


        # Get the file
        self.browser.XnatCommunicator.getFile({self.xnatSrc: self.localDst})
        

        # Open file
        a = slicer.app.coreIOManager()
        t = a.fileType(self.localDst)
        nodeOpener = slicer.util.loadNodeFromFile(self.localDst, t)

        
        # Update status bar
        sessionArgs = XnatSessionArgs(browser = self.browser, srcPath = self.xnatSrc)
        sessionArgs['sessionType'] = "scene download"
        self.browser.XnatView.startNewSession(sessionArgs)
        
        if nodeOpener: 
           print ("'%s' successfully loaded."%(os.path.basename(self.localDst))) 
        else: 
            errStr = "Could not load '%s'!"%(os.path.basename(self.localDst))
            print (errStr)
            qt.QMessageBox.warning( None, "Load Failed", errStr) 
        return nodeOpener
