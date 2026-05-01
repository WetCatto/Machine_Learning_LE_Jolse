# Genetic Algorithm Optimization of Traffic Signals
### A SUMO Microsimulation Study of Urban Intersections in Davao City, Philippines

**Authors:** James O. Ga-as, Julse M. Merencillo, Maureen M. Villamor  
**Affiliation:** University of Southeastern Philippines, College of Information and Computing

---

## Paper Status

**Under revision** — both reviewers recommended Major Revision (April 2026).  
All structural reviewer comments have been addressed in `main.tex`. Quantitative results (Sections 4 and 5, Abstract) remain as fill-in placeholders pending simulation runs.

See [`REVIEW_RESPONSE_SUMMARY.md`](REVIEW_RESPONSE_SUMMARY.md) for a full comment-by-comment breakdown.

> **Two items still require author action before final submission:**
> 1. Fill in simulation results (run `ga_optimize.py` then `evaluate_ga.py` and paste outputs into `main.tex`)
> 2. Manually verify Reference [3] (Gradinescu 2007) — venue and co-authors flagged as unconfirmed by Reviewer 2

---

## Overview

This repository contains the LaTeX paper and SUMO simulation codebase for a study that applies a Genetic Algorithm (GA) to optimize fixed-time traffic signal plans at two Davao City intersections:

- **E. Quirino Avenue** — 150 s cycle, 4 traffic lights
- **Quimpo Boulevard–GE Torres Junction** — multi-phase, 1 traffic light

The GA evolves green-phase duration plans evaluated against full 24-hour SUMO microsimulation runs. Vehicle demand is derived from DPWH five-day traffic classification surveys (April 2025).

---

## Repository Structure

```
claude_code/
├── main.tex                          # LaTeX paper (SPIE A4 format)
├── main.pdf                          # Compiled paper
├── FS_07_1.pdf                       # Peer review sheet 1
├── FS_07_2.pdf                       # Peer review sheet 2
├── Response_to_Reviewers_FS07.docx  # Filled reviewer response
└── machine-learning-le/
    ├── flake.nix                     # Nix environment (SUMO + Python)
    ├── quirino_avenue/
    │   ├── ga_optimize.py            # GA optimizer — run this first
    │   ├── evaluate_ga.py            # Evaluation vs baseline — run second
    │   ├── quirino_avenue.net.xml    # SUMO road network
    │   ├── quirino_avenue.ttl.xml    # Baseline fixed-time signal plan
    │   ├── traffic_routes.rou.xml    # Vehicle demand routes
    │   └── vehicle_types.add.xml     # Vehicle type distribution
    └── quimpo_ge_torres/
        ├── ga_optimize.py
        ├── evaluate_ga.py
        ├── quimpo-GE_torres.net.xml
        ├── trafficl ight.ttl.xml     # note: space in filename
        ├── quimpo_traffic_route.rou.xml
        └── vehicle_types.add.xml
```

---

## Environment Setup

The simulation environment is managed with [Nix](https://nixos.org/). From inside `machine-learning-le/`:

```bash
# Enter the development shell (installs SUMO, Python, all dependencies)
nix develop

# Or with direnv (auto-activates when you cd into the folder)
direnv allow
```

This sets `SUMO_HOME`, adds `sumo` to `PATH`, and pip-installs `traci`, `sumolib`, `stable-baselines3`, and `sumo-rl>=1.4`.

---

## Running the GA Simulation

### Step 1 — Optimize (run the GA)

```bash
cd machine-learning-le/quirino_avenue
python ga_optimize.py
```

Runs 40 generations × 50 chromosomes. Prints best fitness per generation to console.

**Output files:**
| File | Contents |
|---|---|
| `ga_results.csv` | Best fitness score per generation |
| `ga_results_best_chromosome.csv` | Winning green-phase durations |

Repeat for the second intersection:

```bash
cd machine-learning-le/quimpo_ge_torres
python ga_optimize.py
```

### Step 2 — Evaluate (compare GA vs baseline)

```bash
cd machine-learning-le/quirino_avenue
python evaluate_ga.py
```

Runs 10 paired trials (same random seeds) for the baseline fixed-time plan and the GA-optimized plan. Prints a summary table with mean ± SD and two-tailed t-test p-values.

**Output file:**

| File | Contents |
|---|---|
| `ga_comparison_results.csv` | Per-trial metrics: total delay, max queue, throughput |

---

## GA Parameters

| Parameter | Value |
|---|---|
| Population size | 50 |
| Tournament selection size | 3 |
| Crossover rate | 0.8 (single-point) |
| Mutation rate | 0.1 (uniform) |
| Generations | 40 |
| Green-phase bounds | [10, 120] seconds |
| Yellow/all-red phases | Fixed at 5 s (excluded from chromosome) |
| Fitness function | F = 1 / (Σdᵢ + 0.5·Q_max + 1e-6) |
| Simulation episode | 24 hours via libsumo |

### Chromosome Layout

**Quirino Avenue (8 genes):**
`[TL-259606750: g0, g1] [TL-259608478: g0, g1] [TL-267530736: g0, g1] [TL-267530738: g0, g1]`  
Baseline: `[95, 45, 95, 25, 95, 45, 95, 25]`

**Quimpo–GE Torres (5 genes):**
`[TL-1227907805: g0, g2, g4, g6, g8]`  
Baseline: `[85, 40, 40, 45, 35]`

---

## Compiling the Paper

```bash
# Two passes to resolve references
pdflatex main.tex && pdflatex main.tex

# Or use latexmk
latexmk -pdf main.tex

# Clean auxiliary files
latexmk -C
```

### Completing the Paper After Simulation

Once `evaluate_ga.py` has run, fill in the placeholders in `main.tex`:

1. **Abstract** — replace `[RESULTS: …]` and `[CONCLUSION: …]` with actual percentages
2. **Section 4.1** — paste fitness-vs-generation values from `ga_results.csv`
3. **Section 4.2** — paste optimized phase durations from `ga_results_best_chromosome.csv`
4. **Section 4.3** — paste mean ± SD and t-test p-values from `ga_comparison_results.csv`
5. **Section 4.4 and Section 5** — complete the discussion and conclusion with your numbers
6. **Section 3.2 Baseline Validation** — fill in your field-observed queue comparison metrics

---

## Vehicle Type Distribution

| Type | Class | Probability | Length | Max Speed |
|---|---|---|---|---|
| Motorcycle | motorcycle | 20% | 2.2 m | 120 km/h |
| Passenger car | passenger | 57% | 4.5 m | 120 km/h |
| PUV / Jeepney | passenger | 10% | 6.5 m | 80 km/h |
| Goods truck | truck | 11% | 9.0 m | 90 km/h |
| Bus | bus | 2% | 8.5 m | 100 km/h |
