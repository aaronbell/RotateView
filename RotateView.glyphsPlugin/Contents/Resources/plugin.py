# encoding: utf-8
from __future__ import division, print_function, unicode_literals

###########################################################################################################
#
#
#  General Plugin
#
#  Read the docs:
#  https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/General%20Plugin
#
#
###########################################################################################################


# https://developer.apple.com/library/content/documentation/Cocoa/Conceptual/CocoaViewsGuide/SubclassingNSView/SubclassingNSView.html

import objc
from GlyphsApp import Glyphs, UPDATEINTERFACE, WINDOW_MENU, NSMenuItem
from GlyphsApp.plugins import GeneralPlugin
from vanilla import VanillaBaseObject, Group, Slider, TextBox, Window
from AppKit import NSAffineTransform, NSView, NSColor, NSBezierPath, NSFullSizeContentViewWindowMask
from Foundation import NSWidth, NSHeight, NSMidX, NSMidY
import traceback

## Viewer class that contains the copied glyph
# ------------------------


class RotatePreviewView(NSView):

	def drawRect_(self, rect):

		NSColor.whiteColor().set()
		NSBezierPath.fillRect_(rect)

		font = Glyphs.font
		if font is None:
			return

		selectedLayers = font.selectedLayers
		if not selectedLayers:
			return

		glyphToRotate = None
		try:
			glyphToRotate = selectedLayers[0]
		except:
			print(traceback.format_exc())

		if glyphToRotate is None:
			return

		try:
			previewPath = glyphToRotate.completeBezierPath

			rotationFactor = self.wrapper._rotationFactor
			Width = NSWidth(self.frame())
			Height = NSHeight(self.frame())

			scaleFactor = 0.666666 / (glyphToRotate.parent.parent.upm / min(Width, Height))

			## scaling and zeroing the glyph
			# ------------------------
			transform = NSAffineTransform.transform()
			transform.scaleBy_(scaleFactor)
			bounds = glyphToRotate.bounds
			transform.translateXBy_yBy_(-NSMidX(bounds), -NSMidY(bounds))
			previewPath.transformUsingAffineTransform_(transform)

			## rotation
			# ------------------------
			transform = NSAffineTransform.transform()
			transform.rotateByDegrees_(rotationFactor)
			previewPath.transformUsingAffineTransform_(transform)

			## positioning to the middle of the viewport
			# ------------------------
			transform = NSAffineTransform.transform()
			transform.translateXBy_yBy_(Width / 2, Height / 2 - 8)
			previewPath.transformUsingAffineTransform_(transform)

			## fill path
			# ------------------------
			NSColor.blackColor().set()
			previewPath.fill()

		except:
			print(traceback.format_exc())


class RoatatePreview(VanillaBaseObject):
	nsGlyphPreviewClass = RotatePreviewView

	@objc.python_method
	def __init__(self, posSize):
		self._rotationFactor = 0
		self._setupView(self.nsGlyphPreviewClass, posSize)
		self._nsObject.wrapper = self

	@objc.python_method
	def redraw(self):
		self._nsObject.setNeedsDisplay_(True)


class RotateView(GeneralPlugin):

	@objc.python_method
	def settings(self):
		self.name = "Rotate View"

	@objc.python_method
	def start(self):
		if Glyphs.buildNumber >= 3320:
			from GlyphsApp.UI import MenuItem
			newMenuItem = MenuItem(self.name, action=self.showWindow_, target=self)
		elif Glyphs.versionNumber >= 3.3:
			newMenuItem = NSMenuItem(self.name, callback=self.showWindow_, target=self)
		else:
			newMenuItem = NSMenuItem(self.name, self.showWindow_)
		Glyphs.menu[WINDOW_MENU].append(newMenuItem)

	## creates Vanilla Window
	# ------------------------

	def showWindow_(self, sender):
		try:
			self.windowWidth = 300
			self.windowHeight = 240

			self.w = Window((self.windowWidth, self.windowWidth), "Rotate View", minSize=(self.windowWidth, self.windowWidth))
			window = self.w.getNSWindow()
			window.setStyleMask_(window.styleMask() | NSFullSizeContentViewWindowMask)
			try:  # only available in 10.10
				window.setTitlebarAppearsTransparent_(True)
			except:
				pass
			# window.toolbar = nil;
			window.setMovableByWindowBackground_(True)

			self.w.bind("close", self.closeWindow)
			self.w.Preview = RoatatePreview((0, 0, -0, -28))
			self.w.controlBox = Group((0, -28, -0, -0))
			self.w.controlBox.slider = Slider((10, 2, -55, 28), tickMarkCount=17, callback=self.sliderCallback, value=0, minValue=-360, maxValue=360)
			self.w.controlBox.textBox = TextBox((-55, -23, -5, -3), text="0°", alignment="center")
			self.w.controlBox.slider.getNSSlider().setEnabled_(False)

			self.w.open()
			self.changeGlyph_(None)
			Glyphs.addCallback(self.changeGlyph_, UPDATEINTERFACE)  # will be called on ever change to the interface
		except:
			print(traceback.format_exc())

	@objc.python_method
	def closeWindow(self, sender):
		Glyphs.removeCallback(self.changeGlyph_, UPDATEINTERFACE)

	## slider callback
	# ------------------------------

	@objc.python_method
	def sliderCallback(self, sender):
		value = sender.get()
		currentValue = '{:.0f}°'.format(value)
		self.w.controlBox.textBox.set(currentValue)
		self.w.Preview._rotationFactor = float(value)
		self.w.Preview.redraw()

	## on Glyph Change, update the viewer
	# ------------------------------

	def changeGlyph_(self, sender):
		self.w.controlBox.slider.getNSSlider().setEnabled_(Glyphs.font and Glyphs.font.selectedLayers)
		self.w.Preview.redraw()

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
