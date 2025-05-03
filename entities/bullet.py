import pygame
import settings as s


class Bullet:
    def __init__(self, x, y):
        self.image = pygame.Surface((5, 10), pygame.SRCALPHA)  # Transparente Bullet
        pygame.draw.rect(self.image, s.YELLOW, (0, 0, 5, 10))  # Zeichne die Bullet
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = s.BULLET_SPEED
        self.mask = pygame.mask.from_surface(self.image)  # Erstelle eine Maske für pixelgenaue Kollision

    def update(self):
        self.rect.y -= self.speed  # Bewege die Bullet nach oben

    def zeichnen(self, surface):
        surface.blit(self.image, self.rect)
