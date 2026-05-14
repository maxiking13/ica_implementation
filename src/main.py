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
    
    

  # === FOKUS-SIMULATION: EXAKTE REPLIKATION VON BECKER FIG 6 ===
    
    # 1. Die X-Achse (Stichprobengrößen)
    N_LIST = [100, 200, 400, 1000, 4000, 10000]

    # 2. Die Spalten (Endogenitäts-Level rho)
    RHO_LIST = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

    # 3. Die Basis-Verteilungen (Die Zeilen und Farben im Paper)
    BASE_DIST_CONFIGS = [
        # BETA-Verteilung (p, q)
        {'name': 'beta', 'params': {'a': 0.5, 'b': 0.5}},
        {'name': 'beta', 'params': {'a': 1.0, 'b': 1.0}},
        {'name': 'beta', 'params': {'a': 2.0, 'b': 2.0}},
        {'name': 'beta', 'params': {'a': 4.0, 'b': 4.0}},

        # CHI-QUADRAT-Verteilung (df)
        {'name': 'chisquare', 'params': {'df': 2}}, 
        {'name': 'chisquare', 'params': {'df': 8}}, 
        {'name': 'chisquare', 'params': {'df': 14}},
        {'name': 'chisquare', 'params': {'df': 20}},

        # GAMMA-Verteilung (shape, scale)
        {'name': 'gamma', 'params': {'shape': 1.0, 'scale': 0.5}},
        {'name': 'gamma', 'params': {'shape': 1.0, 'scale': 2.0}},
        {'name': 'gamma', 'params': {'shape': 2.0, 'scale': 4.0}},
        {'name': 'gamma', 'params': {'shape': 4.0, 'scale': 2.0}},

        # LOGNORMAL-Verteilung (mean, sigma)
        {'name': 'lognormal', 'params': {'mean': 0.0, 'sigma': 1.0}},
        {'name': 'lognormal', 'params': {'mean': 0.0, 'sigma': 0.75}},
        {'name': 'lognormal', 'params': {'mean': 0.0, 'sigma': 0.50}},
        {'name': 'lognormal', 'params': {'mean': 0.0, 'sigma': 0.25}},

        # STUDENT-T-Verteilung (df)
        {'name': 't', 'params': {'df': 3}},
        {'name': 't', 'params': {'df': 4}},
        {'name': 't', 'params': {'df': 5}},
        {'name': 't', 'params': {'df': 6}},
    ]

    # Wir bauen jetzt dynamisch alle Kombinationen aus Verteilung und Rho zusammen
    DIST_CONFIGS = []
    for rho in RHO_LIST:
        for config in BASE_DIST_CONFIGS:
            new_config = config.copy()
            new_config['rho'] = rho  # Wir fügen das spezifische rho in das config-Dictionary ein
            DIST_CONFIGS.append(new_config)

    engine = SimulationEngine(
        n_iterations=500,
        true_beta=WAHRER_EFFEKT, 
        random_state=99
    )
    
    total_scenarios = len(N_LIST) * len(DIST_CONFIGS)
    print(f"\nStarte GROSSE Replikation von Becker Fig. 6...")
    print(f"Berechne {total_scenarios} Szenarien. Das kann ein paar Minuten dauern...\n")
    
    ergebnis_tabelle = engine.run(
        sample_sizes=N_LIST, 
        distribution_configs=DIST_CONFIGS
    )
    
    # Speichere die riesige Tabelle
    ergebnis_tabelle.to_csv("simulations_becker_fig6_full.csv", index=False)
    print("\nErgebnisse wurden in 'simulations_becker_fig6_full.csv' gespeichert.")
    

if __name__ == "__main__":
    main()