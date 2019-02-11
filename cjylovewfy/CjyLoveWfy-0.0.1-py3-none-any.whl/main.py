import pygame
import time
import random 
import CjyLoveWfy as cw
import os
# import local2utf8  

display_width = 1000
display_height = 800
 
black = (0,0,0)
white = (255,255,255)

red = (200,0,0)
green = (0,200,0)

bright_red = (255,0,0)
bright_green = (0,255,0)
 
block_color = (53,115,255)
 
car_width = 150
clock = pygame.time.Clock()

path=cw.__path__[0]

global gameDisplay

def main():
	global gameDisplay,background,carImg
	pygame.init()
	
	
	 
	gameDisplay = pygame.display.set_mode((display_width,display_height))
	pygame.display.set_caption('Happy Valentines Day!')
	


	carImg = pygame.image.load(path+'/racecar.jpg')
	gameIcon = pygame.image.load(path+'/racecar.jpg')
	background = pygame.image.load(path+'/background.jpg').convert()
	background.set_alpha(40)

	pygame.display.set_icon(gameIcon)

	pause = False

	game_intro()
	game_loop()
	pygame.quit()
	quit()
 
def things_dodged(count):
	global gameDisplay
	font = pygame.font.SysFont("comicsansms", 25)
	text = font.render("Dodged: "+str(count), True, black)
	gameDisplay.blit(text,(0,0))
 
def things(thingx, thingy, thingw, thingh, color):
	global gameDisplay
	pygame.draw.rect(gameDisplay, color, [thingx, thingy, thingw, thingh])

def things_img(thingx, thingy, thingw, thingh, Img):
	global gameDisplay
	gameDisplay.blit(pygame.transform.scale(Img,(thingw,thingh)),(thingx,thingy))
 
def car(x,y):
	global gameDisplay,carImg
	gameDisplay.blit(pygame.transform.scale(carImg,(150,125)),(x,y))
 
def text_objects(text, font):
	textSurface = font.render(text, True, black)
	return textSurface, textSurface.get_rect()
 
def crash():
	largeText = pygame.font.Font(path+"/font.ttf",100)
	TextSurf, TextRect = text_objects("你被撞瓜了！!", largeText)
	TextRect.center = ((display_width/2),(display_height/5*2))
	gameDisplay.blit(TextSurf, TextRect)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
				
		button("再来一局",175,450,150,50,green,bright_green,game_loop)
		button("退出",700,450,100,50,red,bright_red,quitgame)

		pygame.display.update()
		clock.tick(15) 

def out():
	largeText = pygame.font.Font(path+"/font.ttf",100)
	TextSurf, TextRect = text_objects("瓜瓜你出界了呢!", largeText)
	TextRect.center = ((display_width/2),(display_height/5*2))
	gameDisplay.blit(TextSurf, TextRect)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
				
		button("再来一局",175,450,150,50,green,bright_green,game_loop)
		button("退出",700,450,100,50,red,bright_red,quitgame)

		pygame.display.update()
		clock.tick(15) 

def finish():
	largeText = pygame.font.Font(path+"/font.ttf",100)
	TextSurf, TextRect = text_objects("宝贝你通关了呢好厉害~", largeText)
	TextRect.center = ((display_width/2),150)
	gameDisplay.blit(TextSurf, TextRect)

	largeText = pygame.font.Font(path+"/font.ttf",80)
	TextSurf, TextRect = text_objects("祝宝贝节日快乐！", largeText)
	TextRect.center = ((display_width/2), 250)
	gameDisplay.blit(TextSurf, TextRect)

	TextSurf, TextRect = text_objects("希望宝贝每天都开开心心！", largeText)
	TextRect.center = ((display_width/2), 350)
	gameDisplay.blit(TextSurf, TextRect)

	TextSurf, TextRect = text_objects("心情不好的时候，就多想想", largeText)
	TextRect.center = ((display_width/2), 450)
	gameDisplay.blit(TextSurf, TextRect)

	TextSurf, TextRect = text_objects("我们在一起快乐地玩的时光呢~", largeText)
	TextRect.center = ((display_width/2), 550)
	gameDisplay.blit(TextSurf, TextRect)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
				
		button("再来一局",175,650,150,50,green,bright_green,game_loop)
		button("退出",700,650,100,50,red,bright_red,quitgame)

		pygame.display.update()
		clock.tick(15) 

def button(msg,x,y,w,h,ic,ac,action=None):
	mouse = pygame.mouse.get_pos()
	click = pygame.mouse.get_pressed()

	if x+w > mouse[0] > x and y+h > mouse[1] > y:
		pygame.draw.rect(gameDisplay, ac,(x,y,w,h))
		if click[0] == 1 and action != None:
			action()         
	else:
		pygame.draw.rect(gameDisplay, ic,(x,y,w,h))
	smallText = pygame.font.Font(path+"/font.ttf",50)
	textSurf, textRect = text_objects(msg, smallText)
	textRect.center = ( (x+(w/2)), (y+(h/2)) )
	gameDisplay.blit(textSurf, textRect)

def quitgame():
	pygame.quit()
	quit()

def unpause():
	global pause
	pygame.mixer.music.unpause()
	pause = False

def paused():
	############
	pygame.mixer.music.pause()
	#############
	largeText = pygame.font.Font(path+"/font.ttf",100)
	TextSurf, TextRect = text_objects("暂停", largeText)
	TextRect.center = ((display_width/2),(display_height/5*2))
	gameDisplay.blit(TextSurf, TextRect)

	while pause:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()

		button("继续",200,450,100,50,green,bright_green,unpause)
		button("退出",700,450,100,50,red,bright_red,quitgame)

		pygame.display.update()
		clock.tick(15)   

def game_intro():
	global gameDisplay,background
	intro = True

	while intro:
		for event in pygame.event.get():
			#print(event)
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
				
		gameDisplay.fill(white)
		gameDisplay.blit(background,(0,-100))

		largeText = pygame.font.Font(path+"/font.ttf",100)
		TextSurf, TextRect = text_objects("给宝贝的情人节小礼物~", largeText)
		TextRect.center = ((display_width/2),(display_height/4))
		gameDisplay.blit(TextSurf, TextRect)

		middleText = pygame.font.Font(path+"/font.ttf",70)
		TextSurf, TextRect = text_objects("游戏规则：", middleText)
		TextRect.center = ((display_width/2),320)
		gameDisplay.blit(TextSurf, TextRect)

		smallText = pygame.font.Font(path+"/font.ttf",50)
		TextSurf, TextRect = text_objects("1. 按左右键控制小车左右移动", smallText)
		TextRect.center = ((display_width/2),400)
		gameDisplay.blit(TextSurf, TextRect)

		TextSurf, TextRect = text_objects("2. 若小车被方框撞到则游戏结束", smallText)
		TextRect.center = ((display_width/2),460)
		gameDisplay.blit(TextSurf, TextRect)

		TextSurf, TextRect = text_objects("3. 躲开所有方框后即通关", smallText)
		TextRect.center = ((display_width/2),520)
		gameDisplay.blit(TextSurf, TextRect)

		TextSurf, TextRect = text_objects("4. 按 p 键可暂停", smallText)
		TextRect.center = ((display_width/2),580)
		gameDisplay.blit(TextSurf, TextRect)


		button("开始",200,650,100,50,green,bright_green,game_loop)
		button("退出",700,650,100,50,red,bright_red,quitgame)

		pygame.display.update()
		clock.tick(15)

def game_loop():
	global pause,gameDisplay,background
	############
	pygame.mixer.music.load(path+'/tiantiande.wav')
	pygame.mixer.music.play(-1)
	############
	x = (display_width * 0.45)
	y = (display_height * 0.85)
 
	x_change = 0

	thing_width = 500
	thing_height = 375
	thing_startx = random.randrange(10, display_width-(thing_width+10))
	thing_starty = -600
	thing_speed = 3
 
	thingCount = 1
 
	dodged = 0
 
	gameExit = False

	while not gameExit:
		if thingCount>15:
			finish()

		Img=pygame.image.load(path+'/photos/'+str(thingCount)+'.jpg')
		thing_width=Img.get_rect().size[0]
		thing_height=Img.get_rect().size[1]
 
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
 
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					x_change = -15
				if event.key == pygame.K_RIGHT:
					x_change = 15
				if event.key == pygame.K_p:
					pause = True
					paused()
 
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
					x_change = 0
 
		x += x_change
		gameDisplay.fill(white)
		gameDisplay.blit(background,(0,-100))

		things_img(thing_startx, thing_starty, thing_width, thing_height, Img)
 
		thing_starty += thing_speed
		car(x,y)
		things_dodged(dodged)
 
		if x > display_width - car_width or x < 0:
			out()
 
		if thing_starty > display_height:
			thing_starty = 0 - thing_height
			thing_startx = random.randrange(10, display_width-(thing_width+10))
			dodged += 1
			thing_speed += 1
			thingCount+=1
			# thing_width += (dodged * 1.2)
 
		if y < thing_starty+thing_height:
			if x > thing_startx and x < thing_startx + thing_width or x+car_width > thing_startx and x + car_width < thing_startx+thing_width:
				crash()
		
		pygame.display.update()
		clock.tick(60)

if __name__=='__main__':
	main()