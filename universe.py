from settings import *
import pygame
import random
import pyperclip
import threading
import os
import time
from math import cos, sin

pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1' #center window
clock = pygame.time.Clock()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)

colors = [pygame.Color("red"), pygame.Color("purple"), pygame.Color("pink"),
		pygame.Color("white"), pygame.Color("yellow"), pygame.Color("lightblue")]

abc = "abcdefghijklmnopqrstuvwxyz"

prvi=["Ku","Ste","Ser","Gri","Di","Ni","Pa","Bo","A","Je","Ta","Gav","Mi","Sla","Sne","Snje","Di","Du","Da","Bor","Bran","Zdrav","Ra","Lje","Vu","Bo","Voj","Ja","Ran","Nov","Su","Sve","Svje",
		  "Zvje","Zve","Sve","Dmi","Slav","Mir","Rat","Rad","Boj","Stra","Ne","Ve","Sun","Ma","Ta","Fej","Ju","Je","I","Vla"]
sred=["go","ri","mi","tri","ko","li","sta","si","li","sa","ve","tja","lo","ri","dja","za","ja","brav","bor","doj","po","sa","go","sla","dran","za","tla","zda","mir","ni","lja","boj","hi",
		  "ci","ri","ja","hu","a","dzu","tu","re","mi","ho","di","mir","sti"]
zadn=["fan","gej","je","na","vle","jo","ja","ta","lo","mir","ca","djan","ven","ka","va","ljub","slav","ko","tar","sa","nja","bor","ja","din","lah","suf","da","sus","dolf","sta","sto"]


def namer():
		middle=''
		for _ in range(random.randrange(0,3)):
				middle=''.join([middle, random.choice(sred)])
		first = random.choice(prvi)
		last = random.choice(zadn)
		return first+middle+last

def planet_namer():
	output = ""
	for _ in range(random.randint(3,15)):
		output += abc[random.randint(0, 25)]

	return output

class StarType:
	def __init__(self, name, color, temperature, life=False, chance=(0,40)):
		self.name = name #Ime vrste // string
		self.color = color #Boja zvijezde // tuple(R,G,B)
		self.temperature = temperature #Temperatura planeta u celsiusu // tuple(od, do)
		self.life = life #Dal planete mogu imati zivot // True False
		self.chance = chance

#ovdje dodavaj vrste zvijezda
star_types = [
	StarType("Gentle", (255,255,255), (10,40), life=True),
	StarType("Temperate", (255,81,12), (150, 450)), #pakao
	StarType("Frozen", (125,192,255), (-300, -100)),
	StarType("Radioactive", (255,234,100), (30,70), life=True),
	StarType("Acid", (160,255,0), (-120, 120), chance=(0,80)),
	StarType("Black Hole", (10,10,10), (-273, -200), chance=(0,250))
]

class Planet:
	def __init__(self):
		self.radius = 0
		self.name = ""
		self.t = 0
		self.reversedRotation = False
		self.hasWater = False
		self.life = False
		self.ring = False
		self.temperature = 0 #celsius
		self.gas_giant = False
		self.moons = []

		self.gases = 0.0
		self.water = 0.0
		self.minerals = 0.0
		self.resources = 0.0
		self.population = 0
				

class Star:
	def __init__(self, x, y, generateSystem=True):
		seed = (x & 0xFFFF) << 16 | (y & 0xFFFF)
		random.seed(seed)
		self.type = random.choice(star_types)
		self.starExists = random.randint(*self.type.chance) == 1
		if not self.starExists:
				return

		self.color = self.type.color
		self.radius = random.randint(5, 22)

		#Ako mi treba samo da prikaze zvijezdu ne mora onda generisati sve planete i detalje o njoj
		#nego samo izgled
		if not generateSystem: 
			return

		self.name = namer()
		self.planets = []
		n_planets = random.randint(0, 6)
		for _ in range(n_planets):
			p = Planet()
			p.name = namer()
			p.radius = random.randint(5,12)
			p.reversedRotation = random.randint(0,150)==1
			p.t = random.randint(0,360)
			nMoons = random.randint(-5, 3) #-5 da budu vece sanse da nemaju nista nego da svaka ima satelit
			for _ in range(nMoons):
				t = random.randint(0,360)
				reversedRotation = random.randint(0,20)==1
				p.moons.append([t, reversedRotation])


			p.ring = random.randint(0,10) == 1
			p.temperature = random.randint(*self.type.temperature)

			if p.radius >= 10: 
				p.gas_giant = random.randint(0,5) == 1

			if not p.gas_giant:
				if p.temperature > 0 and p.temperature < 100:
					p.hasWater = random.randint(0,50) == 1
					if p.hasWater and self.type.life:
						p.life = random.randint(0,10) == 1

			
			if p.gas_giant:
				p.gases = 1.0
				p.minerals = 0.0
				p.resources = 0.0
				p.water = 0.0
			else:
				p.gases = random.random()
				p.minerals = random.random()
				p.resources = random.random()
				if p.hasWater: p.water = random.random()
			final = 1.0 / (p.gases + p.minerals + p.resources + p.water)
			p.gases *= final * 100
			p.minerals *= final * 100
			p.resources *= final * 100
			p.water *= final * 100
			#Ovaj dio sluzi da izracuna procenat %
			self.planets.append(p)


class Camera:
	def __init__(self):
		self.x = 0
		self.y = 0
		self.speed = 1

	def move(self):
		pressed = False
		key = pygame.key.get_pressed()

		if key[pygame.K_w]:
				self.y -= self.speed
				pressed = True

		if key[pygame.K_s]:
				self.y += self.speed
				pressed = True

		if key[pygame.K_a]:
				self.x -= self.speed
				pressed = True

		if key[pygame.K_d]:
				self.x += self.speed
				pressed = True

		if key[pygame.K_v]:
			#ako se pritisne V onda uzme od clipboarda podatke
			try:
				x, y = pyperclip.paste().split(":")
				x, y = int(x), int(y)
				self.teleport(x, y)
			except:
				return

		return pressed

			
	def teleport(self, x, y):
		self.x = x
		self.y = y

cam = Camera()

font = pygame.font.SysFont("Arial", 30)
font_star = pygame.font.SysFont("Arial", 12, bold=True)
font_info = pygame.font.SysFont("Arial", 25)

def get_mouse_in_segment(galaxy=True):
	mos_pos = pygame.mouse.get_pos()
	mos_pos = (mos_pos[0]//SEGMENTS, mos_pos[1]//SEGMENTS) #pozicija misa na ekranu
	mos_galaxy = (mos_pos[0] + cam.x, mos_pos[1] + cam.y) #pozicija misa u svemiru

	if galaxy:
		return mos_galaxy
	else:
		return mos_pos

def clicked():
	click = pygame.mouse.get_pressed()

	if click[0]:
		return 1
	elif click[2]:
		return 2

def command():
	#Konzola thread
	print("To change coords use this format - x:y or use WASD")
	while True:
		coords = input(">>> ")
		try:
			x, y = coords.split(":")
			x, y = int(x), int(y)
		except:
			continue

		cam.teleport(x, y)


threading.Thread(target=command, daemon=True).start()

width = HALF_WIDTH
height = HEIGHT
border = 1

selected = False
selectedStar = [0,0] #x,y

running = True
while running:
	clock.tick(60)
	win.fill(BLACK)

	cam.move()

	for x in range(SECTORS_X):
		for y in range(SECTORS_Y):
			#pygame.draw.rect(win, WHITE, (x*SEGMENTS,y*SEGMENTS,SEGMENTS,SEGMENTS), 1)
			star = Star(x + cam.x, y + cam.y, False)
			if star.starExists:
				center = (x*SEGMENTS+SEGMENTS//2, y*SEGMENTS+SEGMENTS//2)
				pygame.draw.circle(win, star.color, center, star.radius)
				#renderuje zvijezde bez generisanja detalja (samo izgleda)


	if selected:
		x, y = selectedStar
	else:
		x, y = get_mouse_in_segment()
	star = Star(x, y)
	if star.starExists:
		x, y = x-cam.x, y-cam.y
		center = (x*SEGMENTS+SEGMENTS//2, y*SEGMENTS+SEGMENTS//2)
		if x > -SECTORS_X and x < SEGMENTS:
			if y > -SECTORS_Y and y < SEGMENTS:
				#ako je x,y u ekranu onda radi slijedece:
				pygame.draw.circle(win, WHITE, center, star.radius+5, 1)
				name_text = font_star.render(star.name, True, WHITE)
				name_w = name_text.get_width()
				name_h = name_text.get_height()
				win.blit(name_text, (center[0] - name_w//2,center[1] + star.radius+5))
				try:
					pos_text = font_star.render(f"x:{x+cam.x} y: {y+cam.y}", True, WHITE)
					pos_w = pos_text.get_width()
					win.blit(pos_text, (center[0] - pos_w//2,center[1] +star.radius+20))
				except:
					pass

		rel_x = 0
		rel_y = HEIGHT-height - border

		if x*SEGMENTS <= rel_x + width:
			#if y*SEGMENTS >= rel_y and y*SEGMENTS <= rel_y+height:
			#ako je x na lijevoj strani onda prikaze podatke na desnoj
			rel_x = WIDTH-width-border
			rel_y = 0 - border

		rel_x_center = rel_x+width//2
		rel_y_center = rel_y+height//2
		left_bottom = (rel_x, height)

		pygame.draw.rect(win, BLACK, (rel_x, rel_y, width, height))
		pygame.draw.rect(win, WHITE, (rel_x, rel_y, width, height), 2)

		pygame.draw.circle(win, star.color, (rel_x_center, rel_y_center), star.radius)
		mos_x, mos_y = pygame.mouse.get_pos()

		texts = []
		texts.append(font_info.render(f"Name: {star.name}", True, WHITE))
		texts.append(font_info.render(f"Type: {star.type.name}", True, WHITE))
		texts.append(font_info.render(f"Number of planets: {len(star.planets)}", True, WHITE))
		


		text_width = texts[2].get_width()
		text_height = texts[0].get_height()
		text_offset = -text_height
		for text in reversed(texts):
			win.blit(text, (rel_x+width-text_width, height+text_offset))
			text_offset -= text_height
			#Render textova


		orbit = star.radius*2 + 25
		for n, planet in enumerate(star.planets):
			n += 1
			planet.t += -time.time()/n if planet.reversedRotation else time.time()/(n**2)

			planet_x = orbit * cos(planet.t) + rel_x_center
			planet_y = orbit * sin(planet.t) + rel_y_center

			pygame.draw.circle(win, WHITE, (rel_x_center, rel_y_center), orbit, 1)

			if planet.moons:
				moon_orbit = planet.radius + 10
				for n, (t, reversedRotation) in enumerate(planet.moons):
					n += 1 #da nebi bilo djeljenja sa 0
					t += -time.time()/n if reversedRotation else time.time()/n
					moon_x = moon_orbit * cos(t) + planet_x
					moon_y = moon_orbit * sin(t) + planet_y
					moon_size = random.randint(3,5)
					pygame.draw.circle(win, WHITE, (int(planet_x), int(planet_y)), moon_orbit, 1)
					pygame.draw.circle(win, WHITE, (int(moon_x), int(moon_y)), moon_size)
					moon_orbit += 10

			if selected:
				if (mos_x - rel_x_center)**2 + (mos_y - rel_y_center)**2 < (orbit+10)**2:
					if (mos_x - rel_x_center)**2 + (mos_y - rel_y_center)**2 > (orbit-10)**2:
						pygame.draw.circle(win, WHITE, (int(planet_x), int(planet_y)), planet.radius+3, 2)
						pygame.draw.circle(win, WHITE, (rel_x_center, rel_y_center), orbit+1, 3)

						texts = []

						texts.append(font_info.render(f"Gases: {round(planet.gases)}%", True, WHITE))
						texts.append(font_info.render(f"Minerals: {round(planet.minerals)}%", True, WHITE))
						texts.append(font_info.render(f"Resources: {round(planet.resources)}%", True, WHITE))
						texts.append(font_info.render(f"Water: {round(planet.water)}%", True, WHITE))
						texts.append(font_info.render(f"Temperature: {planet.temperature}C", True, WHITE))
						texts.append(font_info.render(f"Name: {planet.name}", True, WHITE))

						
						text_height = texts[0].get_height()
						text_offset = -text_height
						for text in texts:
							win.blit(text, (rel_x+3, height+text_offset))
							text_offset -= text_height


			pygame.draw.circle(win, BLUE if planet.water and not planet.life else GREEN if planet.life else GAS if planet.gas_giant else BROWN, 
							(int(planet_x), int(planet_y)), planet.radius)
			orbit += 45

		if clicked() == 1:
			if mos_x >= rel_x and mos_x <= rel_x+width:
				pass
			else:
				selected = False


	if clicked() == 1:
		x, y = get_mouse_in_segment()
		star = Star(x, y, False)
		if star.starExists:
			pyperclip.copy(f"{x - (SECTORS_X//2)}:{y - (SECTORS_Y//2)}")
			if not selected:
				selected = True
				selectedStar = [x,y]
	
	try:
			cords = font.render(f"X:{str(cam.x)}, Y: {str(cam.y)}", True, WHITE)
	except:
			cords = font.render(f"You are too far from the center. Don't get lost", True, WHITE)		
	fps = font.render(f"FPS: {str(int(clock.get_fps()))}", True, WHITE)
	win.blit(fps, FPS_POS)
	win.blit(cords, CORD_POS)

	pygame.display.flip()
	for event in pygame.event.get():
			if event.type == pygame.QUIT:
					running = False

pygame.quit()
quit()
