import pygame

def draw_menu(win, font, ready):
    win.fill((0, 0, 0))
    text = font.render("Press 'R' to Ready", True, (255, 255, 255))
    win.blit(text, (250, 250))
    status = "Ready" if ready else "Not Ready"
    status_text = font.render(status, True, (255, 255, 255))
    win.blit(status_text, (250, 300))
    pygame.display.update()