import socket                                  # Modul für Netzwerkkommunikation (TCP/IP)
import threading                               # Ermöglicht parallele Verarbeitung (ein Thread pro Client)
import pickle                                  # Zum Serialisieren/Deserialisieren von Python-Objekten
import settings as s                           # Importiert globale Konstanten (z. B. SCREEN_WIDTH, PLAYER_SPEED)

spieler_daten = {                              # Startpositionen für Spieler 0 und 1
    0: (100, s.SCREEN_HEIGHT - 40),            # Spieler 0 startet links unten
    1: (600, s.SCREEN_HEIGHT - 40)             # Spieler 1 startet rechts unten
}

verbindungen = {}                              # Dictionary für aktive Verbindungen {spieler_id: conn}
spielzustand = [(100, s.SCREEN_HEIGHT - 40), (600, s.SCREEN_HEIGHT - 40)]  # Positionen beider Spieler


def client_thread(conn, spieler_id):           # Funktion für die Client-Verarbeitung in einem Thread
    global spielzustand, verbindungen
    conn.sendall(pickle.dumps(spielzustand))   # Sende initialen Spielzustand an den Client

    while True:
        try:
            daten = pickle.loads(conn.recv(1024))         # Empfange Eingaben vom Client
            richtung_x = daten.get("richtung_x", 0)       # Extrahiere Bewegungsrichtung für x
            richtung_y = daten.get("richtung_y", 0)       # Extrahiere Bewegungsrichtung für y
            x, y = spielzustand[spieler_id]               # Hole aktuelle Position dieses Spielers
            x += richtung_x * s.PLAYER_SPEED              # Aktualisiere x-Position
            y += richtung_y * s.PLAYER_SPEED              # Aktualisiere y-Position
            x = max(0, min(s.SCREEN_WIDTH - 50, x))       # Begrenze x-Position
            y = max(0, min(s.SCREEN_HEIGHT - 30, y))      # Begrenze y-Position
            spielzustand[spieler_id] = (x, y)             # Aktualisiere Spielzustand
            conn.sendall(pickle.dumps(spielzustand))      # Sende den neuen Spielzustand an den Client zurück
        except (ConnectionResetError, EOFError, pickle.UnpicklingError) as e:
            print(f"Verbindung zu Spieler {spieler_id} verloren: {e}")
            del verbindungen[spieler_id]                 # Entferne die Verbindung aus der Liste
            break
    conn.close()                                         # Verbindung schließen


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Erstelle ein TCP/IP-Server-Socket
server.bind(("0.0.0.0", 65432))                # Binde Server an alle Netzwerkinterfaces, Port 65432
server.listen(2)                               # Warte auf bis zu 2 gleichzeitige Verbindungen
print("Server gestartet")                      # Bestätigung auf der Konsole

while True:                                    # Endlosschleife für neue Verbindungen
    conn, addr = server.accept()               # Warte auf eingehende Verbindung
    print(f"Neue Verbindung von: {addr}")

    # Finde eine freie Spieler-ID
    freie_id = None
    for i in range(2):
        if i not in verbindungen:
            freie_id = i
            break

    if freie_id is not None:                   # Wenn eine freie Spieler-ID gefunden wurde
        verbindungen[freie_id] = conn          # Speichere die Verbindung
        print(f"Spieler {freie_id} verbunden: {addr}")
        thread = threading.Thread(target=client_thread, args=(conn, freie_id))  # Erstelle neuen Thread
        thread.start()                         # Starte den Thread
    else:
        print("Maximale Spieleranzahl erreicht. Verbindung abgelehnt.")
        conn.close()                           # Schließe die Verbindung, wenn kein Platz frei ist
