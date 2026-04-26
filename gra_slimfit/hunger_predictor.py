import numpy as np

def daily_hunger_curve(calories, protein_g, fiber_g, tdee, n_points=4):
    """
    Returns an array of hunger values (0-10) for n_points times during the day.
    Simple linear model based on energy deficit, protein, fiber.
    """
    deficit = tdee - calories
    # Baseline hunger from deficit (kcal)
    deficit_factor = np.clip(deficit / 500, 0, 2)  # 500 kcal deficit gives hunger 5?
    hunger_base = deficit_factor * 2.5  # scale to 0-5

    # Protein and fiber reduce hunger (satiety)
    satiety = 0.02 * protein_g + 0.03 * fiber_g  # empirical
    hunger = hunger_base - satiety
    # Add some circadian variation: evening slightly higher
    time_mult = np.linspace(0.8, 1.2, n_points)
    hunger = hunger * time_mult
    return np.clip(hunger, 0, 10)

def daily_hunger_stats(calories, protein_g, fiber_g, tdee):
    """
    Return max, amplitude (max-min), and average hunger for a single day.
    """
    hunger = daily_hunger_curve(calories, protein_g, fiber_g, tdee)
    return np.max(hunger), np.ptp(hunger), np.mean(hunger)
