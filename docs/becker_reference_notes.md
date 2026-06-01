# Becker Reference Notes

Source: `papers/Becker_example.pdf`, Becker et al., *Revisiting Gaussian copulas to handle endogenous regressors*, Journal of the Academy of Marketing Science, 2022.

Scope: These notes use Becker et al. as an evaluation and presentation reference. The goal is not to implement the Gaussian copula method.

## 1. Simulation Design Logic

### Becker-specific content

- Becker et al. use simulation studies to replicate, extend, and stress-test the Gaussian copula approach rather than only reporting one favorable DGP (Simulation Study 1, pp. 4-7; Study 4, pp. 10-15; Study 5, pp. 15-16).
- Study 1 starts from Park and Gupta's Case 1 and varies intercept handling and sample size (pp. 4-6).
- Study 4 broadens the design to additional factors: sample size, endogeneity/error correlation, endogenous regressor distribution, and explained variance `R^2` (pp. 10-12; Table 1, p. 12).
- Study 5 tests robustness to misspecification of the error distribution and copula structure (pp. 15-16).

### Transferable evaluation logic

- Start from a known/reference DGP, then extend it systematically along factors that are likely to affect method performance.
- Separate design factors from performance metrics.
- Use simulation results not only to show average performance, but to derive boundary conditions and practical warnings.

### Possible ICA adaptation

- For ICA, the first grid should follow the Haschka/Dost DGP and assumptions, then vary factors that affect ICA identification: sample size, endogeneity strength, distribution/non-normality of the exogenous component, extra normal noise, and ICA failure/instability.
- Becker's structure is useful, but the factors must be ICA-specific. For example, Gaussian copula correlation structure is Becker-specific and should not become an ICA requirement.

## 2. Relative Bias Definition

### Becker-specific content

- Becker defines bias for parameter `theta` as estimated value minus true value: `theta_hat - theta` (Evaluation criteria, p. 4).
- Mean bias is computed over 1,000 simulation datasets per factor-level combination in Study 1 (p. 4).
- Relative bias is defined as the bias in the copula model divided by the bias in the untreated model without copula (p. 4).
- Becker interprets relative bias as the proportion of original endogeneity bias that remains after correction (p. 4).

### Transferable evaluation logic

- Relative bias is helpful when untreated bias differs across scenarios because it normalizes the corrected method's remaining bias against the original problem size.
- It can make scenarios with different endogeneity strengths more comparable.

### Possible ICA adaptation

- Use the already documented ICA adaptation:

```text
Bias_OLS = mean(beta_hat_OLS - beta_true)
Bias_ICA = mean(beta_hat_ICA - beta_true)
Relative_Bias_ICA = Bias_ICA / Bias_OLS
```

- If `Bias_OLS` is zero or very close to zero, relative bias is unstable and must be flagged.
- Failed ICA runs should be recorded; bias and RMSE should use valid estimates only, with failure rate reported separately.

## 3. Sample Size Variation

### Becker-specific content

- Study 1 expands Park and Gupta's sample sizes to a wide range: `100, 200, 400, 600, 800, 1000, 2000, 4000, 6000, 8000, 10000, 20000, 40000, 60000` (p. 4).
- Study 4 uses sample sizes from `100` to `10000`; Table 1 lists `100, 200, 400, 600, 800, 1000, 2000, 4000, 6000, 8000, 10000` (Table 1, p. 12).
- Becker finds that sample size is central for Gaussian copula performance with intercepts (pp. 5-6, 11-15, 17-19).

### Transferable evaluation logic

- Sample size should be a primary simulation dimension.
- Small samples should be tested explicitly because finite-sample failure can be central to whether a method is usable.
- Results can be translated into sample-size guidance only after systematic simulation evidence.

### Possible ICA adaptation

- Use a Becker-style sample-size axis for presentation, but choose the final ICA grid after runtime checks.
- Current provisional grid:

```text
N = [100, 200, 400, 1000, 4000, 10000]
```

- Quick-mode results must not be used as thesis evidence.

## 4. Distribution Variation

### Becker-specific content

- Study 4 varies the endogenous regressor's distribution because nonnormality is a prerequisite for Gaussian copula identification (pp. 10-11).
- Figure 6 uses five distribution families with four parameter settings each (Figure 6, p. 13):
  - Beta: `(0.50, 0.50)`, `(1, 1)`, `(2, 2)`, `(4, 4)`.
  - Chi-square: `df = 2, 8, 14, 20`.
  - Gamma: `(alpha, beta) = (1, 0.50), (1, 2), (2, 4), (4, 2)`.
  - Log-normal: `(mu, sigma) = (0, 1), (0, 0.75), (0, 0.50), (0, 0.25)`.
  - Student-t: `df = 3, 4, 5, 6`.
- Becker also evaluates skewness, kurtosis, and several nonnormality tests (pp. 10-15; Table 2, p. 14).

### Transferable evaluation logic

- Distribution variation should not be cosmetic. It should target the identifying assumptions of the method.
- Moment diagnostics such as skewness and kurtosis are useful descriptive outputs.
- Nonnormality tests can be studied as practical diagnostics, not only as binary preconditions.

### Possible ICA adaptation

- Start with distributions meaningful for Haschka/Dost's ICA assumptions: the exogenous component of `P` must be non-normal and independent.
- Becker's distribution families and layout are useful for comparability, but should not be copied blindly if a distribution does not stress an ICA-relevant property.
- For ICA, distribution variation should distinguish skewed nonnormality, symmetric heavy-tailed nonnormality, and near-normal cases.

## 5. Endogeneity Strength Variation

### Becker-specific content

- Study 4 varies error correlation/endogeneity levels from `0.10` to `0.80` (Table 1, p. 12; Figure 6, p. 13).
- Becker reports that error correlation affects the power of the copula term, and Table 1 summarizes effects by endogeneity level (pp. 11-12; Table 1, p. 12).

### Transferable evaluation logic

- Endogeneity strength should be varied because untreated bias and correction difficulty differ across scenarios.
- Reporting both absolute bias and relative bias helps separate "large remaining bias" from "large original problem."

### Possible ICA adaptation

- ICA simulations should vary `rho`, the loading of the normal/error component into the endogenous regressor.
- The exact grid can be Becker-style for presentation, but should reflect Haschka/Dost's DGP. A plausible grid is `rho = 0.1, 0.2, ..., 0.8`, or a smaller quick-mode subset.

## 6. Figure 6 Structure and Visual Logic

### Becker-specific content

- Figure 6 is titled "Relative bias of the endogenous regressor for different distributions with varying distribution parameters, sample sizes, and endogeneity levels" (Figure 6 caption, p. 13).
- Panel structure:
  - Rows: distribution families.
  - Columns: endogeneity/error-correlation levels.
  - Within each panel: lines for distribution parameter settings.
- Axes:
  - X-axis: sample size on a log scale.
  - Y-axis: relative bias of the endogenous regressor.
- Colors / grouping:
  - Four colors represent four parameter settings within each distribution family.
  - Caption maps colors to parameter settings for each distribution family (p. 13).
- Sample sizes:
  - Figure 6 follows Study 4 sample-size logic; Table 1 lists `100` through `10000` (Table 1, p. 12).
- Distributions:
  - Beta, chi-square, gamma, log-normal, and Student-t (Figure 6 caption, p. 13).
- Performance metric:
  - Relative bias of the endogenous regressor.
- Interpretation:
  - Lower relative bias indicates less untreated endogeneity bias remains after correction.
  - The visual shows how performance depends jointly on sample size, endogeneity strength, distribution family, and distribution parameter.

### Transferable evaluation logic

- A grid of small panels is effective when performance depends on several simulation dimensions.
- A common y-axis within rows and log-scaled sample-size axis help show convergence/performance changes across sample sizes.
- Color is reserved for a single dimension: distribution parameters.

### Possible ICA adaptation

- Use Figure 6 as a layout template for ICA relative bias:
  - Rows: distribution families of the non-normal exogenous component.
  - Columns: endogeneity strength `rho`.
  - Lines/colors: distribution parameters.
  - X-axis: sample size, likely log scale.
  - Y-axis: `Relative_Bias_ICA = Bias_ICA / Bias_OLS`.
- Add or separately report ICA-specific diagnostics, such as failure rate and RMSE, because relative bias alone does not show instability.
- If some Becker distributions are not meaningful for ICA, replace or supplement them with Haschka/Dost-relevant distributions.

## 7. Figure 8 Flowchart Structure and Decision Logic

### Becker-specific content

- Figure 8 is a decision flowchart for whether to apply the Gaussian copula approach (Figure 8, p. 19).
- The top decision asks whether there is theoretical evidence for the Gaussian copula assumptions:
  - non-normal endogenous regressor distribution,
  - normal error term distribution,
  - Gaussian copula correlation structure.
- If not, the flowchart sends the researcher to other methods.
- The flowchart includes intercept-related checks:
  - whether an intercept is included,
  - whether no intercept is justified by fully standardized or mean-centered data,
  - whether there is a strong theoretical reason not to include an intercept,
  - whether the mean of endogenous regressors differs from zero.
- It includes a residual normality check for the model estimated without copula.
- It uses sample-size and absolute-skewness thresholds:
  - `n > 1000`,
  - absolute skewness around `0.8`,
  - absolute skewness around `2`,
  - `n > 200`,
  - `n > 2000`.
- Outcomes are qualitative:
  - high probability of valid Gaussian copula results,
  - low probability of valid Gaussian copula results, revert to other methods,
  - revert to other methods to correct for endogeneity.

### Required diagnostics in Becker

- Theoretical support for Gaussian copula assumptions.
- Whether the regression includes an intercept.
- Whether variables are standardized or mean-centered.
- Whether excluding the intercept has a strong theoretical reason.
- Whether endogenous-regressor means differ from zero.
- Residual normality of the model without copula.
- Sample size.
- Absolute skewness of the endogenous regressor.

### Thresholds or qualitative rules in Becker

- The paper states that Study 4 uses decision-tree analysis to derive thresholds for at least 80% copula power (p. 14).
- Text reports:
  - If skewness is larger than `0.774`, sample size should be larger than `1000`.
  - If skewness is equal to or smaller than `0.774`, more than `2000` observations are required.
  - For sample sizes between `400` and `1000`, skewness around `1.932` is required.
  - No considered distribution achieved sufficient power for sample sizes of `200` or smaller (p. 14).
- Figure 8 rounds these into practical flowchart thresholds such as absolute skewness `> 0.8`, absolute skewness `> 2`, `n > 1000`, `n > 2000`, and `n > 200`.

### Transferable evaluation logic

- A flowchart should not be purely theoretical. Becker derives practical decision rules from simulation evidence and observable diagnostics.
- The flowchart guides method use by first checking assumptions, then checking diagnostics and finite-sample conditions.
- Qualitative outcomes are easier to use than tables of coefficients.

### Possible ICA adaptation

- An ICA Figure 8-style flowchart should use ICA assumptions and diagnostics:
  - theoretical support for additive omitted-variable structure,
  - normal shared/omitted component assumption,
  - non-normal independent exogenous component in `P`,
  - sample size,
  - skewness/kurtosis or nonnormality diagnostics,
  - ICA convergence/failure rate from simulations,
  - possibly recovered-component normality as an application diagnostic.
- The final ICA flowchart should not rely on true bias, because true bias is unknown in real applications.
- Simulation-derived metrics such as relative bias, RMSE, failure rate, and recovered-component normality can justify thresholds behind the flowchart.

## 8. Translating Simulation Results Into Guidelines

### Becker-specific content

- Becker summarizes simulation findings in Table 3 as practical conclusions and warnings (Table 3, p. 17).
- The paper turns Study 4 results into threshold-based guidance using decision-tree analysis (p. 14).
- It explicitly warns that thresholds are approximate and constrained by the simulation design (p. 14).
- It distinguishes finite-sample limitations from deeper assumption failures (pp. 17-19).

### Transferable evaluation logic

- Guidelines should be evidence-backed and qualified.
- The thesis should state which thresholds come from simulations and which assumptions remain untestable.
- Tables and flowcharts can translate complex simulation results into defensible practical advice.

### Possible ICA adaptation

- Use a similar pipeline:
  1. Define ICA-relevant simulation scenarios.
  2. Compute bias, relative bias, RMSE, failure rate, and diagnostics.
  3. Identify empirical patterns by sample size, nonnormality, and endogeneity strength.
  4. Derive cautious decision rules for when ICA is likely reliable.
  5. State that thresholds are approximate and simulation-design dependent.

## 9. Useful Templates for the ICA Thesis

### Transferable

- Relative-bias framing: remaining corrected-method bias relative to untreated OLS bias.
- Multi-panel Figure 6 layout for comparing distributions, parameters, sample sizes, and endogeneity levels.
- Summary tables of main design-factor effects.
- Reporting diagnostics alongside performance metrics.
- Translating simulation evidence into a Figure 8-style flowchart.
- Explicitly warning that simulation-derived thresholds are approximate.

### Possible ICA-specific additions

- Failure rate per scenario.
- Number of valid ICA runs used for bias/RMSE.
- ICA convergence warnings.
- Normality score/statistic for recovered components.
- RMSE and standard-error instability.
- Separate quick/debug and final/thesis simulation modes.

## 10. Not Directly Transferable Because the Method Differs

### Becker-specific content not transferable as ICA rules

- Gaussian copula correlation structure is specific to the copula method.
- Copula term significance/power is not an ICA diagnostic.
- Maximum likelihood versus control-function copula comparison is not directly relevant to ICA.
- Intercept-specific copula failures should not be assumed to apply identically to ICA without evidence.
- Becker's nonnormality requirement refers to the endogenous regressor in the Gaussian copula setup; ICA specifically needs a non-normal independent exogenous component of `P`.
- Becker's exact Figure 8 thresholds are copula-specific and cannot be reused as ICA thresholds without ICA simulation evidence.

### Transfer caveat

Becker is a presentation and evaluation reference. The Haschka/Dost paper remains the theoretical source of truth for ICA, and the R implementation remains the reference implementation for software behavior.
