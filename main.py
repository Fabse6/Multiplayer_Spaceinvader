import pygame
import socket
import pickle
import threading

from settings import WIDTH, HEIHGT, FPS, PLAYER_SPEED, SERVER_IP, SERVER_PORT
from player import Player
from enemy import Enemy
from bullet import Bullet
from menu import draw_menu

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIHGT))
pygame.display.set_caption("Multiplayer Game")
font = pygame.font.SysFont("Arial", 30)

clock = pygame.time.Clock()
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, SERVER_PORT))
player_id = pickle.loads(client.recv(4096))
color = (0, 0, 255) if player_id == 0 else (255, 0, 0)
player = Player(375, 500, color)
bullets = []
enemies = [Enemy() for _ in range(5)]
ready = False
players = {}
ready_status = {}

def receive_data():
    global players, ready_status
    while True:
        try:
            data = pickle.loads(client.recv(4096))
            players = data['players']
            ready_status = data['ready']
        except:
            break

threading.Thread(target=receive_data, daemon=True).start()

def main():
    global ready, bullets, enemies
    run = True
    in_game = False  # Korrekte Initialisierung
    while run:
        clock.tick(FPS)
        try:
            if not in_game:
                draw_menu(win, font, ready)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            ready = not ready
                client.send(pickle.dumps({'player': player, 'ready': ready}))
                if all(ready_status.values()) and len(ready_status) > 0:
                    in_game = True
                    bullets = []
                    enemies = [Enemy() for _ in range(5)]
                    player.alive = True
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE and player.alive:
                            bullets.append(Bullet(player.rect.x, player.rect.y))
                keys = pygame.key.get_pressed()
                if player.alive:
                    player.move(keys)
                for bullet in bullets[:]:
                    bullet.move()
                    if bullet.rect.y < 0:
                        bullets.remove(bullet)
                for enemy in enemies[:]:
                    enemy.move()
                    if enemy.rect.colliderect(player.rect):
                        player.alive = False
                    for bullet in bullets[:]:
                        if enemy.rect.colliderect(bullet.rect):
                            bullets.remove(bullet)
                            enemies.remove(enemy)
                            break
                if not player.alive:
                    in_game = False
                    ready = False
                win.fill((0, 0, 0))
                player.draw(win)
                for bullet in bullets:
                    bullet.draw(win)
                for enemy in enemies:
                    enemy.draw(win)
                pygame.display.update()
                client.send(pickle.dumps({'player': player, 'bullets': bullets, 'enemies': enemies}))
        except Exception as e:
            print(f"Ein Fehler ist aufgetreten: {e}")
            run = False

    pygame.quit()

if __name__ == "__main__":
    main()








