# Codebase Stabilization Plan

Goal: reduce the audit findings into a short implementation plan for a cleaner, defensible, and easier-to-extend Python codebase. This is not a thesis-writing plan and not a Figure 6/Figure 8 plan.

## 1. Executive Summary

- The core Python structure is close: `DataGenerator`, `ICAEstimator`, `SimulationEngine`, `main.py`, and plotting are already separated.
- The simple core DGP is usable as a starting point: `P = eta + rho * xi`, `Y = alpha + beta * P + xi`.
- The largest methodological issue remains FastICA versus JADE; do not replace FastICA yet.
- `CF=True` is closest to the paper's control-function description; `CF=False` mirrors the R reference variant but needs careful documentation.
- Simulation output is the least stable part: metric names, failure reporting, relative bias, and diagnostics need cleanup.
- Direct simulation calls to `_run_single_estimation()` are intentional for speed, but should become a public point-estimation API.
- Output paths should move to `outputs/data/`, `outputs/figures/`, and `outputs/logs/`.
- Reproducibility needs improvement, especially passing `random_state` into ICA during simulations.
- Avoid big refactors until the low-risk stabilization changes are complete.
- Every mathematical behavior change needs explicit approval.

## 2. Critical Issues That Affect Mathematical Correctness

- **FastICA versus JADE:** R and paper examples use JADE; Python uses FastICA. This may affect recovered components and final coefficients.
- **Default `CF=False`:** The paper explains the method mainly as adding the recovered component to final OLS. `CF=False` is R-reference behavior, not clearly paper-derived.
- **Component selection:** Python's KS standardization appears close to R's empirical mean/sd KS test, but edge cases need verification.
- **Exogenous-regressor handling:** Structure looks aligned, but intercept behavior and factor/categorical controls need later testing.
- **Bootstrap failure handling:** Failed ICA or endless rank redraws could affect standard errors.

## 3. Important Issues That Affect Simulation Validity

- Current `Bias_ICA` uses median bias, while the target primary metric is mean bias.
- Relative bias is not implemented, even though the plot labels the y-axis as relative bias.
- Failed ICA runs are stored as `NaN` but failure counts/rates are not reported.
- Kurtosis is computed by `DataGenerator` but not included in simulation output.
- The simulation sets data-generation seeds but does not set `ICAEstimator.random_state`.
- Current large grid is not quick mode, but output is not final-thesis ready.

## 4. Minor Issues That Affect Project Organization Or Reproducibility

- Source code still reads/writes root-level output files instead of `outputs/`.
- `requirements.txt` is missing plotting dependencies and includes likely unused scaffold dependencies.
- `README.md` is generic and not thesis-specific.
- `src/table_analysis.py` is a preliminary artifact and should not drive current implementation.
- Public `fit()` does not expose the recovered control function or diagnostics.

## 5. Open Questions That Are Blocking Code Changes

- Should final simulations use `CF=True`, `CF=False`, or both as separate reported variants?
- Should FastICA remain the implementation method after a matched comparison with R/JADE?
- What exact public point-estimation method name should be used: `fit_point()`, `estimate_point()`, or another name?
- Should `fit()` return only a dataframe, or should it return/attach a richer result object with control function and diagnostics?
- How should failed bootstrap runs be handled: retry, store as `NaN`, or fail the estimation?

## 6. Open Questions That Can Wait

- Whether to add optional error component `u` to the simulation DGP.
- Whether to support full R-style formula syntax, factors, interactions, or transformations.
- Whether to implement a Python JADE dependency or vendored JADE code.
- Final sample-size grid and final iteration count.
- Final Figure 6 and Figure 8 design choices.
- Dependency cleanup beyond obvious missing plotting dependencies.

## 7. Recommended Implementation Order

1. Stabilize output paths and folder creation.
2. Add a public point-estimation method that wraps current `_run_single_estimation()` behavior without bootstrap.
3. Update `SimulationEngine` to use the public point-estimation method.
4. Improve simulation output schema: valid/failed run counts, mean/median estimates, mean bias, RMSE, relative bias, skewness, kurtosis.
5. Add deterministic ICA random seeds in simulation.
6. Add small verification checks or lightweight examples for `CF=True`, `CF=False`, and exogenous residualization.
7. Only after that, run a matched FastICA-versus-R/JADE comparison.

## 8. First Three Code Changes To Do

1. **Output path cleanup**
   - Write simulation CSVs to `outputs/data/`.
   - Write figures to `outputs/figures/`.
   - Keep logs under `outputs/logs/`.
   - Mathematical behavior changes: no.

2. **Public point-estimation API**
   - Add a public method such as `estimate_point()` that calls the current point-estimation logic and returns point estimates plus control function.
   - Update simulations to call the public method instead of `_run_single_estimation()`.
   - Mathematical behavior changes: no, if it is only an API wrapper.

3. **Simulation output schema cleanup**
   - Add failure counts/rate, `mean_beta_ols`, `mean_beta_ica`, optional `median_beta_ica`, `bias_ols_mean`, `bias_ica_mean`, optional `bias_ica_median`, `relative_bias_ica`, `rmse_ols`, `rmse_ica`, `avg_skewness_P`, and `avg_kurtosis_P`.
   - Mathematical behavior changes: no estimator change, but metric definitions change and must be approved.

## 9. Things That Should Explicitly Not Be Changed Yet

- Do not replace FastICA with JADE yet.
- Do not add new dependencies for JADE yet.
- Do not change the default `CF` behavior yet.
- Do not expand the DGP to exogenous regressors, extra noise, or assumption-violation scenarios yet.
- Do not build final Figure 6 or Figure 8 logic yet.
- Do not remove `src/table_analysis.py` yet.
- Do not create a large test suite yet.
- Do not treat current generated outputs as final thesis evidence.

## 10. What The User Needs To Decide Before Implementation

- Approve whether the first implementation batch should be:
  1. output paths,
  2. public point-estimation API,
  3. simulation output schema.
- Choose the public method name: recommended `estimate_point()`.
- Confirm that simulation output should use mean ICA bias as primary and median only as optional robustness.
- Confirm whether relative bias should be added now using:

```text
relative_bias_ica = bias_ica_mean / bias_ols_mean
```

- Decide whether `CF=False` remains the simulation default for now, while `CF=True` is kept for later comparison.
