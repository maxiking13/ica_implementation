# Simulation Design Analysis

Source basis:

- Python files: `src/data_generator.py`, `src/simulation.py`, `src/main.py`, `src/plot_fig.py`
- Haschka/Dost notes: `docs/paper_notes.md`
- Becker reference notes: `docs/becker_reference_notes.md`
- Python overview and audit context: `docs/python_implementation_overview.md`, `docs/audit_report.md`

Scope: This document analyzes the current simulation design. It does not modify source code and does not treat current preliminary outputs as final thesis evidence.

## 1. What the Simulation Currently Tests

The current simulation tests how naive OLS and the Python ICA estimator behave across:

- sample sizes,
- distribution families for the non-normal component,
- distribution parameters,
- endogeneity strength values `rho`.

Current simulation dimensions are defined mainly in `src/main.py` lines 48-101 and executed through `SimulationEngine.run()` in `src/simulation.py` lines 24-114.

The current simulation does not yet test:

- exogenous regressors,
- multiple endogenous regressors,
- `CF=True` versus `CF=False`,
- JADE versus FastICA,
- optional additional error component `u`,
- explicit assumption-violation scenarios such as correlated `eta` and `xi`,
- failure-rate-based decision thresholds.

## 2. Current Data-Generating Process

The current DGP is implemented in `DataGenerator.generate()` in `src/data_generator.py` lines 115-132:

```text
xi = standard normal
eta = selected distribution
P = eta + rho * xi
Y = alpha + beta * P + xi
```

The returned dataframe contains:

- `Y`
- `P`
- `true_xi`
- `true_eta`

The dataframe also stores:

- `df.attrs["skewness"] = skew(P)`
- `df.attrs["kurtosis"] = kurtosis(P, fisher=True)`

The simulation engine currently records only skewness, not kurtosis.

## 3. Relation to the Haschka/Dost Paper

The current DGP is close to the simple core/proof-style Haschka/Dost setting:

```text
P = eta + rho xi
Y = alpha + beta_1 P + xi
```

Paper references:

- Basic structural model: Equation (1), p. 7.
- Decomposition of `P` and the omitted component: Equation (2), p. 7.
- Formal proof representation: Equations (3)-(4), p. 10.
- Simulation relevance: `docs/paper_notes.md` Section 19.

This is a reasonable starting DGP for development and first simulations. However, it is not the full paper simulation space. The paper also discusses:

- observed exogenous regressors and residualization before ICA,
- benchmark simulations with additional variables,
- optional additional error/noise components,
- identification-breakdown cases,
- distribution sensitivity,
- finite-sample limitations.

So the current simulation is a core-DGP simulation, not yet a full Haschka/Dost simulation replication.

## 4. Current Sample Sizes

`src/main.py` lines 50-51 define:

```text
N = [100, 200, 400, 1000, 4000, 10000]
```

This is a reduced Becker-style sample-size grid. It is also consistent with the current project decision to use small values for development/debugging and larger values only after runtime checks.

Current status:

- Good as a first broad grid.
- Too expensive for quick debugging when combined with all distributions, all rho values, and 500 iterations.
- Not final thesis grid yet.

## 5. Current Distributions

`DataGenerator._generate_eta()` supports more distributions than the current main simulation uses:

- `gamma`
- `exponential`
- `beta`
- `t`
- `uniform`
- `normal`
- `lognormal`
- `f`
- `chisquare`
- `laplace`
- `weibull`

The current Figure 6-style simulation in `src/main.py` uses only:

- `beta`
- `chisquare`
- `gamma`
- `lognormal`
- `t`

These match Becker-style distribution families and are useful for presentation comparability. For the ICA thesis, they should be interpreted as distributions for the non-normal component `eta`, not as Gaussian-copula regressor distributions.

## 6. Current Distribution Parameters

`src/main.py` lines 57-87 define four parameter settings per distribution family:

- Beta:
  - `a=0.5, b=0.5`
  - `a=1.0, b=1.0`
  - `a=2.0, b=2.0`
  - `a=4.0, b=4.0`
- Chi-square:
  - `df=2`
  - `df=8`
  - `df=14`
  - `df=20`
- Gamma:
  - `shape=1.0, scale=0.5`
  - `shape=1.0, scale=2.0`
  - `shape=2.0, scale=4.0`
  - `shape=4.0, scale=2.0`
- Lognormal:
  - `mean=0.0, sigma=1.0`
  - `mean=0.0, sigma=0.75`
  - `mean=0.0, sigma=0.50`
  - `mean=0.0, sigma=0.25`
- Student-t:
  - `df=3`
  - `df=4`
  - `df=5`
  - `df=6`

These parameter settings are Becker-style and useful for a first Figure 6 layout. For ICA, the final distribution grid should be checked against Haschka/Dost's non-normality and cumulant logic, especially for symmetric distributions and near-normal cases.

## 7. Current Endogeneity Strength Values

`src/main.py` lines 53-54 define:

```text
rho = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
```

`rho` is then inserted into every distribution configuration in `src/main.py` lines 89-95.

In the current DGP, `rho` controls the loading of the normal error/confounder component into `P`:

```text
P = eta + rho * xi
```

This is conceptually appropriate for the Haschka/Dost setting. The exact final `rho` grid should remain provisional until runtime and stability checks are done.

## 8. Current Number of Iterations

Defaults and actual current usage differ:

- `SimulationEngine.__init__()` default: `n_iterations=100` (`src/simulation.py` line 13).
- `src/main.py` current large simulation: `n_iterations=500` (`src/main.py` lines 97-100).

Given the current grid:

```text
6 sample sizes * 8 rho values * 5 distributions * 4 parameter settings = 960 scenarios
```

At 500 iterations, this implies:

```text
960 * 500 = 480,000 simulated datasets / estimation attempts
```

That is not a quick/debug simulation. It is closer to an intermediate or final-style workload, but the output metrics are not yet final-thesis ready.

## 9. Current Random Seed Strategy

The simulation engine sets a seed per generated dataset:

```text
current_seed = self.random_state + i + n
```

Reference: `src/simulation.py` lines 54-64.

Consequences:

- The generated data are partly reproducible for a given `random_state`, sample size, and iteration index.
- The seed does not include distribution family, distribution parameters, or `rho`.
- Scenarios with the same `n` and iteration index reuse the same base random seed while changing distribution transformation and `rho`.
- The ICA estimator inside the simulation is created without a `random_state`:

```text
estimator_ica = ICAEstimator(formula="Y ~ P", CF=False)
```

Reference: `src/simulation.py` line 75.

This means the generated data are seeded, but FastICA itself is not fully reproducible in the current simulation loop. This is important for thesis reproducibility.

## 10. Current OLS Estimator

The current OLS baseline is:

```text
Y ~ const + P
```

Reference: `src/simulation.py` lines 69-72.

The estimated coefficient on `P` is stored in `estimates_ols`.

This is appropriate as the untreated/endogenous baseline for the current simple DGP. It matches the logic that OLS is biased because `P` contains the shared normal component `xi`.

## 11. Current ICA Estimator

The simulation uses:

```text
ICAEstimator(formula="Y ~ P", CF=False)
```

Reference: `src/simulation.py` lines 74-83.

Important current behavior:

- It uses only the one-endogenous-regressor case.
- It uses `CF=False`.
- It calls `_run_single_estimation()` directly.
- It skips bootstrapping.
- It uses the current Python estimator's FastICA implementation.
- It does not set an ICA random seed.

The direct private-method call is an intentional temporary performance shortcut, because `fit()` performs bootstrap and would be too expensive for large grids. A public point-estimation method should be proposed later, but not implemented without approval.

## 12. Current Bias Definition

The current OLS bias is:

```text
Bias_OLS = mean(estimates_ols) - true_beta
```

Reference: `src/simulation.py` lines 92-93.

The current ICA bias is:

```text
Bias_ICA = median(valid_ica_estimates) - true_beta
```

Reference: `src/simulation.py` lines 89-95.

This is important: although the code comment says bias is the average estimate minus the true value, the current ICA calculation uses the median, not the mean.

Current status:

- OLS bias is mean-based.
- ICA bias is median-based.
- This is not aligned with the draft final metric definition, where the primary ICA bias should be mean-based and median should be optional robustness output.

## 13. Current Relative Bias Definition

There is currently no implemented relative bias column.

The plotting script labels the y-axis as:

```text
Relative Bias of the Endogenous Regressor
```

Reference: `src/plot_fig.py` lines 66-68.

But it plots:

```text
Bias_ICA
```

Reference: `src/plot_fig.py` lines 41-45.

Therefore, the current Figure 6-style plot is preliminary and should not be interpreted as Becker-style relative bias.

The current project draft definition is:

```text
bias_ols_mean = mean(beta_hat_OLS - beta_true)
bias_ica_mean = mean(beta_hat_ICA - beta_true)
relative_bias_ica = bias_ica_mean / bias_ols_mean
```

This should be implemented later only after approval.

## 14. Current RMSE Definition

The current OLS RMSE is:

```text
RMSE_OLS = sqrt(mean((estimates_ols - true_beta)^2))
```

Reference: `src/simulation.py` lines 96-98.

The current ICA RMSE is:

```text
RMSE_ICA = sqrt(mean((valid_ica_estimates - true_beta)^2))
```

Reference: `src/simulation.py` lines 96-98.

ICA RMSE uses valid, non-NaN ICA estimates only. This is reasonable if failures are separately reported, but the current output does not yet report failure counts.

## 15. Handling of Failed ICA Runs

Current behavior:

- If `_run_single_estimation()` raises an exception, the simulation appends `np.nan` to `estimates_ica`.
- Later, invalid ICA estimates are filtered out:

```text
valid_ica = [x for x in estimates_ica if not np.isnan(x)]
```

Reference: `src/simulation.py` lines 77-90.

Current limitation:

- Failed runs are not silently crashed, which is good.
- But the output does not report:
  - `n_total_runs`
  - `n_valid_ica_runs`
  - `n_failed_ica_runs`
  - `failure_rate_ica`

This is a high-priority missing metric for thesis interpretation.

## 16. Bootstrapping in Simulation

Bootstrapping is skipped in the simulation.

Current behavior:

- `SimulationEngine` calls `_run_single_estimation()` directly instead of `ICAEstimator.fit()`.
- This avoids `n_bootstraps` repetitions inside every Monte Carlo iteration.

Reference:

- `src/simulation.py` lines 74-83.
- `docs/python_implementation_overview.md` Section 4.

Reason:

- `fit()` performs bootstrap standard-error estimation.
- Running bootstrap inside every simulation iteration would be very expensive for a large grid.

Current status:

- This is an intentional temporary fast simulation mode.
- It should later be formalized with a public point-estimation method such as `fit_point()` or `estimate_point()`.

## 17. Whether the Output Supports Figure 6

Current output partially supports a Becker-style Figure 6 layout.

Supported:

- sample size `N`,
- distribution family,
- distribution parameter string,
- rho/endogeneity strength,
- one performance metric for ICA,
- one row per scenario.

Not yet supported correctly:

- true relative bias,
- mean-based ICA bias,
- failure rate,
- valid run counts,
- kurtosis diagnostics,
- clean column names,
- organized output paths,
- final thesis interpretation.

The current `src/plot_fig.py` can generate a 5-by-8 panel layout, but it plots `Bias_ICA` while labeling it as relative bias. So it is a visual prototype, not a final Figure 6.

## 18. Whether the Output Supports Figure 8

Current output is not sufficient for a Figure 8-style decision flowchart.

It provides early ingredients:

- sample size,
- distribution family and parameters,
- rho,
- average skewness,
- OLS and ICA bias/RMSE.

But Figure 8-style guidance needs more:

- failure rate,
- valid run count,
- kurtosis,
- relative bias,
- RMSE thresholds,
- possibly recovered-component normality diagnostics,
- possibly ICA convergence information,
- quick/final mode indicator,
- simulation-derived thresholds.

Also, the final flowchart should rely on diagnostics that a researcher can observe or compute in real applications. True bias and RMSE can justify thresholds in simulation, but cannot be decision nodes in real data.

## 19. Missing Metrics Needed for the Thesis

At minimum, future simulation output should include the draft schema already documented in `docs/python_implementation_overview.md`:

Scenario metadata:

- `N`
- `n_iterations`
- `rho`
- `true_beta`
- `distribution`
- `distribution_params`

Distribution diagnostics:

- `avg_skewness_P`
- `avg_kurtosis_P`
- optional `std_skewness_P`
- optional `std_kurtosis_P`

Run validity:

- `n_total_runs`
- `n_valid_ica_runs`
- `n_failed_ica_runs`
- `failure_rate_ica`

Estimator summaries:

- `mean_beta_ols`
- `mean_beta_ica`
- optional `median_beta_ica`

Bias metrics:

- `bias_ols_mean`
- `bias_ica_mean`
- optional `bias_ica_median`

Relative bias:

- `relative_bias_ica = bias_ica_mean / bias_ols_mean`
- optional `relative_bias_ica_percent = 100 * relative_bias_ica`

RMSE:

- `rmse_ols`
- `rmse_ica`

Additional useful diagnostics later:

- component-normality statistic,
- selected component index,
- ICA convergence warnings,
- FastICA iteration count if available,
- runtime per scenario,
- simulation mode: `quick`, `intermediate`, or `final`.

## 20. Recommended Improvements

No code changes should be made from this document alone. Recommended later improvements are:

1. **Separate quick, intermediate, and final modes**
   - Quick mode: small grid and `n_iterations=5` to `20`, only for debugging.
   - Intermediate mode: `n_iterations=50` to `100`, for runtime and output checks.
   - Final mode: larger grid and likely `n_iterations=500` to `1000` if runtime allows.
   - Quick results must not be interpreted as thesis evidence.

2. **Make simulation output thesis-ready**
   - Add failure counts and failure rate.
   - Add mean and median ICA summaries separately.
   - Add relative bias using the approved Becker-style ICA definition.
   - Add kurtosis and optional skewness/kurtosis standard deviations.

3. **Fix metric naming before final plots**
   - Replace broad names like `Bias_ICA` with explicit names such as `bias_ica_mean`, `bias_ica_median`, and `relative_bias_ica`.
   - Ensure Figure 6 plots true relative bias if labeled as relative bias.

4. **Improve reproducibility**
   - Pass a deterministic `random_state` into `ICAEstimator` during simulation.
   - Consider whether scenario-level seeds should include distribution, parameter, and rho identifiers.
   - Record seed strategy in the output or logs.

5. **Formalize fast point-estimation mode**
   - Replace direct `_run_single_estimation()` calls with an approved public method such as `fit_point()` or `estimate_point()`.
   - Keep bootstrap out of large Monte Carlo loops unless specifically studying estimator-reported uncertainty.

6. **Keep Becker as layout reference, not method source**
   - Use Becker-style Figure 6 layout and relative-bias logic.
   - Do not copy Becker thresholds or Gaussian-copula assumptions as ICA rules.

7. **Expand DGP only after core audit is stable**
   - Add exogenous regressors later.
   - Add assumption-violation scenarios later.
   - Add optional noise/error variants later.
   - Compare FastICA and JADE before treating final simulations as method evidence.

8. **Support Figure 8 with evidence**
   - Use simulation results to justify thresholds.
   - Keep real-data decision nodes observable: sample size, skewness, kurtosis, nonnormality diagnostics, warnings, and method assumptions.
   - Use true bias/RMSE only behind the scenes to derive and justify thresholds.

## Quick Versus Final Interpretation

Current simulation settings in `src/main.py` are too large for quick debugging but still not final-thesis ready because the output schema and metric definitions are incomplete.

Recommended interpretation:

- Existing generated artifacts are preliminary.
- Current design is useful for discovering code and runtime issues.
- Final thesis evidence should only be produced after:
  - metric definitions are fixed,
  - failure handling is reported,
  - reproducibility is controlled,
  - FastICA versus JADE is addressed,
  - quick/intermediate runtime checks are complete.
