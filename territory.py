"""
Territory Engine — hierarchie administrative et resolution de territoire
=========================================================================

Perimetre honnete de ce module (a lire avant de l'etendre)
------------------------------------------------------------
La hierarchie region -> departement ci-dessous est une donnee
administrative **stable et verifiee** (decoupage officiel du Senegal,
46 departements / 14 regions, recoupe par source publique le 29 aout 2026).
Elle ne s'accompagne d'**aucune** statistique socio-economique au niveau
departement : ces donnees ne sont pas integrees au projet (cf.
DATA_INVENTORY.md, D01 "Repertoire des localites RGPH-5" — exclu du MVP
faute de telechargement effectif ; les tentatives d'ingestion automatique
via AgriData/CKAN n'ont remonte aucune ventilation departementale
exploitable, cf. ckan_client.py).

Ce module resout donc **quel territoire administratif** l'utilisateur vise
et **detecte les ambiguites de nommage** (ex. "Mbour" designe a la fois une
commune et un departement) — il ne pretend PAS fournir un calcul a un niveau
plus fin que la region tant que les donnees correspondantes ne sont pas
integrees. Resoudre "Mbour" vers son departement puis vers sa region donne
aujourd'hui exactement la meme region qu'une resolution directe ville->region
: la valeur ajoutee actuelle est la **transparence** (l'utilisateur sait sur
quel perimetre il est reellement evalue), pas une precision supplementaire.

Quand un dataset departemental sera reellement integre, ce module est le
point d'extension naturel : il suffira d'attacher les indicateurs aux cles
`DEPARTEMENTS` existantes plutot que de tout reconstruire.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field

import config

# --------------------------------------------------------------------------
# Hierarchie administrative (donnee stable, verifiee par source publique)
# --------------------------------------------------------------------------
# 46 departements repartis sur les 14 regions. Chaque departement porte le
# nom de son chef-lieu, qui est aussi le nom de la commune correspondante :
# c'est la source structurelle de l'ambiguite "commune vs departement".

DEPARTEMENTS: dict[str, list[str]] = {
    "Dakar": ["Dakar", "Pikine", "Rufisque", "Guediawaye", "Keur Massar"],
    "Ziguinchor": ["Bignona", "Oussouye", "Ziguinchor"],
    "Diourbel": ["Bambey", "Diourbel", "Mbacke"],
    "Saint-Louis": ["Dagana", "Podor", "Saint-Louis"],
    "Tambacounda": ["Bakel", "Tambacounda", "Goudiry", "Koumpentoum"],
    "Kaolack": ["Kaolack", "Nioro du Rip", "Guinguineo"],
    "Thies": ["Mbour", "Thies", "Tivaouane"],
    "Louga": ["Kebemer", "Linguere", "Louga"],
    "Fatick": ["Fatick", "Foundiougne", "Gossas"],
    "Kolda": ["Kolda", "Velingara", "Medina Yoro Foulah"],
    "Matam": ["Kanel", "Matam", "Ranerou"],
    "Kaffrine": ["Kaffrine", "Birkelane", "Koungheul", "Malem Hodar"],
    "Kedougou": ["Kedougou", "Salemata", "Saraya"],
    "Sedhiou": ["Sedhiou", "Bounkiling", "Goudomp"],
}

_NB_DEPARTEMENTS = sum(len(v) for v in DEPARTEMENTS.values())
assert _NB_DEPARTEMENTS == 46, (
    f"46 departements attendus (decoupage officiel), {_NB_DEPARTEMENTS} trouves "
    "-- verifier DEPARTEMENTS avant de continuer."
)

def _normaliser(texte: str) -> str:
    """Minuscule, sans accents, espaces normalises."""
    if not texte:
        return ""
    sans_accent = unicodedata.normalize("NFKD", texte)
    sans_accent = "".join(c for c in sans_accent if not unicodedata.combining(c))
    return " ".join(sans_accent.lower().split())


# Index inverse departement (normalise) -> region
_DEPARTEMENT_VERS_REGION: dict[str, str] = {}
for _region, _deps in DEPARTEMENTS.items():
    for _dep in _deps:
        _DEPARTEMENT_VERS_REGION[_normaliser(_dep)] = _region


def region_du_departement(nom_departement: str) -> str | None:
    """Region parente d'un departement, ou None si le nom est inconnu."""
    return _DEPARTEMENT_VERS_REGION.get(_normaliser(nom_departement))


def departements_de_la_region(region: str) -> list[str]:
    """Liste des departements d'une region du referentiel."""
    return list(DEPARTEMENTS.get(region, []))


def est_nom_de_departement(nom: str) -> bool:
    """Vrai si `nom` correspond exactement a un nom de departement connu."""
    return _normaliser(nom) in _DEPARTEMENT_VERS_REGION


# --------------------------------------------------------------------------
# Resolution et desambiguisation
# --------------------------------------------------------------------------

@dataclass
class ResolutionTerritoriale:
    """Resultat de la resolution d'un nom de lieu en territoire administratif."""

    nom_saisi: str
    region: str
    departement: str | None = None
    ambigu: bool = False
    interpretations: list[str] = field(default_factory=list)
    note: str = ""


def resoudre_territoire(nom: str) -> ResolutionTerritoriale | None:
    """
    Resout un nom de lieu libre (ville, commune, departement ou region) vers
    son territoire administratif, en signalant les ambiguites de nommage.

    Ordre de resolution :
      1. Nom de departement connu -> ambigu si son chef-lieu est aussi une
         "ville" du referentiel VILLES_VERS_REGION (quasi toujours vrai,
         c'est la structure meme du decoupage senegalais).
      2. Nom de ville/localite du referentiel existant (config.VILLES_VERS_REGION).
      3. Nom de region du referentiel.
      4. Aucune correspondance -> None.
    """
    nom_norm = _normaliser(nom)
    if not nom_norm:
        return None

    # 1. Nom de departement
    region_dep = _DEPARTEMENT_VERS_REGION.get(nom_norm)
    if region_dep:
        departement = next(
            d for d in DEPARTEMENTS[region_dep] if _normaliser(d) == nom_norm)
        ville_correspondante = nom_norm in {
            _normaliser(v) for v in config.VILLES_VERS_REGION}
        if ville_correspondante:
            return ResolutionTerritoriale(
                nom_saisi=nom,
                region=region_dep,
                departement=departement,
                ambigu=True,
                interpretations=[
                    f"commune de {departement}", f"département de {departement}"],
                note=(
                    f"« {nom} » désigne à la fois une commune et un "
                    f"département — dans les deux cas, le calcul est fait au "
                    f"niveau de la région {config.REGIONS_AFFICHAGE.get(region_dep, region_dep)}, "
                    f"faute de données démographiques désagrégées au niveau "
                    f"départemental ou communal."
                ),
            )
        return ResolutionTerritoriale(
            nom_saisi=nom, region=region_dep, departement=departement)

    # 2. Ville/localite connue
    for ville, region in config.VILLES_VERS_REGION.items():
        if _normaliser(ville) == nom_norm:
            return ResolutionTerritoriale(nom_saisi=nom, region=region)

    # 3. Region directement
    for region in config.REGIONS:
        variantes = {region, config.REGIONS_AFFICHAGE.get(region, region)}
        if any(_normaliser(v) == nom_norm for v in variantes):
            return ResolutionTerritoriale(nom_saisi=nom, region=region)

    return None


if __name__ == "__main__":
    print(f"{_NB_DEPARTEMENTS} départements sur {len(DEPARTEMENTS)} régions\n")
    for exemple in ("Mbour", "Dakar", "Thies", "Ziguinchor", "Atlantide"):
        r = resoudre_territoire(exemple)
        print(f"{exemple!r:15s} -> {r}")
