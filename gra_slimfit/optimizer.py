import numpy as np
from deap import base, creator, tools, algorithms
from .foam_calculators import StaticFoam, CyclicFoam, ChaoticFoam
from .metabolism_model import simulate_plan
from .hunger_predictor import daily_hunger_stats
import random

def optimize(initial_weight=80.0, height=1.70, age=30, sex='male',
             target_weight=70.0, duration_days=180, pop_size=50, ngen=100,
             lambda_static=0.5, lambda_cycle=0.3, lambda_chaos=0.2,
             cal_bounds=(1200, 3500), protein_bounds=(50, 200), fiber_bounds=(10, 50)):
    """Evolve a daily calorie, protein, fiber plan."""

    # Precompute a simple initial plan: even deficit, high protein
    bmr_est = (10*initial_weight + 6.25*100*height - 5*age + 5) if sex=='male' else (10*initial_weight + 6.25*100*height - 5*age - 161)
    tdee_est = bmr_est * 1.2
    target_deficit = 500  # kcal/day
    init_cal = max(cal_bounds[0], tdee_est - target_deficit)

    n_genes = duration_days * 3  # each day: cal, prot, fiber
    def random_plan():
        plan = []
        for _ in range(duration_days):
            cal = random.uniform(cal_bounds[0], cal_bounds[1])
            prot = random.uniform(protein_bounds[0], protein_bounds[1])
            fib = random.uniform(fiber_bounds[0], fiber_bounds[1])
            plan.extend([cal, prot, fib])
        return plan

    def decode(individual):
        # returns daily_cal, daily_protein, daily_fiber as lists
        cal = [individual[i] for i in range(0, n_genes, 3)]
        prot = [individual[i+1] for i in range(0, n_genes, 3)]
        fib = [individual[i+2] for i in range(0, n_genes, 3)]
        # Ensure bounds
        cal = np.clip(cal, cal_bounds[0], cal_bounds[1])
        prot = np.clip(prot, protein_bounds[0], protein_bounds[1])
        fib = np.clip(fib, fiber_bounds[0], fiber_bounds[1])
        return cal, prot, fib

    def evaluate(individual):
        cal, prot, fib = decode(individual)
        # Simulate
        weight_arr, fat_arr, ffm_arr, tdee_arr = simulate_plan(
            cal, prot, fib, initial_weight, height, age, sex, duration_days=duration_days
        )
        # Static foam
        static_foam = StaticFoam(target_weight=target_weight, 
                                healthy_fat_pct=0.15, max_weight_loss=20.0,
                                pred_rmr=1500.0)
        phi_static = static_foam(weight_arr, fat_arr, ffm_arr, tdee_arr)

        # Cyclic foam (need daily hunger max)
        hunger_max_arr = []
        for d in range(duration_days):
            max_h, _, _ = daily_hunger_stats(cal[d], prot[d], fib[d], tdee_arr[d])
            hunger_max_arr.append(max_h)
        cyclic_foam_obj = CyclicFoam(cal, prot, fib, tdee_arr)
        phi_cycle = cyclic_foam_obj()

        # Chaotic foam
        chaotic_foam_obj = ChaoticFoam(weight_arr, hunger_max_arr)
        phi_chaos = chaotic_foam_obj()

        total = lambda_static * phi_static + lambda_cycle * phi_cycle + lambda_chaos * phi_chaos
        # Penalize unrealistic muscle loss
        if ffm_arr[-1] < ffm_arr[0] * 0.8:  # >20% FFM loss
            total += 100
        return (total,)

    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register("attr_float", random.random)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=n_genes)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evaluate)
    toolbox.register("mate", tools.cxBlend, alpha=0.5)
    toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.1, indpb=0.1)
    toolbox.register("select", tools.selTournament, tournsize=3)

    pop = toolbox.population(n=pop_size)
    hof = tools.HallOfFame(5)
    stats = tools.Statistics(lambda ind: ind.fitness.values[0])
    stats.register("avg", np.mean)
    stats.register("min", np.min)

    algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=ngen,
                        stats=stats, halloffame=hof, verbose=True)
    best = hof[0]
    best_cal, best_prot, best_fib = decode(best)
    return best_cal, best_prot, best_fib, best.fitness.values[0], hof
