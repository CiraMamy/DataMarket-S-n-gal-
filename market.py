"""
MODULE 2 - Calculateur TAM / SAM / SOM
======================================

Definitions retenues
--------------------
TAM (Total Addressable Market)
    Depense annuelle totale, sur l'ensemble du perimetre geographique
    considere, sur le poste de consommation adresse par le secteur.
        TAM = population cible x depense annuelle par tete sur le poste

SAM (Serviceable Available Market)
    Sous-ensemble du TAM effectivement atteignable compte tenu de la zone
    de chalandise reelle, du format de commerce et du segment vise.
        SAM = TAM x part_geographique x part_segment

SOM (Serviceable Obtainable Market)
    Chiffre d'affaires realistement capturable a horizon 3 ans compte tenu
    de la concurrence, du capital investi et de la capacite d'execution.
        SOM = SAM x part_de_marche_visee

Chaque calcul est trace : le dictionnaire `hypotheses` retourne l'integralite
des coefficients utilises, de sorte qu'aucun chiffre n'est une boite noire.

Les trois secteurs modelises
----------------------------
  commerce_proximite  : superette / boutique de quartier
  restauration_sante  : restauration a indice glycemique maitrise (diabete)
  agrobusiness        : transformation agroalimentaire
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

import config
from pipeline import JeuDeDonnees


# ==========================================================================
# Structure de resultat
# ==========================================================================

@dataclass
class ResultatMarche:
    """Resultat complet d'une etude TAM/SAM/SOM."""

    secteur: str
    libelle: str
    regions: list[str]
    tam: float
    sam: float
    som: float
    population_cible: int
    detail_regional: pd.DataFrame
    hypotheses: dict = field(default_factory=dict)
    avertissements: list[str] = field(default_factory=list)
    provenance: dict = field(default_factory=dict)

    @property
    def perimetre(self) -> str:
        if len(self.regions) == 14:
            return "National (14 régions)"
        return ", ".join(config.REGIONS_AFFICHAGE.get(r, r) for r in self.regions)

    @property
    def ca_mensuel_som(self) -> float:
        return self.som / 12

    def clients_potentiels(self) -> float | None:
        """Nombre de transactions annuelles implicites, si un ticket est defini."""
        ticket = self.hypotheses.get("ticket_moyen_fcfa", 0)
        if not ticket:
            return None
        return self.som / ticket

    def resume(self) -> dict:
        return {
            "Secteur": self.libelle,
            "Périmètre": self.perimetre,
            "Population cible": self.population_cible,
            "TAM": self.tam,
            "SAM": self.sam,
            "SOM": self.som,
            "CA mensuel visé": self.ca_mensuel_som,
        }

    def tableau_synthese(self) -> pd.DataFrame:
        lignes = [
            {
                "Indicateur": "TAM",
                "Définition": "Marché total adressable",
                "Montant (FCFA)": self.tam,
                "Montant lisible": config.formater_fcfa(self.tam),
                "% du TAM": 100.0,
            },
            {
                "Indicateur": "SAM",
                "Définition": "Marché accessible (zone + segment)",
                "Montant (FCFA)": self.sam,
                "Montant lisible": config.formater_fcfa(self.sam),
                "% du TAM": 100 * self.sam / self.tam if self.tam else 0,
            },
            {
                "Indicateur": "SOM",
                "Définition": "Marché captable à 3 ans",
                "Montant (FCFA)": self.som,
                "Montant lisible": config.formater_fcfa(self.som),
                "% du TAM": 100 * self.som / self.tam if self.tam else 0,
            },
        ]
        return pd.DataFrame(lignes)


# ==========================================================================
# Fonctions de segmentation par secteur
# ==========================================================================

def _base_regionale(jeu: JeuDeDonnees, regions: list[str]) -> pd.DataFrame:
    """Assemble population + depenses + production pour les regions retenues."""
    df = jeu.consolide.copy()
    df = df[df["region"].isin(regions)].reset_index(drop=True)
    if df.empty:
        raise ValueError(f"Aucune region valide parmi : {regions}")
    return df


def _tam_commerce_proximite(df: pd.DataFrame, p: dict) -> pd.DataFrame:
    """
    Panier alimentaire + hygiene/entretien, pondere par le taux de captation
    du commerce de detail organise (plus eleve en urbain).
    """
    df = df.copy()

    depense_alimentaire = df["depense_tete"] * df["part_alimentation_pct"] / 100
    # Le panier d'une superette inclut l'hygiene et l'entretien
    panier = depense_alimentaire * (1 + p["part_hygiene_entretien"])

    captation = (
        df["population_urbaine"] * p["captation_urbain"]
        + df["population_rurale"] * p["captation_rural"]
    ) / df["population"]

    df["population_cible"] = df["population"]
    df["depense_cible_tete"] = panier * captation
    df["tam_region"] = df["population_cible"] * df["depense_cible_tete"]
    return df


def _tam_restauration_sante(df: pd.DataFrame, p: dict) -> pd.DataFrame:
    """
    Cible : adultes urbains concernes par le diabete ou le prediabete,
    solvables pour la restauration hors domicile.
    """
    df = df.copy()

    prevalence_totale = p["prevalence_diabete"] + p["prevalence_prediabete"]

    adultes_urbains = df["population_urbaine"] * p["part_adultes_25_plus"]
    cible = adultes_urbains * prevalence_totale * p["coefficient_solvabilite"]

    depense_alimentaire = df["depense_tete"] * df["part_alimentation_pct"] / 100
    depense_resto = depense_alimentaire * p["part_restauration_hors_domicile"]

    df["population_cible"] = cible
    df["depense_cible_tete"] = depense_resto
    df["tam_region"] = df["population_cible"] * df["depense_cible_tete"]
    return df


def _tam_agrobusiness(df: pd.DataFrame, p: dict) -> pd.DataFrame:
    """
    Double approche :
      - Aval : demande interne en produits alimentaires transformes.
      - Amont : valeur de la production agricole regionale non encore
        transformee localement (gisement de matiere premiere).
    Le TAM retenu est la demande aval, borne par le gisement amont lorsque
    celui-ci est le facteur limitant.
    """
    df = df.copy()

    depense_alimentaire = df["depense_tete"] * df["part_alimentation_pct"] / 100
    demande_transforme = depense_alimentaire * p["part_produits_transformes"]

    df["population_cible"] = df["population"]
    df["depense_cible_tete"] = demande_transforme
    df["tam_demande"] = df["population_cible"] * df["depense_cible_tete"]

    # Gisement amont : production non transformee x valorisation
    production = df.get("production_totale_t", pd.Series(0, index=df.index)).fillna(0)
    df["gisement_amont"] = (
        production
        * (1 - p["taux_transformation_actuel"])
        * p["prix_moyen_tonne_fcfa"]
    )

    # Le marche reel est borne par le plus contraignant des deux cotes
    df["tam_region"] = np.minimum(df["tam_demande"], df["gisement_amont"])
    # Si une region n'a aucune production, le potentiel de transformation
    # locale est nul meme si la demande existe (approvisionnement externe).
    df.loc[production <= 0, "tam_region"] = 0.0
    return df


_MOTEURS = {
    "commerce_proximite": _tam_commerce_proximite,
    "restauration_sante": _tam_restauration_sante,
    "agrobusiness": _tam_agrobusiness,
}

# Coefficients HYP les plus incertains de chaque secteur (cf. config.SECTEURS
# et DATA_MAPPING.md) : ce sont eux qui font l'objet de l'analyse de
# sensibilite, plutot qu'une marge arbitraire appliquee au TAM lui-meme.
_COEFFICIENTS_SENSIBLES = {
    "commerce_proximite": ["captation_urbain", "captation_rural"],
    "restauration_sante": ["prevalence_diabete", "prevalence_prediabete",
                           "coefficient_solvabilite"],
    "agrobusiness": ["part_produits_transformes"],
}


# ==========================================================================
# Calcul principal
# ==========================================================================

def calculer(
    jeu: JeuDeDonnees,
    secteur: str,
    regions: list[str] | None = None,
    part_geographique: float | None = None,
    part_marche_visee: float | None = None,
    budget: float | None = None,
    facteur_sensibilite: float = 1.0,
) -> ResultatMarche:
    """
    Calcule TAM / SAM / SOM pour un secteur et un perimetre donnes.

    Parametres
    ----------
    jeu : JeuDeDonnees
        Sortie du module 1.
    secteur : str
        Cle dans config.SECTEURS.
    regions : list[str] | None
        Regions retenues. None = les 14 regions.
    part_geographique : float | None
        Part du TAM reellement couverte par la zone de chalandise (0-1).
        None = valeur par defaut du secteur.
    part_marche_visee : float | None
        Part du SAM visee a 3 ans (0-1). None = valeur par defaut.
    budget : float | None
        Capital disponible en FCFA. S'il est renseigne, il module la part
        de marche atteignable (un budget inferieur au capex minimal reduit
        proportionnellement l'ambition).
    facteur_sensibilite : float
        Multiplie le(s) coefficient(s) HYP les plus incertains du secteur
        (_COEFFICIENTS_SENSIBLES). 1.0 = valeurs de reference. Utilise par
        fourchette() pour produire un TAM bas/central/haut ; n'a aucun
        effet sur les autres hypotheses (zone de chalandise, part visee).

    Retourne
    --------
    ResultatMarche
    """
    if secteur not in config.SECTEURS:
        raise KeyError(
            f"Secteur inconnu : '{secteur}'. "
            f"Valeurs admises : {list(config.SECTEURS)}"
        )

    p = dict(config.SECTEURS[secteur])
    if facteur_sensibilite != 1.0:
        for cle in _COEFFICIENTS_SENSIBLES.get(secteur, []):
            if cle in p:
                p[cle] = min(max(p[cle] * facteur_sensibilite, 0.0), 1.0)

    regions = list(regions) if regions else list(config.REGIONS)
    regions = [r for r in regions if r in config.REGIONS]
    if not regions:
        regions = list(config.REGIONS)

    avertissements: list[str] = []

    df = _base_regionale(jeu, regions)
    df = _MOTEURS[secteur](df, p)

    tam = float(df["tam_region"].sum())
    population_cible = int(round(float(df["population_cible"].sum())))

    # --- SAM -------------------------------------------------------------
    part_geo = p["sam_defaut"] if part_geographique is None else float(part_geographique)
    part_geo = min(max(part_geo, 0.0), 1.0)
    sam = tam * part_geo

    # --- SOM -------------------------------------------------------------
    part_som = p["som_defaut"] if part_marche_visee is None else float(part_marche_visee)
    part_som = min(max(part_som, 0.0), 1.0)

    coefficient_budget = 1.0
    capex_min = p.get("capex_min_fcfa", 0)
    if budget is not None and capex_min:
        if budget < capex_min:
            coefficient_budget = max(budget / capex_min, 0.05)
            avertissements.append(
                f"Budget de {config.formater_fcfa(budget)} inférieur au capital "
                f"minimal observé pour ce secteur ({config.formater_fcfa(capex_min)}). "
                f"La part de marché atteignable est réduite d'un facteur "
                f"{coefficient_budget:.2f}."
            )
        elif budget > capex_min * 3:
            coefficient_budget = min(1 + 0.15 * np.log(budget / capex_min), 1.6)

    part_som_effective = min(part_som * coefficient_budget, 1.0)
    som = sam * part_som_effective

    # --- Detail regional -------------------------------------------------
    df["sam_region"] = df["tam_region"] * part_geo
    df["som_region"] = df["sam_region"] * part_som_effective
    df["part_tam_pct"] = 100 * df["tam_region"] / tam if tam else 0.0
    df["tam_par_habitant"] = df["tam_region"] / df["population"].replace(0, np.nan)

    colonnes = [
        "region", "population", "population_cible", "depense_cible_tete",
        "tam_region", "sam_region", "som_region", "part_tam_pct",
        "tam_par_habitant",
    ]
    if secteur == "agrobusiness":
        colonnes += ["tam_demande", "gisement_amont", "production_totale_t"]
    detail = df[[c for c in colonnes if c in df.columns]].copy()
    detail = detail.sort_values("tam_region", ascending=False).reset_index(drop=True)

    # --- Controles de coherence -----------------------------------------
    if tam <= 0:
        avertissements.append(
            "TAM nul : vérifiez que les données de dépense et de population "
            "sont bien chargées pour ce périmètre."
        )
    if secteur == "agrobusiness" and "production_totale_t" in detail.columns:
        sans_prod = detail.loc[
            detail["production_totale_t"].fillna(0) <= 0, "region"].tolist()
        if sans_prod:
            avertissements.append(
                "Aucune production agricole recensée pour : "
                + ", ".join(config.REGIONS_AFFICHAGE.get(r, r) for r in sans_prod)
                + ". Le potentiel de transformation locale y est considéré nul."
            )

    hypotheses = {
        **p,
        "part_geographique": part_geo,
        "part_marche_visee_saisie": part_som,
        "part_marche_visee_effective": part_som_effective,
        "coefficient_budget": coefficient_budget,
        "budget_fcfa": budget,
        "nb_regions": len(regions),
        "depense_nationale_tete": config.DEPENSE_ANNUELLE_TETE,
        "population_nationale": config.POPULATION_NATIONALE,
    }

    # --- Provenance (DATA_MAPPING.md section 0) --------------------------
    # depense_cible_tete mobilise toujours un coefficient de modelisation
    # (captation, part restauration hors domicile, part transformee) : HYP.
    prov_population = p.get("provenance_population_cible", "EST")
    prov_depense = "HYP"
    prov_tam = config.propager_provenance(prov_population, prov_depense)
    prov_sam = config.propager_provenance(prov_tam, "HYP")   # part_geographique
    prov_som = config.propager_provenance(prov_sam, "HYP")   # part_marche_visee
    provenance = {
        "population_cible": prov_population,
        "tam": prov_tam,
        "sam": prov_sam,
        "som": prov_som,
    }

    return ResultatMarche(
        secteur=secteur,
        libelle=p["libelle"],
        regions=regions,
        tam=tam,
        sam=sam,
        som=som,
        population_cible=population_cible,
        detail_regional=detail,
        hypotheses=hypotheses,
        avertissements=avertissements,
        provenance=provenance,
    )


# ==========================================================================
# Intervalle de confiance (analyse de sensibilite)
# ==========================================================================

def coefficients_sensibles(secteur: str) -> list[str]:
    """Noms des coefficients HYP varies par fourchette() pour ce secteur."""
    return list(_COEFFICIENTS_SENSIBLES.get(secteur, []))


def fourchette(
    jeu: JeuDeDonnees,
    secteur: str,
    regions: list[str] | None = None,
    part_geographique: float | None = None,
    part_marche_visee: float | None = None,
    budget: float | None = None,
    marge: float = 0.20,
) -> dict:
    """
    TAM / SAM / SOM bas-central-haut, en faisant varier de +/- `marge` le(s)
    coefficient(s) HYP les plus incertains du secteur (_COEFFICIENTS_SENSIBLES)
    -- pas une marge arbitraire appliquee au TAM lui-meme. Les autres
    hypotheses (zone de chalandise, part de marche visee, budget) restent
    figees a la valeur centrale : seule l'incertitude de modelisation
    proprement dite est representee.

    Pour l'agrobusiness, le TAM est borne par le gisement de matiere
    premiere regionale (cf. _tam_agrobusiness) : dans une region ou ce
    gisement est le facteur limitant, bas = central = haut, ce qui est le
    comportement attendu, pas un defaut.
    """
    args = (jeu, secteur, regions, part_geographique, part_marche_visee, budget)
    central = calculer(*args, facteur_sensibilite=1.0)
    bas = calculer(*args, facteur_sensibilite=1.0 - marge)
    haut = calculer(*args, facteur_sensibilite=1.0 + marge)

    return {
        "marge": marge,
        "coefficients_varies": _COEFFICIENTS_SENSIBLES.get(secteur, []),
        "tam": {"bas": bas.tam, "central": central.tam, "haut": haut.tam},
        "sam": {"bas": bas.sam, "central": central.sam, "haut": haut.sam},
        "som": {"bas": bas.som, "central": central.som, "haut": haut.som},
    }


# ==========================================================================
# Classement des regions (alimente la carte choroplethe du module 4)
# ==========================================================================

def potentiel_par_region(jeu: JeuDeDonnees, secteur: str) -> pd.DataFrame:
    """
    Calcule le TAM de chaque region prise isolement, puis un score de
    potentiel normalise 0-100 combinant volume de marche et intensite
    par habitant.
    """
    resultat = calculer(jeu, secteur, regions=list(config.REGIONS))
    df = resultat.detail_regional.copy()

    def normaliser(serie: pd.Series) -> pd.Series:
        s = serie.fillna(0).astype(float)
        etendue = s.max() - s.min()
        if etendue <= 0:
            return pd.Series(50.0, index=s.index)
        return 100 * (s - s.min()) / etendue

    score_volume = normaliser(df["tam_region"])
    score_intensite = normaliser(df["tam_par_habitant"])
    # 70 % volume (taille du gateau) / 30 % intensite (richesse du marche)
    df["score_potentiel"] = (0.7 * score_volume + 0.3 * score_intensite).round(1)

    df["region_affichage"] = df["region"].map(
        lambda r: config.REGIONS_AFFICHAGE.get(r, r))
    df["tam_lisible"] = df["tam_region"].map(config.formater_fcfa)
    df["rang"] = df["score_potentiel"].rank(ascending=False, method="min").astype(int)

    return df.sort_values("score_potentiel", ascending=False).reset_index(drop=True)


def comparer_secteurs(jeu: JeuDeDonnees,
                      regions: list[str] | None = None,
                      lang: str = "fr") -> pd.DataFrame:
    """Compare les trois secteurs sur un meme perimetre geographique."""
    lignes = []
    for cle in config.SECTEURS:
        r = calculer(jeu, cle, regions=regions)
        lignes.append({
            "Secteur": config.libelle_secteur(cle, lang),
            "TAM (FCFA)": r.tam,
            "SAM (FCFA)": r.sam,
            "SOM (FCFA)": r.som,
            "TAM": config.formater_fcfa(r.tam),
            "SAM": config.formater_fcfa(r.sam),
            "SOM": config.formater_fcfa(r.som),
            "CA mensuel visé": config.formater_fcfa(r.ca_mensuel_som),
            "Population cible": r.population_cible,
        })
    return pd.DataFrame(lignes).sort_values("SOM (FCFA)", ascending=False)


if __name__ == "__main__":
    from pipeline import charger_donnees

    jeu = charger_donnees()

    print("=== Comparaison nationale des 3 secteurs ===")
    print(comparer_secteurs(jeu)[
        ["Secteur", "TAM", "SAM", "SOM", "CA mensuel visé"]
    ].to_string(index=False))

    print("\n=== Supérette à Mbour (région de Thiès) ===")
    r = calculer(jeu, "commerce_proximite", regions=["Thies"],
                 part_geographique=0.08, budget=12_000_000)
    print(r.tableau_synthese()[["Indicateur", "Montant lisible", "% du TAM"]]
          .to_string(index=False))
    for a in r.avertissements:
        print("  ! " + a)

    print("\n=== Potentiel par région - commerce de proximité ===")
    print(potentiel_par_region(jeu, "commerce_proximite")[
        ["rang", "region_affichage", "tam_lisible", "score_potentiel"]
    ].to_string(index=False))
