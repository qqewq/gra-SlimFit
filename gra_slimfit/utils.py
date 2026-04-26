import matplotlib.pyplot as plt
from .metabolism_model import simulate_plan

def plot_results(cal, prot, fib, initial_weight=80, height=1.70, age=30, sex='male'):
    weight_arr, fat_arr, ffm_arr, tdee_arr = simulate_plan(
        cal, prot, fib, initial_weight, height, age, sex
    )
    days = range(len(weight_arr))
    plt.figure(figsize=(12,8))
    plt.subplot(2,2,1)
    plt.plot(days, weight_arr, label='Weight')
    plt.title('Weight')
    plt.subplot(2,2,2)
    plt.plot(days, fat_arr, label='Fat mass')
    plt.plot(days, ffm_arr, label='FFM')
    plt.legend()
    plt.title('Body composition')
    plt.subplot(2,2,3)
    plt.plot(days, cal, label='Calories')
    plt.plot(days, tdee_arr, '--', label='TDEE')
    plt.legend()
    plt.title('Energy intake vs TDEE')
    plt.subplot(2,2,4)
    plt.plot(days, prot, label='Protein')
    plt.plot(days, fib, label='Fiber')
    plt.legend()
    plt.title('Macronutrients')
    plt.tight_layout()
    plt.show()
