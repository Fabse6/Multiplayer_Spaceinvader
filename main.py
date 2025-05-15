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

def zeige_bereit_button(sock):
    """Zeigt den Bereit-Button an und ändert die Farbe, wenn der Spieler bereit ist."""
    font = pygame.font.Font(None, 36)
    waiting_text = font.render("Bereit?", True, s.WHITE)
    button_color = s.BLUE
    button_rect = pygame.Rect(s.SCREEN_WIDTH // 2 - 100, s.SCREEN_HEIGHT // 2 - 25, 200, 50)
    bereit = False

    while not bereit:
        window.fill(s.BLACK)
        pygame.draw.rect(window, button_color, button_rect)
        window.blit(waiting_text, waiting_text.get_rect(center=button_rect.center))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    sock.sendall(pickle.dumps({"bereit": True}))  # Sende Bereitschaft an den Server
                    bereit = True
                    button_color = s.GRAY  # Ändere die Farbe des Buttons zu Grau
                    waiting_text = font.render("Warte...", True, s.WHITE)  # Aktualisiere den Text
                    pygame.draw.rect(window, button_color, button_rect)
                    window.blit(waiting_text, waiting_text.get_rect(center=button_rect.center))
                    pygame.display.update()

# Ersetze die ursprüngliche Warte-Bildschirm-Logik durch die neue Funktion
zeige_bereit_button(sock)

# Warte auf Startsignal vom Server
font = pygame.font.Font(None, 36)
waiting_text = font.render("Warte auf anderen Spieler...", True, s.WHITE)
waiting = True
while waiting:
    window.fill(s.BLACK)
    window.blit(waiting_text, waiting_text.get_rect(center=(s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2)))
    pygame.display.update()

    try:
        daten = pickle.loads(sock.recv(2048))
        if daten.get("start"):
            waiting = False
    except (ConnectionResetError, EOFError, pickle.UnpicklingError):
        print("Verbindung zum Server verloren.")
        pygame.quit()
        sys.exit()

# Spielerobjekte werden erzeugt – Startpositionen kommen gleich vom Server
spieler = [Player((0, 0), color=s.GREEN), Player((0, 0), color=s.BLUE)]  # Zwei Spielerobjekte
gegner = [Enemy(0, 0) for _ in range(5)]        # Platzhalter für Gegner
bullets = []                                    # Liste für Bullets

def zeige_game_over_menu(sock):
    """Zeigt das Game-Over-Menü an und wartet auf die Bereitschaft der Spieler."""
    font = pygame.font.Font(None, 36)
    game_over_text = font.render("Spiel beendet! Bereit für Neustart?", True, s.WHITE)
    button_color = s.BLUE
    button_rect = pygame.Rect(s.SCREEN_WIDTH // 2 - 100, s.SCREEN_HEIGHT // 2 - 25, 200, 50)
    bereit = False

    while not bereit:
        window.fill(s.BLACK)
        pygame.draw.rect(window, button_color, button_rect)
        window.blit(game_over_text, game_over_text.get_rect(center=(s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2 - 50)))
        waiting_text = font.render("Bereit?", True, s.WHITE)
        if bereit:
            waiting_text = font.render("Warte auf Spieler...", True, s.WHITE)
        window.blit(waiting_text, waiting_text.get_rect(center=button_rect.center))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos) and not bereit:
                    sock.sendall(pickle.dumps({"bereit": True}))  # Sende Bereitschaft an den Server
                    bereit = True
                    button_color = s.GRAY  # Ändere die Farbe des Buttons zu Grau

running = True  # Spielschleife aktiv
while running:
    clock.tick(s.FPS)  # Begrenze Framerate auf z. B. 60 FPS
    window.fill(s.BLACK)  # Füllt den Hintergrund schwarz

    for event in pygame.event.get():  # Ereignisschleife
        if event.type == pygame.QUIT:  # Wenn das Fenster geschlossen wird
            running = False  # Spielschleife beenden

    # Mausposition abfragen
    maus_position = pygame.mouse.get_pos()  # Liefert (x, y)-Koordinaten der Maus

    # Spielerposition so anpassen, dass die Maus in der Mitte des Spielers ist
    spieler_breite = spieler[0].rect.width
    spieler_hoehe = spieler[0].rect.height
    angepasste_position = (maus_position[0] - spieler_breite // 2, maus_position[1] - spieler_hoehe // 2)

    # Nachricht mit angepasster Position erstellen
    nachricht = {"position": angepasste_position, "schuss": pygame.mouse.get_pressed()[0]}  # Linksklick als Schuss

    # Sende die Daten serialisiert an den Server
    sock.sendall(pickle.dumps(nachricht))

    # Empfange aktualisierte Positionen vom Server
    daten = pickle.loads(sock.recv(2048))
    if daten.get("game_over"):  # Prüfe, ob das Spiel beendet werden soll
        print("Spiel beendet! Ein Spieler wurde getroffen.")
        zeige_game_over_menu(sock)  # Zeige das Game-Over-Menü
        continue  # Warte auf Neustart

    # Prüfe, ob die erwarteten Schlüssel vorhanden sind
    if "spieler" in daten and "gegner" in daten and "bullets" in daten:
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
