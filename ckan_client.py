"""
Client CKAN - ingestion automatisee des portails Open Data de l'ANSD
====================================================================

Portails cibles
---------------
  AgriData        https://agridata.ansd.sn
                  ANSD + IPAR + DAPSA. CKAN avec extension DataStore.
                  Statistiques agricoles.

  ODP Regional    https://odpregional.statsenegal.sn
                  Statistiques regionales officielles, niveau departement.
                  Plateforme non confirmee comme CKAN : le client teste et
                  se rabat proprement si l'API ne repond pas.

Ce que ce module apporte
------------------------
Jusqu'ici, toute donnee entrait dans DataMarket par telechargement manuel puis
depot dans data/raw/. Avec une API CKAN, l'ingestion devient programmable et
surtout **reactualisable** : le meme script relance demain donne les donnees
de demain. C'est la difference entre un prototype fige et une plateforme.

Trois usages
------------
  1. RECONNAISSANCE  Cartographier le catalogue d'un portail sans rien
                     telecharger. Repond a la question « qu'y a-t-il
                     dedans ? » avant d'ecrire la moindre ligne d'ingestion.

  2. INGESTION       Telecharger une ressource DataStore en DataFrame, avec
                     pagination transparente, et l'ecrire dans data/raw/ ou
                     pipeline.py la recuperera automatiquement.

  3. TRACABILITE     Conserver pour chaque ressource ses metadonnees
                     (portail, dataset, licence, date de modification, URL),
                     conformement au §11 du cahier des charges.

Utilisation en ligne de commande
--------------------------------
    python ckan_client.py explorer                  # cartographie AgriData
    python ckan_client.py explorer --portail odp    # cartographie l'ODP
    python ckan_client.py dataset donneeagricole    # detail d'un jeu
    python ckan_client.py extraire <resource_id>    # telecharge en CSV
    python ckan_client.py tout-agricole             # ingestion agricole

ETAT VERIFIE (25 aout 2026)
---------------------------
Ce client a d'abord ete ecrit sans pouvoir etre execute, puis reellement
teste contre les deux portails. Resultats :

  AgriData   Accessible. Un bug bloquait toute connexion Python (le
             serveur ne renvoie pas son certificat intermediaire
             GlobalSign — corrige ci-dessous par _bundle_verification()).
             298 jeux de donnees, 281 ressources interrogeables par API.

             Mais : les 16 jeux "prioritaires" de DATASETS_PRIORITAIRES
             (population, depenses, production) suivent tous le meme
             format "fiche indicateur SDR" — une seule ligne, valeurs
             par annee, malgre des titres qui promettent une ventilation
             "par region". Un balayage exhaustif des 281 ressources
             interrogeables (filtre 10-20 lignes, proxy d'une table a une
             ligne par region) n'a remonte aucune table region x
             population/depense/production exploitable. Les seules
             donnees reellement regionales trouvees sont hors-sujet
             (ex. seuils d'alerte des cours d'eau par station).

             Conclusion : AgriData ne permet pas aujourd'hui de remplacer
             les estimations regionales de ref_*.csv par des donnees
             observees. Les jeux prioritaires restent utiles au niveau
             national (serie longue par indicateur) mais pas au niveau
             regional attendu par le pipeline.

  ODP        Repond (HTTP 401) mais exige une authentification que ce
  Regional   projet n'a pas. A revisiter si un acces est obtenu.

Avant de retenter une ingestion automatique, revalider manuellement le
contenu de chaque jeu vise (`python ckan_client.py dataset <nom>` puis
inspection des premieres lignes) : le titre d'un jeu sur ce portail ne
garantit pas sa structure.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None

import config

# --------------------------------------------------------------------------
# Chaine de certification
# --------------------------------------------------------------------------
# agridata.ansd.sn (nginx) ne renvoie que son certificat feuille, sans
# l'intermediaire GlobalSign GCC R3 DV TLS CA 2020. Les navigateurs et
# Windows tolerent cette omission via une recuperation automatique de la
# chaine (AIA fetching) ; Python/OpenSSL ne le font pas et rejettent la
# connexion avec « unable to get local issuer certificate ». On complete
# donc le magasin certifi avec l'intermediaire manquant plutot que de
# desactiver la verification TLS. Intermediaire recupere une fois pour
# toutes depuis le point de distribution officiel de l'autorite :
# http://secure.globalsign.com/cacert/gsgccr3dvtlsca2020.crt
_CERTS_DIR = Path(__file__).resolve().parent / "certs"
_bundle_verification_cache: str | None = None


def _bundle_verification() -> str:
    """Chemin d'un bundle CA = certifi + intermediaires manquants du projet."""
    global _bundle_verification_cache
    if _bundle_verification_cache:
        return _bundle_verification_cache

    import certifi

    intermediaires = sorted(_CERTS_DIR.glob("*.pem")) if _CERTS_DIR.is_dir() else []
    if not intermediaires:
        _bundle_verification_cache = certifi.where()
        return _bundle_verification_cache

    cache_dir = Path(tempfile.gettempdir()) / "datamarket_senegal"
    cache_dir.mkdir(parents=True, exist_ok=True)
    bundle = cache_dir / "ca_bundle_ansd.pem"

    contenu = Path(certifi.where()).read_bytes()
    for chemin in intermediaires:
        contenu += b"\n" + chemin.read_bytes()
    bundle.write_bytes(contenu)

    _bundle_verification_cache = str(bundle)
    return _bundle_verification_cache

# ==========================================================================
# Portails connus
# ==========================================================================

PORTAILS = {
    "agridata": {
        "libelle": "AgriData — ANSD / IPAR / DAPSA",
        "base_url": "https://agridata.ansd.sn",
        "type": "ckan",
        "theme": "Statistiques agricoles",
        "producteur": "ANSD, IPAR, DAPSA",
        "confirme": True,
    },
    "odp": {
        "libelle": "ODP Régional — statistiques régionales",
        "base_url": "https://odpregional.statsenegal.sn",
        "type": "inconnu",       # a confirmer : CKAN ou API REST propre
        "theme": "Statistiques régionales et départementales",
        "producteur": "ANSD",
        "confirme": False,
    },
}

# Ressources DataStore reperees dans la documentation publique d'AgriData.
# Elles servent de point d'entree si package_list echoue.
RESSOURCES_CONNUES_AGRIDATA = [
    "9b40d530-9f3c-4916-8813-51b8ed788f65",
    "ac648d96-007f-416c-833c-705c8108f9ea",
]

# ==========================================================================
# Jeux prioritaires AgriData
# ==========================================================================
# Releve effectue sur package_list le 4 aout 2026 : 280 jeux de donnees.
# Contre toute attente, le portail ne contient pas que de l'agricole : il
# expose aussi des tableaux de population issus du RGPH-5 2023 et un jeu sur
# les depenses alimentaires. Ce sont exactement les briques qui manquaient au
# pipeline et qui etaient jusqu'ici remplacees par des estimations.
#
# Les noms sont repris tels quels : le portail a translittere les accents en
# supprimant les voyelles ("rgion", "mnages", "sngal"). Ne pas les corriger.

DATASETS_PRIORITAIRES = {
    # --- Population : remplace les estimations regionales du prototype ----
    "population": {
        "priorite": 0,
        "usage": "Remplace ref_population.csv (estimations) par des donnees "
                 "observees RGPH-5",
        "cible_pipeline": "population",
        "jeux": [
            # Le plus important : population + urbanisation + menages en un seul
            # tableau. Couvre a lui seul trois colonnes actuellement estimees.
            "population_rsidente_taux_durbanisation_et_nombre_et_taille_des_mnages",
            "population_rsidente_nombre_et_taille_des_mnages_par_rgion",
            # Pyramide des ages par region : debloque la segmentation client
            # du secteur restauration sante, aujourd'hui fondee sur une
            # hypothese nationale.
            "rpartition_de_la_population_du_sngal_par_rgion_sexe_et_groupe_dge_rgph5_2023",
            "population_du_sngal_par_rgion_age_et_sexe_2023",
            "population_du_sngal_par_groupes_dges",
            "rpartition_des_membres_de_mnages_selon_la_rgion",
        ],
    },

    # --- Consommation ----------------------------------------------------
    "consommation": {
        "priorite": 0,
        "usage": "Coefficient budgetaire alimentaire — intrant direct du TAM",
        "cible_pipeline": "depenses",
        "jeux": [
            "partdesdepensesalimentaires",
            "etudelaconsommationdescerealesdebaseausenegal",
            "approvisionnement_en_crales_en_kg_par_habitant",
        ],
    },

    # --- Production agricole : debloque le secteur agrobusiness ----------
    "production_agregee": {
        "priorite": 1,
        "usage": "Remplace ref_production.csv (non source) — comble le trou D13",
        "cible_pipeline": "production",
        "jeux": [
            "les_principales_cultures_production_rendement_et_superficie",
            "superficie_rendement_et_production_agricoles",
            "production_des_denres_agricoles",
            "production_des_denres_agricoles_par_habitant",
            "production_des_types_de_culture",
            "production_des_principales_crales_production_rendement_et_superficie_december_2022",
            "production_nationale_de_crales",
        ],
    },

    "production_par_culture": {
        "priorite": 2,
        "usage": "Detail par culture si les tableaux agreges manquent de finesse",
        "cible_pipeline": "production",
        "jeux": [
            "productionarachide", "productionmil", "productionriz",
            "productionmais", "productionsorgho", "productionfonio",
            "productionniebe", "productioncoton", "productionsesame",
            "productionmanioc", "productionpatatedouce",
            "productiontomate", "productiontomates", "rendementoignon",
            "productionpasteque", "productionmelon", "productiongombo",
            "productionchoupomme", "productionharicot", "productionmangue",
            "productionbanane", "productionagrumes",
        ],
    },

    # --- Prix : permet de valoriser le gisement agrobusiness -------------
    "prix": {
        "priorite": 2,
        "usage": "Remplace le prix moyen a la tonne, aujourd'hui une hypothese",
        "cible_pipeline": None,
        "jeux": [
            "indice-des-prix-a-la-production-pour-les-principales-cultures",
            "prix_produits_craliers_imports",
        ],
    },

    # --- Infrastructure commerciale : proxy de concurrence ---------------
    # Le RGE datant de 2016, ces comptages sont un complement interessant.
    # Les variantes suffixees "rgph" proviennent du recensement et ont donc
    # des chances d'etre ventilees geographiquement.
    "infrastructure_commerciale": {
        "priorite": 2,
        "usage": "Proxy de densite commerciale, en complement du RGE 2016",
        "cible_pipeline": None,
        "jeux": [
            "nombredefoirails", "nombredefoirailsrgph",       # marches a betail
            "nombredabattoirs", "nombredabattoirsrgph",
            "nombredemagasinsdestockagerehabilites",
            "nombredepharmaciesveterinaires", "nombredepharmaciesveterinairesrgph",
            "nombredecliniquesveterinaires", "nombresdecliniquesveterinairesrgph",
            "nombredemenagesagricoles", "nombredemenagesagricolesrgph",
        ],
    },

    # --- Emploi ----------------------------------------------------------
    "emploi": {
        "priorite": 3,
        "usage": "Risk Engine — dependance du territoire a l'agriculture",
        "cible_pipeline": None,
        "jeux": [
            "proportiondemploidanslagriculture",
            "proportiondemploidanslagricultureenes",
            "emploi_jeunes",
        ],
    },
}


def jeux_par_priorite(maximum: int = 1) -> list[str]:
    """Noms des jeux prioritaires jusqu'au niveau de priorite donne."""
    noms = []
    for groupe in DATASETS_PRIORITAIRES.values():
        if groupe["priorite"] <= maximum:
            noms.extend(groupe["jeux"])
    return list(dict.fromkeys(noms))

DELAI = 30          # secondes
PAUSE = 0.4         # entre deux appels, par courtoisie envers le serveur
TAILLE_PAGE = 1000  # lignes par appel datastore_search


# ==========================================================================
# Erreurs
# ==========================================================================

class ErreurCkan(RuntimeError):
    """Erreur remontee par l'API CKAN ou par le transport."""


# ==========================================================================
# Client
# ==========================================================================

@dataclass
class Ressource:
    """Une ressource (fichier ou table) au sein d'un jeu de donnees."""

    id: str
    nom: str
    format: str
    url: str
    datastore_actif: bool
    dataset: str = ""
    description: str = ""

    @property
    def interrogeable(self) -> bool:
        """Vrai si la ressource est requetable ligne a ligne via l'API."""
        return self.datastore_actif and bool(self.id)


@dataclass
class JeuCkan:
    """Un jeu de donnees CKAN."""

    nom: str
    titre: str
    notes: str = ""
    licence: str = ""
    organisation: str = ""
    modifie_le: str = ""
    groupes: list[str] = field(default_factory=list)
    ressources: list[Ressource] = field(default_factory=list)

    @property
    def nb_interrogeables(self) -> int:
        return sum(1 for r in self.ressources if r.interrogeable)


class ClientCkan:
    """
    Client de l'API CKAN Action v3.

    Tolere les variantes de chemin rencontrees sur les instances
    multilingues : /api/3/action/... et /fr/api/3/action/...
    """

    def __init__(self, portail: str = "agridata", delai: int = DELAI):
        if portail not in PORTAILS:
            raise KeyError(
                f"Portail inconnu : '{portail}'. "
                f"Valeurs admises : {list(PORTAILS)}")
        self.cle = portail
        self.portail = PORTAILS[portail]
        self.base = self.portail["base_url"].rstrip("/")
        self.delai = delai
        self.prefixe = ""      # determine au premier appel reussi
        self._session = None

    # -- transport --------------------------------------------------------

    @property
    def session(self):
        if requests is None:
            raise ErreurCkan(
                "Le paquet `requests` est absent. "
                "Installez-le : pip install requests")
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({
                "User-Agent": "DataMarket-Senegal/1.0 (plateforme "
                              "d'intelligence economique, ANSD Hackathon 2026)",
                "Accept": "application/json",
            })
            self._session.verify = _bundle_verification()
        return self._session

    def _appeler(self, action: str, **parametres) -> object:
        """
        Appelle une action CKAN et retourne le champ `result`.

        Essaie successivement les prefixes de chemin connus, memorise celui
        qui fonctionne, et leve ErreurCkan avec un message exploitable en cas
        d'echec.
        """
        prefixes = [self.prefixe] if self.prefixe else ["", "/fr", "/en"]
        derniere_erreur = None

        for prefixe in prefixes:
            url = f"{self.base}{prefixe}/api/3/action/{action}"
            try:
                reponse = self.session.get(
                    url, params=parametres, timeout=self.delai)
            except Exception as erreur:
                derniere_erreur = f"{type(erreur).__name__} : {erreur}"
                continue

            if reponse.status_code == 404:
                derniere_erreur = f"404 sur {url}"
                continue

            try:
                charge = reponse.json()
            except ValueError:
                derniere_erreur = (
                    f"Réponse non-JSON sur {url} "
                    f"(HTTP {reponse.status_code}). Le portail renvoie "
                    f"probablement une page HTML : l'API CKAN n'est peut-être "
                    f"pas exposée à cette adresse.")
                continue

            if not charge.get("success", False):
                message = charge.get("error", {})
                raise ErreurCkan(f"CKAN a refusé l'action '{action}' : {message}")

            self.prefixe = prefixe
            time.sleep(PAUSE)
            return charge.get("result")

        raise ErreurCkan(
            f"Aucun endpoint CKAN n'a répondu pour l'action '{action}' sur "
            f"{self.base}. Dernière erreur : {derniere_erreur}")

    # -- catalogue --------------------------------------------------------

    def liste_jeux(self) -> list[str]:
        """Noms de tous les jeux de donnees du portail."""
        resultat = self._appeler("package_list")
        return list(resultat) if isinstance(resultat, list) else []

    def detail_jeu(self, nom: str) -> JeuCkan:
        """Metadonnees completes d'un jeu de donnees."""
        brut = self._appeler("package_show", id=nom)
        return self._vers_jeu(brut)

    def rechercher(self, requete: str = "", lignes: int = 1000) -> list[JeuCkan]:
        """
        Tous les jeux de donnees avec leurs metadonnees, en une passe
        paginee. Plus efficace que liste_jeux() + detail_jeu() en boucle.
        """
        jeux, debut = [], 0
        while True:
            resultat = self._appeler(
                "package_search", q=requete, rows=min(lignes, 100), start=debut)
            lot = resultat.get("results", []) if isinstance(resultat, dict) else []
            if not lot:
                break
            jeux.extend(self._vers_jeu(p) for p in lot)
            debut += len(lot)
            if debut >= resultat.get("count", 0) or debut >= lignes:
                break
        return jeux

    def groupes(self) -> list[str]:
        try:
            return list(self._appeler("group_list") or [])
        except ErreurCkan:
            return []

    def organisations(self) -> list[str]:
        try:
            return list(self._appeler("organization_list") or [])
        except ErreurCkan:
            return []

    @staticmethod
    def _vers_jeu(brut: dict) -> JeuCkan:
        ressources = []
        for r in brut.get("resources", []) or []:
            ressources.append(Ressource(
                id=r.get("id", ""),
                nom=r.get("name") or "(sans nom)",
                format=(r.get("format") or "").upper(),
                url=r.get("url", ""),
                datastore_actif=bool(r.get("datastore_active")),
                dataset=brut.get("name", ""),
                description=(r.get("description") or "")[:300],
            ))
        organisation = brut.get("organization") or {}
        return JeuCkan(
            nom=brut.get("name", ""),
            titre=brut.get("title") or brut.get("name", ""),
            notes=(brut.get("notes") or "")[:600],
            licence=brut.get("license_title") or brut.get("license_id") or "",
            organisation=organisation.get("title") or organisation.get("name", ""),
            modifie_le=brut.get("metadata_modified", ""),
            groupes=[g.get("name", "") for g in (brut.get("groups") or [])],
            ressources=ressources,
        )

    # -- donnees ----------------------------------------------------------

    def lire_ressource(self, resource_id: str,
                       maximum: int | None = None) -> pd.DataFrame:
        """
        Telecharge une ressource DataStore en DataFrame, avec pagination.

        `maximum` borne le nombre de lignes ; None = tout.
        """
        lignes: list[dict] = []
        decalage = 0

        while True:
            taille = TAILLE_PAGE
            if maximum is not None:
                taille = min(taille, maximum - len(lignes))
                if taille <= 0:
                    break

            resultat = self._appeler(
                "datastore_search",
                resource_id=resource_id,
                limit=taille,
                offset=decalage,
            )
            if not isinstance(resultat, dict):
                break

            lot = resultat.get("records", [])
            if not lot:
                break

            lignes.extend(lot)
            decalage += len(lot)

            total = resultat.get("total")
            if total is not None and decalage >= total:
                break
            if len(lot) < taille:
                break

        df = pd.DataFrame(lignes)
        # CKAN ajoute une colonne technique de rang
        return df.drop(columns=["_id"], errors="ignore")

    def requete_sql(self, sql: str) -> pd.DataFrame:
        """
        Requete SQL directe sur le DataStore.

        Exemple :
            SELECT * FROM "9b40d530-..." WHERE region = 'Thies'

        Note : l'identifiant de ressource doit etre entre guillemets doubles.
        """
        resultat = self._appeler("datastore_search_sql", sql=sql)
        lignes = resultat.get("records", []) if isinstance(resultat, dict) else []
        return pd.DataFrame(lignes).drop(columns=["_id"], errors="ignore")

    def telecharger_fichier(self, url: str) -> pd.DataFrame | None:
        """Telecharge une ressource non-DataStore (CSV ou Excel) par son URL."""
        try:
            reponse = self.session.get(url, timeout=self.delai * 2)
            reponse.raise_for_status()
        except Exception:
            return None

        from io import BytesIO

        contenu = BytesIO(reponse.content)
        if url.lower().endswith((".xlsx", ".xls")):
            try:
                return pd.read_excel(contenu)
            except Exception:
                return None

        for encodage in ("utf-8-sig", "utf-8", "latin-1"):
            for sep in (None, ",", ";", "\t"):
                try:
                    contenu.seek(0)
                    df = pd.read_csv(contenu, encoding=encodage, sep=sep,
                                     engine="python", on_bad_lines="skip")
                    if df.shape[1] >= 2:
                        return df
                except Exception:
                    continue
        return None


# ==========================================================================
# Reconnaissance
# ==========================================================================

def explorer(portail: str = "agridata",
             sortie: Path | None = None) -> pd.DataFrame:
    """
    Cartographie un portail sans rien telecharger.

    Produit un tableau une ligne par ressource, et ecrit un rapport Markdown
    listant ce qui est exploitable. C'est la premiere commande a lancer sur
    un portail inconnu.
    """
    client = ClientCkan(portail)
    infos = client.portail

    print(f"\n{'=' * 74}")
    print(f"  {infos['libelle']}")
    print(f"  {infos['base_url']}")
    print(f"{'=' * 74}\n")

    try:
        jeux = client.rechercher()
    except ErreurCkan as erreur:
        print(f"  ECHEC : {erreur}\n")
        if not infos["confirme"]:
            print("  Ce portail n'était pas confirmé comme instance CKAN.")
            print("  Ouvrez ces adresses dans un navigateur pour trancher :")
            for chemin in ("/api/3/action/package_list",
                           "/api/3/action/status_show",
                           "/data.json", "/api"):
                print(f"    {infos['base_url']}{chemin}")
        return pd.DataFrame()

    if not jeux:
        print("  Le portail répond mais ne renvoie aucun jeu de données.\n")
        return pd.DataFrame()

    lignes = []
    for jeu in jeux:
        if not jeu.ressources:
            lignes.append({
                "dataset": jeu.nom, "titre": jeu.titre,
                "ressource": "(aucune)", "resource_id": "", "format": "",
                "datastore": False, "licence": jeu.licence,
                "organisation": jeu.organisation, "modifie_le": jeu.modifie_le,
                "url": "",
            })
            continue
        for ressource in jeu.ressources:
            lignes.append({
                "dataset": jeu.nom,
                "titre": jeu.titre,
                "ressource": ressource.nom,
                "resource_id": ressource.id,
                "format": ressource.format,
                "datastore": ressource.datastore_actif,
                "licence": jeu.licence,
                "organisation": jeu.organisation,
                "modifie_le": jeu.modifie_le,
                "url": ressource.url,
            })

    catalogue = pd.DataFrame(lignes)

    interrogeables = catalogue[catalogue["datastore"]]
    print(f"  Jeux de données ......... {len(jeux)}")
    print(f"  Ressources .............. {len(catalogue)}")
    print(f"  Interrogeables par API .. {len(interrogeables)}")
    print(f"  Formats ................. "
          f"{', '.join(sorted(f for f in catalogue['format'].unique() if f))}\n")

    if len(interrogeables):
        print("  Ressources directement exploitables :\n")
        for r in interrogeables.head(40).itertuples():
            print(f"    {r.resource_id}")
            print(f"      {r.titre} — {r.ressource}\n")

    dossier = sortie or config.BASE_DIR
    dossier.mkdir(parents=True, exist_ok=True)

    chemin_csv = dossier / f"catalogue_{portail}.csv"
    catalogue.to_csv(chemin_csv, index=False, encoding="utf-8-sig")

    chemin_md = dossier / f"CATALOGUE_{portail.upper()}.md"
    chemin_md.write_text(_rapport_markdown(infos, jeux, catalogue),
                         encoding="utf-8")

    print(f"  Catalogue écrit : {chemin_csv.name} et {chemin_md.name}\n")
    return catalogue


def _rapport_markdown(infos: dict, jeux: list[JeuCkan],
                      catalogue: pd.DataFrame) -> str:
    horodatage = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    interrogeables = catalogue[catalogue["datastore"]]

    lignes = [
        f"# Catalogue — {infos['libelle']}",
        "",
        f"Relevé automatique du {horodatage}",
        "",
        f"- **Portail** : {infos['base_url']}",
        f"- **Producteur** : {infos['producteur']}",
        f"- **Thème** : {infos['theme']}",
        f"- **Jeux de données** : {len(jeux)}",
        f"- **Ressources** : {len(catalogue)}",
        f"- **Interrogeables par API** : {len(interrogeables)}",
        "",
        "> Ce fichier est généré par `ckan_client.py explorer`. Il constitue",
        "> le catalogue de données exigé au §12 du cahier des charges.",
        "",
        "---",
        "",
        "## Ressources interrogeables par API",
        "",
        "| resource_id | Jeu de données | Ressource | Format |",
        "|---|---|---|---|",
    ]

    for r in interrogeables.itertuples():
        lignes.append(
            f"| `{r.resource_id}` | {r.titre} | {r.ressource} | {r.format} |")

    lignes += ["", "---", "", "## Détail par jeu de données", ""]

    for jeu in sorted(jeux, key=lambda j: j.titre):
        lignes += [
            f"### {jeu.titre}",
            "",
            f"- **Identifiant** : `{jeu.nom}`",
            f"- **Organisation** : {jeu.organisation or 'non renseignée'}",
            f"- **Licence** : {jeu.licence or '⚠️ non renseignée'}",
            f"- **Dernière modification** : {jeu.modifie_le or 'inconnue'}",
            f"- **Groupes** : {', '.join(jeu.groupes) or 'aucun'}",
            f"- **Ressources** : {len(jeu.ressources)} "
            f"(dont {jeu.nb_interrogeables} interrogeables)",
        ]
        if jeu.notes:
            lignes += ["", f"> {jeu.notes.strip()}"]
        if jeu.ressources:
            lignes += ["", "| Ressource | Format | API | resource_id |",
                       "|---|---|---|---|"]
            for ressource in jeu.ressources:
                marque = "✅" if ressource.datastore_actif else "—"
                lignes.append(
                    f"| {ressource.nom} | {ressource.format} | {marque} | "
                    f"`{ressource.id}` |")
        lignes.append("")

    return "\n".join(lignes)


# ==========================================================================
# Ingestion
# ==========================================================================

def extraire(resource_id: str, portail: str = "agridata",
             nom_fichier: str | None = None,
             maximum: int | None = None) -> pd.DataFrame:
    """
    Telecharge une ressource et l'ecrit dans data/raw/, ou pipeline.py la
    recuperera automatiquement au prochain chargement.

    Ecrit egalement un fichier .meta.json portant la tracabilite exigee au
    §11 : portail, ressource, date d'acces, URL, nombre de lignes.
    """
    client = ClientCkan(portail)
    print(f"  Extraction de {resource_id} …")

    df = client.lire_ressource(resource_id, maximum=maximum)
    if df.empty:
        print("  Aucune ligne retournée.")
        return df

    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    base = nom_fichier or f"{portail}_{resource_id[:8]}"
    chemin = config.RAW_DIR / f"{base}.csv"
    df.to_csv(chemin, index=False, encoding="utf-8-sig")

    metadonnees = {
        "portail": portail,
        "portail_url": PORTAILS[portail]["base_url"],
        "producteur": PORTAILS[portail]["producteur"],
        "resource_id": resource_id,
        "date_acces": datetime.now(timezone.utc).isoformat(),
        "nb_lignes": int(len(df)),
        "colonnes": list(df.columns),
        "classement_tracabilite": "OBS",
        "methode": "API CKAN datastore_search",
    }
    chemin.with_suffix(".meta.json").write_text(
        json.dumps(metadonnees, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"  {len(df)} lignes × {df.shape[1]} colonnes → {chemin.name}")
    print(f"  Colonnes : {', '.join(map(str, df.columns[:12]))}")
    return df


def sonder(priorite_max: int = 1, portail: str = "agridata") -> pd.DataFrame:
    """
    Diagnostic : pour chaque jeu prioritaire, repond a LA question qui
    conditionne tout — **les donnees sont-elles ventilees par region ?**

    Un tableau national ne sert a rien au Territory Engine. Cette commande
    telecharge 5 lignes de chaque ressource, inspecte les colonnes et
    classe le jeu en `regional`, `national` ou `indetermine`.

    C'est la commande a lancer juste apres `explorer`.
    """
    client = ClientCkan(portail)
    noms = jeux_par_priorite(priorite_max)
    lignes = []

    print(f"\n  Sondage de {len(noms)} jeux prioritaires "
          f"(priorité ≤ {priorite_max})\n")

    for nom in noms:
        try:
            jeu = client.detail_jeu(nom)
        except ErreurCkan as erreur:
            lignes.append({"dataset": nom, "statut": f"introuvable ({erreur})",
                           "niveau": "—", "resource_id": "", "colonnes": ""})
            print(f"    ✗ {nom}")
            continue

        interrogeables = [r for r in jeu.ressources if r.interrogeable]
        if not interrogeables:
            lignes.append({"dataset": nom, "statut": "aucune ressource API",
                           "niveau": "—", "resource_id": "",
                           "colonnes": "", "licence": jeu.licence})
            print(f"    ~ {nom} — pas d'accès API")
            continue

        ressource = interrogeables[0]
        try:
            apercu = client.lire_ressource(ressource.id, maximum=5)
        except ErreurCkan:
            apercu = pd.DataFrame()

        colonnes = [str(c) for c in apercu.columns]
        niveau = _deviner_niveau(colonnes, apercu)

        lignes.append({
            "dataset": nom,
            "titre": jeu.titre,
            "statut": "ok" if not apercu.empty else "vide",
            "niveau": niveau,
            "resource_id": ressource.id,
            "colonnes": " | ".join(colonnes[:14]),
            "licence": jeu.licence or "⚠️ absente",
            "modifie_le": jeu.modifie_le,
        })

        marque = {"régional": "✅", "national": "⚠️ ", "indéterminé": "?"}[niveau]
        print(f"    {marque} {nom}")
        print(f"        {niveau} — {', '.join(colonnes[:8])}")

    rapport = pd.DataFrame(lignes)
    chemin = config.BASE_DIR / f"sondage_{portail}.csv"
    rapport.to_csv(chemin, index=False, encoding="utf-8-sig")

    if "niveau" in rapport.columns:
        regionaux = (rapport["niveau"] == "régional").sum()
        print(f"\n  {regionaux} jeu(x) ventilé(s) par région sur "
              f"{len(rapport)} sondés.")
        if not regionaux:
            print("  ⚠️  Aucun jeu régional : le portail ne servira qu'au "
                  "niveau national.")
    print(f"  Rapport écrit : {chemin.name}\n")
    return rapport


_INDICES_REGION = ("region", "rgion", "regions", "zone", "territoire",
                   "departement", "dpartement", "commune", "localite",
                   "adm1", "adm2", "milieu")


def _deviner_niveau(colonnes: list[str], apercu: pd.DataFrame) -> str:
    """Devine si un tableau est ventile geographiquement."""
    from pipeline import normaliser_cle, normaliser_region

    for colonne in colonnes:
        cle = normaliser_cle(colonne).replace(" ", "")
        if any(indice in cle for indice in _INDICES_REGION):
            return "régional"

    # Pas de colonne evidente : chercher des noms de region dans les valeurs
    for colonne in colonnes:
        try:
            valeurs = apercu[colonne].dropna().astype(str).head(5)
        except Exception:
            continue
        if sum(1 for v in valeurs if normaliser_region(v)) >= 2:
            return "régional"

    return "national" if colonnes else "indéterminé"


def ingerer_agricole(maximum: int | None = None) -> dict[str, pd.DataFrame]:
    """
    Ingestion ciblee des donnees agricoles d'AgriData.

    Repond au trou D13 de DATA_INVENTORY.md : la production agricole
    regionale etait la seule brique du prototype sans source verifiee.
    """
    client = ClientCkan("agridata")
    recoltes: dict[str, pd.DataFrame] = {}

    # 1. Ressources documentees publiquement
    identifiants = list(RESSOURCES_CONNUES_AGRIDATA)

    # 2. Complement par le catalogue, sur mots-cles agricoles
    try:
        for jeu in client.rechercher():
            pertinent = any(
                mot in (jeu.titre + jeu.notes + jeu.nom).lower()
                for mot in ("agricol", "production", "culture", "rendement",
                            "superficie", "campagne", "arachide", "mil",
                            "riz", "mais", "horticol")
            )
            if not pertinent:
                continue
            for ressource in jeu.ressources:
                if ressource.interrogeable and ressource.id not in identifiants:
                    identifiants.append(ressource.id)
    except ErreurCkan as erreur:
        print(f"  Catalogue inaccessible ({erreur}).")
        print("  Repli sur les ressources documentées uniquement.\n")

    for resource_id in identifiants:
        try:
            df = extraire(resource_id, "agridata", maximum=maximum)
            if not df.empty:
                recoltes[resource_id] = df
        except ErreurCkan as erreur:
            print(f"  Échec sur {resource_id} : {erreur}")

    print(f"\n  {len(recoltes)} ressource(s) ingérée(s) dans {config.RAW_DIR}")
    if recoltes:
        print("  Relancez l'application : pipeline.py les détectera "
              "automatiquement.")
    return recoltes


# ==========================================================================
# CLI
# ==========================================================================

def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(
        description="Client CKAN pour les portails Open Data de l'ANSD.")
    sous = analyseur.add_subparsers(dest="commande")

    p = sous.add_parser("explorer", help="cartographier un portail")
    p.add_argument("--portail", default="agridata", choices=list(PORTAILS))

    p = sous.add_parser("dataset", help="détail d'un jeu de données")
    p.add_argument("nom")
    p.add_argument("--portail", default="agridata", choices=list(PORTAILS))

    p = sous.add_parser("extraire", help="télécharger une ressource")
    p.add_argument("resource_id")
    p.add_argument("--portail", default="agridata", choices=list(PORTAILS))
    p.add_argument("--nom", default=None)
    p.add_argument("--max", type=int, default=None)

    p = sous.add_parser(
        "sonder", help="diagnostic : les jeux prioritaires sont-ils régionaux ?")
    p.add_argument("--priorite", type=int, default=1)
    p.add_argument("--portail", default="agridata", choices=list(PORTAILS))

    sous.add_parser("tout-agricole", help="ingestion agricole complète")

    arguments = analyseur.parse_args(argv)

    if arguments.commande == "explorer":
        explorer(arguments.portail)
    elif arguments.commande == "dataset":
        client = ClientCkan(arguments.portail)
        jeu = client.detail_jeu(arguments.nom)
        print(f"\n  {jeu.titre}")
        print(f"  Organisation : {jeu.organisation}")
        print(f"  Licence      : {jeu.licence or '⚠️ non renseignée'}")
        print(f"  Modifié le   : {jeu.modifie_le}")
        print(f"\n  {jeu.notes}\n")
        for ressource in jeu.ressources:
            marque = "✅ API" if ressource.datastore_actif else "   fichier"
            print(f"  {marque}  {ressource.format:6}  {ressource.id}")
            print(f"            {ressource.nom}")
    elif arguments.commande == "extraire":
        extraire(arguments.resource_id, arguments.portail,
                 arguments.nom, arguments.max)
    elif arguments.commande == "sonder":
        sonder(arguments.priorite, arguments.portail)
    elif arguments.commande == "tout-agricole":
        ingerer_agricole()
    else:
        analyseur.print_help()
        print("\n  Première commande à lancer :")
        print("    python ckan_client.py explorer\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
