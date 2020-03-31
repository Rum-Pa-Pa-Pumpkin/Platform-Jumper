# pygame template - skeleton for a new pygame project
import pygame
import random
from settings import *

# initialize pygame and create window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
# Game loop
is_running = True
while is_running:
    # keep the loop running at the same speed
    clock.tick(FPS)
    # Process input (events)
    for event in pygame.event.get():
        # check for closing the window
        if event.type == pygame.QUIT:
            is_running = False
    # Update
    all_sprites.update()
    # Render
    screen.fill(BLACK)
    all_sprites.draw(screen)
    # after drawing everything flip the display
    pygame.display.flip()


pygame.quit()