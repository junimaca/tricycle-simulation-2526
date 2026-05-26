import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime
import time

main_dataframe = None

class SimulationRun:
    def __init__(self, run_dir):
        """Initialize from a simulation run directory"""
        self.run_dir = run_dir
        
        # Load metadata
        with open(os.path.join(run_dir, 'metadata.json'), 'r') as f:
            metadata = json.load(f)
            self.metadata = metadata
            self.seed = metadata["seed"]
            self.numTrikes = metadata['totalTrikes']
            self.numPassengers = metadata['totalPassengers']
            self.numSectors = metadata['totalSectors']
            self.useSmartIntersectionAlgorithm = metadata['smartIntersectionAlgorithm']
            self.useSmartScheduler = metadata['smartScheduling']
            self.trikeCapacity = metadata['trikeConfig']['capacity']
            self.s_enqueue_radius = metadata['trikeConfig']['s_enqueue_radius_meters']
            self.enqueue_radius = metadata['trikeConfig']['enqueue_radius_meters']
            self.maxCycles = metadata['trikeConfig']['maxCycles']
        
        # Load summary statistics
        with open(os.path.join(run_dir, 'summary.json'), 'r') as f:
            self.summary = json.load(f)
        
        # Load passenger data
        self.passengers = []
        for filename in os.listdir(run_dir):
            if filename.startswith('passenger_') and filename.endswith('.json'):
                with open(os.path.join(run_dir, filename), 'r') as f:
                    passenger_data = json.load(f)
                    passenger = {
                        "waitingTime": passenger_data['pickupTime'] - passenger_data['createTime'],
                        "travelingTime": passenger_data['deathTime'] - passenger_data['pickupTime'],
                        "waitingTimeSeconds": passenger_data['pickupTime'] - passenger_data['createTime'],
                        "travelingTimeSeconds": passenger_data['deathTime'] - passenger_data['pickupTime']
                    }
                    self.passengers.append(passenger)
        
        # Load tricycle data
        self.trikes = []
        for filename in os.listdir(run_dir):
            if filename.startswith('trike_') and filename.endswith('.json'):
                with open(os.path.join(run_dir, filename), 'r') as f:
                    trike_data = json.load(f)
                    trike = {
                        "totalDistance": trike_data['totalDistance'],
                        "productiveDistance": trike_data['productiveDistance'],
                        "waitingTimeSeconds": max(0, trike_data['waitingTime']),
                        "speed": trike_data['speed'],
                        "productiveTravelTimeSeconds": trike_data['totalProductiveDistanceM']/trike_data['speed'],
                        "unproductiveTravelTimeSeconds": (trike_data['totalDistance']-trike_data['productiveDistance'])/trike_data['speed']
                    }
                    trike["totalTimeSeconds"] = trike["waitingTimeSeconds"] + trike["productiveTravelTimeSeconds"] + trike["unproductiveTravelTimeSeconds"]
                    self.trikes.append(trike)

def initialize_main_dataframe():
    global main_dataframe

    main_dataframe = pd.DataFrame(columns=[
        'Number of Tricycles', 'Number of Sectors', 'Intersection Algorithm', 'Number of Passengers', 'Total Trips Completed', 'Completion Rate', 'Average Wait Time', 'Average Travel Time', 'Total Distance', 'Productive Distance', 'Efficiency Percentage'
    ])

def main():
    global main_dataframe

    # Initialize Pandas dataframe 
    initialize_main_dataframe()

    # Create figures directory if it doesn't exist
    os.makedirs('figures', exist_ok=True)
    
    # Load simulation results
    print("\nLoading simulation results...")
    simulations = []

    cutoff_time = 1779818400

    
    # Look for simulation directories
    data_dir = os.path.join('data', 'real')
    for run_dir in os.listdir(data_dir):
        run_path = os.path.join(data_dir, run_dir)
        if os.path.isdir(run_path) and not run_dir.startswith('.'):
            # modified_time = os.path.getmtime(run_path)

            # if modified_time < cutoff_time:
            #     continue

            try:
                simulation = SimulationRun(run_path)
                simulations.append(simulation)
                algo_name = "smart" if simulation.useSmartIntersectionAlgorithm else "basic"
                print(f"Loaded simulation with {simulation.numTrikes} tricycles, {simulation.numPassengers} passengers, {simulation.numSectors} sectors, uses {algo_name} intersection algorithm")
            
                new_row = pd.DataFrame({
                    'Seed': [simulation.seed],
                    'Number of Tricycles': [simulation.numTrikes],
                    'Number of Sectors': [simulation.numSectors],
                    'Intersection Algorithm': [algo_name],
                    'Number of Passengers': [simulation.numPassengers],
                    'Total Trips Completed': [simulation.summary['total_trips_completed']],
                    'Completion Rate': [simulation.summary['completion_rate']],
                    'Average Wait Time': [simulation.summary['average_wait_time']],
                    'Average Travel Time': [simulation.summary['average_travel_time']],
                    'Total Distance': [simulation.summary['total_distance_km']],
                    'Productive Distance': [simulation.summary['productive_distance_km']],
                    'Efficiency Percentage': [simulation.summary['efficiency_percentage']]
                })
                main_dataframe = pd.concat([main_dataframe, new_row], ignore_index=True)

            except Exception as e:
                print(f"Failed to load simulation {run_dir}: {str(e)}")
                continue

    print(f"\nTotal simulations loaded: {len(simulations)}")
    
    main_dataframe.to_csv('csv/newer_sims.csv')

if __name__ == '__main__':
    main() 