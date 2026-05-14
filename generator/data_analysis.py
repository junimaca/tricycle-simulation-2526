import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime

def main():
    # Create figures directory if it doesn't exist
    os.makedirs('figures', exist_ok=True)
    
    # Load simulation results
    print("\nLoading simulation results...")
    simulations = []
    
    # Look for simulation directories
    data_dir = os.path.join('data', 'real')
    for run_dir in os.listdir(data_dir):
        run_path = os.path.join(data_dir, run_dir)
        if os.path.isdir(run_path) and not run_dir.startswith('.'):
            try:
                simulation = SimulationRun(run_path)
                simulations.append(simulation)
                print(f"Loaded simulation with {simulation.numTrikes} tricycles, capacity {simulation.trikeCapacity}, s_radius {simulation.s_enqueue_radius}, e_radius {simulation.enqueue_radius}, maxCycles {simulation.maxCycles}")
            except Exception as e:
                print(f"Failed to load simulation {run_dir}: {str(e)}")
                continue

    print(f"\nTotal simulations loaded: {len(simulations)}")
    
    if len(simulations) == 0:
        print("\nNo valid simulations found! Check the following:")
        print("1. Are there any simulation results in data/real/ directory?")
        print("2. Do the simulation results have the correct format?")
        return

    # Group A: Number of tricycles (smart scheduling, capacity 3, s_radius=50, e_radius=100, maxCycles=2)
    group_a_sims = [x for x in valid_simulations 
                   if x.useSmartScheduler 
                   and x.trikeCapacity == 3 
                   and x.s_enqueue_radius == 50 
                   and x.enqueue_radius == 100 
                   and x.maxCycles == 2]
    if group_a_sims:
        x_values = [x.numTrikes for x in group_a_sims]
        plot_metric(group_a_sims, x_values, "Number of Tricycles", "Number of Tricycles", "A")
        print(f"Generated Group A figures (Number of Tricycles) - {len(group_a_sims)} simulations")
        print(f"Found tricycle counts: {sorted(set(x_values))}")



    print("\nAll figures have been generated in the 'figures' directory")

if __name__ == '__main__':
    main() 