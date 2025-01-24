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
    def __init__(self, grid_size, num_actions=3, epsilon=0.99, alpha=None, gamma=0.9):
        """Initialisation"""
        self.grid_size = grid_size
        self.num_actions = num_actions  # 0: Haut, 1: Bas, 2: Gauche, 3: Droite
        self.epsilon = epsilon  # Taux d'exploration
        self.alpha = alpha  # Taux d'apprentissage
        self.gamma = gamma  # Facteur de discount

        # Q-table : associe chq etat a une liste de recompenses pr chq action
        self.q_table = {}

    def get_action(self, state):
        """Choisit une action en utilisant la strategie epsilon-greedy."""
        if random.random() < self.epsilon:
            # Exploration : action aleatoire
            return random.randint(0, self.num_actions - 1)
        else:
            # Exploitation : choisir l'action avec la valeur Q la plus elevee
            if state in self.q_table:
                return np.argmax(self.q_table[state])
            else:
                # Si l'etat n'est pas encore connu, initialiser avec des valeurs par defaut
                self.q_table[state] = [0] * self.num_actions
                return random.randint(0, self.num_actions - 1)

    def update(self, state, action, reward, next_state):
        """Met a jour la Q-table selon l'equation Q-Learning."""
        if state not in self.q_table:
            self.q_table[state] = [0] * self.num_actions
        if next_state not in self.q_table:
            self.q_table[next_state] = [0] * self.num_actions

        # EQUATION Q-LEARNING
        old_value = self.q_table[state][action]
        next_max = max(self.q_table[next_state])
        self.q_table[state][action] = old_value + self.alpha * (reward + (self.gamma * next_max) - old_value)
    
    def decay_epsilon(self, decay_rate=0.09, min_epsilon=0.01):
        """Reduit epsilon graduellement apres chaque session."""
        self.epsilon = max(min_epsilon, self.epsilon * decay_rate)
