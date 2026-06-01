# Codex Prompts for ICA Bachelor Thesis Audit

## Purpose of this file

This file contains step-by-step prompts for Codex.

Use these prompts one at a time. Do not run the whole file at once.

The goal is to guide Codex through a controlled scientific audit of the Python implementation for the ICA-based endogeneity correction bachelor thesis.

The workflow is:

1. Inspect repository.
2. Understand paper.
3. Extract mathematical model.
4. Analyze R reference implementation.
5. Analyze Python implementation.
6. Compare paper, R implementation, and Python implementation.
7. Investigate FastICA vs JADE.
8. Audit simulation design.
9. Plan Becker-style Figure 6.
10. Plan Figure 8-style flowchart.
11. Only after approval: implement small, justified changes.

---

# Prompt 0: Initial repository inspection

```text
Read `AGENTS.md` first.

Then inspect the repository structure.

Do not modify any files.

Create or update `docs/repository_overview.md`.

The overview should include:

1. All relevant folders and files you found.
2. Which files appear to be part of the Python implementation.
3. Which files appear to be papers or reference material.
4. Which files appear to be the R reference implementation.
5. Which files are missing or unexpected based on `AGENTS.md`.
6. Any immediate setup issues you notice.
7. Open questions before starting the scientific audit.

Important:
Do not analyze the mathematical correctness yet.
Do not modify source code.
Do not make assumptions if file paths differ. Document the actual paths you find.
```

---

# Prompt 1: Paper reading plan

```text
Read `AGENTS.md` and inspect the papers in the `papers/` folder.

Do not modify source code.

Create or update `docs/paper_reading_plan.md`.

The goal is to identify which parts of the papers are relevant for the thesis.

Focus on:

1. The Haschka/Dost ICA paper as the main theoretical source.
2. The Becker paper as an evaluation and presentation reference.
3. Which sections, equations, figures, tables, and appendices are relevant.
4. Which parts are likely needed for implementation.
5. Which parts are likely needed for simulation design.
6. Which parts are likely needed for Figure 6-style and Figure 8-style outputs.
7. Open questions or ambiguous parts.

Important:
Do not summarize the full papers yet.
Do not modify source code.
```

---

# Prompt 2: Main paper summary

```text
Read the Haschka/Dost ICA paper carefully.

Do not modify source code.

Create or update `docs/paper_notes.md`.

Focus on the ICA-based endogeneity correction method.

Use this structure:

1. Research problem
2. Why omitted variable bias is relevant
3. Why instrumental variables are difficult
4. Why Gaussian copula is not sufficient for the target case
5. Data-generating process
6. Key variables and notation
7. Mathematical assumptions
8. ICA intuition
9. Identification logic
10. Estimation procedure
11. One-endogenous-regressor case
12. Case with exogenous regressors
13. Control function approach
14. Residualization approach
15. Bootstrap / uncertainty handling
16. Diagnostics and warnings
17. Limitations
18. Parts relevant for Python implementation
19. Parts relevant for simulation design
20. Open questions

For every important statement, include paper references such as page, section, equation, table, figure, or listing if available.

Separate clearly:

- what the paper explicitly states,
- what you infer,
- what remains unclear.
```

---

# Prompt 3: Mathematical model extraction

```text
Using the Haschka/Dost ICA paper and `docs/paper_notes.md`, create or update `docs/model_equations.md`.

Do not modify source code.

Extract the mathematical and algorithmic reference model for the Python implementation.

Use this structure:

1. Structural equation for Y
2. Equation for the endogenous regressor P
3. Decomposition of the error term / omitted variable component
4. Distributional assumptions
5. Independence assumptions
6. Non-normality requirement
7. ICA source separation formulation
8. Identification assumptions
9. Control function estimation procedure
10. Residualization procedure when CF = FALSE
11. Handling of exogenous regressors
12. Intercept handling
13. Bootstrap standard errors
14. Diagnostics / identification checks
15. Finite-sample considerations
16. What a correct implementation must do
17. Possible implementation pitfalls

For every equation or model component, include:

- paper reference,
- notation,
- plain-language explanation,
- implementation implication,
- possible edge cases.

Do not invent missing assumptions. If something is ambiguous, mark it as ambiguous and list it in `docs/open_questions.md`.
```

---

# Prompt 4: Becker paper evaluation reference

```text
Read the Becker paper as an evaluation and presentation reference.

Do not modify source code.

Create or update `docs/becker_reference_notes.md`.

The goal is not to implement the Gaussian copula method.

The goal is to understand how the Becker paper structures simulation evidence and result presentation.

Focus especially on:

1. Simulation design logic
2. Relative bias definition
3. Sample size variation
4. Distribution variation
5. Endogeneity strength variation
6. Figure 6 structure and visual logic
7. Figure 8 flowchart structure and decision logic
8. How simulation results are translated into guidelines
9. Which parts are useful as a template for the ICA thesis
10. Which parts are not directly transferable because the method differs

For Figure 6, document:

- panel structure,
- axes,
- colors / grouping variables,
- sample sizes,
- distributions,
- performance metric,
- interpretation.

For Figure 8, document:

- decision nodes,
- required diagnostics,
- thresholds or qualitative rules,
- how the figure guides method use.

Clearly separate:

- Becker-specific content,
- transferable evaluation logic,
- possible adaptations for the ICA method.
```

---

# Prompt 5: R reference implementation analysis

```text
Read the R reference implementation in `reference_implementation/R/`.

Do not modify any files.

Create or update `docs/r_reference_analysis.md`.

Analyze the R implementation as the primary reference implementation for the ICA method.

Focus on:

1. Function interface
2. Formula syntax
3. Handling of endogenous variables
4. Handling of exogenous variables
5. Intercept handling
6. Input validation
7. Missing value handling
8. Rank checks
9. ICA call
10. JADE usage
11. Selection of the most normal ICA component
12. CF = TRUE control function logic
13. CF = FALSE residualization logic
14. Bootstrap logic
15. Identification warnings
16. Return values
17. Example applications
18. Potential bugs or ambiguities in the R code
19. Which behavior Python should replicate
20. Which behavior may be R-specific and not directly transferable

For every important behavior, document:

- R file reference,
- function name,
- code location if possible,
- explanation,
- relevance for Python implementation.

Important:
Treat the R code as a reference implementation, but not as automatically infallible.
If the R code and paper appear to differ, document the discrepancy.
```

---

# Prompt 6: Python implementation overview

```text
Read the Python implementation in `src/`.

Do not modify any files.

Create or update `docs/python_implementation_overview.md`.

Describe the current Python implementation.

Use this structure:

1. Overall architecture
2. Role of `DataGenerator`
3. Role of `ICAEstimator`
4. Role of `SimulationEngine`
5. Role of `main.py`
6. Role of `plot_fig.py`
7. Data flow through the project
8. How a single estimation works
9. How simulations are currently run
10. How figures are currently generated
11. Current libraries and dependencies
12. Current output files
13. Current strengths of the implementation
14. Current risks or unclear parts
15. Open questions

Important:
Do not judge mathematical correctness yet.
Do not modify code.
Preserve the modular class-based structure as an intentional design choice.
```

---

# Prompt 7: Paper-R-Python comparison audit

```text
Using the following documents:

- `docs/paper_notes.md`
- `docs/model_equations.md`
- `docs/r_reference_analysis.md`
- `docs/python_implementation_overview.md`

compare the Haschka/Dost paper, the R reference implementation, and the Python implementation.

Do not modify source code.

Create or update `docs/code_mapping.md` and `docs/audit_report.md`.

For `docs/code_mapping.md`, create a mapping table with:

1. Paper concept / equation / algorithm step
2. Paper reference
3. R implementation reference
4. Python implementation reference
5. Status
6. Notes

For `docs/audit_report.md`, classify each important part as:

- correct
- likely correct but needs verification
- incomplete
- inconsistent with the paper
- inconsistent with the R implementation
- missing
- unclear because the paper is ambiguous
- unclear because the R implementation is ambiguous
- unclear because the Python implementation is ambiguous

For every issue, include:

1. Severity: low / medium / high
2. Paper reference
3. R reference
4. Python reference
5. Explanation
6. Suggested fix or clarification
7. Whether it changes mathematical behavior
8. Whether it could affect thesis results
9. Whether user approval is required before implementation

Important:
Do not implement fixes.
Do not silently assume that Python is wrong just because it differs from R.
Classify differences carefully.
```

---

# Prompt 8: FastICA versus JADE audit

```text
Investigate the methodological difference between the R implementation's JADE ICA and the Python implementation's FastICA.

Do not modify source code.

Create or update `docs/fastica_vs_jade.md`.

Analyze:

1. What JADE does conceptually.
2. What FastICA does conceptually.
3. How each method identifies independent components.
4. Whether both are suitable for the ICA-based endogeneity correction setting.
5. Whether the Haschka/Dost paper or R implementation requires JADE specifically.
6. Whether FastICA is a defensible substitute.
7. What empirical differences may occur in simulation results.
8. Whether a Python JADE implementation should be considered.
9. Which Python libraries could provide JADE, if needed.
10. Trade-offs: correctness, reproducibility, explainability, installation complexity, and thesis defense.
11. Recommended next step.

Important:
Do not replace FastICA.
Do not add dependencies.
Do not make a final decision without clearly explaining the uncertainty.
If the issue requires supervisor input, say so.
```

---

# Prompt 9: Simulation design audit

```text
Analyze the current simulation design.

Use the Python files in `src/`, the Becker reference notes, and the Haschka/Dost paper notes.

Do not modify source code.

Create or update `docs/simulation_design.md`.

Focus on:

1. What the simulation currently tests.
2. Current data-generating process.
3. How the DGP relates to the Haschka/Dost paper.
4. Current sample sizes.
5. Current distributions.
6. Current distribution parameters.
7. Current endogeneity strength values.
8. Current number of iterations.
9. Current random seed strategy.
10. Current OLS estimator.
11. Current ICA estimator.
12. Current bias definition.
13. Current relative bias definition if present.
14. Current RMSE definition.
15. Handling of failed ICA runs.
16. Whether bootstrapping is skipped in simulation and why.
17. Whether the simulation output supports Figure 6.
18. Whether the simulation output supports Figure 8.
19. Missing metrics needed for the thesis.
20. Recommended improvements.

Important:
Distinguish between quick development simulation settings and final thesis simulation settings.
Do not modify code.
```

---

# Prompt 10: Figure 6 plan

```text
Using the Becker reference notes and the current Python simulation design, create or update `docs/figure6_plan.md`.

Do not modify source code.

The goal is to plan a Becker-style Figure 6 equivalent for the ICA method.

Include:

1. Purpose of the figure
2. Exact metric to plot
3. Definition of relative bias
4. Sample sizes to include
5. Distribution families to include
6. Distribution parameters to include
7. Endogeneity strengths to include
8. Whether skewness and kurtosis should appear in the figure or only in the data
9. Required simulation output columns
10. Recommended plot layout
11. Recommended axis scaling
12. Recommended labels
13. Recommended file names
14. How closely it should match the Becker visual style
15. What should differ because this is the ICA method
16. Potential interpretation of the final figure
17. Open design decisions

Important:
The first version should be as close as reasonably possible to Becker-style Figure 6.
Later thesis versions may be expanded with more distributions or adapted after results are available.
Do not invent final conclusions before running simulations.
```

---

# Prompt 11: Figure 8 flowchart plan

```text
Using the Haschka/Dost paper, Becker reference notes, and the planned simulation output, create or update `docs/figure8_flowchart_plan.md`.

Do not modify source code.

The goal is to design a Figure 8-style flowchart for deciding when the ICA method is suitable.

The flowchart must be derived from simulation results and methodological reasoning.

Include:

1. Purpose of the flowchart
2. Target user of the flowchart
3. What decision the flowchart should support
4. Candidate input diagnostics
5. Candidate decision criteria
6. Candidate thresholds
7. How each threshold could be justified empirically
8. Role of sample size
9. Role of skewness
10. Role of kurtosis
11. Role of distribution family
12. Role of endogeneity strength
13. Role of relative bias
14. Role of RMSE
15. Role of ICA failure rate
16. Role of recovered-component normality
17. Which criteria require simulation evidence
18. Which criteria come from theory
19. Proposed first draft of the decision logic
20. Open questions before finalizing the flowchart

Important:
Do not create unsupported final rules.
Mark any provisional thresholds as provisional.
The final flowchart should be defensible in a bachelor thesis and presentation.
```

---

# Prompt 12: Documentation plan for bachelor thesis

```text
Create or update `docs/thesis_documentation_plan.md`.

Do not modify source code.

The goal is to outline how the implementation, simulation, and results can be documented in a 20–30 page bachelor thesis.

Suggest a thesis-oriented structure with sections such as:

1. Introduction
2. Endogeneity and omitted variable bias
3. ICA-based correction method
4. Mathematical model and assumptions
5. R reference implementation
6. Python implementation design
7. Simulation design
8. Results: Figure 6-style relative bias analysis
9. Results: Figure 8-style decision flowchart
10. Discussion
11. Limitations
12. Conclusion

For each section, include:

- purpose,
- key points to cover,
- required figures or tables,
- required code references,
- required paper references,
- possible pitfalls.

Important:
This is not the final thesis text.
It is a documentation plan to guide implementation and writing.
```

---

# Prompt 13: Open questions consolidation

```text
Review all documents in `docs/`.

Create or update `docs/open_questions.md`.

Collect all unresolved questions.

Group them by:

1. Paper interpretation
2. R reference implementation
3. Python implementation
4. FastICA versus JADE
5. Simulation design
6. Figure 6
7. Figure 8
8. Runtime and reproducibility
9. Thesis writing
10. Supervisor clarification

For each question, include:

- question,
- why it matters,
- possible options,
- recommended next step,
- whether supervisor input is needed.

Do not modify source code.
```

---

# Prompt 14: Approved implementation template

Use this prompt only after a specific change has been approved.

```text
Read `AGENTS.md` first.

Implement only the following approved change:

[DESCRIBE THE APPROVED CHANGE HERE]

Before editing, summarize your implementation plan.

Then make the smallest necessary code change.

Preserve the modular class-based structure.

Do not change mathematical behavior beyond the approved scope.

After editing, provide:

1. Changed files
2. Summary of the change
3. Why the change was needed
4. Whether mathematical behavior changed
5. How to verify the change
6. Whether simulation results need to be regenerated
7. Any remaining risks or open questions
```

---

# Prompt 15: Post-change review

Use this after Codex implemented an approved change.

```text
Review the last code changes.

Do not make further changes.

Create a concise review with:

1. What changed
2. Whether the change matches the approved scope
3. Whether any unrelated code was changed
4. Whether the modular structure was preserved
5. Whether mathematical behavior changed
6. Whether documentation must be updated
7. Whether simulations must be rerun
8. Whether the change should be committed

If you find a problem, propose a fix but do not implement it.
```

---

# Recommended working rhythm

Use this rhythm throughout the project:

1. Run one prompt.
2. Read the generated Markdown.
3. Ask clarifying questions if needed.
4. Manually inspect important claims.
5. Commit useful documentation changes.
6. Only then continue with the next prompt.

Recommended commits:

```bash
git add docs/
git commit -m "Add Codex paper analysis"
```

```bash
git add docs/
git commit -m "Add R and Python implementation audit"
```

```bash
git add docs/
git commit -m "Add simulation and figure planning"
```

```bash
git add src/ docs/
git commit -m "Implement approved ICA correction change"
```

Never commit large unexplained code changes.
