# Review Response Summary — FS_07

**Paper:** Genetic Algorithm Optimization of Traffic Signals: A SUMO Microsimulation Study of Urban Intersections in Davao City, Philippines  
**Authors:** Ga-as, Merencillo, Villamor  
**Decision:** Major Revision (both reviewers)  
**Full response document:** `Response_to_Reviewers_FS07.docx`

---

## Reviewer 1 (FS_07_1)

| Comment | Status | Where in paper |
|---|---|---|
| Results & Discussion section not yet written | ✅ Section 4 added (fill-in template; numbers pending simulation) | Section 4 |
| Conclusion not yet written | ✅ Section 5 added (fill-in template; numbers pending simulation) | Section 5 |
| Date inconsistency — Section 2.4 said "October 2023" but Section 3.1 said "April 2025" | ✅ Fixed — all dates now consistently April 15–20, 2025 | Throughout |
| Abstract shows "RESULT PENDING" placeholder | ✅ Replaced with structured abstract; result/conclusion sentences are labelled fill-in slots | Abstract |
| Krauss model calibration values (e.g. 0.5 m motorcycle gap) stated without citation | ⚠️ Qualitative justification added; no Philippine-specific empirical citation found — insert one if available | Section 3.2 |

---

## Reviewer 2 (FS_07_2)

| Comment | Status | Where in paper |
|---|---|---|
| SUMO acronym never expanded on first use in Introduction | ✅ Expanded: "SUMO (Simulation of Urban MObility)" on first use | Introduction, para 3 |
| Davao City selection not justified — why not Metro Manila or Cebu? | ✅ Dedicated paragraph added with three reasons (largest Mindanao city, DPWH data available, no prior microsimulation review) | Introduction, para 5 |
| Scope and delimitation not formally stated | ✅ Explicit scope statement added after objectives list | Introduction |
| Specific intersection selection not justified in methodology | ✅ Three-reason justification added (high-volume corridor, DPWH data available, no prior review) | Section 3.1 |
| GA parameter values not defended | ✅ Parameter justification paragraph added with citations to Park et al. [10] and Goldberg [9] | Section 3.3 |
| SUMO network setup insufficient detail | ✅ Section 3.2 expanded to include lane counts, phase structure, how DPWH demand was mapped to routes | Section 3.2 |
| Reference [2] (DPWH data) not cited in methodology | ✅ Now cited in both Section 3.1 and 3.2 | Sections 3.1, 3.2 |
| No validation step comparing simulated baseline to real-world data | ✅ "Baseline Validation" paragraph added describing 5-trial comparison against field queue counts | Section 3.2 |
| Baseline for t-tests not clearly identified | ✅ Explicitly named as current fixed-time plans (150 s cycle at Quirino, multi-phase 250 s at Quimpo) | Section 3.4 |
| No limitations acknowledged | ✅ Limitations subsection added (5 items) | Section 3.5 |
| No comparison of GA against RL or fuzzy logic | ✅ Comparison added explaining why GA is preferred over RL and fuzzy for this deployment context | Section 2.2 |
| Reference [7] wrong journal name | ✅ Corrected to "IJFMR — Intl. Journal for Multidisciplinary Research" with URL | References [7] |
| Reference [11] wrong journal, volume, year | ✅ Corrected to Transportation Research Part C, vol. 32, pp. 159–178 (2013) | References [11] |
| Reference [12] wrong year (listed 2024, actual 2025) | ✅ Corrected to 2025 with DOI added | References [12] |
| Reference [3] (Gradinescu 2007) venue and co-authors unverifiable | ⚠️ Flagged — **manual verification required** by authors before final submission | References [3] |

---

## Still Pending (awaiting simulation results)

These items cannot be completed until `evaluate_ga.py` has been run:

- **Abstract** — replace `[RESULTS: …]` and `[CONCLUSION: …]` with actual percentage reductions
- **Section 4.1** — insert fitness-vs-generation narrative from `ga_results.csv`
- **Section 4.2** — insert optimized green durations from `ga_results_best_chromosome.csv`
- **Section 4.3** — insert mean ± SD and t-test p-values from `ga_comparison_results.csv`
- **Section 4.4 and Section 5** — complete discussion and conclusion with your numbers
- **Section 3.2 Baseline Validation** — insert RMSE or % agreement against field queue counts
