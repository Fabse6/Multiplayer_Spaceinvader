import pygame
import settings as s


class Player:
    def __init__(self, start_pos, color=s.GREEN):
        self.image = pygame.Surface((50, 30))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = start_pos
        self.speed = s.PLAYER_SPEED

    def bewegen(self, richtung):
        self.rect.x += richtung * self.speed
        self.rect.x = max(0, min(s.SCREEN_WIDTH - self.rect.width, self.rect.x))

    def zeichnen(self, surface):
        surface.blit(self.image, self.rect)
