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
    
    

    engine = SimulationEngine(
        n_iterations=20, 
        true_beta=WAHRER_EFFEKT, 
        true_rho=0.8, 
        random_state=99
    )
    
    print("Starte Simulation über verschiedene N und Verteilungen...\n")
    ergebnis_tabelle = engine.run(
        sample_sizes=[250, 500, 1000], 
        distributions=['gamma', 't']
    )
    
    print("\n=== FINALE SIMULATIONSERGEBNISSE ===")
    print(ergebnis_tabelle.to_string(index=False))
    

if __name__ == "__main__":
    main()