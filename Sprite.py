#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPixmap, QTransform
from math import degrees, radians, cos, sin, atan2

# Classe de sprite
class Sprite:
	
	# Initialiser avec le fichier d'image et la position
	def __init__(self, path, x, y, frame):
		self.img = QPixmap(path)
		self.x = x
		self.y = y
		
		# Taille du sprite
		self.width = 32
		self.height = 32
		
		# Prendre une QFrame en argument, afin de:
		# - pouvoir écouter quelles touches du clavier sont enfoncées
		# - ajouter/retirer des sprites dans la mémoire
		self.frame = frame
		
		# Initialiser le mouvement 360
		self.direction = 0
		self.speed = 0

		# Regard
		self.facing = 1
   	 
	# Comportement du sprite
	def update(self):
		pass

	# short caméra
	def getCamera(self):
		return self.frame.state.myCamera
		
	# Rendu du sprite à l'écran
	def render(self, painter):
		painter.drawPixmap(self.x - self.getCamera().x, self.y - self.getCamera().y, self.width, self.height, self.img.transformed(QTransform().scale(self.facing, 1)))
		
	# Appliquer le mouvement 360
	def move(self):
		self.x += cos(radians(self.direction)) * self.speed
		self.y += sin(radians(self.direction)) * self.speed
		
	# Retourner la direction entre deux points
	def pointDirection(self, x1, y1, x2, y2):
		return degrees(atan2(y2-y1, x2-x1))
		
	# Test de collision avec un autre sprite
	# Prend une classe en paramètre
	# Lorsqu'une collision est détectée avec une instance de cet objet, cette instance est retournée
	def checkCollision(self, sClass):
		try:
			for s in self.frame.state.sprites:
				if isinstance(s, sClass):
					if QRect(s.x, s.y, s.width, s.height).intersects(QRect(self.x+2, self.y+2, self.width-2, self.height-2)):
						return s
			return False
		except:
			pass
		
	# Destruction de l'objet: le retirer de la mémoire
	def destroy(self):
		try:
			self.frame.state.sprites.remove(self)
		except:
			pass
		
	# Ajouter un autre objet en mémoire
	def spawnObject(self, o):
		self.frame.state.addSprite(o)
		
	# Retourner la liste des touches appuyées
	def getTouches(self):
		return self.frame.getTouches()
		
	# Retourner la référence du joueur
	def getPlayer(self):
		return self.frame.state.myPlayer
		
	# Booléen: la tuile en X, Y est-elle solide?
	def isSolid(self, x, y):
		try:
			return (self.frame.state.getSquare(x, y) > 0)
		except:
			pass