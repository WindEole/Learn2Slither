"""Classe SnakeGame.

La classe SnakeGame initialise le jeu et definit toutes les fonctions afferentes.
grid : taille de la grille.
"""
import random


class SnakeGame:
    def __init__(self, grid, goal):
        """Initialisation."""
        self.grid_size = grid
        self.goal = goal  # Nb de segments a atteindre
        self.snake = self._place_snake_randomly()

        self.green_apples = []  # Initialisation temporaire
        self.red_apple = (0, 0)  # Initialisation temporaire
        self.green_apples = self._place_apples_randomly(2)
        self.red_apple = self._place_apples_randomly(1)[0]

        self.done = False
        self.reward = 0
        self.current_direction = 'haut'

    def _place_snake_randomly(self):
        """Place un serpent de 3 segments a une position random."""
        # longueur initiale du serpent
        snake_length = 3

        # Generer une position de depart aleatoire en evitant les bords
        margin = snake_length + 1
        start_x = random.randint(margin, self.grid_size - margin - 1)
        start_y = random.randint(margin, self.grid_size - margin - 1)

        # orientation initiale (haut, bas, gauche, droite)
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # (dx, dy)
        current_direction = random.choice(directions)

        # Construire le corps du serpent en fonction de l'orientation
        snake = [(start_x, start_y)]
        for i in range(1, snake_length):
            # Modifier la direction occasionnellement
            if random.random() < 0.3:  # 30% de chance de changer de direction
                current_direction = random.choice(directions)

            # Ajouter les segments en suivant la direction
            new_x = snake[-1][0] + current_direction[0]
            new_y = snake[-1][1] + current_direction[1]
            snake.append((new_x, new_y))

        # retourne la liste des segments du serpent
        return snake

    def _place_apples_randomly(self, num_apples):
        """Place les pommes a des positions random."""
        # genere des positions uniques pour les pommes
        all_pos = set((x, y) for x in range(1, self.grid_size - 2) for y in range(1, self.grid_size - 2))
        occupied = set(self.snake) | set(self.green_apples) | {self.red_apple}  # empeche les pommes d'apparaitre sur le snake ou sur d'autres apples
        available_pos = list(all_pos - occupied)
        return random.sample(available_pos, num_apples)

    def get_snake_vision(self):
        """Donne la vue depuis la tete du serpent sous forme d'un vecteur."""
        if len(self.snake) == 0:
            print("Erreur: le serpent est vide. Reinitialisation necessaire.")
            return
        head_x, head_y = self.snake[0]  # Coordonnees de la tete

        # Init une vue vide
        vision_grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        # Ajouter les elements visibles dans la rangee
        for x, y in self.snake:
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                vision_grid[y][x] = 1  # 1 = Serpent

        for x, y in self.green_apples:
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                vision_grid[y][x] = 2  # 2 = Green Apples

        rx, ry = self.red_apple
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            vision_grid[ry][rx] = 3  # 3 = Red Apple

        # print("Grille vision :")
        # for row in vision_grid:
        #     print(row)

        # Vérifiez que head_x et head_y sont valides
        if not (0 <= head_x < self.grid_size and 0 <= head_y < self.grid_size):
            raise ValueError(f"Tête hors des limites : head_x={head_x}, head_y={head_y}")

        # Extraire les visions horizontale et verticale
        horizontal_view = [vision_grid[head_y][x] for x in range(self.grid_size)]
        vertical_view = [vision_grid[y][head_x] for y in range(self.grid_size)]

        # Combiner les vues pour former un vecteur unique
        combined_view = horizontal_view + vertical_view
        return combined_view

    def get_new_direction(self, action):
        """Determine la nouvelle direction en fonction de l'action."""
        directions = ['haut', 'droite', 'bas', 'gauche']
        idx = directions.index(self.current_direction)

        if action == 1:  # Tourner a gauche
            idx = (idx - 1) % 4
        if action == 2:  # Tourner a droite
            idx = (idx + 1) % 4
        return directions[idx]

    def step(self, action):
        """Applique l'action, maj l'etat du jeu, et retourne reward + etat."""
        if len(self.snake) == 0:
            print("Erreur: le serpent est vide. Reinitialisation necessaire.")
            self.reward -= 10
            return self.reward, True  # Penalisation et terminaison du jeu

        head_x, head_y = self.snake[0]  # Coordonnees de la tete

        # print(f"current head = ({head_x}, {head_y})")

        # Calculer la nouvelle direction en fonction de l'action
        self.current_direction = self.get_new_direction(action)

        # Calculer la nouvelle position de la tete
        if self.current_direction == 'haut':  # Haut
            new_head = (head_x, head_y - 1)
        elif self.current_direction == 'bas':  # Bas
            new_head = (head_x, head_y + 1)
        elif self.current_direction == 'gauche':  # Gauche
            new_head = (head_x - 1, head_y)
        elif self.current_direction == 'droite':  # Droite
            new_head = (head_x + 1, head_y)

        # Verifier les collision (serpent et murs)
        if new_head in self.snake[1:] or new_head[0] < 0 or new_head[1] < 0 or new_head[0] >= self.grid_size or new_head[1] >= self.grid_size:
            # print(f"Collision avec le mur : {new_head}")
            self.reward -= 20
            return self.reward, True  # Collision == grosse punition et fin de partie

        # Ajouter la nouvelle tete
        self.snake.insert(0, new_head)

        # Gestion des pommes
        if new_head in self.green_apples:
            self.green_apples.remove(new_head)
            self.reward += 10
            new_apple = self._place_apples_randomly(1)[0]
            self.green_apples.append(new_apple)  # Ajoute la nouvelle pomme verte
        elif new_head == self.red_apple:
            self.reward -= 5
            self.red_apple = self._place_apples_randomly(1)[0]
            # print(f"On est sur une pomme rouge. snake = {self.snake}")
            # Vérifier que le serpent a au moins deux segments avant de retirer le dernier
            if len(self.snake) > 2:
                self.snake.pop()  # Retirer les 2 derniers segment car on a allonge le serpent lors de son avancee
                self.snake.pop()
            elif len(self.snake) > 1:
                self.snake.pop()  # Ne retirer qu'un seul segment si le serpent n'en a qu'un
                # print(f"On a mange la pomme rouge. Snake = {self.snake}")
            else:
                print("Le serpent ne peut pas perdre plus de segments !")
        else:
            self.snake.pop()
            self.reward -= 1

        # Gestion de la taille du serpent
        if len(self.snake) >= self.goal:
            self.reward += 50
            print(f"Congratulations : you reached a snake size of {self.goal} !")
            self.goal += 5

        if len(self.snake) == 0:
            print("Your snake is dead ! You lose.")
            self.reward -= 15
            return self.reward, True

        # head_x, head_y = new_head
        # print(f"new head = ({head_x}, {head_y})")

        return self.reward, False  # Retourner la recompense et l'indicateur de fin

    def reset(self):
        """Reinitialise le jeu avec un placement aleatoire."""
        self.snake = self._place_snake_randomly()
        self.green_apples = self._place_apples_randomly(2)
        self.red_apple = self._place_apples_randomly(1)[0]
        self.done = False
        self.reward = 0
        self.current_direction == 'haut'  # Reinit la direction
        return self.get_state()

    def get_state(self):
        """Retourne l'etat du jeu (positions du serpent et des pommes)."""
        return self.snake, self.green_apples, self.red_apple
