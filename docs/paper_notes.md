# Paper Notes: Haschka/Dost ICA Method

Source: `papers/haschka_ICA.pdf`, Dost and Haschka, *ICA at the Cocktail Party: Casting Instrument-free Omitted Variable Bias Correction as a Blind Source Separation Problem*, dated July 22, 2025.

Scope: These notes focus on the ICA-based endogeneity correction method. They are not yet a Paper-R-Python audit and do not judge whether the current Python implementation is correct.

## 1. Research Problem

### Paper explicitly states

- The paper targets endogeneity from omitted variables in empirical research, especially cases where valid instruments are difficult to find (Abstract, p. 1; Introduction, pp. 2-3).
- The proposed method is instrument-free and is designed for additive omitted variable bias rather than for generic regressor-error dependence (Abstract, p. 1; Introduction, pp. 3-5).
- The paper reframes omitted-variable endogeneity as a blind source separation problem: observed variables are mixtures of latent independent sources (Introduction, pp. 4-5; Section 2.1, pp. 8-10).

### Inference for thesis

- The thesis should present the method as a targeted correction for a specific omitted-variable DGP, not as a universal endogeneity correction.
- The central object is the causal slope on the endogenous regressor, denoted `beta_1` or `beta` depending on the paper section (Equation (1), p. 7; simulations, Section 4).

### Unclear / needs later audit

- The paper's simulation notation sometimes changes from `P, Y, xi, eta, v` to `p_i, y_i, xi_i, v_i`. This should be standardized in `docs/model_equations.md`.

## 2. Why Omitted Variable Bias Is Relevant

### Paper explicitly states

- Endogeneity arises when the regressor is correlated with the error term because of omitted variables (Introduction, p. 2; Section 2, p. 7).
- In the structural model `Y = alpha + beta_1 P + xi`, `P` is endogenous because it shares a normal component with `xi` (Equation (1), p. 7; Equation (2), p. 7).
- OLS is biased when `P` and `xi` share the omitted component (Section 2, p. 7; benchmark simulation discussion, p. 21).
- The paper describes additive omitted variable bias as the common marketing-research case that the method is intended to handle (Introduction, p. 3; Discussion, pp. 43-45).

### Inference for thesis

- The simulation setup should include untreated OLS as a baseline because OLS bias is the problem the ICA estimator tries to reduce.
- Omitted variable bias should be explained through the shared component between `P` and the structural error, not only through abstract correlation.

### Unclear / needs later audit

- The paper allows `xi = v (+ u)` in Equation (2), but the formal proof later uses a simpler `xi` source. The exact role of additional error noise `u` should be clarified in the model-equation document.

## 3. Why Instrumental Variables Are Difficult

### Paper explicitly states

- The classical remedy for endogeneity is instrumental variables, but valid instruments satisfying exclusion restrictions are difficult to find (Introduction, p. 2; Discussion, p. 43).
- The proposed method is motivated by settings where external instruments are unavailable (Abstract, p. 1; Introduction, pp. 2-5).
- The paper analogizes the non-normal exogenous component in the endogenous regressor to a latent instrument: it affects `P` but not `Y` except through `P` (Introduction, p. 4).

### Inference for thesis

- The thesis can present ICA as recovering latent source variation that plays an instrument-like or control-function role, but should avoid saying it creates a conventional observed IV.

### Unclear / needs later audit

- The exact relationship between the paper's "latent instrument" intuition and classical IV assumptions should be handled carefully, especially because the estimator is implemented as a control-function correction.

## 4. Why Gaussian Copula Is Not Sufficient for the Target Case

### Paper explicitly states

- Gaussian copula control function methods assume non-normal endogenous regressors, normal errors, and a Gaussian copula dependence structure (Introduction, p. 2).
- The paper states that Gaussian copula control function methods fail for traditional additive omitted variable bias and can be more biased than OLS in that case (Abstract, p. 1; Introduction, p. 3; Discussion, p. 44).
- The reason given is that Gaussian copula methods assume a particular nonlinearity or bijective transformation source of regressor-error dependence, whereas additive omitted-variable bias has a different structure (Introduction, p. 3).

### Inference for thesis

- Becker-style Gaussian copula work should be used for evaluation and presentation templates, not as the theoretical basis for ICA.
- The thesis should clearly distinguish the ICA DGP from Gaussian copula DGPs.

### Unclear / needs later audit

- The paper compares to Park and Gupta and other IV-free approaches in Section 4.4, but detailed comparison is not needed before the core ICA model is extracted.

## 5. Data-Generating Process

### Paper explicitly states

- Basic structural model: `Y = alpha + beta_1 P + xi` (Equation (1), p. 7).
- Decomposition: `P = eta + rho v` and `xi = v (+ u)` (Equation (2), p. 7).
- `v` is normally distributed with zero mean; `eta` is non-normal and independent of `(v, u)`; `u` is exogenous and independent of `(v, eta)` if present (Equation (2), p. 7).
- Formal proof rewrites the model as `P = eta + rho xi` and `Y = alpha + beta_1 P + xi` (Equations (3)-(4), p. 10).
- In the proof, `eta` is non-normal with a nonzero third or fourth cumulant, `xi` is normal, and `eta` and `xi` are mutually independent (p. 10).
- With observed exogenous regressors, the paper gives `P = eta + rho xi + tau X` and `Y = alpha + beta_1 P + beta_2 X + xi` (Remark 5, pp. 15-16).

### Inference for thesis

- For a first Python simulation, the minimal DGP can be `P = eta + rho xi` and `Y = alpha + beta P + xi`.
- For simulations with exogenous regressors, the paper supports residualizing `P` and `Y` with respect to `X` before ICA, then estimating the final model with `P`, `X`, and the recovered component.

### Unclear / needs later audit

- The paper uses `v` for the normal omitted component in Equation (2), but the proof uses `xi` as a latent source in `P = eta + rho xi`. This is mathematically related but should be made notationally consistent before implementation claims are made.

## 6. Key Variables and Notation

### Paper explicitly states

- `Y`: dependent/outcome variable (Equation (1), p. 7).
- `P`: scalar endogenous regressor in the core model (Equation (1), p. 7).
- `alpha`: intercept (Equation (1), p. 7; listings, pp. 17-19).
- `beta_1` or `beta`: causal slope on the endogenous regressor (Equation (1), p. 7; simulations, Section 4).
- `xi`: structural error term; in the formal proof it is normal (Equation (1), p. 7; p. 10).
- `v`: normal component shared by `P` and the error in the intuitive DGP (Equation (2), p. 7).
- `eta`: non-normal exogenous component of `P`, independent of the normal/confounding component (Equation (2), p. 7; p. 10).
- `rho`: governs the strength of endogeneity through the loading of the normal/error component into `P` (Equation (2), p. 7; Equation (25), p. 21).
- `X`: observed exogenous regressor(s), introduced for residualization/partialling-out logic (Remark 5, pp. 15-16; Section 3.2, pp. 18-19).
- `S`: vector of latent sources in the ICA/mixing representation (Equation (5), p. 11).
- `A`: mixing matrix mapping sources into observed variables (Equation (5), p. 11).

### Inference for thesis

- Use one notation system in thesis text. Suggested: reserve `xi` for the structural error/normal confounder in the simple implementation and document how this maps to the paper's `v` and `xi`.

### Unclear / needs later audit

- Whether to call the recovered component a "confounder", "normal component", or "control function" should be standardized. The paper uses all three ideas in different places (pp. 5, 16-20, 44-45).

## 7. Mathematical Assumptions

### Paper explicitly states

- The structural error term is normally distributed (Introduction, p. 3; p. 10).
- The hidden confounder/shared component is normally distributed (Introduction, p. 3; Equation (2), p. 7; Discussion, p. 44).
- The endogenous regressor contains a non-normal exogenous component (Abstract, p. 1; Equation (2), p. 7; p. 10).
- The non-normal component must be independent of the normal/error component (Equation (2), p. 7; p. 10).
- Identification is based on differences in higher cumulants between `eta` and `xi`; `eta` must have a nonzero third or fourth cumulant while the normal component has zero higher cumulants (footnote 2, p. 7; Assumption 2, p. 11; Remark 3, p. 15).
- The mixing matrix is invertible in the core two-source proof (Assumption 1, p. 11).
- The cumulant tensor is diagonal because of source independence (Assumption 3, p. 11).

### Inference for thesis

- The thesis should treat non-normality as a necessary identifying feature, not merely a plotting characteristic.
- Distribution choices in simulations should vary skewness/kurtosis and closeness to normality because the method relies on higher cumulant differences.

### Unclear / needs later audit

- The paper does not give a complete practical rule for "sufficient" non-normality in empirical data. Simulations and diagnostics must support any threshold used later.

## 8. ICA Intuition

### Paper explicitly states

- ICA recovers latent independent factors from observed linear mixtures and uses higher-order statistics, unlike PCA/factor analysis, which rely on covariance structure (Section 2.1, p. 8).
- ICA is described as blind source separation, with the cocktail-party analogy (Section 2.1, p. 8; Introduction, p. 4).
- In the regression problem, `P` and `Y` are treated as mixtures of independent influences: the normal omitted factor and the non-normal exogenous component in `P` (Introduction, pp. 4-5; Section 2.1, pp. 8-10).
- The paper highlights JADE as a known ICA implementation that uses fourth-order cumulants and joint approximate diagonalization (Section 2.1, pp. 9-10).

### Inference for thesis

- The intuitive explanation should be: ICA separates the normal source associated with endogeneity from the non-normal source providing exogenous variation in `P`; the normal source is then controlled for in the final regression.
- PCA is not an equivalent substitute because the relevant identifying information comes from higher-order non-Gaussian structure, not only covariance.

### Unclear / needs later audit

- The paper's implementation example uses JADE; the Python implementation currently uses FastICA. This is a critical later audit point, but not resolved in these paper notes.

## 9. Identification Logic

### Paper explicitly states

- The observed vector is `X = [P, Y]^T`, represented as `X = A S`, where `S = [eta, xi]^T` and the mixing matrix `A` contains the structural slope (Equation (5), p. 11).
- The structural parameter matrix is `Lambda = A^{-1}` (p. 11).
- Identification uses higher-order cumulants: the normal component has zero third/fourth cumulants, while `eta` has a nonzero third or fourth cumulant (Assumption 2, p. 11).
- The cumulant objective `Q_h(w)` is defined for `h = 3` or `h = 4` (Equation (6), p. 11).
- The Hessian factorizes as `nabla_w^2 Q_h(w) = A D(w) A^T` (Equations (7)-(11), pp. 11-12).
- A pseudoinverse/eigendecomposition argument recovers the first column of `A`, proportional to `[1, beta_1]^T` (Theorem 1, pp. 12-14).
- The slope is identified by normalizing the recovered eigenvector: `beta_1 = v_Y / v_P` (Equation (20), p. 14).
- The paper states point identification under Assumptions 1-3 (Theorem 2, p. 14).

### Inference for thesis

- The implementation's component-recovery procedure should be justified as an applied ICA version of the paper's source-separation/eigenvector identification logic.
- The model equations document should separate formal identification from the practical estimator, because the paper proves identification through cumulants but the R/Python implementations call an ICA routine.

### Unclear / needs later audit

- The paper does not provide a detailed bridge from the formal Hessian/eigenvector proof to the exact practical component-selection statistic used in the R function.

## 10. Estimation Procedure

### Paper explicitly states

- General procedure for one endogenous regressor: run ICA on observed `Y` and `P`, identify the most normal component, then regress `Y` on `P` and the identified normal component (Section 3.1, p. 16; Listing 1, p. 17).
- With exogenous regressors: residualize `Y` and `P` with respect to `X`, run ICA on the residuals, identify the most normal component, then regress original `Y` on `P`, `X`, and the identified component (Section 3.2, pp. 18-19; Listing 2, p. 19).
- With multiple endogenous and exogenous regressors: residualize each endogenous regressor and `Y` on all exogenous regressors, run ICA on the residualized variables with `K + 1` components, identify the most normal component, and estimate the final regression with all original regressors and the component (Section 3.3, pp. 19-20).

### Inference for thesis

- The estimator has two conceptually separate stages: source recovery and final regression.
- Formula parsing, intercept handling, residualization, and component selection are all implementation-sensitive and should be audited later against R.

### Unclear / needs later audit

- The paper says "identify the component that is the most normal" but the formal paper text does not specify a formal test statistic or standardization rule for this step (Section 3, pp. 16-20).

## 11. One-Endogenous-Regressor Case

### Paper explicitly states

- For one endogenous regressor, the paper uses `data_matrix <- cbind(Y, P)`, calls `ica(..., nc = 2, method = "jade")`, visually inspects/identifies the normally distributed component, and estimates `lm(Y ~ P + component)` (Listing 1, p. 17).
- The conceptual steps are ICA decomposition, most-normal-component identification, and final regression with the component (Section 3.1, p. 16).

### Inference for thesis

- This is the natural starting point for the Python implementation audit and simple simulation DGP.
- The final regression should use the original `Y` and `P`, not the recovered non-normal component as a substitute for `P`, unless a separate residualization variant is explicitly justified.

### Unclear / needs later audit

- Listing 1 selects `ica_result$S[,1]` in the final model after saying the normal component should be identified. It is not clear from the listing alone whether component 1 is guaranteed to be normal or is chosen manually after inspection.

## 12. Case With Exogenous Regressors

### Paper explicitly states

- If observed exogenous regressors are present, the paper first removes linear dependence of `Y` and `P` on `X` (Section 3.2, p. 18).
- The paper residualizes both `Y` and `P` on `X`, runs ICA on these residuals, and then estimates `Y ~ P + X + recovered component` (Section 3.2, pp. 18-19; Listing 2, p. 19).
- Remark 5 gives the theoretical justification: after partialling out `X`, `(P_perp, Y_perp)` satisfy the same system as the core model (pp. 15-16).

### Inference for thesis

- Any Python support for exogenous regressors should residualize before ICA and include the original exogenous regressors in the final regression.
- This is a high-priority audit point because mistakes in residualization can change the method mathematically.

### Unclear / needs later audit

- The paper does not specify detailed handling of intercepts during residualization. The R implementation must be checked for this.

## 13. Control Function Approach

### Paper explicitly states

- The recovered confounder/normal component is incorporated as a control function (Abstract, p. 1; Introduction, p. 5).
- The final regression includes the identified normal ICA component alongside `P` and, if present, observed controls `X` (Section 3.1, p. 16; Section 3.2, pp. 18-19).
- The paper says this mimics a control-function or IV logic by purging endogeneity through the ICA decomposition (Section 3.1, p. 16).

### Inference for thesis

- The default thesis explanation should treat the recovered normal component as a control function for the omitted confounder.
- In implementation terms, this means the component becomes an additional regressor in the final OLS model.

### Unclear / needs later audit

- The paper does not discuss alternative control-function transformations or multiple recovered normal components in the core implementation section.

## 14. Residualization Approach

### Paper explicitly states

- The paper explicitly uses residualization/partialling out for observed exogenous regressors before ICA (Remark 5, pp. 15-16; Section 3.2, pp. 18-19; Section 3.3, pp. 19-20).
- It does not describe a separate final-estimation approach where the control function itself is residualized out instead of included in the final model.

### Inference for thesis

- "Residualization" in the paper should primarily mean removing observed exogenous controls from `Y` and `P` before source separation.
- If the R implementation has a `CF = FALSE` residualization option, that is an R-implementation detail that must be analyzed separately rather than assumed from the paper text.

### Unclear / needs later audit

- The relation between paper residualization and the R function's `CF` argument requires R-code analysis.

## 15. Bootstrap / Uncertainty Handling

### Paper explicitly states

- The paper says the open-source R implementation provides robust standard errors with an adapted bootstrap (Introduction, p. 6, footnote 1 context).
- The discussion states that the R routine supplies bootstrap standard errors (Discussion, p. 45).
- Simulation tables report empirical SD, RMSE, and bias t-ratio over 1,000 replications (Table 1 note, p. 22; other tables refer back to Table 1).

### Inference for thesis

- Bootstrap uncertainty is part of the intended practical implementation, but the paper itself does not provide enough procedural detail for a Python implementation.
- For simulations, uncertainty should be separated into empirical Monte Carlo variability versus estimator-reported bootstrap standard errors.

### Unclear / needs later audit

- The exact bootstrap algorithm, resampling level, p-value calculation, and treatment of failed bootstrap runs must be taken from the R reference implementation, not from the paper alone.

## 16. Diagnostics and Warnings

### Paper explicitly states

- The paper says the R implementation includes diagnostics, including checking the non-normality requirement (Introduction, p. 6).
- The method requires a non-normal exogenous component in `P`; the paper says non-normality of `P` as a whole can be checked in the data, but the source of non-normality is an assumption about the exogenous component (Introduction, p. 4; Discussion, p. 44).
- Large standard errors may flag identification deviations in empirical applications (Section 4.10, p. 43).
- Section 4.5 studies breakdown when the exogenous component becomes normal or correlated with the error (pp. 33-36; Tables 7-8).

### Inference for thesis

- Diagnostics should include at least sample size, non-normality/skewness/kurtosis of the endogenous regressor or its exogenous component proxy, ICA failures, and unusually large standard errors.
- A Figure 8-style decision guideline should be based on observable diagnostics where possible and simulation evidence where thresholds are needed.

### Unclear / needs later audit

- The paper does not specify exact warning thresholds for non-normality, standard errors, or ICA instability.
- The paper does not specify which normality test should be used for component selection; the R code should determine the current reference behavior.

## 17. Limitations

### Paper explicitly states

- The method depends on identifying conditions: a normal shared/confounding component and a non-normal independent exogenous component in the endogenous regressor (Abstract, p. 1; Section 2, pp. 7-16; Discussion, pp. 44-45).
- Finite samples can be problematic because cumulant estimation requires enough observations, empirical noise can dominate higher cumulants, and smooth non-Gaussian distributions help higher moments converge (Remark 4, p. 15).
- Identification deteriorates when the exogenous component becomes normal (Section 4.5.1, pp. 33-34; Table 7).
- Bias grows when the non-normal component becomes correlated with the error (Section 4.5.2, pp. 35-36; Table 8).
- Additional normal noise in the endogenous regressor can strongly inflate standard errors and can indicate identification problems (Section 4.10, p. 43; Table 14).
- The paper notes sensitivity to severe departures from normality in the confounder and possible complexity with multiple latent confounders (Discussion, p. 45).

### Inference for thesis

- The thesis should avoid claiming the estimator is robust to all endogeneity forms.
- The simulation design should include failure/near-failure scenarios, not only favorable cases.

### Unclear / needs later audit

- The boundary between acceptable and unacceptable departures from assumptions is not given as a ready-to-use rule. It should be derived or supported by simulation evidence.

## 18. Parts Relevant for Python Implementation

### Paper explicitly states

- ICA input for one endogenous regressor: `Y` and `P` (Section 3.1, p. 16; Listing 1, p. 17).
- ICA input with exogenous regressors: residualized `Y` and residualized `P` (Section 3.2, pp. 18-19; Listing 2, p. 19).
- Number of ICA components: two for one endogenous regressor; `K + 1` for `K` endogenous regressors plus residualized `Y` (Section 3.1, p. 16; Section 3.3, pp. 19-20).
- Component selection: identify the most normal ICA component (Section 3.1, p. 16; Section 3.2, p. 18; Section 3.3, p. 20).
- Final regression: include original endogenous regressors, exogenous controls if present, and the identified normal component (Section 3, pp. 16-20).
- Paper example uses `method = "jade"` in R (Listing 1, p. 17; Listing 2, p. 19).

### Inference for thesis

- Critical Python audit areas: ICA algorithm choice, formula parsing, intercept handling, residualization with exogenous regressors, component normality selection, final regression design matrix, bootstrap uncertainty, and diagnostics.
- The Python implementation should be evaluated for methodological equivalence, not line-by-line similarity.

### Unclear / needs later audit

- The paper does not define a formal API, input validation behavior, missing-value handling, or bootstrap details. These must come from the R implementation and Python code audit.

## 19. Parts Relevant for Simulation Design

### Paper explicitly states

- Benchmark simulation uses `xi_i ~ N(0,1)`, `v_i ~ Gamma(1,1)`, `x_i ~ N(0,1)`, `w_i ~ Exp(1)`, and `p_i = v_i + rho xi_i + .5 x_i + .5 w_i` (Equations (21)-(25), pp. 20-21).
- The benchmark varies `rho = {0, .25, .5, 1}` and `n = {250, 500, 1000}` (p. 21).
- Simulation tables use mean estimates, empirical SD, RMSE, and bias t-ratio over `R = 1,000` replications (Table 1 note, p. 22).
- The paper includes a true omitted-variables setting with up to `J = {20, 10, 5}` omitted variables from several distributions (Section 4.3, pp. 25-27; Table 3).
- Identification-breakdown simulations vary closeness of the exogenous component to normality and correlation between non-normal component and error (Section 4.5, pp. 33-36; Tables 7-8).
- Distribution sensitivity includes chi-square, lognormal, uniform, and beta variants scaled to zero mean and unit variance (Section 4.7, pp. 39-40; Table 11).
- Error/noise robustness scenarios are in Sections 4.8-4.10 (pp. 40-43; Tables 12-14).

### Inference for thesis

- First simulations should start with the core DGP matching the implementation's scope, then expand toward the paper's benchmark and robustness scenarios.
- Metrics should include OLS and ICA estimates, bias, relative bias, RMSE, failure rate, sample size, distribution family/parameters, skewness, and kurtosis.
- Quick/debug simulations must not be interpreted as thesis evidence; final simulations need stable runtime and enough replications.

### Unclear / needs later audit

- The exact final grid for the bachelor's thesis should be chosen after quick runtime checks and after the Python implementation audit confirms which scenarios are supported.

## 20. Open Questions

### Paper explicitly states

- The available paper plus R reference implementation are sufficient for the first audit according to the current project decision.

### Inference for thesis

- The next documentation step should split this note into formal equations in `docs/model_equations.md` and implementation mapping in later R/Python audit documents.

### Unclear / needs later audit

- How exactly does the R implementation choose the "most normal" component?
- How does the R implementation implement the adapted bootstrap and diagnostics?
- How does the R implementation interpret `CF = TRUE` versus `CF = FALSE`, and how does that relate to the paper's control-function wording?
- Is FastICA an acceptable Python substitute for JADE, or should a JADE implementation be considered? This is a critical later audit point, not resolved here.
- How should finite-sample thresholds for a Figure 8-style ICA flowchart be derived from simulation evidence?
