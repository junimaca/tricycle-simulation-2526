import os
import sys
import time
import json
from datetime import datetime
import traceback
from numpy import random

# Add the generator directory to Python path
generator_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, generator_dir)

from scenarios.real import Simulator
import config

# Global configuration
NUM_SEEDS = 12  # Number of seeds

def save_progress(all_results, data_dir):
    """Save current progress to a temporary file"""
    temp_file = os.path.join(data_dir, 'simulation_progress.json')
    with open(temp_file, 'w') as f:
        json.dump(all_results, f, indent=2)

def load_progress(data_dir):
    """Load progress from temporary file if it exists"""
    temp_file = os.path.join(data_dir, 'simulation_progress.json')
    if os.path.exists(temp_file):
        with open(temp_file, 'r') as f:
            return json.load(f)
    return None

def run_simulation(num_trikes, lambdas, algos=False,  use_smart_scheduler=True, trike_capacity=4, seed=None, max_retries=10, max_wait_time=300, s_enqueue_radius_meters=20, enqueue_radius_meters=20, maxCycles=2):
    """
    Run a single simulation with the given parameters.
    
    Args:
        num_trikes (int): Number of tricycles to simulate
        lambdas: spawn rates of passengers in the sectors of the map
        algos: determines if trike will have a forward bias algorithm (True) or random choice algorithm (False) at the intersections
        use_smart_scheduler (bool): Whether to use smart scheduling or FIFO
        trike_capacity (int): Capacity of each tricycle
        seed (str): Seed string for reproducibility
        max_retries (int): Maximum number of retries for failed simulations
        max_wait_time (int): Maximum wait time between retries in seconds
        s_enqueue_radius_meters (float): Radius for enqueueing when tricycle is serving passengers
        enqueue_radius_meters (float): Radius for enqueueing when tricycle is not serving passengers
        maxCycles (int): Maximum number of cycles before generating new path
    Returns:
        dict: Simulation results or None if all retries failed
    """
    # Common parameters
    params = {
        'totalTrikes': num_trikes,
        'totalTerminals': 2,
        'roadPassengerChance': 1.0,
        'roamingTrikeChance': 1.0,
        'trikeConfig': {
            'capacity': trike_capacity,
            'speed': 5.556,  # 20 km/h in meters per second
            'scheduler': None,  # Will be set by Simulator based on useSmartScheduler
            'useMeters': True,
            'maxCycles': maxCycles,
            's_enqueue_radius_meters': s_enqueue_radius_meters,
            'enqueue_radius_meters': enqueue_radius_meters
        },
        'useFixedHotspots': True,
        'useFixedTerminals': False,
        'useSmartScheduler': use_smart_scheduler,
        'trikeCapacity': trike_capacity,
        'isRealistic': True,
        'passengerSpawnRates': lambdas, #added 
        'useSmartIntersectionAlgorithm': algos,
        'totalPassengers': 20
    }
    
    attempt = 0
    total_wait_time = 0
    last_error = None
    
    while attempt < max_retries:
        try:
            # Create simulator instance
            simulator = Simulator(**params)
            
            # Run simulation
            print(f"\nRunning simulation with {num_trikes} tricycles (capacity: {trike_capacity}, s_radius: {s_enqueue_radius_meters}, e_radius: {enqueue_radius_meters}, maxCycles: {maxCycles}, seed: {seed}, attempt: {attempt + 1}/{max_retries})")
            start_time = time.time()
            
            results = simulator.run(seed=seed, maxTime=7200, fixedHotspots=config.MAGIN_HOTSPOTS, fixedTerminals=config.MAGIN_TERMINALS)
            end_time = time.time()
            
            # Add execution time and metadata to results
            results['execution_time_seconds'] = end_time - start_time
            results['metadata'] = {
                'num_trikes': num_trikes,
                'lambdas': lambdas,
                'use_smart_intersection_algorithm': algos,
                'use_smart_scheduler': use_smart_scheduler,
                'trike_capacity': trike_capacity,
                'seed': seed,
                'attempt': attempt + 1,
                'total_retries': attempt,
                'total_wait_time': total_wait_time,
                's_enqueue_radius_meters': s_enqueue_radius_meters,
                'enqueue_radius_meters': enqueue_radius_meters,
                'maxCycles': maxCycles
            }
            
            print(f"Simulation completed in {results['execution_time_seconds']:.2f} seconds")
            return results
            
        except Exception as e:
            last_error = e
            print(f"Error running simulation (attempt {attempt + 1}/{max_retries}): {str(e)}")
            
            # Calculate wait time with exponential backoff
            wait_time = min(5 * (2 ** attempt), max_wait_time)  # Start with 5s, double each time, but cap at max_wait_time
            total_wait_time += wait_time
            
            if "OSRM" in str(e):
                print(f"OSRM server error detected, waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                # For non-OSRM errors, wait a shorter time
                wait_time = min(wait_time / 2, 30)  # Cap at 30 seconds for non-OSRM errors
                print(f"Error detected, waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            
            attempt += 1
            continue
    
    print("All retry attempts failed")
    print("Last error:", str(last_error))
    print("Full error traceback:")
    print(traceback.format_exc())
    return None

def print_progress(completed_simulations, total_simulations):
    """Print progress update for all groups"""
    print(f"\nProgress Update:")
    print(f"{completed_simulations}/{total_simulations} simulations completed ({(completed_simulations/total_simulations)*100:.1f}%)")
    print("########################################################")

def main():
    # Create data directory if it doesn't exist
    data_dir = os.path.join('data', 'real')
    os.makedirs(data_dir, exist_ok=True) 

    # Try to load existing progress
    all_results = load_progress(data_dir)
    if all_results is None:
        all_results = {
            'timestamp': datetime.now().isoformat(),
            'simulations': []
        }
    
    # Initialize progress counters
    completed_simulations = 0

    # Test parameters for each group

    tricycle_counts = [5, 10, 15, 20]
    lambdas = [
                [[37.5, 75], [75, 37.5]],
                [[56.25, 112.5, 56.25], [112.5, 56.25, 112.5]],
                [[75, 150, 75, 150], [150, 75, 150, 75]],
              ]
    algorithms = [True, False]

    seeds = [int(x) for x in random.randint(10**9, size=NUM_SEEDS)]
    print(seeds)

    # Calculate total number of simulations 
    total_simulations = len(tricycle_counts) * len(lambdas) * len(algorithms) * len(seeds)

    def update_progress():
        print_progress(completed_simulations, total_simulations)

    for i in range(len(seeds)):
        current_seed = seeds[i]

        for count in tricycle_counts:
            for lam in lambdas:
                for algo in algorithms:
                    print(f"Seed {i+1}: {current_seed}")
                    if algo:
                        print(f"Parameters: {count} tricycles, {len(lam) * len(lam[0])} sectors, uses smart intersection algorithm")
                    else:
                        print(f"Parameters: {count} tricycles, {len(lam) * len(lam[0])} sectors, uses basic intersection algorithm")
                    # print(f"Parameters: capacity=4, ")
                    results = run_simulation(
                        num_trikes=count,
                        lambdas=lam,
                        algos=algo,
                        use_smart_scheduler=True,
                        trike_capacity=4,
                        seed=current_seed,
                        s_enqueue_radius_meters=20,
                        enqueue_radius_meters=20,
                        maxCycles=2
                    )
                    if results:
                        all_results['simulations'].append(results)
                        save_progress(all_results, data_dir)
                        completed_simulations += 1
                        update_progress()

    # Save final results
    final_file = os.path.join(data_dir, f'simulation_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    with open(final_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Clean up progress file
    progress_file = os.path.join(data_dir, 'simulation_progress.json')
    if os.path.exists(progress_file):
        os.remove(progress_file)

    print(f"\nFinal Progress Summary:")
    print(f"Total simulations completed: {completed_simulations}/{total_simulations} ({(completed_simulations/total_simulations)*100:.1f}%)")
    print(f"Final results saved to: {final_file}")

if __name__ == '__main__':
    main() 