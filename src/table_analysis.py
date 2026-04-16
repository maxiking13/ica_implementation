import pandas as pd

def main():
    try:
        df = pd.read_csv("simulations_ergebnisse_gross.csv")
    except FileNotFoundError:
        print("Datei nicht gefunden.")
        return

    # 1. FIX: Wir erzeugen eine eindeutige ID aus Verteilung und den fixen Parametern
    df['Config_ID'] = df['Verteilung_X'] + " | " + df['Parameter']
    
    # 2. Wir berechnen die DURCHSCHNITTLICHE Schiefe für diese Konfiguration über alle N
    mean_skew = df.groupby('Config_ID')['Avg_Skewness'].mean().round(2)
    
    # 3. Jetzt bauen wir den stabilen Namen für die Spalten
    df['Szenario'] = df.apply(lambda row: f"{row['Verteilung_X']} (Mean Skew: {mean_skew[row['Config_ID']]})", axis=1)

    # 4. Pivot-Tabellen erstellen (Jetzt klappt es ohne NaNs!)
    pivot_ols = df.pivot(index='N', columns='Szenario', values='Bias_OLS')
    pivot_ica = df.pivot(index='N', columns='Szenario', values='Bias_ICA')

    # Pandas-Einstellungen für eine schöne Konsolenausgabe
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 200)
    pd.set_option('display.float_format', '{:+.4f}'.format)

    print("\n" + "="*80)
    print("1. OLS BIAS (Verzerrung ohne Korrektur)")
    print("="*80)
    print(pivot_ols)

    print("\n" + "="*80)
    print("2. ICA BIAS (Fehler nach Endogenitätskorrektur)")
    print("="*80)
    print(pivot_ica)

    # Zusammenfassung für das Flowchart
    print("\n" + "="*80)
    print("3. STATISTISCHE EIGENSCHAFTEN DER SZENARIEN")
    print("="*80)
    stats_df = df.groupby('Config_ID').agg({
        'Verteilung_X': 'first',
        'Parameter': 'first',
        'Avg_Skewness': 'mean',
        'Avg_Kurtosis': 'mean'
    }).round(4).sort_values(by='Avg_Skewness', ascending=False)
    
    pd.reset_option('display.float_format') 
    print(stats_df[['Verteilung_X', 'Parameter', 'Avg_Skewness', 'Avg_Kurtosis']].to_string(index=False))

if __name__ == "__main__":
    main()