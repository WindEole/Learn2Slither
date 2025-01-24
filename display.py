"""Affichage.

Ce programme affiche l'etat du jeu.
Dans une fenetre pygame : la progression du jeu
Dans le terminal : la vision depuis la tete du serpent.
"""
import pygame

from pygame.locals import *
from snakegame import SnakeGame


def display_snake_vision(game: SnakeGame):
    """Affiche la vision du serpent sur le terminal."""
    # Obtenir la vision du serpent
    grid_size = game.grid_size
    snake_vision = game.get_snake_vision()
    head_x, head_y = game.snake[0]  # position de la tete

    # Extraire la vue
    hori_view = snake_vision[:grid_size]
    vert_view = snake_vision[grid_size:]

    # Remplacer les codes par des symboles
    symbol_map = {0: "0", 1: "S", 2: "G", 3: "R"}
    hori_view = [symbol_map.get(value, "0") for value in hori_view]
    vert_view = [symbol_map.get(value, "0") for value in vert_view]

    # Remplacer le symbole de la tete de serpent
    hori_view[head_x] = "H"
    vert_view[head_y] = "H"

    # Construire la representation visuelle
    visual = []
    visual.append(" " * (head_x + 1) + "W")  # ligne sup avec mur
    for i, sym in enumerate(vert_view):
        if i == head_y:
            visual.append("W" + "".join(hori_view) + "W")
        else:
            visual.append(" " * (head_x + 1) + sym)
    visual.append(" " * (head_x + 1) + "W")  # ligne inf avec mur

    # Afficher la vue dans le terminal
    print("\n".join(visual))


def draw_grid(DISPLAYSURF, grid: int, mult: int, line_color=(200, 175, 175)):
    """Trace un quadrillage sur le plateau."""
    for x in range(grid + 1):
        pygame.draw.line(DISPLAYSURF, line_color, (x * mult, 0), (x * mult, (grid + 1) * mult))
    for y in range(grid + 1):
        pygame.draw.line(DISPLAYSURF, line_color, (0, y * mult), ((grid + 1) * mult, y * mult))


def draw_game_display(DISPLAYSURF, game: SnakeGame, grid: int, mult: int, images: dict):
    """Affiche les assets du jeu."""
    # Recupere l'etat actuel du jeu
    snake, green_apples, red_apple = game.get_state()
    fullgrid = grid + 2

    # Affiche le sol
    for x in range(fullgrid):
        for y in range(fullgrid):
            DISPLAYSURF.blit(images["floor"], (x * mult, y * mult))
    
    # Affiche le quadrillage
    draw_grid(DISPLAYSURF, fullgrid, mult)

    # Affiche les murs
    for x in range(fullgrid):  # parcourt les colonnes
        DISPLAYSURF.blit(images["wall"], (x * mult, 0))  # haut
        DISPLAYSURF.blit(images["wall"], (x * mult, (grid + 1) * mult))  # bas
    for y in range(fullgrid):  # parcourt les lignes
        DISPLAYSURF.blit(images["wall"], (0, y * mult))  # gauche
        DISPLAYSURF.blit(images["wall"], ((grid + 1) * mult, y * mult))

    # Affiche le serpent
    x, y = snake[0]
    DISPLAYSURF.blit(images["snake_head"], ((x + 1) * mult, (y + 1) * mult))
    for segment in snake[1:]:
        x, y = segment
        # pygame.draw.rect(DISPLAYSURF, BLUE, (x * mult, y * mult, mult, mult))
        DISPLAYSURF.blit(images["snake_segment"], ((x + 1) * mult, (y + 1) * mult))

    # Affiche les pommes vertes
    for apple in green_apples:
        x, y = apple
        DISPLAYSURF.blit(images["green_apple"], ((x + 1) * mult, (y + 1) * mult))

    # Affiche la pomme rouge
    x, y = red_apple
    DISPLAYSURF.blit(images["red_apple"], ((x + 1) * mult, (y + 1) * mult))