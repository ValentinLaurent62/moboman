#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Classe de caméra, utilisée pour afficher une certaine partie d'un niveau
class Camera:
    
    # Initialiser la caméra
    def __init__(self, myPlayer):
        self.x = 0
        self.y = 0
        self.myPlayer = myPlayer # Prendre le joeur en paramètre

    # Center l'affichage autour du joueur
    def centerOnPlayer(self):

        # So smooth
        self.x += (self.myPlayer.x+16-self.myPlayer.frame.screenWidth*0.5 - self.x) * 0.06
        self.y += (self.myPlayer.y+16-self.myPlayer.frame.screenHeight*0.5 - self.y) * 0.06

        # Empêcher la caméra d'afficher une zone en dehors de la salle
        try:
            if self.x < 0:
                self.x = 0
            elif self.x > self.myPlayer.frame.state.width-640:
                    self.x = self.myPlayer.frame.state.width-640

            if self.y < 0:
                self.y = 0
            elif self.y > self.myPlayer.frame.state.height-480:
                self.y = self.myPlayer.frame.state.height-480
        except:
            pass