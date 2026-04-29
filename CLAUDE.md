# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LaTeX academic paper formatted for SPIE A4 proceedings. The paper is titled **"Genetic Algorithm Optimization of Traffic Signals: A SUMO Microsimulation Study of Urban Intersections in Davao City, Philippines"** — authored by Ga-as, Merencillo, and Villamor from the University of Southeastern Philippines.

The accompanying simulation codebase is in `machine-learning-le/`.

## Building the Paper

```bash
# Compile with bibliography support (run twice for references to resolve)
pdflatex main.tex && pdflatex main.tex

# Or use latexmk for automatic multi-pass compilation
latexmk -pdf main.tex

# Clean auxiliary files
latexmk -C
```

Note: `poppler-utils` is not installed. To read PDFs in-shell: `brew install poppler`.

## Document Structure

`main.tex` is a single-file paper with no `\input` or `\include` dependencies.

Sections (in order):
1. **Introduction** — motivation, Philippine congestion context, Davao City justification, study objectives, scope
2. **Review of Related Literature** — fixed-time control, GA methods, RL/fuzzy comparison, SUMO, Philippine traffic context, research gap
3. **Methodology** — site selection/justification, SUMO calibration + validation, GA implementation + parameter justification, experimental design, limitations
4. **Results and Discussion** — convergence, optimized timing tables, performance comparison, discussion (**fill in after running simulation**)
5. **Conclusion** — (**fill in after running simulation**)
6. **References** — `\thebibliography{99}` format (16 entries, inline `[N]` style)

## Formatting Constraints (SPIE A4 Style)

- **Page margins:** top 2.54 cm, bottom 4.94 cm, left/right 1.93 cm
- **Font:** Times Roman via `newtxtext`/`newtxmath`
- **Sections:** 11 pt bold centered uppercase (e.g., `1. INTRODUCTION`)
- **Subsections:** 10 pt bold left-justified
- **Citations:** `[N]` bracket format — hardcoded inline numbers, `\thebibliography` for bibliography
- **Title:** 16 pt bold; authors 12 pt; affiliation normal size

## Key Technical Details

- **Study sites:** E. Quirino Avenue (150 s cycle, 4 TLs, baseline 95 s / 45 s splits) and Quimpo Blvd–GE Torres (multi-phase, 1 TL, 5 green phases: 85/40/40/45/35 s)
- **Traffic data:** DPWH 5-day classification counts, **April 15–20, 2025**
- **Vehicle mix:** cars 57%, motorcycles 20%, PUVs/jeepneys 10%, trucks 11%, buses 2%
- **GA parameters:** population 50, tournament selection (size 3), single-point crossover 0.8, uniform mutation 0.1, 40 generations, elitism (1 best per gen)
- **Fitness function:** F = 1 / (Σdᵢ + ω·Q_max + ε), ω = 0.5, ε = 1e-6
- **Simulation:** libsumo via `LIBSUMO_AS_TRACI=1`, 24-hour episodes, green-phase bounds [10, 120] s, yellow/all-red phases fixed at 5 s

## Simulation Codebase (`machine-learning-le/`)

### Environment Setup

Uses Nix flake — run `nix develop` (or `direnv allow` with `.envrc`) to enter the shell. This sets `SUMO_HOME`, adds SUMO to `PATH`, and pip-installs `traci`, `sumolib`, `stable-baselines3`, `sumo-rl>=1.4`.

### Running the GA

```bash
# E. Quirino Avenue
cd machine-learning-le/quirino_avenue
python ga_optimize.py     # 40 generations × 50 chromosomes; writes ga_results.csv
python evaluate_ga.py     # 10-trial comparison; writes ga_comparison_results.csv

# Quimpo Blvd–GE Torres
cd machine-learning-le/quimpo_ge_torres
python ga_optimize.py
python evaluate_ga.py
```

### Output Files

| File | Contents |
|---|---|
| `ga_results.csv` | best fitness per generation |
| `ga_results_best_chromosome.csv` | winning green-phase durations |
| `ga_comparison_results.csv` | per-trial metrics (delay, queue, throughput) for baseline and GA plans |

### Chromosome Layout

**Quirino** (8 genes): `[TL-259606750-g0, g1, TL-259608478-g0, g1, TL-267530736-g0, g1, TL-267530738-g0, g1]`  
Baseline: `[95, 45, 95, 25, 95, 45, 95, 25]`

**Quimpo** (5 genes): `[g0, g2, g4, g6, g8]` for TL-1227907805  
Baseline: `[85, 40, 40, 45, 35]`

### Codebase History

The original implementation used DQN reinforcement learning (Stable Baselines3). The `train.py` and `evaluate.py` files at the root and in `quimpo_ge_torres/` are the old RL scripts. They are preserved for reference. The GA implementations (`ga_optimize.py`, `evaluate_ga.py`) in each intersection subdirectory are the current versions aligned with the paper.

### SUMO Network Files (do not modify)

- `quirino_avenue/quirino_avenue.net.xml` — road network
- `quirino_avenue/quirino_avenue.ttl.xml` — baseline fixed-time traffic light plan
- `quirino_avenue/traffic_routes.rou.xml` — vehicle demand routes
- `quirino_avenue/vehicle_types.add.xml` — vehicle type distribution
- `quimpo_ge_torres/quimpo-GE_torres.net.xml`
- `quimpo_ge_torres/trafficl ight.ttl.xml` — note: space in filename
- `quimpo_ge_torres/quimpo_traffic_route.rou.xml`
- `quimpo_ge_torres/vehicle_types.add.xml`

## Reference Files

- `FS_07_1.pdf`, `FS_07_2.pdf` — peer review sheets (both recommend Major Revision)
