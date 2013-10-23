from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil



comment = """
XnatAnimatedCollapsible is a collapsible widget that animates
itself when the user toggles it.  Much like other QT widgets, 
the user can set a layout (where the contents) reside to allow
for the animation.  It should be noted that the user should 
provide the specific widgets also, so they can be hidden/shown
on the various toggle states (setContentsWidgets).

TODO:        
"""



class XnatAnimatedCollapsible(qt.QFrame):
    """ Descriptor above.
    """
    
    def __init__(self, MODULE, title, maxHeight = 250):
        """ Init function.
        """
        
        #--------------------
        # Call parent init.
        #--------------------
        qt.QFrame.__init__(self)


        
        #--------------------
        # We hide the module first because
        # it creates a flikering on loadup
        #--------------------
        self.hide()


        
        #--------------------
        # Set internal variables.
        #--------------------        
        self.MODULE = MODULE
        self.rightArrowChar = u'\u25b8'
        self.downArrowChar = u'\u25be'
        #
        # Size
        #
        self.minHeight = 28
        self.maxHeight = maxHeight
        self.toggleHeight = 16
        self.toggleWidth = 80
        self.setStyleSheet('width: 100%')
        #
        # Animation duration
        #
        self.animDuration = 350
        

        
        #----------------
        # Set the easing curve.  See:
        # http://harmattan-dev.nokia.com/docs/library/html/qt4/qeasingcurve.html
        # for more options.
        #----------------
        self.easingCurve = qt.QEasingCurve(2);


        
        #----------------
        # Set the minimum hieght
        #----------------
        self.setMinimumHeight(self.minHeight)
        

        
        #----------------
        # set  the Title
        #----------------       
        self.title = title


        
        #----------------
        # Make button
        #----------------
        self.button = qt.QPushButton(self)
        self.button.setFixedHeight(self.toggleHeight)
        self.button.setFixedWidth(self.toggleWidth)
        self.button.setCheckable(True)
        self.button.setStyleSheet('border: none; background-color: white; margin-left: 5px;')
        self.setButtonText(True)
     

        
        #----------------
        # Make the internal 'frame' and set the style
        # accordingly.
        #----------------
        self.frame = qt.QFrame(self)
        #
        # To prevent style sheet inheritance
        #
        self.frame.setObjectName('animFrame')
        self.frame.setStyleSheet('#animFrame {margin-top: 9px; border: 2px solid lightgray}')

        
        
        #----------------
        # Stack the button on top of the frame via a 
        # QStackedLayout
        #----------------
        self.stackedLayout = qt.QStackedLayout()
        self.stackedLayout.addWidget(self.frame)
        self.stackedLayout.addWidget(self.button)
        #
        # To make sure the button is on top.
        #
        self.stackedLayout.setCurrentIndex(1)
        self.stackedLayout.setStackingMode(1)



        #----------------
        # Set the sayout
        #----------------        
        self.setLayout(self.stackedLayout)



        #----------------
        # Init the animation group and callbacks.
        #----------------  
        self.animations = qt.QParallelAnimationGroup()
        self.onAnimate = None
        self.onCollapse = None
        self.onExpand = None
        self.ContentsWidgets = None

       

        #----------------
        # Set the default states after creation.
        #----------------
        self.button.setChecked(True)
        self.button.connect('toggled(bool)', self.setChecked)
        self.toggled = True
        


        
    def setAnimationDuration(self, duration):
        """ As stated.
        """
        self.animDuration = duration;


        
        
    def addToLayout(self, layout):
        """ Adds a layout to the internal frame
            which will be the contents of the widget.
        """
        self.frame.setLayout(layout)


        
        #----------------
        # Temporarily turn off the animation
        # when adding contents.
        #----------------
        tempDuration = self.animDuration
        self.animDuration = 0
        self.setChecked(True)
        self.animDuration = tempDuration
        



    def setButtonText(self, toggled):
        """ Modifies the arrow character of the button
            title to match the 'toggled' state and also
            sets the following text.
        """
        arrowChr = self.downArrowChar if toggled else self.rightArrowChar
        self.button.setText(arrowChr + '  ' + self.title)



        
    def setOnCollapse(self, callback):
        """ As stated.
        """
        self.onCollapse = callback



        
    def setOnExpand(self, callback):
        """ As stated.
        """
        self.onExpand = callback



        
    def setOnAnimate(self, callback):
        """ As stated.
        """
        self.onAnimate = callback
        


        
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
        


            
    def onAnimateMain(self, variant):
        """ Function during main animation
            sequence -- runs the 'onAnimate'
            callback.
        """
        if self.onAnimate:
            self.onAnimate()
        self.setFixedHeight(variant.height())



        
    def onAnimationFinished(self):
        """ Callback function when the animation
            finishes.
        """


        #---------------- 
        # Call the animate function.
        #---------------- 
        self.onAnimateMain(qt.QSize(self.geometry.width(), self.geometry.height()))


        
        #---------------- 
        # If the widget is toggled...
        #---------------- 
        if self.toggled:
            #
            # Set the height
            #
            self.setFixedHeight(self.maxHeight)
            #
            # Show contents
            #
            self.showContentsWidgets()
            #
            # Run callbacks, animate and end.
            #
            if self.onExpand:
                self.onExpand()

                

        #---------------- 
        # Otherwise...
        #---------------- 
        else:                
            #
            # Set the height
            #
            self.setFixedHeight(self.minHeight)
            #
            # Run callbacks
            #
            if self.onCollapse:
                self.onCollapse()


                

        
    def setChecked(self, toggled, animDuration = None):
        """ Constructs an executes an animation for the widget
            once the title button is toggled.
        """

        #---------------- 
        # Track whether collapsible was toggled.
        #---------------- 
        self.toggled = toggled


        
        #---------------- 
        # Define the animation duration.
        #----------------        
        if not animDuration: 
            animDuration = self.animDuration


            
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
        anim.setDuration(animDuration)	

        #
        # Set the easing curve
        #
        anim.setEasingCurve(self.easingCurve)

        #
        # Set the start/end values depending on
        # the toggle state.
        #
        if self.toggled:
            self.setMaximumHeight(self.maxHeight)
            anim.setStartValue(minSize)
            anim.setEndValue(maxSize)
        else:
            anim.setStartValue(maxSize)
            anim.setEndValue(minSize)
            self.hideContentsWidgets()

            
       
        #---------------- 
        # Set callback during animation.
        #----------------
        anim.valueChanged.connect(self.onAnimateMain)



        #---------------- 
        # Connect the 'finished()' signal of the animation
        # to the finished callback...
        #----------------
        anim.connect('finished()', self.onAnimationFinished)


        
        #---------------- 
        # Add main animation to queue and  
        # start animation.
        #----------------       
        self.animations.addAnimation(anim)
        self.animations.start()


