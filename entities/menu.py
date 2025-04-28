import pygame
import sys
import settings as s

class Menu:
    def __init__(self, window):
        self.window = window
        self.font = pygame.font.SysFont(None, 48)

    def anzeigen(self, text="Press ENTER to Start"):
        self.window.fill(s.BLACK)
        title_text = self.font.render("Multiplayer Space Invader", True, s.WHITE)
        instruction_text = self.font.render(text, True, s.WHITE)

        # Positioniere die Texte
        title_rect = title_text.get_rect(center=(s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 3))
        instruction_rect = instruction_text.get_rect(center=(s.SCREEN_WIDTH // 2, s.SCREEN_HEIGHT // 2))

        # Zeichne die Texte
        self.window.blit(title_text, title_rect)
        self.window.blit(instruction_text, instruction_rect)

        pygame.display.update()

        # Warte auf Eingabe
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Spiel starten
                        return