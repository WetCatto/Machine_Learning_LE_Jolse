"""
Evaluate GA-optimised vs baseline fixed-time plan for Quimpo Blvd–GE Torres.

Runs N_TRIALS independent simulation trials for each plan (same random seeds
for a fair paired comparison), then reports mean ± SD and two-tailed t-test
p-values for total vehicle delay, max queue length, and vehicle throughput.

Usage:
    # Run ga_optimize.py first, then:
    python evaluate_ga.py

Outputs:
    ga_comparison_results.csv
"""

import os
import csv
import random
import statistics
import xml.etree.ElementTree as ET

os.environ['LIBSUMO_AS_TRACI'] = '1'
import traci  # noqa: E402

try:
    from scipy import stats as scipy_stats
    _SCIPY = True
except ImportError:
    _SCIPY = False
    print("scipy not found — t-test p-values will not be computed.")

from ga_optimize import (
    _DIR, NET_FILE, ROUTE_FILE, VTYPE_FILE, TTL_FILE,
    TL_CONFIGS, NUM_SECONDS,
    _apply_chromosome, _parse_tripinfo,
    BASELINE_CHROMOSOME, RESULTS_CSV,
)

N_TRIALS       = 10
COMPARISON_CSV = os.path.join(_DIR, 'ga_comparison_results.csv')


def load_best_chromosome():
    best_csv = RESULTS_CSV.replace('.csv', '_best_chromosome.csv')
    if not os.path.exists(best_csv):
        raise FileNotFoundError(
            f"Best chromosome file not found: {best_csv}\n"
            "Run ga_optimize.py first."
        )
    with open(best_csv) as f:
        reader = csv.reader(f)
        next(reader)
        row = next(reader)
    return [int(x) for x in row]


def run_trial(chromosome, trial_id, seed):
    tripinfo_path = os.path.join(_DIR, f'_eval_tripinfo_{trial_id}.xml')

    sumo_cmd = [
        'sumo',
        '-n', NET_FILE,
        '-r', ROUTE_FILE,
        '--additional-files', f'{VTYPE_FILE},{TTL_FILE}',
        '--tripinfo-output', tripinfo_path,
        '--no-warnings', '--no-step-log',
        '--seed', str(seed),
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


def evaluate():
    best_chromosome = load_best_chromosome()
    seeds = [random.randint(0, 99999) for _ in range(N_TRIALS)]

    print("=" * 60)
    print("Quimpo Blvd–GE Torres — GA vs Baseline Evaluation")
    print("=" * 60)
    print(f"Baseline:     {BASELINE_CHROMOSOME}")
    print(f"GA-optimised: {best_chromosome}")
    print(f"Trials: {N_TRIALS}  |  Seeds: {seeds}\n")

    rows = []

    print("Running baseline trials...")
    b_delays, b_queues, b_thrpts = [], [], []
    for i, seed in enumerate(seeds):
        d, q, t = run_trial(BASELINE_CHROMOSOME, trial_id=i, seed=seed)
        b_delays.append(d); b_queues.append(q); b_thrpts.append(t)
        rows.append(['baseline', i + 1, seed, d, q, t])
        print(f"  Trial {i+1:02d}: delay={d:>10.1f} s  queue={q:>4}  throughput={t}")

    print("\nRunning GA-optimised trials...")
    g_delays, g_queues, g_thrpts = [], [], []
    for i, seed in enumerate(seeds):
        d, q, t = run_trial(best_chromosome, trial_id=i, seed=seed)
        g_delays.append(d); g_queues.append(q); g_thrpts.append(t)
        rows.append(['ga_optimised', i + 1, seed, d, q, t])
        print(f"  Trial {i+1:02d}: delay={d:>10.1f} s  queue={q:>4}  throughput={t}")

    with open(COMPARISON_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['plan', 'trial', 'seed',
                         'total_delay_s', 'max_queue_veh', 'throughput_veh'])
        writer.writerows(rows)

    def _fmt(vals):
        return f"{statistics.mean(vals):>12.2f} ± {statistics.stdev(vals):<8.2f}"

    def _pct_change(base, new):
        m_base = statistics.mean(base)
        m_new  = statistics.mean(new)
        return (m_new - m_base) / m_base * 100.0 if m_base != 0 else 0.0

    print("\n" + "=" * 60)
    print(f"{'Metric':<22} {'Baseline':>22} {'GA-Optimised':>22} {'Change':>8}")
    print("-" * 60)
    print(f"{'Total delay (s)':<22} {_fmt(b_delays):>22} {_fmt(g_delays):>22} "
          f"{_pct_change(b_delays, g_delays):>+7.1f}%")
    print(f"{'Max queue (veh)':<22} {_fmt(b_queues):>22} {_fmt(g_queues):>22} "
          f"{_pct_change(b_queues, g_queues):>+7.1f}%")
    print(f"{'Throughput (veh)':<22} {_fmt(b_thrpts):>22} {_fmt(g_thrpts):>22} "
          f"{_pct_change(b_thrpts, g_thrpts):>+7.1f}%")

    if _SCIPY:
        _, p_delay = scipy_stats.ttest_ind(b_delays, g_delays)
        _, p_queue = scipy_stats.ttest_ind(b_queues, g_queues)
        _, p_thrpt = scipy_stats.ttest_ind(b_thrpts, g_thrpts)

        print("\n--- Two-tailed t-test (α = 0.05) ---")
        for label, p in [("Total delay", p_delay),
                         ("Max queue",   p_queue),
                         ("Throughput",  p_thrpt)]:
            sig = "*significant*" if p < 0.05 else "not significant"
            print(f"  {label:<16} p = {p:.4f}  ({sig})")

    print(f"\nResults saved to {COMPARISON_CSV}")


if __name__ == '__main__':
    evaluate()
