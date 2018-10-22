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

from GlyphsApp import *
from GlyphsApp.plugins import *
import objc
from vanilla import VanillaBaseObject
from AppKit import NSAffineTransform, NSRectFill, NSView, NSNoBorder, NSColor, NSBezierPath
from Foundation import NSWidth, NSHeight, NSMidX, NSMidY
import traceback

## Viewer class that contains the copied glyph
#------------------------

class RoatatePreviewView(NSView):
	def drawRect_(self, rect):
		
		NSColor.whiteColor().set()
		NSBezierPath.fillRect_(rect)
		
		glyphToRotate = None
		try:
			glyphToRotate = Glyphs.font.selectedLayers[0]
		except:
			print traceback.format_exc()
		
		if glyphToRotate is None:
			return
		
		try:
			previewPath = glyphToRotate.completeBezierPath
		
			rotationFactor = self.wrapper._rotationFactor
			Width = NSWidth(self.frame())
			Height = NSHeight(self.frame())
			
			scaleFactor = 0.666666 / (glyphToRotate.parent.parent.upm / min(Width, Height))
			
			## scaling and zeroing the glyph
			#------------------------
			transform = NSAffineTransform.transform()
			transform.scaleBy_( scaleFactor )
			bounds = glyphToRotate.bounds
			transform.translateXBy_yBy_(-NSMidX(bounds),-NSMidY(bounds))
			previewPath.transformUsingAffineTransform_( transform )
			
			## rotation
			#------------------------
			transform = NSAffineTransform.transform()
			transform.rotateByDegrees_(rotationFactor)
			previewPath.transformUsingAffineTransform_( transform )
			
			## positioning to the middle of the viewport
			#------------------------
			transform = NSAffineTransform.transform()
			transform.translateXBy_yBy_( Width / 2, Height / 2)
			previewPath.transformUsingAffineTransform_(transform)
	
			## fill path
			#------------------------
			NSColor.blackColor().set()
			previewPath.fill()
		
		except:
			print traceback.format_exc()

class RoatatePreview(VanillaBaseObject):
	nsGlyphPreviewClass = RoatatePreviewView
	def __init__(self, posSize):
		self._rotationFactor = 0
		self._setupView(self.nsGlyphPreviewClass, posSize)
		self._nsObject.wrapper = self
	def redraw(self):
		self._nsObject.setNeedsDisplay_(True)

class RotateView(GeneralPlugin):
	def settings(self):
		self.name = "RotateView"

	## creates Vanilla Window
	#------------------------

	def showWindow(self, sender):
		try:
			from vanilla import Group, Slider, TextBox, Window
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
