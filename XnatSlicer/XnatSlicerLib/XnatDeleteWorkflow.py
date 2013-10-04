from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import zipfile



comment = """


"""





    
class XnatDeleteWorkflow(object):
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
        self.deleteDialog.setText("Are you sure you want to delete the file: '%s' from Xnat?"%(self.browser.XnatView.viewWidget.currentItem().text(self.browser.XnatView.column_name)))   
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
            delStr = self.browser.XnatView.getXnatDir(self.browser.XnatView.getParents(self.browser.XnatView.viewWidget.currentItem()))
            if (('files' in self.browser.XnatView.viewWidget.currentItem().text(self.browser.XnatView.column_category))
                or (self.browser.utils.slicerFolderName in self.browser.XnatView.viewWidget.currentItem().text(self.browser.XnatView.column_category))):
                delStr = delStr
            else:
                delStr = os.path.dirname(delStr)
            self.browser.XnatCommunicator.delete(delStr)

            
            # Set currItem to parent and expand it   
            self.browser.XnatView.viewWidget.setCurrentItem(self.browser.XnatView.viewWidget.currentItem().parent())
            self.browser.XnatView.onTreeItemExpanded(self.browser.XnatView.viewWidget.currentItem())

            
        # Cancel workflow if cancel pressed
        elif button and button.text.lower().find('cancel') > -1:
             return
