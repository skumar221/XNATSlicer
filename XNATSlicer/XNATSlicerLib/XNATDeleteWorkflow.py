from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import zipfile



comment = """


"""





    
class XNATDeleteWorkflow(object):
    """ Descriptor above.
    """



    
    def __init__(self, browser):
        """ Parent class of any load workflow
        """

        # The browser
        self.browser = browser


        # The Dialog box
        self.deleteDialog = qt.QMessageBox()
        self.deleteDialog.setIcon(qt.QMessageBox.Warning)
        self.deleteDialog.setText("Are you sure you want to delete the file: '%s' from XNAT?"%(self.browser.XNATView.viewWidget.currentItem().text(self.browser.XNATView.column_name)))   
        self.deleteDialog.connect('buttonClicked(QAbstractButton*)', self.beginWorkflow)
        self.deleteDialog.addButton(qt.QMessageBox.Ok)
        self.deleteDialog.addButton(qt.QMessageBox.Cancel)  


        
        
    def beginWorkflow(self, button = None):
        """ Descriptor
        """

        # Show the delete dialog.  If 'ok' it cycles back to this function for condition below
        if not button:
  
            self.deleteDialog.show()

        # If 'ok' pressed
        elif button and button.text.lower().find('ok') > -1: 

            
            # Construct the full delete string based on type of tree item deleted
            delStr = self.browser.XNATView.getXNATDir(self.browser.XNATView.getParents(self.browser.XNATView.viewWidget.currentItem()))
            if (('files' in self.browser.XNATView.viewWidget.currentItem().text(self.browser.XNATView.column_category))
                or (self.browser.utils.slicerDirName in self.browser.XNATView.viewWidget.currentItem().text(self.browser.XNATView.column_category))):
                delStr = delStr
            else:
                delStr = os.path.dirname(delStr)
            self.browser.XNATCommunicator.delete(delStr)

            
            # Set currItem to parent and expand it   
            self.browser.XNATView.viewWidget.setCurrentItem(self.browser.XNATView.viewWidget.currentItem().parent())
            self.browser.XNATView.getChildrenExpanded(self.browser.XNATView.viewWidget.currentItem())

            
        # Cancel workflow if cancel pressed
        elif button and button.text.lower().find('cancel') > -1:
             return
