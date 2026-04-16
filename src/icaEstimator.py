
import warnings

import numpy as np
import pandas as pd
# lm() in R 
import statsmodels.api as sm
# KS-Test.
from scipy import stats
#JADE aus dem R-Code
from sklearn.decomposition import FastICA



#Implementierung der ica_reg() Funktion vom R-Code.


class ICAEstimator:
    """
    formula: Im Format 'Y ~ P1 + P2 | X1 + X2' 
    CF: True = Control_function direkt in die Regression, False = Residuen arbeiten
    n_bootstraps: Anzahl der Bootstrap-Wiederholungen 
    random_state: Seed für Reproduzierbarkeit
    """

    def __init__(self, formula: str, CF: bool = False, n_bootstraps: int = 199, random_state: int = None):

        self.formula = formula
        self.CF = CF
        self.n_bootstraps = n_bootstraps
        self.random_state = random_state

        # Variablen zum Speichern der geparsten Formel
        self.dep_var = None
        self.endog_vars = []
        self.exog_vars = []
        self.has_intercept = True

        # Formel direkt beim Initialisieren parsen
        self._parse_formula()

   
    # trennt die Formel Bestandteile vor und nach dem |
    #  soll zum Schluss so aussehen: self.dep_var = "Y" self.endog_vars = ["P1", "P2"] self.exog_vars = ["X1"]

    def _parse_formula(self):
        if "-1" in self.formula.replace(" ", "") or "- 1" in self.formula:
            self.has_intercept = False
            self.formula = self.formula.replace("-1", "").replace("- 1", "")
            
        left, right = self.formula.split('~')
        self.dep_var = left.strip()
        
        if '|' in right:
            # speichern edogene und exogene Variablen in eine Liste
            endog_part, exog_part = right.split('|')
            self.endog_vars = [v.strip() for v in endog_part.split('+') if v.strip()]
            self.exog_vars = [v.strip() for v in exog_part.split('+') if v.strip()]
        else:
            # gibt keine exogenen Kontrollvariablen, nur endogene
            self.endog_vars = [v.strip() for v in right.split('+') if v.strip()]
            self.exog_vars = []

    # führt Input-Validierungen analog zum R-Code durch
    def _validate_inputs(self, df):
        """Prüft die Eingabedaten auf fehlende, nicht-numerische oder konstante Variablen sowie den vollen Rang."""
        all_vars = [self.dep_var] + self.endog_vars + self.exog_vars
        
        missing_vars = [v for v in all_vars if v not in df.columns]
        if missing_vars:
            raise ValueError(f"Folgende Variablen fehlen im Datensatz: {', '.join(missing_vars)}")
            
        non_numeric = [v for v in all_vars if not pd.api.types.is_numeric_dtype(df[v])]
        if non_numeric:
            raise ValueError(f"Folgende Variablen sind nicht numerisch: {', '.join(non_numeric)}")
            
        constant_vars = [v for v in all_vars if df[v].nunique() <= 1]
        if constant_vars:
            raise ValueError(f"Folgende Variablen sind konstant (keine Varianz): {', '.join(constant_vars)}")
            
        feature_cols = self.endog_vars + self.exog_vars
        X_check = df[feature_cols].copy()
        if self.has_intercept:
            X_check = sm.add_constant(X_check, has_constant='add')
            
        if np.linalg.matrix_rank(X_check.values) < X_check.shape[1]:
            raise ValueError("Die Designmatrix hat keinen vollen Spaltenrang (Rank Deficient).")

    # Hilfsmethode um die Residuen zu berechnen, wollen für ICA X auschleißen, ansonsten wird X auch zerlegt (wollen wir nicht)
    # Residuum von Y: Alles an Y, was NICHT durch X erklärt werden kann, für P genauso
    def _get_residuals(self, y, X, force_intercept=True):
        # force_intercept=True stellt sicher, dass wie in R immer ein Intercept 
        # bei der Residualisierung genutzt wird.
        if force_intercept or self.has_intercept:
            X = sm.add_constant(X, has_constant='add')
        model = sm.OLS(y, X).fit()
        return model.resid

    def _run_single_estimation(self, df):
    
        # separierten Daten in Y und P schreiben
        Y = df[self.dep_var]
        P = df[self.endog_vars]
        
        # FWL-Theorem anwenden, rausrechnen von X mit Hilfsmethode siehe oben
        if len(self.exog_vars) > 0:
            X = df[self.exog_vars]
            
            # Y ~ X --> Y Residuen
            Y_res = self._get_residuals(Y, X)
            
            # P ~ X --> P Residuen
            P_res = pd.DataFrame(index=df.index)
            for p_col in self.endog_vars:
                P_res[p_col] = self._get_residuals(df[p_col], X)
                
            # Für die ICA bereinigten Daten nutzen
            ica_data = pd.concat([Y_res, P_res], axis=1)
        else:
            ica_data = pd.concat([Y, P], axis=1)

        # Durchführung der ICA auf bereinigten Daten
        # Warnungen ignorieren, da FastICA manchmal Warnungen wirft
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Modell initialisieren mit Anzahl der variablen Y und alle P
            ica = FastICA(n_components=ica_data.shape[1], random_state=self.random_state)
            # spuckt die Signale aus, eigentlicher Rechenschritt
            # die beobachteten Variablen in ica_data sind Mischungen
            # ICA versucht, die verborgenen unabhängigen Signale dahinter zu rekonstruieren
            # diese Signale landen in S
            S = ica.fit_transform(ica_data)
        
        # KS-Test, die am stärksten normalverteilte Spalte finden (ist Zufall wo die steht)
        ks_stats = []
        # über alle Spalten laufen, i sind dann die einzelen Komponenten (v und n)
        for i in range(S.shape[1]):
            # alle Zeilen aber nur Spalte i
            comp = S[:, i]
            # müssen standardisieren weil kstest das so will (arbeitet mit Standardnormalverteilung)
            comp_std = (comp - np.mean(comp)) / np.std(comp)
            # wie stark weicht comp_std von einer Normalverteilung ab, interessant ist nur die KS-Statistik, nicht der p-Wert
            stat, _ = stats.kstest(comp_std, 'norm')
            # der kleinerer Wert im Array ist näher an normalverteilt und der größere Wert weicht stärker ab
            ks_stats.append(stat)
        # unsere control_func ist die Spalte, die am stärksten normalverteilt ist 
        control_func = S[:, np.argmin(ks_stats)]

        # Start der Endogenitätskorrektur 
        X_final = df[self.endog_vars + self.exog_vars].copy()
        
        if self.CF:
            # direkte Weg CF zur Formel hinzufügen, sieht ungefähr so aus Y~ P + X + control_func (control_func als neue Spalte)
            X_final['control_func'] = control_func
        else:
            # Hier wird nicht die Kontrollfunktion direkt in die Regression gesteckt, sondern P bereinigt
            CF_df = pd.DataFrame({'control_func': control_func})
            for p_col in self.endog_vars:
                X_final[p_col] = self._get_residuals(df[p_col], CF_df)
        
        # finale Regression
        if self.has_intercept:
            X_final = sm.add_constant(X_final, has_constant='add')
            
        final_model = sm.OLS(Y, X_final).fit()
        
        # geschätzen parameter und control_func zurück geben
        return final_model.params, control_func


    # Hauptaufruf der ICA Methode mit bootstrapping Unsere control_func stand nicht einfach so im originalen Datensatz. 
    # Wir haben sie  durch die ICA geschätzt. Diese Schätzung hat eine eigene Unsicherheit (Varianz).
    # Wenn wir die control_func jetzt in die finale OLS-Regression  stecken, 
    # denkt das OLS-Modell aber, es sei eine ganz normale, zu 100 % feststehende Variable (OLS ignoriert die Unsicherheit der Vorab-Schätzung).

    def fit(self, df):

        # 0. Datensatz bereinigen (NAs entfernen) und Inputs validieren
        df = df.dropna(subset=[self.dep_var] + self.endog_vars + self.exog_vars).copy()
        self._validate_inputs(df)

        # Schätzung auf den Originaldaten (Point-Estimation)
        point_estimates, control_func = self._run_single_estimation(df)
        
        # 2. Bootstrapping (wiederholung des ganzen Ablaufs x mal)
        boot_estimates = []
        rng = np.random.default_rng(self.random_state)
        
        # brauchen die Features für den Rank-Check 
        feature_cols = self.endog_vars + self.exog_vars
        
        # eigentliche Bootstrap Schleife Matrix soll vollen Rang habe (alle Spalten eigene Informationen)
        # Sicherheitsmechanismus, dass Simulation nicht abstürtzt
        for _ in range(self.n_bootstraps):
            while True:
                # Ziehe Zufalls-Indizes
                indices = rng.choice(len(df), size=len(df), replace=True)
                df_boot = df.iloc[indices].reset_index(drop=True)
                
                # Baue Matrix um den Rang zu prüfen
                X_check = df_boot[feature_cols]
                if self.has_intercept:
                    X_check = sm.add_constant(X_check, has_constant='add')
                
                matrix_rank = np.linalg.matrix_rank(X_check.values)
                
                # Wenn Full Rank dann verlasse die Schleife!
                if matrix_rank == X_check.shape[1]:
                    break
            
            # Schätzung auf dem gültigen Bootstrap-Sample 
            boot_beta, _ = self._run_single_estimation(df_boot)
            boot_estimates.append(boot_beta)
            
        # Standardfehler aus den Bootstrap-Ergebnissen
        boot_df = pd.DataFrame(boot_estimates)
        standard_errors = boot_df.std(ddof=1)
        
        # Zusammenfassen als schönes DataFrame
        result_df = pd.DataFrame({
            'Estimate': point_estimates,
            'Std. Error': standard_errors
        })
        
        # t-Werte und p-Werte berechnen
        result_df['t value'] = result_df['Estimate'] / result_df['Std. Error']
        # 2-seitiger p-Wert
        result_df['Pr(>|t|)'] = 2 * (1 - stats.norm.cdf(np.abs(result_df['t value'])))

        # 4. Identifikations-Checks (analog zum R-Code)
        # KS-Test auf Standardnormalverteilung (Skalierung zur Sicherheit)
        cf_std = (control_func - np.mean(control_func)) / np.std(control_func)
        _, ks_p_value = stats.kstest(cf_std, 'norm')

        if ks_p_value < 0.1:
            warnings.warn(
                f"Joint component may not be normally distributed: Kolmogorov-Smirnov p = {ks_p_value:.4f}"
            )

        # Prüfung auf Duplikate (Ties)
        if len(np.unique(control_func)) < len(control_func):
            warnings.warn("Endogenous regressors contain ties (repeated values)")
        
        return result_df

