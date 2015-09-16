from Tkinter import *
from PIL import Image, ImageTk
import glob
import tkFont
import sys
import pprint
import os
from random import randint
from pygame import mixer

class JoypadScreen:
        
        
    image_infoscreen            = 'resources/bg_pre.jpg'
    image_finalscreen           = 'resources/bg_post.jpg' 
	
    def __init__(self, joypadui):
        self.joypadui = joypadui
		
		
    def loadInfoScreen(self):
        print "Showing info screen. Press 1 to start."
        
        joypadui = self.joypadui
        
        self.joypadui.status=self.joypadui.STATUS_INFOSCREEN()
        self.joypadui.resetCountdownTimer(0)
        
        self.joypadui.imageBG = Image.open( self.image_infoscreen )
        self.joypadui.photoBG = ImageTk.PhotoImage(self.joypadui.imageBG)
        self.joypadui.c.itemconfig(self.joypadui.bg, image= self.joypadui.photoBG)

        hideElements = ['imageGameA','textHeadingA','imageGameB','textHeadingB','textTeamAscore','textTeamBscore','textTimer']

        for guiElement in hideElements:
            if (hasattr(self.joypadui,guiElement)):
                self.joypadui.c.itemconfig(getattr(self.joypadui,guiElement), state=HIDDEN)
                
                
    def loadFinalScreen(self):
        print "Showing final screen"
        
        joypadui = self.joypadui
        
        self.joypadui.status=self.joypadui.STATUS_INFOSCREEN()
        self.joypadui.resetCountdownTimer(0)
        
        self.joypadui.imageBG = Image.open( self.image_finalscreen )
        self.joypadui.photoBG = ImageTk.PhotoImage(self.joypadui.imageBG)
        self.joypadui.c.itemconfig(self.joypadui.bg, image= self.joypadui.photoBG)

        hideElements = ['imageGameA','textHeadingA','imageGameB','textHeadingB','textTeamAscore','textTeamBscore','textTimer']

        for guiElement in hideElements:
            if (hasattr(self.joypadui,guiElement)):
                self.joypadui.c.itemconfig(getattr(self.joypadui,guiElement), state=HIDDEN)
