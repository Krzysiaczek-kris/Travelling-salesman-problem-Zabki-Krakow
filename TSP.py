import numpy as np
import random
import time
from datetime import timedelta
from numba import njit, jit

random.seed(0)
np.random.seed(0)

distance_matrix = np.load('data/distance_matrix.npy')
distance_matrix = distance_matrix / 1000  
distance_matrix = np.round(distance_matrix, 3)     
distance_matrix = (distance_matrix * 100000).astype(np.int32) # centimeter precision

# ------------------------------------------------------------
@njit
def evaluate_route_distance(route, distance_mat):
    total = 0
    for i in range(len(route)-1):
        total += distance_mat[route[i], route[i+1]]
    return total

@jit(nopython=True, parallel=True)
def evaluate_population(population, distance_mat):
    distances = np.zeros(len(population), dtype=np.int32)
    for i in range(len(population)):
        distances[i] = evaluate_route_distance(population[i], distance_mat)
    return distances

@njit
def tournament_select(population, fitness, k=5):
    n = len(population)
    indices = np.random.choice(n, k)
    best_idx = indices[0]
    best_fitness = fitness[best_idx]
    
    for idx in indices[1:]:
        if fitness[idx] < best_fitness:
            best_idx = idx
            best_fitness = fitness[idx]
    
    return population[best_idx].copy()

@njit
def pmx_crossover(parent1, parent2):
    n = len(parent1)
    child = parent2.copy()
    
    start = np.random.randint(0, n-1)
    end = np.random.randint(start+1, n)
    
    pos1 = np.full(n, -1, dtype=np.int32)
    pos2 = np.full(n, -1, dtype=np.int32)
    
    for i in range(n):
        pos1[parent1[i]] = i
        pos2[parent2[i]] = i
    
    for i in range(start, end+1):
        val1 = parent1[i]
        val2 = child[i]
        
        if val1 != val2:
            pos = pos2[val1]
            child[i] = val1
            child[pos] = val2
            pos2[val1] = i
            pos2[val2] = pos
            
    return child

@njit
def mutate(route):
    n = len(route)
    i, j = np.random.randint(0, n, 2)
    route[i], route[j] = route[j], route[i]
    
    i = np.random.randint(0, n-1)
    j = np.random.randint(i+1, n)
    route[i:j+1] = route[i:j+1][::-1]
    return route

@njit
def solve_tsp_numba(distance_mat, pop_size=1000, generations=1000, mutation_rate=0.2):
    n_cities = len(distance_mat)
    
    population = np.zeros((pop_size, n_cities), dtype=np.int32)
    for i in range(pop_size):
        population[i] = np.random.permutation(n_cities)
    
    best_route = population[0].copy()
    best_distance = np.inf
    
    for gen in range(generations):
        if gen % 1000 == 0:
            print(f"Generation: {gen}/{generations}")
        fitness = evaluate_population(population, distance_mat)
        
        min_idx = np.argmin(fitness)
        if fitness[min_idx] < best_distance:
            best_distance = fitness[min_idx]
            best_route = population[min_idx].copy()
        
        new_pop = np.zeros((pop_size, n_cities), dtype=np.int32)
        new_pop[0] = best_route
        
        for i in range(1, pop_size):
            parent1 = tournament_select(population, fitness)
            parent2 = tournament_select(population, fitness)
            child = pmx_crossover(parent1, parent2)
            
            if np.random.random() < mutation_rate:
                child = mutate(child)
            
            new_pop[i] = child
            
        population = new_pop
        
    return best_route, best_distance

def warmup_numba():
    print("Compiling Numba functions...")
    small_distance_mat = np.random.randint(1, 100, size=(10, 10), dtype=np.int32)
    small_pop_size = 10
    small_gens = 2
    
    test_route = np.arange(10, dtype=np.int32)
    evaluate_route_distance(test_route, small_distance_mat)
    
    test_pop = np.array([np.random.permutation(10) for _ in range(small_pop_size)], dtype=np.int32)
    test_fitness = np.random.randint(1, 100, size=small_pop_size, dtype=np.int32)
    
    evaluate_population(test_pop, small_distance_mat)
    tournament_select(test_pop, test_fitness)
    pmx_crossover(test_pop[0], test_pop[1])
    mutate(test_route.copy())
    
    solve_tsp_numba(small_distance_mat, small_pop_size, small_gens)
    print("Compilation complete!")

# ------------------------------------------------------------
if __name__ == "__main__":
    warmup_numba() # Compile Numba functions

    print("Starting main computation")
    start_time = time.time()
    
    route, distance = solve_tsp_numba(distance_matrix, pop_size=5000, generations=50000)
    np.save('data/best_route.npy', route)
    
    print("Best Route:", route.tolist())
    print("Distance:", distance / 100_000, "km")
    print("Elapsed time:", timedelta(seconds=time.time() - start_time))
    print("Valid route:", len(set(route)) == len(route))
