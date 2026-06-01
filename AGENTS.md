# AGENTS.md

## Project context

This repository contains the Python implementation for a bachelor thesis on ICA-based endogeneity correction.

The thesis implements and evaluates the method described in the paper:

* Dost, F. and Haschka, R. E. (2025): *ICA at the Cocktail Party: Casting Instrument-free Omitted Variable Bias Correction as a Blind Source Separation Problem.*

The existing R implementation is used as the main reference implementation. The Python code is not intended to be a line-by-line translation of the R code, but it must be mathematically and methodologically equivalent where appropriate.

The Becker et al. Gaussian copula paper is used as an evaluation and presentation reference, especially for simulation design, relative bias figures, and a flowchart-style decision guideline.

This is a scientific bachelor thesis project, not a generic code cleanup task. Accuracy, traceability, and explainability are more important than quick changes.

## Repository structure

Expected repository structure:

```text
repo/
├── AGENTS.md
├── README.md
├── papers/
│   ├── haschka_ICA.pdf
│   └── Becker_example.pdf
├── src/
│   ├── data_generator.py
│   ├── icaEstimator.py
│   ├── main.py
│   ├── plot_fig.py
│   └── simulation.py
├── reference_implementation/
│   └── R/
│       ├── ICAReg.R
│       └── README.md
└── docs/
    ├── codex_prompts.md
    ├── paper_notes.md
    ├── model_equations.md
    ├── r_reference_analysis.md
    ├── code_mapping.md
    ├── audit_report.md
    ├── simulation_design.md
    ├── figure6_plan.md
    ├── figure8_flowchart_plan.md
    └── open_questions.md
```

If the actual paths differ, inspect the repository first and adapt references accordingly. Do not assume missing files exist.

## Main objective

The main objective is to help audit, improve, and document the Python implementation of the ICA-based method.

The work should support a bachelor thesis of approximately 20–30 pages. Therefore, the code and results must be understandable, scientifically justified, and suitable for explanation in a thesis defense or presentation.

The core tasks are:

1. Understand the Haschka/Dost paper.
2. Extract the mathematical model, assumptions, equations, and estimation procedure.
3. Analyze the R reference implementation.
4. Analyze the Python implementation.
5. Compare paper, R implementation, and Python implementation.
6. Identify deviations, ambiguities, possible mistakes, and implementation risks.
7. Support simulation design and result generation.
8. Support creation of Becker-style Figure 6 and Figure 8 outputs.
9. Document all important methodological and implementation decisions.

## Source hierarchy

Use this hierarchy when checking correctness:

1. The Haschka/Dost paper is the theoretical source of truth.
2. The R implementation is the primary reference implementation.
3. The Python implementation is the thesis implementation and may be modular or idiomatic Python, but must remain methodologically justified.
4. The Becker paper is an evaluation and presentation reference, not the method being implemented.

If the paper and the R implementation appear to differ, do not guess. Document the discrepancy and ask for clarification.

If the R implementation and Python implementation differ, classify the difference as one of:

* intentional Python design choice
* harmless implementation detail
* library-related difference
* potential translation error
* mathematical or methodological issue
* unclear and requires clarification

## Strict default rule: analyze before changing

Do not modify source code by default.

Default workflow:

1. Analyze.
2. Document findings.
3. Propose changes.
4. Explain the reason for each proposed change.
5. Wait for explicit user approval.
6. Only then implement the approved change.

If the user explicitly asks for implementation, implement only the approved change. Keep the change small, reviewable, and easy to understand.

After any implementation, summarize:

* what changed,
* why it changed,
* which files were affected,
* whether the mathematical logic changed,
* how to verify the change.

## Clarification rule

If anything is unclear, ask clarifying questions before proceeding.

This is especially important for:

* mathematical assumptions,
* interpretation of the papers,
* differences between paper, R code, and Python code,
* simulation design,
* bias and RMSE definitions,
* Figure 6 replication,
* Figure 8 flowchart criteria,
* FastICA versus JADE,
* choice of distributions,
* sample sizes and runtime decisions.

It is better to ask multiple questions than to proceed with a wrong assumption.

## Preserve the modular Python structure

The Python implementation intentionally uses a modular class-based structure instead of one long script.

Preserve this structure unless there is a clearly justified reason to change it.

Do not collapse the implementation into one monolithic script.

The current conceptual roles are:

* `DataGenerator`: data-generating process and simulated data creation.
* `ICAEstimator`: ICA-based endogeneity correction estimator.
* `SimulationEngine`: repeated simulation runs across scenarios.
* `main.py`: orchestration and example execution.
* `plot_fig.py`: figure generation.

If proposing structural changes, explain why they improve clarity, correctness, reproducibility, or thesis presentation.

## Libraries and dependencies

Use the currently used Python ecosystem as the default:

* numpy
* pandas
* scipy
* statsmodels
* scikit-learn / FastICA
* matplotlib
* seaborn
* tqdm

Do not introduce new dependencies unless there is a clear technical or scientific reason.

If a new library is recommended, explain:

1. why it is needed,
2. what problem it solves,
3. why the existing libraries are insufficient,
4. whether it affects reproducibility,
5. whether it affects comparability to the R implementation,
6. whether the student can easily explain it in the thesis.

## Critical audit point: FastICA versus JADE

The R reference implementation uses ICA with method `"jade"`.

The current Python implementation uses `sklearn.decomposition.FastICA`.

This difference is a critical methodological audit point.

Investigate and document:

1. whether FastICA and JADE are methodologically comparable for this thesis use case,
2. whether FastICA is an acceptable substitute for JADE,
3. whether using FastICA affects simulation results,
4. whether the thesis must document this difference,
5. whether a Python JADE implementation should be considered,
6. what trade-offs exist in terms of correctness, reproducibility, availability, and explainability.

Do not replace FastICA with another method without explicit approval.

## Mathematical and methodological expectations

When analyzing the method, focus on:

* the assumed data-generating process,
* omitted variable bias,
* decomposition of the endogenous regressor,
* role of the normal confounder,
* role of the non-normal exogenous component,
* ICA as blind source separation,
* identification assumptions,
* selection of the most normal ICA component,
* control function logic,
* residualization alternative when `CF = FALSE`,
* handling of exogenous regressors,
* intercept handling,
* bootstrap standard errors,
* identification checks,
* non-normality requirements,
* finite-sample limitations.

Do not simplify or reinterpret mathematical assumptions without explicitly marking the simplification.

## R reference implementation analysis

Analyze the R implementation carefully.

Important aspects include:

* formula syntax: `depvar ~ endog_vars | exog_vars`,
* support for removing the intercept using `-1`,
* handling of endogenous and exogenous variables,
* input validation,
* rank checks,
* ICA execution,
* selection of the most normal component,
* `CF = TRUE` control function approach,
* `CF = FALSE` residualization approach,
* bootstrap standard errors,
* identification warnings,
* example applications.

When comparing to Python, check whether each of these aspects is implemented, missing, simplified, or intentionally different.

## Python implementation audit

When auditing the Python implementation, inspect:

* formula parsing,
* input validation,
* missing value handling,
* intercept handling,
* rank checks,
* data residualization when exogenous regressors are present,
* ICA input matrix,
* number of components,
* selection of the normal component,
* treatment of the control function,
* final OLS regression,
* bootstrap sampling,
* bootstrap standard errors,
* p-value calculation,
* warnings and identification checks,
* reproducibility through random seeds,
* compatibility with the intended simulation design.

For every issue, provide:

* severity: low / medium / high,
* paper reference,
* R reference,
* Python code reference,
* explanation,
* suggested fix,
* whether it changes mathematical behavior,
* whether it affects thesis results,
* whether clarification is needed.

## Simulation goals

The simulations should evaluate the ICA-based method systematically.

The main simulation outputs should include:

* OLS estimates,
* ICA estimates,
* bias,
* relative bias,
* RMSE,
* sample size,
* distribution family,
* distribution parameters,
* skewness,
* kurtosis,
* endogeneity strength,
* failure rate or number of invalid ICA runs if applicable.

Clarify and document all definitions before using them.

In particular, check:

* whether bias is computed using mean or median,
* whether OLS and ICA are aggregated consistently,
* how failed ICA runs are handled,
* how NaN values are handled,
* how relative bias is defined,
* whether the definition matches or intentionally differs from the Becker-style reference.

## Figure 6 goal

Create a Becker-style Figure 6 equivalent for the ICA method.

The figure should be as close as reasonably possible to the Becker-style structure at first.

It should show relative bias across:

* sample sizes,
* distribution families,
* distribution parameters,
* endogeneity strengths.

Later, the figure may be expanded or adapted for the bachelor thesis, for example by adding more distributions or removing distributions that are not meaningful for the ICA setting.

Do not invent final figure design choices without documenting the reason.

## Figure 8 flowchart goal

The Figure 8-style flowchart should be a central thesis output.

It should not be purely theoretical or invented without evidence. It should be derived from simulation results and methodological reasoning.

The flowchart should help answer:

* when the ICA method is suitable,
* for which distributions it performs well,
* from which sample sizes it becomes reliable,
* how skewness and kurtosis relate to method performance,
* whether endogeneity strength affects reliability,
* whether failure rate or unstable ICA behavior matters,
* whether additional diagnostics are needed.

Potential decision criteria include:

* sample size,
* skewness,
* kurtosis,
* relative bias,
* RMSE,
* distribution family,
* distribution parameters,
* endogeneity strength,
* ICA failure rate,
* normality of recovered component.

The exact decision rules are not fixed yet. They must be proposed, justified, and, where possible, supported by simulation evidence.

## Runtime strategy

Simulation runtime may be long for final results.

Use two modes conceptually:

1. Quick development mode:

   * small number of iterations,
   * fewer sample sizes,
   * fewer distributions,
   * used only for debugging and checking code.

2. Final thesis mode:

   * larger number of iterations,
   * full distribution grid,
   * thesis-relevant sample sizes,
   * may run for several hours.

Clearly distinguish quick checks from final simulation runs.

Do not treat quick-check results as final thesis evidence.

## Output organization

Prefer organized output directories instead of writing result files directly into the repository root.

Recommended structure:

```text
outputs/
├── data/
│   └── simulation_results.csv
├── figures/
│   ├── figure6_relative_bias.pdf
│   └── figure8_flowchart.pdf
└── logs/
```

If changing output paths, propose the change first and explain why it improves reproducibility and thesis organization.

## Documentation expectations

The project must support a bachelor thesis. Therefore, document not only what the code does, but why it does it.

Important documentation topics:

* explanation of the ICA method,
* relation to omitted variable bias,
* relation to the R implementation,
* relation to the Haschka/Dost paper,
* explanation of the modular Python design,
* simulation design,
* distribution choices,
* metrics,
* figure generation,
* limitations,
* open questions,
* assumptions,
* deviations from the R implementation.

Documentation should be precise enough that the thesis author can explain and defend the work in a presentation.

## Tests

Unit tests are not the first priority.

Focus first on:

* paper-code-R comparison,
* correctness of the implementation,
* simulation design,
* documentation,
* Figure 6 and Figure 8 planning.

Tests may be proposed later if they directly increase confidence in critical mathematical components.

Do not create a large test suite unless explicitly asked.

## Communication style

Be precise, conservative, and explicit.

Avoid vague claims such as:

* “this is probably fine”
* “the methods are basically the same”
* “the result looks good”
* “this should work”

Instead, explain what is known, what is uncertain, and what needs verification.

Whenever confidence is limited, say so.

Every important recommendation should include a reason.

## Final principle

This project will be supervised by one of the authors of the main paper. Treat all mathematical, methodological, and implementation details with high care.

The goal is not only to produce working code, but to produce code and documentation that are scientifically defensible.
