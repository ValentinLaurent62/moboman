#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import Qt, QBasicTimer
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication
from room import *
from tiles import *
from sound import *

# Classe jeu: fenêtre principale
class Game(QMainWindow):

	# Initialisation de l'objet
	def __init__(self):
		super().__init__()
		self.initUI()

	# Initialisation de l'affichage
	def initUI(self):
		# Créer la frame
		self.frame = Frame(self)
		# L'utiliser comme widger principale
		self.setCentralWidget(self.frame)
		# Taille de la fenêtre
		self.setFixedSize(640, 480)
		# Centrage
		self.center()
		# Nom de la fenêtre
		self.setWindowTitle("MOBOMAN")
		# Afficher tout
		self.show()

	# Centrer la fenêtre
	def center(self):
		screen = QDesktopWidget().screenGeometry()
		size = self.geometry()
		self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
   	 
# Classe de frame (affichage de graphismes)
class Frame(QFrame):

	def __init__(self, parent):
		super().__init__(parent)

        # Taille de l'écran
		self.screenWidth = 640
		self.screenHeight = 480

		# Tableau de touches
		self.touches = []
		
		# Charger les tuiles
		Tiles.initTiles()

		# Charger les sons
		SoundFX.initSounds()

		# Etat actuel du jeu

		self.state = TitleScreen(self)
		
		# Timer d'images par seconde
		self.timer = QBasicTimer()
		self.timer.start(16.66, self)
		
		# Forcer le focus
		self.setFocusPolicy(Qt.StrongFocus)
		
	# Tick du timer
	def timerEvent(self, event):
		self.update()
		
	# Comportement du jeu
	def update(self):
		super().update()
		self.state.update()

	# Evenement d'affichage
	def paintEvent(self, event):

		# Dessinateur
		painter = QPainter(self)

		# Rendre l'état actuel
		self.state.render(painter)

	# Detection d'appuis sur une touche
	def keyPressEvent(self, event):
		if event.key() not in self.touches:
			self.touches.append(event.key())

	# Detection Relachement d'une touche
	def keyReleaseEvent(self, event):
		if event.key() in self.touches:
			self.touches.remove(event.key())
		
	def getTouches(self):
		return self.touches


# Lancement du jeu
if __name__ == "__main__":
	app = QApplication([])
	game = Game()
	sys.exit(app.exec_())
