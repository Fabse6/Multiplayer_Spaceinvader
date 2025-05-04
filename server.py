import socket                                  # Modul für Netzwerkkommunikation (TCP/IP)
import threading                               # Ermöglicht parallele Verarbeitung (ein Thread pro Client)
import pickle                                  # Zum Serialisieren/Deserialisieren von Python-Objekten
import settings as s                           # Importiert globale Konstanten (z. B. SCREEN_WIDTH, PLAYER_SPEED)

spieler_daten = {                              # Startpositionen für Spieler 0 und 1
    0: (100, s.SCREEN_HEIGHT - 40),            # Spieler 0 startet links unten
    1: (600, s.SCREEN_HEIGHT - 40)             # Spieler 1 startet rechts unten
}

verbindungen = []                              # Liste aller aktiven Verbindungen
spielzustand = [(100, s.SCREEN_HEIGHT - 40), (600, s.SCREEN_HEIGHT - 40)]  # Positionen beider Spieler


def client_thread(conn, spieler_id):           # Funktion für die Client-Verarbeitung in einem Thread
    global spielzustand
    conn.sendall(pickle.dumps(spielzustand))   # Sende initialen Spielzustand an den Client

    while True:                                 # Endlosschleife zur Kommunikation mit diesem Client
        try:
            daten = pickle.loads(conn.recv(1024))         # Empfange Eingaben vom Client (deserialisiert mit pickle)
            richtung = daten.get("richtung", 0)           # Extrahiere Bewegungsrichtung (-1, 0 oder 1)
            x, y = spielzustand[spieler_id]               # Hole aktuelle Position dieses Spielers
            x += richtung * s.PLAYER_SPEED                # Aktualisiere x-Position basierend auf Eingabe
            x = max(0, min(s.SCREEN_WIDTH - 50, x))       # Begrenze Position innerhalb des Fensters
            spielzustand[spieler_id] = (x, y)             # Aktualisiere Spielzustand
            conn.sendall(pickle.dumps(spielzustand))      # Sende den neuen Spielzustand an den Client zurück
        except (ConnectionResetError, EOFError, pickle.UnpicklingError) as e:  # Wenn die Verbindung unterbrochen wurde
            print(f"Verbindung zu Spieler {spieler_id} verloren: {e}")         # Fehler ausgeben
            break
    conn.close()                                # Verbindung zum Client schließen


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
