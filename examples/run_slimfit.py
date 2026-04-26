from gra_slimfit.optimizer import optimize
from gra_slimfit.utils import plot_results
from gra_slimfit.metabolism_model import simulate_plan

if __name__ == "__main__":
    best_cal, best_prot, best_fib, fitness, _ = optimize(
        initial_weight=85.0, target_weight=75.0, duration_days=150,
        pop_size=30, ngen=50
    )
    print(f"Best fitness: {fitness:.4f}")
    print(f"Final weight (simulated): {simulate_plan(best_cal, best_prot, best_fib, initial_weight=85, duration_days=150)[0][-1]:.1f} kg")
    plot_results(best_cal, best_prot, best_fib, initial_weight=85)
