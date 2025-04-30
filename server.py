# server.py
import socket
import threading
import pickle

from settings import SERVER_IP, SERVER_PORT, MAX_PLAYERS

class Server:
    def __init__(self):
        self.players = {}
        self.ready = {}
        self.lock = threading.Lock()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((SERVER_IP, SERVER_PORT))
        self.server.listen()
        print(f"Server started on {SERVER_IP}:{SERVER_PORT}")

    def client_thread(self, conn, player_id):
        conn.send(pickle.dumps(player_id))
        while True:
            try:
                data = pickle.loads(conn.recv(1024))
                if not data:
                    break
                with self.lock:
                    self.players[player_id] = data['player']
                    self.ready[player_id] = data['ready']
                conn.send(pickle.dumps({'players': self.players, 'ready': self.ready}))
            except:
                break
        print(F"Verbindung zu Spieler {player_id} getrennt")
        with self.lock:
            del self.players[player_id]
            del self.ready[player_id]
        conn.close()

    def run(self):
        player_id = 0
        while True:
            conn, addr = self.serber.accept()
            print(f"Verbindung von {addr} akzeptiert")
            with self.lock:
                self.players[player_id] = None
                self.ready[player_id] = False
            threading.Thread(target=self.client_thread, args=(conn, player_id)).start()
            player_id += 1

if __name__ == "__main__":
    server = Server()
    server.run()
