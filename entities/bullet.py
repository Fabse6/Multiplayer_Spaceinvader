import pygame
import settings as s


class Bullet:
    def __init__(self, x, y):
        self.image = pygame.Surface((5, 10))
        self.image.fill(s.YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = s.BULLET_SPEED

    def update(self):
        self.rect.y += self.speed

    def zeichnen(self, surface):
        surface.blit(self.image, self.rect)
