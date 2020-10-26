# -*- coding: utf8 -*-
import tkinter as tk
import re
import pygame
from pygame import *
import random, math, datetime, os

# set the color value
black = ( 0, 0, 0)
white = ( 255, 255, 255)
red = ( 255, 0, 0)
blue = ( 0, 0, 255)
green = (0, 255, 0)
bg = (30, 62, 87)

# Defines the class that fires the target flash block
class Block(pygame.sprite.Sprite):
	def __init__(self, color):				  
		pygame.sprite.Sprite.__init__(self)	  
		self.image = pygame.Surface([30, 30]) 
		self.image.fill(color)				  
		self.rect = self.image.get_rect()	  

# Defines the class for shooting sight
class Player(pygame.sprite.Sprite):		  
	def __init__(self):										
		pygame.sprite.Sprite.__init__(self)					
		gun = pygame.image.load('aim.png').convert_alpha()	
		gun = pygame.transform.smoothscale(gun,(30,30))		
		self.image = gun									
		self.rect = self.image.get_rect()					

	def update(self):					 
		pos = pygame.mouse.get_pos()	 
		self.rect.x = pos[0]			 
		self.rect.y = pos[1]

# Defines the bullet class
class Bullet(pygame.sprite.Sprite):
	def __init__(self, mouse, players):					   
		pygame.sprite.Sprite.__init__(self)				   
		self.image = pygame.Surface([4, 10])			   
		self.mouse_x, self.mouse_y = mouse[0], mouse[1]	   
		self.player = players							   
		self.rect = self.image.get_rect()				   

# Floating text during the game
# Parameters are: font, which object to float on, text content, font size, position, and color
def draw_text(font, surf, text, size, x, y, color): 
	text_surface = font.render(text, True, color)
	text_rect = text_surface.get_rect()
	text_rect.midtop = (x, y)
	surf.blit(text_surface, text_rect)

# Enter the shooting range
def run():
	
	lvscore = {'hard': [13, 10], 'medium': [18, 12], 'easy': [30, 20]}
	
	bestscore = {"hard": {"30": 0.0, "45": 0.0, "60": 0.0}, "medium": {"30": 0.0, "45": 0.0, "60": 0.0}, "easy": {"30": 0.0, "45": 0.0, "60": 0.0}}
	
	pygame.init()
	
	pygame.mixer.init()
	
	ak47 = pygame.mixer.Sound('ak47.wav')
	
	ak47.set_volume(0.6)
	
	pygame.mouse.set_cursor((8, 8), (0, 0), (0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0))
	
	screen_width = 700
	screen_height = 400
	
	screen = pygame.display.set_mode([screen_width,screen_height])
	
	all_sprites_list = pygame.sprite.Group()
	block_list = pygame.sprite.Group()
	bullet_list = pygame.sprite.Group()
	
	myfont = pygame.font.SysFont(pygame.font.get_fonts()[0], 16)
	
	player = Player()
	
	all_sprites_list.add(player)
	
	done = False
	
	clock = pygame.time.Clock()
	# Current game initialization: score 0, number of shots 0
	score = 0
	shot = 0
	
	timecapsule = {}
	
	starttime = datetime.datetime.now()
	
	countdown = 1
	
	if os.path.exists("./bestscore.dat"):
		for line in open("./bestscore.dat","r"):
			lv, tm, sc = line.strip().split(",")
			bestscore[lv][tm] = float(sc)
	
	
	tm, lv = getVar()
	
	totaltime = int(tm)
	
	i = 0 
	# Main game loop
	while not done:
		i += 1 # The count of cycles + 1
		countdown = totaltime - (datetime.datetime.now() - starttime).seconds 
		if countdown <= 0: # Countdown to 0, game over, exit main game loop
			done = True
		for b in block_list: 
			timecapsule[b] -= 1 
			if timecapsule[b] <= 0: 
				all_sprites_list.remove(b) 
				block_list.remove(b) 
		
		if i % lvscore[lv][1] == 1: # The interval between reaching the flash block of the current difficulty
			block = Block(blue) # Add a new flash block, randomly configured, but not beyond the window
			block.rect.x = random.randrange(screen_width-30)
			block.rect.y = random.randrange(screen_height-50)
			block_list.add(block) 
			timecapsule[block] = lvscore[lv][0] 
			all_sprites_list.add(block) 
	
		# Listen for all events
		for event in pygame.event.get(): 
			if event.type == pygame.QUIT: # When the close window is clicked, the game ends directly
				done = True
			elif event.type == pygame.MOUSEBUTTONDOWN: # When clicking a mouse to shoot
				bullet = Bullet(pygame.mouse.get_pos(), [player.rect.x, player.rect.y]) 
				bullet.rect.x = player.rect.x + 12 + int(random.random() * 2) 
				bullet.rect.y = player.rect.y + 12 + int(random.random() * 2)
				all_sprites_list.add(bullet) 
				bullet_list.add(bullet) 
				ak47.play() 
				shot += 1 

		# game logic
		all_sprites_list.update() 

		for bullet in bullet_list: 
			block_hit_list = pygame.sprite.spritecollide(bullet, block_list, True) 
			for block in block_hit_list: 
				block_list.remove(block) 
				all_sprites_list.remove(block) 
				score += 1 
			bullet_list.remove(bullet) 
			all_sprites_list.remove(bullet) 
		
		screen.fill(bg) 
		all_sprites_list.draw(screen) 
		# Draws at the bottom of the screen the shot score for the current round and the best score in history for the same length/difficulty
		draw_text(myfont, screen, "TotalShots: %d TotalHits: %d Accuracy: %.2f%% BestScore: %.2f%%"%(shot, score, 0.0 if shot == 0 else score * 100.0 / float(shot), bestscore[lv][tm] ), 18, screen_width / 2, screen_height - 30, green)
		# Draws the number of seconds left in the current game at the top of the screen
		draw_text(myfont, screen, "Time CountDown: %d"%(countdown), 14, screen_width / 2, 10, green)
		# refresh screen
		pygame.display.flip()
		 
		clock.tick(20)
	
	if countdown <= 0: # The remaining time is 0 to finish the current game, and the score is compared with the best score in history
		bestscore[lv][tm] = max(score * 100.0 / float(shot) if shot > 0 else 0.0, bestscore[lv][tm])
		# The updated best result is written to the file
		with open("./bestscore.dat","w") as f:
			for k1 in bestscore:
				for k2 in bestscore[k1]:
					f.write("%s,%s,%f\n"%(k1,k2,bestscore[k1][k2]))
	
	pygame.quit()

# Process the selected game time/difficulty text
def getVar():
	tm = re.findall(r"\d+\.?\d*",timeVar.get())[0] 
	lv = skillVar.get().split(": ")[1].replace(" ","") 
	return tm, lv

# Save the current configuration
def save():
	tm, lv = getVar() 
	with open("./param.cfg","w") as f: f.write("%s,%s"%(tm,lv)) 

# Program entrance
if __name__ == "__main__":
	
	window = tk.Tk()
	
	winWidth = 600
	winHeight = 400
	
	tm = 30
	lv = 'medium'
	# If saved the game configuration, the read configuration automatically updates the default game time and difficulty
	if os.path.exists("./param.cfg"):
		tm, lv = open("./param.cfg","r").read().strip().split(",")
		tm = int(tm) if tm in ['30', '45', '60'] else 30
		lv = lv if lv in ['medium', 'easy', 'hard'] else 'medium'

	# Main window Settings
	window.title("Aiming Assistant")
	
	window.geometry("%sx%s+%s+%s" % (winWidth, winHeight, int((window.winfo_screenwidth() - winWidth) / 2), int((window.winfo_screenheight() - winHeight) / 2)))
   
	window.resizable(0, 0)
	
	window['background']='silver'
	
	tk.Label(window, bg='silver', fg='black', text='Aiming Assistant', font=('Times', 32, 'bold')).place(relx = 0.25, rely = 0.1)
	
	# Game time check box
	timeVar = tk.StringVar()
	
	timeVar.set("Time: %ds"%(tm))
	
	tmp = tk.OptionMenu(window, timeVar, "Time: 30s", "Time: 45s", "Time: 60s")
	
	tmp.place(relx	= 0.28, rely = 0.4)
	
	# Game difficulty check box
	skillVar = tk.StringVar()
	
	skillVar.set("Level: %s"%(lv))
	
	tmp = tk.OptionMenu(window, skillVar, "	 Level: easy  ", "Level: medium", "	 Level: hard  ")
	
	tmp.place(relx = 0.48, rely = 0.4)
	
	# START button to define the size and position, and then call the Run function to enter the shooting range interface
	tk.Button(window, text="START", width=15, pady=5, command=run).place(relx = 0.37, rely = 0.6)
	# EXIT button, define the size and location, and then call EXIT directly to EXIT the program
	tk.Button(window, text="EXIT", width=15, pady=5, command=exit).place(relx = 0.37, rely = 0.8)
	# SAVE button, define size and location, click after calling SAVE function to SAVE the current selection time and difficulty of the configuration to the configuration file
	tk.Button(window, text="SAVE", width=15, pady=5, command=save).place(relx = 0.37, rely = 0.7)
	
	window.mainloop() # The home directory window loop captures user interaction
