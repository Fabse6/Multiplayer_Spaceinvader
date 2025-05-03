import random
import pygame
import settings as s


class Enemy:
    def __init__(self, x, y):
        self.image = pygame.image.load("Raumschiff.png").convert_alpha()  # Lade das Bild mit Transparenz
        self.image = pygame.transform.scale(self.image, (40, 40))  # Skaliere das Bild auf 40x40 Pixel
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = s.ENEMY_SPEED
        self.mask = pygame.mask.from_surface(self.image)  # Erstelle eine Maske für pixelgenaue Kollision

    def update(self):
        self.rect.y += self.speed  # Bewege den Gegner nach unten
        if self.rect.top > s.SCREEN_HEIGHT:  # Wenn der Gegner den unteren Rand verlässt
            self.rect.y = -self.rect.height  # Setze ihn wieder oben
            self.rect.x = random.randint(0, s.SCREEN_WIDTH - self.rect.width)  # Zufällige X-Position

    def zeichnen(self, surface):
        surface.blit(self.image, self.rect)
