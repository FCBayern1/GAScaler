import random

class GeneticAlgorithm:
    def __init__(self, population_size, mutation_rate, crossover_rate, max_generations, max_replicas, current_replica_count):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.max_generations = max_generations
        self.max_replicas = max_replicas
        self.current_replica_count = current_replica_count

    def initialize_population(self):
        # Generate a random population of solutions
        return [[random.randint(1, self.max_replicas // 2) for _ in range(5)] for _ in range(self.population_size)]

    def penalty(self, individual):
        # Calculate the penalty based on the change in replica count
        total_replicas = sum(individual)
        change_in_replica = abs(self.current_replica_count - total_replicas)
        return change_in_replica if change_in_replica > 2 else 0

    def fitness(self, individual, metrics):
        w1, w2, w3 = 1 / 3, 1 / 3, 1 / 3  # Assuming equal weights for simplicity
        lambda_penalty = 10  # Penalty weight for replica count change

        fitness_value = (w1 * metrics['cpu_usage'] +
                         w2 * metrics['memory_working_set_bytes'] +
                         w3 * metrics['network_transmit_bytes'] -
                         lambda_penalty * self.penalty(individual))

        return fitness_value
    def mutate(self, individual):
        # Implement mutation logic
        if random.random() < self.mutation_rate:
            index = random.randint(0, len(individual) - 1)
            individual[index] = random.randint(1, self.max_replicas)

    def crossover(self, parent1, parent2):
        # Implement crossover logic
        if random.random() < self.crossover_rate:
            index = random.randint(0, len(parent1) - 1)
            child1 = parent1[:index] + parent2[index:]
            child2 = parent2[:index] + parent1[index:]
            return child1, child2
        return parent1, parent2

    def evolve(self, cpu_usage, memory_working_set_bytes,network_transmit_bytes):
        population = self.initialize_population()
        for _ in range(self.max_generations):
            population.sort(key=lambda individual: self.fitness(individual, {'cpu_usage': cpu_usage, 'memory_working_set_bytes': memory_working_set_bytes, 'network_transmit_bytes': network_transmit_bytes}), reverse=True)
            next_population = []
            while len(next_population) < len(population):
                parent1 = random.choice(population)
                parent2 = random.choice(population)
                child1, child2 = self.crossover(parent1, parent2)
                self.mutate(child1)
                self.mutate(child2)
                next_population.extend([child1, child2])
            population = next_population[:self.population_size]
        return population[0][0]  # return the best solution