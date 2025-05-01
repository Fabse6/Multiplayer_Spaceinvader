import pygame                                 # Pygame für Grafik, Eingabe und Spielsteuerung
import sys                                    # Für sauberes Beenden (sys.exit)
import socket                                 # Für Netzwerkverbindung (TCP)
import pickle                                 # Für Serialisierung/Deserialisierung von Python-Objekten
import random                                 # Für zufällige Positionen der Gegner
import settings as s                          # Importiert die globalen Einstellungen (z. B. Auflösung, Farben)
from entities.player import Player            # Importiert die Spielerklasse
from entities.enemy import Enemy              # Importiere die Enemy-Klasse
from entities.bullet import Bullet            # Importiere die Bullet-Klasse

pygame.init()                                 # Initialisiert alle Pygame-Module
window = pygame.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))  # Erzeugt das Spiel-Fenster
pygame.display.set_caption("Multiplayer Space Invader")              # Setzt den Fenstertitel
clock = pygame.time.Clock()                   # Erzeugt eine Uhr zur Steuerung der Framerate

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)             # Erstellt ein TCP/IP-Socket
sock.connect(('127.0.0.1', 65432))                                   # Verbindet sich mit dem Server (hier lokal)

# Spielerobjekte werden erzeugt – Startpositionen kommen gleich vom Server
spieler = Player((0, 0), color=s.GREEN)         # Lokaler Spieler (grün)
gegner = Player((0, 0), color=s.BLUE)           # Gegner (blau)

# Erstelle eine Liste von Gegnern mit zufälligen Startpositionen
gegner_liste = [Enemy(random.randint(0, s.SCREEN_WIDTH - 40), random.randint(-300, -30)) for _ in range(5)]

# Status der Spieler (True = aktiv, False = getroffen)
spieler_status = [True, True]

# Liste für aktive Bullets
bullets = []

running = True                                  # Spielschleife aktiv
while running:
    clock.tick(s.FPS)                           # Begrenze Framerate auf z. B. 60 FPS
    window.fill(s.BLACK)                        # Füllt den Hintergrund schwarz

    for event in pygame.event.get():            # Ereignisschleife
        if event.type == pygame.QUIT:           # Wenn das Fenster geschlossen wird
            running = False                     # Spielschleife beenden
        if event.type == pygame.KEYDOWN:        # Wenn eine Taste gedrückt wird
            if event.key == pygame.K_SPACE and spieler_status[0]:  # Schieße nur, wenn Spieler 1 aktiv ist
                # Erstelle eine neue Bullet an der Position des Spielers
                bullets.append(Bullet(spieler.rect.centerx, spieler.rect.top))

    keys = pygame.key.get_pressed()             # Tastenzustand abfragen
    richtung_x = 0                              # Horizontale Bewegung
    richtung_y = 0                              # Vertikale Bewegung

    if keys[pygame.K_LEFT]:                     # Pfeiltaste links
        richtung_x = -1
    elif keys[pygame.K_RIGHT]:                  # Pfeiltaste rechts
        richtung_x = 1
    if keys[pygame.K_UP]:                       # Pfeiltaste oben
        richtung_y = -1
    elif keys[pygame.K_DOWN]:                   # Pfeiltaste unten
        richtung_y = 1

    nachricht = {"richtung_x": richtung_x, "richtung_y": richtung_y}  # Verpacke Eingabe in ein Dictionary
    sock.sendall(pickle.dumps(nachricht))       # Sende die Daten serialisiert an den Server

    daten = pickle.loads(sock.recv(2048))       # Empfange aktualisierte Positionen vom Server
    spieler.rect.topleft = daten[0]             # Setze eigene Position
    gegner.rect.topleft = daten[1]              # Setze Gegnerposition

    # Aktualisiere und zeichne alle Gegner
    for enemy in gegner_liste:
        enemy.update()
        enemy.zeichnen(window)

        # Überprüfe Kollision mit Spieler 1
        if spieler_status[0] and spieler.rect.colliderect(enemy.rect):
            spieler_status[0] = False           # Spieler 1 wurde getroffen

        # Überprüfe Kollision mit Spieler 2
        if spieler_status[1] and gegner.rect.colliderect(enemy.rect):
            spieler_status[1] = False           # Spieler 2 wurde getroffen

    # Aktualisiere und zeichne alle Bullets
    for bullet in bullets[:]:
        bullet.update()
        bullet.zeichnen(window)

        # Überprüfe Kollision mit Gegnern
        for enemy in gegner_liste:
            if bullet.rect.colliderect(enemy.rect):
                bullets.remove(bullet)          # Entferne die Bullet
                enemy.rect.y = -enemy.rect.height  # Respawne den Gegner oben
                enemy.rect.x = random.randint(0, s.SCREEN_WIDTH - enemy.rect.width)
                break                           # Verlasse die Schleife, da die Bullet bereits entfernt wurde

        # Entferne Bullets, die den oberen Bildschirmrand verlassen
        if bullet.rect.bottom < 0:
            bullets.remove(bullet)

    # Zeichne Spieler nur, wenn sie aktiv sind
    if spieler_status[0]:
        spieler.zeichnen(window)
    if spieler_status[1]:
        gegner.zeichnen(window)

    # Überprüfe, ob beide Spieler getroffen wurden
    if not any(spieler_status):                 # Wenn beide Spieler False sind
        print("Beide Spieler wurden getroffen. Spiel beendet!")
        running = False                         # Beende die Spielschleife

    pygame.display.update()                     # Aktualisiere Bildschirm

pygame.quit()                                   # Beende Pygame
sys.exit()                                      # Beende das Programm vollständig
