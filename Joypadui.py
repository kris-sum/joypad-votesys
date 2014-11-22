# UI class
from Tkinter import *
from PIL import Image, ImageTk
import tkFont

class Joypadui:
    'UI controller for joypad voting system'
    
    # count down timer - change this value if you want
    timerSeconds = 300

    # init using the root Tk() instance, and the Joypadio library
    def __init__(self, root, io):
        self.root = root
        self.io = io
        self.timeRemaining = self.timerSeconds
        self.canvas_height = root.winfo_screenheight()-40
        self.canvas_width  = root.winfo_screenwidth()
        self.font_header = tkFont.Font(family="Helvetica", size=100, weight="bold")

    def initGui(self):
        self.c = Canvas(self.root, width=self.canvas_width, height=self.canvas_height)

        # make everything centered, that way we can deal with different resolutions easier insetad of
        # anchoring everything to the top left
        self.imageBG = Image.open( "resources/bg.jpg")
  
        self.photoBG = ImageTk.PhotoImage(self.imageBG)
        self.bg = self.c.create_image(self.canvas_width/2,self.canvas_height/2,image=self.photoBG)

        self.textTeamA = self.c.create_text(self.canvas_width/4, 100, text="Team A", font=self.font_header, fill="white")
        self.textTeamB = self.c.create_text(self.canvas_width/4*3, 100, text="Team B", font=self.font_header, fill="white")
        self.textTeamAscore = self.c.create_text(self.canvas_width/4, 250, text="0", font=self.font_header, fill="white")
        self.textTeamBscore = self.c.create_text(self.canvas_width/4*3, 250, text="0", font=self.font_header, fill="white")

        self.textTimer = self.c.create_text(self.canvas_width/2, self.canvas_height/2, text="COUNTDOWN", font=self.font_header, fill="red")

        self.updateUI()
        self.countdownTimer()

        self.c.pack()

    def countdownTimer(self):
        if (self.timeRemaining <= 0):
            self.timerReached();
        else:
            self.timeRemaining = self.timeRemaining - 1;
            self.root.after(1000,self.countdownTimer);

    def resetCountdownTimer(self):
        self.timeRemaining = self.timerSeconds

    def timerReacher(self):
        'something'
        # dislpay the voting results screen, plus a countdown to the next vote session

    def updateUI(self):
        'update the UI to display scores every 200ms'
        self.c.itemconfig(self.textTeamAscore, text = self.io.scoreA)
        self.c.itemconfig(self.textTeamBscore, text = self.io.scoreB)
        self.c.itemconfig(self.textTimer, text= self.timeRemaining);
        self.root.after(200,self.updateUI)
