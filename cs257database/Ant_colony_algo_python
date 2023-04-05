import random
import numpy as np


class AntColonyOptimization:
    # Initializes the distance matrix, number of ants,
    # number of iterations, and other parameters required for the ACO algorithm.
    def __init__(self, distance_matrix, n_ants, n_iterations, alpha, beta, rho, q):
        self.distance_matrix = distance_matrix
        self.n_ants = n_ants
        self.n_iterations = n_iterations
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.q = q

        self.n_nodes = len(distance_matrix)
        self.pheromone_matrix = np.ones((self.n_nodes, self.n_nodes))


    #Calculates the probabilities for an ant to move from its current position to the unvisited nodes.
    # The probabilities are calculated using the pheromone matrix and the visibility of the nodes
    def _calculate_probabilities(self, ant_position, unvisited_nodes, pheromone_matrix):
        probabilities = []

        for node in unvisited_nodes:
            pheromone = pheromone_matrix[ant_position][node] ** self.alpha
            visibility = (
                1 / self.distance_matrix[ant_position][node]) ** self.beta
            probability = pheromone * visibility
            probabilities.append(probability)

        probabilities_sum = sum(probabilities)
        probabilities = [prob / probabilities_sum for prob in probabilities]

        return probabilities

    #Generates a tour for an ant using the pheromone matrix. It starts by randomly selecting the initial node
    # and then iteratively selects the next node to visit based on the probabilities calculated
    # using the _calculate_probabilities() method
    def _generate_tour(self, pheromone_matrix):
        tour = [random.randint(0, self.n_nodes - 1)]
        unvisited_nodes = set(range(self.n_nodes)) - set(tour)

        while unvisited_nodes:
            ant_position = tour[-1]
            probabilities = self._calculate_probabilities(
                ant_position, unvisited_nodes, pheromone_matrix)
            next_node = random.choices(list(unvisited_nodes), probabilities)[0]
            tour.append(next_node)
            unvisited_nodes.remove(next_node)

        return tour

    # Updates the pheromone matrix based on the tours taken by the ants. The pheromone on edge is increased
    # if the edge is included in a tour, and the amount of increase is inversely proportional to the tour cost
    def _update_pheromone_matrix(self, pheromone_matrix, tours):
        updated_pheromone_matrix = (1 - self.rho) * pheromone_matrix

        for tour in tours:
            tour_cost = self._calculate_tour_cost(tour)
            for i in range(len(tour) - 1):
                node_a, node_b = tour[i], tour[i + 1]
                updated_pheromone_matrix[node_a][node_b] += self.q / tour_cost
                updated_pheromone_matrix[node_b][node_a] += self.q / tour_cost

        return updated_pheromone_matrix

    # Calculates the cost of a given tour based on the distance matrix
    def _calculate_tour_cost(self, tour):
        cost = 0
        for i in range(len(tour) - 1):
            node_a, node_b = tour[i], tour[i + 1]
            cost += self.distance_matrix[node_a][node_b]
        return cost

    #Executes the ACO algorithm for the specified number of iterations and returns the best tour and its cost
    def solve(self):
        best_tour = None
        best_tour_cost = float("inf")

        for _ in range(self.n_iterations):
            tours = [self._generate_tour(self.pheromone_matrix)
                     for _ in range(self.n_ants)]
            self.pheromone_matrix = self._update_pheromone_matrix(
                self.pheromone_matrix, tours)

            for tour in tours:
                tour_cost = self._calculate_tour_cost(tour)
                if tour_cost < best_tour_cost:
                    best_tour = tour
                    best_tour_cost = tour_cost

        return best_tour, best_tour_cost
