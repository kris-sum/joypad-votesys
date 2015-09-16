from Tkinter import *
from PIL import Image, ImageTk
import glob
import tkFont
import sys
import pprint
import os
from JoypadScreen import JoypadScreen
from random import randint
from pygame import mixer

class JoypadioEvent(object):
    pass

class Joypadui:
    'UI controller for joypad voting system'

    # how long to stay on the pre-voting screen
    timerPrevote = 510 # 8 minutes 30 seconds

    # how long to keep the vote open for
    timerSeconds = 60
    
    # how long to spend on the vote result screen
    timeOnVoteResults = 30
    
    heading_top = 125
    
    sound_vote_open             = 'resources/vote_open.wav'    
    sound_win_team_a            = 'resources/win_team_a.wav'
    sound_win_team_b            = 'resources/win_team_b.wav'
    sound_vote_press_a          = 'resources/vote_press_a.wav'
    sound_vote_press_b          = 'resources/vote_press_b.wav'

    # --- no modifications to be made below this line please --

    # internal status,
    #   0 = initialising
    #   1 = vote is pending
    #   2 = vote is active
    #   3 = sudden death mode (next vote wins!) -- deprecated
    #   4 = displaying vote results
    # animations only run in states 1,2,3,4
    status = 0
    status_for_animations = [1,2,3,4]
    
    def STATUS_VOTE_PENDING(self):
        return 1
    def STATUS_VOTE_ACTIVE(self):
        return 2    
    def STATUS_VOTE_RESULTS(self):
        return 4
    def STATUS_INFOSCREEN(self):
        return 5

    # init using the root Tk() instance and the Joypadio library
    def __init__(self, root, io):
        print 'JoypadUI v1.1 initialising'
        self.root   = root
        self.io     = io
        self.io.subscribe(self.registerVote);
        
        self.timeRemaining      = self.timerPrevote
        self.displayTimeout     = self.timeOnVoteResults
        self.canvas_height      = root.winfo_screenheight() - 40 
        self.canvas_width       = root.winfo_screenwidth()
        self.font_header        = tkFont.Font(family="Helvetica", size=100, weight="bold")
        self.font_header2       = tkFont.Font(family="Helvetica", size=50, weight="bold")
        self.font_timer_pending = tkFont.Font(family="Helvetica", size=30, weight="normal")

        #screen loader
        self.screen = JoypadScreen(self)

        #vote control
        self.currentVoteId  = 1
        self.voteConfig     = []
        self.initFilesystem()
        # audio support
        mixer.init()
        # keyboard support
        self.registerKeyboardEvents()
        
        # ids (pointers) to timer objects so we can cancel them
        self.idCountdownTimer = 0; 
        self.idAnnounceWinner = 0;
        
   
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
        for i in xrange(1,32,1):
            voteEntity = {
                'voteId'         : i,
                'media_a'       : None,
                'media_b'       : None,
                'heading_a'      : 'Game A',
                'heading_b'      : 'Game B',
            }
            
            resdir = "resources" + os.path.sep
            
            # look for files on filesystem
            files = glob.glob(resdir + str(i) + "*.*")
            
            for team in ['a','b']:
                if (resdir + str(i) + team + '.txt') in files:
                    tmp = open(resdir + str(i) + team + ".txt")
                    voteEntity['heading_' + team] = tmp.read()
                if (resdir + str(i) + team +'.gif') in files:
                    voteEntity['media_'+team] = resdir + str(i) + team +".gif"
                if (resdir + str(i) + team +'.jpg') in files:
                    voteEntity['media_'+team] = resdir + str(i) + team + ".jpg"
                if (resdir + str(i) + team +'.jpeg') in files:
                    voteEntity['media_'+team] = resdir + str(i) + team + ".jpeg"          
                if (resdir + str(i) + team +'.mp4') in files:
                    voteEntity['media_'+team] = resdir + str(i) + team + ".mp4"
                    
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
        self.imageBG = Image.open( "resources/bg_pending.jpg")
        self.photoBG = ImageTk.PhotoImage(self.imageBG)
        self.bg = self.c.create_image(self.canvas_width/2,self.canvas_height/2,image=self.photoBG)

        self.imageBG_win_a = Image.open( "resources/bg_win_a.jpg")
        self.photoBG_win_a = ImageTk.PhotoImage(self.imageBG_win_a)
        self.imageBG_win_b = Image.open( "resources/bg_win_b.jpg")
        self.photoBG_win_b = ImageTk.PhotoImage(self.imageBG_win_b)
        
  
        self.textHeadingA = self.c.create_text(self.canvas_width/4, self.heading_top, text="Game A", font=self.font_header2, fill="white", anchor="n", justify="center")
        self.textHeadingB = self.c.create_text(self.canvas_width/4*3, self.heading_top, text="Game B", font=self.font_header2, fill="white", anchor="n", justify="center")
        self.textTeamAscore = self.c.create_text(self.canvas_width/4, self.canvas_height - 150, text="0", font=self.font_header, fill="white", justify="center")
        self.textTeamBscore = self.c.create_text(self.canvas_width/4*3, self.canvas_height - 150, text="0", font=self.font_header, fill="white", justify="center")

        self.textTimer = self.c.create_text(self.canvas_width/2, 75, text="COUNTDOWN", font=self.font_header, fill="green", justify="center")

        # register some mouse click events
        # allow modification of votes by clicking on the vote numbers - right click to decrease
        self.c.tag_bind(self.textTeamAscore,'<Button-1>', lambda event: self.registerVotePress(event,'a'));
        self.c.tag_bind(self.textTeamAscore,'<Button-2>', lambda event: self.registerVotePress(event,'-a'));
        self.c.tag_bind(self.textTeamAscore,'<Button-3>', lambda event: self.registerVotePress(event,'-a'));
        self.c.tag_bind(self.textTeamBscore,'<Button-1>', lambda event: self.registerVotePress(event,'b'));
        self.c.tag_bind(self.textTeamBscore,'<Button-2>', lambda event: self.registerVotePress(event,'-b'));
        self.c.tag_bind(self.textTeamBscore,'<Button-3>', lambda event: self.registerVotePress(event,'-b'));

        self.status = self.STATUS_INFOSCREEN()
        # self.loadVote(self.currentVoteId - 1)
        self.screen.loadInfoScreen()

        # start the GUI update routines
        self.updateUI()   

        self.c.pack()
        
    # register vote - manual overriding by clicking ... 
    def registerVotePress(self, event, team):
        if (team=='a'):
            self.io.scoreA += 1
            e = JoypadioEvent()
            e.action='vote'
            e.team='a'
            self.registerVote(e)
        if (team=='-a'):
            self.io.scoreA -= 1            
        if (team=='b'):
            self.io.scoreB += 1
            e = JoypadioEvent()
            e.action='vote'
            e.team='b'
            self.registerVote(e)			
        if (team=='-b'):
            self.io.scoreB -= 1

    def registerKeyboardEvents(self):

        self.root.bind_all('<Key>', self.handleKeyPress);

    def handleKeyPress(self, event):
        print "Keypressed:",event.char
        if (event.char=='i' or event.char=='I'):
            self.abortTimers()
            self.screen.loadInfoScreen()
        if event.char in ['1','2','3','4','5','6','7','8','9','0']:
            if event.char=='0':
                self.gotoVote(10)
            else:
                self.gotoVote(int(event.char))

        if event.char=='+':
            self.gotoVote(self.currentVoteId+1)
            
        if event.char=='-':
            self.gotoVote(self.currentVoteId-1)
            
        if event.char=='r':
            self.resetVote()
            
        if event.char=='t':
            self.skipTimer()
            
        if event.char=='f':
            self.abortTimers()
            self.screen.loadFinalScreen()
            
    def gotoVote(self,voteNumber):

        if (voteNumber<1 or voteNumber>len(self.voteConfig)):
            print "Vote number",voteNumber,"is not valid"
            return
        self.abortTimers()
        print "Interrupting current vote and loading vote",voteNumber
        self.resetVote()
        self.currentVoteId=voteNumber
        self.loadVote(self.currentVoteId - 1)
        self.countdownTimer()
        
    def loadVote(self, index):

        if (index >= len(self.voteConfig)):
            print "No more votes to load. Going to final screen."
            self.finalScreen()
            return

        print "Loading vote (index "+str(index)+")"

        # Set background to bg_pending
        self.imageBG = Image.open( "resources/bg_pending.jpg")
        self.photoBG = ImageTk.PhotoImage(self.imageBG)
        self.c.itemconfig(self.bg, image= self.photoBG)

        # headings
        self.c.itemconfig(self.textHeadingA, text=self.voteConfig[index]['heading_a'])
        self.c.itemconfig(self.textHeadingB, text=self.voteConfig[index]['heading_b'])

        # delete old gifs
        if (hasattr(self,'gif_a')):
            del self.gif_a        
        if (hasattr(self,'gif_b')):
            del self.gif_b
            
        # gif support
        if self.voteConfig[index]['media_a'].endswith('.gif'):
            self.gif_a = anim_gif(self.voteConfig[index]['media_a'])
            if (not hasattr(self,'imageGameA')):
                self.imageGameA = self.c.create_image(self.canvas_width/4,self.canvas_height/2,image=None)
            self.animate('a')
               
        if self.voteConfig[index]['media_b'].endswith('.gif'):
            self.gif_b = anim_gif(self.voteConfig[index]['media_b'])
            if (not hasattr(self,'imageGameB')):
                self.imageGameB = self.c.create_image(self.canvas_width/4*3,self.canvas_height/2,image=None)
            self.animate('b')

        #jpg support
        if (self.voteConfig[index]['media_a'].endswith('.jpg') or self.voteConfig[index]['media_a'].endswith('.jepg')):
            self.photo_a = Image.open(self.voteConfig[index]['media_a'])
            self.photo_aa = ImageTk.PhotoImage(self.photo_a);
            if (not hasattr(self,'imageGameA')):
                self.imageGameA = self.c.create_image(self.canvas_width/4,self.canvas_height/2,image=self.photo_aa)
            else:
                self.c.itemconfig(self.imageGameA, image=self.photo_aa)
            
        if (self.voteConfig[index]['media_b'].endswith('.jpg') or self.voteConfig[index]['media_b'].endswith('.jpeg')):
            self.photo_b = Image.open(self.voteConfig[index]['media_b'])
            self.photo_bb = ImageTk.PhotoImage(self.photo_b)
            if (not hasattr(self,'imageGameB')):
                self.imageGameB = self.c.create_image(self.canvas_width/4*3,self.canvas_height/2,image=self.photo_bb)
            else:
                self.c.itemconfig(self.imageGameB, image=self.photo_bb)
        
        # reset hidden/shown states, position

        showElements = ['imageGameA','textHeadingA','imageGameB','textHeadingB','textTeamAscore','textTeamBscore','textTimer']
        for guiElement in showElements:
            if (hasattr(self, guiElement)):
                obj = getattr(self, guiElement)
                self.c.itemconfig(obj, state=NORMAL)

        self.c.coords(self.textHeadingA, self.canvas_width/4,self.heading_top)
        self.c.coords(self.textHeadingB, self.canvas_width/4*3,self.heading_top)
        if (hasattr(self,'imageGameA')):
            self.c.coords(self.imageGameA, self.canvas_width/4, self.canvas_height/2)
        if (hasattr(self,'imageGameB')): 
             self.c.coords(self.imageGameB, self.canvas_width/4*3, self.canvas_height/2)

        hideElements = ['textTeamAscore','textTeamBscore']
        for guiElement in hideElements:
            if (hasattr(self, guiElement)):
                obj = getattr(self,guiElement)
                self.c.itemconfig(obj, state=HIDDEN)    


    def openVote(self):
        # set background to load bg_active
        self.imageBG = Image.open( "resources/bg_active.jpg")
        self.photoBG = ImageTk.PhotoImage(self.imageBG)
        self.c.itemconfig(self.bg, image= self.photoBG)
        
        # have to reset the score, as people were probably pushing buttons ... 
        self.io.scoreA = 0
        self.io.scoreB = 0
        self.c.itemconfig(self.textTeamAscore, state=NORMAL)
        self.c.itemconfig(self.textTeamBscore, state=NORMAL)
        self.status=self.STATUS_VOTE_ACTIVE()
        self.resetCountdownTimer(self.timerSeconds)
        self.countdownTimer()
        #play sound
        try:
            sound = mixer.Sound(self.sound_vote_open)
            sound.play()
        except:
            print "unable to play sound " + self.sound_vote_open;
        
        
    def countdownTimer(self):
        if (self.timeRemaining <= 0):
            self.timerReached();
        else:
            self.timeRemaining -= 1;
            self.idCountdownTimer = self.root.after(1000,self.countdownTimer);

    def resetCountdownTimer(self, time):
        if (time != None):
            self.timeRemaining = time
        else:
            self.timeRemaining = self.timerSeconds

    def abortTimers(self):
        self.root.after_cancel(self.idCountdownTimer)
        self.root.after_cancel(self.idAnnounceWinner)
            
    def timerReached(self):
        if (self.status==self.STATUS_VOTE_PENDING()):
            self.openVote();
            print 'Opening voting for ' +  str(self.timeRemaining) + ' seconds for vote #' + str(self.currentVoteId);
            return
            
        if (self.status==self.STATUS_VOTE_ACTIVE()):
            print '=========================='
            print ' Timer reached for vote ' + str(self.currentVoteId);
            print '=========================='
            print 'Team A: '+str(self.io.scoreA)+' votes for ' + self.voteConfig[self.currentVoteId-1]['heading_a'];
            print 'Team B: '+str(self.io.scoreB)+' votes for ' + self.voteConfig[self.currentVoteId-1]['heading_b'];

        if (self.status==self.STATUS_VOTE_ACTIVE() ):
                
            if (self.io.scoreA == self.io.scoreB):
                # choose a random winner in a draw situation
                winner = randint(1,2)
                if (winner==1):
                    print " ** Draw - randomly making team A win)";
                    self.io.scoreA += 1;
                else:
                    print " ** Draw - randomly making team B win)";
                    self.io.scoreB += 1; 
                
            if (self.io.scoreA > self.io.scoreB):
                print " ** Team A wins by " + str(self.io.scoreA-self.io.scoreB) +" votes **";
                print " ** "+ self.voteConfig[self.currentVoteId-1]['heading_a']+ " **";
                self.announceWinner('a')
                return
            else:
                print " ** Team B wins by " + str(self.io.scoreB-self.io.scoreA) +" votes **";
                print " ** "+ self.voteConfig[self.currentVoteId-1]['heading_b']+ " **";
                self.announceWinner('b')
                return

    # sets the active timer to zero so that we don't have to wait any longer
    def skipTimer(self):
        mixer.stop()
        self.abortTimers()
        
        if (self.status == self.STATUS_VOTE_PENDING() or self.status == self.STATUS_VOTE_ACTIVE()):
            self.timeRemaining = 0
            self.timerReached()
            return
        if (self.status == self.STATUS_VOTE_RESULTS()):
            self.resetAndLoadNextVote()
            return
        
        
    def announceWinner(self,team):
        self.status = self.STATUS_VOTE_RESULTS()
        if (team=='-'):
            if (self.displayTimeout <= 0):
                # announcement should finish now, so load next vote
                self.resetAndLoadNextVote()
                return
        if (team=='a'):
            self.c.itemconfig(self.bg, image=self.photoBG_win_a)
            self.displayTimeout = self.timeOnVoteResults
            self.c.coords(self.imageGameA, self.canvas_width/2, self.canvas_height/2)
            self.c.coords(self.textHeadingA, self.canvas_width/2,self.heading_top)
            self.c.itemconfig(self.imageGameB, state=HIDDEN)
            self.c.itemconfig(self.textHeadingB, state=HIDDEN)
            #play sound
            try:
                sound = mixer.Sound(self.sound_win_team_a)
                sound.play()
                print "playing sound " + self.sound_win_team_a;
            except:
                print "unable to play sound " + self.sound_win_team_a;
        if (team=='b'):
            self.c.itemconfig(self.bg, image=self.photoBG_win_b)
            self.displayTimeout = self.timeOnVoteResults      
            self.c.coords(self.imageGameB, self.canvas_width/2, self.canvas_height/2)
            self.c.coords(self.textHeadingB, self.canvas_width/2,self.heading_top)
            self.c.itemconfig(self.imageGameA, state=HIDDEN)
            self.c.itemconfig(self.textHeadingA, state=HIDDEN)
            #play sound
            try:
                sound = mixer.Sound(self.sound_win_team_b)
                sound.play()
                print "playing sound " + self.sound_win_team_b;
            except:
                print "unable to play sound " + self.sound_win_team_b;            
        if (team == 'a' or team == 'b'):
            self.c.itemconfig(self.textTeamAscore, state=HIDDEN)
            self.c.itemconfig(self.textTeamBscore, state=HIDDEN)
            self.c.itemconfig(self.textTimer, state=HIDDEN)
            
        # decerment the timer and run this function again after 1 second
        self.displayTimeout -= 1
        self.idAnnounceWinner = self.root.after(1000, self.announceWinner, '-');

    def resetVote(self):
        mixer.stop()
        self.root.after_cancel(self.idCountdownTimer)
        self.root.after_cancel(self.idAnnounceWinner)
        self.status = self.STATUS_VOTE_PENDING()
        self.resetCountdownTimer(self.timerPrevote)
        self.io.scoreA = 0
        self.io.scoreB = 0

    def resetAndLoadNextVote(self):
        mixer.stop()
        self.resetVote()
        self.currentVoteId += 1
        self.loadVote(self.currentVoteId - 1)
        self.countdownTimer()

    def finalScreen(self):
        self.abortTimers()
        self.screen.loadFinalScreen()

    def updateUI(self):
        'update the UI to display scores every 200ms'

        if (self.status == self.STATUS_VOTE_PENDING()):
            self.c.itemconfig(self.textTimer, text= 'Vote opens in ' + str(self.timeRemaining) + ' secs', fill='white', font=self.font_timer_pending);
         
        # vote is running
        if (self.status == self.STATUS_VOTE_ACTIVE()):
            self.c.itemconfig(self.textTeamAscore, text = self.io.scoreA)
            self.c.itemconfig(self.textTeamBscore, text = self.io.scoreB)
            self.c.itemconfig(self.textTimer, text= self.timeRemaining, fill='green', font=self.font_header);
         
        self.root.after(200,self.updateUI)
        
    def animate(self, target):
        if (target=='a'):
            if hasattr(self,'gif_a'):
                self.c.itemconfig(self.imageGameA, image= self.gif_a['frames'][self.gif_a['loc']])
                self.gif_a['loc'] += 1
                if self.gif_a['loc'] == self.gif_a['len']:
                    self.gif_a['loc'] = 0
                if (self.status in self.status_for_animations):
                    self.root.after(self.gif_a["delays"][self.gif_a['loc']] - 10, self.animate,'a')
        elif (target=='b'):
            if hasattr(self,'gif_b'):
                self.c.itemconfig(self.imageGameB, image= self.gif_b['frames'][self.gif_b['loc']])
                self.gif_b['loc'] += 1
                if self.gif_b['loc'] == self.gif_b['len']:
                    self.gif_b['loc'] = 0
                if (self.status in self.status_for_animations):
                    self.root.after(self.gif_b["delays"][self.gif_b['loc']] - 10, self.animate,'b')

    def registerVote(self, event):

        #play sound if there's an active vote
        if (event.action=='vote' and self.status == self.STATUS_VOTE_ACTIVE()):

            soundfile='';
            
            if (event.team=='a'):
                soundfile = self.sound_vote_press_a
            elif (event.team=='b'):
                soundfile = self.sound_vote_press_b

            if (soundfile != ''):
                try:
                    sound = mixer.Sound(soundfile)
                    sound.play()
                except:
                    print "unable to play sound " +soundfile ;
        
#
# other utility functions
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
