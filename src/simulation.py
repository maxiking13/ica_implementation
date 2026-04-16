import numpy as np
import pandas as pd
import statsmodels.api as sm
from tqdm import tqdm

from data_generator import DataGenerator
from icaEstimator import ICAEstimator 

class SimulationEngine:
    
    # Art von Versuchsleiter, der die Simulation durchführt

    def __init__(self, n_iterations=100, true_beta=1.0, true_rho=0.8, random_state=42):
        """
        n_iterations: Anzahl der Durchläufe pro Szenario (z.B. 100)
        true_beta: Der wahre kausale Effekt, den die Modelle finden sollen
        true_rho: Die Stärke der Endogenität (Konfounder-Einfluss)
        """
        self.n_iterations = n_iterations
        self.true_beta = true_beta
        self.true_rho = true_rho
        self.random_state = random_state

    def run(self, sample_sizes, distribution_configs):
        """
        Führt die Simulation für alle Kombinationen aus N und Verteilungskonfigurationen durch.
        
        sample_sizes: Liste von N (z.B. [250, 500, 1000])
        distribution_configs: Liste von dicts, z.B. [{'name': 'gamma', 'params': {'shape': 1.0}}]
        Rückgabe: DataFrame mit den aggregierten Ergebnissen (Bias, RMSE, Skewness, Kurtosis)
        """
        results = []
        
        # Wir durchlaufen alle gewünschten Stichprobengrößen
        for n in sample_sizes:
            # Wir durchlaufen alle gewünschten Verteilungs-Konfigurationen
            for config in distribution_configs:
                dist_name = config['name']
                dist_params = config.get('params', {})
                
                print(f"Simuliere Szenario: N={n}, Verteilung={dist_name}, Parameter={dist_params}")
                
                estimates_ols = []
                estimates_ica = []
                skewness_list = []
                kurtosis_list = []
                
                # Die eigentliche Wiederholung (tqdm macht Ladebalken)
                for i in tqdm(range(self.n_iterations)):
                    
                    # Daten neu generieren
                    current_seed = self.random_state + i + n
                    generator = DataGenerator(
                        n_samples=n, 
                        beta=self.true_beta, 
                        rho=self.true_rho, 
                        eta_dist=dist_name, 
                        random_state=current_seed
                    )
                    
                    # Übergebe die spezifischen Parameter an den DataGenerator
                    df = generator.generate(dist_params=dist_params)
                    
                    # Speichere die empirische Schiefe und Wölbung für dieses Sample
                    skewness_list.append(df.attrs['skewness'])
                    kurtosis_list.append(df.attrs['kurtosis'])
                    
                    # Y ~ P Regression normales OLS Modell
                    X_ols = sm.add_constant(df[['P']])
                    model_ols = sm.OLS(df['Y'], X_ols).fit()
                    estimates_ols.append(model_ols.params['P'])
                    
                    # ICA-Schätzer 
                    estimator_ica = ICAEstimator(formula="Y ~ P", CF=False)
                    # WICHTIG: Tupel entpacken (_ fängt die control_func ab), da die Methode jetzt 2 Werte zurückgibt!
                    params_ica, _ = estimator_ica._run_single_estimation(df)
                    estimates_ica.append(params_ica['P'])
                
                
                # Bias und RMSE berechnen
                bias_ols = np.mean(estimates_ols) - self.true_beta
                bias_ica = np.mean(estimates_ica) - self.true_beta
                
                rmse_ols = np.sqrt(np.mean((np.array(estimates_ols) - self.true_beta)**2))
                rmse_ica = np.sqrt(np.mean((np.array(estimates_ica) - self.true_beta)**2))
                
                # Durchschnittliche Schiefe und Wölbung über alle Iterationen
                avg_skewness = np.mean(skewness_list)
                avg_kurtosis = np.mean(kurtosis_list)
                
                # Ergebnisse des Szenarios
                results.append({
                    'N': n,
                    'Verteilung_X': dist_name,
                    'Parameter': str(dist_params),
                    'Avg_Skewness': round(avg_skewness, 4),
                    'Avg_Kurtosis': round(avg_kurtosis, 4),
                    'Bias_OLS': round(bias_ols, 4),
                    'Bias_ICA': round(bias_ica, 4),
                    'RMSE_OLS': round(rmse_ols, 4),
                    'RMSE_ICA': round(rmse_ica, 4)
                })
                
        # Aus Liste von Dictionaries DataFrame machen
        return pd.DataFrame(results)
