# Python Implementation Overview

This document describes the current Python implementation in `src/` as it exists now. It is an architecture and workflow overview only. It does not evaluate mathematical correctness, methodological equivalence to the paper, or equivalence to the R reference implementation.

## 1. Overall Architecture

The Python implementation is organized as a small modular codebase rather than one monolithic script. This matches the intended project direction in `AGENTS.md` and should be preserved unless a later approved change has a clear scientific or reproducibility reason.

Relevant Python files currently found in `src/`:

- `src/data_generator.py`: defines the simulated data-generating process through `DataGenerator`.
- `src/icaEstimator.py`: defines the ICA-based estimator through `ICAEstimator`.
- `src/simulation.py`: defines repeated simulation execution through `SimulationEngine`.
- `src/main.py`: acts as an executable script for a demo estimation and a larger Becker-style simulation run.
- `src/plot_fig.py`: generates a Becker-style Figure 6 plot from simulation results.
- `src/table_analysis.py`: preliminary exploratory artifact for table/flowchart-oriented summaries; the user has clarified that it is not important for the current audit.
- `src/app_types/__init__.py`: empty package marker or placeholder.

Confirmed planning decision: future generated outputs should be written under the organized `outputs/` structure, especially `outputs/data/`, `outputs/figures/`, and `outputs/logs/`. The current source code has not yet been changed to implement this.

The main implementation flow is:

1. Generate simulated data with `DataGenerator`.
2. Estimate a naive OLS model and an ICA-based model with `ICAEstimator`.
3. Repeat this across scenarios with `SimulationEngine`.
4. Save simulation output from `main.py`.
5. Plot the saved output with `plot_fig.py`.

## 2. Role of `DataGenerator`

File reference: `src/data_generator.py`.

`DataGenerator` is responsible for creating synthetic data for the simulation setting.

Constructor parameters:

- `n_samples`: number of observations.
- `alpha`: intercept used in the outcome equation.
- `beta`: true coefficient of `P` in the generated outcome.
- `rho`: strength of the dependence between `P` and the unobserved component `xi`.
- `eta_dist`: distribution family for the non-normal component.
- `random_state`: seed used through `numpy.random.default_rng`.

Important current behavior:

- `_generate_eta()` supports several distribution families: `gamma`, `exponential`, `beta`, `t`, `uniform`, `normal`, `lognormal`, `f`, `chisquare`, `laplace`, and `weibull`.
- `generate()` creates:
  - `xi` as standard normal noise.
  - `eta` from the configured distribution.
  - `P = eta + rho * xi`.
  - `Y = alpha + beta * P + xi`.
- The returned `pandas.DataFrame` contains `Y`, `P`, `true_xi`, and `true_eta`.
- The generated dataframe receives `attrs["skewness"]` and `attrs["kurtosis"]`, computed from `P`.

Implementation note for later audit: this file defines the current simulation DGP. Whether the DGP exactly matches the paper or thesis target should be checked later, not decided here.

## 3. Role of `ICAEstimator`

File reference: `src/icaEstimator.py`.

`ICAEstimator` is the main estimator class. It exposes a formula-based interface and returns a regression-style results table.

Constructor parameters:

- `formula`: parsed as `depvar ~ endog_vars | exog_vars`.
- `CF`: selects between control-function logic and residualization logic.
- `n_bootstraps`: number of bootstrap replications for standard errors.
- `random_state`: seed passed into the ICA routine.

Important current behavior:

- `_parse_formula()` parses dependent, endogenous, and optional exogenous variables. It also detects `-1` or `- 1` as an instruction to remove the intercept.
- `_validate_inputs()` checks for missing variables, non-numeric variables, constant variables, and rank deficiency in the regressor matrix.
- `fit()` drops rows with missing values in the variables used by the model, validates the data, runs the point estimate, runs bootstrap replications, and returns a results dataframe.
- `_run_single_estimation()` performs the single-estimation workflow used by both `fit()` and the simulation engine.
- ICA is currently performed with `sklearn.decomposition.FastICA`.
- The current component-selection logic standardizes each recovered component and uses a Kolmogorov-Smirnov test against the standard normal distribution; the component with the smallest KS statistic is selected as the control-function candidate.
- With `CF=True`, the selected component is added to the final regression as `control_func`.
- With `CF=False`, each endogenous regressor is residualized on the selected component before the final regression.
- Bootstrap standard errors are computed from repeated resamples, and p-values are computed with a normal approximation.
- `fit()` emits warnings based on a KS normality check of the selected control function and duplicate values in that component.

Implementation note for later audit: this overview only records that the implementation uses FastICA, KS-based component selection, a `CF` switch, and bootstrap output. The later paper/R/Python audit should evaluate whether each behavior is methodologically equivalent to the reference model.

## 4. Role of `SimulationEngine`

File reference: `src/simulation.py`.

`SimulationEngine` runs repeated simulations over a grid of sample sizes and distribution configurations.

Constructor parameters:

- `n_iterations`: number of repetitions per scenario.
- `true_beta`: true coefficient used for bias and RMSE calculations.
- `true_rho`: default endogeneity-strength parameter if a scenario does not override it.
- `random_state`: base seed for repeated simulation runs.

Important current behavior:

- `run(sample_sizes, distribution_configs)` loops over sample sizes and distribution configurations.
- Each distribution config is expected to contain a `name`, optional `params`, and optional `rho`.
- For each iteration, it creates a `DataGenerator`, generates data, runs naive OLS, and runs `ICAEstimator`.
- OLS is estimated directly with `statsmodels`.
- ICA is currently run by calling `ICAEstimator._run_single_estimation(df)` directly rather than `ICAEstimator.fit(df)`.
- ICA failures are caught and stored as `NaN` estimates for that iteration.
- The returned dataframe currently includes scenario descriptors and aggregate metrics such as `Bias_OLS`, `Bias_ICA`, `RMSE_OLS`, and `RMSE_ICA`.

Implementation note for later audit: direct use of a private estimator method is an intentional temporary performance shortcut. `ICAEstimator.fit()` performs bootstrapping, which would be too expensive for large simulation grids. The final design should probably expose a public point-estimation method, for example `fit_point()` or `estimate_point()`, that runs the ICA point estimate without bootstrap. This refactor should be proposed later and not implemented without approval.

## 5. Role of `main.py`

File reference: `src/main.py`.

`main.py` is the current executable orchestration script.

It currently does two main things:

1. Runs a small demonstration:
   - Creates one simulated dataset with `DataGenerator`.
   - Prints the first rows.
   - Fits a naive OLS model.
   - Fits `ICAEstimator(formula="Y ~ P", CF=False, n_bootstraps=100, random_state=42)`.
   - Prints the estimator result table.

2. Runs a larger Becker-style simulation:
   - Uses sample sizes `[100, 200, 400, 1000, 4000, 10000]`.
   - Uses rho levels from `0.1` to `0.8`.
   - Uses distribution families `beta`, `chisquare`, `gamma`, `lognormal`, and `t`, with four parameter settings each.
   - Runs `SimulationEngine(n_iterations=500, true_beta=1.0, random_state=99)`.
   - Writes the output to `simulations_becker_fig6_full.csv` in the repository root.

Path note: the current repository organization treats this CSV as a preliminary generated artifact under `outputs/data/`, but `main.py` still writes to the old root-level filename.

## 6. Role of `plot_fig.py`

File reference: `src/plot_fig.py`.

`plot_fig.py` creates a Becker-style Figure 6 plot from the simulation CSV.

Important current behavior:

- Reads `simulations_becker_fig6_full.csv` from the repository root.
- Uses `pandas`, `matplotlib`, and `seaborn`.
- Creates a `5 x 8` grid:
  - rows: `beta`, `chisquare`, `gamma`, `lognormal`, `t`;
  - columns: rho levels;
  - x-axis: sample size on a logarithmic scale;
  - y-axis: labeled as relative bias of the endogenous regressor;
  - colors: parameter configurations within each distribution family.
- Saves `fig6_becker_replikation.pdf` in the repository root.

Path note: the current repository organization treats this PDF as a preliminary generated artifact under `outputs/figures/`, but `plot_fig.py` still reads and writes the old root-level filenames.

## 7. Data Flow Through the Project

The current data flow is:

1. `DataGenerator.generate()` creates a dataframe with simulated `Y`, `P`, `true_xi`, and `true_eta`.
2. `main.py` or `SimulationEngine` uses the dataframe for OLS and ICA estimation.
3. `ICAEstimator` parses the model formula, optionally residualizes variables with exogenous regressors, runs ICA, selects a component, and performs the final regression.
4. `SimulationEngine.run()` aggregates repeated estimates into one row per scenario.
5. `main.py` writes the aggregated simulation table to CSV.
6. `plot_fig.py` reads the CSV and writes a PDF figure.

The currently documented output organization prefers `outputs/data/`, `outputs/figures/`, and `outputs/logs/`. The current source code has not yet been adjusted to these output paths.

## 8. How a Single Estimation Works

The public single-estimation entry point is `ICAEstimator.fit(df)`.

Current steps:

1. Parse the formula during initialization.
2. Drop missing rows for all variables used in the formula.
3. Validate the variables and rank of the design matrix.
4. Run `_run_single_estimation()` on the cleaned data.
5. If exogenous regressors are present, residualize `Y` and each endogenous regressor on the exogenous variables before ICA.
6. Run FastICA on the ICA input matrix.
7. Select the component that appears most normal under the current KS-statistic rule.
8. Construct the final regression design:
   - include endogenous and exogenous variables;
   - add the selected component if `CF=True`;
   - residualize endogenous variables on the selected component if `CF=False`;
   - add an intercept unless the formula removed it.
9. Fit the final OLS model.
10. Bootstrap the estimation procedure to compute standard errors.
11. Return a dataframe with estimates, standard errors, test statistics, and p-values.

The simulation engine uses the internal `_run_single_estimation()` path directly, so simulation runs currently do not use the full public `fit()` workflow or bootstrap output.

## 9. How Simulations Are Currently Run

Simulations are currently run through `SimulationEngine.run()` and orchestrated in `src/main.py`.

Current scenario dimensions from `main.py`:

- Sample sizes: `100`, `200`, `400`, `1000`, `4000`, `10000`.
- Rho levels: `0.1` through `0.8`.
- Distribution families: `beta`, `chisquare`, `gamma`, `lognormal`, `t`.
- Four parameter settings per distribution family.
- Iterations per scenario: `500`.

Current per-iteration behavior:

- Generate data with one distribution configuration and one sample size.
- Estimate OLS.
- Estimate ICA with `formula="Y ~ P"` and `CF=False`.
- Store failed ICA estimates as `NaN`.

Current aggregate output:

- `N`
- `Rho`
- `Verteilung_X`
- `Parameter`
- `Avg_Skewness`
- `Bias_OLS`
- `Bias_ICA`
- `RMSE_OLS`
- `RMSE_ICA`

The current simulation code does not yet write logs or a separate failure-rate column. Failed ICA estimates are represented internally as `NaN` before aggregation.

Draft target schema for later simulation output:

- Scenario metadata: `N`, `n_iterations`, `rho`, `true_beta`, `distribution`, `distribution_params`.
- Distribution diagnostics: `avg_skewness_P`, `avg_kurtosis_P`, optionally `std_skewness_P`, optionally `std_kurtosis_P`.
- Run validity: `n_total_runs`, `n_valid_ica_runs`, `n_failed_ica_runs`, `failure_rate_ica`.
- Estimator summaries: `mean_beta_ols`, `mean_beta_ica`, optionally `median_beta_ica` as a robustness summary.
- Bias metrics: `bias_ols_mean`, `bias_ica_mean`, optionally `bias_ica_median` as a robustness summary.
- Relative bias: `relative_bias_ica = bias_ica_mean / bias_ols_mean`, optionally `relative_bias_ica_percent = 100 * relative_bias_ica`.
- RMSE: `rmse_ols`, `rmse_ica`.

This schema is a first draft, not a final specification. It should be refined after the broad paper/R/Python audit, quick-mode runtime checks, and concrete example outputs.

## 10. How Figures Are Currently Generated

Figures are currently generated by running `src/plot_fig.py` after the simulation CSV exists.

Current figure workflow:

1. Load `simulations_becker_fig6_full.csv`.
2. Filter the data by distribution family and rho.
3. Plot `Bias_ICA` against `N`.
4. Use parameter settings as colored lines.
5. Save the result as `fig6_becker_replikation.pdf`.

The current figure script is designed around the existing Becker-style preliminary output. It is not yet generalized for final thesis figure generation or the organized `outputs/` directory.

## 11. Current Libraries and Dependencies

Libraries imported by the Python implementation:

- `numpy`
- `pandas`
- `scipy.stats`
- `statsmodels.api`
- `sklearn.decomposition.FastICA`
- `matplotlib.pyplot`
- `seaborn`
- `tqdm`
- `warnings`

Dependencies currently listed in `requirements.txt`:

- `Flask==2.0.3`
- `requests==2.26.0`
- `pytest==6.2.5`
- `numpy`
- `pandas`
- `statsmodels`
- `scipy`
- `scikit-learn`
- `tqdm`

Immediate setup note: `matplotlib` and `seaborn` are imported by `src/plot_fig.py` but are not currently listed in `requirements.txt`. `Flask`, `requests`, and `pytest` are listed but do not appear to be used by the current implementation files inspected here. Dependency cleanup has already been marked as a later task, not a current priority.

## 12. Current Output Files

Current source-code output paths:

- `src/main.py` writes `simulations_becker_fig6_full.csv` to the repository root.
- `src/plot_fig.py` writes `fig6_becker_replikation.pdf` to the repository root.
- `src/table_analysis.py` reads `simulations_ergebnisse_gross.csv` from the repository root.

Current organized repository artifacts:

- `outputs/data/simulations_becker_fig6_full.csv`
- `outputs/figures/fig6_becker_replikation.pdf`
- `outputs/logs/`

Interpretation for now:

- `simulations_becker_fig6_full.csv` and `fig6_becker_replikation.pdf` are preliminary generated artifacts, not final thesis results.
- `src/table_analysis.py` is a preliminary exploratory artifact and should be reviewed later before it is used.
- The code paths and organized output folders are currently not aligned.
- Future generated outputs should go into `outputs/data/`, `outputs/figures/`, and `outputs/logs/`; code changes for this should be proposed separately before implementation.

## 13. Current Strengths of the Implementation

Current implementation strengths, at the architecture level:

- The code is modular and separates data generation, estimation, simulation, and plotting.
- `DataGenerator` makes the simulation DGP explicit and configurable.
- `ICAEstimator` provides a reusable class with formula parsing, input checks, missing-value handling, bootstrap output, and a `CF` switch.
- `SimulationEngine` centralizes repeated scenario execution rather than embedding all loops directly in `main.py`.
- The simulation grid already includes sample-size variation, distribution variation, parameter variation, and endogeneity-strength variation.
- Failures during simulation are not allowed to crash the full run; they are currently represented as invalid ICA estimates.
- The plotting script already has a Becker-style panel structure that can serve as a starting point for a later thesis figure plan.

These are implementation-structure observations only, not claims of methodological correctness.

## 14. Current Risks or Unclear Parts

These points should be treated as later audit targets, not as final findings:

- The source code still uses root-level output paths, while the repository organization now prefers `outputs/data/`, `outputs/figures/`, and `outputs/logs/`.
- `SimulationEngine` calls `ICAEstimator._run_single_estimation()` directly, bypassing the public `fit()` method and its bootstrap/result-table workflow. This is intentional for now as a performance shortcut, but not ideal as final API design.
- Failed ICA runs are represented as `NaN`, but the returned simulation table does not yet include an explicit failure count or failure rate.
- The current simulation output includes `Avg_Skewness`, but `src/table_analysis.py` expects `Avg_Kurtosis` as well.
- `src/table_analysis.py` reads `simulations_ergebnisse_gross.csv`, which is separate from the current `simulations_becker_fig6_full.csv` workflow.
- `plot_fig.py` labels the y-axis as relative bias but currently plots the `Bias_ICA` column. The metric definition and naming should be clarified before interpreting figures.
- `requirements.txt` does not list all plotting dependencies used by the code.
- `README.md` is still generic and does not yet describe the thesis-specific project.
- The current use of FastICA instead of the R reference implementation's JADE approach is already known as a critical later audit topic, but should not be resolved at this overview stage.
- Formula parsing supports a compact syntax but should later be compared carefully to the R formula interface.
- Exogenous-regressor handling exists in `ICAEstimator`, but the current main simulation path uses only `formula="Y ~ P"`.

Naming note for later implementation: the current `Bias_ICA` column should probably be replaced or supplemented with clearer metric names once the final simulation schema is implemented. A likely first draft is `bias_ica_mean` for the primary mean-bias metric, `bias_ica_median` only as an optional robustness metric, and `relative_bias_ica` for the Becker-style relative-bias metric adapted to the ICA setting.

## 15. Open Questions

Open questions before the later paper/R/Python comparison audit:

1. What is the best concrete implementation path for moving generated outputs into `outputs/data/`, `outputs/figures/`, and `outputs/logs/`?
2. What public point-estimation API should replace direct simulation calls to `_run_single_estimation()` later: `fit_point()`, `estimate_point()`, or another name?
3. Which parts of the draft final simulation schema should become required, and which should remain optional robustness or diagnostic columns?
4. Should the current `Bias_ICA` column be replaced outright, or temporarily supplemented with clearer columns during a transition?
5. Should `src/table_analysis.py` be kept as a preliminary artifact, moved, rewritten, or removed later?
6. Which parts of `requirements.txt` are required for the final thesis workflow, and which are leftovers from the initial project scaffold?
7. How should the final quick/intermediate/final simulation modes be represented in code: separate scripts, configuration dictionaries, command-line arguments, or documented manual edits?
8. Should the final figure-generation script be generalized beyond the current Becker-style preliminary Figure 6 reproduction?
9. How should warnings and failed ICA runs be logged for long final simulations?
10. How should the Python implementation document the known FastICA-versus-JADE difference before any method change is considered?
