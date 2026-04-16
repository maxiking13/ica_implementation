import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis


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
    def _generate_eta(self, dist_params=None):
        """
        Generiert die exogene, nicht-normalverteilte Komponente (eta).
        dist_params: Ein Dictionary mit Parametern wie 'shape', 'scale' oder 'df'.
        """
        if dist_params is None:
            dist_params = {}

        if self.eta_dist == "gamma":
            # Standardmäßig shape=1, scale=1, aber über dist_params anpassbar
            shape = dist_params.get("shape", 1.0)
            scale = dist_params.get("scale", 1.0)
            return self.rng.gamma(shape=shape, scale=scale, size=self.n_samples)
            
        elif self.eta_dist == "exponential":
            scale = dist_params.get("scale", 1.0)
            return self.rng.exponential(scale=scale, size=self.n_samples)
            
        elif self.eta_dist == "beta":
            a = dist_params.get("a", 2.0)
            b = dist_params.get("b", 5.0)
            return self.rng.beta(a=a, b=b, size=self.n_samples)

        elif self.eta_dist == "t":
            df = dist_params.get("df", 4)
            return self.rng.standard_t(df=df, size=self.n_samples)

        elif self.eta_dist == "uniform":
            low = dist_params.get("low", -1.0)
            high = dist_params.get("high", 1.0)
            return self.rng.uniform(low=low, high=high, size=self.n_samples)

        elif self.eta_dist == "lognormal":
            mean = dist_params.get("mean", 0.0)
            sigma = dist_params.get("sigma", 1.0)
            return self.rng.lognormal(mean=mean, sigma=sigma, size=self.n_samples)
        
        elif self.eta_dist == "f":
            # F-Verteilung (stark rechtsschief)
            dfnum = dist_params.get("dfnum", 5)
            dfden = dist_params.get("dfden", 2)
            return self.rng.f(dfnum=dfnum, dfden=dfden, size=self.n_samples)
            
        elif self.eta_dist == "chisquare":
            # Chi-Quadrat
            df = dist_params.get("df", 2)
            return self.rng.chisquare(df=df, size=self.n_samples)
            
        elif self.eta_dist == "laplace":
            # Laplace-Verteilung (symmetrisch, aber sehr spitz/hohe Kurtosis)
            scale = dist_params.get("scale", 1.0)
            return self.rng.laplace(loc=0, scale=scale, size=self.n_samples)
            
        elif self.eta_dist == "weibull":
            # Weibull-Verteilung
            a = dist_params.get("a", 1.5)
            return self.rng.weibull(a=a, size=self.n_samples)

        else:
            raise ValueError(f"Die Verteilung '{self.eta_dist}' ist in _generate_eta nicht implementiert.")

    def generate(self, dist_params=None) -> pd.DataFrame:
        xi = self.rng.standard_normal(self.n_samples)
        eta = self._generate_eta(dist_params)

        P = eta + self.rho * xi
        Y = self.alpha + self.beta * P + xi

        df = pd.DataFrame({
            "Y": Y,
            "P": P,
            "true_xi": xi,
            "true_eta": eta,
        })

        df.attrs['skewness'] = skew(P)
        df.attrs['kurtosis'] = kurtosis(P, fisher=True) # Fisher=True gibt Excess Kurtosis (Normalverteilung = 0)

        return df