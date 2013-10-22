from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil



comment = """
XnatAnimatedCollapsible

TODO:        
"""



class XnatAnimatedCollapsible(qt.QFrame):
    """ Descriptor above.
    """
    
    def __init__(self, MODULE, title, maxHeight = 300):
        """ Init function.
        """

        qt.QFrame.__init__(self)

        self.MODULE = MODULE
        self.rightArrowChar = u'\u25b8'
        self.downArrowChar = u'\u25be'

        self.minHeight = 28
        self.maxHeight = maxHeight
        
        self.toggleHeight = 16
        self.toggleWidth = 80
        self.animDuration = 350
        self.setStyleSheet('width: 100%')
        


        
        #----------------
        # 
        #----------------
        self.easingCurve = qt.QEasingCurve(2);

        
        #----------------
        # 
        #----------------
        self.setMinimumHeight(self.minHeight)
        


        self.title = title
        
        #----------------
        # 
        #----------------
        self.button = qt.QPushButton()
        self.button.setFixedHeight(self.toggleHeight)
        self.button.setFixedWidth(self.toggleWidth)
        self.button.setCheckable(True)
        self.button.setStyleSheet('border: none; background-color: white; margin-left: 5px;')
        self.setButtonText(True)


        
        #----------------
        # 
        #----------------
        self.frame = qt.QFrame()
        #
        # To prevent style sheet inheritance
        #
        self.frame.setObjectName('animFrame')
        self.frame.setStyleSheet('#animFrame {margin-top: 9px; border: 2px solid lightgray}')
        

        
        #----------------
        # 
        #----------------
        self.stackedLayout = qt.QStackedLayout()
        self.stackedLayout.addWidget(self.frame)
        self.stackedLayout.addWidget(self.button)
        self.stackedLayout.setStackingMode(1)



        #----------------
        # 
        #----------------        
        self.setLayout(self.stackedLayout)




        self.animations = qt.QParallelAnimationGroup()
        self.animateCallback = None
        self.collapseCallback = None
        self.expandCallback = None
        self.ContentsWidgets = None

       

        #----------------
        # 
        #----------------
        self.button.setChecked(True)
        self.button.connect('toggled(bool)', self.onToggle)
        


        
    def addToLayout(self, layout):
        """ Adds a layout to the self identifier.
        """
        self.frame.setLayout(layout)
        self.button.setChecked(True)
        



    def setButtonText(self, toggled):
        """ Modifies the arrow character of the button
            title to match the 'toggled' state.
        """
        arrowChr = ''
        if toggled:
            arrowChr = self.downArrowChar	
        else:
            arrowChr = self.rightArrowChar
        self.button.setText(arrowChr + '  ' + self.title)


        

    def setChecked(self, checked):
        """
        """
        self.onToggle(checked)


        
    def setOnCollapse(self, callback):
        """ As stated.
        """
        self.collapseCallback = callback



        
    def setOnExpand(self, callback):
        """ As stated.
        """
        self.expandCallback = callback



        
    def setOnAnimate(self, callback):
        """ As stated.
        """
        self.animateCallback = callback
        


        
    def setContentsWidgets(self, ContentsWidgets):
        """ As stated.
        """
        self.ContentsWidgets = ContentsWidgets




    def hideContentsWidgets(self):
        """ As stated.
        """
        if self.ContentsWidgets:
            for contentsWidget in self.ContentsWidgets:
                contentsWidget.hide()



            
    def showContentsWidgets(self):
        """ As stated.
        """
        if self.ContentsWidgets:
            for contentsWidget in self.ContentsWidgets:
                contentsWidget.show()
        


            
    def onAnimate(self, variant):
        """ Callback function during main animation
            sequence.
        """
        if self.animateCallback:
            self.animateCallback()
        self.setFixedHeight(variant.height())
        self.MODULE.mainLayout.update()


        

        
    def onToggle(self, toggled):
        """ Constructs an executes an animation for the widget
            once the title button is toggled.
        """

        #---------------- 
        # Clear animation
        #---------------- 
        self.animations.clear()



        #---------------- 
        # For safety...
        #----------------   
        self.setStyleSheet('width: 100%')


        
        #---------------- 
        # Modify button text to match the toggled
        # state (down arrow) 
        #----------------       
        self.setButtonText(toggled)	


            
        #---------------- 
        # Construct top-level animation.
        #----------------	
        
        #
        # Establish the animation sizes
        #	
        minSize = qt.QSize(self.geometry.width(), self.minHeight)
        maxSize = qt.QSize(self.geometry.width(), self.maxHeight)  

        #
        # Make the animation object
        #
        anim = qt.QPropertyAnimation(self, 'size')
        
        #
        # Set the duration
        #
        anim.setDuration(self.animDuration)	

        #
        # Set the easing curve
        #
        anim.setEasingCurve(self.easingCurve)

        #
        # Set the start/end values depending on
        # the toggle state.
        #
        if toggled:
            self.setMaximumHeight(self.maxHeight)
            anim.setStartValue(minSize)
            anim.setEndValue(maxSize)
        else:
            anim.setStartValue(maxSize)
            anim.setEndValue(minSize)
            self.hideContentsWidgets()

            
       
        #---------------- 
        # Connect callback during animation.
        #----------------
        anim.valueChanged.connect(self.onAnimate)



        #---------------- 
        # Connect the 'finished()' signal of the animation
        # to the finished callback...
        #----------------
        def finishedCallback():
            if toggled:
                #
                # Set the height
                #
                self.setFixedHeight(self.maxHeight)
                #
                # Show contents
                #
                self.showContentsWidgets()
                #
                # Run callbacks
                #
                if self.expandCallback:
                    self.expandCallback()
            else:                
                #
                # Set the height
                #
                self.setFixedHeight(self.minHeight)
                #
                # Run callbacks
                #
                if self.collapseCallback:
                    self.collapseCallback()
        #
        # Connect
        #
        anim.connect('finished()', finishedCallback)


        
        #---------------- 
        # Add main animation to queue.  
        # Start animation.
        #----------------       
        self.animations.addAnimation(anim)
        self.animations.start()


