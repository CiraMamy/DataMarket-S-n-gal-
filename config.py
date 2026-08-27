"""
DataMarket Senegal - Configuration centrale
===========================================
Constantes nationales, referentiel des 14 regions, parametres sectoriels.

Sources officielles :
  - RGPH-5 2023 (ANSD)   : population residente totale = 18 126 390 hab.
  - EHCVM II 2021-2022   : depense de consommation annuelle par tete = 542 706 FCFA
  - EAA / DAPSA          : production agricole par region (campagne de reference)

ATTENTION - statut des donnees :
  Les totaux nationaux ci-dessous sont des chiffres OFFICIELS publies par l'ANSD.
  La ventilation regionale fine (fichiers ref_*.csv) est DERIVEE des parts
  publiees et calibree sur les densites officielles. Elle est destinee a etre
  remplacee par vos propres exports ANSD : deposez vos CSV dans ./data/raw/
  (voir pipeline.py) et ils ecraseront automatiquement les valeurs de reference.
"""

from __future__ import annotations

import os
from pathlib import Path

# --------------------------------------------------------------------------
# Chemins
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"          # vos CSV ANSD (prioritaires)
GEO_DIR = BASE_DIR / "data" / "geo"          # cache GeoJSON
EXPORT_DIR = BASE_DIR / "exports"            # rapports PDF generes

REF_POPULATION = BASE_DIR / "ref_population.csv"
REF_DEPENSES = BASE_DIR / "ref_depenses.csv"
REF_PRODUCTION = BASE_DIR / "ref_production.csv"

for _d in (RAW_DIR, GEO_DIR, EXPORT_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------
# Agregats nationaux officiels
# --------------------------------------------------------------------------
POPULATION_NATIONALE = 18_126_390        # RGPH-5 2023
DEPENSE_ANNUELLE_TETE = 542_706          # FCFA - EHCVM II 2021-2022
TAUX_URBANISATION_NATIONAL = 54.7        # %
TAILLE_MENAGE_NATIONALE = 9.0
PART_MOINS_15_ANS = 39.0                 # %
PART_MOINS_35_ANS = 75.0                 # %
AGE_MEDIAN = 19
CROISSANCE_DEMOGRAPHIQUE = 2.9           # % / an, intercensitaire 2013-2023

DEVISE = "FCFA"

# --------------------------------------------------------------------------
# Referentiel des 14 regions
# --------------------------------------------------------------------------
REGIONS = [
    "Dakar", "Thies", "Diourbel", "Kaolack", "Saint-Louis", "Louga",
    "Fatick", "Tambacounda", "Kolda", "Matam", "Kaffrine",
    "Ziguinchor", "Sedhiou", "Kedougou",
]

# Libelles d'affichage accentues
REGIONS_AFFICHAGE = {
    "Dakar": "Dakar",
    "Thies": "Thiès",
    "Diourbel": "Diourbel",
    "Kaolack": "Kaolack",
    "Saint-Louis": "Saint-Louis",
    "Louga": "Louga",
    "Fatick": "Fatick",
    "Tambacounda": "Tambacounda",
    "Kolda": "Kolda",
    "Matam": "Matam",
    "Kaffrine": "Kaffrine",
    "Ziguinchor": "Ziguinchor",
    "Sedhiou": "Sédhiou",
    "Kedougou": "Kédougou",
}

# Centroides approximatifs (lat, lon) - utilises pour le fallback carto
CENTROIDES = {
    "Dakar": (14.72, -17.35),
    "Thies": (14.85, -16.75),
    "Diourbel": (14.75, -16.10),
    "Kaolack": (14.05, -16.00),
    "Saint-Louis": (16.20, -15.60),
    "Louga": (15.45, -15.90),
    "Fatick": (14.20, -16.45),
    "Tambacounda": (13.70, -13.50),
    "Kolda": (12.90, -14.55),
    "Matam": (15.40, -13.60),
    "Kaffrine": (14.05, -15.35),
    "Ziguinchor": (12.65, -16.20),
    "Sedhiou": (12.80, -15.45),
    "Kedougou": (12.70, -12.30),
}

# --------------------------------------------------------------------------
# Villes principales -> region (pour le parsing langage naturel, module 3)
# --------------------------------------------------------------------------
VILLES_VERS_REGION = {
    # Dakar
    "dakar": "Dakar", "pikine": "Dakar", "guediawaye": "Dakar",
    "rufisque": "Dakar", "keur massar": "Dakar", "parcelles": "Dakar",
    "yoff": "Dakar", "ouakam": "Dakar", "almadies": "Dakar",
    "plateau": "Dakar", "medina": "Dakar", "grand yoff": "Dakar",
    "sacre coeur": "Dakar", "point e": "Dakar", "ngor": "Dakar",
    "diamniadio": "Dakar", "bargny": "Dakar", "sebikotane": "Dakar",
    # Thies
    "thies": "Thies", "mbour": "Thies", "tivaouane": "Thies",
    "saly": "Thies", "joal": "Thies", "joal-fadiouth": "Thies",
    "khombole": "Thies", "pout": "Thies", "mekhe": "Thies",
    "nguekhokh": "Thies", "somone": "Thies", "popenguine": "Thies",
    "kayar": "Thies",
    # Diourbel
    "diourbel": "Diourbel", "touba": "Diourbel", "mbacke": "Diourbel",
    "bambey": "Diourbel", "ndoulo": "Diourbel",
    # Kaolack
    "kaolack": "Kaolack", "nioro": "Kaolack", "guinguineo": "Kaolack",
    "nioro du rip": "Kaolack", "kahone": "Kaolack",
    # Saint-Louis
    "saint-louis": "Saint-Louis", "saint louis": "Saint-Louis",
    "ndar": "Saint-Louis", "richard-toll": "Saint-Louis",
    "richard toll": "Saint-Louis", "dagana": "Saint-Louis",
    "podor": "Saint-Louis", "ross bethio": "Saint-Louis",
    # Louga
    "louga": "Louga", "linguere": "Louga", "kebemer": "Louga",
    "dahra": "Louga",
    # Fatick
    "fatick": "Fatick", "foundiougne": "Fatick", "gossas": "Fatick",
    "sokone": "Fatick", "passy": "Fatick", "diofior": "Fatick",
    # Tambacounda
    "tambacounda": "Tambacounda", "tamba": "Tambacounda",
    "bakel": "Tambacounda", "goudiry": "Tambacounda",
    "koumpentoum": "Tambacounda",
    # Kolda
    "kolda": "Kolda", "velingara": "Kolda", "medina yoro foulah": "Kolda",
    # Matam
    "matam": "Matam", "kanel": "Matam", "ranerou": "Matam",
    "ourossogui": "Matam", "thilogne": "Matam",
    # Kaffrine
    "kaffrine": "Kaffrine", "birkelane": "Kaffrine",
    "koungheul": "Kaffrine", "malem hodar": "Kaffrine",
    # Ziguinchor
    "ziguinchor": "Ziguinchor", "bignona": "Ziguinchor",
    "oussouye": "Ziguinchor", "cap skirring": "Ziguinchor",
    "diouloulou": "Ziguinchor",
    # Sedhiou
    "sedhiou": "Sedhiou", "goudomp": "Sedhiou", "bounkiling": "Sedhiou",
    # Kedougou
    "kedougou": "Kedougou", "salemata": "Kedougou", "saraya": "Kedougou",
}

# --------------------------------------------------------------------------
# Parametres sectoriels (module 2)
# --------------------------------------------------------------------------
# Chaque secteur definit :
#   cible          : fonction de segmentation de la population (voir market.py)
#   poste_depense  : poste EHCVM mobilise
#   taux_captation : part du poste de depense reellement adressable par ce
#                    type de commerce (le reste = autoconsommation, marches
#                    informels, circuits non captables)
#   sam_defaut     : part geographique/segment par defaut
#   som_defaut     : part de marche visee par defaut a 3 ans
SECTEURS = {
    "commerce_proximite": {
        "libelle": "Commerce de proximité (supérette, boutique)",
        "libelle_en": "Corner store (supermarket, shop)",
        "poste_depense": "part_alimentation_pct",
        "description": (
            "Vente au detail de produits alimentaires et d'entretien. "
            "Cible : ensemble des menages, avec une captation plus forte "
            "en milieu urbain (circuits modernes) qu'en milieu rural "
            "(autoconsommation et marches hebdomadaires)."
        ),
        "description_en": (
            "Retail of food and household products. Target: all "
            "households, with stronger capture in urban areas (modern "
            "retail) than in rural areas (self-consumption and weekly "
            "markets)."
        ),
        "captation_urbain": 0.55,
        "captation_rural": 0.30,
        "part_hygiene_entretien": 0.12,   # ajout au panier alimentaire
        "sam_defaut": 0.25,
        "som_defaut": 0.03,
        "ticket_moyen_fcfa": 3500,
        "capex_min_fcfa": 8_000_000,
        # Population cible = ventilation regionale brute, sans filtre
        # comportemental : classee EST (derivee des parts publiees).
        "provenance_population_cible": "EST",
    },
    "restauration_sante": {
        "libelle": "Restauration santé / diabète",
        "libelle_en": "Health-focused catering / diabetes",
        "poste_depense": "part_alimentation_pct",
        "description": (
            "Restauration et plats prepares a indice glycemique maitrise. "
            "Cible : adultes de 25 ans et plus vivant en milieu urbain et "
            "concernes par le diabete ou l'hyperglycemie moderee, avec un "
            "pouvoir d'achat permettant la restauration hors domicile."
        ),
        "description_en": (
            "Catering and prepared meals with controlled glycemic index. "
            "Target: urban adults aged 25+ affected by diabetes or "
            "moderate hyperglycemia, with enough purchasing power for "
            "eating out."
        ),
        "part_adultes_25_plus": 0.36,      # derive de la pyramide RGPH-5
        "prevalence_diabete": 0.034,       # 3,4 % des adultes
        "prevalence_prediabete": 0.080,    # 8,0 % hyperglycemie moderee
        "part_restauration_hors_domicile": 0.16,  # du budget alimentaire urbain
        "coefficient_solvabilite": 0.45,   # part de la cible solvable
        "sam_defaut": 0.30,
        "som_defaut": 0.05,
        "ticket_moyen_fcfa": 4500,
        "capex_min_fcfa": 15_000_000,
        # Population cible = ventilation filtree par prevalence/solvabilite,
        # deux hypotheses de modelisation : classee HYP.
        "provenance_population_cible": "HYP",
    },
    "agrobusiness": {
        "libelle": "Agrobusiness (transformation agroalimentaire)",
        "libelle_en": "Agribusiness (food processing)",
        "poste_depense": "part_alimentation_pct",
        "description": (
            "Transformation et valorisation de la production agricole locale. "
            "TAM construit sur deux jambes : la demande interne en produits "
            "alimentaires transformes et la valeur de la production agricole "
            "regionale mobilisable en amont."
        ),
        "description_en": (
            "Processing and adding value to local agricultural output. "
            "TAM is built on two legs: domestic demand for processed food "
            "products and the value of regional agricultural output still "
            "available upstream."
        ),
        "part_produits_transformes": 0.30,   # du budget alimentaire
        "prix_moyen_tonne_fcfa": 185_000,    # valorisation moyenne matiere premiere
        "taux_transformation_actuel": 0.15,  # part deja transformee localement
        "sam_defaut": 0.20,
        "som_defaut": 0.04,
        "ticket_moyen_fcfa": 0,
        "capex_min_fcfa": 35_000_000,
        # Population cible = ventilation regionale brute (demande aval) ;
        # le TAM est ensuite borne par le gisement amont : classee EST.
        "provenance_population_cible": "EST",
    },
}

# --------------------------------------------------------------------------
# API Anthropic (module 3)
# --------------------------------------------------------------------------
ANTHROPIC_MODEL = "claude-sonnet-5"
ANTHROPIC_MAX_TOKENS = 1024


def libelle_secteur(secteur: str, lang: str = "fr") -> str:
    """Nom d'affichage d'un secteur, dans la langue demandee."""
    p = SECTEURS[secteur]
    return p.get(f"libelle_{lang}", p["libelle"]) if lang != "fr" else p["libelle"]


def description_secteur(secteur: str, lang: str = "fr") -> str:
    """Description d'un secteur, dans la langue demandee."""
    p = SECTEURS[secteur]
    return p.get(f"description_{lang}", p["description"]) if lang != "fr" else p["description"]


def get_api_key() -> str | None:
    """Cle API lue depuis st.secrets puis l'environnement. None si absente."""
    try:
        import streamlit as st

        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    return os.environ.get("ANTHROPIC_API_KEY")


# --------------------------------------------------------------------------
# Presentation
# --------------------------------------------------------------------------
PALETTE = {
    "primaire": "#00853F",     # vert du drapeau senegalais
    "secondaire": "#FDEF42",   # jaune
    "accent": "#E31B23",       # rouge
    "sombre": "#1B2A32",
    "clair": "#F5F7F5",
}

ECHELLE_CHOROPLETHE = "YlGn"

# --------------------------------------------------------------------------
# Provenance des donnees (tracabilite, cf. DATA_MAPPING.md section 0)
# --------------------------------------------------------------------------
# Chaque valeur affichee dans l'interface porte un classement de fiabilite.
# Regle de propagation : le classement d'un calcul est celui de son intrant
# le moins fiable, dans l'ordre croissant d'incertitude ci-dessous. Un TAM
# qui combine une population OBS et une hypothese de captation HYP est donc
# classe HYP, jamais OBS.
ORDRE_PROVENANCE = ["OBS", "CALC", "EST", "PROJ", "HYP"]

PROVENANCE = {
    "OBS": {"label": "OBS", "titre": "Donnée observée — publication officielle",
            "bg": "#FFFFFF", "bordure": "#00853F", "texte": "#00441B"},
    "CALC": {"label": "CALC", "titre": "Indicateur calculé à partir de données observées",
             "bg": "#FFFFFF", "bordure": "#6C757D", "texte": "#333333"},
    "EST": {"label": "EST", "titre": "Estimation — ventilation dérivée de parts publiées",
            "bg": "#FFF3CD", "bordure": "#E8A33D", "texte": "#7A4E00"},
    "PROJ": {"label": "PROJ", "titre": "Projection dans le futur",
              "bg": "#FFF3CD", "bordure": "#E8A33D", "texte": "#7A4E00"},
    "HYP": {"label": "HYP", "titre": "Hypothèse de modélisation — modifiable",
            "bg": "#E7F1FF", "bordure": "#3B82C4", "texte": "#1B4D7A"},
    "EXT": {"label": "EXT", "titre": "Donnée externe, hors ANSD",
            "bg": "#F5F5F5", "bordure": "#999999", "texte": "#555555"},
    "ND": {"label": "N/D", "titre": "Donnée non disponible dans les sources intégrées",
           "bg": "#F0F0F0", "bordure": "#CCCCCC", "texte": "#666666"},
}


def propager_provenance(*codes: str) -> str:
    """Classement d'un calcul = celui de son intrant le moins fiable."""
    presents = [c for c in codes if c in ORDRE_PROVENANCE]
    if not presents:
        return "CALC"
    return max(presents, key=ORDRE_PROVENANCE.index)


def badge_html(code: str, texte: str | None = None) -> str:
    """Pastille HTML compacte signalant la provenance d'une valeur."""
    info = PROVENANCE.get(code, PROVENANCE["ND"])
    libelle = texte or info["label"]
    return (
        f'<span title="{info["titre"]}" style="display:inline-block;'
        f'padding:1px 7px;border-radius:9px;font-size:0.68rem;font-weight:700;'
        f'letter-spacing:0.02em;background:{info["bg"]};'
        f'border:1px solid {info["bordure"]};color:{info["texte"]};'
        f'margin-left:5px;vertical-align:middle;">{libelle}</span>'
    )


def formater_fcfa(montant: float) -> str:
    """Formate un montant en FCFA avec l'unite la plus lisible."""
    if montant is None:
        return "n/d"
    montant = float(montant)
    signe = "-" if montant < 0 else ""
    m = abs(montant)
    if m >= 1_000_000_000:
        return f"{signe}{m / 1_000_000_000:,.1f} Md {DEVISE}".replace(",", " ")
    if m >= 1_000_000:
        return f"{signe}{m / 1_000_000:,.1f} M {DEVISE}".replace(",", " ")
    if m >= 1_000:
        return f"{signe}{m / 1_000:,.0f} k {DEVISE}".replace(",", " ")
    return f"{signe}{m:,.0f} {DEVISE}".replace(",", " ")


def formater_nombre(n: float) -> str:
    """Separateur de milliers a la francaise (espace insecable fine)."""
    if n is None:
        return "n/d"
    return f"{float(n):,.0f}".replace(",", " ")
