import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    try:
        df = pd.read_csv("simulations_becker_fig6_full.csv")
    except FileNotFoundError:
        print("CSV nicht gefunden. Warte, bis die Simulation fertig ist!")
        return

    # Becker et al. nutzt ein sehr cleanes ggplot-artiges Design
    sns.set_theme(style="ticks", context="paper")
    plt.rcParams.update({'font.family': 'sans-serif', 'font.size': 10})

    rho_levels = sorted(df['Rho'].unique())
    distributions = ['beta', 'chisquare', 'gamma', 'lognormal', 't']
    dist_labels = ['beta', 'chisq', 'gamma', 'log-normal', 'stud_t']
    
    # R-ähnliche ggplot Farben (Rot, Grün, Blau, Lila wie im Paper)
    colors = ['#F8766D', '#7CAE00', '#00BFC4', '#C77CFF'] 

    # Wir bauen das gigantische 5x8 Grid
    fig, axes = plt.subplots(nrows=5, ncols=8, figsize=(18, 12), sharex=True, sharey='row')

    for row_idx, dist in enumerate(distributions):
        df_dist = df[df['Verteilung_X'] == dist]
        
        # Die 4 Parameter-Konfigurationen exakt in der Reihenfolge der main.py
        unique_params = df_dist['Parameter'].unique()
        
        for col_idx, rho in enumerate(rho_levels):
            ax = axes[row_idx, col_idx]
            
            # Schwarze Nulllinie wie im Paper
            ax.axhline(0, color='black', linewidth=1)
            
            for param_idx, param_str in enumerate(unique_params):
                subset = df_dist[(df_dist['Rho'] == rho) & (df_dist['Parameter'] == param_str)]
                
                if not subset.empty:
                    # Wir plotten den Bias der ICA (Relative Bias)
                    ax.plot(subset['N'], subset['Bias_ICA'], 
                            marker='o', markersize=3, 
                            color=colors[param_idx], linewidth=1.5)
            
            # X-Achse auf Log-Scale setzen, wie bei Becker!
            ax.set_xscale('log')
            
            # Y-Achsen Limits an das Original anpassen
            ax.set_ylim(-0.5, 1.0)
            
            # Spaltentitel (nur in der obersten Zeile)
            if row_idx == 0:
                ax.set_title(f"{rho}")
                
            # Zeilenbeschriftung (nur ganz rechts)
            if col_idx == 7:
                ax.set_ylabel(dist_labels[row_idx], rotation=-90, labelpad=15)
                ax.yaxis.set_label_position("right")

            # Aufräumen: Y-Achsen-Zahlen nur ganz links anzeigen
            if col_idx > 0:
                ax.tick_params(labelleft=False)

    # Globale Achsenbeschriftung
    fig.supxlabel('Sample Size (Log Scale)', fontweight='bold')
    fig.supylabel('Relative Bias of the Endogenous Regressor', fontweight='bold')
    
    # Grid eng zusammenrücken (wie im Paper)
    plt.tight_layout()
    plt.subplots_adjust(wspace=0.05, hspace=0.1) 
    
    plt.savefig('fig6_becker_replikation.pdf')
    plt.close()
    
    print("BAM! Publikationsreifer Plot in 'fig6_becker_replikation.pdf' gespeichert.")

if __name__ == "__main__":
    main()