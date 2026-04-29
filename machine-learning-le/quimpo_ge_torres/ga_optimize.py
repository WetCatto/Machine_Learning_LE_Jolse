"""
Genetic Algorithm optimizer for Quimpo Blvd–GE Torres traffic signal timing.

Paper: "Genetic Algorithm Optimization of Traffic Signals: A SUMO Microsimulation
Study of Urban Intersections in Davao City, Philippines"

Chromosome: 5 integers [g0, g2, g4, g6, g8], one green-phase duration per
optimisable green phase (indices 0, 2, 4, 6, 8 in the 10-phase TL program).
Transition/yellow phases (indices 1, 3, 5, 7, 9) are fixed at 5 s.

Usage:
    python ga_optimize.py
Outputs:
    ga_results.csv
    ga_results_best_chromosome.csv
"""

import os
import random
import csv
import xml.etree.ElementTree as ET

os.environ['LIBSUMO_AS_TRACI'] = '1'
import traci  # noqa: E402

# ---------------------------------------------------------------------------
# Paths (relative to this file)
# ---------------------------------------------------------------------------
_DIR        = os.path.dirname(os.path.abspath(__file__))
NET_FILE    = os.path.join(_DIR, 'quimpo-GE_torres.net.xml')
ROUTE_FILE  = os.path.join(_DIR, 'quimpo_traffic_route.rou.xml')
VTYPE_FILE  = os.path.join(_DIR, 'vehicle_types.add.xml')
TTL_FILE    = os.path.join(_DIR, 'trafficl ight.ttl.xml')   # note: space in filename
RESULTS_CSV = os.path.join(_DIR, 'ga_results.csv')

# ---------------------------------------------------------------------------
# GA hyper-parameters (from paper Section 3.3)
# ---------------------------------------------------------------------------
POPULATION_SIZE = 50
TOURNAMENT_SIZE = 3
CROSSOVER_RATE  = 0.8
MUTATION_RATE   = 0.1
N_GENERATIONS   = 40
MIN_GREEN       = 10    # seconds — safety minimum per phase
MAX_GREEN       = 120   # seconds
OMEGA           = 0.5   # queue-length penalty weight
EPSILON         = 1e-6
NUM_SECONDS     = 86400 # 24-hour simulation episode

# ---------------------------------------------------------------------------
# Traffic light phase configuration (derived from trafficl ight.ttl.xml)
#
# TL 1227907805 has 10 phases alternating between green and transition/yellow:
#   Index 0 (85 s): green  — optimisable
#   Index 1  (5 s): transition/yellow — FIXED
#   Index 2 (40 s): green  — optimisable
#   Index 3  (5 s): transition/yellow — FIXED
#   Index 4 (40 s): green  — optimisable
#   Index 5  (5 s): yellow — FIXED
#   Index 6 (45 s): green  — optimisable
#   Index 7  (5 s): yellow — FIXED
#   Index 8 (35 s): green  — optimisable
#   Index 9  (5 s): yellow — FIXED
# ---------------------------------------------------------------------------
TL_CONFIGS = {
    '1227907805': {'green_indices': [0, 2, 4, 6, 8], 'baseline': [85, 40, 40, 45, 35]},
}

BASELINE_CHROMOSOME = [d for cfg in TL_CONFIGS.values() for d in cfg['baseline']]
CHROMOSOME_LENGTH   = len(BASELINE_CHROMOSOME)  # 5


# ---------------------------------------------------------------------------
# Chromosome helpers
# ---------------------------------------------------------------------------

def create_chromosome():
    return [random.randint(MIN_GREEN, MAX_GREEN) for _ in range(CHROMOSOME_LENGTH)]


def compute_fitness(total_delay, max_queue):
    """F = 1 / (sum_delay + omega * Q_max + epsilon)  — maximised."""
    return 1.0 / (total_delay + OMEGA * max_queue + EPSILON)


def tournament_select(population, fitnesses):
    candidates = random.sample(range(len(population)), TOURNAMENT_SIZE)
    best = max(candidates, key=lambda i: fitnesses[i])
    return population[best][:]


def crossover(parent1, parent2):
    if random.random() < CROSSOVER_RATE:
        point = random.randint(1, CHROMOSOME_LENGTH - 1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2
    return parent1[:], parent2[:]


def mutate(chromosome):
    return [
        random.randint(MIN_GREEN, MAX_GREEN) if random.random() < MUTATION_RATE else g
        for g in chromosome
    ]


# ---------------------------------------------------------------------------
# SUMO interaction
# ---------------------------------------------------------------------------

def _apply_chromosome(chromosome):
    """Inject chromosome's green durations into the currently running SUMO sim."""
    gene_offset = 0
    for tl_id, cfg in TL_CONFIGS.items():
        green_indices = cfg['green_indices']
        n = len(green_indices)
        new_durations = chromosome[gene_offset:gene_offset + n]
        gene_offset += n

        logics = traci.trafficlight.getAllProgramLogics(tl_id)
        if not logics:
            continue
        logic = logics[0]

        new_phases = []
        gi = 0
        for idx, phase in enumerate(logic.phases):
            if idx in green_indices:
                new_phases.append(traci.trafficlight.Phase(new_durations[gi], phase.state))
                gi += 1
            else:
                new_phases.append(traci.trafficlight.Phase(phase.duration, phase.state))

        new_logic = traci.trafficlight.Logic("ga_opt", logic.type, 0, new_phases)
        traci.trafficlight.setProgramLogic(tl_id, new_logic)
        traci.trafficlight.setProgram(tl_id, "ga_opt")


def _parse_tripinfo(filepath):
    """Return (total_time_loss_s, throughput) from a SUMO tripinfo XML."""
    try:
        tree = ET.parse(filepath)
    except (ET.ParseError, FileNotFoundError):
        return 0.0, 0
    total_loss = 0.0
    throughput = 0
    for trip in tree.getroot().findall('tripinfo'):
        total_loss += float(trip.get('timeLoss', 0.0))
        if trip.get('arrival') is not None:
            throughput += 1
    return total_loss, throughput


def run_simulation(chromosome, trial_id=0):
    """
    Run one 24-hour SUMO simulation with the given timing plan.

    Returns:
        (total_delay_s, max_queue_veh, throughput_veh)
    """
    tripinfo_path = os.path.join(_DIR, f'_ga_tripinfo_{trial_id}.xml')

    sumo_cmd = [
        'sumo',
        '-n', NET_FILE,
        '-r', ROUTE_FILE,
        '--additional-files', f'{VTYPE_FILE},{TTL_FILE}',
        '--tripinfo-output', tripinfo_path,
        '--no-warnings', '--no-step-log',
        '--begin', '0',
        '--end', str(NUM_SECONDS),
    ]
    traci.start(sumo_cmd)
    _apply_chromosome(chromosome)

    controlled_lanes = set()
    for tl_id in TL_CONFIGS:
        for lane in traci.trafficlight.getControlledLanes(tl_id):
            controlled_lanes.add(lane)

    max_queue = 0
    while traci.simulation.getTime() < NUM_SECONDS:
        traci.simulationStep()
        q = sum(traci.lane.getLastStepHaltingNumber(lane) for lane in controlled_lanes)
        if q > max_queue:
            max_queue = q
        if traci.simulation.getMinExpectedNumber() == 0:
            break

    traci.close()

    total_delay, throughput = _parse_tripinfo(tripinfo_path)
    try:
        os.remove(tripinfo_path)
    except OSError:
        pass

    return total_delay, max_queue, throughput


# ---------------------------------------------------------------------------
# GA main loop
# ---------------------------------------------------------------------------

def run_ga():
    """
    Execute the full GA optimisation and return (best_chromosome, fitness_history).
    Population: 50, Tournament: 3, Crossover: 0.8, Mutation: 0.1, Generations: 40
    Elitism: best individual carried forward each generation.
    """
    population = [create_chromosome() for _ in range(POPULATION_SIZE)]
    fitness_history = []
    overall_best = BASELINE_CHROMOSOME[:]
    overall_best_fitness = -1.0

    print(f"GA optimisation — Quimpo Blvd–GE Torres")
    print(f"Population: {POPULATION_SIZE}  Generations: {N_GENERATIONS}  "
          f"Crossover: {CROSSOVER_RATE}  Mutation: {MUTATION_RATE}")
    print(f"Baseline chromosome: {BASELINE_CHROMOSOME}\n")

    for gen in range(N_GENERATIONS):
        fitnesses = []
        for idx, chrom in enumerate(population):
            delay, queue, _ = run_simulation(chrom, trial_id=idx)
            fitnesses.append(compute_fitness(delay, queue))

        best_idx = max(range(len(population)), key=lambda i: fitnesses[i])
        gen_best = fitnesses[best_idx]
        fitness_history.append(gen_best)

        if gen_best > overall_best_fitness:
            overall_best_fitness = gen_best
            overall_best = population[best_idx][:]

        print(f"Gen {gen + 1:02d}/{N_GENERATIONS}  "
              f"best_fitness={gen_best:.8f}  "
              f"chromosome={population[best_idx]}")

        new_population = [population[best_idx][:]]
        while len(new_population) < POPULATION_SIZE:
            p1 = tournament_select(population, fitnesses)
            p2 = tournament_select(population, fitnesses)
            c1, c2 = crossover(p1, p2)
            new_population.append(mutate(c1))
            if len(new_population) < POPULATION_SIZE:
                new_population.append(mutate(c2))

        population = new_population

    print(f"\nOptimisation complete.")
    print(f"Best chromosome: {overall_best}  (fitness={overall_best_fitness:.8f})")
    return overall_best, fitness_history


def save_results(best_chromosome, fitness_history):
    with open(RESULTS_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['generation', 'best_fitness'])
        for gen, fit in enumerate(fitness_history, 1):
            writer.writerow([gen, fit])

    best_csv = RESULTS_CSV.replace('.csv', '_best_chromosome.csv')
    headers = []
    for tl_id, cfg in TL_CONFIGS.items():
        for i in range(len(cfg['green_indices'])):
            headers.append(f'{tl_id}_g{i}')
    with open(best_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerow(best_chromosome)

    print(f"Saved: {RESULTS_CSV}")
    print(f"Saved: {best_csv}")


if __name__ == '__main__':
    best, history = run_ga()
    save_results(best, history)
