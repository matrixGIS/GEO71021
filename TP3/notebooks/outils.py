"""Fonctions utilitaires du laboratoire « séries temporelles ».
Les étudiants n'ont pas à modifier ce fichier : il cache la plomberie pour garder les notebooks courts."""
from pathlib import Path
import numpy as np, pandas as pd, matplotlib.pyplot as plt

DOSSIER = Path(__file__).resolve().parent.parent / "formatted_data"
plt.rcParams.update({"figure.dpi": 100, "axes.grid": True, "grid.alpha": .3, "figure.figsize": (9, 3.6)})

# ---------------------------------------------------------------- lecture
def lire(station):
    """station : 'PaP', 'MJ', 'Comi' ou 'Neigette'."""
    f = {"PaP": "PaP_7056068_horaire.csv", "MJ": "MontJoli_7055122_horaire.csv",
         "Comi": "MontComi_15min.csv", "Neigette": "Neigette_021916_quotidien.csv"}[station]
    col = "date" if station == "Neigette" else "date_utc"
    return pd.read_csv(DOSSIER / f, parse_dates=[col], low_memory=False).set_index(col)

# ---------------------------------------------------------------- partie 1
def moyennes(serie, freq="MS", completude=0.8):
    """Moyennes par période ; NaN si moins de `completude` des valeurs sont présentes."""
    m = serie.resample(freq).mean()
    m[serie.resample(freq).count() < completude * serie.resample(freq).size()] = np.nan
    return m

def matrice(serie):
    """Matrice année × jour de l'année."""
    return serie.to_frame("v").assign(an=serie.index.year, j=serie.index.dayofyear).pivot_table(index="an", columns="j", values="v")

def ccf(x, y, decalages=range(-6, 7)):
    """Corrélation croisée ; décalage > 0 : y en retard sur x."""
    x, y = pd.Series(np.asarray(x, float)), pd.Series(np.asarray(y, float))
    return pd.Series([x.corr(y.shift(-k)) for k in decalages], index=list(decalages))

def preblanchir(x, y, p=None):
    """Ajuste un AR(p) sur x et applique le même filtre à x et y."""
    from statsmodels.tsa.ar_model import AutoReg, ar_select_order
    x, y = np.asarray(x, float), np.asarray(y, float)
    p = p or len(ar_select_order(x, maxlag=10, ic="bic").ar_lags)
    phi = AutoReg(x, lags=p).fit().params
    f = lambda v: v[p:] - sum(phi[i] * v[p - i:len(v) - i] for i in range(1, p + 1))
    return f(x), f(y), p

# ---------------------------------------------------------------- partie 2
def seuil(D):
    """Seuil intensité-durée (Boulet et al., 2022) : I (mm/h) = 10,5 · D(h)^-0,58."""
    return 10.5 * np.asarray(D, float) ** -0.58

def delimiter(p, T=None, mit=24, pmin=0.0):
    """Délimite les événements de pluie d'une série horaire p (mm).
    mit  : nombre d'heures sans pluie qui séparent deux événements.
    pmin : les heures avec p <= pmin comptent comme « sèches » (évite qu'une bruine allonge l'événement)."""
    p = p.asfreq("h")
    sig = p[p > pmin].dropna()
    num = (sig.index.to_series().diff() > pd.Timedelta(hours=mit)).cumsum().values
    lignes = []
    for _, g in sig.groupby(num):
        seg = p[g.index[0]:g.index[-1]]
        d = dict(debut=g.index[0], fin=g.index[-1], D=len(seg), P=seg.sum(), Imax=seg.max())
        if T is not None: d["T_moy"] = T.reindex(seg.index).mean()
        lignes.append(d)
    E = pd.DataFrame(lignes)
    E["I"] = E.P / E.D
    E["depasse"] = E.I > seuil(E.D)
    return E

def annee_pont(t):
    """Année débutant le 12 septembre (date d'installation du nouveau pont)."""
    t = pd.DatetimeIndex(t)
    return np.asarray(t.year - ((t.month < 9) | ((t.month == 9) & (t.day < 12))))

# ---------------------------------------------------------------- choix des étudiants
import re as _re

def _mmjj(v):
    return isinstance(v, str) and _re.fullmatch(r"(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])", v) is not None

# règle de validation et texte d'aide pour chaque paramètre
CHOIX = {
    "VARIABLE": (lambda v: v in ["temp_surface_sol_C", "temp_sol_C", "hr_pct", "vent_vit_ms"],
                 '"temp_surface_sol_C", "temp_sol_C", "hr_pct" ou "vent_vit_ms"'),
    "COUVERTURE": (lambda v: isinstance(v, (int, float)) and 0.5 <= v <= 1.0, "un nombre entre 0.5 et 1.0"),
    "AGREGATION": (lambda v: v in ["annuelle", "mensuelle"], '"annuelle" ou "mensuelle"'),
    "TEST": (lambda v: v in ["original", "hamed_rao", "saisonnier", "saisonnier_correle"],
             '"original", "hamed_rao", "saisonnier" ou "saisonnier_correle"'),
    "MOIS": (lambda v: v in ["mai-oct", "annee"], '"mai-oct" ou "annee"'),
    "PREBLANCHIR": (lambda v: v in [True, False], "True ou False"),
    "FENETRE_DEBUT": (_mmjj, 'une date "mm-jj" (p. ex. "02-01")'),
    "FENETRE_FIN": (lambda v: v == "pic" or _mmjj(v), 'une date "mm-jj" ou "pic"'),
    "SEC": (lambda v: v in [6, 12, 24], "6, 12 ou 24"),
    "PMIN": (lambda v: v in [0, 0.1, 0.2, 0.5], "0, 0.1, 0.2 ou 0.5"),
    "T_PLUIE": (lambda v: v in [0, 1, 2, 3], "0, 1, 2 ou 3"),
    "IMAX_PLAUSIBLE": (lambda v: v == "aucun" or (isinstance(v, (int, float)) and v > 0), 'un nombre positif (mm) ou "aucun"'),
    "DEBUT_REFERENCE": (lambda v: isinstance(v, int) and 2004 <= v <= 2015, "une année entière entre 2004 et 2015"),
    "TEST_TAUX": (lambda v: v in ["poisson", "mann-whitney"], '"poisson" ou "mann-whitney"'),
}
CHOIX["COMPLETUDE"], CHOIX["MIT"] = CHOIX["COUVERTURE"], CHOIX["SEC"]     # anciens noms, toujours acceptés

class ChoixManquant(Exception):
    pass

def verifier(**parametres):
    """Vérifie que chaque paramètre est défini et permis ; affiche le résumé des choix."""
    for nom, val in parametres.items():
        regle, aide = CHOIX[nom]
        if val is None:
            raise ChoixManquant(f"Définissez {nom} avant d'exécuter ({aide}).")
        if not regle(val):
            raise ChoixManquant(f"{nom} = {val!r} n'est pas permis : {aide}.")
    if parametres.get("AGREGATION") == "annuelle" and str(parametres.get("TEST", "")).startswith("saisonnier"):
        raise ChoixManquant("Un test saisonnier demande des données mensuelles (AGREGATION = 'mensuelle').")
    deb, fin = parametres.get("FENETRE_DEBUT"), parametres.get("FENETRE_FIN")
    if deb and fin and fin != "pic" and fin <= deb:
        raise ChoixManquant("FENETRE_FIN doit être après FENETRE_DEBUT.")
    print("Choix retenus :", ", ".join(f"{k} = {v}" for k, v in parametres.items()))

def mann_kendall(serie, test):
    """Applique la variante choisie du test de Mann-Kendall (bibliothèque pymannkendall)."""
    import pymannkendall as mk
    f = {"original": mk.original_test, "hamed_rao": mk.hamed_rao_modification_test,
         "saisonnier": lambda x: mk.seasonal_test(x, period=12),
         "saisonnier_correle": lambda x: mk.correlated_seasonal_test(x, period=12)}[test]
    return f(serie.values)
