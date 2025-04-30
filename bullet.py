import pygame

from settings import BULLET_SPEED

class Bullet:
    def __iit__(self, x, y):
        self.rect = pygame.Rect(x + 20, y, 10, 10)

    def move(self):
        self.rect.y -= BULLET_SPEED

    def draw(self, win):
        pygame.draw.rect(win, (255, 255, 0), self.rect)
        