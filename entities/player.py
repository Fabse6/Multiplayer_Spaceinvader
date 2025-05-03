import pygame
import settings as s


class Player:
    def __init__(self, start_pos):
        self.image = pygame.image.load("Rakete.png").convert_alpha()  # Lade das Bild mit Transparenz
        self.image = pygame.transform.scale(self.image, (50, 50))  # Skaliere das Bild auf 50x50 Pixel
        self.rect = self.image.get_rect()
        self.rect.topleft = start_pos
        self.speed = s.PLAYER_SPEED
        self.mask = pygame.mask.from_surface(self.image)  # Erstelle eine Maske für pixelgenaue Kollision

    def bewegen(self, richtung):
        self.rect.x += richtung * self.speed
        self.rect.x = max(0, min(s.SCREEN_WIDTH - self.rect.width, self.rect.x))

    def zeichnen(self, surface):
        surface.blit(self.image, self.rect)
