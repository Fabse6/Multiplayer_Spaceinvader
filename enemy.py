import pygame
import random

from settings import ENEMY_SPEED

class Enemy:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, 750), random.randint(0, 600), 50, 50)
        self.speed = ENEMY_SPEED

    def move(self):
             self.rect.x += self.speed

    def draw(self, win):
        pygame.draw.rect(win, (255, 0, 0), self.rect)
        