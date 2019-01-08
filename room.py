#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import subprocess
from PyQt5.QtCore import Qt, QBasicTimer
from PyQt5.QtGui import QPainter, QPixmap
from random import randint
from sprites import *
from camera import *
from tiles import *

# Pas une classroom hein x')
class Room:

    # Initialisation de la salle
    def __init__(self, frame):
        self.map=1
        self.frame=frame
        # Liste de sprites en mémoire
        self.sprites = []

        # Créer le joueur et l'ajouter dans la liste des sprites
        self.myPlayer = Player(0, 0, frame)
        self.sprites.append(self.myPlayer)
        #charger une map à partir d'un fichier.
        self.mapInit(self.map, frame)
        self.map+=1
        print(self.map)
        # Créer une caméra
        self.myCamera = Camera(self.myPlayer)
        
    # charger une nouvelle map
    def mapInit(self, number, frame):
        try:
            with open('res/maps/map'+str(number)+'.kdm', 'r') as mapr:
                mapdata=mapr.read().split()
        
            print(mapdata)
            w=int(mapdata[0])
            h=int(mapdata[1])

            #stocker le niveau d'entrée du joueur
            self.power_store=self.myPlayer.power

            # Taille (pixels)
            self.width = w*32
            self.height = h*32
            
            # Nombre de tuiles
            self.tw = w
            self.th = h

            #placer tuiles
            self.tiles = [[0 for i in range(w)] for j in range(h)]
            for i in range(w):
                for j in range(h):
                    self.tiles[j][i]=int(mapdata[2+i+j*w])

            #placer objets
            if len(self.sprites) > 0:
                del self.sprites[1:]
            for i in range(w*h+2, len(mapdata)-1, 3):
                if mapdata[i]=="Enemy":
                    self.addSprite(Enemy(int(mapdata[i+1]), int(mapdata[i+2]), frame))
                elif mapdata[i]=="Enemy2":
                    self.addSprite(Enemy2(int(mapdata[i+1]), int(mapdata[i+2]), frame))
                elif mapdata[i]=="Enemy3":
                    self.addSprite(Enemy3(int(mapdata[i+1]), int(mapdata[i+2]), frame))
                elif mapdata[i]=="Enemy4":
                    self.addSprite(Enemy4(int(mapdata[i+1]), int(mapdata[i+2]), frame))
                elif mapdata[i]=="Enemy5":
                    self.addSprite(Enemy5(int(mapdata[i+1]), int(mapdata[i+2]), frame))
                elif mapdata[i]=="Enemy6":
                    self.addSprite(Enemy6(int(mapdata[i+1]), int(mapdata[i+2]), frame))
                elif mapdata[i]=="Enemy7":
                    self.addSprite(Enemy7(int(mapdata[i+1]), int(mapdata[i+2]), frame))
                elif mapdata[i]=="Enemy8":
                    self.addSprite(Enemy8(int(mapdata[i+1]), int(mapdata[i+2]), frame))
                elif mapdata[i]=="Enemy9":
                    self.addSprite(Enemy9(int(mapdata[i+1]), int(mapdata[i+2]), frame))
                elif mapdata[i]=="Enemy10":
                    self.addSprite(Enemy10(int(mapdata[i+1]), int(mapdata[i+2]), frame))
                elif mapdata[i]=="Fin":
                    self.addSprite(Fin(int(mapdata[i+1]), int(mapdata[i+2]), frame))
                elif mapdata[i]=="Player":
                    self.myPlayer.x=int(mapdata[i+1])
                    self.myPlayer.y=int(mapdata[i+2])

            # Jouer la musique
            SoundFX.stopMusic()
            if (self.map-1) % 2 == 0:
                SoundFX.play("musicA")
            else:
                SoundFX.play("musicB")

        except:
            frame.state=Win(frame, self.myPlayer.time)
        
    # Retourner l'id de la tuile en X, Y
    def getSquare(self, x, y):
        try:
            return self.tiles[int(y//32)][int(x//32)]
        except:
            pass

    # Comportement de l'état 'Room'
    def update(self):
        #mourir
        if self.myPlayer.power<1:
            del self.sprites[1:]
            self.frame.state=Mort(self.frame)
        # Centrer la caméra sur le joueur
        self.myCamera.centerOnPlayer()

        # Comportement des sprites
        for s in self.sprites:
            # Vérifier que le sprite est dans le champ de la caméra
            if QRect(s.x, s.y, s.width, s.height).intersects(QRect(self.myCamera.x-32, self.myCamera.y-32, self.frame.screenWidth+64, self.frame.screenHeight+64)):
                s.update() # Exécuter le comportement de chaque sprite stocké en mémoire

    # Rendu de l'état 'Room'
    def render(self, painter):

        # Coordonnées pour le rendu des tuiles
        # * 0.03125 -> division par 32
        xStart = int(self.myCamera.x * 0.03125)
        xEnd = min( int(xStart + (self.myPlayer.frame.screenWidth + 32) * 0.03125), int(self.width * 0.03125))
        yStart = int(self.myCamera.y * 0.03125)
        yEnd = min( int(yStart + (self.myPlayer.frame.screenHeight + 32) * 0.03125), int(self.height * 0.03125))
        
        # Dessiner chaque tuile visible à l'écran
        for i in range(xStart, xEnd): # Itérer dans le tableau tuiles
            for j in range(yStart, yEnd):
                tile = self.tiles[j][i]
                if tile != 0: # Vérifier que la case n'est pas vide
                    painter.drawPixmap(i * 32 - self.myCamera.x, j * 32 - self.myCamera.y, 32, 32, Tiles.getTile(tile))
        
        # Dessiner chaque sprite stocké en mémoire
        for s in self.sprites:
            # Vérifier que le sprite est dans le champ de la caméra
            if QRect(s.x, s.y, s.width, s.height).intersects(QRect(self.myCamera.x-32, self.myCamera.y-32, self.width+32, self.height+32)):
                s.render(painter)
            
        # Dessiner l'interface
        self.k=10
        # sprites du hud en mémoire
        self.hud_0=QPixmap("res/hud_0.png")
        self.hud_1=QPixmap("res/hud_1.png")
        self.hud_2=QPixmap("res/hud_2.png")
        self.hud_bar_0=QPixmap("res/hud_bar_0.png")
        self.hud_bar_1=QPixmap("res/hud_bar_1.png")
        self.tir=QPixmap("res/tir.png")
        self.saut=QPixmap("res/saut.png")
        self.dash=QPixmap("res/dash.png")
        
        painter.scale(1.4,1.4)
        painter.drawPixmap(30, 39, self.saut)
        if (self.myPlayer.can_jump):
            painter.drawPixmap(39, 39, self.hud_bar_0)
        else:
            painter.drawPixmap(39, 39, self.hud_bar_1)
        painter.drawPixmap(30, 55, self.tir)
        if (self.myPlayer.can_attack):
            painter.drawPixmap(39, 55, self.hud_bar_0)
        else:
            painter.drawPixmap(39, 55, self.hud_bar_1)
        painter.drawPixmap(30, 70, self.dash)
        if (self.myPlayer.can_dash):
            painter.drawPixmap(39, 70, self.hud_bar_0)
        else:
            painter.drawPixmap(39, 70, self.hud_bar_1)
        painter.scale(1.4,1.4)
        painter.drawPixmap(self.k, 8, self.hud_0)
        self.k+=3
        for i in range (self.myPlayer.power):
            painter.drawPixmap(self.k, 8, self.hud_1)
            self.k+=4
        painter.drawPixmap(self.k, 8, self.hud_2)
        painter.drawText(QRect(0,0, self.k+16, 36), Qt.AlignRight, str(2**self.myPlayer.power))
    # Ajout d'un sprite en mémoire
    def addSprite(self, o):
        self.sprites.append(o)
    
class TitleScreen:

    #initialisation de la title.
    def __init__(self, frame):
        self.frame=frame
        self.arrow=QPixmap("res/buttons1.png")
        self.arrow_p=QPixmap("res/buttons0.png")
        self.selection=0
        self.key=True
        self.tiles = []
        self.bug_editor=False

    def update(self):
        if Qt.Key_Z in self.frame.touches and self.selection >0 and self.key:
            self.selection-=1
            self.key=False
        if Qt.Key_S in self.frame.touches and self.selection <2 and self.key:
            self.selection+=1
            self.key=False
        if Qt.Key_Z not in self.frame.touches and Qt.Key_S not in self.frame.touches:
            self.key=True

        if self.selection==0 and (Qt.Key_Enter in self.frame.touches or Qt.Key_Return in self.frame.touches or Qt.Key_K in self.frame.touches):
            self.frame.state=Room(self.frame)
        if self.selection==1 and (Qt.Key_Enter in self.frame.touches or Qt.Key_Return in self.frame.touches or Qt.Key_K in self.frame.touches):
            #le lancement bug constemment sur une de nos machines, j'ai mis une exception à celui-ci
            try:
                subprocess.call(["python3","editor.py"])
                raise SystemExit()
            except:
                self.bug_editor=True
        if self.selection==2 and (Qt.Key_Enter in self.frame.touches or Qt.Key_Return in self.frame.touches or Qt.Key_K in self.frame.touches):
            raise SystemExit()

            
    def render(self, painter):

        #quand bug d'editor détecté
        if self.bug_editor:
            painter.drawText(self.frame.screenWidth//2-200, self.frame.screenHeight//2-210,"Sorry nothing")

        painter.drawPixmap(self.frame.screenWidth//2-95,self.frame.screenHeight//2-120, self.arrow_p)
        painter.drawPixmap(self.frame.screenWidth//2-95,self.frame.screenHeight//2-90, self.arrow_p)
        painter.drawText(self.frame.screenWidth//2-80, self.frame.screenHeight//2-100,"Move: ZQSD.")
        painter.drawText(self.frame.screenWidth//2-80, self.frame.screenHeight//2-70,"Shoot: K, Dash: Space, Map reset: R.")
        painter.drawPixmap(self.frame.screenWidth//2-65,self.frame.screenHeight//2-10+(30*self.selection), self.arrow)
        painter.drawPixmap(self.frame.screenWidth//2+30,self.frame.screenHeight//2-10+(30*self.selection), self.arrow.transformed(QTransform().scale(-1, 1)))
        painter.drawText(self.frame.screenWidth//2-50, self.frame.screenHeight//2+10,"  BEGIN")
        painter.drawText(self.frame.screenWidth//2-50, self.frame.screenHeight//2+40," EDITOR")
        painter.drawText(self.frame.screenWidth//2-50, self.frame.screenHeight//2+70,"   QUIT")

    def getSquare(self, x, y):
        return self.tiles[int(y//32)][int(x//32)]
        
class Win:

    #initialisation
    def __init__(self, frame, time):
        self.time=time
        self.frame=frame
        self.arrow=QPixmap("res/buttons1.png")
        self.player=QPixmap("res/player.png")
        self.selection=0 #curseur du joueur
        self.key=True
        self.text=randint(0,2) #texte affiché
        self.tiles = []
        self.width = 0
        self.height = 0
        self.bug_editor=False
        self.myPlayer = Player(-100, -100, frame)


    def update(self):
        if Qt.Key_Z in self.frame.touches and self.selection >0 and self.key:
            self.selection-=1
            self.key=False
        if Qt.Key_S in self.frame.touches and self.selection <2 and self.key:
            self.selection+=1
            self.key=False
        if Qt.Key_Z not in self.frame.touches and Qt.Key_S not in self.frame.touches:
            self.key=True

        if self.selection==0 and (Qt.Key_Enter in self.frame.touches or Qt.Key_Return in self.frame.touches):
            self.frame.state=Room(self.frame)
        if self.selection==1 and (Qt.Key_Enter in self.frame.touches or Qt.Key_Return in self.frame.touches):
            #le lancement bug constemment sur une de nos machines, j'ai mis une exception à celui-ci
            try:
                subprocess.call(["python3","editor.py"])
                raise SystemExit()
            except:
                self.bug_editor=True
        if self.selection==2 and (Qt.Key_Enter in self.frame.touches or Qt.Key_Return in self.frame.touches):
            raise SystemExit()

    def render(self, painter):
        if self.text==0:
            painter.drawText(self.frame.screenWidth//2-60, self.frame.screenHeight//2-190,"CONGLATURATION !!!")
            painter.drawText(self.frame.screenWidth//2-60, self.frame.screenHeight//2-160,"YOU HAVE COMPLETED")
            painter.drawText(self.frame.screenWidth//2-60, self.frame.screenHeight//2-130,"   A GREAT GAME")
            painter.drawText(self.frame.screenWidth//2-60, self.frame.screenHeight//2-100,"AND PROOVED THE JUSTICE")
            painter.drawText(self.frame.screenWidth//2-60, self.frame.screenHeight//2-70,"   OF OUR CULTURE.")
            painter.drawText(self.frame.screenWidth//2-60, self.frame.screenHeight//2-40,"NOW GO AND REST OUR")
            painter.drawText(self.frame.screenWidth//2-60, self.frame.screenHeight//2-10,"      HEROES !")
        elif self.text==1:
            painter.drawText(self.frame.screenWidth//2-60, self.frame.screenHeight//2-190,"   CONGRATURATION")
            painter.drawText(self.frame.screenWidth//2-60, self.frame.screenHeight//2-160,"THIS STORY IS HAPPY END")
            painter.drawText(self.frame.screenWidth//2-60, self.frame.screenHeight//2-130,"    THANK YOU")
        elif self.text==2:
            painter.drawPixmap(self.frame.screenWidth//2-20,self.frame.screenHeight//2-190, self.player)
            painter.drawText(self.frame.screenWidth//2-60, self.frame.screenHeight//2-70,"A WINNER IS YOU")
            painter.drawText(self.frame.screenWidth//2-60, self.frame.screenHeight//2-40,"TIME   "+str(self.time//60))

        #quand bug d'editor détecté
        if self.bug_editor:
            painter.drawText(self.frame.screenWidth//2-200, self.frame.screenHeight//2-210,"Sorry nothing")

        painter.drawPixmap(self.frame.screenWidth//2-65,self.frame.screenHeight//2+50+(30*self.selection), self.arrow)
        painter.drawPixmap(self.frame.screenWidth//2+30,self.frame.screenHeight//2+50+(30*self.selection), self.arrow.transformed(QTransform().scale(-1, 1)))
        painter.drawText(self.frame.screenWidth//2-50, self.frame.screenHeight//2+70,"   AGAIN?")
        painter.drawText(self.frame.screenWidth//2-50, self.frame.screenHeight//2+100,"  EDITOR")
        painter.drawText(self.frame.screenWidth//2-50, self.frame.screenHeight//2+130,"   QUIT")

    def getSquare(self, x, y):
        return self.tiles[int(y//32)][int(x//32)]

class Mort:

    #initialisation du title.
    def __init__(self, frame):
        self.frame=frame
        self.arrow=QPixmap("res/buttons1.png")
        self.selection=0
        self.key=True
        self.tiles = []
        self.width = 0
        self.height = 0
        self.myPlayer = Player(-100, -100, frame)

    def update(self):
        if Qt.Key_Z in self.frame.touches and self.selection >0 and self.key:
            self.selection-=1
            self.key=False
        if Qt.Key_S in self.frame.touches and self.selection <1 and self.key:
            self.selection+=1
            self.key=False
        if Qt.Key_Z not in self.frame.touches and Qt.Key_S not in self.frame.touches:
            self.key=True

        if self.selection==0 and (Qt.Key_Enter in self.frame.touches or Qt.Key_Return in self.frame.touches):
            self.frame.state=Room(self.frame)
        if self.selection==1 and (Qt.Key_Enter in self.frame.touches or Qt.Key_Return in self.frame.touches):
            raise SystemExit()

    def render(self, painter):
        painter.drawPixmap(self.frame.screenWidth//2-65,self.frame.screenHeight//2-10+(60*self.selection), self.arrow)
        painter.drawPixmap(self.frame.screenWidth//2+30,self.frame.screenHeight//2-10+(60*self.selection), self.arrow.transformed(QTransform().scale(-1, 1)))
        painter.drawText(self.frame.screenWidth//2-50, self.frame.screenHeight//2+10,"   RETRY?")
        painter.drawText(self.frame.screenWidth//2-50, self.frame.screenHeight//2+70,"    QUIT")

    def getSquare(self, x, y):
        return self.tiles[int(y//32)][int(x//32)]
       
