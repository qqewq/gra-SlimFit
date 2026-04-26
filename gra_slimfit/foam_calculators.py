import numpy as np
from .metabolism_model import simulate_plan
from .hunger_predictor import daily_hunger_stats

class StaticFoam:
    def __init__(self, target_weight=70.0, target_fat_pct=0.2, max_weight_loss=20.0, 
                 healthy_fat_pct=0.15, alpha=None, pred_rmr=1500.0):
        if alpha is None:
            alpha = [0.4, 0.3, 0.2, 0.1]
        self.alpha = alpha
        self.target_weight = target_weight
        self.target_fat_pct = target_fat_pct
        self.max_weight_loss = max_weight_loss
        self.healthy_fat_pct = healthy_fat_pct
        self.pred_rmr = pred_rmr  # predicted resting metabolic rate at target weight

    def __call__(self, weight_arr, fat_arr, ffm_arr, tdee_arr):
        final_weight = weight_arr[-1]
        final_fat_mass = fat_arr[-1]
        final_ffm = ffm_arr[-1]
        final_weight_total = final_fat_mass + final_ffm
        fat_pct = final_fat_mass / final_weight_total if final_weight_total > 0 else 0
        initial_ffm = ffm_arr[0]
        ffm_loss = max(0, initial_ffm - final_ffm)
        # Final RMR approximation (using final day TDEE adjusted for activity)
        final_rmr = tdee_arr[-1] / 1.2  # rough
        # Penalties
        f_weight = ((final_weight - self.target_weight) / self.max_weight_loss) ** 2
        f_fat = ((fat_pct - self.target_fat_pct) / self.healthy_fat_pct) ** 2 if fat_pct > self.target_fat_pct else 0
        f_ffm = (ffm_loss / initial_ffm) ** 2
        f_rmr = max(0, (1 - final_rmr / self.pred_rmr)) ** 2
        return self.alpha[0]*f_weight + self.alpha[1]*f_fat + self.alpha[2]*f_ffm + self.alpha[3]*f_rmr

class CyclicFoam:
    def __init__(self, daily_cal, daily_protein, daily_fiber, tdee_arr, beta=None):
        if beta is None:
            beta = [0.3, 0.4, 0.3]
        self.beta = beta
        self.daily_cal = daily_cal
        self.daily_protein = daily_protein
        self.daily_fiber = daily_fiber
        self.tdee_arr = tdee_arr

    def __call__(self):
        D = len(self.daily_cal)
        total = 0.0
        for d in range(D):
            max_h, amp_h, avg_h = daily_hunger_stats(self.daily_cal[d], self.daily_protein[d],
                                                     self.daily_fiber[d], self.tdee_arr[d])
            deficit_frac = max(0, (self.tdee_arr[d] - self.daily_cal[d]) / self.tdee_arr[d])
            total += self.beta[0] * amp_h**2 + self.beta[1] * max_h**2 + self.beta[2] * deficit_frac**2
        return total / D

class ChaoticFoam:
    def __init__(self, weight_arr, hunger_max_arr, plateau_threshold_days=14, gamma=None):
        if gamma is None:
            gamma = [0.4, 0.3, 0.3]
        self.gamma = gamma
        self.weight_arr = weight_arr
        self.hunger_max_arr = hunger_max_arr
        self.plateau_threshold_days = plateau_threshold_days

    def __call__(self):
        D = len(self.weight_arr)
        weekly_var = np.var(np.diff(self.weight_arr, prepend=self.weight_arr[0])[-min(D,7):])  # variance of recent week changes
        # Days with hunger >= 8 (very high)
        high_hunger_frac = np.mean(np.array(self.hunger_max_arr) >= 8.0)
        # Detect plateaus: periods where weight change < 0.1 kg over plateau_threshold_days
        plateau_count = 0
        i = 0
        while i < D - self.plateau_threshold_days:
            changes = np.abs(np.diff(self.weight_arr[i:i+self.plateau_threshold_days]))
            if np.max(changes) < 0.1:
                plateau_count += 1
                i += self.plateau_threshold_days
            else:
                i += 1
        return self.gamma[0]*weekly_var + self.gamma[1]*high_hunger_frac + self.gamma[2]*plateau_count
