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
import traceback

## Viewer class that contains the copied glyph
#------------------------

class RoatatePreviewView(NSView):
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
		bounds = glyphToRotate.bounds
		if bounds.origin.y < 0:
			if bounds.origin.x < 0:
				transform.translateXBy_yBy_(abs(bounds.origin.x),abs(bounds.origin.y))
			else:
				transform.translateXBy_yBy_(-bounds.origin.x,abs(bounds.origin.y))
		else:
			if bounds.origin.x < 0:
				transform.translateXBy_yBy_(abs(bounds.origin.x),-bounds.origin.y)
			else:
				transform.translateXBy_yBy_(-bounds.origin.x,-bounds.origin.y)

		self._previewPath.bezierPath.transformUsingAffineTransform_( transform )
		
		## positioning to the middle of the viewport
		#------------------------
		centering = NSAffineTransform.transform()
		centering.translateXBy_yBy_( (self._windowWidth - (bounds.size.width * scaleFactor)) / 2, (self._windowHeight - (bounds.size.height * scaleFactor))/2)
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

class RoatatePreview(VanillaBaseObject):
	nsGlyphPreviewClass = RoatatePreviewView
	def __init__(self, posSize):
		self._rotationFactor = 0
		self._setupView(self.nsGlyphPreviewClass, posSize)
		self._nsObject.wrapper = self
	def redraw(self):
		self._nsObject.setNeedsDisplay_(YES)

class RotateView(GeneralPlugin):
	def settings(self):
		self.name = "RotateView"

	## creates Vanilla Window
	#------------------------

	def showWindow(self, sender):
		try:
			self.windowWidth = 300
			self.windowHeight = 240
			
			self.w = Window((self.windowWidth, self.windowWidth), "RotateView", minSize=(self.windowWidth, self.windowWidth+20))
			
			self.w.Preview = RoatatePreview((0, 0, -0, -60))
			self.w.controlBox = Group((0, -60, -0, -0))
			self.w.controlBox.slider = Slider((10, 6, -10, 23), tickMarkCount=17, callback=self.sliderCallback, value=0, minValue=-360, maxValue=360)
			self.w.controlBox.textBox = TextBox( (10, -25, -10, 22), text="0.00"+unicode(u'\u00b0'), alignment="center")
			self.w.controlBox.slider.getNSSlider().setEnabled_(False)
		
			self.w.open()
			self.changeGlyph(None)
			Glyphs.addCallback( self.changeGlyph, UPDATEINTERFACE ) #will be called on ever change to the interface
		except:
			print traceback.format_exc()


	## slider callback
	#------------------------------

	def sliderCallback(self, sender):
		currentValue = '{:.2f}'.format(sender.get())
		self.w.controlBox.textBox.set(str(currentValue)+unicode(u'\u00b0'))
		self.w.Preview._rotationFactor = float(currentValue)
		self.w.Preview.redraw()


	## on Glyph Change, update the viewer
	#------------------------------
	
	def changeGlyph(self, sender):
		self.w.controlBox.slider.getNSSlider().setEnabled_(len(Glyphs.font.selectedLayers) > 0)
		self.w.Preview.redraw()

	def start(self):
		newMenuItem = NSMenuItem(self.name, self.showWindow)
		Glyphs.menu[WINDOW_MENU].append(newMenuItem)

	def __del__(self):
		Glyphs.removeCallback( self.changeGlyph, UPDATEINTERFACE )

	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__