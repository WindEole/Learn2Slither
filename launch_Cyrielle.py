#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import random
import argparse
import pygame
import time

# ------------------------------------------------------------------
# CONSTANTES GLOBALES
# ------------------------------------------------------------------

BOARD_SIZE = 10
CELL_SIZE = 40
NB_GREEN_APPLES = 2
NB_RED_APPLES = 1

COLOR_BG      = (30, 30, 30)
COLOR_SNAKE   = (0, 0, 200)
COLOR_GREEN   = (0, 200, 0)
COLOR_RED     = (200, 0, 0)
COLOR_HEAD    = (0, 100, 255)

UP = 0
LEFT = 1
DOWN = 2
RIGHT = 3
ACTION_NAMES = ["UP", "LEFT", "DOWN", "RIGHT"]

ALPHA = 0.1
GAMMA = 0.9
EPSILON = 0.9

# ------------------------------------------------------------------
# CLASSE : Board
# ------------------------------------------------------------------

class Board:
    def __init__(self):
        self.size = BOARD_SIZE
        self.reset()

    def reset(self):
        """
        Réinitialise la grille et les positions :
        - Le serpent (3 cases contiguës).
        - Les pommes vertes et rouges (sets de positions).
        """
        self.game_over = False
        
        # --- Placer le serpent ---
        self.snake = []
        head_x = random.randint(0, self.size - 1)
        head_y = random.randint(0, self.size - 1)
        self.snake.append((head_x, head_y))  # tête

        # Tenter d'ajouter 2 segments
        possible_dirs = [(1,0), (-1,0), (0,1), (0,-1)]
        random.shuffle(possible_dirs)
        placed = False
        for dx, dy in possible_dirs:
            x2 = head_x + dx
            y2 = head_y + dy
            x3 = head_x + 2*dx
            y3 = head_y + 2*dy
            if 0 <= x2 < self.size and 0 <= y2 < self.size \
               and 0 <= x3 < self.size and 0 <= y3 < self.size:
                self.snake.append((x2, y2))
                self.snake.append((x3, y3))
                placed = True
                break
        if not placed:
            # Par sécurité, on force une position simple
            self.snake = [(0,0), (0,1), (0,2)]

        # --- Placer les pommes dans des sets ---
        self.green_apples = set()
        self.red_apples = set()
        
        # Ajoute NB_GREEN_APPLES pommes vertes au hasard
        for _ in range(NB_GREEN_APPLES):
            self._place_apple('G')
        # Ajoute NB_RED_APPLES pommes rouges au hasard
        for _ in range(NB_RED_APPLES):
            self._place_apple('R')

        # Mettre à jour la grille pour affichage
        self._update_grid()

    def _place_apple(self, apple_type):
        """
        Place UNE pomme (verte ou rouge) au hasard sur une case libre.
        apple_type = 'G' ou 'R'
        """
        # Récupérer toutes les cases occupées par serpent + pommes existantes
        occupied = set(self.snake) | self.green_apples | self.red_apples
        empty_positions = [(x, y)
                           for x in range(self.size)
                           for y in range(self.size)
                           if (x, y) not in occupied]
        if not empty_positions:
            return
        new_x, new_y = random.choice(empty_positions)
        if apple_type == 'G':
            self.green_apples.add((new_x, new_y))
        else:
            self.red_apples.add((new_x, new_y))

    def _update_grid(self):
        """
        Reconstruit la grille (list of lists) à partir du serpent et des pommes.
        Utile pour l'affichage et la vision.
        """
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        # Marquer le serpent
        for i, (sx, sy) in enumerate(self.snake):
            self.grid[sy][sx] = 'S'
        # Marquer les pommes
        for (gx, gy) in self.green_apples:
            self.grid[gy][gx] = 'G'
        for (rx, ry) in self.red_apples:
            self.grid[ry][rx] = 'R'

    def step(self, action):
        """
        Fait avancer le serpent dans la direction 'action'.
        Renvoie un reward et met self.game_over = True si échec.
        """
        if self.game_over:
            return 0

        head_x, head_y = self.snake[0]
        if action == UP:
            new_head = (head_x, head_y - 1)
        elif action == LEFT:
            new_head = (head_x - 1, head_y)
        elif action == DOWN:
            new_head = (head_x, head_y + 1)
        else:  # RIGHT
            new_head = (head_x + 1, head_y)

        nx, ny = new_head
        # Vérif mur
        if not (0 <= nx < self.size and 0 <= ny < self.size):
            self.game_over = True
            return -200  # collision mur

        # Vérif collision avec soi-même
        if new_head in self.snake:
            self.game_over = True
            return -200  # collision queue

        # Avancer le serpent
        self.snake.insert(0, new_head)
        reward = -20  # petite pénalité par défaut

        # Vérif si on mange une pomme verte
        if new_head in self.green_apples:
            reward = +100
            # Retirer la pomme mangée
            self.green_apples.remove(new_head)
            # Régénérer une nouvelle pomme verte
            self._place_apple('G')
        # Vérif si on mange une pomme rouge
        elif new_head in self.red_apples:
            reward = -25
            # Retirer la pomme mangée
            self.red_apples.remove(new_head)
            # Régénérer une nouvelle pomme rouge
            self._place_apple('R')
            # Rétrécir le serpent d'une unité en plus
            if len(self.snake) > 1:
                self.snake.pop()
            if len(self.snake) == 0:
                self.game_over = True
                return -10

        else:
            # Pas de pomme mangée -> enlever le dernier segment
            self.snake.pop()

        # Mettre à jour la grille
        self._update_grid()

        # Vérif si le serpent a taille 0
        if len(self.snake) == 0:
            self.game_over = True
            return -10

        return reward

    def is_game_over(self):
        return self.game_over

    def get_snake_head(self):
        return self.snake[0]

    def get_snake_length(self):
        return len(self.snake)

    def get_state_representation(self):
        """
        Récupère la vision 4 directions (UP, LEFT, DOWN, RIGHT).
        Renvoie un tuple, ex : ('S','0','W','G').
        """
        hx, hy = self.snake[0]

        def scan(dx, dy):
            x, y = hx, hy
            while True:
                x += dx
                y += dy
                if x < 0 or x >= self.size or y < 0 or y >= self.size:
                    return 'W'  # mur
                cell = self.grid[y][x]
                if cell == 'S':
                    return 'S'
                elif cell == 'G':
                    return 'G'
                elif cell == 'R':
                    return 'R'
                # sinon 0 => continue
        up_obj    = scan(0, -1)
        left_obj  = scan(-1, 0)
        down_obj  = scan(0, 1)
        right_obj = scan(1, 0)
        return (up_obj, left_obj, down_obj, right_obj)

# ------------------------------------------------------------------
# AGENT Q-LEARNING
# ------------------------------------------------------------------

class QLearningAgent:
    def __init__(self, alpha=ALPHA, gamma=GAMMA, epsilon=EPSILON):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        # Q-table : dict[ state -> [q_UP, q_LEFT, q_DOWN, q_RIGHT] ]
        self.q_table = {}

    def get_q_values(self, state):
        if state not in self.q_table:
            self.q_table[state] = [0.0, 0.0, 0.0, 0.0]
        return self.q_table[state]

    def choose_action(self, state, no_learn=False):
        qvals = self.get_q_values(state)
        if no_learn:
            # exploitation pure (epsilon=0)
            return max(range(4), key=lambda a: qvals[a])
        else:
            # epsilon-greedy
            if random.random() < self.epsilon:
                return random.randint(0, 3)
            else:
                return max(range(4), key=lambda a: qvals[a])

    def update(self, state, action, reward, next_state):
        old_q = self.get_q_values(state)[action]
        max_next_q = max(self.get_q_values(next_state))
        td_target = reward + self.gamma * max_next_q
        new_q = old_q + self.alpha * (td_target - old_q)
        self.q_table[state][action] = new_q

    def save(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            for state, qvals in self.q_table.items():
                line = ",".join(state) + " " + " ".join(map(str, qvals))
                f.write(line + "\n")

    def load(self, filename):
        self.q_table = {}
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                state_str = parts[0]
                qvals_str = parts[1:]
                state_tuple = tuple(state_str.split(","))
                qvals_float = list(map(float, qvals_str))
                self.q_table[state_tuple] = qvals_float

# ------------------------------------------------------------------
# FONCTIONS D'AFFICHAGE ET MAIN
# ------------------------------------------------------------------

def print_snake_vision(state):
    up, left, down, right = state
    print(f"Snake sees -> Up={up}, Left={left}, Down={down}, Right={right}")

def draw_board(screen, board):
    screen.fill(COLOR_BG)
    for y in range(board.size):
        for x in range(board.size):
            cell = board.grid[y][x]
            rect = (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if cell == 'S':
                # tête en couleur différente
                if (x,y) == board.snake[0]:
                    pygame.draw.rect(screen, COLOR_HEAD, rect)
                else:
                    pygame.draw.rect(screen, COLOR_SNAKE, rect)
            elif cell == 'G':
                pygame.draw.rect(screen, COLOR_GREEN, rect)
            elif cell == 'R':
                pygame.draw.rect(screen, COLOR_RED, rect)
    pygame.display.flip()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-sessions", type=int, default=1)
    parser.add_argument("-save", type=str, default=None)
    parser.add_argument("-load", type=str, default=None)
    parser.add_argument("-visual", type=str, default="on", choices=["on","off"])
    parser.add_argument("-step-by-step", action="store_true")
    parser.add_argument("-dontlearn", action="store_true")
    return parser.parse_args()

def main():
    args = parse_args()

    visual_enabled = (args.visual == "on")
    if visual_enabled:
        pygame.init()
        screen = pygame.display.set_mode((BOARD_SIZE*CELL_SIZE, BOARD_SIZE*CELL_SIZE))
        pygame.display.set_caption("Snake RL - Fixed Apples")

    agent = QLearningAgent(alpha=ALPHA, gamma=GAMMA, epsilon=EPSILON)

    # Charger un modèle si demandé
    if args.load:
        print(f"Loading model from {args.load}")
        agent.load(args.load)

    for sess in range(1, args.sessions+1):
        board = Board()
        game_over = False
        total_reward = 0
        max_length = board.get_snake_length()
        steps = 0

        while not game_over:
            if visual_enabled:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

            state = board.get_state_representation()
            print_snake_vision(state)

            action = agent.choose_action(state, no_learn=args.dontlearn)
            reward = board.step(action)
            total_reward += reward
            game_over = board.is_game_over()
            next_state = board.get_state_representation()

            if not args.dontlearn and not game_over:
                agent.update(state, action, reward, next_state)

            if visual_enabled:
                draw_board(screen, board)
                time.sleep(0.15)

            if args.step_by_step:
                input("Press ENTER for next step...")

            current_length = board.get_snake_length()
            if current_length > max_length:
                max_length = current_length

            steps += 1

        print(f"[Session {sess}] Game over. Final length={board.get_snake_length()}, "
              f"max length={max_length}, total reward={total_reward}, steps={steps}")

    if args.save:
        print(f"Saving model to {args.save}")
        agent.save(args.save)

    if visual_enabled:
        print("Press Ctrl+C or close the window to exit.")
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            time.sleep(0.1)

if __name__ == "__main__":
    main()