"""Classe Agent.

epsilon : si epsilon est trop petit, l'agent n'explore pas assez et risque
    d'adopter une strategie sous-optimale.
alpha (taux d'apprentissage) : si alpha est trop grand, l'agent oublie vite
    ses experiences passees.
gamma (future recompense) : si trop petit, l'agent ne considere pas assez les
    recompenses futures.
Combi de base : epsilon= 1.0, alpha=0.1, gamma=0.9
"""
import numpy as np
import random


class QLearningAgent:
    def __init__(self, grid_size, play_mode, num_actions=3, epsilon=0.99, alpha=None, gamma=0.9):
        """Initialisation"""
        self.grid_size = grid_size
        self.num_actions = num_actions  # 0: Haut, 1: Bas, 2: Gauche, 3: Droite
        self.epsilon = epsilon  # Taux d'exploration
        self.alpha = alpha  # Taux d'apprentissage
        self.gamma = gamma  # Facteur de discount

        # Q-table : associe chq etat a une liste de recompenses pr chq action
        # Q-table : dict[ state -> [q_UP, q_LEFT, q_DOWN, q_RIGHT] ]
        self.q_table = {}

    def get_q_values(self, state):
        if state not in self.q_table:
            self.q_table[state] = [0] * self.num_actions
        return self.q_table[state]

    def get_action(self, state, play_mode):
        """Choisit une action en utilisant la strategie epsilon-greedy."""
        qvals = self.get_q_values(state)  # Centralise la recup des valeurs Q

        if play_mode:
            # Exploitation pure (pas d'exploration)
            self.epsilon = 0.1
            return np.argmax(qvals)
            # return max(range(self.num_actions), key=lambda a: qvals[a])

        # Exploration epsilon-greedy
        if random.random() < self.epsilon:
            # Exploration : action aleatoire
            return random.randint(0, self.num_actions - 1)
        else:
            # Exploitation : choisir l'action avec la valeur Q la plus elevee
            return np.argmax(qvals)

    def update(self, state, action, reward, next_state):
        """Met a jour la Q-table selon l'equation Q-Learning."""
        self.q_table[state] = self.get_q_values(state)
        self.q_table[next_state] = self.get_q_values(next_state)

        # EQUATION Q-LEARNING
        old_value = self.q_table[state][action]
        next_max = max(self.q_table[next_state])
        self.q_table[state][action] = old_value + self.alpha * (reward + (self.gamma * next_max) - old_value)
    
    def decay_epsilon(self, decay_rate=0.09, min_epsilon=0.01):
        """Reduit epsilon graduellement apres chaque session."""
        self.epsilon = max(min_epsilon, self.epsilon * decay_rate)
