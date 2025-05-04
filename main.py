import pygame                                 # Pygame für Grafik, Eingabe und Spielsteuerung
import sys                                    # Für sauberes Beenden (sys.exit)
import socket                                 # Für Netzwerkverbindung (TCP)
import pickle                                 # Für Serialisierung/Deserialisierung von Python-Objekten
import settings as s                          # Importiert die globalen Einstellungen (z. B. Auflösung, Farben)
from entities.player import Player            # Importiert die Spielerklasse
from entities.bullet import Bullet            # Importiert die Bullet-Klasse
from entities.enemy import Enemy              # Importiert die Enemy-Klasse

pygame.init()                                 # Initialisiert alle Pygame-Module
window = pygame.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))  # Erzeugt das Spiel-Fenster
pygame.display.set_caption("Multiplayer Space Invader")              # Setzt den Fenstertitel
clock = pygame.time.Clock()                   # Erzeugt eine Uhr zur Steuerung der Framerate

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)             # Erstellt ein TCP/IP-Socket
sock.connect(('127.0.0.1', 65432))                                   # Verbindet sich mit dem Server (hier lokal)

# Warte-Bildschirm anzeigen
font = pygame.font.Font(None, 36)  # Schriftart und -größe
waiting_text = font.render("Warte auf zweiten Spieler...", True, s.WHITE)  # Text rendern
waiting_rect = waiting_text.get_rect(center=(s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2))  # Zentriere den Text

waiting = True
while waiting:
    window.fill(s.BLACK)  # Hintergrund schwarz
    window.blit(waiting_text, waiting_rect)  # Text auf den Bildschirm zeichnen
    pygame.display.update()  # Bildschirm aktualisieren

    try:
        daten = pickle.loads(sock.recv(2048))  # Warte auf Startsignal vom Server
        if daten.get("start"):  # Wenn das Startsignal empfangen wird
            waiting = False  # Warte-Bildschirm verlassen
    except (ConnectionResetError, EOFError, pickle.UnpicklingError):
        print("Verbindung zum Server verloren.")
        pygame.quit()
        sys.exit()

# Spielerobjekte werden erzeugt – Startpositionen kommen gleich vom Server
spieler = [Player((0, 0), color=s.GREEN), Player((0, 0), color=s.BLUE)]  # Zwei Spielerobjekte
gegner = [Enemy(0, 0) for _ in range(5)]        # Platzhalter für Gegner
bullets = []                                    # Liste für Bullets

running = True  # Spielschleife aktiv
while running:
    clock.tick(s.FPS)  # Begrenze Framerate auf z. B. 60 FPS
    window.fill(s.BLACK)  # Füllt den Hintergrund schwarz

    for event in pygame.event.get():  # Ereignisschleife
        if event.type == pygame.QUIT:  # Wenn das Fenster geschlossen wird
            running = False  # Spielschleife beenden

    keys = pygame.key.get_pressed()  # Tastenzustand abfragen
    richtung = [0, 0]  # Standard: keine Bewegung
    if keys[pygame.K_LEFT]:  # Pfeiltaste links
        richtung[0] = -1
    elif keys[pygame.K_RIGHT]:  # Pfeiltaste rechts
        richtung[0] = 1
    if keys[pygame.K_UP]:  # Pfeiltaste oben
        richtung[1] = -1
    elif keys[pygame.K_DOWN]:  # Pfeiltaste unten
        richtung[1] = 1

    schuss = keys[pygame.K_SPACE]  # Schuss-Taste (Leertaste)

    nachricht = {"richtung": richtung, "schuss": schuss}  # Verpacke Eingabe in ein Dictionary
    sock.sendall(pickle.dumps(nachricht))  # Sende die Daten serialisiert an den Server

    daten = pickle.loads(sock.recv(2048))  # Empfange aktualisierte Positionen vom Server
    if daten.get("game_over"):  # Prüfe, ob das Spiel beendet werden soll
        print("Spiel beendet! Ein Spieler wurde getroffen.")
        running = False  # Beende die Spielschleife
        break

    spieler_daten = daten["spieler"]  # Daten der Spieler
    gegner_daten = daten["gegner"]  # Daten der Gegner
    bullets_daten = daten["bullets"]  # Daten der Bullets

    # Aktualisiere Spielerpositionen
    for i, spieler_obj in enumerate(spieler):
        spieler_obj.rect.topleft = spieler_daten[i]
        spieler_obj.zeichnen(window)

    # Aktualisiere und zeichne Gegner
    for i, gegner_obj in enumerate(gegner):
        gegner_obj.rect.topleft = (gegner_daten[i]["x"], gegner_daten[i]["y"])
        gegner_obj.zeichnen(window)

    # Aktualisiere und zeichne Bullets
    bullets.clear()
    for bullet_data in bullets_daten:
        bullet = Bullet(bullet_data["x"], bullet_data["y"])
        bullets.append(bullet)
        bullet.zeichnen(window)

    pygame.display.update()  # Aktualisiere Bildschirm

pygame.quit()  # Beende Pygame
sys.exit()  # Beende das Programm vollständig
