import random  # Für zufällige Startpositionen
import pygame
import settings as s


class Enemy:
    def __init__(self, x, y):
        self.image = pygame.Surface((40, 30))
        self.image.fill(s.RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = s.ENEMY_SPEED

    def update(self):
        self.rect.y += self.speed  # Bewege den Gegner nach unten
        if self.rect.top > s.SCREEN_HEIGHT:  # Wenn der Gegner den unteren Rand verlässt
            self.rect.y = -self.rect.height  # Setze ihn wieder oben
            self.rect.x = random.randint(0, s.SCREEN_WIDTH - self.rect.width)  # Zufällige X-Position

    def zeichnen(self, surface):
        surface.blit(self.image, self.rect)
