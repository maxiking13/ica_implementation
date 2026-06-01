# Open Questions

This file records ambiguities that should not be silently resolved by assumption. Source basis for the current entries: `papers/haschka_ICA.pdf`, `docs/paper_notes.md`, and `docs/model_equations.md`.

## Paper / Model Ambiguities

1. **Notation for the normal omitted component**
   - The paper first writes `P = eta + rho v` and `xi = v (+ u)` (Equation (2), p. 7), but the formal proof rewrites the system as `P = eta + rho xi` and `Y = alpha + beta_1 P + xi` (Equations (3)-(4), p. 10).
   - Question: For thesis notation and Python documentation, should the shared normal component be denoted `v`, `xi`, or separated into `v` as latent confounder and `xi` as structural error?

2. **Role of the optional exogenous error component `u`**
   - Equation (2), p. 7, allows `xi = v (+ u)`, but the core proof uses the simpler normal source notation.
   - Question: Should simulations include an additional independent error component in the baseline DGP, or only in robustness scenarios?

3. **Component normality selection rule**
   - The paper says to identify the "most normal" ICA component (Section 3, pp. 16-20), but does not specify the exact statistic or standardization rule.
   - Project decision so far: mirror the R implementation using a Kolmogorov-Smirnov based diagnostic unless later audit shows otherwise.
   - Question: Does the R implementation standardize components before the KS test, and how exactly are ties or near-ties handled?

4. **Relationship between paper residualization and `CF = FALSE`**
   - The paper describes residualizing `Y` and `P` on observed exogenous regressors before ICA (Remark 5, pp. 15-16; Section 3.2, pp. 18-19).
   - It does not define a `CF` argument.
   - Question: How does the R implementation's `CF = FALSE` behavior relate to the paper's control-function description?

5. **Intercept handling**
   - The paper includes an intercept in the structural equations and examples, but does not specify formula-level intercept removal or residualization intercept rules.
   - Question: How does the R implementation handle `-1`, intercepts in residualization, and intercepts in the final regression?

6. **Bootstrap procedure**
   - The paper states that the R implementation supplies adapted bootstrap standard errors (Introduction, p. 6; Discussion, p. 45), but does not provide the full algorithm.
   - Question: What exactly is resampled, how are failed bootstrap runs handled, and how are p-values computed?

7. **Diagnostics and warning thresholds**
   - The paper mentions diagnostics and identifies failure modes, but does not define exact software thresholds for warnings.
   - Question: Which diagnostics should be reported in the Python implementation, and which should trigger warnings?

8. **JADE versus FastICA**
   - The paper examples use `method = "jade"` (Listings 1-2, pp. 17-19), while the current Python implementation uses FastICA.
   - Question: Is FastICA methodologically acceptable for the thesis implementation, or should a JADE implementation be considered?

9. **Final simulation grid**
   - The project has provisional quick/intermediate/final runtime modes, but the final thesis grid depends on runtime checks and implementation stability.
   - Question: What final sample sizes, iteration count, distributions, and endogeneity strengths are feasible after quick-mode runtime measurement?

## Python Implementation / Simulation Clarifications

These points were clarified after creating `docs/python_implementation_overview.md`. They are not final code changes; they are documentation-level decisions to guide later implementation proposals.

1. **Generated output paths**
   - Clarification: Future generated outputs should be written to an organized `outputs/` structure:
     - `outputs/data/`
     - `outputs/figures/`
     - `outputs/logs/`
   - Status: Documented as the preferred direction. Source code has not yet been changed.

2. **SimulationEngine and `_run_single_estimation()`**
   - Clarification: The direct call to `ICAEstimator._run_single_estimation()` is intentional for now as a fast simulation mode.
   - Reason: `ICAEstimator.fit()` performs bootstrapping, which would be too expensive for large simulation grids.
   - Status: This should be treated as an intentional temporary performance shortcut, not the ideal final API.
   - Later proposal: expose a public point-estimation method, for example `fit_point()` or `estimate_point()`, that runs the ICA point estimate without bootstrap. Do not implement this without approval.

3. **Draft final simulation output schema**
   - Clarification: The final simulation output should contain at least the following draft columns, but this is not fixed yet.
   - Scenario metadata: `N`, `n_iterations`, `rho`, `true_beta`, `distribution`, `distribution_params`.
   - Distribution diagnostics: `avg_skewness_P`, `avg_kurtosis_P`, optionally `std_skewness_P`, optionally `std_kurtosis_P`.
   - Run validity: `n_total_runs`, `n_valid_ica_runs`, `n_failed_ica_runs`, `failure_rate_ica`.
   - Estimator summaries: `mean_beta_ols`, `mean_beta_ica`, optionally `median_beta_ica`.
   - Bias metrics: `bias_ols_mean`, `bias_ica_mean`, optionally `bias_ica_median`.
   - Relative bias: `relative_bias_ica = bias_ica_mean / bias_ols_mean`, optionally `relative_bias_ica_percent = 100 * relative_bias_ica`.
   - RMSE: `rmse_ols`, `rmse_ica`.
   - Status: First draft only. The exact schema should be refined after concrete code examples, quick-mode outputs, and audit findings.

4. **`Bias_ICA` naming**
   - Clarification: The current `Bias_ICA` column name is too broad for the later final schema.
   - Likely later direction: use explicit names such as `bias_ica_mean`, optional `bias_ica_median`, and `relative_bias_ica`.
   - Status: Do not rename or refactor yet. Decide during the concrete simulation-output implementation step.
