import numpy as np
import pandas as pd


class DataGenerator:
    """
    Diese Klasse simuliert den Datengenerierungsprozess (DGP) basierend auf dem 
    Paper von Dost & Haschka (2025). 
    Wenn wir später ein Objekt dieser Klasse 
    erstellen, können wir die Parameter für unsere Simulationen flexibel anpassen.
    """

    # Die __init__ Methode ist der "Konstruktor". Sie wird automatisch aufgerufen, 
    # sobald wir einen neuen DataGenerator erstellen. Hier legen wir die 
    # Startbedingungen (Parameter) für unsere Simulation fest.
    def __init__(
        self,
        n_samples=1000,
        alpha=2.0,
        beta=1.0,
        rho=0.8,
        eta_dist="gamma",
        random_state=None,
    ):
        # n_samples (N): Die Anzahl der Beobachtungen (Zeilen in unserer Tabelle)
        self.n_samples = n_samples

        # alpha: Der wahre Achsenabschnitt (Intercept) unserer Y-Gleichung. Im Paper alpha = 2
        self.alpha = alpha

        # beta: Der wahre kausale Effekt von P auf Y. Das ist die Zahl, die uns interessiert
        self.beta = beta

        # rho: Steuert die Stärke der Endogenität. Je höher rho, desto stärker ist der Regressor P mit dem Störterm korreliert
        self.rho = rho

        # eta_dist: Ein Text-String, der angibt, welche Verteilung die exogene Komponente haben soll. 
        self.eta_dist = eta_dist

        #In Simulationen wollen wir Ergebnisse oft reproduzieren un immer exakt diesselbe Zufallszahl generieren
        self.rng = np.random.default_rng(random_state)


    """
    Generiert die exogene, zwingend NICHT-normalverteilte Komponente (eta).
    Das ist der 'gute' Teil unseres Regressors P.
    """
    def _generate_eta(self):
        if self.eta_dist == "gamma":
            return self.rng.gamma(shape=1.0, scale=1.0, size=self.n_samples)
        elif self.eta_dist == "t":
            return self.rng.standard_t(df=4, size=self.n_samples)
        elif self.eta_dist == "uniform":
            return self.rng.uniform(low=-1.0, high=1.0, size=self.n_samples)
        else:
            raise ValueError(
                f"Die Verteilung '{self.eta_dist}' ist noch nicht implementiert."
            )

    def generate(self) -> pd.DataFrame:
        xi = self.rng.standard_normal(self.n_samples)
        eta = self._generate_eta()

        P = eta + self.rho * xi
        Y = self.alpha + self.beta * P + xi

        return pd.DataFrame(
            {
                "Y": Y,
                "P": P,
                "true_xi": xi,
                "true_eta": eta,
            }
        )