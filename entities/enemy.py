import pygame
import random
import settings as s


class Enemy:
    def __init__(self, x, y):
        self.image = pygame.image.load("Raumschiff.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = s.ENEMY_SPEED
        self.mask = pygame.mask.from_surface(self.image)  # Maske für pixelgenaue Kollision

    def update(self):
        self.rect.y += self.speed
        # Wenn der Gegner das Spielfeld verlässt, spawne ihn oben neu
        if self.rect.top > s.SCREEN_HEIGHT:
            self.rect.x = random.randint(0, s.SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randint(-200, -50)

    def zeichnen(self, surface):
        surface.blit(self.image, self.rect)

