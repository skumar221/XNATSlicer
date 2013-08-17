from XNATLoadWorkflow import *

class FileLoader(XNATLoadWorkflow):
        
    def setup(self):
        pass
    
    def load(self, args):
        """Iterates through the various types of Slicer nodes by attempting to load fileName
           and reading whether or not the loadNodeFromFile method returns True or False.  
           Also updates the UI locking and Status components."""
        #----------------------------
        # STEP 1: Call parent
        #----------------------------
        super(FileLoader, self).load(args)
        #----------------------------
        # STEP 2: Get the file
        #----------------------------
        self.browser.XNATCommunicator.getFile({self.xnatSrc: self.localDst})
        #slicer.app.processEvents()
        #----------------------------
        # STEP 3: Open file
        #----------------------------
        a = slicer.app.coreIOManager()
        t = a.fileType(self.localDst)
        nodeOpener = slicer.util.loadNodeFromFile(self.localDst, t)
        #----------------------------
        # STEP 4: Update status bar
        #----------------------------
        sessionArgs = XNATSessionArgs(browser = self.browser, srcPath = self.xnatSrc)
        sessionArgs['sessionType'] = "scene download"
        self.browser.XNATView.startNewSession(sessionArgs)
        
        if nodeOpener: 
            self.browser.updateStatus(["", "'%s' successfully loaded."%(os.path.basename(self.localDst)),""]) 
        else: 
            errStr = "Could not load '%s'!"%(os.path.basename(self.localDst))
            self.browser.updateStatus(["", errStr,""])
            qt.QMessageBox.warning( None, "Load Failed", errStr) 
        return nodeOpener
