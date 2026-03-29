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

    def run(self, sample_sizes, distributions):
        """
        Führt die Simulation für alle Kombinationen aus N und Verteilungen durch.
        
        sample_sizes: Liste von N (z.B. [250, 500, 1000])
        distributions: Liste von Verteilungen (z.B. ['gamma', 't'])
        DataFrame mit den aggregierten Ergebnissen (Bias, RMSE)
        """
        results = []
        
        # Wir durchlaufen alle gewünschten Stichprobengrößen
        for n in sample_sizes:
            # Wir durchlaufen alle gewünschten Verteilungen des Schocks
            for dist in distributions:
                
                print(f"Simuliere Szenario: N={n}, Verteilung={dist}")
                
                estimates_ols = []
                estimates_ica = []
                
                # Die eigentliche Wiederholung (tqdm macht Ladebalken)
                for i in tqdm(range(self.n_iterations)):
                    
                    # Daten neu generieren (jedes Mal leicht anders wegen neuem Seed) Zufallszahl Ziehen, daraus P und Y bauen und alles in df speichern
                    current_seed = self.random_state + i + n
                    generator = DataGenerator(
                        n_samples=n, 
                        beta=self.true_beta, 
                        rho=self.true_rho, 
                        eta_dist=dist, 
                        random_state=current_seed
                    )
                    df = generator.generate()
                    
                    # Y ~ P Regression normales OLS Modell, verzerrt wegen Endogenität. gilt einfach als Vergelichsmaßstab
                    X_ols = sm.add_constant(df[['P']])
                    model_ols = sm.OLS(df['Y'], X_ols).fit()
                    estimates_ols.append(model_ols.params['P'])
                    
                    # ICA-Schätzer (siehe icaEstimator.py))
                    estimator_ica = ICAEstimator(formula="Y ~ P", CF=False)
                    # direkter Aufruf ohne das Bootstrapping
                    beta_ica = estimator_ica._run_single_estimation(df)['P']
                    estimates_ica.append(beta_ica)
                
                
                # Bias = Durchschnittlicher Schätzwert - Wahrer Wert
                bias_ols = np.mean(estimates_ols) - self.true_beta
                bias_ica = np.mean(estimates_ica) - self.true_beta
                
                # RMSE = Wurzel aus dem durchschnittlichen quadrierten Fehler
                rmse_ols = np.sqrt(np.mean((np.array(estimates_ols) - self.true_beta)**2))
                rmse_ica = np.sqrt(np.mean((np.array(estimates_ica) - self.true_beta)**2))
                
                # Ergebnisse des Szenarios
                results.append({
                    'N': n,
                    'Verteilung_X': dist,
                    'Bias_OLS': round(bias_ols, 4),
                    'Bias_ICA': round(bias_ica, 4),
                    'RMSE_OLS': round(rmse_ols, 4),
                    'RMSE_ICA': round(rmse_ica, 4)
                })
                
        # Aus Liste von Dictionaries DataFrame machen
        return pd.DataFrame(results)
