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
        Führt die Simulation für alle Kombinationen aus N und Verteilungen durch.
        
        sample_sizes: Liste von N (z.B. [100, 250, 500])
        distribution_configs: Liste von Dictionaries mit Verteilungen und Parametern
        DataFrame mit den aggregierten Ergebnissen (Bias, RMSE)
        """
        import warnings
        
        results = []
        
        # Wir durchlaufen alle gewünschten Stichprobengrößen
        for n in sample_sizes:
            # Wir durchlaufen alle gewünschten Verteilungs-Konfigurationen
            for config in distribution_configs:
                dist_name = config['name']
                dist_params = config.get('params', {})
                
                rho_val = config.get('rho', self.true_rho) 
            
                print(f"Simuliere Szenario: N={n}, Verteilung={dist_name}, Parameter={dist_params}, Rho={rho_val}")
                
                estimates_ols = []
                estimates_ica = []
                skewness_list = []
                
                # Die eigentliche Wiederholung (tqdm macht Ladebalken)
                for i in tqdm(range(self.n_iterations)):
                    
                    # Daten neu generieren (jedes Mal leicht anders wegen neuem Seed) 
                    # Zufallszahl Ziehen, daraus P und Y bauen und alles in df speichern
                    current_seed = self.random_state + i + n
                    generator = DataGenerator(
                        n_samples=n, 
                        beta=self.true_beta, 
                        rho=rho_val,
                        eta_dist=dist_name, 
                        random_state=current_seed
                    )
                    df = generator.generate(dist_params=dist_params)
                    
                    # Speichere die empirische Schiefe für dieses Sample
                    skewness_list.append(df.attrs['skewness'])
                    
                    # Y ~ P Regression normales OLS Modell, verzerrt wegen Endogenität. gilt einfach als Vergelichsmaßstab
                    X_ols = sm.add_constant(df[['P']])
                    model_ols = sm.OLS(df['Y'], X_ols).fit()
                    estimates_ols.append(model_ols.params['P'])
                    
                    # ICA-Schätzer (siehe icaEstimator.py)
                    estimator_ica = ICAEstimator(formula="Y ~ P", CF=False)
                    
                    # Direkter Aufruf ohne das Bootstrapping (TURBO-MODUS für die Simulation)
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        try:
                            # Wir fangen die Parameter und die (hier ignorierte) control_func ab
                            params_ica, _ = estimator_ica._run_single_estimation(df)
                            estimates_ica.append(params_ica['P'])
                        except Exception:
                            # Falls ICA bei sehr kleinem N crasht (Matrix nicht vollen Rang etc.)
                            estimates_ica.append(np.nan)
                
                
                # Leere/kaputte Durchläufe (NaNs) aus der ICA-Liste filtern
                valid_ica = [x for x in estimates_ica if not np.isnan(x)]
                
                # Bias = Durchschnittlicher Schätzwert - Wahrer Wert
                bias_ols = np.mean(estimates_ols) - self.true_beta
                bias_ica = np.median(valid_ica) - self.true_beta if valid_ica else np.nan
                
                # RMSE = Wurzel aus dem durchschnittlichen quadrierten Fehler
                rmse_ols = np.sqrt(np.mean((np.array(estimates_ols) - self.true_beta)**2))
                rmse_ica = np.sqrt(np.mean((np.array(valid_ica) - self.true_beta)**2)) if valid_ica else np.nan
                
                # Ergebnisse des Szenarios
                results.append({
                    'N': n,
                    'Rho': rho_val,
                    'Verteilung_X': dist_name,
                    'Parameter': str(dist_params),
                    'Avg_Skewness': round(np.mean(skewness_list), 4),
                    'Bias_OLS': round(bias_ols, 4),
                    'Bias_ICA': round(bias_ica, 4),
                    'RMSE_OLS': round(rmse_ols, 4),
                    'RMSE_ICA': round(rmse_ica, 4)
                })
                
        # Aus Liste von Dictionaries DataFrame machen
        return pd.DataFrame(results)
