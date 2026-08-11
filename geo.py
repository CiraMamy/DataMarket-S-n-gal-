"""
Couche geographique - frontieres des 14 regions du Senegal
==========================================================

Strategie a trois niveaux, du plus precis au plus degrade :

  1. Cache local        data/geo/senegal_regions.geojson
  2. Telechargement     geoBoundaries (ADM1, licence ouverte), puis mise en cache
  3. Repli cercles      pastilles proportionnelles positionnees sur les
                        centroides regionaux (config.CENTROIDES)

Le niveau atteint est retourne dans le champ `mode` afin que l'interface
puisse le signaler honnetement a l'utilisateur.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import config
from pipeline import normaliser_region

FICHIER_CACHE = config.GEO_DIR / "senegal_regions.geojson"

# Sources ouvertes, par ordre de preference
SOURCES = [
    "https://www.geoboundaries.org/api/current/gbOpen/SEN/ADM1/",
    "https://raw.githubusercontent.com/wmgeolab/geoBoundaries/main/"
    "releaseData/gbOpen/SEN/ADM1/geoBoundaries-SEN-ADM1_simplified.geojson",
]

# Cle de propriete contenant le nom de region selon la source
_CLES_NOM = ("shapeName", "NAME_1", "name", "NOM", "region", "ADM1_FR",
             "admin1Name", "NAME", "nom")


@dataclass
class Geographie:
    """Resultat du chargement geographique."""

    geojson: dict | None
    mode: str          # "cache" | "telecharge" | "cercles"
    message: str

    @property
    def a_polygones(self) -> bool:
        return self.geojson is not None


def _normaliser_proprietes(geojson: dict) -> dict:
    """
    Uniformise chaque entite : ajoute une propriete `region` contenant le
    nom canonique (l'un des 14 libelles du referentiel). Les entites non
    reconnues sont ecartees.
    """
    entites = []
    for entite in geojson.get("features", []):
        proprietes = entite.get("properties", {}) or {}

        brut = None
        for cle in _CLES_NOM:
            if proprietes.get(cle):
                brut = proprietes[cle]
                break
        if brut is None:
            for valeur in proprietes.values():
                if isinstance(valeur, str) and normaliser_region(valeur):
                    brut = valeur
                    break

        region = normaliser_region(brut) if brut else None
        if region is None:
            continue

        proprietes["region"] = region
        proprietes["region_affichage"] = config.REGIONS_AFFICHAGE.get(region, region)
        entite["properties"] = proprietes
        entite["id"] = region
        entites.append(entite)

    return {"type": "FeatureCollection", "features": entites}


def _telecharger() -> dict | None:
    """Telecharge le GeoJSON depuis les sources ouvertes. None si echec."""
    try:
        import requests
    except ImportError:
        return None

    for url in SOURCES:
        try:
            reponse = requests.get(url, timeout=20)
            reponse.raise_for_status()
            donnees = reponse.json()

            # L'API geoBoundaries renvoie un descripteur, pas le GeoJSON
            if isinstance(donnees, dict) and "gjDownloadURL" in donnees:
                suite = requests.get(donnees["gjDownloadURL"], timeout=30)
                suite.raise_for_status()
                donnees = suite.json()
            elif isinstance(donnees, list) and donnees and "gjDownloadURL" in donnees[0]:
                suite = requests.get(donnees[0]["gjDownloadURL"], timeout=30)
                suite.raise_for_status()
                donnees = suite.json()

            if isinstance(donnees, dict) and donnees.get("features"):
                return donnees
        except Exception:
            continue
    return None


def charger_geographie(forcer_telechargement: bool = False) -> Geographie:
    """Charge les frontieres regionales selon la strategie a trois niveaux."""

    # Niveau 1 : cache
    if FICHIER_CACHE.exists() and not forcer_telechargement:
        try:
            donnees = json.loads(FICHIER_CACHE.read_text(encoding="utf-8"))
            normalise = _normaliser_proprietes(donnees)
            n = len(normalise["features"])
            if n >= 10:
                return Geographie(
                    normalise, "cache",
                    f"Frontières régionales chargées depuis le cache local "
                    f"({n}/14 régions).")
        except Exception:
            pass

    # Niveau 2 : telechargement
    donnees = _telecharger()
    if donnees:
        normalise = _normaliser_proprietes(donnees)
        n = len(normalise["features"])
        if n >= 10:
            try:
                FICHIER_CACHE.write_text(
                    json.dumps(donnees, ensure_ascii=False), encoding="utf-8")
            except Exception:
                pass
            return Geographie(
                normalise, "telecharge",
                f"Frontières régionales téléchargées et mises en cache "
                f"({n}/14 régions).")

    # Niveau 3 : repli
    return Geographie(
        None, "cercles",
        "Frontières régionales indisponibles (pas de connexion réseau ni de "
        "cache). Affichage dégradé en pastilles proportionnelles sur les "
        "chefs-lieux. Placez un fichier senegal_regions.geojson dans "
        "data/geo/ pour activer la carte choroplèthe.")


def regions_couvertes(geo: Geographie) -> list[str]:
    """Liste des regions effectivement presentes dans le GeoJSON."""
    if not geo.a_polygones:
        return []
    return sorted({
        e["properties"]["region"] for e in geo.geojson["features"]
    })


def regions_manquantes(geo: Geographie) -> list[str]:
    """Regions du referentiel absentes du GeoJSON."""
    presentes = set(regions_couvertes(geo))
    return [r for r in config.REGIONS if r not in presentes]


if __name__ == "__main__":
    g = charger_geographie()
    print(f"Mode : {g.mode}")
    print(g.message)
    if g.a_polygones:
        print(f"Régions couvertes : {len(regions_couvertes(g))}")
        manquantes = regions_manquantes(g)
        if manquantes:
            print(f"Manquantes : {', '.join(manquantes)}")
