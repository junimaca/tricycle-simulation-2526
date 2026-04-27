import config
import random

from scenarios.real import Simulator, defaultTrikeConfig

if __name__ == '__main__':
    NUM_TRIKES = 1
    NUM_TERMINALS = 1
    NUM_PASSENGERS = 20
    MAX_TIME = 5_000
    TEST_COUNT = 1
    LAMBDAS = [[10000000, 10000000],
               [10000000, 60]]
    
    # Simulation parameters
    S_ENQUEUE_RADIUS_METERS = 20  # Radius for enqueueing when tricycle is serving passengers
    ENQUEUE_RADIUS_METERS = 20  # Radius for enqueueing when tricycle is not serving passengers
    MAX_CYCLES = 2  # Maximum number of cycles a tricycle can roam without picking up passengers
    
    # Create custom trike config
    trike_config = {**defaultTrikeConfig}
    trike_config.update({
        "capacity": 3,
        "s_enqueue_radius_meters": S_ENQUEUE_RADIUS_METERS,
        "enqueue_radius_meters": ENQUEUE_RADIUS_METERS,
        "maxCycles": MAX_CYCLES
    })
    
    # you can look at the code of Simulator for more options
    simulator = Simulator(
        totalTrikes=NUM_TRIKES,
        totalTerminals=NUM_TERMINALS,
        totalPassengers=NUM_PASSENGERS,
        roadPassengerChance=1.0,
        roamingTrikeChance=1.0,
        useFixedHotspots=False, # only use if you have setup hotspots in config
        useFixedTerminals=False, # only use if you have setup hotspots in config
        useSmartScheduler=True,
        trikeConfig=trike_config,
        isRealistic=True, # always set to true
        passengerSpawnRates = LAMBDAS

    )
    for _ in range(TEST_COUNT):
        seed = random.randint(0, 10**9)
        simulator.run(maxTime=MAX_TIME, fixedHotspots=config.MAGIN_HOTSPOTS, fixedTerminals=config.MAGIN_TERMINALS, seed=seed)
