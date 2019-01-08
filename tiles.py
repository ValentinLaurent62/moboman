#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtGui import QPixmap

# Classe statique contenant les tuiles
class Tiles:

    # Définir chaque tuile
    tiles = {}

    def loadTiles():

        with open("res/editor/tiles.kdc", "r") as f:
            data = f.readlines()

        return data

    # Initialiser les tuiles
    def initTiles():
        data = Tiles.loadTiles()
        numbSolid = 0
        numbBackg = 0
        for line in data:
            words = line.split()
            if words[1] == "true":
                numbSolid += 1
                Tiles.tiles[numbSolid] = QPixmap(words[0])
            else:
                numbBackg -= 1
                Tiles.tiles[numbBackg] = QPixmap(words[0])
    
    # Récupérer une tuile par son id
    def getTile(n):
        try:
            return Tiles.tiles[n]
        except KeyError:
            print("Warning: unknown texture id:", n)
            return QPixmap("res/err.png")