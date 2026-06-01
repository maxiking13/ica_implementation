# Paper Reading Plan

This plan identifies which parts of the available papers should be read for the thesis work. It is not a full paper summary and does not assess the mathematical correctness of the Python implementation.

## Sources inspected

- `papers/haschka_ICA.pdf`: Dost and Haschka ICA paper, 49 pages. This is the main theoretical source for the thesis method.
- `papers/Becker_example.pdf`: Becker et al. Gaussian copula paper, 21 pages. This is an evaluation and presentation reference, not the method source.

Text extraction was possible with `pypdf`. Some equations, tables, and figure captions extracted imperfectly, so exact notation should be checked visually in the PDFs during detailed reading.

## Reading priorities

1. Read the Haschka/Dost paper first for the method, assumptions, identification argument, estimation procedure, and simulation logic.
2. Read the Becker paper second for simulation-design structure, relative-bias presentation, nonnormality diagnostics, and flowchart-style decision guidance.
3. Do not start with the FastICA-versus-JADE issue. First understand the paper model, R reference implementation, and Python implementation broadly; then treat FastICA versus JADE as a focused audit.

## Haschka/Dost ICA Paper

### Highest-priority sections

- Abstract and Introduction, pp. 1-7:
  - Use for thesis motivation: omitted-variable endogeneity, limits of instruments, limits of Gaussian copula correction under additive omitted variable bias, and why ICA is proposed.
  - Extract only the problem framing and the paper's stated contribution; do not yet write a broad literature review.

- Section 2, `Endogeneity from omitted variables`, pp. 7-16:
  - Main theoretical source for the data-generating process and identification logic.
  - Needed for `docs/paper_notes.md` and especially `docs/model_equations.md`.

- Section 2.1, `Intuition for ICA-based omitted component extraction`, pp. 8-10:
  - Relevant for explaining ICA as blind source separation in thesis language.
  - Relevant for the defense/presentation intuition: observed variables as mixtures of a normal confounder and non-normal exogenous variation.

- Section 2.2, `Proof of identification`, pp. 10-16:
  - Core formal material for the thesis.
  - Extract equations, assumptions, cumulant argument, eigenvector recovery, point identification, and finite-sample remarks.
  - This section should drive `docs/model_equations.md`.

- Section 3, `Implementation with example code`, pp. 16-20:
  - Core implementation reading.
  - Must be compared later with the R reference implementation and Python code.
  - Pay special attention to the one-endogenous-regressor case, exogenous-regressor residualization, multiple endogenous regressors, normal-component selection, and final control-function regression.

- Section 4, `Monte Carlo simulations`, pp. 20-43:
  - Relevant for simulation design, metrics, robustness scenarios, and possible Figure 6/Figure 8 adaptation.
  - Read selectively at first. Prioritize subsections that correspond to the thesis implementation and planned simulations.

- Section 5, `Discussion`, pp. 43-45:
  - Relevant for limitations, boundary conditions, and what can be safely claimed in the thesis.
  - Use later when building a defensible Figure 8-style flowchart for ICA.

### Equations and formal items to extract

For `docs/model_equations.md`, extract and standardize notation from:

- Equations (1)-(2): structural model and decomposition of the endogenous regressor/error.
- Equations (3)-(5): simultaneous-equation representation and mixing matrix form.
- Assumptions 1-3: invertibility, non-zero higher cumulant, and diagonal cumulant tensor.
- Equations (6)-(11): cumulant objective and Hessian factorization.
- Equations (12)-(19): pseudoinverse/eigenvector recovery argument.
- Equation (20): slope identification by eigenvector normalization.
- Remark 3: role of third versus fourth cumulants.
- Remark 4: finite-sample considerations.
- Remark 5: exogenous-regressor residualization.

For `docs/paper_notes.md`, translate these formal pieces into readable thesis notes:

- The omitted-variable problem.
- Why the shared normal component creates endogeneity.
- Why a non-normal exogenous component in the endogenous regressor is needed.
- Why ICA can separate the components under the stated assumptions.
- Why the recovered normal component can be used as a control function.

### Implementation-relevant paper parts

- Section 3.1, pp. 16-17:
  - One endogenous regressor.
  - ICA input: observed `Y` and `P`.
  - Number of ICA components.
  - Selection of the most normal component.
  - Final regression with `Y`, `P`, and recovered normal component.

- Section 3.2, pp. 18-19:
  - One endogenous and one exogenous regressor.
  - Residualize `Y` and `P` with respect to `X` before ICA.
  - Final regression includes original `Y`, `P`, `X`, and recovered normal component.

- Section 3.3, pp. 19-20:
  - Multiple endogenous and exogenous regressors.
  - Residualization for each endogenous regressor and for the dependent variable.
  - ICA on residualized variables with `K + 1` components.

- Listings 1-2:
  - Useful for mapping the paper's implementation sketch to the R reference and Python code.
  - Check later whether the Python implementation follows the same data passed to ICA, component selection, and final regression logic.

### Simulation-relevant paper parts

- Section 4.1, benchmark simulations, pp. 20-22:
  - Relevant for baseline DGP with endogenous and exogenous regressors.
  - Table 1 reports mean estimates, empirical SD, RMSE, and bias t-ratio over 1,000 replications.

- Section 4.2, multiple endogenous regressors, pp. 23-24:
  - Relevant if the thesis wants to discuss extension beyond one endogenous regressor.
  - Lower priority for first implementation audit if the Python work focuses on one endogenous regressor.

- Section 4.3, true omitted variables setting, pp. 25-27:
  - Highly relevant. This directly targets omitted-variable bias and the central thesis use case.
  - Table 3 should be read for benchmark expectations and robustness logic.

- Section 4.4, comparison with other IV-free approaches, pp. 28-32:
  - Relevant for positioning against Gaussian copula and LIV.
  - Useful for thesis motivation, but lower priority than the core ICA model.

- Section 4.5, adverse effects of breakdown in identification, pp. 33-35:
  - Highly relevant for limitations and Figure 8-style decision rules.
  - Section 4.5.1 studies the exogenous component approaching normality.
  - Section 4.5.2 studies correlation between the non-normal component and the error.

- Section 4.6, robustness checks, pp. 36-38:
  - Relevant for robustness discussion.
  - Lower priority for first simulation replication unless the thesis explicitly tests dependence structures.

- Section 4.7, varying the distribution of the regressor's exogenous component, p. 39:
  - Highly relevant for distribution grid design.
  - Candidate source for choosing distributions and interpreting skewness/kurtosis.

- Sections 4.8-4.10, pp. 40-43:
  - Relevant for limitations and failure modes involving error distribution and additional normal noise.
  - Especially important for flowchart criteria and diagnostics.

### Tables, figures, listings, and appendix

- Listings 1 and 2: relevant for implementation mapping.
- Tables 1-3: high priority for baseline simulation metrics, multiple endogenous regressors, and omitted-variable setting.
- Tables 4-6: medium priority for comparison with copula, 2SCOPE, and LIV.
- Tables 7-14: high priority for limitations, robustness, and flowchart-style criteria.
- Appendix, pp. 48-49: appears non-substantive in the available PDF. Recheck visually before concluding that no appendix material is needed.

## Becker Paper

### Role in this thesis

Use Becker et al. as a reference for evaluation and presentation, not as a source for the ICA estimator. Relevant uses:

- Simulation design structure.
- Bias, relative bias, power, and nonnormality diagnostics.
- Figure 6-style relative-bias visualization.
- Figure 8-style decision flowchart.
- Boundary-condition language and how to derive decision thresholds from simulation evidence.

### Highest-priority sections

- Introduction, pp. 1-4:
  - Read only for context on why Gaussian copula methods require careful evaluation.
  - Do not use it as the main theoretical basis for ICA.

- Simulation study 1, pp. 4-7:
  - Relevant for evaluation criteria definitions.
  - The paper defines mean bias, relative bias, and statistical power in a simulation setting.
  - Important for clarifying whether the ICA thesis should use the same definitions or an explicitly adapted definition.

- Simulation study 4, pp. 10-15:
  - Highest-priority Becker section.
  - Relevant for sample sizes, endogeneity levels, distribution families, nonnormality tests, skewness/kurtosis, relative bias, and boundary-condition analysis.

- Summary of key findings and conclusions, pp. 17-19:
  - Relevant for how to present method limitations and practical guidelines.
  - Figure 8 appears here and should guide the structure, not the content, of an ICA-specific flowchart.

### Becker figures and tables relevant for this thesis

- Figure 6, p. 13:
  - Main visual reference for a Becker-style relative-bias figure.
  - Relevant dimensions: distribution families, distribution parameters, sample sizes, and endogeneity levels.
  - Distribution families shown: beta, chi-square, gamma, log-normal, and Student-t.
  - Use as a layout and presentation reference only; the ICA method may require adapted metrics and diagnostics.

- Figure 8, p. 19:
  - Main reference for a flowchart-style decision guideline.
  - Use as a structural reference for an ICA suitability flowchart, but derive ICA rules from the Haschka/Dost assumptions and simulation evidence.

- Table 1, p. 12:
  - Relevant for how Becker summarizes effects of sample size, explained variance, and endogeneity level on power, bias, and relative bias.
  - Useful template for aggregate simulation summaries.

- Table 2, p. 14:
  - Relevant for comparing nonnormality diagnostics.
  - Useful for deciding whether the ICA thesis should track skewness, kurtosis, Anderson-Darling, Cramer-von Mises, Shapiro-Wilk, or other diagnostics.

- Table 3, p. 17:
  - Relevant as a guideline-summary template.
  - Should not be copied as ICA guidance because it is specific to Gaussian copula.

### Becker parts likely needed for simulation design

- Evaluation criteria section, pp. 4-5:
  - Define or adapt mean bias, relative bias, and power/failure metrics.
  - Need to decide whether relative bias for ICA should be `Bias_ICA / Bias_OLS`, percentage remaining bias, absolute relative bias, or another explicitly stated variant.

- Study 4 design/results, pp. 10-15:
  - Use as the reference for sample size grids, distribution grids, endogeneity levels, and nonnormality diagnostics.
  - The web appendix is referenced for detailed design, so the local PDF may not contain all required replication details.

- Boundary-condition analysis, pp. 14-15:
  - Relevant for deriving data-supported thresholds for a Figure 8-style ICA flowchart.
  - The thesis should not invent thresholds without simulation evidence.

### Becker parts likely needed for Figure 6-style output

- Figure 6, p. 13:
  - Use the facet-grid idea and dimensions.
  - Adapt title/axis labels to ICA and the chosen relative-bias definition.
  - Track distribution parameters and endogeneity strengths carefully so plots can be traced back to simulation scenarios.

### Becker parts likely needed for Figure 8-style output

- Figure 8, p. 19:
  - Use as a visual/organizational reference for a decision guideline.
  - The actual ICA decision criteria should come from:
    - Haschka/Dost assumptions.
    - ICA simulation results.
    - diagnostics such as sample size, skewness, kurtosis, normality of recovered component, failure rate, RMSE, and relative bias.

## Working decisions for later simulation and audit design

### Relative bias definition

- Use the Becker-style definition as the primary relative-bias formula, adapted to the ICA setting.
- For each simulation scenario:

```text
Bias_OLS = mean(beta_hat_OLS - beta_true)
Bias_ICA = mean(beta_hat_ICA - beta_true)
Relative_Bias_ICA = Bias_ICA / Bias_OLS
```

- If Becker's exact definition differs in detail, document the difference and explain why the ICA-specific version is used.
- If `Bias_OLS` is zero or numerically close to zero, the relative-bias calculation must be handled explicitly and documented before interpretation.

### Simulation grid

- Start with a simulation grid that is relevant for the Haschka/Dost ICA setting.
- The Haschka/Dost method is the main method of the thesis, so its assumptions and distributional requirements come first.
- Use Becker-style distribution families and layout logic for comparability and presentation, but do not blindly copy Becker's grid if some distributions are not meaningful for ICA.

### Sample sizes and runtime modes

- There is no final answer yet for the final sample-size grid and iteration count.
- Decide the final grid after quick-mode runtime checks.
- Quick/debug mode:
  - small grid,
  - few iterations,
  - used only to verify that the simulation code works, outputs the required metrics, and plotting works,
  - results must not be interpreted as thesis evidence.
- Final/thesis mode:
  - larger grid,
  - higher iteration count,
  - used only after runtime has been measured and the simulation design is stable,
  - runtime of several hours is acceptable.
- As a provisional starting point, use a Becker-style sample-size grid such as:

```text
N = [100, 200, 400, 1000, 4000, 10000]
```

- For quick mode, use for example `n_iterations = 5` to `20`.
- For intermediate checks, use for example `n_iterations = 50` to `100`.
- For final thesis runs, propose a feasible count after runtime measurement, likely in the range `n_iterations = 500` to `1000` if runtime allows.

### Failed or unstable ICA runs

- Do not silently exclude failed or unstable ICA runs.
- Record failed or unstable runs explicitly.
- Use `NaN` for failed estimates where needed, but also report a failure rate per scenario.
- For bias and RMSE calculations, use valid estimates only and document how many runs were excluded or failed.

### Normality diagnostic for ICA component selection

- For now, mirror the R reference implementation as closely as possible.
- Identify the most normal ICA component using a Kolmogorov-Smirnov based normality diagnostic.
- If the Python implementation differs in standardization or parameter handling, document that as an audit point.
- Do not change the diagnostic without approval.

### Figure 8 flowchart diagnostics

- The final Figure 8-style flowchart should primarily use diagnostics that a researcher can observe or compute before or during application, such as sample size, skewness, kurtosis, and non-normality diagnostics.
- Simulation-derived diagnostics such as failure rate, relative bias, RMSE, and recovered-component normality may be used to justify the decision thresholds behind the flowchart.
- The final flowchart should not depend on knowing the true bias in real data.

### Becker web appendices

- The Becker appendices are not currently available in the repository.
- They are not required for the first broad audit.
- For closer replication of Becker-style figures or decision-tree logic, they may be useful later.
- For now, continue with the available Becker paper and document that appendices are missing; this is not important for the first audit.

### Haschka/Dost appendix or updated version

- The currently available Haschka/Dost paper and R reference implementation are sufficient for the first audit.
- No fuller appendix, supplementary material, or updated paper version is currently needed for the first audit.

### FastICA versus JADE

- Record FastICA versus JADE as a critical later audit point.
- Do not resolve it yet.
- First complete the broad paper, R, and Python understanding.
- Then perform the dedicated FastICA-versus-JADE audit as planned.


## Next documentation steps

1. Fill `docs/paper_notes.md` with the paper-understanding notes from the Haschka/Dost paper.
2. Fill `docs/model_equations.md` with the formal model extraction and notation.
3. Then analyze `reference_implementation/R/ICAReg.R` into a dedicated R-reference document.
4. Then map the Python implementation against paper and R behavior.
5. Only after those steps, use `docs/audit_report.md` for the Paper-R-Python comparison audit.
