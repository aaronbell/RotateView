# encoding: utf-8

###########################################################################################################
#
#
#	General Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/General%20Plugin
#
#
###########################################################################################################


#https://developer.apple.com/library/content/documentation/Cocoa/Conceptual/CocoaViewsGuide/SubclassingNSView/SubclassingNSView.html

from GlyphsApp.plugins import *
from vanilla import *
from AppKit import NSAffineTransform, NSRectFill, NSView, NSNoBorder, NSColor


## Viewer class that contains the copied glyph
#------------------------

class Viewer(NSView):
	def drawRect_(self, rect):

		glyphToRotate = self._glyphToRotate
		self._previewPath = glyphToRotate.copyDecomposedLayer()
		rotationFactor = self._rotationFactor
		windowWidth = self._windowWidth
		windowHeight = self._windowHeight

		if windowWidth > windowHeight+60:		#modification of the scaleFactor to allow it to grow with the window
			scaler = (windowHeight+60) / 300
		else:
			scaler = windowWidth / 300

		scaleFactor = 1 / (glyphToRotate.parent.parent.upm / (2 * 100.0) ) * (scaler)

		## scaling and zeroing the glyph
		#------------------------
		transform = NSAffineTransform.transform()
		transform.scaleBy_( scaleFactor )

		if glyphToRotate.bounds.origin.y < 0:
			if glyphToRotate.bounds.origin.x < 0:
				transform.translateXBy_yBy_(abs(glyphToRotate.bounds.origin.x),abs(glyphToRotate.bounds.origin.y))
			else:
				transform.translateXBy_yBy_(-glyphToRotate.bounds.origin.x,abs(glyphToRotate.bounds.origin.y))
		else:
			if glyphToRotate.bounds.origin.x < 0:
				transform.translateXBy_yBy_(abs(glyphToRotate.bounds.origin.x),-glyphToRotate.bounds.origin.y)
			else:
				transform.translateXBy_yBy_(-glyphToRotate.bounds.origin.x,-glyphToRotate.bounds.origin.y)

		self._previewPath.bezierPath.transformUsingAffineTransform_( transform )
		
		## positioning to the middle of the viewport
		#------------------------
		centering = NSAffineTransform.transform()
		centering.translateXBy_yBy_( (self._windowWidth - (glyphToRotate.bounds.size.width * scaleFactor)) / 2, (self._windowHeight - (glyphToRotate.bounds.size.height * scaleFactor))/2)
		self._previewPath.bezierPath.transformUsingAffineTransform_( centering )

		## rotational
		#------------------------

		mMatrix = NSAffineTransform.transform()
		mMatrix.translateXBy_yBy_( -windowWidth / 2, -windowHeight / 2)
		self._previewPath.bezierPath.transformUsingAffineTransform_( mMatrix )

		rMatrix = NSAffineTransform.transform()
		rMatrix.rotateByDegrees_(rotationFactor)
		self._previewPath.bezierPath.transformUsingAffineTransform_( rMatrix )
		self._currentRotation = rotationFactor


		move = NSAffineTransform.transform()
		move.translateXBy_yBy_( windowWidth / 2, windowHeight/2)
		self._previewPath.bezierPath.transformUsingAffineTransform_( move )
		
		## fill path
		#------------------------
		NSColor.blackColor().set()
		self._previewPath.bezierPath.fill()

class RotateView(GeneralPlugin):
	def settings(self):
		self.name = "RotateView"

	## creates Vanilla Window with default values
	#------------------------

	def showWindow(self, sender):
		self.windowWidth = 300
		self.windowHeight = 240

		self.initiated = False 

		self.w = Window((self.windowWidth, self.windowWidth), "RotateView", minSize=(self.windowWidth, self.windowWidth+20))
		self.w.bind("resize", self.windowResize )
		
		self.w.inactiveView = Group((0, 0, -0, -0))
		self.w.inactiveView.textBox = TextBox( (0, self.windowHeight/2, self.windowWidth, 22), text="Please select a glyph", alignment="center")	
		setattr(self.w,"box",self.w.inactiveView)

		self.w.controlBox = Group((0, -60, -0, -0))
		self.w.controlBox.slider = Slider((10, 6, -10, 23), tickMarkCount=17, callback=self.sliderCallback, value=0, minValue=-360, maxValue=360)
		self.w.controlBox.textBox = TextBox( (10, -25, -10, 22), text="0.00"+unicode(u'\u00b0'), alignment="center")	
		self.w.controlBox.slider.getNSSlider().setEnabled_(False)
		
		self.w.open()

		if Glyphs.font.currentTab: #checks if you are in the Active Tab or not and returns the right value for currentl selection
			if Glyphs.font.selectedLayers: #checks if there are any glyphs selected
				if Glyphs.font.selectedLayers[0].bezierPath or Glyphs.font.selectedLayers[0].components: #checks if the selected glyph contains anything
					self.initializeViewer()
		else:
			if Glyphs.font.selection: #same as above, but for the Font View
				if Glyphs.font.selection[0].layers[Glyphs.font.selectedFontMaster.id].bezierPath or Glyphs.font.selection[0].layers[Glyphs.font.selectedFontMaster.id].components:
					self.initializeViewer()

		
		Glyphs.addCallback( self.changeGlyph, UPDATEINTERFACE ) #will be called on ever change to the interface

	## initializes the glyph Viewer with default values
	#------------------------------

	def initializeViewer(self):
		if self.initiated == False:
			delattr(self.w, "box")
			self.w.controlBox.slider.getNSSlider().setEnabled_(True)
			self.initiated = True
			self.inactive = False

		self.viewBox = Viewer.alloc().init()

		if Glyphs.font.currentTab:
			if Glyphs.font.selectedLayers:
				if Glyphs.font.selectedLayers[0].bezierPath or Glyphs.font.selectedLayers[0].components:
					self.viewBox._glyphToRotate = Glyphs.font.selectedLayers[0]
		else:
			if Glyphs.font.selection:
				if Glyphs.font.selection[0].layers[Glyphs.font.selectedFontMaster.id].bezierPath or Glyphs.font.selection[0].layers[Glyphs.font.selectedFontMaster.id].components:
					self.viewBox._glyphToRotate = Glyphs.font.selection[0].layers[Glyphs.font.selectedFontMaster.id]

		self.viewBox._rotationFactor = 0
		self.viewBox._windowWidth = self.windowWidth
		self.viewBox._windowHeight = self.windowHeight

		self.viewBox.setFrame_( ((0, 0), (self.windowWidth, self.windowHeight)) )
		self.viewBox.setNeedsDisplay_( True )
		setattr(self.w, "box", self.scrollView()) #this is needed as we will be re-initializing the Viewer by re-adding the scrollView to the window

	## places the viewer in the scrollView
	#------------------------------

	def scrollView(self):
		bgColor = NSColor.whiteColor().set()
		s = ScrollView((0, 0, self.windowWidth, self.windowHeight), # with margins
			self.viewBox,
			hasHorizontalScroller=False,
			hasVerticalScroller=False,
			backgroundColor=bgColor,
			)
		s._nsObject.setBorderType_(NSNoBorder)
		return s

	## initializes the glyph Viewer
	#------------------------------
	def sliderCallback(self, sender):

		currentValue = '{:.2f}'.format(sender.get())
		self.w.controlBox.textBox.set(str(currentValue)+unicode(u'\u00b0'))

		self.viewBox._rotationFactor = float(currentValue)

		delattr(self.w, "box")
		setattr(self.w, "box", self.scrollView()) #here we remove the scrollView, then re-add it. This forces the redraw. 

	## on Glyph Change, update the viewer
	#------------------------------

	def changeGlyph(self, sender):

		if self.initiated == False: #if the viewer hasn't been inialized, this will do that process instead of the change glyph functionality
			if Glyphs.font.currentTab:
				if Glyphs.font.selectedLayers:
					if Glyphs.font.selectedLayers[0].bezierPath or Glyphs.font.selectedLayers[0].components:
						self.initializeViewer()
			else:
				if Glyphs.font.selection:
					if Glyphs.font.selection[0].layers[Glyphs.font.selectedFontMaster.id].bezierPath or Glyphs.font.selection[0].layers[Glyphs.font.selectedFontMaster.id].components:
						self.initializeViewer()
		else:
			if Glyphs.font.currentTab: #the rule we need to use for identifying the currently selected glyph differs between the Font View and Active View
				if Glyphs.font.selectedLayers:
					if Glyphs.font.selectedLayers[0].bezierPath or Glyphs.font.selectedLayers[0].components:
						self.viewBox._glyphToRotate = Glyphs.font.selectedLayers[0]
						self.inactive = False
						self.w.controlBox.slider.getNSSlider().setEnabled_(True) # should a glyph not be selected, or is empty, the window switches into an inactive mode
					else:
						self.inactive = True
						self.w.controlBox.slider.getNSSlider().setEnabled_(False)
				else:
					self.inactive = True
					self.w.controlBox.slider.getNSSlider().setEnabled_(False)
			else:
				if Glyphs.font.selection:
					if Glyphs.font.selection[0].layers[Glyphs.font.selectedFontMaster.id].bezierPath or Glyphs.font.selection[0].layers[Glyphs.font.selectedFontMaster.id].components:
						self.viewBox._glyphToRotate = Glyphs.font.selection[0].layers[Glyphs.font.selectedFontMaster.id]
						self.inactive = False
						self.w.controlBox.slider.getNSSlider().setEnabled_(True)
					else:
						self.inactive = True
						self.w.controlBox.slider.getNSSlider().setEnabled_(False)
				else:
					self.inactive = True
					self.w.controlBox.slider.getNSSlider().setEnabled_(False)

			delattr(self.w, "box")

			if self.inactive == True:	
				self.w.inactiveView.textBox.set("No glyph to display")
				setattr(self.w,"box",self.w.inactiveView)
			else:
				setattr(self.w, "box", self.scrollView())



	def windowResize(self, sender):
		self.windowWidth = sender.getPosSize()[2]
		self.windowHeight = sender.getPosSize()[3]-60 #leaves room for the controls

		self.viewBox._windowWidth = self.windowWidth
		self.viewBox._windowHeight = self.windowHeight
		self.viewBox.setFrame_( ((0, 0), (self.windowWidth, self.windowHeight)) )

		delattr(self.w, "box")

		if self.inactive == True:	
			setattr(self.w,"box",self.w.inactiveView)
		else:
			setattr(self.w, "box", self.scrollView())


	def start(self):
		newMenuItem = NSMenuItem(self.name, self.showWindow)
		Glyphs.menu[WINDOW_MENU].append(newMenuItem)

	def __del__(self):
		Glyphs.removeCallback( self.changeGlyph, UPDATEINTERFACE )

	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__