import statsmodels.api as sm
from data_generator import DataGenerator
from icaEstimator import ICAEstimator
from simulation import SimulationEngine


def main():
 
    
    # kausaler Effekt
    WAHRER_EFFEKT = 1.0 
    
    # 1. Daten generieren
    generator = DataGenerator(
        n_samples=500,
        beta=WAHRER_EFFEKT, 
        rho=0.8,           
        eta_dist="gamma",   
        random_state=42
    )
    df_simulated = generator.generate()
    
    print("\n1. Datensatz erfolgreich generiert! Erste 5 Zeilen:")
    print(df_simulated.head())
    
 
    print("\n2. Berechne naives OLS Modell...")
    X_ols = sm.add_constant(df_simulated[['P']])
    model_ols = sm.OLS(df_simulated['Y'], X_ols).fit()
    bias_ols = model_ols.params['P'] - WAHRER_EFFEKT
    print(f"   OLS Schätzung für P: {model_ols.params['P']:.4f} (Bias: {bias_ols:+.4f})")


    # ICA-Estimator anwenden
    print("\n3. Wende ICA-Estimator an (inkl. 100 Bootstrap-Durchläufe)...")
    estimator = ICAEstimator(formula="Y ~ P", CF=False, n_bootstraps=100, random_state=42)
    
    # .fit() führt die Point-Estimation und das Bootstrapping durch
    ica_results = estimator.fit(df_simulated)
    
    print("\n   ICA-Estimator Ergebnisse:")
    print(ica_results.round(4))
    bias_ica = ica_results.loc['P', 'Estimate'] - WAHRER_EFFEKT
    print(f"\n   -> Erfolg: Die ICA-Schätzung liegt viel näher am wahren Wert (Bias: {bias_ica:+.4f})")
    
    

    N_LIST = [100, 200, 400, 800, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]

    DIST_CONFIGS = [
        {'name': 'gamma', 'params': {'shape': 1.0, 'scale': 1.0}},      # Extrem schief
        {'name': 'gamma', 'params': {'shape': 5.0, 'scale': 1.0}},      # Moderat schief
        {'name': 'exponential', 'params': {'scale': 1.0}},             # Stark schief
        {'name': 'beta', 'params': {'a': 0.5, 'b': 0.5}},             # U-förmig
        {'name': 'f', 'params': {'dfnum': 5, 'dfden': 2}},             # Langer rechter Rand
        {'name': 'chisquare', 'params': {'df': 1}},                    # Extrem spitz/schief
        {'name': 'laplace', 'params': {'scale': 1.0}},                 # Symmetrisch, hohe Kurtosis
        {'name': 'weibull', 'params': {'a': 0.5}},                     # Stark abfallend
    ]

    # 2. SimulationEngine mit mehr Iterationen für stabilere Ergebnisse
    engine = SimulationEngine(n_iterations=100, true_beta=WAHRER_EFFEKT, random_state=99)
    
    print(f"Starte Groß-Simulation über {len(N_LIST)} Stichprobengrößen und {len(DIST_CONFIGS)} Verteilungen...\n")
    
    ergebnis_tabelle = engine.run(
        sample_sizes=N_LIST, 
        distribution_configs=DIST_CONFIGS
    )
    
    # 3. Ergebnisse anzeigen und als CSV für die Auswertung speichern
    print("\n=== FINALE SIMULATIONSERGEBNISSE ===")
    print(ergebnis_tabelle.head(20).to_string(index=False)) # Zeige die ersten 20 Zeilen
    
    # Speichere die Daten für deine Graphen/Plots
    ergebnis_tabelle.to_csv("simulations_ergebnisse_gross.csv", index=False)
    print("\nErgebnisse wurden in 'simulations_ergebnisse_gross.csv' gespeichert.")
    

if __name__ == "__main__":
    main()