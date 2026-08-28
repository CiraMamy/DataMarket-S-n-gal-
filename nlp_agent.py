"""
MODULE 3 - Interface conversationnelle
======================================

L'utilisateur saisit une phrase libre :

    "Je veux ouvrir une superette a Mbour avec 15 millions"

Le module en extrait une intention structuree :

    Intention(secteur="commerce_proximite", regions=["Thies"],
              budget=15_000_000, ville="Mbour", ...)

puis declenche le calcul TAM/SAM/SOM du module 2.

Deux moteurs d'extraction
-------------------------
  1. API Anthropic Claude - comprehension fine, formulations libres,
     francais et wolof francise. Utilise si une cle API est disponible.
  2. Analyseur local (regex + lexiques) - aucun appel reseau, aucun cout.
     Sert de repli automatique si l'API est absente ou en erreur.

Le champ `Intention.moteur` indique toujours quel moteur a produit le
resultat, et `Intention.confiance` donne un indice de fiabilite.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field

import config
import territory
from pipeline import JeuDeDonnees
from market import ResultatMarche, calculer


# ==========================================================================
# Structure d'intention
# ==========================================================================

@dataclass
class Intention:
    """Intention structuree extraite d'une phrase libre."""

    secteur: str = "commerce_proximite"
    regions: list[str] = field(default_factory=list)
    ville: str | None = None
    budget: float | None = None
    part_geographique: float | None = None
    part_marche_visee: float | None = None
    activite_brute: str | None = None
    confiance: float = 0.5
    moteur: str = "local"
    notes: list[str] = field(default_factory=list)

    def resume(self) -> str:
        lieu = self.ville or (
            ", ".join(config.REGIONS_AFFICHAGE.get(r, r) for r in self.regions)
            if self.regions else "national"
        )
        secteur = config.SECTEURS[self.secteur]["libelle"]
        budget = config.formater_fcfa(self.budget) if self.budget else "non précisé"
        return f"{secteur} — {lieu} — budget {budget}"


# ==========================================================================
# Lexiques de l'analyseur local
# ==========================================================================

_MOTS_SECTEURS: dict[str, list[str]] = {
    "commerce_proximite": [
        "superette", "supérette", "boutique", "epicerie", "épicerie",
        "commerce", "magasin", "alimentation generale", "mini market",
        "minimarket", "supermarche", "supermarché", "libre service",
        "quincaillerie", "detail", "détail", "vente", "kiosque",
        "boutik", "commerce de proximite", "grande surface", "marche",
        "distribution", "point de vente", "shop", "store",
    ],
    "restauration_sante": [
        "restaurant", "restauration", "diabete", "diabète", "diabetique",
        "diabétique", "sante", "santé", "dietetique", "diététique",
        "nutrition", "repas equilibre", "repas équilibré", "traiteur",
        "cantine", "fast food", "snack", "food", "cuisine", "plat",
        "gargote", "tangana", "sans sucre", "indice glycemique",
        "glycemique", "glycémique", "bio", "vegan", "healthy",
        "livraison de repas", "dark kitchen", "hypertension",
    ],
    "agrobusiness": [
        "agrobusiness", "agro business", "agro-industrie", "agroalimentaire",
        "transformation", "usine", "agriculture", "agricole", "ferme",
        "cereale", "céréale", "arachide", "mil", "riz", "mais", "maïs",
        "horticulture", "maraichage", "maraîchage", "jus", "conserve",
        "sechage", "séchage", "minoterie", "huilerie", "decorticage",
        "décorticage", "cereales", "produits locaux", "farine",
        "transformer", "unite de production", "unité de production",
        "elevage", "élevage", "peche", "pêche", "anacarde", "mangue",
    ],
}

# Multiplicateurs de montants
_MULTIPLICATEURS = [
    (r"\b(?:milliards?|mds?|md)\b", 1_000_000_000),
    (r"\b(?:millions?|m|mio)\b", 1_000_000),
    (r"\b(?:milles?|mille|k)\b", 1_000),
]

_NOMBRES_LETTRES = {
    "un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5,
    "six": 6, "sept": 7, "huit": 8, "neuf": 9, "dix": 10, "onze": 11,
    "douze": 12, "quinze": 15, "vingt": 20, "vingt-cinq": 25,
    "trente": 30, "quarante": 40, "cinquante": 50, "soixante": 60,
    "cent": 100, "cents": 100,
}


def _sans_accent(t: str) -> str:
    nfkd = unicodedata.normalize("NFKD", str(t))
    return "".join(c for c in nfkd if not unicodedata.combining(c))


# ==========================================================================
# Analyseur local (repli, zero cout)
# ==========================================================================

def analyser_local(phrase: str) -> Intention:
    """Extraction par lexiques et expressions regulieres. Aucun appel reseau."""
    intention = Intention(moteur="local")
    if not phrase or not phrase.strip():
        intention.regions = list(config.REGIONS)
        intention.confiance = 0.0
        intention.notes.append(
            "Phrase vide : périmètre national et secteur par défaut appliqués.")
        return intention

    texte = _sans_accent(phrase.lower())
    texte_espace = f" {re.sub(r'[^a-z0-9 ]+', ' ', texte)} "
    texte_espace = re.sub(r"\s+", " ", texte_espace)

    # ---- Secteur -------------------------------------------------------
    scores: dict[str, int] = {}
    trouve_brut = None
    for secteur, mots in _MOTS_SECTEURS.items():
        score = 0
        for mot in mots:
            mot_norm = _sans_accent(mot.lower())
            if f" {mot_norm} " in texte_espace:
                # Les termes longs et specifiques pesent plus lourd
                score += 3 if len(mot_norm) > 8 else 2
                if trouve_brut is None:
                    trouve_brut = mot
            elif mot_norm in texte:
                score += 1
                if trouve_brut is None:
                    trouve_brut = mot
        if score:
            scores[secteur] = score

    if scores:
        intention.secteur = max(scores, key=scores.get)
        intention.activite_brute = trouve_brut
        meilleur = scores[intention.secteur]
        total = sum(scores.values())
        intention.confiance = 0.55 + 0.35 * (meilleur / total) if total else 0.55
    else:
        intention.notes.append(
            "Aucun secteur reconnu : commerce de proximité appliqué par défaut.")
        intention.confiance = 0.3

    # ---- Lieu ----------------------------------------------------------
    # Priorite aux villes (plus specifiques) puis aux regions
    meilleure_ville, longueur_max = None, 0
    for ville, region in config.VILLES_VERS_REGION.items():
        ville_norm = _sans_accent(ville.lower())
        if f" {ville_norm} " in texte_espace and len(ville_norm) > longueur_max:
            meilleure_ville, longueur_max = ville, len(ville_norm)
            intention.regions = [region]

    if meilleure_ville:
        intention.ville = meilleure_ville.title()
        intention.confiance = min(intention.confiance + 0.1, 0.95)
        resolution = territory.resoudre_territoire(intention.ville)
        if resolution and resolution.ambigu:
            intention.notes.append(resolution.note)
    else:
        from pipeline import normaliser_region

        for region in config.REGIONS:
            for variante in {region, config.REGIONS_AFFICHAGE.get(region, region)}:
                v = _sans_accent(variante.lower())
                if f" {v} " in texte_espace:
                    if region not in intention.regions:
                        intention.regions.append(region)

    if not intention.regions:
        if re.search(r"\b(senegal|national|tout le pays|pays entier)\b", texte):
            intention.regions = list(config.REGIONS)
            intention.notes.append("Périmètre national détecté.")
        else:
            intention.regions = list(config.REGIONS)
            intention.notes.append(
                "Aucune localisation détectée : périmètre national appliqué.")
            intention.confiance = max(intention.confiance - 0.1, 0.2)

    # ---- Budget --------------------------------------------------------
    intention.budget = _extraire_budget(texte)
    if intention.budget:
        intention.confiance = min(intention.confiance + 0.05, 0.95)

    # ---- Part de marche visee explicite --------------------------------
    m = re.search(r"(\d{1,2}(?:[.,]\d+)?)\s*(?:%|pour ?cent|pourcent)", texte)
    if m:
        intention.part_marche_visee = float(m.group(1).replace(",", ".")) / 100

    # ---- Ajustement de la zone de chalandise ---------------------------
    if intention.ville:
        # Une ville seule ne couvre qu'une fraction de sa region
        part = _part_ville_dans_region(intention.ville, intention.regions[0])
        intention.part_geographique = part
        intention.notes.append(
            f"Zone de chalandise estimée à {part:.0%} de la région "
            f"{config.REGIONS_AFFICHAGE.get(intention.regions[0], '')} "
            f"(ville de {intention.ville})."
        )

    if re.search(r"\b(quartier|coin|rue|voisinage)\b", texte):
        intention.part_geographique = min(intention.part_geographique or 0.2, 0.03)
        intention.notes.append("Échelle « quartier » détectée : SAM restreint.")

    return intention


_POIDS_VILLES = {
    # Villes majeures : part approximative de la population regionale
    "Dakar": 0.30, "Pikine": 0.28, "Guediawaye": 0.09, "Rufisque": 0.20,
    "Keur Massar": 0.13, "Diamniadio": 0.02,
    "Thies": 0.16, "Mbour": 0.38, "Tivaouane": 0.12, "Saly": 0.04,
    "Touba": 0.55, "Mbacke": 0.10, "Diourbel": 0.15, "Bambey": 0.08,
    "Kaolack": 0.28, "Nioro": 0.10,
    "Saint-Louis": 0.25, "Richard-Toll": 0.12, "Dagana": 0.08, "Podor": 0.12,
    "Louga": 0.20, "Dahra": 0.10, "Linguere": 0.10, "Kebemer": 0.10,
    "Fatick": 0.12, "Sokone": 0.06, "Foundiougne": 0.08,
    "Tambacounda": 0.25, "Bakel": 0.10, "Koumpentoum": 0.08,
    "Kolda": 0.22, "Velingara": 0.15,
    "Matam": 0.15, "Ourossogui": 0.10, "Kanel": 0.12,
    "Kaffrine": 0.20, "Koungheul": 0.12,
    "Ziguinchor": 0.40, "Bignona": 0.20, "Cap Skirring": 0.03,
    "Sedhiou": 0.20, "Goudomp": 0.15,
    "Kedougou": 0.35, "Saraya": 0.20,
}


def _part_ville_dans_region(ville: str, region: str) -> float:
    """Part estimee de la population regionale couverte par une ville."""
    for nom, part in _POIDS_VILLES.items():
        if _sans_accent(nom.lower()) == _sans_accent(ville.lower()):
            return part
    return 0.15  # ville secondaire par defaut


def _extraire_budget(texte: str) -> float | None:
    """Extrait un montant en FCFA d'une phrase en francais."""
    texte = texte.replace("f cfa", "fcfa").replace("franc cfa", "fcfa")

    # Forme "15 millions", "2,5 millions", "300 mille", "1 milliard"
    for motif_unite, multiplicateur in _MULTIPLICATEURS:
        motif = r"(\d+(?:[.,]\d+)?)\s*" + motif_unite
        m = re.search(motif, texte)
        if m:
            valeur = float(m.group(1).replace(",", "."))
            return valeur * multiplicateur

    # Forme "quinze millions" (nombres en lettres)
    for mot, valeur in _NOMBRES_LETTRES.items():
        for motif_unite, multiplicateur in _MULTIPLICATEURS:
            if re.search(rf"\b{mot}\s*{motif_unite}", texte):
                return valeur * multiplicateur

    # Forme "budget de 15000000" ou "8 000 000 fcfa"
    m = re.search(
        r"(?:budget|capital|investir|investissement|dispose de|avec)\D{0,15}"
        r"([\d][\d\s.,]{2,})",
        texte,
    )
    if m:
        brut = re.sub(r"[^\d]", "", m.group(1))
        if brut and len(brut) >= 5:
            return float(brut)

    m = re.search(r"([\d][\d\s.,]{4,})\s*(?:fcfa|cfa|xof)", texte)
    if m:
        brut = re.sub(r"[^\d]", "", m.group(1))
        if brut:
            return float(brut)

    return None


# ==========================================================================
# Moteur API Claude
# ==========================================================================

_SYSTEME = """Tu es le moteur d'analyse d'intention de DataMarket Sénégal, une \
plateforme d'intelligence économique destinée aux entrepreneurs sénégalais.

Ta tâche : convertir la phrase d'un entrepreneur en un objet JSON structuré.

SECTEURS AUTORISÉS (choisis exactement une valeur) :
- "commerce_proximite" : supérette, boutique, épicerie, magasin, commerce de \
détail alimentaire, distribution.
- "restauration_sante" : restaurant, traiteur, cantine, plats préparés, \
alimentation santé, diabète, diététique, nutrition.
- "agrobusiness" : transformation agroalimentaire, usine, minoterie, huilerie, \
séchage, jus, conserves, production agricole valorisée.

RÉGIONS AUTORISÉES (les 14 régions du Sénégal, orthographe exacte, sans accent) :
Dakar, Thies, Diourbel, Kaolack, Saint-Louis, Louga, Fatick, Tambacounda, \
Kolda, Matam, Kaffrine, Ziguinchor, Sedhiou, Kedougou

Si l'utilisateur cite une VILLE, renvoie la région qui la contient et indique \
la ville dans le champ "ville". Exemples : Mbour et Saly -> Thies ; Touba et \
Mbacké -> Diourbel ; Pikine, Guédiawaye et Rufisque -> Dakar ; Richard-Toll -> \
Saint-Louis ; Ourossogui -> Matam.

Si aucun lieu n'est cité, renvoie la liste des 14 régions.

RÉPONDS UNIQUEMENT PAR UN OBJET JSON VALIDE, sans texte avant ni après, \
sans bloc de code markdown, au format :

{
  "secteur": "commerce_proximite",
  "regions": ["Thies"],
  "ville": "Mbour",
  "budget": 15000000,
  "part_geographique": 0.38,
  "part_marche_visee": null,
  "activite_brute": "supérette",
  "confiance": 0.92,
  "raisonnement": "Une phrase expliquant l'interprétation."
}

RÈGLES SUR LES CHAMPS :
- "budget" : montant en FCFA, nombre entier, ou null si non précisé. \
"15 millions" = 15000000. "2,5 millions" = 2500000.
- "part_geographique" : entre 0 et 1, part de la population régionale couverte \
par la zone de chalandise. Une ville moyenne dans sa région ≈ 0.15 à 0.40 ; \
un quartier ≈ 0.02 à 0.05 ; toute la région = 1.0. null si indéterminable.
- "part_marche_visee" : entre 0 et 1, uniquement si l'utilisateur exprime une \
ambition de part de marché explicite. Sinon null.
- "confiance" : entre 0 et 1, ta certitude sur l'interprétation globale.
"""


def analyser_avec_claude(phrase: str, cle_api: str | None = None) -> Intention | None:
    """
    Extraction via l'API Anthropic. Retourne None en cas d'echec
    (cle absente, SDK non installe, reseau, JSON invalide), ce qui
    declenche le repli sur l'analyseur local.
    """
    cle = cle_api or config.get_api_key()
    if not cle:
        return None

    try:
        import anthropic
    except ImportError:
        return None

    try:
        client = anthropic.Anthropic(api_key=cle)
        reponse = client.messages.create(
            model=config.ANTHROPIC_MODEL,
            max_tokens=config.ANTHROPIC_MAX_TOKENS,
            system=_SYSTEME,
            messages=[{"role": "user", "content": phrase}],
        )
        brut = "".join(
            bloc.text for bloc in reponse.content if getattr(bloc, "type", "") == "text"
        ).strip()
    except Exception:
        return None

    donnees = _extraire_json(brut)
    if donnees is None:
        return None

    return _valider(donnees, phrase)


def _extraire_json(texte: str) -> dict | None:
    """Extrait le premier objet JSON valide d'une reponse texte."""
    texte = texte.strip()
    texte = re.sub(r"^```(?:json)?\s*|\s*```$", "", texte, flags=re.MULTILINE).strip()
    try:
        return json.loads(texte)
    except json.JSONDecodeError:
        pass
    debut = texte.find("{")
    fin = texte.rfind("}")
    if debut != -1 and fin > debut:
        try:
            return json.loads(texte[debut:fin + 1])
        except json.JSONDecodeError:
            return None
    return None


def _valider(donnees: dict, phrase: str) -> Intention:
    """
    Valide et borne la sortie du modele. Toute valeur aberrante est
    corrigee plutot que propagee.
    """
    intention = Intention(moteur="claude")
    notes: list[str] = []

    # Secteur
    secteur = str(donnees.get("secteur", "")).strip()
    if secteur in config.SECTEURS:
        intention.secteur = secteur
    else:
        repli = analyser_local(phrase)
        intention.secteur = repli.secteur
        notes.append(
            f"Secteur '{secteur}' non reconnu : '{intention.secteur}' retenu "
            "par analyse locale.")

    # Regions
    regions_brutes = donnees.get("regions") or []
    if isinstance(regions_brutes, str):
        regions_brutes = [regions_brutes]
    from pipeline import normaliser_region

    regions = []
    for r in regions_brutes:
        norm = normaliser_region(r)
        if norm and norm not in regions:
            regions.append(norm)
    intention.regions = regions or list(config.REGIONS)
    if not regions:
        notes.append("Aucune région valide renvoyée : périmètre national appliqué.")

    # Ville
    ville = donnees.get("ville")
    if isinstance(ville, str) and ville.strip():
        intention.ville = ville.strip().title()
        resolution = territory.resoudre_territoire(intention.ville)
        if resolution and resolution.ambigu:
            notes.append(resolution.note)

    # Budget
    budget = donnees.get("budget")
    if isinstance(budget, (int, float)) and budget > 0:
        if budget < 50_000:
            notes.append(
                f"Budget de {budget:,.0f} FCFA jugé improbable : ignoré.")
        else:
            intention.budget = float(budget)
    elif budget is not None:
        repli_budget = _extraire_budget(_sans_accent(phrase.lower()))
        if repli_budget:
            intention.budget = repli_budget

    # Parts
    for champ in ("part_geographique", "part_marche_visee"):
        valeur = donnees.get(champ)
        if isinstance(valeur, (int, float)):
            v = float(valeur)
            if v > 1:                      # tolere une saisie en pourcentage
                v = v / 100
            if 0 < v <= 1:
                setattr(intention, champ, v)

    intention.activite_brute = donnees.get("activite_brute")

    confiance = donnees.get("confiance")
    intention.confiance = (
        float(confiance) if isinstance(confiance, (int, float)) and 0 <= confiance <= 1
        else 0.75
    )

    raisonnement = donnees.get("raisonnement")
    if isinstance(raisonnement, str) and raisonnement.strip():
        notes.append(raisonnement.strip())

    intention.notes = notes
    return intention


# ==========================================================================
# Point d'entree du module
# ==========================================================================

def analyser(phrase: str, cle_api: str | None = None,
             forcer_local: bool = False) -> Intention:
    """
    Analyse une phrase libre. Tente l'API Claude puis retombe sur
    l'analyseur local. Ne leve jamais d'exception.
    """
    if not forcer_local:
        via_api = analyser_avec_claude(phrase, cle_api)
        if via_api is not None:
            return via_api

    intention = analyser_local(phrase)
    if not forcer_local:
        intention.notes.append(
            "Analyse effectuée en local (API Claude indisponible ou clé absente).")
    return intention


def interroger(jeu: JeuDeDonnees, phrase: str, cle_api: str | None = None,
               forcer_local: bool = False) -> tuple[Intention, ResultatMarche]:
    """
    Chaine complete : phrase libre -> intention -> etude de marche.

    >>> jeu = charger_donnees()
    >>> intention, resultat = interroger(jeu, "Je veux ouvrir une supérette à Mbour")
    >>> resultat.som
    """
    intention = analyser(phrase, cle_api=cle_api, forcer_local=forcer_local)
    resultat = calculer(
        jeu,
        secteur=intention.secteur,
        regions=intention.regions,
        part_geographique=intention.part_geographique,
        part_marche_visee=intention.part_marche_visee,
        budget=intention.budget,
    )
    return intention, resultat


def redaction_synthese(intention: Intention, resultat: ResultatMarche,
                       cle_api: str | None = None) -> str | None:
    """
    Genere un commentaire strategique en francais a partir des chiffres
    calcules. Retourne None si l'API n'est pas disponible : l'application
    affiche alors une synthese factuelle construite localement.

    Les chiffres transmis au modele sont ceux calcules par le module 2 :
    le modele commente, il ne recalcule rien.
    """
    cle = cle_api or config.get_api_key()
    if not cle:
        return None

    try:
        import anthropic
    except ImportError:
        return None

    top = resultat.detail_regional.head(5)[["region", "tam_region"]]
    classement = "\n".join(
        f"- {config.REGIONS_AFFICHAGE.get(r.region, r.region)} : "
        f"{config.formater_fcfa(r.tam_region)}"
        for r in top.itertuples()
    )

    contexte = f"""Étude de marché calculée par DataMarket Sénégal.

Projet : {intention.resume()}
Secteur : {resultat.libelle}
Périmètre : {resultat.perimetre}
Population cible : {config.formater_nombre(resultat.population_cible)} personnes

TAM : {config.formater_fcfa(resultat.tam)}
SAM : {config.formater_fcfa(resultat.sam)} \
({100 * resultat.sam / resultat.tam:.1f} % du TAM)
SOM : {config.formater_fcfa(resultat.som)} \
({100 * resultat.som / resultat.tam:.2f} % du TAM)
Chiffre d'affaires mensuel visé : {config.formater_fcfa(resultat.ca_mensuel_som)}

Régions les plus porteuses :
{classement}

Sources : RGPH-5 2023 (ANSD) pour la population, EHCVM II 2021-2022 pour les \
dépenses de consommation, EAA/DAPSA pour la production agricole.
"""

    consigne = """Rédige une synthèse stratégique en français à destination d'un \
entrepreneur sénégalais, en 4 paragraphes courts et sans titre :

1. Ce que révèlent ces chiffres sur la taille réelle de l'opportunité.
2. Deux à trois facteurs de risque concrets et propres au marché sénégalais.
3. Deux recommandations opérationnelles précises pour les 12 premiers mois.
4. Une phrase de mise en garde sur les limites méthodologiques de l'estimation.

Contraintes : ton direct et professionnel, pas de langue de bois, pas de \
listes à puces, pas de titres. Reprends les montants tels qu'ils te sont \
fournis sans en recalculer aucun. Maximum 300 mots au total."""

    try:
        client = anthropic.Anthropic(api_key=cle)
        reponse = client.messages.create(
            model=config.ANTHROPIC_MODEL,
            max_tokens=1200,
            messages=[{"role": "user", "content": contexte + "\n\n" + consigne}],
        )
        return "".join(
            b.text for b in reponse.content if getattr(b, "type", "") == "text"
        ).strip()
    except Exception:
        return None


def synthese_locale(intention: Intention, resultat: ResultatMarche,
                    lang: str = "fr") -> str:
    """Synthese factuelle construite sans appel API."""
    from i18n import t

    detail = resultat.detail_regional
    tete = detail.iloc[0] if len(detail) else None
    part_sam = 100 * resultat.sam / resultat.tam if resultat.tam else 0
    part_som = 100 * resultat.som / resultat.tam if resultat.tam else 0
    secteur_libelle = config.libelle_secteur(resultat.secteur, lang)

    lignes = [
        t("synth_ligne1", lang, perimetre=resultat.perimetre,
          secteur=secteur_libelle, tam=config.formater_fcfa(resultat.tam),
          population=config.formater_nombre(resultat.population_cible)),
        t("synth_ligne2", lang, sam=config.formater_fcfa(resultat.sam),
          part_sam=f"{part_sam:.1f}", som=config.formater_fcfa(resultat.som),
          part_som=f"{part_som:.2f}",
          ca_mensuel=config.formater_fcfa(resultat.ca_mensuel_som)),
    ]

    transactions = resultat.clients_potentiels()
    if transactions:
        ticket = resultat.hypotheses.get("ticket_moyen_fcfa", 0)
        lignes.append(t(
            "synth_transactions", lang, ticket=config.formater_fcfa(ticket),
            transactions=config.formater_nombre(transactions / 365)))

    if tete is not None and len(detail) > 1:
        lignes.append(t(
            "synth_region_porteuse", lang,
            region=config.REGIONS_AFFICHAGE.get(tete.region, tete.region),
            part=f"{tete.part_tam_pct:.1f}"))

    lignes.append(t("synth_avertissement_final", lang))
    return "\n\n".join(lignes)


if __name__ == "__main__":
    from pipeline import charger_donnees

    jeu = charger_donnees()

    exemples = [
        "Je veux ouvrir une supérette à Mbour",
        "Restaurant pour diabétiques à Dakar avec 25 millions de budget",
        "Monter une unité de transformation d'arachide à Kaolack",
        "Une boutique de quartier à Touba, budget 3 millions",
        "Je souhaite lancer un traiteur santé sur tout le Sénégal",
    ]

    for phrase in exemples:
        intention, resultat = interroger(jeu, phrase, forcer_local=True)
        print(f"\n>>> {phrase}")
        print(f"    Interprétation : {intention.resume()}")
        print(f"    Moteur : {intention.moteur} | "
              f"Confiance : {intention.confiance:.0%}")
        print(f"    TAM {config.formater_fcfa(resultat.tam)} | "
              f"SAM {config.formater_fcfa(resultat.sam)} | "
              f"SOM {config.formater_fcfa(resultat.som)}")
