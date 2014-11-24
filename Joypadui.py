from Tkinter import *
from PIL import Image, ImageTk
import glob
import tkFont
import sys
import pprint

class Joypadui:
    'UI controller for joypad voting system'
    
    # count down timer - change this value if you want
    timerSeconds = 10
    # how long to spend on the vote result screen
    timeOnVoteResults = 120

    # internal status, 0 = initialising, 1 = running a vote, 2 = displaying vote results,
    #   3 = sudden death mode (next vote wins!)
    # animations only run in state 1 or 2
    status = 0    

    # init using the root Tk() instance and the Joypadio library
    def __init__(self, root, io):
        print 'JoypadUI v1.0 initialising'
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
        self.initFilesystem()
   
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
        print 'Looking for vote files ...'
        for i in xrange(1,16,1):
            voteEntity = {
                'voteId'         : i,
                'media_a'       : None,
                'media_b'       : None,
                'heading_a'      : 'Game A',
                'heading_b'      : 'Game B',
            }
            # look for files on filesystem
            files = glob.glob("resources/" + str(i) + "*.*")
            
            for team in ['a','b']:
                if ("resources/" + str(i) + team + '.txt') in files:
                    tmp = open("resources/" + str(i) + team + ".txt")
                    voteEntity['heading_' + team] = tmp.read()
                if ("resources/" + str(i) + team +'.gif') in files:
                    voteEntity['media_'+team] = "resources/" + str(i) + team +".gif"
                if ("resources/" + str(i) + team +'.jpg') in files:
                    voteEntity['media_'+team] = "resources/" + str(i) + team + ".jpg"   
                if ("resources/" + str(i) + team +'.mp4') in files:
                    voteEntity['media_'+team] = "resources/" + str(i) + team + ".mp4"
                    
            if ((voteEntity['media_a']) and (voteEntity['media_b'])): 
                # add to self.voteConfig
                self.voteConfig.append(voteEntity)
        print "Vote configured as follows:"
        pp = pprint.PrettyPrinter(indent=2);
        pp.pprint(self.voteConfig)

    def initGui(self):
        print "Initialising GUI ..."
        self.c = Canvas(self.root, width=self.canvas_width, height=self.canvas_height)

        # make everything centered, that way we can deal with different resolutions easier insetad of
        # anchoring everything to the top left
        self.imageBG = Image.open( "resources/bg.jpg")
        self.photoBG = ImageTk.PhotoImage(self.imageBG)

        #self.imageBG_win_a = Image.open( "resources/bg_win_a.jpg")
        #self.photoBG_win_a = ImageTk.PhotoImage(self.imageBG_win_a)
        #self.imageBG_win_b = Image.open( "resources/bg_win_b.jpg")
        #self.photoBG_win_b= ImageTk.PhotoImage(self.imageBG_win_b)
        
        self.bg = self.c.create_image(self.canvas_width/2,self.canvas_height/2,image=self.photoBG)

        self.textHeadingA = self.c.create_text(self.canvas_width/4, 100, text="Game A", font=self.font_header2, fill="white")
        self.textHeadingB = self.c.create_text(self.canvas_width/4*3, 100, text="Game B", font=self.font_header2, fill="white")
        self.textTeamAscore = self.c.create_text(self.canvas_width/4, self.canvas_height - 150, text="0", font=self.font_header, fill="white")
        self.textTeamBscore = self.c.create_text(self.canvas_width/4*3, self.canvas_height - 150, text="0", font=self.font_header, fill="white")

        self.textTimer = self.c.create_text(self.canvas_width/2, 100, text="COUNTDOWN", font=self.font_header, fill="green")

        self.status = 1;
        self.loadVote(self.currentVoteId - 1)

        # start the GUI update routines
        self.updateUI()
        self.countdownTimer()      

        self.c.pack()
        
    def loadVote(self, index):

        print "Loading vote (index "+str(index)+")"

        # repaint background (we could've come from a winning / sudden death screen)
        self.c.itemconfig(self.bg, image= self.photoBG)

        # gif support
        if self.voteConfig[index]['media_a'].endswith('.gif'):
            if (hasattr(self,'gif1')):
                del self.gif1
            self.gif1 = anim_gif(self.voteConfig[index]['media_a'])
            if (not hasattr(self,'imageGame1')):
                self.imageGame1 = self.c.create_image(self.canvas_width/4,self.canvas_height/2,image=None)
            self.animate1()
               
        if self.voteConfig[index]['media_b'].endswith('.gif'):
            if (hasattr(self,'gif2')):
                del self.gif2
            self.gif2 = anim_gif(self.voteConfig[index]['media_b'])
            if (not hasattr(self,'imageGame2')):
                self.imageGame2 = self.c.create_image(self.canvas_width/4*3,self.canvas_height/2,image=None)
            self.animate2()

        #jpg support
        if self.voteConfig[index]['media_a'].endswith('.jpg'):
            self.photo_a = Image.open(self.voteConfig[index]['media_a'])
            self.photo_aa = ImageTk.PhotoImage(self.photo_a);
            if (not hasattr(self,'imageGame1')):
                self.imageGame1 = self.c.create_image(self.canvas_width/4,self.canvas_height/2,image=self.photo_aa)
            else:
                self.c.itemconfig(self.imageGame1, image=self.photo_aa)
            
        if self.voteConfig[index]['media_b'].endswith('.jpg'):
            self.photo_b = Image.open(self.voteConfig[index]['media_b'])
            self.photo_bb = ImageTk.PhotoImage(self.photo_b)
            if (not hasattr(self,'imageGame2')):
                self.imageGame2 = self.c.create_image(self.canvas_width/4*3,self.canvas_height/2,image=self.photo_bb)
            else:
                self.c.itemconfig(self.imageGame2, image=self.photo_bb)

    def countdownTimer(self):
        if (self.timeRemaining <= 0):
            self.timerReached();
        else:
            self.timeRemaining = self.timeRemaining - 1;
            self.root.after(1000,self.countdownTimer);

    def resetCountdownTimer(self):
        self.timeRemaining = self.timerSeconds

    def timerReached(self):
        if (self.status==1):
            print '=========================='
            print ' Timer reached for vote ' + str(self.currentVoteId);
            print '=========================='
            print 'Team A: '+str(self.io.scoreA)+' votes for ' + self.voteConfig[self.currentVoteId-1]['heading_a'];
            print 'Team B: '+str(self.io.scoreB)+' votes for ' + self.voteConfig[self.currentVoteId-1]['heading_b'];

        if (self.status==1 or self.status==3):
                
            if (self.io.scoreA == self.io.scoreB):
                if (self.status != 3):
                    print "Entering SUDDEN DEATH mode"
                self.suddenDeathMode()
            elif (self.io.scoreA > self.io.scoreB):
                print " ** Team A wins by " + str(self.io.scoreA-self.io.scoreB) +" votes **";
                print " ** "+ self.voteConfig[self.currentVoteId-1]['heading_a']+ " **";
                self.announceWinner('a');
            else:
                print " ** Team B wins by " + str(self.io.scoreB-self.io.scoreA) +" votes **";
                print " ** "+ self.voteConfig[self.currentVoteId-1]['heading_b']+ " **";
                self.announceWinner('b')

        if (self.status == 2):
            self.resetAndLoadNextVote()


    def suddenDeathMode(self):
        self.status = 3
        self.root.after(100,self.timerReached);

    def announceWinner(self,team):
        'something'
        self.status = 2
        self.timerReached();

    def resetVote(self):
        self.status = 1
        self.resetCountdownTimer()
        self.io.scoreA = 0
        self.io.scoreB = 0

    def resetAndLoadNextVote(self):
        self.resetVote()
        self.currentVoteId += 1
        self.loadVote(self.currentVoteId - 1)
        self.countdownTimer()

    def updateUI(self):
        'update the UI to display scores every 200ms'
        # vote is running
        if (self.status == 1):
            self.c.itemconfig(self.textTeamAscore, text = self.io.scoreA)
            self.c.itemconfig(self.textTeamBscore, text = self.io.scoreB)
            self.c.itemconfig(self.textTimer, text= self.timeRemaining, fill='green');
        # sudden death mode
        if (self.status == 3):
                self.c.itemconfig(self.textTimer, text= 'SUDDEN DEATH', fill='red');
        
        self.root.after(200,self.updateUI)
        
    def animate1(self):
        
        self.c.itemconfig(self.imageGame1, image= self.gif1['frames'][self.gif1['loc']])
        self.gif1['loc'] += 1
        if self.gif1['loc'] == self.gif1['len']:
            self.gif1['loc'] = 0
        if (self.status in [1,2,3]):
            self.root.after(self.gif1["delays"][self.gif1['loc']] - 10, self.animate1)
        
    def animate2(self):
        
        self.c.itemconfig(self.imageGame2, image= self.gif2['frames'][self.gif2['loc']])
        self.gif2['loc'] += 1
        if self.gif2['loc'] == self.gif2['len']:
            self.gif2['loc'] = 0
        if (self.status in [1,2,3]):
            self.root.after(self.gif2["delays"][self.gif2['loc']] - 10, self.animate2)

        
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
