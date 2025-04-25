import pygame
import settings as s


class Enemy:
    def __init__(self, x, y):
        self.image = pygame.Surface((40, 30))
        self.image.fill(s.RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = s.ENEMY_SPEED

    def update(self):
        self.rect.x += self.speed

    def zeichnen(self, surface):
        surface.blit(self.image, self.rect)
