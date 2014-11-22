from Tkinter import *
from PIL import Image, ImageTk
import glob
import tkFont
import sys

class Joypadui:
    'UI controller for joypad voting system'
    
    # count down timer - change this value if you want
    timerSeconds = 300
    # how long to spend on the vote result screen
    timeOnVoteResults = 120

    # init using the root Tk() instance and the Joypadio library
    def __init__(self, root, io):
        self.root = root
        self.io = io
        self.timeRemaining  = self.timerSeconds
        self.canvas_height  = root.winfo_screenheight() - 40 
        self.canvas_width   = root.winfo_screenwidth()
        self.font_header    = tkFont.Font(family="Helvetica", size=100, weight="bold")
        self.font_header2   = tkFont.Font(family="Helvetica", size=50, weight="bold")
        #vote control
        self.currentVoteId  = 1
        self.voteConfig     = []
   
    # find files from the filesystem that will configure the vote system
    # file structure should be as follows:
    #
    # resourecs/1a.gif/jpg      - left picture
    # resoucres/1b.gif/jpg      - right picture
    # resoucres/1a.txt          - left game name (title)
    # resources/1b.txt          - right game name (title)
    # resources/2..
    # etc
    #
    def initFilesystem(self):
        for i in xrange(1,16,1):
            voteEntity = {
                'index'         : i,
                'mediaTypeA'    : 'jpg',
                'mediaTypeB'    : 'jpg',
                'headingA'      : 'Game A',
                'headingB'      : 'Game B',
            }
            # look for files on filesystem
            # add to self.voteConfig
            
            

    def initGui(self):
        self.c = Canvas(self.root, width=self.canvas_width, height=self.canvas_height)

        # make everything centered, that way we can deal with different resolutions easier insetad of
        # anchoring everything to the top left
        self.imageBG = Image.open( "resources/bg.jpg")
        self.photoBG = ImageTk.PhotoImage(self.imageBG)
        self.bg = self.c.create_image(self.canvas_width/2,self.canvas_height/2,image=self.photoBG)

        self.textHeadingA = self.c.create_text(self.canvas_width/4, 100, text="Game A", font=self.font_header2, fill="white")
        self.textHeadingB = self.c.create_text(self.canvas_width/4*3, 100, text="Game B", font=self.font_header2, fill="white")
        self.textTeamAscore = self.c.create_text(self.canvas_width/4, self.canvas_height - 150, text="0", font=self.font_header, fill="white")
        self.textTeamBscore = self.c.create_text(self.canvas_width/4*3, self.canvas_height - 150, text="0", font=self.font_header, fill="white")

        self.textTimer = self.c.create_text(self.canvas_width/2, 100, text="COUNTDOWN", font=self.font_header, fill="green")


        #game A image
        self.gif1 = anim_gif('resources/1.gif')
        self.imageGame1 = self.c.create_image(self.canvas_width/4,self.canvas_height/2,image=None)

        #game B image
        self.gif2 = anim_gif('resources/2.gif')
        self.imageGame2 = self.c.create_image(self.canvas_width/4*3,self.canvas_height/2,image=None)
       
        # start the GUI update routines
        self.updateUI()
        self.countdownTimer()
        self.animate1()
        self.animate2()

        self.c.pack()

    def countdownTimer(self):
        if (self.timeRemaining <= 0):
            self.timerReached();
        else:
            self.timeRemaining = self.timeRemaining - 1;
            self.root.after(1000,self.countdownTimer);

    def resetCountdownTimer(self):
        self.timeRemaining = self.timerSeconds

    def timerReached(self):
        'something'
        # dislpay the voting results screen, plus a countdown to the next vote session

    def updateUI(self):
        'update the UI to display scores every 200ms'
        self.c.itemconfig(self.textTeamAscore, text = self.io.scoreA)
        self.c.itemconfig(self.textTeamBscore, text = self.io.scoreB)
        self.c.itemconfig(self.textTimer, text= self.timeRemaining);
        self.root.after(200,self.updateUI)
        
    def animate1(self):
        self.c.itemconfig(self.imageGame1, image= self.gif1['frames'][self.gif1['loc']])
        self.gif1['loc'] += 1
        if self.gif1['loc'] == self.gif1['len']:
            self.gif1['loc'] = 0
        self.root.after(self.gif1["delays"][self.gif1['loc']] - 20, self.animate1)
        
    def animate2(self):
        self.c.itemconfig(self.imageGame2, image= self.gif2['frames'][self.gif2['loc']])
        self.gif2['loc'] += 1
        if self.gif2['loc'] == self.gif2['len']:
            self.gif2['loc'] = 0
        self.root.after(self.gif2["delays"][self.gif2['loc']] - 20, self.animate2)

        
#
# other utility functinos
#

# anim_gif
# modified code from http://stackoverflow.com/questions/17223854/displaying-animated-gifs-in-tkinter-using-pil
def anim_gif(name):
    
    im = Image.open(name)
    gif = { 'frames': [],
            'delays': [],
            'loc' : 0,
            'len' : 0 }
    pics = []
    try:
        while True:
            pics.append(im.copy())
            im.seek(len(pics))
    except EOFError: pass
    gif['frames'] = [ImageTk.PhotoImage(frame.convert('RGBA')) for frame in pics];
    # each frame can have a different animatino duration as well
    try:
        gif['delays'] = [frame.info['duration'] for frame in pics];
    except:
        gif['delays'] = []  
    
    gif['len'] = len(gif['frames'])
    return gif
