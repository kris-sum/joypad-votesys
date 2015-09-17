import	sys
import	pprint
import	os
import time

class JoypadLights:
	
	def	__init__(self, joypadui):
		self.joypadui = joypadui
		self.joypadui.subscribe(self.eventHandler)
		
		self.gb_board	=	3
		
		#self.initLights()
		#self.setupRamps(0)
		#self.setupRamps(1)
		#self.lightCheck()

	def initLights(self):
		import gertbot2 as gb
		
		gb.open_uart(0)
		print("Found gertbot board version:	%d"	% gb.get_version(self.gb_board))
		
		# set brushed mode
		gb.set_mode(self.gb_board,0,1)
		gb.set_mode(self.gb_board,1,1)
		
		# light init
		self.lights('a','off')
		self.lights('b','off')
	
	def setupRamps(self, channel):
		#setup the on/off ramps
		# short on, long off.
		gb.set_brush_ramps(self.gb_board, channel, 2, 5, 1)
		
	def lightCheck(self):
		#light check
		print "Light Check initialising ..."
		time.sleep(1)
		print "RED (a) ON"
		self.lights('a','on')
		time.sleep(1)
		print "RED (a) OFF"
		self.lights('a','off')
		time.sleep(1)
		print "BLUE (b) ON"
		self.lights('b','on')
		time.sleep(1)
		print "BLUE (b) OFF"
		self.lights('b','off')
		print "Light check finished"
	
	# joypadui events raised go here
	def	eventHandler(self,	event):
		if (event.action=="loadVote"):
			self.onLoadVote(event)		
		if (event.action=="openVote"):
			self.onOpenVote(event)				
		if	(event.action=="countdown"):
			self.onCountdown(event)
			
		if (event.action=="announceWinner"):
			self.onAnnounceWinner(event)		
		
	def	onLoadVote(self, event):
		self.lights('a','off')
		self.lights('b','off')
		
	def	onOpenVote(self, event):
		self.lights('a','on')
		self.lights('b','on')
	
	def	onAnnounceWinner(self, event):
		if (event.team == 'a'):
			self.lights('a','on')
			self.lights('b','off')
		else:
			self.lights('a','off')
			self.lights('b','on')
			
	def onCountdown(self, event):
		if (event.time == 10):
			self.pulseLights('a', 5)
			self.pulseLights('b', 5)
		
	def getChannelFromTeam(self, team):
		if (team =='a'):
			channel	= 0
		else:
			channel	= 1
			
		return channel
	
	# turn the lights on/off for a team
	def	lights(self, team, state):

		if (state=='on'):
			direction =	1
		else:	
			direction =	0
		
		gb.move_brushed(self.gb_board, self.getChannelFromTeam(team), direction)

	# pulese the lights for a team for a given number of iterations
	def pulseLights(self, team, number):
		
		if not hasattr(self.pulseLights, "config"):
			# it doesn't exist yet, so initialize it
			# we use a different set of counters and timers for each team
			self.pulseLights.__func__.config =  { 'a' :  { 'counter':0, 'timer': {} }, 'b':  { 'counter':0, 'timer': {} }  }
		
		if (self.pulseLights.config[team]['counter'] == 0):
			# setup the ramps to do the fading
			gb.set_brush_ramps(self.gb_board, self.getChannelFromTeam(team),2,2,1)
			#print "Lights: ramp config"
		
		if (self.pulseLights.config[team]['counter'] % 2 == 0):
			self.lights(team,'on')
			#print "Lights: " + str(team) + " team on "
		else:
			self.lights(team,'off')
			#print "Lights: " + str(team) + " team off "
			
		if (self.pulseLights.config[team]['counter'] >= (number * 2)):
			# reset this team's configuration
			self.pulseLights.__func__.config[team] = { 'counter':0, 'timer': {} }
			self.setupRamps(self.getChannelFromTeam(team))
			# reset the counter so that the next pulseLights command will work properly
			return
	
		self.pulseLights.__func__.config[team]['counter'] += 1
		self.pulseLights.__func__.config[team]['timer'] = self.joypadui.root.after(1000,self.pulseLights, team, number);
	 	
	   