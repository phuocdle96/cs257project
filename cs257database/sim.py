import mysql.connector
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from Gentic_Algo_pyhton import GeneticAlgorithm
from Ant_colony_algo_python import AntColonyOptimization
from deap import base, creator, tools
from functools import partial


def get_table_row_counts():
    # connection = mysql.connector.connect(
    #     host="localhost",
    #     user="root",
    #     password="",
    #     database="testings"
    # )

    connection = sqlite3.connect('join-order-benchmark/backup_database.db')

    cursor = connection.cursor()
    tables = ['company_type', 'info_type', 'movie_companies', 'movie_info_idx', 'title', 'cinema']
    row_counts = {}

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        row_count = cursor.fetchone()[0]
        row_counts[table] = row_count

    return row_counts


def create_distance_matrix(row_counts, reduction_factor_matrix):
    tables = list(row_counts.keys())
    n_tables = len(tables)
    distance_matrix = np.zeros((n_tables, n_tables))

    for i in range(n_tables):
        for j in range(n_tables):
            if i != j:
                distance_matrix[i][j] = int(row_counts[tables[i]] *
                                            row_counts[tables[j]] * reduction_factor_matrix[i][j])

    return distance_matrix


def fitness_function(individual, distance_matrix):
    total_cost = 0
    for i in range(len(individual) - 1):
        total_cost += distance_matrix[individual[i]][individual[i + 1]]
    return total_cost,


def compare_algorithms(table_reduced_rows, reduction_factor_matrix):
    row_counts = table_reduced_rows
    distance_matrix = create_distance_matrix(row_counts, reduction_factor_matrix)

    # ACO Parameters
    n_ants = 10
    n_iterations = 100
    alpha = 1
    beta = 1
    rho = 0.5
    q = 100

    aco = AntColonyOptimization(
        distance_matrix, n_ants, n_iterations, alpha, beta, rho, q)
    aco_best_tour, aco_best_cost = aco.solve()

    # GA Parameters
    population_size = 100
    gene_length = len(row_counts)
    generations = 10
    crossover_probability = 0.8
    mutation_probability = 0.2

    # Pass the distance_matrix to the fitness_function using partial
    fitness_function_with_distance_matrix = partial(
        fitness_function, distance_matrix=distance_matrix)

    ga = GeneticAlgorithm(
        fitness_function_with_distance_matrix, population_size, gene_length, generations,
        crossover_probability, mutation_probability,
        tools.selTournament, tools.cxPartialyMatched, tools.mutShuffleIndexes
    )
    ga_best_individual, ga_best_cost = ga.evolve()

    print("ACO Best Tour:", aco_best_tour)
    print("ACO Best Cost:", aco_best_cost)
    print("GA Best Individual:", ga_best_individual)
    print("GA Best Cost:", ga_best_cost)

    # Plot a bar chart comparing the performance of ACO and GA
    algorithms = ['ACO', 'GA']
    costs = [aco_best_cost, ga_best_cost]

    plt.bar(algorithms, costs)
    plt.xlabel('Algorithms')
    plt.ylabel('Cost')
    plt.title('Comparison of ACO and GA')
    plt.show()

    return aco_best_cost, ga_best_cost

# Call the compare_algorithms function to run the comparison and plot the graph
# compare_algorithms()
