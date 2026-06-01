# R Reference Implementation Analysis

Source files:

- `reference_implementation/R/ICAReg.R`
- `reference_implementation/R/README.md`

Scope: This document analyzes the R implementation as the primary reference implementation for the ICA method. It is a reference analysis, not a claim that the R code is automatically infallible. When the R code and the paper appear to differ, the discrepancy is documented.

## 1. Function Interface

### R file reference

- `ICAReg.R`, `ica_reg <- function(formula, data, method = "jade", CF = FALSE, nboots = 199)`, lines 261-589.
- `README.md`, lines 1-8.

### Explanation

The public function is `ica_reg()`. Its arguments are:

- `formula`: model formula with endogenous variables before an optional `|` and exogenous variables after `|`.
- `data`: a `data.frame`.
- `method`: ICA method passed to `ica::ica()`, default `"jade"`.
- `CF`: logical switch. `TRUE` uses the control-function approach; `FALSE` residualizes the control function out before final estimation according to the README.
- `nboots`: number of bootstrap replications, default `199`.

### Relevance for Python implementation

Python should expose equivalent conceptual inputs: outcome variable, endogenous variables, optional exogenous variables, ICA method choice or documented default, `CF` behavior, and bootstrap count. It does not need to copy R's exact API, but it must preserve the same methodological choices or document deviations.

## 2. Formula Syntax

### R file reference

- `README.md`, lines 2-8.
- `ica_reg()`, formula split via `nlme::splitFormula(formula, sep = "|")`, line 264.
- Exogenous/full formula reconstruction, lines 455-456.

### Explanation

The intended syntax is:

```r
depvar ~ endog_var1 + endog_var2 + ... | exog_var1 + exog_var2 + ...
```

If there is no `|`, all right-hand-side variables are treated as endogenous. If there is a `|`, variables before `|` are endogenous and variables after `|` are exogenous. The README also states that `-1` removes the intercept and that dummy variables can be modeled with `as.factor(exog_var1)`.

### Relevance for Python implementation

Formula parsing is a high-priority compatibility point. Python should either support this formula convention or document a different interface clearly. If Python supports formula strings, it must distinguish endogenous from exogenous variables exactly and handle intercept removal deliberately.

## 3. Handling of Endogenous Variables

### R file reference

- No-exogenous branch, lines 269-407.
- Exogenous branch, `independent_P_vars <- all.vars(f1P)`, line 433.
- Multiple-endogenous example, lines 609, 734-742.

### Explanation

In the no-exogenous branch, the design matrix is built from the full formula before `|` using `model.matrix(f1P, data = data_cleaned)` (line 305). The intercept column is removed before ICA if present (lines 315-318). ICA then receives the dependent variable plus the endogenous design matrix columns (lines 318-322).

In the exogenous branch, endogenous variables are identified from the formula part before `|` and are residualized on all exogenous variables before ICA (lines 432-490).

### Relevance for Python implementation

Python should support one or more endogenous regressors and should pass `Y` plus endogenous-regressor columns to ICA. With exogenous variables, Python should residualize each endogenous regressor on the exogenous regressors before ICA, following the paper and R logic.

### Potential ambiguity

The R code uses `all.vars(f1P)` for endogenous variables (lines 297 and 433). In ordinary R formula behavior, `all.vars(Y ~ P)` includes both `Y` and `P`. Whether `nlme::splitFormula()` returns a structure that avoids this issue must be checked empirically. This is a potential source of bugs if the dependent variable is accidentally included among endogenous variables.

## 4. Handling of Exogenous Variables

### R file reference

- Exogenous branch begins at line 409.
- Missing checks for endogenous and exogenous variables, lines 414-429.
- Exogenous variable list, line 434.
- Residualization of `Y` on `X`, lines 469-472.
- Residualization of each endogenous variable on `X`, lines 474-487.
- ICA on residuals, lines 489-493.

### Explanation

When `|` is present, the code:

1. Separates endogenous and exogenous formula parts.
2. Removes rows with missing values in selected variables.
3. Builds a full design matrix for rank checks.
4. Regresses `Y` on all exogenous variables and stores residuals.
5. Regresses each endogenous variable on all exogenous variables and stores residuals.
6. Runs ICA on `cbind(Y_residuals, P_residuals)`.

This matches the paper's residualization logic for observed exogenous regressors.

### Relevance for Python implementation

This behavior should be replicated unless a documented alternative is approved. Exogenous regressors should not be included directly in the ICA matrix; they should be partialled out first.

## 5. Intercept Handling

### R file reference

- Intercept detected with `attr(terms(f1[[1]]), "intercept") == 1`, lines 266-267.
- Intercept column removed before no-exogenous ICA if present, lines 315-318.
- No-exogenous CF TRUE final regression with/without intercept, lines 339-346.
- No-exogenous CF FALSE final regression with/without intercept, lines 380-386.
- Bootstrap final regressions with/without intercept, lines 48-62, 173-181, 242-250.
- README says formula accepts `-1`, line 4.

### Explanation

The R implementation detects whether the first formula part includes an intercept. In the no-exogenous branch, it removes the intercept column from the design matrix before ICA. Final regressions include or remove the intercept according to `has_intercept`.

### Relevance for Python implementation

Python should include an intercept by default and support explicit removal only if formula parsing supports it. Intercept handling must be consistent across rank checks, ICA inputs, residualization, and final OLS.

### Potential ambiguity

For exogenous-regressor residualization, the code uses `lm(Y ~ X)` and `lm(P ~ X)`, which include intercepts by R default (lines 469-484), regardless of `has_intercept`. Whether this matches the intended behavior for formulas with `-1` should be checked.

## 6. Input Validation

### R file reference

- No-exogenous missing variable check, lines 274-280.
- No-exogenous numeric and constant checks, lines 284-294.
- Exogenous missing checks, lines 414-429.
- Exogenous numeric and constant checks, lines 436-446.

### Explanation

The code checks that required variables exist, that variables are numeric, and that variables are not constant. In the exogenous branch, the README allows `as.factor()` for dummy/factor exogenous variables, and the code only checks numeric status for `independent_P_vars` (line 437), which appears intended to require continuous endogenous variables while allowing nonnumeric/factor exogenous controls.

### Relevance for Python implementation

Python should validate:

- required variables exist,
- endogenous variables are numeric/continuous,
- constants are rejected where they make rank/ICA invalid,
- exogenous factor/dummy handling is explicit if supported.

### Potential ambiguity / bug risk

In the exogenous branch, `variables` is reassigned to `all.vars(f1X)` at line 423, then `constant_vars <- sapply(data[variables], ...)` checks only exogenous variables at line 438. The error message for nonnumeric endogenous variables also indexes `variables[!numeric_vars]` where `variables` may refer to exogenous variables (line 441). This may produce misleading validation behavior.

## 7. Missing Value Handling

### R file reference

- No-exogenous branch: select relevant variables and `na.omit()`, lines 299-302.
- Exogenous branch: select relevant variables and `na.omit()`, lines 448-452.

### Explanation

The R implementation silently drops rows with missing values in variables selected for the model.

### Relevance for Python implementation

Python should handle missing values explicitly. To match R behavior, it should drop rows with missing values in all relevant variables, but it should ideally report how many rows were removed for transparency.

## 8. Rank Checks

### R file reference

- No-exogenous main rank check, lines 304-312.
- Exogenous main rank check, lines 454-466.
- Bootstrap resampling rank loop in `boot1`, lines 20-30.
- Bootstrap resampling rank loop in `boot2`, lines 126-136.

### Explanation

The code builds a model matrix, computes `X'X`, and checks its rank using `Matrix::rankMatrix()`. If rank is deficient in the main estimation, it stops. In bootstrap functions, it repeatedly resamples until a full-rank sample is obtained.

### Relevance for Python implementation

Python should check rank before estimation and should handle rank-deficient bootstrap samples deliberately. If it resamples until full rank, it should avoid infinite loops or set a maximum retry count.

## 9. ICA Call

### R file reference

- No-exogenous main branch, lines 321-323.
- Exogenous main branch, lines 489-494.
- `boot1`, lines 34-36 and 92-94.
- `boot2`, lines 142-144 and 212-214.

### Explanation

The implementation calls:

```r
ica::ica(X = ..., nc = ncol(...), method = method)
```

The number of components equals the number of ICA input columns: dependent variable plus endogenous variables, or residualized dependent variable plus residualized endogenous variables.

### Relevance for Python implementation

Python should use the same number of components as the number of observed mixture variables. The ICA input matrix must be the correct one for the branch: raw `Y/P` when no exogenous variables exist, residualized `Y/P` when exogenous variables exist.

## 10. JADE Usage

### R file reference

- Default argument `method = "jade"`, line 261.
- ICA calls pass `method = method`, lines 35, 93, 143, 213, 322, 493.
- Paper examples use `method = "jade"` in Listings 1-2.

### Explanation

The R implementation defaults to JADE through the R `ica` package.

### Relevance for Python implementation

The current Python use of FastICA is a critical methodological difference. Python should not silently present FastICA as equivalent to JADE. This difference must be documented and later audited.

## 11. Selection of the Most Normal ICA Component

### R file reference

- No-exogenous main selection, lines 325-331.
- Exogenous main selection, lines 496-502.
- `boot1`, lines 38-44 and 96-102.
- `boot2`, lines 146-152 and 216-222.

### Explanation

For each ICA component, the code runs:

```r
ks.test(x, "pnorm", mean = mean(x), sd = sd(x))
```

It stores the KS statistic and selects the component with the smallest statistic using `which.min(ks_normality)`.

### Relevance for Python implementation

Python should mirror this component selection unless an approved change is made:

1. For every ICA component, compare to a normal distribution with that component's empirical mean and standard deviation.
2. Select the component with the smallest KS statistic.
3. Do not assume component order.

### Potential ambiguity

The identification warning later uses `ks.test(control_func, "pnorm")` without passing the component mean and standard deviation (line 577), unlike component selection. This may make the warning sensitive to component scale/location.

## 12. `CF = TRUE` Control Function Logic

### R file reference

- No-exogenous branch, lines 335-358.
- Exogenous branch, lines 505-523.
- `boot1`, lines 47-64 and 105-110.
- README, line 7.

### Explanation

When `CF == TRUE`, the selected normal ICA component is added as `control_func`, and the final regression includes it directly.

No exogenous variables:

```r
Y ~ endogenous variables + control_func
```

With exogenous variables:

```r
Y ~ endogenous variables + exogenous variables + control_func
```

### Relevance for Python implementation

This is closest to the paper's explicit control-function description. Python should replicate this as the primary paper-grounded behavior.

### Potential bug

In `boot1()` no-exogenous branch, line 35 calls `ica::ica(X = data_cleaned2, ...)`, but `data_cleaned2` is not defined inside the function. This suggests the no-exogenous `CF = TRUE` bootstrap branch may fail unless an external object exists.

## 13. `CF = FALSE` Residualization Logic

### R file reference

- No-exogenous branch, lines 359-399.
- Exogenous branch, lines 524-564.
- `boot2`, lines 155-184 and 225-253.
- README, line 7.

### Explanation

When `CF == FALSE`, the R implementation does not include `control_func` in the final regression. Instead, it first regresses each endogenous variable on `control_func`, replaces the endogenous variables by those residuals, and then estimates the final regression without `control_func`.

No exogenous variables:

```r
P_resid = residuals(P ~ control_func)
Y ~ P_resid
```

With exogenous variables:

```r
P_resid = residuals(P ~ control_func)
Y ~ P_resid + X
```

### Relevance for Python implementation

If Python supports `CF = FALSE`, it should match the R behavior only after confirming the exact R semantics. This behavior is not described explicitly in the paper and should be marked as reference-implementation behavior rather than paper-derived behavior.

### Potential bug / ambiguity

In the no-exogenous `CF = FALSE` main branch, the code assigns `control_func` to `data_cleaned1` (line 333), but then calls `lm(P ~ control_func, data = data_cleaned)` (lines 371-372). `data_cleaned` does not appear to contain `control_func`, suggesting this branch may fail. The bootstrap `boot2()` branch does add `control_func` to `data_cleaned` (line 153), so the main and bootstrap behavior differ.

## 14. Bootstrap Logic

### R file reference

- Helper `boot1()`, lines 11-116.
- Helper `boot2()`, lines 117-259.
- No-exogenous bootstrap calls, lines 351-398.
- Exogenous bootstrap calls, lines 515-563.
- Standard-error aggregation, lines 402-405 and 567-570.

### Explanation

The implementation uses row bootstrap with replacement through `sample_n(size = nrow(data), replace = TRUE)`. Bootstrap samples are redrawn until the design matrix has full rank. Each bootstrap run repeats ICA, component selection, and the corresponding `CF` logic. Standard errors are computed as the standard deviation of bootstrap estimates.

For one coefficient/vector shape case, the code uses:

```r
if (is.numeric(trapped)) { ses <- sd(trapped) } else { ses <- apply(trapped, 1, sd) }
```

Otherwise it uses `apply(trapped, 1, sd)`.

### Relevance for Python implementation

Python should rerun the full estimator inside each bootstrap sample, including ICA and component selection. It should record bootstrap failures and avoid infinite loops during rank checking.

### Potential bugs / ambiguities

- No maximum number of redraws is set for rank-deficient bootstrap samples.
- Failed ICA runs are not explicitly handled.
- Component sign/order can change across bootstrap runs; the R code relies on coefficient names/order returned by regression.
- The no-exogenous `CF = TRUE` bootstrap path may reference undefined `data_cleaned2` (line 35).

## 15. Identification Warnings

### R file reference

- Identification checks, lines 576-585.

### Explanation

After estimation, the code:

1. Runs `ks.test(control_func, "pnorm")`.
2. Warns if p-value is below `0.1`: "Joint component may not be normally distributed".
3. Checks `any(duplicated(control_func))`.
4. Warns if duplicates exist: "Endogenous regressors contain ties (repeated values)".

### Relevance for Python implementation

Python should provide identification diagnostics and warnings, but the exact R checks should be reviewed before replication. At minimum, Python should report normality diagnostics for the selected component and ties/failure indicators.

### Potential ambiguity

The warning KS test does not use empirical mean and standard deviation, unlike the component-selection KS tests. This may be R-specific or accidental. The duplicate check is applied to the recovered component but the warning text refers to endogenous regressors.

## 16. Return Values

### R file reference

- Return statement, line 587.
- Estimate matrix construction, lines 402-405 and 567-570.
- Examples access `mod[[1]]` and `mod[[2]]`, lines 612-613, 630-631, etc.

### Explanation

`ica_reg()` returns:

```r
list(Estimates1, control_func)
```

`Estimates1` is a matrix with columns:

```text
Estimate
Std. Error
```

`control_func` is the selected ICA component.

### Relevance for Python implementation

Python should return at least coefficient estimates, bootstrap standard errors, and the selected control function/component. Additional diagnostics are acceptable and probably desirable, but core outputs should remain traceable to the R return values.

## 17. Example Applications

### R file reference

- Simulated data example, lines 592-613.
- CPS1988 wage example, lines 616-631.
- ISLR Carseats example, lines 634-652.
- BostonHousing example, lines 655-668.
- OrangeJuice examples, lines 671-744.
- README example syntax, line 8.

### Explanation

The examples show:

- Multiple endogenous variables without exogenous variables (`Y ~ z1 + z2`, line 609).
- One endogenous variable with many exogenous controls (`lwage ~ education | ...`, lines 628-629).
- Multiple endogenous variables with exogenous variables (`lsales ~ lprice + lcompprice | ...`, lines 649-650).
- Factor exogenous controls via `as.factor(week)` in the OrangeJuice example (line 742).

### Relevance for Python implementation

Python should prioritize the simulation/thesis use case first, but these examples define the intended feature surface: multiple endogenous variables, exogenous controls, factor-like exogenous controls, and returning the recovered component for inspection.

## 18. Potential Bugs or Ambiguities in the R Code

### R file reference and explanation

- **Possible undefined object in `boot1()` no-exogenous branch**: `data_cleaned2` is used at line 35 but not defined in `boot1()`. This may break `CF = TRUE` bootstrapping without exogenous regressors.
- **Potential dependent-variable inclusion in endogenous lists**: `independent_vars <- all.vars(f1P)` (line 297) and `independent_P_vars <- all.vars(f1P)` (line 433) may include the dependent variable depending on how `splitFormula()` structures `f1P`.
- **No-exogenous `CF = FALSE` may miss `control_func`**: `control_func` is added to `data_cleaned1` (line 333), but residualization uses `data_cleaned` (lines 371-372), which may not include `control_func`.
- **Validation variable mismatch in exogenous branch**: `variables` is reassigned to exogenous variables (line 423), but later used in numeric/constant error handling around lines 436-446.
- **KS selection and warning use different normal references**: component selection uses empirical mean/sd (lines 326-328, 497-499), while the final warning uses default standard normal (line 577).
- **No explicit failed-ICA handling**: bootstrap and main estimation assume ICA succeeds.
- **No maximum redraw count for bootstrap rank checks**: repeat loops at lines 20-30 and 126-136 can theoretically loop indefinitely.

### Relevance for Python implementation

Python should not blindly reproduce likely bugs. For each ambiguous behavior, compare against the paper and decide whether to replicate R behavior for comparability or correct the behavior for methodological clarity.

## 19. Which Behavior Python Should Replicate

Python should replicate these methodological behaviors unless explicitly changed and documented:

- Formula concept: dependent variable, endogenous variables, optional exogenous variables separated by `|` (README lines 2-8; `ica_reg()` line 264).
- Default conceptual ICA method is JADE in the R reference (`method = "jade"`, line 261), even if Python currently uses FastICA.
- Exogenous variables are partialled out of `Y` and endogenous `P` before ICA (lines 469-490).
- ICA uses as many components as columns in the ICA input (lines 322, 493).
- The most normal component is selected by smallest KS statistic using each component's empirical mean/sd (lines 325-331, 496-502).
- `CF = TRUE` includes the selected component as a control function in final OLS (lines 335-358, 505-523).
- Bootstrap standard errors rerun the estimator including ICA and component selection (lines 351-398, 515-563).
- Return estimates, standard errors, and selected control function (line 587).

## 20. Which Behavior May Be R-Specific and Not Directly Transferable

These behaviors are R-specific or should be reconsidered in Python:

- `pacman::p_load()` package loading (lines 1-8).
- R formula parsing via `nlme::splitFormula()` and `Formula::as.Formula()`.
- `model.matrix()` factor expansion and naming.
- `lm()` default intercept behavior.
- `dplyr::sample_n()` bootstrap sampling.
- `pbapply::pbsapply()` progress bar behavior.
- Exact shape behavior of `pbsapply()` and the `is.numeric(trapped)` branch for standard-error aggregation.
- Potential bugs listed in Section 18.
- R-specific warning text, especially where it may not match the checked object.

## Paper-R Discrepancies or Extensions

- The paper describes the control-function approach explicitly: include the recovered normal component in the final regression (paper Section 3.1-3.3). The R implementation's default is `CF = FALSE`, which residualizes endogenous variables on `control_func` and excludes `control_func` from final regression. This is an implementation extension not clearly described in the paper.
- The paper examples use JADE; the R implementation also defaults to JADE, so Python FastICA is a Python-R and Python-paper deviation.
- The paper does not specify bootstrap mechanics, while the R implementation provides a specific row-bootstrap approach.
- The paper says "identify the most normal component" but does not specify the KS statistic; the R implementation operationalizes this with a KS statistic using component-specific mean and standard deviation.
