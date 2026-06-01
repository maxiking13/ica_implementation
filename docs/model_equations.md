# Model Equations and Algorithmic Reference

Source basis:

- Haschka/Dost ICA paper: `papers/haschka_ICA.pdf`.
- Prior notes: `docs/paper_notes.md`.

Scope: This document extracts the mathematical and algorithmic reference model for the Python implementation. It is not yet a comparison against the R reference implementation or the Python code.

Notation convention in this document:

- I use `Y` for the outcome, `P` for the endogenous regressor, `X` for observed exogenous regressors, `xi` for the structural error/normal confounding source in the proof notation, `v` for the omitted normal component in the paper's intuitive notation, and `eta` for the non-normal exogenous component of `P`.
- The paper uses both `v` and `xi` for closely related normal/endogenous components in different sections. This is preserved where needed and marked as an ambiguity.

## 1. Structural Equation for Y

### Paper reference

- Section 2, Equation (1), p. 7.
- Formal proof, Equation (4), p. 10.
- Exogenous-regressor extension, Remark 5, pp. 15-16.
- Simulation DGP examples, Equations (21), (34), (36), (42), (46), (53), (56), (58), (64), (72), (74), pp. 20-43.

### Notation

Core structural equation:

```text
Y = alpha + beta_1 P + xi
```

With observed exogenous regressors:

```text
Y = alpha + beta_1 P + beta_2 X + xi
```

### Plain-language explanation

`Y` is the dependent variable. `P` is the endogenous regressor whose causal coefficient `beta_1` is the main target. `xi` is the structural error term. Endogeneity arises because `P` and `xi` share a latent normal component.

### Implementation implication

A correct implementation must estimate the coefficient on `P` in a final regression that includes the recovered normal ICA component as a control function. If observed exogenous regressors `X` are present, they must also be included in the final regression.

### Possible edge cases

- Multiple endogenous regressors require extending `P` to `P_1, ..., P_K` and using `K + 1` ICA inputs after residualization, according to Section 3.3, pp. 19-20.
- The paper includes an intercept `alpha` in the equations and examples, but does not fully specify implementation details for intercept removal. Intercept handling is therefore an implementation audit point.

## 2. Equation for the Endogenous Regressor P

### Paper reference

- Section 2, Equation (2), p. 7.
- Formal proof, Equation (3), p. 10.
- Exogenous-regressor extension, Remark 5, pp. 15-16.
- Benchmark simulation, Equation (25), p. 21.

### Notation

Intuitive DGP:

```text
P = eta + rho v
```

Formal proof representation:

```text
P = eta + rho xi
```

With observed exogenous regressor:

```text
P = eta + rho xi + tau X
```

Benchmark simulation with an instrument used only for IV comparison:

```text
p_i = v_i + rho xi_i + 0.5 x_i + 0.5 w_i
```

### Plain-language explanation

`P` contains a non-normal exogenous source (`eta` or `v_i` in some simulation sections) and a normal component that is also present in the outcome error. The loading `rho` controls the strength of endogeneity. If `X` is present, `P` may also depend linearly on `X`.

### Implementation implication

For the core estimator, ICA must receive variables that preserve the additive mixing structure. With no observed `X`, this means applying ICA to the observed `Y` and `P`. With observed `X`, the paper says to residualize `Y` and `P` on `X` before ICA.

### Possible edge cases

- If the non-normal component becomes close to normal, the method loses separating power; see Section 4.5.1, pp. 33-34, Table 7.
- If the non-normal component is correlated with the error, bias increases; see Section 4.5.2, pp. 35-36, Table 8.
- If additional normal noise dominates `P`, standard errors can become very large; see Section 4.10, p. 43, Table 14.

## 3. Decomposition of the Error Term / Omitted Variable Component

### Paper reference

- Section 2, Equation (2), p. 7.
- Discussion, pp. 43-45.
- Error/noise robustness sections 4.8-4.10, pp. 40-43.

### Notation

Paper's intuitive decomposition:

```text
xi = v (+ u)
```

where:

```text
v ~ normal component shared with P
u ~ optional exogenous error component, independent of (v, eta)
```

Formal proof simplification:

```text
xi ~ N(0, sigma^2)
```

### Plain-language explanation

The omitted variable component `v` creates endogeneity because it affects both `P` and `Y` through the structural error. The paper also allows an additional exogenous error component `u`, but the main proof uses a simpler normal `xi` source.

### Implementation implication

The implementation does not observe `v`, `xi`, or `u`; it must recover a normal component from the observed mixture. Simulation code should be explicit about whether the error is only the shared normal component or includes additional independent noise.

### Possible edge cases

- Additional normal noise in the error can increase uncertainty while preserving near-unbiased point estimates in the paper's simulations; see Section 4.9, p. 42, Table 13.
- Non-normal error components are studied in Section 4.8, pp. 40-41, Table 12.
- The exact role of `u` is ambiguous from the paper alone and should be treated carefully in implementation documentation.

## 4. Distributional Assumptions

### Paper reference

- Abstract, p. 1.
- Introduction, pp. 3-5.
- Section 2, Equation (2), p. 7.
- Formal proof, p. 10.
- Assumption 2, p. 11.
- Remark 3, p. 15.

### Notation

Core proof assumptions:

```text
xi ~ N(0, sigma^2)
eta is non-normal
kappa_3(eta) != 0 or kappa_4(eta) != 0
kappa_3(xi) = kappa_4(xi) = 0
```

### Plain-language explanation

The normal source has zero higher cumulants. The non-normal source must differ in higher-order moments so ICA/cumulant methods can separate the sources.

### Implementation implication

Simulation scenarios must deliberately vary the non-normal exogenous component. Diagnostics should record distribution family, parameters, skewness, kurtosis, and possibly normality test statistics.

### Possible edge cases

- A distribution can be non-normal but weakly informative for separation in finite samples.
- Symmetric non-normal distributions may have zero third cumulant but nonzero fourth cumulant. The paper allows identification through either `h = 3` or `h = 4` (Remark 3, p. 15).
- If empirical higher cumulants are noisy, ICA may be unstable even if the theoretical distribution is non-normal (Remark 4, p. 15).

## 5. Independence Assumptions

### Paper reference

- Section 2, Equation (2), p. 7.
- Formal proof, p. 10.
- Assumption 3, p. 11.
- Remark 5, pp. 15-16.

### Notation

Core independence:

```text
eta independent of xi
eta independent of (v, u)
u independent of (v, eta), if u is present
X independent of xi, in the exogenous-regressor extension
```

### Plain-language explanation

The non-normal component of `P` must be exogenous: it should not directly carry the omitted-variable error component. Independence is what makes the cumulant tensor diagonal and allows ICA to separate sources.

### Implementation implication

The estimator cannot verify full latent independence from observed data. Simulations should include violation scenarios and record performance degradation.

### Possible edge cases

- Section 4.5.2 intentionally violates this assumption by correlating the non-normal component with the error; bias increases as correlation rises (pp. 35-36, Table 8).
- Observed exogenous regressors must be handled by residualization so that the ICA input corresponds to the core source-separation structure.

## 6. Non-Normality Requirement

### Paper reference

- Abstract, p. 1.
- Introduction, pp. 3-5.
- Section 2, p. 7 and footnote 2.
- Assumption 2, p. 11.
- Remark 3, p. 15.
- Section 4.5.1, pp. 33-34, Table 7.
- Section 4.7, pp. 39-40, Table 11.

### Notation

```text
eta not normally distributed
exists h in {3, 4}: kappa_h(eta) != 0
```

### Plain-language explanation

The exogenous component in `P` must be non-normal so it can be separated from the normal confounding/error component. The paper's identification logic uses higher cumulant differences.

### Implementation implication

The simulation engine should record non-normality characteristics. The estimator should select the most normal recovered component as the control function, leaving the less-normal component as exogenous variation.

### Possible edge cases

- If `eta` approaches normality, identification deteriorates and estimates can become unstable (Section 4.5.1, pp. 33-34, Table 7).
- If `P` is empirically non-normal, that is suggestive but does not prove that the non-normality comes from an independent exogenous component.
- The paper does not give a fixed practical threshold for sufficient non-normality.

## 7. ICA Source Separation Formulation

### Paper reference

- Section 2.1, pp. 8-10.
- Formal proof, Equation (5), p. 11.
- Theorem 1 and Theorem 2, pp. 12-14.
- Section 3 implementation examples, pp. 16-20.

### Notation

Observed vector:

```text
X_obs = [P, Y]^T
```

Latent source vector:

```text
S = [eta, xi]^T
```

Mixing representation:

```text
X_obs = A S
```

with:

```text
A = [[1, rho],
     [beta_1, 1 + rho beta_1]]
```

### Plain-language explanation

The observed regressor and outcome are mixtures of independent latent sources. ICA tries to unmix the observed variables into the latent components. The normal component is interpreted as the omitted confounder/error source and is used as a control.

### Implementation implication

For one endogenous regressor, run ICA with two components on `[Y, P]` or `[P, Y]` consistently. The paper's code uses `cbind(Y, P)`, while the proof writes `[P, Y]^T`; an implementation must be internally consistent and ensure the final regression uses the correct observed `P`.

### Possible edge cases

- ICA components are identifiable only up to scale, sign, and order. Component ordering cannot be assumed.
- The paper's examples use JADE; using a different ICA algorithm is a later audit issue.
- If `Y` and `P` are not linearly mixed as assumed, source separation may not correspond to the paper's identification argument.

## 8. Identification Assumptions

### Paper reference

- Assumption 1, p. 11.
- Assumption 2, p. 11.
- Assumption 3, p. 11.
- Lemma 1, pp. 11-12.
- Theorem 1, pp. 12-14.
- Theorem 2, p. 14.
- Corollary 1, p. 14.

### Notation

Invertibility:

```text
det(A) = 1
```

Nonzero cumulant:

```text
exists h in {3, 4}: kappa_h(eta) != 0 and kappa_h(xi) = 0
```

Diagonal cumulant tensor:

```text
C_h(S) is diagonal
```

Cumulant objective:

```text
Q_h(w) = kappa_h(w^T X_obs)
```

Hessian factorization:

```text
nabla_w^2 Q_h(w) = A D(w) A^T
```

Slope recovery:

```text
beta_1 = v_Y / v_P
```

### Plain-language explanation

The proof shows that higher-order cumulant structure identifies an eigenvector proportional to `[1, beta_1]^T`. Normality of one source and non-normality of the other make the sources distinguishable.

### Implementation implication

The practical ICA estimator should be understood as a numerical source-separation procedure motivated by this identification argument. The implementation need not explicitly compute Hessians if the ICA routine performs equivalent source separation under the assumptions, but this equivalence must be justified in the audit.

### Possible edge cases

- If both sources are normal, ICA cannot identify the relevant rotation.
- If cumulant estimates are unstable in finite samples, component recovery may be noisy.
- Scale/sign indeterminacy means the final control component can have arbitrary sign; this should not affect the final regression fit, but component selection and diagnostics must handle it.

## 9. Control Function Estimation Procedure

### Paper reference

- Abstract, p. 1.
- Introduction, p. 5.
- Section 3.1, p. 16.
- Listing 1, p. 17.
- Section 3.2, pp. 18-19.
- Listing 2, p. 19.

### Notation

One endogenous regressor:

```text
1. Run ICA on [Y, P].
2. Select recovered component C_hat that is most normal.
3. Estimate Y = alpha + beta_1 P + delta C_hat + error.
```

With observed exogenous regressors:

```text
Y = alpha + beta_1 P + beta_2 X + delta C_hat + error
```

### Plain-language explanation

The recovered normal component stands in for the omitted confounder. Including it in the final regression should absorb the confounding channel and recover the causal slope on `P`.

### Implementation implication

The default implementation should add the selected ICA component to the final OLS design matrix. Component selection must happen before final regression and must not assume ICA output order.

### Possible edge cases

- The paper does not define the exact statistic for "most normal" in the text. The R implementation must be used as the reference for this practical detail.
- If multiple components appear similarly normal, the estimator may be unstable; this should be logged as a diagnostic or warning.

## 10. Residualization Procedure When CF = FALSE

### Paper reference

- The paper does not define a `CF` argument.
- Paper residualization for observed exogenous regressors is in Remark 5, pp. 15-16, and Sections 3.2-3.3, pp. 18-20.
- `docs/paper_notes.md`, Section 14, marks the relation between paper residualization and R's `CF` option as unclear.

### Notation

Paper-supported residualization for exogenous regressors:

```text
P_perp = P - fitted(P ~ X)
Y_perp = Y - fitted(Y ~ X)
```

Then run ICA on:

```text
[Y_perp, P_perp]
```

or, for multiple endogenous regressors:

```text
[Y_perp, P_1_perp, ..., P_K_perp]
```

### Plain-language explanation

The paper uses residualization to remove observed exogenous regressors before source separation. This ensures the remaining residualized variables satisfy the same core two-source structure.

### Implementation implication

Do not infer the meaning of `CF = FALSE` from the paper alone. If the Python implementation has a `CF` flag, its intended behavior must be compared to the R reference implementation.

### Possible edge cases

- Residualization should account for intercept handling consistently.
- Residualizing the recovered control function out of variables is not described in the paper text and should not be treated as paper-grounded without R-code support.

## 11. Handling of Exogenous Regressors

### Paper reference

- Remark 5, pp. 15-16.
- Section 3.2, pp. 18-19.
- Section 3.3, pp. 19-20.

### Notation

Model with observed exogenous regressor:

```text
P = eta + rho xi + tau X
Y = alpha + beta_1 P + beta_2 X + xi
```

Residualization:

```text
P_perp = residuals from P ~ X
Y_perp = residuals from Y ~ X
```

Final regression:

```text
Y ~ P + X + C_hat
```

### Plain-language explanation

Observed exogenous regressors should not be decomposed by ICA. Their linear influence on `Y` and `P` is removed first, then ICA is applied to the residualized outcome/regressor system.

### Implementation implication

A correct implementation must:

- residualize `Y` and each endogenous `P_k` on all exogenous regressors before ICA,
- run ICA on the residual matrix,
- add the recovered normal component to the final regression with original `P` and `X`.

### Possible edge cases

- Collinearity among exogenous regressors can break residualization or final OLS.
- Non-numeric/dummy/factor handling is not specified in the paper text and must be checked in the R implementation.
- Whether residualization always includes an intercept is ambiguous from the paper alone.

## 12. Intercept Handling

### Paper reference

- Structural equations include `alpha` (Equation (1), p. 7; Remark 5, pp. 15-16).
- Listings include `alpha` in simulations and use R `lm`, which includes an intercept by default (Listings 1-2, pp. 17-19).
- The paper does not discuss formula-level intercept removal in the method section.

### Notation

Default structural intercept:

```text
Y = alpha + beta_1 P + xi
```

### Plain-language explanation

The theoretical model includes an intercept. The paper examples rely on standard regression behavior with an intercept.

### Implementation implication

The implementation should include an intercept by default in final OLS unless the user explicitly removes it through supported formula syntax. Residualization and rank checks should be consistent with that choice.

### Possible edge cases

- Intercept removal is not specified by the paper, but may be supported by the R implementation.
- If residualization excludes an intercept accidentally, the ICA input may retain mean shifts related to `X`.
- Mean centering is not presented as a substitute for the method.

## 13. Bootstrap Standard Errors

### Paper reference

- Introduction, p. 6: R code provides robust standard errors with an adapted bootstrap.
- Discussion, p. 45: R routine supplies bootstrap standard errors.
- Table 1 note, p. 22: simulations report empirical SD, RMSE, and bias t-ratio over `R = 1,000` replications.

### Notation

The paper does not give a full bootstrap algorithm. A generic placeholder would be:

```text
for b = 1, ..., B:
    resample data
    rerun ICA estimator
    store beta_hat_b
SE_boot(beta_hat) = sd(beta_hat_1, ..., beta_hat_B)
```

This is an inference about likely bootstrap structure, not a paper-specified algorithm.

### Plain-language explanation

The paper treats bootstrap standard errors as part of the supplied practical implementation, but the PDF does not provide the exact resampling procedure.

### Implementation implication

The R implementation is the source of truth for bootstrap details. Python should not invent a bootstrap procedure without first mapping the R behavior.

### Possible edge cases

- ICA can fail in bootstrap samples.
- Component order/sign can change across bootstrap samples.
- Bootstrap estimates may be extreme when identification is weak.
- The treatment of failed bootstrap draws is unspecified in the paper.

## 14. Diagnostics / Identification Checks

### Paper reference

- Introduction, p. 6: implementation includes diagnostics, for example checking non-normality.
- Section 4.5, pp. 33-36, Tables 7-8: assumption-breakdown simulations.
- Section 4.10, p. 43, Table 14: large standard errors as warning sign.
- Discussion, pp. 44-45.

### Notation

Paper-supported diagnostic concepts:

```text
non-normality of P / eta
large standard errors
finite-sample instability
violations of independence
```

### Plain-language explanation

Diagnostics should warn when the data no longer clearly support ICA separation: weak non-normality, near-normal exogenous component, correlated exogenous component, or unstable estimates.

### Implementation implication

At minimum, simulation output should record:

- failed ICA runs,
- failure rate per scenario,
- skewness and kurtosis,
- distribution parameters,
- standard errors where available,
- normality-selection diagnostic values if produced by the estimator.

### Possible edge cases

- The paper does not prescribe exact thresholds.
- The paper does not specify the normality test used for component selection.
- Empirical non-normality of `P` does not prove that the identifying latent component is independent and non-normal.

## 15. Finite-Sample Considerations

### Paper reference

- Remark 4, p. 15.
- Benchmark simulations, pp. 20-22, Table 1.
- Robustness/failure simulations, pp. 33-43, Tables 7-14.
- Discussion, pp. 43-45.

### Notation

Remark 4 states:

```text
n >= binomial(d + h - 1, h)
```

for estimating h-th cumulants, where `d` is the source dimension and `h` is the cumulant order.

### Plain-language explanation

Theoretical identification does not guarantee stable finite-sample estimation. Higher-order moment estimates can be noisy, especially when sample size is small or the non-normal component has weak variance/non-normality.

### Implementation implication

Simulation design should distinguish:

- quick/debug runs for code verification,
- final/thesis runs for evidence,
- failure/instability tracking.

### Possible edge cases

- Small samples can make component recovery unstable.
- Weak non-normality can mimic non-identification.
- Large normal noise can inflate standard errors, even if point estimates remain near the true value.

## 16. What a Correct Implementation Must Do

### Paper reference

- Section 3.1, p. 16; Listing 1, p. 17.
- Section 3.2, pp. 18-19; Listing 2, p. 19.
- Section 3.3, pp. 19-20.
- Remark 5, pp. 15-16.

### Notation / algorithm

For one endogenous regressor:

```text
Input: data with Y and P
Run ICA on [Y, P] with 2 components
Select most-normal component C_hat
Estimate final OLS: Y ~ P + C_hat
Return beta_hat_P and uncertainty/diagnostics
```

With exogenous regressors:

```text
Input: data with Y, P, X
Compute residuals Y_perp from Y ~ X
Compute residuals P_perp from P ~ X
Run ICA on [Y_perp, P_perp]
Select most-normal component C_hat
Estimate final OLS: Y ~ P + X + C_hat
Return beta_hat_P and uncertainty/diagnostics
```

With multiple endogenous regressors:

```text
Residualize Y and every P_k on all X variables
Run ICA on [Y_perp, P_1_perp, ..., P_K_perp] with K + 1 components
Select most-normal component C_hat
Estimate final OLS: Y ~ P_1 + ... + P_K + X + C_hat
```

### Plain-language explanation

The implementation must preserve the paper's sequence: prepare the correct ICA input, recover sources, choose the normal component, and use it as a control in the final regression.

### Implementation implication

Minimum implementation requirements:

- parse dependent, endogenous, and exogenous variables correctly,
- validate required variables and numeric data,
- handle missing data explicitly,
- add/intercept terms consistently,
- check rank/collinearity where OLS is used,
- run ICA with the correct number of components,
- select the most normal component without assuming component order,
- include the selected component in the final regression,
- report estimates, uncertainty, and diagnostics,
- record failures rather than silently dropping them.

### Possible edge cases

- Multiple endogenous regressors with one shared normal component versus multiple latent confounders.
- Component-order and sign indeterminacy.
- ICA convergence failures.
- Rank-deficient design matrices after adding the recovered component.

## 17. Possible Implementation Pitfalls

### Paper reference

- Section 3 implementation sketches, pp. 16-20.
- Remark 4, p. 15.
- Section 4.5, pp. 33-36.
- Section 4.10, p. 43.

### Pitfalls

- Treating the paper as if it specifies all software details. It does not specify formula parsing, missing data handling, bootstrap mechanics, or component-selection test statistics.
- Assuming ICA component order. The paper says to identify the most normal component; it does not say component 1 is always the normal component.
- Confusing the paper's residualization for exogenous regressors with the R implementation's possible `CF = FALSE` behavior.
- Ignoring intercept handling in residualization and final OLS.
- Using an ICA algorithm different from the paper/R example without documenting the methodological implication.
- Silently dropping failed ICA or bootstrap runs.
- Computing bias/RMSE without reporting failure rate.
- Treating quick/debug simulations as thesis evidence.
- Claiming empirical non-normality of `P` proves all latent identification assumptions.
- Applying the method when the non-normal component is near-normal, correlated with the error, or dominated by extra normal noise without warnings.

### Implementation implication

These pitfalls should become explicit audit checks when comparing the paper, R implementation, and Python implementation.

### Possible edge cases

- The estimator may appear numerically successful while selecting the wrong component.
- Bootstrap standard errors may explode in weak-identification scenarios.
- A final OLS coefficient may be close to the true value in quick simulations by chance; this should not be interpreted without adequate replications and diagnostics.
