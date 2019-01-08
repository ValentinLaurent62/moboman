#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtMultimedia import QSound

#classe statique de chargement de sons.
class SoundFX():

    # Déclarer les sons
    ping = None
    anim01 = None
    musicA = None
    musicB = None

    # Initialiser les sons
    def initSounds():
        global ping, anim01, musicA, musicB
        ping = QSound("ritual/Ping.wav")
        anim01 = QSound("ritual/anim01.wav")
        musicA = QSound("ritual/track1.wav")
        musicA.setLoops(QSound.Infinite)
        musicB = QSound("ritual/track2.wav")
        musicB.setLoops(QSound.Infinite)

    # Jouer un son
    def play(name):
        global ping, anim01, music
        if name == "Ping":
            ping.play()
        elif name == "anim01":
            anim01.play()
        elif name == "musicA":
            musicA.play()
        elif name == "musicB":
            musicB.play()

    def stopMusic():
        global musicA, musicB
        musicA.stop()
        musicB.stop()