import random
from typing import Callable, List, Tuple
from deap import base, creator, tools


class GeneticAlgorithm:
	#initializing the genetic algorithm by '__init__' method 
	#Calculating fitness of the individual through fitness_function
	#size of population defined by population_size
	#gene_length is the length of each individual's genome
	#generations are the number of generations to evolve the population
	#crossover_probability is the probability of the crossover that will be occurring between two individuals
	#mutation_probability is the individual's mutation probability
	#selection_method is the function which selects the individuals based on the population for the next generation
	#crossover_method is a function which performs crossover between the two individuals
	#tournsize is total number of individuals that are competing in the selection of tournament
	#mutation_method is individual mutation performing function
	
    def __init__(self, fitness_function: Callable, population_size: int, gene_length: int,
                 generations: int, crossover_probability: float, mutation_probability: float,
                 selection_method: Callable, crossover_method: Callable, mutation_method: Callable,
                 tournsize: int = 3, indpb: float = 0.05):  # Add tournsize parameter with a default value of 3
        self.population_size = population_size
        self.generations = generations
        self.crossover_probability = crossover_probability
        self.mutation_probability = mutation_probability

        creator.create("FitnessMax", base.Fitness, weights=(1.0,)) 
        creator.create("Individual", list, fitness=creator.FitnessMax)
	
	#toolbox is used to register the functions which are used by the genetic algorithm
        self.toolbox = base.Toolbox()
        self.toolbox.register("gene", random.randint, 0, 1)
        self.toolbox.register("individual", tools.initRepeat,
                              creator.Individual, self.toolbox.gene, n=gene_length)
        self.toolbox.register("population", tools.initRepeat,
                              list, self.toolbox.individual)

        self.toolbox.register("mate", crossover_method)
        self.toolbox.register("mutate", mutation_method, indpb=indpb)  # Pass indpb parameter to mutShuffleIndexes()
        # Pass tournsize parameter to selTournament()
        self.toolbox.register("select", selection_method, tournsize=tournsize)
	#evaluation of fitness of each individual is done by evaluate method
        self.toolbox.register("evaluate", fitness_function)

    def evolve(self) -> Tuple[List[int], float]:
        population = self.toolbox.population(n=self.population_size)

        for gen in range(self.generations):
            offspring = self.toolbox.select(population, len(population))
            offspring = list(offspring)

            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.crossover_probability:
		    #mate method performs crossover between two individuals with a probability that is specified by crossover_probability.
                    self.toolbox.mate(child1, child2) 		
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < self.mutation_probability:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values

            invalid_individuals = [
                ind for ind in offspring if not ind.fitness.valid]
            fitnesses = self.toolbox.map(
                self.toolbox.evaluate, invalid_individuals)
            for ind, fit in zip(invalid_individuals, fitnesses):
                ind.fitness.values = fit

            population[:] = offspring

        #selBest function is used to select the best individual and the highest fitness value is selected
        best_individual = tools.selBest(population, 1)[0]
        return best_individual, best_individual.fitness.values[0]
