# Repository Overview

Created after reading the repository instruction file and inspecting the actual repository structure. This document is an inventory only; it does not assess mathematical or methodological correctness.

## Actual top-level structure found

```text
.
├── .git/
├── .gitignore
├── README.md
├── AGENTS.md
├── docs/
├── outputs/
├── papers/
├── reference_implementation/
├── requirements.txt
├── src/
└── tests/
```

Notes:

- The instruction file is now named `AGENTS.md`, matching the expected filename in the project instructions.
- Preliminary generated artifacts have been moved out of the repository root and into `outputs/`. They should not be treated as final thesis results.
- Future generated outputs should use this structure:

```text
outputs/
├── data/
│   └── simulations_becker_fig6_full.csv
├── figures/
│   └── fig6_becker_replikation.pdf
└── logs/
```

## Python implementation files

Files under `src/` that appear to belong to the Python implementation:

```text
src/
├── app_types/
│   └── __init__.py
├── data_generator.py
├── icaEstimator.py
├── main.py
├── plot_fig.py
├── simulation.py
└── table_analysis.py
```

Apparent roles from filenames, imports, classes, and top-level functions:

- `src/data_generator.py`: defines `DataGenerator`; appears to generate simulated data and distribution-specific components.
- `src/icaEstimator.py`: defines `ICAEstimator`; appears to implement the ICA-based estimator using `sklearn.decomposition.FastICA`, `statsmodels`, and `scipy`.
- `src/simulation.py`: defines `SimulationEngine`; appears to run repeated simulation scenarios and collect OLS/ICA estimates and summary metrics.
- `src/main.py`: appears to orchestrate an example run and a larger Becker-style Figure 6 simulation, writing `simulations_becker_fig6_full.csv` to the repository root.
- `src/plot_fig.py`: appears to read `simulations_becker_fig6_full.csv` and write `fig6_becker_replikation.pdf` to the repository root.
- `src/table_analysis.py`: preliminary exploratory artifact, not currently needed. It appears to have been an early attempt to inspect parameters for a future flowchart. It should not be reviewed, repaired, or used during the first audit phase, but can be revisited later if Figure 8-style flowchart work becomes active.
- `src/app_types/__init__.py`: package marker or placeholder; not listed in the expected structure from `agents.md`.

Other Python-related files:

```text
tests/
└── test_main.py
```

- `tests/test_main.py` appears to be a placeholder test file. It imports `your_function` from `src.main` and references `args` and `expected_result`, which are not defined in that file. It should be ignored for now because unit tests are not the current priority.

## Papers and reference material

Files under `papers/`:

```text
papers/
├── Becker_example.pdf
└── haschka_ICA.pdf
```

These match the expected paper/reference-material filenames from `agents.md`.

Documentation/reference files under `docs/`:

```text
docs/
├── audit_report.md
├── code_mapping.md
├── codex_prompts.md
├── model_equations.md
├── paper_notes.md
├── repository_overview.md
└── test_suggestions.md
```

Observed status:

- `docs/codex_prompts.md` contains content.
- `docs/audit_report.md`, `docs/code_mapping.md`, `docs/model_equations.md`, `docs/paper_notes.md`, and `docs/test_suggestions.md` were present but empty at inspection time.
- `docs/test_suggestions.md` is present but not listed in the expected structure from `agents.md`.

Root-level reference or output files:

- `README.md`: present, but currently reads like a generic Python project README rather than a thesis-specific overview.
- `requirements.txt`: present.

Preliminary generated artifacts:

- `outputs/data/simulations_becker_fig6_full.csv`: preliminary generated simulation output; not a final thesis result.
- `outputs/figures/fig6_becker_replikation.pdf`: preliminary generated figure output; not a final thesis result.
- `outputs/logs/`: reserved for future logs.

## R reference implementation files

The expected path in `agents.md` is:

```text
reference_implementation/
└── R/
    ├── ICAReg.R
    └── README.md
```

The actual path found is:

```text
reference_implementation/
└── R/
    ├── ICAReg.R
    └── README.md
```

Important path note:

- The R reference implementation is now stored at the expected top-level path.
- `reference_implementation/R/ICAReg.R` appears to contain the R reference implementation.
- `reference_implementation/R/README.md` describes the R function usage and references Dost & Haschka (2025).

## Missing or unexpected items relative to `agents.md`

Expected but not found at the expected paths:

- `docs/r_reference_analysis.md`.
- `docs/simulation_design.md`.
- `docs/figure6_plan.md`.
- `docs/figure8_flowchart_plan.md`.
- `docs/open_questions.md`.

Found but not listed in the expected structure:

- `requirements.txt`.
- `tests/test_main.py`.
- `src/table_analysis.py`.
- `src/app_types/__init__.py`.
- `docs/test_suggestions.md`.
- `outputs/data/simulations_becker_fig6_full.csv`.
- `outputs/figures/fig6_becker_replikation.pdf`.

Expected docs that exist but are currently empty:

- `docs/paper_notes.md`.
- `docs/model_equations.md`.
- `docs/code_mapping.md`.
- `docs/audit_report.md`.

## Immediate setup issues noticed

These are setup and repository-organization observations only, not mathematical audit findings.

- `requirements.txt` includes `Flask`, `requests`, and `pytest`, but the inspected implementation files do not obviously use Flask or requests.
- `requirements.txt` does not list `matplotlib` or `seaborn`, although `src/plot_fig.py` imports both.
- Dependency cleanup should be considered later, especially checking for missing plotting dependencies and possible unused dependencies.
- `README.md` appears generic and does not describe the thesis project, the ICA method, the R reference implementation, or the simulation workflow.
- `src/main.py` and `src/plot_fig.py` still hardcode the old repository-root output filenames. If these scripts are used again, their output paths should be reviewed and updated to the `outputs/` structure in a later approved code change.
- `tests/test_main.py` appears to be a placeholder and likely cannot run as written because it imports `your_function` and references undefined names. It is not a current priority.
- `src/table_analysis.py` expects a file named `simulations_ergebnisse_gross.csv`, while the inspected simulation/plot workflow uses `simulations_becker_fig6_full.csv`. The file is preliminary and not currently needed.
- Several documentation files required for the planned audit exist but are empty.
- Several documentation files named in `agents.md` are missing.

## Current setup cleanup decisions

- Treat `simulations_becker_fig6_full.csv` and `fig6_becker_replikation.pdf` as preliminary generated artifacts, not final thesis results.
- Store generated outputs under `outputs/`: `outputs/data/`, `outputs/figures/`, and `outputs/logs/`.
- Store the R reference implementation under `reference_implementation/R/`, outside `docs/`.
- Keep `src/table_analysis.py` for now, but treat it as a preliminary artifact from early flowchart-parameter exploration. Do not use it in the first audit phase.
- Ignore `tests/test_main.py` for now. It appears to be a placeholder, and unit tests are not the current priority.
- Consider dependency cleanup later, especially checking `requirements.txt` for missing plotting dependencies and possibly unused dependencies.

## Documentation responsibilities

- `docs/paper_notes.md`: first paper-understanding notes, including the research problem, intuition, assumptions, method overview, estimation procedure, limitations, and implementation-relevant sections.
- `docs/model_equations.md`: formal model extraction, including equations, notation, distributional assumptions, independence assumptions, identification logic, algorithmic steps, and implementation implications.
- `docs/audit_report.md`: later Paper-R-Python comparison audit, after the paper notes, model equations, R analysis, and Python overview exist.
- No new staged audit document should be created for the first paper-understanding/model-extraction phase.

## Planned scientific audit order

The first scientific audit should not start directly with `audit_report.md` or with the FastICA-versus-JADE issue. The initial order should be:

1. Understand the Haschka/Dost paper and extract the model, assumptions, equations, and estimation procedure.
2. Analyze the R reference implementation.
3. Analyze the Python implementation broadly.
4. Compare paper, R implementation, and Python implementation.
5. Investigate FastICA versus JADE as a separate focused audit step after the broader method and implementation context is clear.

## Remaining open questions before starting the scientific audit

No repository-setup questions from the initial overview remain open. The next open questions should come from the paper-understanding and model-extraction work itself.
