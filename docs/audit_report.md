# Initial Paper-R-Python Audit Report

Source basis:

- `docs/paper_notes.md`
- `docs/model_equations.md`
- `docs/r_reference_analysis.md`
- `docs/python_implementation_overview.md`
- `docs/code_mapping.md`
- Inspected Python source files in `src/`

Scope: This is the first broad comparison of the Haschka/Dost paper, the R reference implementation, and the current Python implementation. It does not implement fixes. It also does not assume that Python is wrong whenever it differs from R; differences are classified by their methodological role and current evidence.

## Classification Summary

| Area | Classification | Severity | Short rationale |
|---|---|---:|---|
| Core simple simulation DGP | likely correct but needs verification | medium | Python implements `P = eta + rho xi`, `Y = alpha + beta P + xi`, matching the simple proof-style DGP, but not richer paper simulation variants. |
| ICA input without exogenous regressors | likely correct but needs verification | medium | Python uses `[Y, P]`, matching paper examples and R practical code. |
| Exogenous-regressor residualization before ICA | likely correct but needs verification | medium | Python residualizes `Y` and each endogenous `P` on `X`, matching paper/R structure, but intercept and factor handling need checks. |
| ICA algorithm | inconsistent with the R implementation | high | R and paper examples use JADE; Python uses FastICA. This is a critical later audit point. |
| Most-normal component selection | likely correct but needs verification | medium | Python standardizes components and applies KS against standard normal; R uses component empirical mean/sd in KS. These are close if variance is nonzero. |
| `CF = TRUE` behavior | likely correct but needs verification | medium | Python supports the paper-grounded control-function regression. |
| `CF = FALSE` behavior | unclear because the paper is ambiguous | medium | Python mirrors R's intended residualization variant, but the paper does not describe this as the main procedure. |
| Formula parsing | incomplete | medium | Python supports a simple subset of the R formula interface. |
| Missing values and validation | likely correct but needs verification | low | Python broadly mirrors R but is narrower for exogenous factor variables and does not report dropped rows. |
| Bootstrap | likely correct but needs verification | medium | Python reruns the estimator during bootstrap, but failed bootstrap ICA and infinite rank-redraw risk are not handled explicitly. |
| Public return values and diagnostics | incomplete | medium | Python `fit()` does not return the control function or detailed diagnostics publicly. |
| Simulation output schema | incomplete | high | Current output lacks failure rate, valid run count, kurtosis, relative bias, and clearer metric names. |
| Figure 6 plotting | incomplete | medium | Current plot is preliminary and labels relative bias while plotting `Bias_ICA`. |
| Output paths | incomplete | low | Source still uses root-level output filenames, while project decision is `outputs/`. |

## Detailed Audit Issues

### 1. FastICA Versus JADE

- **Classification:** inconsistent with the R implementation; also inconsistent with the paper examples.
- **Severity:** high.
- **Paper reference:** Section 2.1, pp. 9-10; Listing 1, p. 17; Listing 2, p. 19.
- **R reference:** `ICAReg.R`, default `method = "jade"` line 261; ICA calls pass `method` at lines 322 and 493.
- **Python reference:** `src/icaEstimator.py` imports `FastICA` at line 11 and uses it at lines 124-132.
- **Explanation:** The R reference implementation and paper examples use JADE through the R `ica` package. Python currently uses scikit-learn's FastICA. This may be an acceptable implementation choice, but it is not automatically methodologically equivalent. The paper's identification proof is cumulant-based and JADE is explicitly mentioned as a fourth-order cumulant method.
- **Suggested fix or clarification:** Do not change the algorithm yet. Create a dedicated FastICA-versus-JADE audit step that explains algorithmic differences, availability of Python JADE implementations, reproducibility, and whether simulation results are sensitive to the choice.
- **Changes mathematical behavior:** Possibly yes. The ICA algorithm can affect recovered components and estimates.
- **Could affect thesis results:** Yes, potentially strongly.
- **User approval required before implementation:** Yes.

### 2. `CF = FALSE` Is R-Reference Behavior, Not Clearly Paper-Derived

- **Classification:** unclear because the paper is ambiguous.
- **Severity:** medium.
- **Paper reference:** Section 3.1, p. 16; Section 3.2, pp. 18-19; `docs/model_equations.md` Section 10.
- **R reference:** `ICAReg.R`, `CF = FALSE` residualization logic lines 359-399 and 524-564; README line 7.
- **Python reference:** `src/icaEstimator.py` lines 152-160; default `CF=False` line 26.
- **Explanation:** The paper's explicit estimation procedure adds the recovered normal component to the final regression. The R implementation additionally supports, and defaults to, `CF = FALSE`, where endogenous variables are residualized on the recovered component and the component is not included directly in final OLS. Python mirrors this R-style option and also defaults to `CF=False`.
- **Suggested fix or clarification:** Document `CF=True` as the paper-grounded control-function form and `CF=False` as an R reference implementation variant. Later, decide which should be default for final thesis simulations.
- **Changes mathematical behavior:** Yes, if the default or final simulation mode changes.
- **Could affect thesis results:** Yes.
- **User approval required before implementation:** Yes.

### 3. Component-Selection KS Test Is Close to R, But Needs Edge-Case Verification

- **Classification:** likely correct but needs verification.
- **Severity:** medium.
- **Paper reference:** Section 3.1, p. 16; Section 3.2, p. 18; the paper says to identify the most normal component but does not define the statistic.
- **R reference:** `ICAReg.R` lines 325-331 and 496-502 use `ks.test(x, "pnorm", mean = mean(x), sd = sd(x))`.
- **Python reference:** `src/icaEstimator.py` lines 134-147 standardize each component and run `stats.kstest(comp_std, "norm")`.
- **Explanation:** Standardizing a component and testing against standard normal is broadly equivalent to R's component-specific mean/sd KS setup when the component has nonzero variance. However, tie behavior, zero variance, near-zero variance, and exact p-value/statistic differences can matter in unstable simulation scenarios.
- **Suggested fix or clarification:** Later add a small audit example comparing R-style and Python-style KS values on the same component vectors. Do not change the diagnostic without approval.
- **Changes mathematical behavior:** Usually no for normal component choice, but yes if edge cases select a different component.
- **Could affect thesis results:** Yes, if component selection differs in difficult scenarios.
- **User approval required before implementation:** Yes.

### 4. Exogenous-Regression Residualization Looks Structurally Aligned But Needs Concrete Testing

- **Classification:** likely correct but needs verification.
- **Severity:** medium.
- **Paper reference:** Remark 5, pp. 15-16; Section 3.2, pp. 18-19; Section 3.3, pp. 19-20.
- **R reference:** `ICAReg.R` lines 469-493.
- **Python reference:** `src/icaEstimator.py` lines 105-120 and `_get_residuals()` lines 91-97.
- **Explanation:** Python residualizes `Y` and every endogenous regressor on exogenous regressors before ICA, which matches the paper and R structure. Python also includes exogenous variables in the final design. The remaining uncertainty is about intercept behavior when formulas use `-1`, and about nonnumeric/factor exogenous variables that R formula tools may support.
- **Suggested fix or clarification:** Later run or design a minimal exogenous-regressor example and compare the intended matrices: residualized ICA input, final OLS design, and intercept handling.
- **Changes mathematical behavior:** Potentially yes if intercept handling or exogenous encoding changes.
- **Could affect thesis results:** Yes for simulations or applications with exogenous controls.
- **User approval required before implementation:** Yes.

### 5. Formula Parsing Supports Only a Simple Subset of R Formula Behavior

- **Classification:** incomplete.
- **Severity:** medium.
- **Paper reference:** The paper does not define formula syntax; Section 3 describes variables conceptually.
- **R reference:** README lines 2-8; `ICAReg.R` line 264 uses `nlme::splitFormula()`, and examples include `as.factor(week)` in line 742.
- **Python reference:** `src/icaEstimator.py` lines 46-62.
- **Explanation:** Python manually splits strings on `~`, `|`, and `+`, with simple `-1` detection. This is enough for simple thesis formulas such as `Y ~ P` or `Y ~ P | X`, but it does not support R-style formula transformations, interactions, factor expansion, or robust parsing.
- **Suggested fix or clarification:** For now, document the supported formula subset. Later, if empirical examples need categorical variables or transformations, propose either explicit preprocessing in pandas or a formula library decision.
- **Changes mathematical behavior:** Not for simple simulations; yes if formula features are added later.
- **Could affect thesis results:** Low for current simple simulations, medium for applied examples with controls.
- **User approval required before implementation:** Yes.

### 6. Public Python API Does Not Return the Control Function

- **Classification:** incomplete.
- **Severity:** medium.
- **Paper reference:** Section 3.1, p. 16; Section 3.2, pp. 18-19, where the recovered component is central to the method.
- **R reference:** `ICAReg.R` returns `list(Estimates1, control_func)` at line 587.
- **Python reference:** `_run_single_estimation()` returns `(params, control_func)` at lines 167-168, but public `fit()` returns only `result_df` at line 244.
- **Explanation:** The public Python method hides the recovered component. That limits auditability because the thesis may need diagnostics for the selected component, plots, normality checks, and possibly Figure 8-style evidence.
- **Suggested fix or clarification:** Later propose an estimator result object or additional attributes that expose the selected control function and diagnostics while preserving a clean API.
- **Changes mathematical behavior:** No if only return values change.
- **Could affect thesis results:** Indirectly yes, because diagnostics and reporting affect interpretation.
- **User approval required before implementation:** Yes.

### 7. Bootstrap Lacks Explicit Failure Handling and Retry Limits

- **Classification:** incomplete.
- **Severity:** medium.
- **Paper reference:** Introduction p. 6 and Discussion p. 45 mention bootstrap standard errors, but the paper does not specify the algorithm.
- **R reference:** `ICAReg.R` bootstrap functions lines 11-259; rank redraw loops lines 20-30 and 126-136.
- **Python reference:** `src/icaEstimator.py` lines 185-228.
- **Explanation:** Python reruns the full point-estimation logic inside bootstrap samples, which matches the broad R idea. However, rank-deficient samples are redrawn without a maximum retry count, and ICA failures during bootstrap are not caught or counted. R has similar unresolved risks, so this is not simply a Python deviation.
- **Suggested fix or clarification:** Later propose a bounded retry policy and explicit bootstrap-failure reporting. Decide whether failed bootstrap draws should be retried, stored as `NaN`, or cause the fit to fail.
- **Changes mathematical behavior:** Yes, if failed bootstrap samples are handled differently.
- **Could affect thesis results:** Yes, especially standard errors and p-values.
- **User approval required before implementation:** Yes.

### 8. Simulation Output Schema Is Not Yet Thesis-Ready

- **Classification:** incomplete.
- **Severity:** high.
- **Paper reference:** Table 1 note, p. 22 reports mean estimates, empirical SD, RMSE, and bias t-ratio; project simulation goals also require Becker-style relative bias.
- **R reference:** Not applicable; R file is an estimator, not the Python simulation engine.
- **Python reference:** `src/simulation.py` lines 89-110; draft schema in `docs/python_implementation_overview.md` Section 9.
- **Explanation:** Current simulation output contains `N`, `Rho`, distribution name/parameter string, average skewness, OLS/ICA bias, and RMSE. It does not report `n_iterations`, true beta, valid/failed ICA run counts, failure rate, kurtosis, mean ICA estimate, relative bias, or clearly named mean/median bias columns.
- **Suggested fix or clarification:** Use the documented draft schema as the starting point for a later implementation plan. Keep it flexible until quick-mode outputs and runtime checks show what is practical.
- **Changes mathematical behavior:** No for estimation itself, but yes for metric definitions and interpretation.
- **Could affect thesis results:** Yes, because final conclusions depend on metrics and failure accounting.
- **User approval required before implementation:** Yes.

### 9. Current `Bias_ICA` Uses Median-Based Bias But Plot Labels Relative Bias

- **Classification:** inconsistent with the Python implementation's intended metric documentation.
- **Severity:** high.
- **Paper reference:** Haschka/Dost simulation tables emphasize bias/RMSE; Becker-style relative bias is an evaluation/presentation adaptation, not the ICA method source.
- **R reference:** Not applicable.
- **Python reference:** `src/simulation.py` lines 92-98 computes `bias_ica` using the median of valid ICA estimates; `src/plot_fig.py` lines 42-44 plots `Bias_ICA`; `src/plot_fig.py` lines 66-68 labels the axis as relative bias.
- **Explanation:** The plot labels the y-axis as relative bias, but it plots `Bias_ICA`, which is currently an absolute median-based bias. The user has clarified that the primary later relative-bias definition should be `bias_ica_mean / bias_ols_mean`, with median only optional as robustness.
- **Suggested fix or clarification:** Do not interpret current Figure 6-style output as final thesis evidence. Later replace or supplement `Bias_ICA` with explicit columns such as `bias_ica_mean`, `bias_ica_median`, and `relative_bias_ica`.
- **Changes mathematical behavior:** No for estimator logic, yes for simulation metric definitions and figures.
- **Could affect thesis results:** Yes, strongly for reported figures.
- **User approval required before implementation:** Yes.

### 10. ICA Simulation Failure Handling Is Present But Not Reported

- **Classification:** incomplete.
- **Severity:** high.
- **Paper reference:** Section 4.5, pp. 33-36 and Section 4.10, p. 43 discuss instability and assumption breakdowns.
- **R reference:** R estimator does not explicitly define failed ICA handling in the documented analysis.
- **Python reference:** `src/simulation.py` lines 77-90 catches exceptions and appends `np.nan`; aggregation lines 89-110 filter valid ICA estimates.
- **Explanation:** Python already avoids crashing a full simulation when ICA fails, which is useful. But failures are silently excluded from bias/RMSE except through reduced valid sample size, and the output does not report failure counts or failure rates.
- **Suggested fix or clarification:** Later add `n_total_runs`, `n_valid_ica_runs`, `n_failed_ica_runs`, and `failure_rate_ica` to the simulation output. Bias and RMSE should use valid estimates only and document exclusions.
- **Changes mathematical behavior:** No for point estimates, yes for aggregation transparency.
- **Could affect thesis results:** Yes, because high failure rates change interpretation.
- **User approval required before implementation:** Yes.

### 11. Distribution Diagnostics Are Incomplete

- **Classification:** incomplete.
- **Severity:** medium.
- **Paper reference:** Assumption 2, p. 11; Remark 3, p. 15; Section 4.7, pp. 39-40.
- **R reference:** Not applicable to estimator function.
- **Python reference:** `DataGenerator.generate()` stores skewness and kurtosis in dataframe attrs at lines 129-130; `SimulationEngine.run()` records only skewness at lines 66-67 and 106.
- **Explanation:** The generator computes both skewness and kurtosis, but the simulation output currently stores only average skewness. Kurtosis is important because the paper allows identification through either third or fourth cumulants; symmetric non-normal distributions may have low skewness but nonzero kurtosis.
- **Suggested fix or clarification:** Later include `avg_kurtosis_P` and optionally standard deviations of skewness/kurtosis in the simulation output.
- **Changes mathematical behavior:** No.
- **Could affect thesis results:** Yes, for diagnostics and Figure 8-style thresholds.
- **User approval required before implementation:** Yes.

### 12. Data Generator Covers the Simple DGP But Not the Full Paper Simulation Space

- **Classification:** incomplete.
- **Severity:** medium.
- **Paper reference:** Basic model Equations (1)-(4), pp. 7-10; benchmark DGP Equations (21)-(25), pp. 20-21; robustness sections 4.5-4.10.
- **R reference:** R estimator accepts data; it does not define the thesis simulation DGP.
- **Python reference:** `src/data_generator.py` lines 115-121.
- **Explanation:** Python currently implements the simple core DGP with one endogenous regressor and no exogenous regressors: `P = eta + rho xi`, `Y = alpha + beta P + xi`. This is a useful starting point. It does not yet implement optional additional noise `u`, observed exogenous regressors `X`, benchmark components such as `w`, or explicit assumption-violation scenarios.
- **Suggested fix or clarification:** Keep the simple DGP for initial audit and quick checks. Later design additional DGP variants only after the paper/R/Python implementation audit is stable.
- **Changes mathematical behavior:** Yes if DGP variants are added.
- **Could affect thesis results:** Yes.
- **User approval required before implementation:** Yes.

### 13. Output Paths Are Not Aligned With the Agreed Repository Organization

- **Classification:** incomplete.
- **Severity:** low.
- **Paper reference:** Not applicable.
- **R reference:** Not applicable.
- **Python reference:** `src/main.py` line 113 writes `simulations_becker_fig6_full.csv`; `src/plot_fig.py` lines 7 and 74 read/write root-level paths.
- **Explanation:** The project decision is that future outputs should go under `outputs/data/`, `outputs/figures/`, and `outputs/logs/`. Existing source code still reads/writes old root-level filenames.
- **Suggested fix or clarification:** Later propose a small path cleanup that updates output locations and creates directories if needed.
- **Changes mathematical behavior:** No.
- **Could affect thesis results:** No, but it affects reproducibility and organization.
- **User approval required before implementation:** Yes.

### 14. Dependency List Is Incomplete For Plotting

- **Classification:** incomplete.
- **Severity:** low.
- **Paper reference:** Not applicable.
- **R reference:** Not applicable.
- **Python reference:** `src/plot_fig.py` lines 1-3 imports `matplotlib` and `seaborn`; `requirements.txt` does not list them.
- **Explanation:** The plotting script depends on packages not currently listed in `requirements.txt`. Conversely, `Flask`, `requests`, and `pytest` appear in requirements but are not used by the inspected implementation files.
- **Suggested fix or clarification:** Later perform dependency cleanup after the code path for simulations and plotting is clearer.
- **Changes mathematical behavior:** No.
- **Could affect thesis results:** Indirectly, if figures cannot be reproduced in a clean environment.
- **User approval required before implementation:** Yes.

### 15. Private Point-Estimation Method Is Used Intentionally In Simulations

- **Classification:** incomplete.
- **Severity:** low.
- **Paper reference:** Not applicable to software API.
- **R reference:** Not applicable.
- **Python reference:** `src/simulation.py` lines 74-83; `src/icaEstimator.py` lines 99-168.
- **Explanation:** `SimulationEngine` calls `_run_single_estimation()` directly. The user clarified this is intentional for now because `fit()` performs bootstrapping and would be too expensive for large grids. The design is temporary and should not become the final public API.
- **Suggested fix or clarification:** Later propose a public point-estimation method such as `fit_point()` or `estimate_point()`.
- **Changes mathematical behavior:** No if it only exposes existing point-estimation behavior.
- **Could affect thesis results:** Low directly, but it improves maintainability and reproducibility.
- **User approval required before implementation:** Yes.

## Immediate Priorities Before Code Changes

1. Keep the current audit as documentation only.
2. Do not change FastICA or `CF` behavior before a focused methodological decision.
3. Next useful audit step: inspect concrete Python behavior with simple examples, especially `CF=True` vs `CF=False`, exogenous-regressor residualization, and component-selection diagnostics.
4. When implementation begins later, start with low-risk infrastructure changes only after approval: output paths, explicit simulation schema, failure counts, and public point-estimation API.
