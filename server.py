import socket                                  # Modul für Netzwerkkommunikation (TCP/IP)
import threading                               # Ermöglicht parallele Verarbeitung (ein Thread pro Client)
import pickle                                  # Zum Serialisieren/Deserialisieren von Python-Objekten
import settings as s                           # Importiert globale Konstanten (z. B. SCREEN_WIDTH, PLAYER_SPEED)
import random                                  # Für zufällige Positionen der Gegner

spieler_daten = {                              # Startpositionen für Spieler 0 und 1
    0: (100, s.SCREEN_HEIGHT - 40),            # Spieler 0 startet links unten
    1: (600, s.SCREEN_HEIGHT - 40)             # Spieler 1 startet rechts unten
}

verbindungen = []                              # Liste aller aktiven Verbindungen
spielzustand = [(100, s.SCREEN_HEIGHT - 40), (600, s.SCREEN_HEIGHT - 40)]  # Positionen beider Spieler
gegner = [{"x": random.randint(0, s.SCREEN_WIDTH - 40), "y": -30} for _ in range(5)]  # 5 Gegner
bullets = []                                   # Liste für Bullets


def rechteck_kollision(obj1, obj2):
    """Prüft, ob sich zwei Rechtecke überlappen."""
    return (
        obj1["x"] < obj2["x"] + 40 and  # Linke Seite von obj1 < rechte Seite von obj2
        obj1["x"] + 50 > obj2["x"] and  # Rechte Seite von obj1 > linke Seite von obj2
        obj1["y"] < obj2["y"] + 30 and  # Obere Seite von obj1 < untere Seite von obj2
        obj1["y"] + 30 > obj2["y"]      # Untere Seite von obj1 > obere Seite von obj2
    )

def client_thread(conn, spieler_id):  # Funktion für die Client-Verarbeitung in einem Thread
    global spielzustand, gegner, bullets
    conn.sendall(pickle.dumps({"spieler": spielzustand, "gegner": gegner, "bullets": bullets, "game_over": False}))  # Sende initialen Spielzustand an den Client

    while True:  # Endlosschleife zur Kommunikation mit diesem Client
        try:
            daten = pickle.loads(conn.recv(1024))  # Empfange Eingaben vom Client (deserialisiert mit pickle)
            richtung = daten.get("richtung", (0, 0))  # Extrahiere Bewegungsrichtung (-1, 0 oder 1 für x und y)
            schuss = daten.get("schuss", False)  # Extrahiere Schuss-Information

            # Spielerbewegung
            x, y = spielzustand[spieler_id]  # Hole aktuelle Position dieses Spielers
            x += richtung[0] * s.PLAYER_SPEED  # Aktualisiere x-Position basierend auf Eingabe
            y += richtung[1] * s.PLAYER_SPEED  # Aktualisiere y-Position basierend auf Eingabe
            x = max(0, min(s.SCREEN_WIDTH - 50, x))  # Begrenze x-Position innerhalb des Fensters
            y = max(0, min(s.SCREEN_HEIGHT - 30, y))  # Begrenze y-Position innerhalb des Fensters
            spielzustand[spieler_id] = (x, y)  # Aktualisiere Spielzustand

            # Bullet hinzufügen
            if schuss:
                bullets.append({"x": x + 25, "y": y})  # Füge neue Bullet hinzu

            # Bullets aktualisieren
            for bullet in bullets[:]:
                bullet["y"] += s.BULLET_SPEED  # Aktualisiere y-Position der Bullet
                if bullet["y"] < 0:  # Entferne Bullet, wenn sie aus dem Fenster ist
                    bullets.remove(bullet)

            # Gegner aktualisieren
            for gegner_obj in gegner:
                gegner_obj["y"] += s.ENEMY_SPEED  # Aktualisiere y-Position des Gegners
                if gegner_obj["y"] > s.SCREEN_HEIGHT:  # Setze Gegner zurück, wenn er aus dem Fenster ist
                    gegner_obj["x"] = random.randint(0, s.SCREEN_WIDTH - 40)
                    gegner_obj["y"] = -30

            # Kollisionen prüfen (Spieler vs. Gegner)
            for gegner_obj in gegner:
                for i, (spieler_x, spieler_y) in enumerate(spielzustand):
                    spieler_rect = {"x": spieler_x, "y": spieler_y}  # Rechteck des Spielers
                    if rechteck_kollision(spieler_rect, gegner_obj):  # Prüfe auf Kollision
                        # Kollision erkannt, Spiel beenden
                        for verbindung in verbindungen:  # Sende an alle Clients
                            verbindung.sendall(pickle.dumps({"spieler": spielzustand, "gegner": gegner, "bullets": bullets, "game_over": True}))
                        return  # Beende den Thread

            # Kollisionen prüfen (Bullets vs. Gegner)
            for bullet in bullets[:]:
                for gegner_obj in gegner:
                    if (
                        gegner_obj["x"] < bullet["x"] < gegner_obj["x"] + 40 and
                        gegner_obj["y"] < bullet["y"] < gegner_obj["y"] + 30
                    ):
                        bullets.remove(bullet)  # Entferne Bullet bei Kollision
                        gegner_obj["x"] = random.randint(0, s.SCREEN_WIDTH - 40)  # Setze Gegner zurück
                        gegner_obj["y"] = -30
                        break

            # Aktualisierten Zustand senden
            conn.sendall(pickle.dumps({"spieler": spielzustand, "gegner": gegner, "bullets": bullets, "game_over": False}))
        except (ConnectionResetError, EOFError, pickle.UnpicklingError) as e:  # Wenn die Verbindung unterbrochen wurde
            print(f"Verbindung zu Spieler {spieler_id} verloren: {e}")  # Fehler ausgeben
            break
    conn.close()  # Verbindung zum Client schließen


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Erstelle ein TCP/IP-Server-Socket
server.bind(("0.0.0.0", 65432))                # Binde Server an alle Netzwerkinterfaces, Port 65432
server.listen(2)                               # Warte auf bis zu 2 gleichzeitige Verbindungen
print("Server gestartet")                      # Bestätigung auf der Konsole

spieler_id = 0                                 # Start-ID für erste Verbindung
while spieler_id < 2:                          # Erlaube maximal zwei Spieler
    conn, addr = server.accept()              # Warte auf eingehende Verbindung
    print(f"Spieler {spieler_id} verbunden: {addr}")  # Gib verbundene IP-Adresse aus
    verbindungen.append(conn)                 # Speichere die Verbindung
    thread = threading.Thread(target=client_thread, args=(conn, spieler_id))  # Erstelle neuen Thread für diesen Client
    thread.start()                            # Starte den Thread
    spieler_id += 1                           # Erhöhe Spieler-ID (maximal 2)
