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
spieler_bereit = [False, False]                # Liste, um den Bereitschaftsstatus der Spieler zu speichern


def rechteck_kollision(obj1, obj2):
    """Prüft, ob sich zwei Rechtecke überlappen."""
    return (
        obj1["x"] < obj2["x"] + 40 and  # Linke Seite von obj1 < rechte Seite von obj2
        obj1["x"] + 50 > obj2["x"] and  # Rechte Seite von obj1 > linke Seite von obj2
        obj1["y"] < obj2["y"] + 30 and  # Obere Seite von obj1 < untere Seite von obj2
        obj1["y"] + 30 > obj2["y"]      # Untere Seite von obj1 > obere Seite von obj2
    )


def spiel_zuruecksetzen():
    """Setzt den Spielzustand zurück."""
    global spielzustand, gegner, bullets, spieler_bereit
    spielzustand = [(100, s.SCREEN_HEIGHT - 40), (600, s.SCREEN_HEIGHT - 40)]  # Startpositionen der Spieler
    gegner = [{"x": random.randint(0, s.SCREEN_WIDTH - 40), "y": -30} for _ in range(5)]  # Neue Gegner
    bullets.clear()  # Alle Bullets entfernen
    spieler_bereit = [False, False]  # Spieler wieder auf "nicht bereit" setzen


def client_thread(conn, spieler_id):
    global spielzustand, gegner, bullets
    try:
        conn.sendall(pickle.dumps({"spieler": spielzustand, "gegner": gegner, "bullets": bullets, "game_over": False}))
    except OSError:
        print(f"Fehler beim Senden an Spieler {spieler_id}. Verbindung wird geschlossen.")
        conn.close()
        return

    while True:
        try:
            daten = conn.recv(1024)
            if not daten:
                raise ConnectionResetError("Verbindung wurde vom Client geschlossen.")
            daten = pickle.loads(daten)
            richtung = daten.get("richtung", (0, 0))
            schuss = daten.get("schuss", False)

            # Spielerbewegung
            x, y = spielzustand[spieler_id]
            x += richtung[0] * s.PLAYER_SPEED
            y += richtung[1] * s.PLAYER_SPEED
            x = max(0, min(s.SCREEN_WIDTH - 50, x))
            y = max(0, min(s.SCREEN_HEIGHT - 30, y))
            spielzustand[spieler_id] = (x, y)

            # Bullet hinzufügen
            if schuss:
                bullets.append({"x": x + 25, "y": y})

            # Bullets aktualisieren
            for bullet in bullets[:]:
                bullet["y"] += s.BULLET_SPEED
                if bullet["y"] < 0:
                    bullets.remove(bullet)

            # Gegner aktualisieren
            for gegner_obj in gegner:
                gegner_obj["y"] += s.ENEMY_SPEED
                if gegner_obj["y"] > s.SCREEN_HEIGHT:
                    gegner_obj["x"] = random.randint(0, s.SCREEN_WIDTH - 40)
                    gegner_obj["y"] = -30

            # Kollisionen prüfen (Spieler vs. Gegner)
            for gegner_obj in gegner:
                for i, (spieler_x, spieler_y) in enumerate(spielzustand):
                    spieler_rect = {"x": spieler_x, "y": spieler_y}
                    if rechteck_kollision(spieler_rect, gegner_obj):
                        for verbindung in verbindungen:
                            verbindung.sendall(pickle.dumps({"spieler": spielzustand, "gegner": gegner, "bullets": bullets, "game_over": True}))
                        return

            # Kollisionen prüfen (Bullets vs. Gegner)
            for bullet in bullets[:]:
                for gegner_obj in gegner:
                    if (
                        gegner_obj["x"] < bullet["x"] < gegner_obj["x"] + 40 and
                        gegner_obj["y"] < bullet["y"] < gegner_obj["y"] + 30
                    ):
                        bullets.remove(bullet)
                        gegner_obj["x"] = random.randint(0, s.SCREEN_WIDTH - 40)
                        gegner_obj["y"] = -30
                        break

            # Aktualisierten Zustand senden
            try:
                conn.sendall(pickle.dumps({"spieler": spielzustand, "gegner": gegner, "bullets": bullets, "game_over": False}))
            except OSError:
                print(f"Fehler beim Senden an Spieler {spieler_id}. Verbindung wird geschlossen.")
                conn.close()
                return
        except BlockingIOError:
            # Keine Daten verfügbar, einfach weitermachen
            continue
        except (ConnectionResetError, EOFError, pickle.UnpicklingError) as e:
            print(f"Verbindung zu Spieler {spieler_id} verloren: {e}")
            break
    conn.close()


def warte_auf_bereitschaft():
    """Warte, bis beide Spieler bereit sind."""
    global spieler_bereit
    for conn in verbindungen:
        conn.setblocking(False)  # Setze Verbindungen auf nicht blockierend

    while not all(spieler_bereit):  # Schleife, bis beide Spieler bereit sind
        for i, conn in enumerate(verbindungen):
            if spieler_bereit[i]:  # Überspringe Spieler, die bereits bereit sind
                continue
            try:
                daten = pickle.loads(conn.recv(1024))  # Empfange Daten vom Spieler
                if daten.get("bereit"):  # Spieler hat "Bereit" gesendet
                    spieler_bereit[i] = True
                    print(f"Spieler {i} ist bereit.")
            except BlockingIOError:
                # Keine Daten verfügbar, einfach weitermachen
                continue
            except (ConnectionResetError, EOFError, pickle.UnpicklingError):
                print(f"Verbindung zu Spieler {i} verloren.")
                return False
    return True


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Erstelle ein TCP/IP-Server-Socket
server.bind(("0.0.0.0", 65432))                # Binde Server an alle Netzwerkinterfaces, Port 65432
server.listen(2)                               # Warte auf bis zu 2 gleichzeitige Verbindungen
print("Server gestartet")                      # Bestätigung auf der Konsole

spieler_id = 0                                 # Start-ID für erste Verbindung
while spieler_id < 2:                          # Erlaube maximal zwei Spieler
    conn, addr = server.accept()              # Warte auf eingehende Verbindung
    print(f"Spieler {spieler_id} verbunden: {addr}")  # Gib verbundene IP-Adresse aus
    verbindungen.append(conn)                 # Speichere die Verbindung
    spieler_id += 1                           # Erhöhe Spieler-ID (maximal 2)

while True:
    print("Warte, bis beide Spieler bereit sind...")
    if not warte_auf_bereitschaft():
        print("Spiel konnte nicht gestartet werden.")
        break

    print("Alle Spieler bereit. Spiel startet!")
    spiel_zuruecksetzen()  # Spielzustand zurücksetzen

    # Sende Startsignal an beide Spieler
    for verbindung in verbindungen:
        verbindung.sendall(pickle.dumps({"start": True}))

    # Starte Threads für beide Spieler
    threads = []
    for i, conn in enumerate(verbindungen):
        thread = threading.Thread(target=client_thread, args=(conn, i))
        thread.start()
        threads.append(thread)

    # Warte, bis alle Threads beendet sind
    for thread in threads:
        thread.join()
