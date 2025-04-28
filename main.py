import pygame                                 # Pygame für Grafik, Eingabe und Spielsteuerung
import sys                                    # Für sauberes Beenden (sys.exit)
import socket                                 # Für Netzwerkverbindung (TCP)
import pickle                                 # Für Serialisierung/Deserialisierung von Python-Objekten
import settings as s                          # Importiert die globalen Einstellungen (z. B. Auflösung, Farben)
from entities.player import Player            # Importiert die Spielerklasse
import random
from entities.enemy import Enemy
from entities.menu import Menu                # Importiert die Menüklasse

pygame.init()                                 # Initialisiert alle Pygame-Module
window = pygame.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))  # Erzeugt das Spiel-Fenster
pygame.display.set_caption("Multiplayer Space Invader")              # Setzt den Fenstertitel
clock = pygame.time.Clock()                   # Erzeugt eine Uhr zur Steuerung der Framerate

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)             # Erstellt ein TCP/IP-Socket
sock.connect(('192.168.178.95', 65432))                                   # Verbindet sich mit dem Server (hier lokal)

# Spielerobjekte werden erzeugt – Startpositionen kommen gleich vom Server
spieler = Player((100, s.SCREEN_HEIGHT - 40), color=s.GREEN) 
spieler2 = Player((200, s.SCREEN_HEIGHT - 40), color=s.RED) 
spieler3 = Player((300, s.SCREEN_HEIGHT - 40), color=s.YELLOW)         # Lokaler Spieler (grün)
gegner = Player((400, s.SCREEN_HEIGHT - 40), color=s.BLUE)           # Gegner (blau)

# Erstelle Gegner
gegner_liste = [Enemy(random.randint(0, s.SCREEN_WIDTH - 50), random.randint(-200, -50)) for _ in range(5)]

score = 0  # Initialisiere den Score

# Initialisiere das Menü
menu = Menu(window)

# Zeige das Menü am Anfang des Spiels
menu.anzeigen()

running = True                                  # Spielschleife aktiv
while running:
    clock.tick(s.FPS)                           # Begrenze Framerate auf z. B. 60 FPS
    window.fill(s.BLACK)                        # Füllt den Hintergrund schwarz

    for event in pygame.event.get():            # Ereignisschleife
        if event.type == pygame.QUIT:           # Wenn das Fenster geschlossen wird
            running = False                     # Spielschleife beenden

    # Bewegungseingaben verarbeiten
    keys = pygame.key.get_pressed()             # Tastenzustand abfragen
    richtung_x = 0                              # Standard: keine Bewegung
    richtung_y = 0
    if keys[pygame.K_LEFT]:                     # Pfeiltaste links
        richtung_x = -1
    elif keys[pygame.K_RIGHT]:                  # Pfeiltaste rechts
        richtung_x = 1
    if keys[pygame.K_UP]:                       # Pfeiltaste oben
        richtung_y = -1
    elif keys[pygame.K_DOWN]:                   # Pfeiltaste unten
        richtung_y = 1

    # Spieler bewegen
    if spieler.alive:
        spieler.bewegen(richtung_x, richtung_y)

    # Gegner aktualisieren und zeichnen
    for gegner in gegner_liste:
        gegner.update()
        gegner.zeichnen(window)

        # Pixelgenaue Kollision zwischen Spieler und Gegner prüfen
        if spieler.alive and pygame.sprite.collide_mask(spieler, gegner):
            spieler.alive = False  # Spieler wird getroffen

    # Spieler zeichnen
    spieler.zeichnen(window)

    # Score erhöhen, wenn der Spieler lebt
    if spieler.alive:
        score += 1

    # Prüfen, ob alle Spieler getroffen wurden
    if not spieler.alive:
        if all(not g.alive for g in [spieler2, spieler3]):  # Beispiel für mehrere Spieler
            menu.anzeigen("All players are dead. Press ENTER to Restart")
            # Spiel zurücksetzen
            score = 0
            spieler.alive = True
            spieler2.alive = True
            spieler3.alive = True
            for gegner in gegner_liste:
                gegner.rect.y = random.randint(-200, -50)  # Gegner neu positionieren

    # Score anzeigen
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, s.WHITE)
    window.blit(score_text, (10, 10))

    pygame.display.update()                     # Aktualisiere Bildschirm

pygame.quit()                                   # Beende Pygame
sys.exit()                                      # Beende das Programm vollständig
