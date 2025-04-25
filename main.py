import pygame                                 # Pygame für Grafik, Eingabe und Spielsteuerung
import sys                                    # Für sauberes Beenden (sys.exit)
import socket                                 # Für Netzwerkverbindung (TCP)
import pickle                                 # Für Serialisierung/Deserialisierung von Python-Objekten
import settings as s                          # Importiert die globalen Einstellungen (z. B. Auflösung, Farben)
from entities.player import Player            # Importiert die Spielerklasse

pygame.init()                                 # Initialisiert alle Pygame-Module
window = pygame.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))  # Erzeugt das Spiel-Fenster
pygame.display.set_caption("Multiplayer Space Invader")              # Setzt den Fenstertitel
clock = pygame.time.Clock()                   # Erzeugt eine Uhr zur Steuerung der Framerate

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)             # Erstellt ein TCP/IP-Socket
sock.connect(('127.0.0.1', 65432))                                   # Verbindet sich mit dem Server (hier lokal)

# Spielerobjekte werden erzeugt – Startpositionen kommen gleich vom Server
spieler = Player((0, 0), color=s.GREEN)         # Lokaler Spieler (grün)
gegner = Player((0, 0), color=s.BLUE)           # Gegner (blau)

running = True                                  # Spielschleife aktiv
while running:
    clock.tick(s.FPS)                           # Begrenze Framerate auf z. B. 60 FPS
    window.fill(s.BLACK)                        # Füllt den Hintergrund schwarz

    for event in pygame.event.get():            # Ereignisschleife
        if event.type == pygame.QUIT:           # Wenn das Fenster geschlossen wird
            running = False                     # Spielschleife beenden

    keys = pygame.key.get_pressed()             # Tastenzustand abfragen
    richtung = 0                                # Standard: keine Bewegung
    if keys[pygame.K_LEFT]:                     # Pfeiltaste links
        richtung = -1
    elif keys[pygame.K_RIGHT]:                  # Pfeiltaste rechts
        richtung = 1

    nachricht = {"richtung": richtung}          # Verpacke Eingabe in ein Dictionary
    sock.sendall(pickle.dumps(nachricht))       # Sende die Daten serialisiert an den Server

    daten = pickle.loads(sock.recv(2048))       # Empfange aktualisierte Positionen vom Server
    spieler.rect.topleft = daten[0]             # Setze eigene Position
    gegner.rect.topleft = daten[1]              # Setze Gegnerposition

    spieler.zeichnen(window)                    # Zeichne eigenen Spieler
    gegner.zeichnen(window)                     # Zeichne Gegner
    pygame.display.update()                     # Aktualisiere Bildschirm

pygame.quit()                                   # Beende Pygame
sys.exit()                                      # Beende das Programm vollständig
