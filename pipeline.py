"""
MODULE 1 - Pipeline de donnees
==============================
Charge, nettoie et normalise les donnees statistiques ANSD sur les 14 regions
du Senegal.

Principe de fonctionnement
--------------------------
Le pipeline fonctionne en deux couches :

  1. COUCHE DE REFERENCE  (ref_*.csv, livree avec l'application)
     Valeurs calibrees sur les agregats officiels publies. Permet a
     l'application de tourner immediatement, sans aucun fichier externe.

  2. COUCHE UTILISATEUR   (./data/raw/*.csv, vos exports ANSD)
     Tout fichier depose dans data/raw/ est auto-detecte, son schema est
     reconnu par heuristique (noms de colonnes), et ses valeurs ECRASENT
     la couche de reference region par region.

Le detecteur de schema tolere : accents, majuscules, separateurs , ; ou tab,
encodages utf-8 / latin-1, espaces insecables dans les nombres, virgule
decimale francaise, et une trentaine d'alias de noms de colonnes.

Sortie
------
`charger_donnees()` retourne un objet `JeuDeDonnees` contenant trois
DataFrames indexes sur les 14 regions normalisees, plus un journal de
tracabilite indiquant l'origine de chaque bloc de donnees.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

import config

# ==========================================================================
# 1. Normalisation des libelles
# ==========================================================================

_ALIAS_REGIONS = {
    "dakar": "Dakar",
    "thies": "Thies", "thiès": "Thies", "thes": "Thies",
    "diourbel": "Diourbel",
    "kaolack": "Kaolack", "kaolak": "Kaolack",
    "saintlouis": "Saint-Louis", "saint louis": "Saint-Louis",
    "st louis": "Saint-Louis", "stlouis": "Saint-Louis",
    "saint-louis": "Saint-Louis", "ndar": "Saint-Louis",
    "louga": "Louga",
    "fatick": "Fatick",
    "tambacounda": "Tambacounda", "tamba": "Tambacounda",
    "kolda": "Kolda",
    "matam": "Matam",
    "kaffrine": "Kaffrine",
    "ziguinchor": "Ziguinchor", "zig": "Ziguinchor",
    "sedhiou": "Sedhiou", "sédhiou": "Sedhiou",
    "kedougou": "Kedougou", "kédougou": "Kedougou",
}


def sans_accent(texte: str) -> str:
    """Retire les diacritiques d'une chaine."""
    if texte is None:
        return ""
    nfkd = unicodedata.normalize("NFKD", str(texte))
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normaliser_cle(texte: str) -> str:
    """Cle de comparaison : minuscules, sans accent, sans ponctuation."""
    t = sans_accent(texte).lower().strip()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def normaliser_region(valeur: str) -> str | None:
    """
    Mappe un libelle brut vers l'une des 14 regions officielles.
    Retourne None si aucune correspondance (ligne 'Senegal', 'Total', etc.).
    """
    if valeur is None or (isinstance(valeur, float) and np.isnan(valeur)):
        return None

    cle = normaliser_cle(valeur)
    if not cle:
        return None

    # Rejet explicite des lignes d'agregat
    if cle in {"senegal", "total", "ensemble", "national", "tout senegal",
               "urbain", "rural", "autre", "non declare"}:
        return None

    # Correspondance directe
    cle_compacte = cle.replace(" ", "")
    for alias, region in _ALIAS_REGIONS.items():
        alias_compact = normaliser_cle(alias).replace(" ", "")
        if cle_compacte == alias_compact:
            return region

    # Correspondance par inclusion (ex : "Region de Thies", "DAKAR (DK)")
    for alias, region in _ALIAS_REGIONS.items():
        alias_norm = normaliser_cle(alias)
        if len(alias_norm) >= 4 and alias_norm in cle:
            return region

    # Correspondance par ville chef-lieu
    for ville, region in config.VILLES_VERS_REGION.items():
        if normaliser_cle(ville) == cle:
            return region

    return None


def nettoyer_nombre(valeur) -> float:
    """
    Convertit une valeur textuelle en float.
    Gere : espaces (dont insecables), separateurs de milliers, virgule
    decimale francaise, symboles monetaires, pourcentages, parentheses
    negatives, tirets et 'n/d' -> NaN.
    """
    if valeur is None:
        return np.nan
    if isinstance(valeur, (int, float, np.integer, np.floating)):
        return float(valeur)

    t = str(valeur).strip()
    if t == "" or t.lower() in {"n/a", "na", "nd", "n/d", "-", "--", "..", "."}:
        return np.nan

    negatif = t.startswith("(") and t.endswith(")")
    # Suppression des espaces de toute nature + symboles
    t = re.sub(r"[\s   ]", "", t)
    t = re.sub(r"(?i)(fcfa|xof|cfa|%|€|\$|tonnes?|t\b|hab\.?)", "", t)
    t = t.strip("()")

    # Determination du separateur decimal
    if "," in t and "." in t:
        # Le dernier separateur rencontre est le decimal
        if t.rfind(",") > t.rfind("."):
            t = t.replace(".", "").replace(",", ".")
        else:
            t = t.replace(",", "")
    elif "," in t:
        partie = t.split(",")[-1]
        if len(partie) == 3 and t.count(",") >= 1 and len(t.split(",")[0]) <= 3:
            # Ambigu : "1,234" -> on privilegie le millier
            t = t.replace(",", "")
        else:
            t = t.replace(",", ".")

    t = re.sub(r"[^0-9.\-]", "", t)
    if t in {"", "-", "."}:
        return np.nan

    try:
        v = float(t)
    except ValueError:
        return np.nan
    return -v if negatif else v


# ==========================================================================
# 2. Detection de schema
# ==========================================================================

# Alias -> nom canonique de colonne
_ALIAS_COLONNES = {
    # identifiant geographique
    "region": "region", "regions": "region", "nom region": "region",
    "region de residence": "region", "libelle region": "region",
    "zone": "region", "territoire": "region", "adm1": "region",
    "admin1": "region", "nom": "region", "libelle": "region",
    # Variantes AgriData / ODP : le portail translittere les accents en
    # supprimant la voyelle accentuee (region -> rgion, menage -> mnage).
    "rgion": "region", "rgions": "region", "nom rgion": "region",
    "dpartement": "region", "departement": "region",
    # population
    "population": "population", "population totale": "population",
    "population residente": "population", "effectif": "population",
    "effectifs": "population", "nombre habitants": "population",
    "habitants": "population", "pop": "population",
    "population 2023": "population", "pop totale": "population",
    "population resident total": "population",
    # superficie
    "superficie": "superficie_km2", "superficie km2": "superficie_km2",
    "surface": "superficie_km2", "aire": "superficie_km2",
    "superficie en km2": "superficie_km2",
    # densite
    "densite": "densite", "densite hab km2": "densite",
    "densite de population": "densite",
    # urbanisation
    "taux urbain": "taux_urbain_pct", "taux urbanisation": "taux_urbain_pct",
    "part urbaine": "taux_urbain_pct", "milieu urbain": "taux_urbain_pct",
    "urbain": "taux_urbain_pct", "pourcentage urbain": "taux_urbain_pct",
    # menages
    "taille menage": "taille_menage", "taille moyenne menage": "taille_menage",
    "taille des menages": "taille_menage",
    "nombre menages": "nb_menages", "menages": "nb_menages",
    # depenses
    "depense": "depense_tete", "depense par tete": "depense_tete",
    "depense annuelle": "depense_tete",
    "depense annuelle par tete": "depense_tete",
    "consommation par tete": "depense_tete",
    "depense de consommation": "depense_tete",
    "depense moyenne": "depense_tete", "dtete": "depense_tete",
    "indice depense": "indice_depense", "indice": "indice_depense",
    "part alimentation": "part_alimentation_pct",
    "coefficient budgetaire alimentation": "part_alimentation_pct",
    "alimentation": "part_alimentation_pct",
    "part logement": "part_logement_pct", "logement": "part_logement_pct",
    "part transport": "part_transport_pct", "transport": "part_transport_pct",
    "part sante": "part_sante_pct", "sante": "part_sante_pct",
    "part education": "part_education_pct", "education": "part_education_pct",
    # production agricole
    "arachide": "arachide_t", "production arachide": "arachide_t",
    "arachide tonnes": "arachide_t",
    "mil": "mil_sorgho_t", "sorgho": "mil_sorgho_t",
    "mil sorgho": "mil_sorgho_t", "cereales seches": "mil_sorgho_t",
    "riz": "riz_paddy_t", "riz paddy": "riz_paddy_t",
    "production riz": "riz_paddy_t",
    "mais": "mais_t", "production mais": "mais_t",
    "horticulture": "horticulture_t", "maraichage": "horticulture_t",
    "cultures horticoles": "horticulture_t",
    "production totale": "production_totale_t",
    "production": "production_totale_t", "tonnage": "production_totale_t",
}


def renommer_colonnes(df: pd.DataFrame) -> pd.DataFrame:
    """Renomme les colonnes vers les noms canoniques via le dictionnaire d'alias."""
    correspondances = {}
    for col in df.columns:
        cle = normaliser_cle(col)
        if cle in _ALIAS_COLONNES:
            correspondances[col] = _ALIAS_COLONNES[cle]
        else:
            # Recherche partielle : "population_totale_2023" -> population
            for alias, canon in _ALIAS_COLONNES.items():
                if len(alias) >= 5 and alias in cle:
                    correspondances[col] = canon
                    break
            else:
                correspondances[col] = cle.replace(" ", "_")
    df = df.rename(columns=correspondances)
    # Deduplication : on garde la premiere occurrence de chaque nom canonique
    return df.loc[:, ~df.columns.duplicated()]


def lire_csv_robuste(chemin: Path) -> pd.DataFrame | None:
    """Lit un CSV/TSV en essayant plusieurs encodages et separateurs."""
    if chemin.suffix.lower() in {".xls", ".xlsx"}:
        try:
            return pd.read_excel(chemin)
        except Exception:
            return None

    for encodage in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        for sep in (None, ",", ";", "\t", "|"):
            try:
                df = pd.read_csv(
                    chemin,
                    encoding=encodage,
                    sep=sep,
                    engine="python",
                    skipinitialspace=True,
                    on_bad_lines="skip",
                )
                if df.shape[1] >= 2 and len(df) >= 1:
                    return df
            except Exception:
                continue
    return None


def detecter_type(df: pd.DataFrame) -> str | None:
    """
    Devine le type de jeu de donnees a partir des colonnes presentes.
    Retourne 'population', 'depenses', 'production' ou None.
    """
    colonnes = set(df.columns)

    if colonnes & {"arachide_t", "mil_sorgho_t", "riz_paddy_t",
                   "mais_t", "horticulture_t", "production_totale_t"}:
        return "production"
    if colonnes & {"depense_tete", "indice_depense", "part_alimentation_pct",
                   "part_logement_pct", "part_transport_pct"}:
        return "depenses"
    if colonnes & {"population", "superficie_km2", "taux_urbain_pct",
                   "taille_menage", "nb_menages", "densite"}:
        return "population"
    return None


def preparer(df: pd.DataFrame) -> pd.DataFrame | None:
    """
    Nettoie un DataFrame brut : renomme les colonnes, identifie la colonne
    region, normalise les libelles, convertit les nombres, agrege les
    doublons et reindexe sur les 14 regions.
    """
    if df is None or df.empty:
        return None

    df = df.copy()
    df.columns = [str(c) for c in df.columns]
    df = renommer_colonnes(df)

    # Recherche de la colonne region
    if "region" not in df.columns:
        meilleure, meilleur_score = None, 0
        for col in df.columns:
            if df[col].dtype == object or df[col].dtype.kind in "OU":
                score = df[col].map(normaliser_region).notna().sum()
                if score > meilleur_score:
                    meilleure, meilleur_score = col, score
        if meilleure is None or meilleur_score < 5:
            return None
        df = df.rename(columns={meilleure: "region"})

    df["region"] = df["region"].map(normaliser_region)
    df = df[df["region"].notna()]
    if df.empty:
        return None

    # Conversion numerique de toutes les colonnes hors region
    for col in df.columns:
        if col != "region":
            df[col] = df[col].map(nettoyer_nombre)

    # Suppression des colonnes entierement vides
    df = df.dropna(axis=1, how="all")

    # Agregation des doublons regionaux (ex : donnees departementales)
    numeriques = [c for c in df.columns if c != "region"]
    if not numeriques:
        return None

    # Les colonnes de taux/parts se moyennent, les volumes s'additionnent
    agregations = {}
    for col in numeriques:
        if col.endswith("_pct") or col in {"taille_menage", "densite",
                                           "indice_depense", "depense_tete"}:
            agregations[col] = "mean"
        else:
            agregations[col] = "sum"

    df = df.groupby("region", as_index=False).agg(agregations)
    return df


# ==========================================================================
# 3. Structure de sortie
# ==========================================================================

@dataclass
class JeuDeDonnees:
    """Conteneur des trois DataFrames normalises + tracabilite."""

    population: pd.DataFrame
    depenses: pd.DataFrame
    production: pd.DataFrame
    journal: list[str] = field(default_factory=list)
    sources: dict[str, str] = field(default_factory=dict)

    @property
    def consolide(self) -> pd.DataFrame:
        """Vue unique fusionnant les trois blocs sur la region."""
        df = self.population.merge(self.depenses, on="region", how="left")
        df = df.merge(self.production, on="region", how="left")
        return df

    def controle_qualite(self) -> pd.DataFrame:
        """Tableau de controle : completude et coherence par bloc."""
        lignes = []
        for nom, bloc in (("Population", self.population),
                          ("Depenses", self.depenses),
                          ("Production", self.production)):
            valeurs = bloc.drop(columns=["region"], errors="ignore")
            total_cellules = valeurs.size or 1
            lignes.append({
                "Bloc": nom,
                "Regions": bloc["region"].nunique(),
                "Colonnes": valeurs.shape[1],
                "Completude (%)": round(
                    100 * valeurs.notna().sum().sum() / total_cellules, 1),
                "Source": self.sources.get(nom.lower(), "reference"),
            })
        return pd.DataFrame(lignes)


# ==========================================================================
# 4. Chargement principal
# ==========================================================================

def _charger_reference() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pop = pd.read_csv(config.REF_POPULATION)
    dep = pd.read_csv(config.REF_DEPENSES)
    prod = pd.read_csv(config.REF_PRODUCTION)
    return pop, dep, prod


def _reindexer(df: pd.DataFrame) -> pd.DataFrame:
    """Garantit exactement 14 lignes, une par region, dans l'ordre du referentiel."""
    base = pd.DataFrame({"region": config.REGIONS})
    return base.merge(df, on="region", how="left")


def _calculer_derives(pop: pd.DataFrame, dep: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calcule les colonnes derivees et recale la depense par tete sur
    l'agregat national officiel EHCVM.
    """
    pop = pop.copy()
    dep = dep.copy()

    # Densite
    if "superficie_km2" in pop.columns:
        pop["densite"] = pop["population"] / pop["superficie_km2"].replace(0, np.nan)

    # Part nationale recalculee (toujours coherente avec les populations reelles)
    total = pop["population"].sum()
    pop["part_nationale_pct"] = 100 * pop["population"] / total

    # Populations urbaine / rurale
    if "taux_urbain_pct" in pop.columns:
        pop["population_urbaine"] = pop["population"] * pop["taux_urbain_pct"] / 100
        pop["population_rurale"] = pop["population"] - pop["population_urbaine"]

    # Nombre de menages
    if "taille_menage" in pop.columns:
        pop["nb_menages"] = pop["population"] / pop["taille_menage"].replace(0, np.nan)

    # --- Depense annuelle par tete ---------------------------------------
    fusion = pop[["region", "population"]].merge(dep, on="region", how="left")

    if "depense_tete" in dep.columns and dep["depense_tete"].notna().any():
        # L'utilisateur a fourni des montants absolus : on les respecte.
        dep["depense_tete"] = dep["depense_tete"]
    else:
        # On derive les montants d'un indice, recale sur l'agregat national.
        indice = fusion["indice_depense"].fillna(1.0).to_numpy()
        poids = fusion["population"].to_numpy()
        moyenne_ponderee = np.average(indice, weights=poids)
        facteur = config.DEPENSE_ANNUELLE_TETE / moyenne_ponderee
        dep = dep.merge(fusion[["region", "indice_depense"]].rename(
            columns={"indice_depense": "_idx"}), on="region", how="left")
        dep["depense_tete"] = dep["_idx"].fillna(1.0) * facteur
        dep = dep.drop(columns=["_idx"])

    # Depense totale du marche regional
    dep = dep.merge(pop[["region", "population"]], on="region", how="left")
    dep["depense_totale_region"] = dep["depense_tete"] * dep["population"]
    dep = dep.drop(columns=["population"])

    return pop, dep


def charger_donnees(dossier_brut: Path | None = None,
                    verbose: bool = False) -> JeuDeDonnees:
    """
    Point d'entree du module 1.

    1. Charge la couche de reference.
    2. Scanne data/raw/ et ecrase les blocs correspondants.
    3. Normalise sur les 14 regions, calcule les colonnes derivees.
    """
    journal: list[str] = []
    sources = {"population": "reference (ANSD calibre)",
               "depenses": "reference (EHCVM II calibre)",
               "production": "reference (EAA/DAPSA calibre)"}

    pop, dep, prod = _charger_reference()
    journal.append("Couche de reference chargee (14 regions).")

    dossier = Path(dossier_brut) if dossier_brut else config.RAW_DIR
    if dossier.exists():
        fichiers = sorted(
            [f for f in dossier.iterdir()
             if f.suffix.lower() in {".csv", ".tsv", ".txt", ".xls", ".xlsx"}]
        )
        for fichier in fichiers:
            brut = lire_csv_robuste(fichier)
            if brut is None:
                journal.append(f"[IGNORE] {fichier.name} : format illisible.")
                continue

            propre = preparer(brut)
            if propre is None:
                journal.append(
                    f"[IGNORE] {fichier.name} : aucune colonne region exploitable.")
                continue

            type_detecte = detecter_type(propre)
            if type_detecte is None:
                journal.append(
                    f"[IGNORE] {fichier.name} : type de donnees non reconnu "
                    f"(colonnes : {', '.join(propre.columns[:6])}).")
                continue

            n = propre["region"].nunique()
            if type_detecte == "population":
                pop = _fusionner(pop, propre)
            elif type_detecte == "depenses":
                dep = _fusionner(dep, propre)
            else:
                prod = _fusionner(prod, propre)

            sources[type_detecte] = fichier.name
            journal.append(
                f"[OK] {fichier.name} -> bloc '{type_detecte}' "
                f"({n}/14 regions, {propre.shape[1] - 1} indicateurs).")
    else:
        journal.append(f"Dossier {dossier} absent : couche de reference seule.")

    # Normalisation finale
    pop = _reindexer(pop)
    dep = _reindexer(dep)
    prod = _reindexer(prod)

    # Production : total agrege
    colonnes_prod = [c for c in prod.columns if c.endswith("_t")
                     and c != "production_totale_t"]
    if colonnes_prod:
        prod["production_totale_t"] = prod[colonnes_prod].fillna(0).sum(axis=1)
    prod = prod.fillna({c: 0 for c in prod.columns if c != "region"})

    pop, dep = _calculer_derives(pop, dep)

    jeu = JeuDeDonnees(population=pop, depenses=dep, production=prod,
                       journal=journal, sources=sources)

    if verbose:
        for ligne in journal:
            print(ligne)

    return jeu


def _fusionner(reference: pd.DataFrame, utilisateur: pd.DataFrame) -> pd.DataFrame:
    """
    Ecrase les valeurs de reference par celles de l'utilisateur, colonne par
    colonne et region par region. Les valeurs manquantes cote utilisateur
    laissent la reference intacte.
    """
    fusion = reference.set_index("region")
    apport = utilisateur.set_index("region")

    for col in apport.columns:
        if col not in fusion.columns:
            fusion[col] = np.nan
        fusion[col] = apport[col].combine_first(fusion[col])

    return fusion.reset_index()


if __name__ == "__main__":
    jeu = charger_donnees(verbose=True)
    print("\n--- Controle qualite ---")
    print(jeu.controle_qualite().to_string(index=False))
    print("\n--- Population ---")
    print(jeu.population[["region", "population", "densite",
                          "part_nationale_pct"]].to_string(index=False))
    print(f"\nTotal population : {jeu.population['population'].sum():,.0f}")
    print("\n--- Depenses ---")
    print(jeu.depenses[["region", "depense_tete",
                        "depense_totale_region"]].to_string(index=False))
