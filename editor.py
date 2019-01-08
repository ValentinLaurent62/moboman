#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import Qt, QModelIndex, pyqtSlot, QRect
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QFormLayout, QMainWindow, QFrame, QDesktopWidget, QApplication, QAction, QMessageBox, QFileDialog, QDockWidget, QListView, QTabWidget

from tiles import *

# Classe principale de l'éditeur
class Editor(QMainWindow):
	
	def __init__(self):
		super().__init__()
		Tiles.initTiles()
		self.initUI()
		
	# Initialisation de l'affichage
	def initUI(self):
		# Créer la frame
		self.frame = Frame(self)
		self.setCentralWidget(self.frame)

		# Taille de la fenêtreQFileDialog.getOpenFileName(self, "Ouvrir un fichier", "/home")
		self.setFixedSize(640, 480)
		# Centrage
		self.center()
		# Nom de la fenêtre
		self.setWindowTitle("Editor")

		# Menus
		mainMenu = self.menuBar()
		fileMenu = mainMenu.addMenu("Fichier")

		# Actions du menu Fichier
		self.newAction = QAction("&Nouveau", self, icon=QIcon("res/editor/new-file.png"), shortcut="Ctrl+N", statusTip="Créer une carte", triggered=self.newFile)
		self.openAction = QAction("&Ouvrir", self, icon=QIcon("res/editor/open-file.png"), shortcut="Ctrl+O", statusTip="Charger une carte", triggered=self.openFile)
		self.saveAction = QAction("&Enregistrer", self, icon=QIcon("res/editor/save.png"), shortcut="Ctrl+S", statusTip="Enregistrer", triggered=self.save)
		self.exitAction = QAction("&Quitter", self, icon=QIcon("res/editor/exit.svg"), shortcut="Alt+F4", statusTip="Quitter l'application", triggered=self.quit)
		fileMenu.addAction(self.newAction)
		fileMenu.addAction(self.openAction)
		fileMenu.addAction(self.saveAction)
		fileMenu.addAction(self.exitAction)

		# Barre latérale
		self.items = QDockWidget("Matériel", self)
		self.tabs = Sidebar(self)
		self.items.setWidget(self.tabs)
		self.items.setFloating(False)
		self.addDockWidget(Qt.RightDockWidgetArea, self.items)
		
		# Afficher tout
		self.show()

	# Centrer la fenêtre
	def center(self):
		screen = QDesktopWidget().screenGeometry()
		size = self.geometry()
		self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

	# Nouveau fichier
	def newFile(self):
		self.lsd = LevelSizeDialog(self)

	# Ouvrir un fichier
	def openFile(self):
		fname = QFileDialog.getOpenFileName(self, "Ouvrir un fichier", "res", "Carte (*.kdm)")

		if fname[0] != '':
		
			with open(fname[0], 'r') as mapr:
				mapdata=mapr.read().split()
				print(mapdata)
				w=int(mapdata[0])
				h=int(mapdata[1])

				# Taille (pixels)
				self.frame.width = w*32
				self.frame.height = h*32
				
				# Nombre de tuiles
				self.frame.tw = w
				self.frame.th = h

				#placer tuiles
				self.frame.tiles = [[0 for i in range(w)] for j in range(h)]
				for i in range(w):
					for j in range(h):
						self.frame.tiles[j][i]=int(mapdata[2+i+j*w])

				#placer objets
				if len(self.frame.sprites) > 0:
					del self.frame.sprites[:]
				for i in range(w*h+2, len(mapdata)-1, 3):
					self.frame.sprites.append( EditorSprite(mapdata[i], int(mapdata[i+1]), int(mapdata[i+2]), int(self.frame.objects[mapdata[i]][1]), int(self.frame.objects[mapdata[i]][2]), self.frame.objects[mapdata[i]][0]))
					
	# Enregistrer
	def save(self):
		fname = QFileDialog.getSaveFileName(self, "Enregistrer", "res", "Carte (*.kdm)")

		if fname[0] != '':
			with open(fname[0], 'w') as mapr:
				mapr.write(str(self.frame.tw) + ' ' + str(self.frame.th) + '\n')
				for i in range(self.frame.th):
					line = ""
					for j in range(self.frame.tw):
						line += str(self.frame.tiles[i][j]) + ' '
					mapr.write(line + '\n')

				for s in self.frame.sprites:
					mapr.write(s.type + ' ' + str(s.x) + ' ' + str(s.y) + '\n')

	# Quitter
	def quit(self):
		# Créer la boite
		msgBox = QMessageBox()
		msgBox.setText("Voulez-vous vraiment quitter?")
		msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
		msgBox.setDefaultButton(QMessageBox.Cancel)

		# L'afficher et tester quel button a été appuyé
		if msgBox.exec() == QMessageBox.Yes:
			QApplication.instance().quit()
		
class Frame(QFrame):
	
	def __init__(self, parent):
		super().__init__(parent)
		
		# Position de l'affichage
		self.x = 0
		self.y = 0
		
		# Taille de la room
		self.width = 640
		self.height = 480
		
		# Nombre de tuiles
		self.tw = self.width // 32
		self.th = self.height // 32
		
		# Tableau de touches
		self.touches = []

		# Dico des objets
		# Nom -> (image, w, h)
		self.objects = {}

		# Charger les objets
		self.loadObjects()

		# Liste de sprites
		self.sprites = []
		
		# Tableau des tuiles (contient les id des tuiles)
		# i -> colonnes
		# j -> lignes
		# utiliser self.tiles[j][i]
		self.tiles = [[0 for i in range(self.tw)] for j in range(self.th)]
		
		# Forcer le focus
		self.setFocusPolicy(Qt.StrongFocus)

		# Tuile sélectionnée
		self.currentTile = 1

		# Object sélectionné
		self.currentObject = None

		# Mode d'édition (0->tuiles, 1->objets)
		self.editMode = 0
		
		# Activer le suivi de souris
		self.setMouseTracking(True)
		
	# Detection d'appuis sur une touche
	def keyPressEvent(self, event):
		if event.key() not in self.touches:
			self.touches.append(event.key())
		self.update()

	# Detection Relachement d'une touche
	def keyReleaseEvent(self, event):
		self.touches.remove(event.key())
		self.update()
		
	# Détection clic souris
	def mousePressEvent(self, event):
		# Récupérer la position du curseur de souris sur la grille des tuiles
		mx = (event.pos().x()+self.x) // 32
		my = (event.pos().y()+self.y) // 32

		# Edition de tuiles
		if self.editMode == 0:
		
			# Clic gauche: ajouter une tuile
			if event.button() == Qt.LeftButton:
				self.tiles[my][mx] = self.currentTile
			# Clic droit: supprimer
			elif event.button() == Qt.RightButton:
				self.tiles[my][mx] = 0

		# Edition d'objets
		else:

			# Placer
			if event.button() == Qt.LeftButton:
				for s in self.sprites:
					if s.x == mx*32 and s.y == my*32:
						return
				self.sprites.append(EditorSprite(self.currentObject, mx*32, my*32, int(self.objects[self.currentObject][1]), self.objects[self.currentObject][2], self.objects[self.currentObject][0]))
		
			# Supprimer
			if event.button() == Qt.RightButton:
				for s in self.sprites:
					if s.x == mx*32 and s.y == my*32:
						self.sprites.remove(s)

		# Mettre à jour l'éditeur
		self.update()

	def loadObjects(self):
		with open("res/editor/objects.kdc", "r") as f:
			data = f.readlines()

		for line in data:
			words = line.split()
			self.objects[words[0]] = (words[1], int(words[2]), int(words[3]))
		
	def update(self):
		super().update()
		
		# Déplacement de l'affichage haut-bas
		if Qt.Key_Z in self.touches:
			self.y -= 32
		elif Qt.Key_S in self.touches:
			self.y += 32
			
		# Déplacement de l'affichage gauche-droite
		if Qt.Key_Q in self.touches:
			self.x -= 32
		elif Qt.Key_D in self.touches:
			self.x += 32
			
		# Ne pas sortir de la salle
		if self.x < 0:
			self.x = 0
		elif self.x > self.width-640:
			self.x = self.width-640
			
		if self.y < 0:
			self.y = 0
		elif self.y > self.height-480:
			self.y = self.height-480

		# Cacher/afficher la barre de tuiles
		if Qt.Key_Escape in self.touches:
			if self.parent().items.isVisible():
				self.parent().items.hide()
			else:
				self.parent().items.show()
		
	# Rendu
	def paintEvent(self, event):
		
		painter = QPainter(self)
	
		# Coordonnées pour le rendu des tuiles
		# * 0.03125 -> division par 32
		xStart = int(self.x * 0.03125)
		xEnd = min( int(xStart + (640 + 32) * 0.03125), int(self.width * 0.03125))
		yStart = int(self.y * 0.03125)
		yEnd = min( int(yStart + (480 + 32) * 0.03125), int(self.height * 0.03125))
		
		# Dessiner chaque tuile visible à l'écran
		for i in range(xStart, xEnd): # Itérer dans le tableau tuiles
			for j in range(yStart, yEnd):
				tile = self.tiles[j][i]
				if tile != 0: # Vérifier que la case n'est pas vide
					painter.drawPixmap(i * 32 - self.x, j * 32 - self.y, 32, 32, Tiles.getTile(tile))

		# Dessiner les objets
		for s in self.sprites:
			# Vérifier que le sprite est dans le champ de la caméra
			if QRect(s.x, s.y, 32, 32).intersects(QRect(self.x-32, self.y-32, self.width+32, self.height+32)):
				painter.drawPixmap(s.x - self.x, s.y - self.y, s.width, s.height, s.img)

# Classe bar latérale
class Sidebar(QTabWidget):
	def __init__(self, parent=None):
		super(Sidebar, self).__init__(parent)

		# Créer deux onglets: tuiles et objets
		self.tilesTab = QListView()
		self.objTab = QListView()
		self.addTab(self.tilesTab, "Tuiles")
		self.addTab(self.objTab, "Objets")
		self.tilesTabUI()
		self.objTabUI()

	# Initialiser l'onglet tuiles
	def tilesTabUI(self):
		self.tilesTab.setViewMode(QListView.IconMode)
		self.tabmodel = QStandardItemModel(self.tilesTab)
		self.tilesTab.clicked.connect(self.on_tileview_clicked)

		# Parcourir les tuiles disponibles
		# les ajouter à la barre
		for k,v in Tiles.tiles.items():
			item = QStandardItem()
			item.setIcon(QIcon(v))
			item.setText(str(k))
			self.tabmodel.appendRow(item)

		self.tilesTab.setModel(self.tabmodel)

	# Initialiser l'onglet objets
	def objTabUI(self):
		self.objTab.setViewMode(QListView.IconMode)
		self.objmodel = QStandardItemModel(self.objTab)
		self.objTab.clicked.connect(self.on_objview_clicked)

		# Parcourir les objets, les ajouter à la barre
		for k,v in self.parent().frame.objects.items():
			item = QStandardItem()
			item.setIcon(QIcon(v[0]))
			item.setText(k)
			self.objmodel.appendRow(item)

		self.objTab.setModel(self.objmodel)

	@pyqtSlot(QModelIndex)
	def on_tileview_clicked(self, index):
		self.parent().parent().frame.editMode = 0
		self.parent().parent().frame.currentTile = int(index.data())

	@pyqtSlot(QModelIndex)
	def on_objview_clicked(self, index):
		self.parent().parent().frame.editMode = 1
		self.parent().parent().frame.currentObject = str(index.data())

class EditorSprite():
	def __init__(self, stype, x, y, width, height, img):
		self.type = stype
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.img = QPixmap(img)

class LevelSizeDialog(QWidget):
	def __init__(self, myWin):
		super(LevelSizeDialog, self).__init__(None)
		# Récupérer l'éditeur pour lui passer des valeurs
		self.myWin = myWin

		layout = QFormLayout()
		self.setFixedSize(200, 100)

		self.wLabel = QLabel("Longueur (tuiles): ")
		self.hLabel = QLabel("Hauteur (tuiles): ")
		self.wBox = QLineEdit()
		self.hBox = QLineEdit()
		self.okButton = QPushButton("OK")
		self.cancelButton = QPushButton("Annuler")

		self.okButton.clicked.connect(self.ok)
		self.cancelButton.clicked.connect(self.cancel)

		layout.addRow(self.wLabel, self.wBox)
		layout.addRow(self.hLabel, self.hBox)
		layout.addRow(self.okButton, self.cancelButton)
		self.setLayout(layout)
		self.setWindowTitle("Nouvelle carte")

		self.show()

	def ok(self):
		
		# Nombre de tuiles
		try:
			self.myWin.frame.tw = max(20,int(self.wBox.text()))
			self.myWin.frame.th = max(15,int(self.hBox.text()))
			self.myWin.frame.width = self.myWin.frame.tw*32
			self.myWin.frame.height = self.myWin.frame.th*32
			self.myWin.frame.tiles = [[0 for i in range(self.myWin.frame.tw)] for j in range(self.myWin.frame.th)]
			if len(self.myWin.frame.sprites) > 0:
				del self.myWin.frame.sprites[:]
			self.close()
		except ValueError:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Critical)
			msg.setWindowTitle("Erreur")
			msg.setText("Valeurs incorrectes")
			msg.exec_()

	def cancel(self):
		self.close()

# Lancement de l'éditeur
if __name__ == "__main__":
	app = QApplication([])
	editor = Editor()
	sys.exit(app.exec_())