import pygame
import settings as s


class Bullet:
    def __init__(self, x, y):
        self.image = pygame.Surface((5, 10))  # Rechteckiges Projektil
        self.image.fill(s.YELLOW)            # Farbe des Projektils
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -s.BULLET_SPEED         # Negative Geschwindigkeit für Bewegung nach oben

    def update(self):
        self.rect.y += self.speed            # Bewege das Projektil nach oben

    def zeichnen(self, surface):
        surface.blit(self.image, self.rect)
