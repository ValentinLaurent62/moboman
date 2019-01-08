#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPixmap
from math import degrees, radians, cos, sin, atan2
from random import randint
from Sprite import *
from sound import *

# Classe Player héritée de Sprite
class Player(Sprite):

	# Initialiser avec le fichier d'image et la position
	def __init__(self, x, y, frame):
		super().__init__("res/player.png", x, y, frame)
		self.maxV=2.6
		self.veY=0
		self.veX=0
		self.accel_generale=0.03
		self.accY=self.accel_generale
		self.accX=self.accel_generale
		self.gravity=0.1
		self.friction=0.85
		self.counterVe=0.2
		self.negater=0.05
		self.jump_cst=2
		self.can_jump=False
		self.is_jump=0
		self.jump_max=36
		self.can_attack=False
		self.Iframes=0
		self.max_frames=65
		self.can_dash=False
		self.waitdash=0
		self.time=0
		self.wait_reset=180

		# Angle de tir
		self.shootDir = 0

		# Variable utilisé pour la direction de mouvement du joueur
		# -1 pour gauche, 1 pour droite, 2 haut, 0 bas.
		self.facing = 1

		# Initialiser le nombre du joueur (puissance de 2)
		self.power = 1

		# Temps restant avant de pouvoir attaquer à nouveau
		self.waitAttack = 1

	# Comportement du joueur
	def update(self):
		#temps
		self.time+=1

		#collisions:

		# Collision avec le plafond
		if self.isSolid(self.x+4, self.y) or self.isSolid(self.x+28, self.y):
			self.can_jump=False
			self.is_jump=0
			self.veY = 0
			self.y = self.y // 32 * 32 + 32

		#collision doite:
		if self.isSolid(self.x+32, self.y) or self.isSolid(self.x+32, self.y+19) or self.checkCollision(Enemy4) or self.checkCollision(Enemy9):
			self.veX = 0
			self.x = self.x // 32 * 32

		#collision gauche	
		if self.isSolid(self.x, self.y) or self.isSolid(self.x, self.y+19) or self.checkCollision(Enemy4) or self.checkCollision(Enemy9):
			self.veX = 0
			self.x = self.x // 32 * 32 + 32

		# Appliquer la gravité
		if not self.isSolid(self.x+4, self.y+32) and not self.isSolid(self.x+28, self.y+32):
			if self.is_jump==0:
				self.can_jump = False
			self.veY+=self.gravity
			
		# Collision avec le sol
		elif not (self.veY<=0.01 and self.veY>=-0.01):
			self.veY=0
			self.y = self.y // 32 * 32

		# empêche de resauter en FP rien qu'en restant appuyé sur Z
		if Qt.Key_Z not in self.getTouches() or (self.y==self.frame.state.height - self.height - 1):
			self.can_jump = True
			self.is_jump=0
	
		# Gérer la recharge d'attaque
		if self.waitAttack > 0:
			self.waitAttack -= 1
		if self.waitAttack==0  and Qt.Key_K not in self.getTouches():
			self.can_attack=True
	
		# Saut
		# vérif saut variable, à jump_max met is_jump à 0, arrête la progression du saut.
		if self.is_jump==self.jump_max:
			self.can_jump=False
			self.is_jump=0
		# saut en lui-même
		if Qt.Key_Z in self.getTouches() and self.can_jump:
			self.veY-=(self.jump_cst*(self.jump_max-self.is_jump))/2
			self.is_jump+=1
		#viser haut/bas pendant saut
		if self.veY!=0:
			if Qt.Key_Z in self.getTouches():
				self.shootDir = 270
			if Qt.Key_S in self.getTouches():
				self.shootDir = 90

		# vitesse de chute maximale 
		if (self.veY)>self.jump_cst:
				self.veY=self.maxV*1.3
				
		# vitesse de saut maximale
		if (self.veY)<-self.jump_cst:
				self.veY=-self.jump_cst
				
		# Mouvement vertical
		self.y+=self.veY
				
		# Déplacement gauche-droite
		if (Qt.Key_Q in self.getTouches() or Qt.Key_D in self.getTouches()):
		
			# Gauche
			if Qt.Key_Q in self.getTouches():
				if self.facing==1 and self.veY == 0:
					self.veX=self.counterVe
				self.veX-=self.accX
				self.facing=-1
				self.shootDir = 180
			
			# Droite
			elif Qt.Key_D in self.getTouches():
				if self.facing==-1 and self.veY == 0:
					self.veX=-self.counterVe
				self.veX+=self.accX
				self.facing=1
				self.shootDir = 0

			# vitesse max droite/gauche
			if (self.veX+self.accX)>self.maxV and self.waitdash<=104:
				self.veX=self.maxV
			if (self.veX-self.accX)<-self.maxV and self.waitdash<=104:
				self.veX=-self.maxV

		# mouvement horizontal	
		self.x+=self.veX
		
		# réduction de vitesse par friction
		if (Qt.Key_Q not in self.getTouches() and Qt.Key_D not in self.getTouches()) and self.veY==0 and self.veX!=0:
			if self.veX<self.negater and self.veX>-self.negater:
				self.veX=0
			else:
				self.veX*=self.friction

		# Empêcher le joueur de sortir de la salle
		if self.x < 0:
			self.x = 0
		elif self.x > self.frame.state.width - self.width - 1:
			self.x = self.frame.state.width - self.width - 1
		
		if self.y < -32:
			self.y = -32
		elif self.y > self.frame.state.height - self.height - 1:
			self.y = self.frame.state.height - self.height - 1
			
		# Attaque
		if (self.can_attack) and (Qt.Key_K in self.getTouches()):
			if self.power == 11:
				self.spawnObject(Laser(self.x, self.y, self.frame, self.shootDir))
				self.waitAttack = 32
				SoundFX.play("Ping")
			else:
				self.spawnObject(ProjectileP(self.x, self.y, self.frame, self.power, self.shootDir))
				self.waitAttack = 24
				SoundFX.play("Ping")
				
			self.can_attack = False

		#recharge dash
		if self.waitdash > 0:
			self.waitdash -= 1
		if self.waitdash==0  and Qt.Key_Space not in self.getTouches():
			self.can_dash=True

		#dash
		if (self.can_dash) and (Qt.Key_Space in self.getTouches()):
			if self.facing==1:
				self.veX=self.maxV*1.4
				self.waitdash = 120
				self.can_dash = False
			elif self.facing==-1:
				self.veX=-self.maxV*1.4
				self.waitdash = 120
				self.can_dash = False
			
		# Collision avec un projectile ennemi
		if self.Iframes==0:
			p = self.checkCollision(ProjectileE) or self.checkCollision(ProjectileL)
			k = self.checkCollision(Enemy3) or self.checkCollision(Enemy5) or self.checkCollision(Enemy7) or self.checkCollision(Enemy8) or self.checkCollision(Enemy10)
			door = self.checkCollision(Enemy4) or self.checkCollision(Enemy9)
			if p:
				if p.power == self.power: # Si la puissance du projectile et celle du joueur sont égales
					self.power += 1 # Augmenter notre puissance!
				elif self.power != 0:
					self.power -= 1 # Sinon perdre en puissance
					self.Iframes=self.max_frames
				p.destroy()
			if k:
				if k.power == self.power: # Si la puissance du projectile et celle du joueur sont égales
					self.power += 1 # Augmenter notre puissance!
					k.destroy()
					SoundFX.play("anim01")
				elif self.power != 0:
					self.power -= 1 # Sinon perdre en puissance
					self.Iframes=self.max_frames
			if door and self.power==door.power:
				if door.power == self.power: # Si la puissance du projectile et celle du joueur sont égales
					self.power += 1 # Augmenter notre puissance!
				elif self.power != 0:
					self.power -= 1 # Sinon perdre en puissance
					self.Iframes=self.max_frames
				door.destroy()
				SoundFX.play("anim01")

		#Iframes
		if self.Iframes!=0:
			self.Iframes-=1


		#bouton de reset de map:
		if self.wait_reset!=0:
			self.wait_reset-=1

		if Qt.Key_R in self.getTouches() and self.wait_reset==0:
			self.getPlayer().power=self.frame.state.power_store
			self.frame.state.mapInit(self.frame.state.map-1, self.frame)
			self.wait_reset=180

	# Rendu du joueur
	def render(self, painter):
		if self.Iframes % 4 == 0: # Clignotement après dégât
			painter.drawPixmap(self.x - self.getCamera().x, self.y - self.getCamera().y, self.width, self.height, self.img.transformed(QTransform().scale(self.facing, 1)))
			
# Classe projectile joueur, héritée de Sprite
class ProjectileP(Sprite):

	# Initialiser avec le fichier d'image et la position
	def __init__(self, x, y, frame, power, direction):
		super().__init__("res/bullet.png", x, y, frame)
		self.power = power # Prend la puissance du projectile en argument (puissance de 2)
		self.direction = direction # Prend la direction de tir en argument
		self.width = 32
		self.height = 32
		self.speed = 4
		
	# Comportement du projectile
	def update(self):
	
		# Mouvement
		self.move()
		
		# Détruire en dehors de l'écran ou collision
		if self.x < self.getCamera().x - self.width or self.x > self.getCamera().x-18 + self.frame.screenWidth:
			self.destroy()
		elif self.isSolid(self.x+15, self.y+15):
			self.destroy()

# Firin my lazor
class Laser(ProjectileP):

	def __init__(self, x, y, frame, shootDir):
		super().__init__(x, y, frame, 10, 0)
		self.img = QPixmap("res/bolt.png")
		self.direction = shootDir # direction de tir
		self.ttl = 8
		self.startX = self.x
		self.startY = self.y
		self.speed = 32

	def update(self):
		# Mouvement
		self.move()

		# Détruire en dehors de l'écran
		if self.x < self.getCamera().x - self.width or self.x > self.getCamera().x-15 + self.frame.screenWidth or self.y < self.getCamera().y or self.y > self.getCamera().y+self.frame.screenHeight:
			self.destroy()
			
	def render(self, painter):
		if self.direction == 0:
			for parcours in range(int(self.startX)+32, int(self.x)+32, 32):
				painter.drawPixmap(parcours - self.getCamera().x, self.y - self.getCamera().y, self.width, self.height, self.img)
		elif self.direction == 180:
			for parcours in range(int(self.x), int(self.startX), 32):
				painter.drawPixmap(parcours - self.getCamera().x, self.y - self.getCamera().y, self.width, self.height, self.img)
		elif self.direction == 90:
			for parcours in range(int(self.startY)+32, int(self.y), 32):
				painter.drawPixmap(self.x - self.getCamera().x, parcours - self.getCamera().y, self.width, self.height, self.img.transformed(QTransform().rotate(90)))
		else:
			for parcours in range(int(self.y), int(self.startY), 32):
				painter.drawPixmap(self.x - self.getCamera().x, parcours - self.getCamera().y, self.width, self.height, self.img.transformed(QTransform().rotate(90)))
			
# Classe ennemi, héritée de Sprite
class Enemy(Sprite):

	def __init__(self, x, y, frame):
		super().__init__("res/adude.png", x, y, frame)
		self.waitShoot = 1 # Attente avant d'attaquer
		self.power = 1    # Nombre de l'ennemi (puissance de 2)
		self.width = 32
		self.height = 64
		self.speed = 0.2
		self.direction = 0

	# Comportement de l'ennemi
	def update(self):
		
		# Décrémenter le temps pour tourner
		self.waitShoot -= 1

		# Tirer
		if self.waitShoot == 0:
			SoundFX.play("Ping")
			self.spawnObject(ProjectileE(self.x, self.y, self.frame, self.power, self.pointDirection(self.x, self.y, self.getPlayer().x, self.getPlayer().y)))
			self.waitShoot = 180

		# Regarder le joueur
		if self.getPlayer().x < self.x:
			self.facing = 1
		else:
			self.facing = -1
			
		# Mouvement
		self.direction = self.pointDirection(self.x, self.y, self.getPlayer().x, self.getPlayer().y)
		self.move()
		
		# Collision avec un projectile du joueur
		p = self.checkCollision(ProjectileP)
		if p != False:
			SoundFX.play("anim01")
			p.destroy()
			self.destroy()
	
			
class Enemy2(Sprite):

	def __init__(self, x, y, frame):
		super().__init__("res/drone.png", x, y, frame)
		self.waitMove = 60 # Attente avant de se retourner
		self.power = 3    # Nombre de l'ennemi (puissance de 2)
		self.facing = -1   # Direction de mouvement
		self.width = 32
		self.height = 32
		self.hp=self.power



	# Comportement de l'ennemi
	def update(self):

		# Décrémenter le temps pour tourner
		if self.waitMove > 0:
			self.waitMove -= 1
		if self.waitMove==0:
			self.facing = -self.facing

		# Se retourner
		if self.waitMove == 0:
			self.spawnObject(ProjectileE2(randint(self.x-64, self.x+128), randint(self.y-64, self.y+128), self.frame, self.power, self.pointDirection(self.x, self.y, self.getPlayer().x, self.getPlayer().y)))
			self.waitMove=180

		# Mouvement
		self.x += self.facing

		# Collision avec un projectile du joueur
		p = self.checkCollision(ProjectileP)
		if p != False:
			self.hp-=p.power
			if self.hp<1:
				self.destroy()
			p.destroy()

# Classe projectile ennemi, héritée de Sprite
class ProjectileE2(Sprite):

	# Initialiser avec le fichier d'image et la position
	def __init__(self, x, y, frame, power, direction):
		super().__init__("res/attaque.png", x, y, frame)
		self.power = power # Prend la puissance du projectile en argument (puissance de 2)
		self.direction = self.pointDirection(self.x, self.y, self.getPlayer().x, self.getPlayer().y)
		self.speed = 4
		self.width = 32
		self.height = 32
		self.wait=70
		
	# Comportement du projectile
	def update(self):
	
		# Mouvement
		if self.wait>0:
			self.wait-=1
		else:
			self.spawnObject(ProjectileE(self.x, self.y, self.frame, self.power, self.direction))
			self.destroy()
		
		# Détruire en dehors de l'écran
		if self.x < self.getCamera().x-self.width or self.x > self.getCamera().x+self.frame.screenWidth:
			self.destroy()
		
	# Afficher la puissance du projectile
	def render(self, painter):
		super().render(painter)
		painter.drawText(QRect(self.x - self.getCamera().x, self.y - self.getCamera().y, self.width, self.height), Qt.AlignCenter, str(2**self.power))

# Classe projectile ennemi, héritée de Sprite
class ProjectileE(Sprite):

	# Initialiser avec le fichier d'image et la position
	def __init__(self, x, y, frame, power, direction):
		super().__init__("res/bullet.png", x, y, frame)
		self.power = power # Prend la puissance du projectile en argument (puissance de 2)
		self.direction = direction
		self.speed = 4
		self.width = 32
		self.height = 32
		
	# Comportement du projectile
	def update(self):
	
		# Mouvement
		self.move()
		
		# Détruire en dehors de l'écran ou collision
		if self.x < self.getCamera().x - self.width or self.x > self.getCamera().x + self.frame.screenWidth:
			self.destroy()
		if self.isSolid(self.x+15, self.y+15):
			self.destroy()

		
	# Afficher la puissance du projectile
	def render(self, painter):
		super().render(painter)
		painter.drawText(QRect(self.x - self.getCamera().x, self.y - self.getCamera().y, self.width, self.height), Qt.AlignCenter, str(2**self.power))

#Enemy3, le petit nouveau.
class Enemy3(Sprite):

	def __init__(self, x, y, frame):
		super().__init__("res/LED_Green.png", x, y, frame)
		self.waitMove = 1 # Attente avant de se retourner
		self.power = 2    # Nombre de l'ennemi (puissance de 2)
		self.facing = -1   # Direction de mouvement
		self.width = 32
		self.height = 32
		self.hp = self.power

	# Comportement de l'ennemi
	def update(self):
		
		# Décrémenter le temps pour tourner

		# Appliquer la gravité
		if not self.isSolid(self.x+4, self.y+32) and not self.isSolid(self.x+28, self.y+32):
			self.y+=3

		# Se retourner à collision ou fin de map:
		if self.x < 1:
			self.facing = -self.facing
		elif self.x > self.frame.state.width - self.width - 1:
			self.facing = -self.facing
		if self.isSolid(self.x, self.y) or self.isSolid(self.x+31, self.y):
			self.facing = -self.facing

		# Mouvement
		self.x += 1.7*self.facing
		
		# Collision avec un projectile du joueur
		p = self.checkCollision(ProjectileP)
		if p != False:
			self.hp-=p.power
			if self.hp<1:
				self.destroy()
			p.destroy()

	#afficher puissance
	def render(self, painter):
		super().render(painter)
		painter.drawText(QRect(self.x - self.getCamera().x, self.y - self.getCamera().y -20, self.width, self.height), Qt.AlignCenter, str(2**self.power))

#enemy4, le premier mur.
class Enemy4(Sprite):

	def __init__(self, x, y, frame):
		super().__init__("res/USB_Key.png", x, y, frame)
		self.power = 4    # Nombre de l'ennemi (puissance de 2)
		self.width = 32
		self.height = 64

	# Comportement de l'ennemi
	def update(self):
		
		# Collision avec un projectile du joueur
		k = self.checkCollision(Laser)
		if k != False:
			self.destroy()
		p = self.checkCollision(ProjectileP)
		if p != False:
			p.destroy()


	#afficher puissance
	def render(self, painter):
		super().render(painter)
		painter.drawText(QRect(self.x - self.getCamera().x, self.y - self.getCamera().y, self.width, self.height), Qt.AlignCenter, str(2**self.power))

# Enemy5, clé usb agressive
class Enemy5(Sprite):

	def __init__(self, x, y, frame):
		super().__init__("res/USB_Key_A.png", x, y, frame)
		self.power = 5    # Nombre de l'ennemi (puissance de 2)
		self.width = 32
		self.height = 64

		self.veX = 0
		self.veY = 0
		self.gravity = 0.1

		self.waitJump = 120
		
		self.hp = self.power

	# Comportmeent de l'ennemi
	def update(self):

		if self.x < self.getPlayer().x:
			self.facing = 1
		else:
			self.facing = -1

		# Collision avec le plafond
		if self.isSolid(self.x+4, self.y) or self.isSolid(self.x+28, self.y):
			self.can_jump=False
			self.is_jump=0
			self.veY = 0
			self.y = self.y // 32 * 32 + 32

		#collision doite:
		if self.veX > 0 and (self.isSolid(self.x+32, self.y+32) or self.isSolid(self.x+32, self.y+51)):
			self.veX = 0
			self.x = self.x // 32 * 32

		#collision gauche	
		if self.veX < 0 and (self.isSolid(self.x, self.y+32) or self.isSolid(self.x, self.y+51)):
			self.veX = 0
			self.x = self.x // 32 * 32 + 32

		# Appliquer la gravité
		if not self.isSolid(self.x+4, self.y+64) and not self.isSolid(self.x+28, self.y+64):
			self.veY+=self.gravity
			
		# Collision avec le sol
		elif self.veY >= 0:
			self.veY = 0
			self.veX = 0
			self.y = self.y // 32 * 32
			
		if self.veY > 3:
			self.veY = 3

		# Mouvement horizontal
		self.x += self.veX

		# Mouvement vertical
		self.y += self.veY

		# Saut
		if self.waitJump > 0:
			self.waitJump -= 1
		elif self.veY == 0:
			self.veY = -4
			self.veX = 1.5*self.facing
			self.waitJump = 180
			
	# Collision avec un projectile du joueur
		p = self.checkCollision(ProjectileP)
		if p != False:
			self.hp-=p.power
			if self.hp<1:
				self.destroy()
				SoundFX.play("anim01")
			p.destroy()

	#afficher puissance
	def render(self, painter):
		super().render(painter)
		painter.drawText(QRect(self.x - self.getCamera().x, self.y - self.getCamera().y, self.width, self.height), Qt.AlignCenter, str(2**self.power))

# Tank!
class Enemy6(Sprite):

	def __init__(self, x, y, frame):
		super().__init__("res/tank.png", x, y, frame)
		self.waitShoot = 1 # Attente avant d'attaquer
		self.power = 6    # Nombre de l'ennemi (puissance de 2)
		self.width = 32
		self.height = 32
		self.speed = 0.4
		self.direction = 0
		self.life=self.power

	# Comportement de l'ennemi
	def update(self):
		
		# Décrémenter le temps pour tourner
		self.waitShoot -= 1

		# Tirer
		if self.waitShoot == 0:
			SoundFX.play("Ping")
			self.spawnObject(ProjectileE(self.x, self.y, self.frame, self.power, (self.facing==1)*180))
			self.waitShoot = 180

		# Regarder le joueur
		if self.getPlayer().x < self.x:
			self.facing = 1
		else:
			self.facing = -1
			
		# Mouvement
		self.direction = self.pointDirection(self.x, self.y, self.getPlayer().x, self.getPlayer().y)
		self.move()
		
		# Collision avec un projectile du joueur
		p = self.checkCollision(ProjectileP)
		if p != False:
			self.life-=p.power
			p.destroy()
		if self.life<1:
			SoundFX.play("anim01")
			self.destroy()

# Enemy7, microchip
class Enemy7(Sprite):

	def __init__(self, x, y, frame):
		super().__init__("res/Microchip.png", x, y, frame)
		self.power = 7    # Nombre de l'ennemi (puissance de 2)
		self.width = 64
		self.height = 64

		self.veX = 0
		self.veY = 0
		self.gravity = 0.1
		
		self.hp = self.power

	def update(self):

		if self.x < self.getPlayer().x:
			self.facing = 1
		else:
			self.facing = -1

		# Détruire les briques
		if self.frame.state.getSquare(self.x, self.y) == 2:
			self.frame.state.tiles[int(self.y//32)][int(self.x//32)] = 0
		if self.frame.state.getSquare(self.x, self.y+32) == 2:
			self.frame.state.tiles[int((self.y+32)//32)][int(self.x//32)] = 0
		if self.frame.state.getSquare(self.x+64, self.y) == 2:
			self.frame.state.tiles[int(self.y//32)][int((self.x+64)//32)] = 0
		if self.frame.state.getSquare(self.x+64, self.y+32) == 2:
			self.frame.state.tiles[int((self.y+32)//32)][int((self.x+64)//32)] = 0

		# Collision avec le plafond
		if self.isSolid(self.x+4, self.y) or self.isSolid(self.x+62, self.y):
			self.can_jump=False
			self.is_jump=0
			self.veY = 0
			self.y = self.y // 32 * 32 + 32

		#collision doite:
		if self.veX > 0 and (self.isSolid(self.x+64, self.y) or self.isSolid(self.x+64, self.y+32) or self.isSolid(self.x+64, self.y+51)):
			self.veX = 0
			self.x = self.x // 32 * 32
			if self.veY == 0:
				self.veY = -2

		#collision gauche	
		if self.veX < 0 and (self.isSolid(self.x, self.y) or self.isSolid(self.x, self.y+32) or self.isSolid(self.x, self.y+51)):
			self.veX = 0
			self.x = self.x // 32 * 32 + 32
			if self.veY == 0:
				self.veY = -2

		# Appliquer la gravité
		if not self.isSolid(self.x+4, self.y+64) and not self.isSolid(self.x+32, self.y+64) and not self.isSolid(self.x+62, self.y+64):
			self.veY+=self.gravity
			
		# Collision avec le sol
		elif self.veY >= 0:
			self.veY = 0
			self.veX = 0
			self.y = self.y // 32 * 32
			
		if self.veY > 3:
			self.veY = 3

		# Pourchasser le joueur
		self.veX = 1*self.facing

		# Mouvement horizontal
		self.x += self.veX

		# Mouvement vertical
		self.y += self.veY
		
	# Collision avec un projectile du joueur
		p = self.checkCollision(ProjectileP)
		if p != False:
			self.hp-=p.power
			if self.hp<1:
				self.destroy()
				SoundFX.play("anim01")
			p.destroy()

	#afficher puissance
	def render(self, painter):
		super().render(painter)
		painter.drawText(QRect(self.x - self.getCamera().x, self.y - self.getCamera().y, self.width, self.height), Qt.AlignCenter, str(2**self.power))

#enemy8, une mouche très embêtante.
class Enemy8(Sprite):

	def __init__(self, x, y, frame):
		super().__init__("res/ultimate_dood.png", x, y, frame)
		self.waitShoot = 180 # Attente avant d'attaquer
		self.power = 8    # Nombre de l'ennemi (puissance de 2)
		self.width = 32
		self.height = 80
		self.speed = 1
		self.direction = 0
		self.high=1
		self.hp = self.power

	# Comportement de l'ennemi
	def update(self):
		
		# Décrémenter le temps pour tourner

		# Tourner

		# Regarder le joueur
		if self.getPlayer().x < self.x:
			self.facing = 1
		else:
			self.facing = -1
		self.facing*0.07

		if self.getPlayer().y < self.y:
			self.high = 1
		else:
			self.high = -1
			
		# Mouvement
		self.direction = self.pointDirection(self.x, self.y, self.getPlayer().x, self.getPlayer().y)
		self.x-=self.facing
		self.y-=self.facing
		self.move()
		
		# Collision avec un projectile du joueur
		p = self.checkCollision(ProjectileP)
		if p != False:
			self.hp-=p.power
			if self.hp<1:
				self.destroy()
			p.destroy()

#enemy9, le deuxième mur.
class Enemy9(Sprite):

	def __init__(self, x, y, frame):
		super().__init__("res/final_door.png", x, y, frame)
		self.power = 9    # Nombre de l'ennemi (puissance de 2)
		self.width = 32
		self.height = 64
		self.waitMove=180

	# Comportement de l'ennemi
	def update(self):
		
		# Collision avec un projectile du joueur
		p = self.checkCollision(ProjectileP)
		if p != False:
			p.destroy()

		#attaquer
		if self.waitMove > 0:
			self.waitMove -= 1
		if self.waitMove == 0:
			self.spawnObject(ProjectileE9(randint(self.x-64, self.x+128), randint(self.y-64, self.y+128), self.frame, self.power, self.pointDirection(self.x, self.y, self.getPlayer().x, self.getPlayer().y)))
			self.waitMove=180
		

	#afficher puissance
	def render(self, painter):
		super().render(painter)
		painter.drawText(QRect(self.x - self.getCamera().x, self.y - self.getCamera().y, self.width, self.height), Qt.AlignCenter, str(2**self.power))

# Classe projectile ennemi9, héritée de Sprite
class ProjectileE9(Sprite):

	# Initialiser avec le fichier d'image et la position
	def __init__(self, x, y, frame, power, direction):
		super().__init__("res/attaque_A.png", x, y, frame)
		self.power = power # Prend la puissance du projectile en argument (puissance de 2)
		self.direction = self.pointDirection(self.x, self.y, self.getPlayer().x, self.getPlayer().y)
		self.speed = 4
		self.width = 32
		self.height = 32
		self.wait=180
		
	# Comportement du projectile
	def update(self):
	
		# Mouvement
		if self.wait>0:
			self.wait-=1
		if self.wait<=60:
			self.spawnObject(ProjectileL(self.x, self.y, self.frame, self.power, self.direction))
		if self.wait==0:
			self.destroy()
		
		# Détruire en dehors de l'écran
		if self.x < self.getCamera().x-self.width or self.x > self.getCamera().x+self.frame.screenWidth:
			self.destroy()
		
	# Afficher la puissance du projectile
	def render(self, painter):
		super().render(painter)
		painter.drawText(QRect(self.x - self.getCamera().x, self.y - self.getCamera().y, self.width, self.height), Qt.AlignCenter, str(2**self.power))

# Firin my lazor, version enemy9
class ProjectileL(ProjectileE):

	def __init__(self, x, y, frame, power, facing):
		super().__init__(x, y, frame, 10, 0)
		self.img = QPixmap("res/bolt.png")
		self.facing = facing
		self.ttl = 60
		self.startX = self.x

	def update(self):
		# Mouvement
		if self.facing==0:
			self.y+=32
		if self.facing==2:
			self.y-=32
		else:
			self.x += 32*self.facing

		# Détruire en dehors de l'écran
		if self.x < self.getCamera().x - self.width or self.x > self.getCamera().x-15 + self.frame.screenWidth:
			self.destroy()
			
	def render(self, painter):
		if self.facing == 1:
			for parcours in range(int(self.startX)+32, int(self.x), 32):
				painter.drawPixmap(parcours - self.getCamera().x, self.y - self.getCamera().y, self.width, self.height, self.img)
		else:
			for parcours in range(int(self.x), int(self.startX), 32):
				painter.drawPixmap(parcours - self.getCamera().x, self.y - self.getCamera().y, self.width, self.height, self.img)

#sprite de fin de niveau
class Fin(Sprite):

	def __init__(self, x, y, frame):
		super().__init__("res/dood.png", x, y, frame)
		self.width = 32
		self.height = 32

	# Comportement de l'ennemi
	def update(self):
		
		# Collision avec un projectile du joueur
		p = self.checkCollision(Player)
		if p != False:
			self.frame.state.mapInit(self.frame.state.map, self.frame)
			try:
				self.frame.state.map+=1
			except:
				pass

#1024
class Enemy10(Sprite):

	def __init__(self, x, y, frame):
		super().__init__("res/1024.png", x, y, frame)
		self.power=10
		self.width = 32
		self.height = 32

	# Comportement de l'ennemi
	def update(self):
		pass