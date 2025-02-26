"""Launch program.

Ce programme recupere les arguments optionnels en ligne de commande,
et lance le programme d'apprentissage. Options:
- taille de la grille (--grid_size)
- affichage du jeu pendant la phase d'apprentissage (--display)
- nombre de sessions de jeu (--sessions)
- delai d'affichage pour lisibilite (--delay)
- nombre de segments de serpent a atteindre (--goal)
- commencer a partir de sessions deja crees: save models / load models (--load)
A RAJOUTER
- learn ou don't learn
- implementer une lifetime
"""
import argparse
import pickle
import pygame
import sys
import time

import matplotlib.pyplot as plt
from snakegame import SnakeGame
from agent import QLearningAgent
from display import draw_game_display, display_snake_vision

MAX_STEPS = 500


def close_on_enter(event: any) -> None:
    """Close the figure when the Enter key is pressed."""
    if event.key == "enter":  # Si la touche 'Enter' est pressée
        plt.close(event.canvas.figure)  # Ferme la figure associée


def pause(DISPLAYSURF, paused=None):
    """Gestion de la pause avec ESPACE."""
    # Gestion des evenements clavier
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused  # Bascule l'etat de pause

    # Si en pause, attendre jusqu'a reprise
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                paused = not paused  # Reprise
        # Affichage d'un message pendant la pause
        if DISPLAYSURF:
            font = pygame.font.SysFont(None, 36)
            text = font.render(
                "PAUSE - Appuyer sur ESPACE pour continuer.",
                True, (255, 255, 255)
                )
            text_rect = text.get_rect(
                center=(DISPLAYSURF.get_width() // 2,
                        DISPLAYSURF.get_height() // 2)
                )
            DISPLAYSURF.blit(text, text_rect)
            pygame.display.flip()
        pygame.time.Clock().tick(10)  # Limite FPS pendant la pause
    return paused


def learning_phase(
        game: SnakeGame,
        agent: QLearningAgent,
        DISPLAYSURF=None,
        grid=None,
        mult=None,
        images=None,
        display=False,
        num_sessions=None,
        delay=None,
        vision=None,
        play_mode=False
        ) -> tuple:
    """Phase d'apprentissage du Q-Learning avec affichage optionnel."""
    reward_total = []
    delay = 100
    timer = []

    for session in range(num_sessions):
        state = tuple(game.get_snake_vision())
        session_reward = 0
        session_start = time.time()  # On set un timer
        max_length = game.get_snake_length()
        steps = 0
        game_over = False
        paused = False  # variable pour gerer l'etat de pause

        while not game_over and steps < MAX_STEPS:
            if DISPLAYSURF is not None:
                paused = pause(DISPLAYSURF, paused)

            # Choisir une action via l'agent
            action = agent.get_action(state, play_mode)

            # Effectuer l'action et obtenir la recompense
            reward, game_over = game.step(action)
            session_reward += reward

            # Observer le nouvel etat
            next_state = tuple(game.get_snake_vision())

            # Maj des Q-values si entrainement actif
            if not play_mode:
                agent.update(state, action, reward, next_state)

            # Passer au prochain etat
            state = next_state

            current_length = game.get_snake_length()
            if current_length > max_length:
                max_length = current_length

            steps += 1

            if vision:
                display_snake_vision(game)

            # Affichage pendant l'entrainement
            if DISPLAYSURF is not None and images is not None and display:
                draw_game_display(DISPLAYSURF, game, grid, mult, images)
                pygame.display.flip()
                # paused = not paused
                # Ajouter un delai pour ralentir l'affichage (en millisecondes)
                pygame.time.delay(delay)

        session_end = time.time()
        session_time = session_end - session_start
        # paused = not paused

        reward_total.append(session_reward)
        timer.append(session_time)
        # print(f"session {session}, Recompense totale : {session_reward}")
        if max_length >= game.init_goal:
            print(f"[Session {session}] Game over. "
                  f"Final length={game.get_snake_length()}, "
                  f"max length={max_length}, "
                  f"total reward={session_reward}, steps={steps}")

        # Reinitialiser l'env pour la prochaine session
        game.reset()

        # Reduction progressive d'epsilon apres chaque episode
        if not play_mode:
            agent.decay_epsilon()

    return reward_total, timer


def load_images(mult: int) -> dict:
    """Charge et redimensionne les images."""
    return {
        "green_apple": pygame.transform.scale(pygame.image.load("Graphics/GreenApple.png"), (mult, mult)),
        "red_apple": pygame.transform.scale(pygame.image.load("Graphics/RedApple.png"), (mult, mult)),
        "snake_segment": pygame.transform.scale(pygame.image.load("Graphics/Snake_SegmentBlueIce.png"), (mult, mult)),
        "snake_head": pygame.transform.scale(pygame.image.load("Graphics/Snake_HeadBlueIce.png"), (mult, mult)),
        "floor": pygame.transform.scale(pygame.image.load("Graphics/FloorTile.png"), (mult, mult)),
        "wall": pygame.transform.scale(pygame.image.load("Graphics/WallTile.png"), (mult, mult)),
    }


def save_agent_state(agent: QLearningAgent, filename: str):
    """Sauvegarde l'etat d'un agent entraine dans un fichier."""
    # A TESTER : on retire les etats ou les valeurs sont tres faibles
    # for state in list(agent.q_table.keys()):
        # if max(agent.q_table[state]) < -100:
        #     del agent.q_table[state]
    with open(filename, "wb") as file:
        pickle.dump(agent, file)
    print(f"Etat de l'agent sauvegarde dans {filename}.")


def load_agent_state(filename: str) -> QLearningAgent:
    """Charge l'etat d'un agent a partir d'un fichier."""
    try:
        with open(filename, "rb") as file:
            agent = pickle.load(file)
        print(f"Etat de l'agent charge depuis {filename}.")

        # AFFICHAGE des attributs de l'agent :
        print(f"Alpha: {agent.alpha}")
        print(f"Gamma: {agent.gamma}")
        print(f"Epsilon: {agent.epsilon}")
        print(f"taille de la Q-table: {len(agent.q_table)} etats enregistres.")

        # afficher quelques entrees de la Q-table:
        print("\nQuelques entrees de la Q-table: ")
        for i, (state, actions) in enumerate(agent.q_table.items()):
            print(f"{i}: {state} -> Actions: {actions}")
            # if i == 5:  # Affiche seulement les 5 premiers
            #     break
        print("\n")
        return agent
    except FileNotFoundError:
        print(f"Fichier {filename} introuvable. Entrainement a partir de 0.")
        return None


def calculate_mult_based_on_grid(grid: int, max_window_size=800):
    """Calcule la valeur de mult pour que la fenetre soit de taille definie."""
    return max_window_size // (grid + 2)


def Q_Learning_algo(
        grid: int,
        display: bool,
        sessions: int,
        delay: float,
        vision: bool,
        goal: int,
        alpha: float,
        load: bool,
        play_mode: bool,
        ) -> None:
    """Lance l'apprentissage via Q-Learning, avec ou sans affichage."""
    pygame.init()  # initialize the pygame engine

    # Si mode jeu : forcer une seule session et activer l'affichage
    if play_mode:
        sessions = 1
        display = True

    # Definition du facteur multiplicateur pour passer de grid a pixel
    mult = calculate_mult_based_on_grid(grid)
    fullgrid = grid + 2  # On ajoute des bords murs pour affichage
    WIN_SIZE = fullgrid * mult
    DISPLAYSURF = None
    images = None

    # Creation du jeu
    game = SnakeGame(grid, goal=goal)

    # Gestion du chargement d'un agent deja entraine
    if load:
        load_file = f"agent_state_sessions_{load}.pkl"
        print(f"Chargement de l'agent depuis {load_file}.")
        agent = load_agent_state(load_file)
        if agent is None:
            print("Echec du chagement, creation d'un nouvel agent.")
            agent = QLearningAgent(grid, alpha=alpha)
        if not play_mode:
            agent.epsilon = 0.99
    else:
        print("Pas de session chargee. creation d'un nouvel agent.")
        # print(f"grid = {grid}, play-mode = {play_mode}, alpha = {alpha}")
        agent = QLearningAgent(grid, alpha=alpha)
        # print(agent)

    # Definition de l'affichage si active
    if display:
        # Learning phase avec affichage du jeu :
        DISPLAYSURF = pygame.display.set_mode((WIN_SIZE, WIN_SIZE))
        pygame.display.set_caption("Snake Q-Learning Visualization")
        # Charger et redimensionner les images
        images = load_images(mult)

    # Phase d'apprentissage / de jeu
    reward_total, timer = learning_phase(
        game, agent, DISPLAYSURF, grid, mult, images, display=display,
        num_sessions=sessions, delay=delay, vision=vision, play_mode=play_mode
        )
    # print(f"reward = {reward_total}")

    # Sauvegarder l'etat de l'agent
    if not play_mode:
        save_file = f"agent_state_sessions_{sessions}.pkl"
        print(f"Sauvegarde de l'agent dans {save_file}.")
        save_agent_state(agent, save_file)

    pygame.quit()

    print(f"Temps max d'une session = {(max(timer) * 1000):.2f} ms")

    # Tracer l'evolution des recompenses
    if not play_mode:
        plt.plot(reward_total)
        plt.xlabel("sessions")
        plt.ylabel("Recompenses cumulees")
        plt.title("Progression des recompenses")
        fig = plt.gcf()
        fig.canvas.mpl_connect("key_press_event", close_on_enter)
        plt.show()


def parse_arguments():
    """Recupere tous les arguments optionnels de la ligne de commande."""
    parser = argparse.ArgumentParser(description="Snake Q-Learning options.")
    parser.add_argument(
        "--grid_size",
        type=int,
        default=10,
        help="Taille de la grille du jeu. Par defaut : 10."
    )
    parser.add_argument(
        "--display",
        action="store_true",
        help="Activer l'affichage graphique lors de la phase d'apprentissage."
    )
    parser.add_argument(
        "--sessions",
        type=int,
        default=1000,
        help="Nombre de sessions pour l'apprentissage. Par defaut : 1000."
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.1,
        help="Délai entre chaque frame en secondes (par défaut : 0.1s).",
    )
    parser.add_argument(
        "--vision",
        action="store_true",
        help="Activer l'affichage sur terminal de la vision du serpent."
    )
    parser.add_argument(
        "--goal",
        type=int,
        default=10,
        help="Nombre de segments que le serpent doit atteindre pour finir le jeu. Par defaut: 10."
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.1,
        help="Taux d'apprentissage (learning rate) entre 0.0 et 1.0. Si alpha est grand : l'agent n'apprend rien. Par defaut: 0.1."
    )
    parser.add_argument(
        "--load",
        nargs='?',  # permet un argument optionnel
        const='1',  # valeur par defaut si l'option est fournie sans valeur
        # choices=['1', '10', '100', '1000', '10000', '100000', '1000000'],
        help="Charge un etat d'entrainement (1, 10 ou 100)."
    )
    parser.add_argument(
        "--dontlearn",
        action="store_true",
        help="Jouer avec l'agent sans apprentissage"
    )
    return parser.parse_args()


def main() -> None:
    """Check arguments and options and launch program."""
    args = parse_arguments()

    try:
        Q_Learning_algo(
            grid=args.grid_size,
            display=args.display,
            sessions=args.sessions,
            delay=args.delay,
            vision=args.vision,
            goal=args.goal,
            alpha=args.alpha,
            load=args.load,
            play_mode=args.dontlearn,
            )
    except KeyboardInterrupt:
        print("\nInterruption du programme par l'utilisateur (Ctrl + C)")
        sys.exit(0)
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    main()
