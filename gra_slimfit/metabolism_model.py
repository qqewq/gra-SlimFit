import numpy as np

def simulate_plan(daily_cal, daily_protein, daily_fiber, initial_weight=80.0, height=1.70, age=30, sex='male',
                  activity_factor=1.2, duration_days=180):
    """
    Simplified Hall-like model: weight change based on energy balance.
    Returns arrays: weight_kg, fat_mass_kg, ffm_kg, tdee (daily).
    """
    # Constants
    cal_per_kg_fat = 9400   # kcal/kg
    cal_per_kg_ffm = 1840   # kcal/kg (approximate)

    # Initial body composition estimation (rough)
    bmi = initial_weight / (height ** 2)
    fat_pct = 0.25 if sex == 'male' else 0.32  # average
    fat_mass = initial_weight * fat_pct
    ffm = initial_weight - fat_mass

    # Record arrays
    weight_arr = np.zeros(duration_days)
    fat_arr = np.zeros(duration_days)
    ffm_arr = np.zeros(duration_days)
    tdee_arr = np.zeros(duration_days)

    weight = initial_weight
    for d in range(duration_days):
        # Save state
        weight_arr[d] = weight
        fat_arr[d] = fat_mass
        ffm_arr[d] = ffm

        # TDEE: basic metabolic rate (Mifflin-St Jeor) + activity
        if sex == 'male':
            bmr = 10 * weight + 6.25 * height * 100 - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height * 100 - 5 * age - 161
        # Adaptive thermogenesis: reduce BMR by 0.5% per kg loss beyond 5%
        weight_loss_ratio = (initial_weight - weight) / initial_weight
        adaptation = max(0, (weight_loss_ratio - 0.05) * 0.1)  # 10% reduction per unit
        tdee = (bmr * (1 - adaptation)) * activity_factor
        tdee_arr[d] = tdee

        # Energy balance
        energy_balance = daily_cal[d] - tdee

        # Partitioning: fraction of energy from fat vs FFM (Forbes curve simplified)
        # Assume 80% fat loss if adequate protein; else higher FFM loss
        protein_ratio = daily_protein[d] / max(daily_cal[d], 1e-6)  # protein fraction of calories
        # Optimal protein ~ 0.25-0.3; if below, then more FFM loss
        if protein_ratio < 0.2:
            fat_fraction = 0.6
        elif protein_ratio < 0.3:
            fat_fraction = 0.8
        else:
            fat_fraction = 0.9

        # Fiber bonus: slight increase in satiety and fat oxidation (simulated)
        fiber_g = daily_fiber[d]
        fat_fraction = min(0.95, fat_fraction + 0.001 * fiber_g)

        # Weight change
        if energy_balance < 0:
            deficit = -energy_balance
            fat_loss = deficit * fat_fraction / cal_per_kg_fat
            ffm_loss = deficit * (1 - fat_fraction) / cal_per_kg_ffm
            weight -= (fat_loss + ffm_loss)
            fat_mass -= fat_loss
            ffm -= ffm_loss
        else:
            surplus = energy_balance
            fat_gain = surplus * 0.75 / cal_per_kg_fat
            ffm_gain = surplus * 0.25 / cal_per_kg_ffm
            weight += (fat_gain + ffm_gain)
            fat_mass += fat_gain
            ffm += ffm_gain

        # Ensure non-negative
        fat_mass = max(fat_mass, 1.0)
        ffm = max(ffm, 10.0)
        weight = fat_mass + ffm

    return weight_arr, fat_arr, ffm_arr, tdee_arr
