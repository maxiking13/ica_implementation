# FastICA Versus JADE Audit

Source basis:

- Haschka/Dost ICA paper notes: `docs/paper_notes.md`
- Model extraction: `docs/model_equations.md`
- R reference analysis: `docs/r_reference_analysis.md`
- Python overview: `docs/python_implementation_overview.md`
- R reference implementation: `reference_implementation/R/ICAReg.R`
- Current Python implementation: `src/icaEstimator.py`
- External references listed at the end of this document.

Scope: This document investigates the methodological difference between the R reference implementation's JADE ICA and the Python implementation's FastICA. It does not replace FastICA, add dependencies, or make a final implementation decision.

## 1. What JADE Does Conceptually

JADE stands for Joint Approximate Diagonalization of Eigenmatrices. Conceptually, it is an ICA method that:

1. centers and whitens the observed data,
2. constructs fourth-order cumulant information from the whitened data,
3. searches for an orthogonal rotation that approximately diagonalizes a set of cumulant matrices,
4. treats the rotated components as the estimated independent sources.

The R `ica` package documentation describes `icajade()` as Cardoso and Souloumiac's JADE approach and says it finds the orthogonal rotation matrix that approximately diagonalizes the cumulant array of the source signals. This is directly related to the Haschka/Dost paper's emphasis on higher-order cumulants.

Important conceptual point: JADE uses fourth-order cumulant structure directly. That makes it especially natural for a method whose identification argument uses differences in third/fourth cumulants between a normal and a non-normal source.

## 2. What FastICA Does Conceptually

FastICA is also an ICA method, but it solves the source-separation problem through a different numerical criterion.

Conceptually, FastICA:

1. centers and whitens the observed data,
2. searches for directions/components that are maximally non-Gaussian,
3. uses a fixed-point iteration algorithm,
4. approximates non-Gaussianity through a contrast function such as `logcosh`, `exp`, or `cube`.

The scikit-learn documentation describes FastICA as performing independent component analysis, with parameters for whitening, algorithm mode, maximum iterations, tolerance, and a function `G` used in the approximation to negentropy. The scikit-learn user guide states that ICA separates a multivariate signal into additive subcomponents that are maximally independent and that scikit-learn implements ICA using FastICA.

Important conceptual point: FastICA is still an ICA method and still relies on non-Gaussianity, but it does not identify components through the same explicit joint diagonalization of cumulant matrices as JADE.

## 3. How Each Method Identifies Independent Components

### JADE

JADE identifies components by exploiting fourth-order cumulants. After whitening, the remaining task is to find an orthogonal rotation. JADE chooses the rotation that makes the cumulant matrices as diagonal as possible. If the sources are independent, higher-order cross-cumulants should vanish, so diagonalization is a way to recover independent sources.

In this thesis context, that is attractive because:

- the Haschka/Dost proof relies on higher-order cumulants,
- normal sources have zero third and fourth cumulants,
- the non-normal source should have a nonzero third or fourth cumulant,
- the paper explicitly mentions JADE and uses `method = "jade"` in examples.

### FastICA

FastICA identifies components by optimizing a non-Gaussianity contrast. After whitening, it searches for directions whose projected data are as non-Gaussian as possible, using fixed-point iteration. The choice of contrast function matters. In scikit-learn, the default is `logcosh`.

In this thesis context, FastICA is related but less directly aligned:

- it still aims to separate independent non-Gaussian components,
- it can recover the same kind of latent sources in favorable settings,
- but it is not the same cumulant-diagonalization procedure used in the R reference implementation.

## 4. Suitability for ICA-Based Endogeneity Correction

Both methods are potentially suitable in the broad ICA sense: they try to recover latent independent sources from observed linear mixtures. The core Haschka/Dost estimator needs source separation, not a conventional supervised prediction model.

However, suitability is not identical:

- **JADE is closer to the paper's theoretical language.** The paper's identification argument is formulated through cumulants, and JADE is a cumulant-based joint diagonalization method.
- **FastICA is a defensible ICA baseline, but not automatically equivalent.** It is widely used, available in scikit-learn, reproducible with a fixed random seed, and simple to explain as a non-Gaussian source-separation method.
- **The estimator's final step selects the most normal component.** Even if both algorithms recover independent components, small differences in component recovery can change which component is selected and therefore change the final regression coefficient.

Working classification: FastICA is methodologically related and may be defensible, but JADE is the closer match to the paper/R reference.

## 5. Does the Paper or R Implementation Require JADE Specifically?

### Paper

The Haschka/Dost paper does not appear to prove that only JADE can be used. The theoretical source of truth is the ICA/cumulant identification logic, not a software package requirement.

But the paper does:

- highlight JADE as a relevant ICA implementation,
- discuss JADE as a fourth-order cumulant / joint diagonalization method,
- use `method = "jade"` in implementation examples.

Therefore, the paper does not strictly require JADE as the only possible ICA algorithm, but it strongly motivates JADE as the natural reference algorithm.

### R Reference Implementation

The R implementation defaults to JADE:

```r
ica_reg <- function(formula, data, method = "jade", CF = FALSE, nboots = 199)
```

The R implementation passes the selected method into `ica::ica(...)`. The R `ica` package supports FastICA, Infomax, and JADE, but the thesis reference implementation chooses JADE by default.

Conclusion: JADE is not merely incidental in the R implementation. It is the default reference behavior.

## 6. Is FastICA a Defensible Substitute?

FastICA can be defensible as a temporary or pragmatic substitute, but only with explicit documentation.

Arguments in favor of FastICA:

- It is available in scikit-learn, already part of the expected Python ecosystem.
- It is easy to install and reproduce.
- It is a standard ICA algorithm.
- It targets independent non-Gaussian components, which is the broad requirement of the estimator.
- It keeps the Python implementation simple and explainable for a bachelor thesis.

Arguments against treating FastICA as automatically equivalent:

- The paper's proof and examples are more naturally aligned with cumulant methods and JADE.
- The R reference implementation defaults to JADE.
- FastICA's output can depend on initialization, contrast function, convergence tolerance, whitening behavior, and random seed.
- Different ICA algorithms may recover slightly different components in finite samples, especially when non-normality is weak or sample size is small.
- The final regression can be sensitive to component selection if the recovered components are not cleanly separated.

Current judgement: FastICA is defensible as a provisional implementation choice if the thesis clearly states the deviation and empirically checks whether results are stable. It should not be presented as identical to JADE without evidence.

## 7. Empirical Differences That May Occur

FastICA and JADE may differ empirically in:

- which component is recovered as most normal,
- convergence behavior,
- sensitivity to sample size,
- sensitivity to weak non-normality,
- sensitivity to symmetric non-normal distributions where skewness is low but kurtosis matters,
- sensitivity to outliers or heavy tails,
- failure or warning rates,
- estimated `beta` after the final control-function or residualization step,
- RMSE and relative bias in simulations,
- bootstrap variability.

Scenarios where differences are most likely:

- small `N`,
- near-normal `eta`,
- low signal-to-noise separation,
- distributions with weak fourth-order signal,
- heavy-tailed distributions,
- multiple endogenous regressors,
- exogenous-control residualization cases.

Scenarios where differences may be small:

- simple two-source DGP,
- strong non-normality,
- large sample size,
- clear separation between normal and non-normal components.

## 8. Should a Python JADE Implementation Be Considered?

Yes, but not immediately as a code replacement.

A Python JADE implementation should be considered if:

- FastICA and JADE give noticeably different simulation results,
- the supervisor expects close replication of the R reference implementation,
- thesis defense requires strong alignment with the paper's cumulant argument,
- final results are sensitive to the ICA algorithm,
- FastICA has convergence or instability issues in important scenarios.

A Python JADE implementation may not be necessary if:

- FastICA results are empirically close to R/JADE across thesis-relevant scenarios,
- the thesis explicitly documents FastICA as an implementation choice,
- the supervisor accepts FastICA as a reasonable ICA substitute,
- adding JADE would create too much dependency or maintenance complexity.

Supervisor input is recommended before making a final decision, because this is a methodological rather than purely technical choice.

## 9. Python Libraries That Could Provide JADE

Potential options found during the audit:

1. **Keep scikit-learn FastICA and compare against R/JADE externally**
   - No new Python dependency.
   - Use the R implementation as the JADE benchmark.
   - Best first step.

2. **Use a small Python JADE implementation such as `jadeR.py`**
   - There are Python translations of Cardoso's MATLAB JADE code, for example `gbeckers/jadeR`.
   - Advantage: conceptually close to JADE.
   - Risk: not a mainstream packaged dependency; maintenance, API, license, testing, and reproducibility need review.

3. **Use domain-specific packages with joint diagonalization tools**
   - Some packages, such as pyRiemann, provide approximate joint diagonalization tools, but not necessarily the same fourth-order JADE estimator needed here.
   - These may be inappropriate unless they implement the exact required ICA/Jade variant.

4. **Use MNE/Picard/Infomax alternatives**
   - MNE supports FastICA, Infomax, and Picard, but not JADE in its current documented ICA interface.
   - Picard may be useful for other ICA comparisons, but it is not a JADE replacement.

5. **Port or vendor a JADE implementation**
   - Possible but higher responsibility.
   - Would require careful attribution, licensing review, tests, and explanation in the thesis.

Current recommendation: do not add a Python JADE dependency yet. First compare current Python FastICA results against the R implementation on matched simulation scenarios.

## 10. Trade-Offs

| Option | Correctness / paper alignment | Reproducibility | Explainability | Installation complexity | Thesis defense |
|---|---|---|---|---|---|
| Keep FastICA only | Medium: valid ICA method, but not R/paper default | High with fixed seed and scikit-learn version | Easy to explain broadly, harder to defend as paper-equivalent | Low | Acceptable only if deviation is documented and empirically checked |
| Add Python JADE dependency | High if implementation matches Cardoso/R JADE | Depends on package maturity | Strong paper/R alignment, but more algorithm detail to explain | Medium to high | Stronger if package is stable; risky if package is obscure |
| Compare Python FastICA against R JADE without adding dependency | High as audit evidence, no code change | Medium: requires R environment | Easy to justify as validation step | Low to medium | Strong first step; avoids premature dependency decision |
| Implement/port JADE manually | Potentially high but hard to guarantee | Medium if tested well | Harder; more code to defend | High | Only justified if necessary and approved |

## 11. Recommended Next Step

Recommended next step:

1. Do not replace FastICA now.
2. Create a small matched comparison plan:
   - same generated datasets,
   - Python FastICA estimator,
   - R `ica_reg(..., method = "jade")`,
   - same `CF` setting where possible,
   - same component-selection logic as closely as possible,
   - compare selected component normality, `beta` estimate, failures, and runtime.
3. Start with the simplest two-variable DGP and a few sample sizes.
4. Then test more difficult cases: weak non-normality, heavy tails, symmetric non-normal distributions, and small sample sizes.
5. Use the results to decide whether FastICA is acceptable or whether a JADE implementation is needed.
6. Ask the supervisor before making a final method decision, especially if the thesis will claim methodological equivalence to the R reference implementation.

Working recommendation for now: FastICA is acceptable as a provisional implementation while auditing continues, but final thesis results should either demonstrate that FastICA behaves similarly to JADE in thesis-relevant scenarios or switch to a justified JADE implementation after explicit approval.

## References

- Haschka/Dost paper notes: `docs/paper_notes.md`, especially Sections 8-11 and 18.
- R reference analysis: `docs/r_reference_analysis.md`, especially Sections 9-11.
- scikit-learn FastICA API documentation: https://scikit-learn.org/stable/modules/generated/fastica-function.html
- scikit-learn ICA user guide: https://scikit-learn.org/stable/modules/decomposition.html#ica
- R `ica` package manual, including `icajade`: https://cran.r-universe.dev/ica/ica.pdf
- R `ica` package overview: https://www.rdocumentation.org/packages/ica/versions/1.0-3
- Example Python JADE translation (`jadeR.py`): https://github.com/gbeckers/jadeR
- MNE ICA method documentation: https://mne.tools/stable/generated/mne.preprocessing.ICA.html
