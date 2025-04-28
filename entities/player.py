import pygame
import settings as s


class Player:
    def __init__(self, start_pos, color=s.GREEN):
        self.image = pygame.image.load("Rakete.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.topleft = start_pos
        self.speed = s.PLAYER_SPEED
        self.alive = True  # Spielerstatus: Lebendig oder getroffen
        self.mask = pygame.mask.from_surface(self.image)  # Maske für pixelgenaue Kollision

    def bewegen(self, richtung_x, richtung_y):
        # Bewege den Spieler in x-Richtung
        self.rect.x += richtung_x * self.speed
        self.rect.x = max(0, min(s.SCREEN_WIDTH - self.rect.width, self.rect.x))
        # Bewege den Spieler in y-Richtung
        self.rect.y += richtung_y * self.speed
        self.rect.y = max(0, min(s.SCREEN_HEIGHT - self.rect.height, self.rect.y))

    def zeichnen(self, surface):
        if self.alive:  # Zeichne nur, wenn der Spieler lebendig ist
            surface.blit(self.image, self.rect)
