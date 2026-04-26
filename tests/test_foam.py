import unittest
import numpy as np
from gra_slimfit.foam_calculators import StaticFoam, CyclicFoam, ChaoticFoam
from gra_slimfit.metabolism_model import simulate_plan

class TestFoam(unittest.TestCase):
    def setUp(self):
        self.cal = np.ones(30) * 1800
        self.prot = np.ones(30) * 120
        self.fib = np.ones(30) * 25
        self.w, self.fat, self.ffm, self.tdee = simulate_plan(
            self.cal, self.prot, self.fib, initial_weight=80, duration_days=30
        )

    def test_static_foam_positive(self):
        sf = StaticFoam(target_weight=70, target_fat_pct=0.2, max_weight_loss=20)
        val = sf(self.w, self.fat, self.ffm, self.tdee)
        self.assertTrue(val >= 0)

    def test_cyclic_foam(self):
        hunger_max = [5]*30
        cf = CyclicFoam(self.cal, self.prot, self.fib, self.tdee)
        val = cf()
        self.assertTrue(val > 0)

    def test_chaotic_foam(self):
        hunger_max = [2]*30
        chf = ChaoticFoam(self.w, hunger_max)
        val = chf()
        self.assertTrue(val >= 0)

if __name__ == '__main__':
    unittest.main()
