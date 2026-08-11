"""
MODULE 4 (partie export) - Generation du rapport PDF
====================================================

Produit une etude de marche exportable de 3 a 4 pages :

  Page 1  Couverture, synthese chiffree, entonnoir TAM/SAM/SOM
  Page 2  Detail region par region
  Page 3  Hypotheses de calcul et methodologie
  Page 4  Sources, avertissements et limites

Dependance unique : reportlab (pur Python, aucun binaire externe).
Aucune image n'est requise : les graphiques sont redessines en vectoriel
directement dans le PDF, ce qui evite la dependance a kaleido/chrome.
"""

from __future__ import annotations

import datetime as _dt
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Flowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

import config
from market import ResultatMarche

VERT = colors.HexColor("#00853F")
VERT_SOMBRE = colors.HexColor("#00441B")
VERT_CLAIR = colors.HexColor("#C7E9C0")
JAUNE = colors.HexColor("#FDEF42")
GRIS = colors.HexColor("#5A6B72")
GRIS_CLAIR = colors.HexColor("#EEF2EE")
SOMBRE = colors.HexColor("#1B2A32")


# ==========================================================================
# Styles
# ==========================================================================

def _styles():
    base = getSampleStyleSheet()
    return {
        "titre": ParagraphStyle(
            "titre", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=25, leading=29, textColor=VERT_SOMBRE, spaceAfter=6),
        "sous_titre": ParagraphStyle(
            "sous_titre", parent=base["Normal"], fontName="Helvetica",
            fontSize=13, leading=17, textColor=GRIS, spaceAfter=16),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=14, leading=18, textColor=VERT_SOMBRE,
            spaceBefore=16, spaceAfter=8),
        "h3": ParagraphStyle(
            "h3", parent=base["Heading3"], fontName="Helvetica-Bold",
            fontSize=11, leading=14, textColor=SOMBRE,
            spaceBefore=10, spaceAfter=5),
        "corps": ParagraphStyle(
            "corps", parent=base["Normal"], fontName="Helvetica",
            fontSize=9.5, leading=14, alignment=TA_JUSTIFY, spaceAfter=7),
        "petit": ParagraphStyle(
            "petit", parent=base["Normal"], fontName="Helvetica",
            fontSize=8, leading=11, textColor=GRIS, spaceAfter=4),
        "cellule": ParagraphStyle(
            "cellule", parent=base["Normal"], fontName="Helvetica",
            fontSize=8, leading=10.5),
        "centre": ParagraphStyle(
            "centre", parent=base["Normal"], fontName="Helvetica",
            fontSize=9, leading=12, alignment=TA_CENTER, textColor=GRIS),
    }


# ==========================================================================
# Entonnoir vectoriel
# ==========================================================================

class Entonnoir(Flowable):
    """Entonnoir TAM/SAM/SOM dessine en vectoriel (sans dependance graphique)."""

    def __init__(self, tam: float, sam: float, som: float,
                 largeur: float = 16 * cm, hauteur: float = 5.4 * cm):
        super().__init__()
        self.tam, self.sam, self.som = tam, sam, som
        self.width, self.height = largeur, hauteur

    def draw(self):
        c = self.canv
        valeurs = [
            ("TAM", self.tam, VERT_SOMBRE, colors.white),
            ("SAM", self.sam, VERT, colors.white),
            ("SOM", self.som, JAUNE, SOMBRE),
        ]
        maxi = max(self.tam, 1)
        h = self.height / 3.35
        ecart = h * 0.14

        for i, (etiquette, valeur, fond, texte) in enumerate(valeurs):
            # Largeur proportionnelle, avec un plancher de lisibilite
            ratio = max((valeur / maxi) ** 0.42, 0.16)
            largeur = self.width * ratio
            x = (self.width - largeur) / 2
            y = self.height - (i + 1) * (h + ecart)

            c.setFillColor(fond)
            c.setStrokeColor(colors.white)
            c.setLineWidth(1.2)
            c.roundRect(x, y, largeur, h, 3, fill=1, stroke=1)

            c.setFillColor(texte)
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(self.width / 2, y + h / 2 + 2, etiquette)
            c.setFont("Helvetica", 8)
            part = f"  ({100 * valeur / maxi:.2f} % du TAM)" if i else ""
            c.drawCentredString(
                self.width / 2, y + h / 2 - 8.5,
                config.formater_fcfa(valeur) + part)


class Filet(Flowable):
    """Filet horizontal de separation."""

    def __init__(self, largeur: float = 16 * cm, couleur=VERT, epaisseur=1.6):
        super().__init__()
        self.width, self.height = largeur, epaisseur + 2
        self.couleur, self.epaisseur = couleur, epaisseur

    def draw(self):
        self.canv.setStrokeColor(self.couleur)
        self.canv.setLineWidth(self.epaisseur)
        self.canv.line(0, 1, self.width, 1)


# ==========================================================================
# Habillage de page
# ==========================================================================

def _habillage(canvas, doc):
    canvas.saveState()
    largeur, hauteur = A4

    # Bandeau superieur
    canvas.setFillColor(VERT_SOMBRE)
    canvas.rect(0, hauteur - 1.15 * cm, largeur, 1.15 * cm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(2 * cm, hauteur - 0.78 * cm, "DataMarket Sénégal")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(largeur - 2 * cm, hauteur - 0.78 * cm,
                           "Étude de marché automatisée")

    # Pied de page
    canvas.setStrokeColor(VERT_CLAIR)
    canvas.setLineWidth(0.8)
    canvas.line(2 * cm, 1.5 * cm, largeur - 2 * cm, 1.5 * cm)
    canvas.setFillColor(GRIS)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(
        2 * cm, 1.05 * cm,
        "Sources : RGPH-5 2023 (ANSD) · EHCVM II 2021-2022 · EAA/DAPSA")
    canvas.drawRightString(largeur - 2 * cm, 1.05 * cm, f"Page {doc.page}")
    canvas.restoreState()


def _tableau(donnees: list[list], largeurs: list[float],
             aligner_droite: list[int] | None = None) -> Table:
    """Tableau au style uniforme de l'application."""
    table = Table(donnees, colWidths=largeurs, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), VERT_SOMBRE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRIS_CLAIR]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D5DDD5")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    for colonne in (aligner_droite or []):
        style.append(("ALIGN", (colonne, 1), (colonne, -1), "RIGHT"))
    table.setStyle(TableStyle(style))
    return table


# ==========================================================================
# Generation
# ==========================================================================

def generer_rapport(
    resultat: ResultatMarche,
    chemin: str | Path | None = None,
    synthese: str | None = None,
    intention_brute: str | None = None,
    potentiel: "object | None" = None,
) -> Path:
    """
    Genere le rapport PDF complet.

    Parametres
    ----------
    resultat : ResultatMarche
        Sortie du module 2.
    chemin : str | Path | None
        Destination. None = exports/etude_<secteur>_<horodatage>.pdf
    synthese : str | None
        Commentaire strategique (module 3). Optionnel.
    intention_brute : str | None
        Phrase saisie par l'utilisateur, reproduite en couverture.
    potentiel : DataFrame | None
        Classement national des regions, ajoute en annexe si fourni.
    """
    horodatage = _dt.datetime.now()
    if chemin is None:
        nom = f"etude_{resultat.secteur}_{horodatage:%Y%m%d_%H%M%S}.pdf"
        chemin = config.EXPORT_DIR / nom
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)

    s = _styles()
    document = SimpleDocTemplate(
        str(chemin),
        pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=1.9 * cm, bottomMargin=2 * cm,
        title=f"Étude de marché — {resultat.libelle}",
        author="DataMarket Sénégal",
        subject=f"TAM/SAM/SOM — {resultat.perimetre}",
    )

    contenu = []
    largeur_utile = 17 * cm

    # ---------------------------------------------------------------- p.1
    contenu.append(Spacer(1, 0.5 * cm))
    contenu.append(Paragraph("Étude de marché", s["titre"]))
    contenu.append(Paragraph(
        f"{resultat.libelle}<br/>{resultat.perimetre}", s["sous_titre"]))
    contenu.append(Filet(largeur_utile))
    contenu.append(Spacer(1, 0.4 * cm))

    if intention_brute:
        contenu.append(Paragraph(
            f'<i>Demande initiale : « {intention_brute} »</i>', s["petit"]))
        contenu.append(Spacer(1, 0.25 * cm))

    # Indicateurs cles
    entetes = ["Indicateur", "Définition", "Montant annuel", "Part du TAM"]
    lignes = [entetes]
    for _, r in resultat.tableau_synthese().iterrows():
        lignes.append([
            Paragraph(f"<b>{r['Indicateur']}</b>", s["cellule"]),
            Paragraph(r["Définition"], s["cellule"]),
            r["Montant lisible"],
            f"{r['% du TAM']:.2f} %",
        ])
    contenu.append(_tableau(
        lignes, [2 * cm, 7 * cm, 4.6 * cm, 2.6 * cm], aligner_droite=[2, 3]))
    contenu.append(Spacer(1, 0.55 * cm))

    contenu.append(Entonnoir(resultat.tam, resultat.sam, resultat.som,
                             largeur_utile))
    contenu.append(Spacer(1, 0.45 * cm))

    # Chiffres complementaires
    complements = [
        ["Population cible", config.formater_nombre(resultat.population_cible)],
        ["Chiffre d'affaires mensuel visé",
         config.formater_fcfa(resultat.ca_mensuel_som)],
        ["Nombre de régions couvertes", str(len(resultat.regions))],
    ]
    transactions = resultat.clients_potentiels()
    if transactions:
        complements.append([
            "Transactions quotidiennes implicites",
            config.formater_nombre(transactions / 365)])
    if resultat.hypotheses.get("budget_fcfa"):
        complements.append([
            "Budget déclaré",
            config.formater_fcfa(resultat.hypotheses["budget_fcfa"])])

    contenu.append(Paragraph("Repères complémentaires", s["h3"]))
    contenu.append(_tableau(
        [["Repère", "Valeur"]] + complements,
        [11 * cm, 6 * cm], aligner_droite=[1]))

    if synthese:
        contenu.append(Paragraph("Lecture stratégique", s["h2"]))
        for paragraphe in [p for p in synthese.split("\n") if p.strip()]:
            contenu.append(Paragraph(paragraphe.strip(), s["corps"]))

    # ---------------------------------------------------------------- p.2
    contenu.append(PageBreak())
    contenu.append(Paragraph("Détail par région", s["h2"]))
    contenu.append(Paragraph(
        "Décomposition du marché adressable sur le périmètre retenu. "
        "La colonne « TAM par habitant » mesure l'intensité du marché "
        "indépendamment du volume de population.", s["corps"]))
    contenu.append(Spacer(1, 0.2 * cm))

    entetes = ["Région", "Population", "Population cible", "Dép./tête",
               "TAM", "SAM", "SOM", "% TAM"]
    lignes = [entetes]
    detail = resultat.detail_regional
    for r in detail.itertuples():
        lignes.append([
            Paragraph(config.REGIONS_AFFICHAGE.get(r.region, r.region), s["cellule"]),
            config.formater_nombre(r.population),
            config.formater_nombre(r.population_cible),
            config.formater_nombre(r.depense_cible_tete),
            config.formater_fcfa(r.tam_region),
            config.formater_fcfa(r.sam_region),
            config.formater_fcfa(r.som_region),
            f"{r.part_tam_pct:.1f}",
        ])
    lignes.append([
        Paragraph("<b>Total</b>", s["cellule"]),
        config.formater_nombre(detail["population"].sum()),
        config.formater_nombre(detail["population_cible"].sum()),
        "—",
        config.formater_fcfa(resultat.tam),
        config.formater_fcfa(resultat.sam),
        config.formater_fcfa(resultat.som),
        "100,0",
    ])

    tableau = _tableau(
        lignes,
        [2.5 * cm, 2.1 * cm, 2.4 * cm, 1.9 * cm, 2.9 * cm, 2.6 * cm,
         2.4 * cm, 1.2 * cm],
        aligner_droite=[1, 2, 3, 4, 5, 6, 7],
    )
    tableau.setStyle(TableStyle([
        ("BACKGROUND", (0, -1), (-1, -1), VERT_CLAIR),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    contenu.append(tableau)

    # ---------------------------------------------------------------- p.3
    contenu.append(PageBreak())
    contenu.append(Paragraph("Méthodologie et hypothèses", s["h2"]))

    contenu.append(Paragraph("Définitions", s["h3"]))
    for sigle, definition in [
        ("TAM", "Total Addressable Market — dépense annuelle totale, sur "
                "l'ensemble du périmètre, sur le poste de consommation "
                "adressé par l'activité. TAM = population cible × dépense "
                "annuelle par tête sur ce poste."),
        ("SAM", "Serviceable Available Market — part du TAM réellement "
                "atteignable compte tenu de la zone de chalandise et du "
                "segment visé. SAM = TAM × part géographique."),
        ("SOM", "Serviceable Obtainable Market — chiffre d'affaires "
                "réalistement capturable à trois ans compte tenu de la "
                "concurrence et du capital engagé. SOM = SAM × part de "
                "marché visée."),
    ]:
        contenu.append(Paragraph(f"<b>{sigle}</b> — {definition}", s["corps"]))

    contenu.append(Paragraph("Modèle sectoriel appliqué", s["h3"]))
    contenu.append(Paragraph(
        config.SECTEURS[resultat.secteur]["description"], s["corps"]))

    contenu.append(Paragraph("Coefficients de calcul", s["h3"]))
    exclues = {"libelle", "description", "poste_depense"}
    lignes = [["Hypothèse", "Valeur"]]
    for cle, valeur in resultat.hypotheses.items():
        if cle in exclues or valeur is None:
            continue
        libelle = cle.replace("_", " ").capitalize()
        if isinstance(valeur, float):
            if 0 < abs(valeur) < 1:
                affichage = f"{valeur:.1%}"
            elif abs(valeur) >= 100_000:
                affichage = config.formater_fcfa(valeur)
            else:
                affichage = f"{valeur:,.2f}".replace(",", " ")
        elif isinstance(valeur, int) and abs(valeur) >= 100_000:
            affichage = config.formater_nombre(valeur)
        else:
            affichage = str(valeur)
        lignes.append([Paragraph(libelle, s["cellule"]), affichage])

    contenu.append(_tableau(lignes, [11 * cm, 6 * cm], aligner_droite=[1]))

    # ---------------------------------------------------------------- p.4
    contenu.append(PageBreak())
    contenu.append(Paragraph("Sources et limites", s["h2"]))

    contenu.append(Paragraph("Sources statistiques", s["h3"]))
    lignes = [
        ["Source", "Usage", "Millésime"],
        [Paragraph("RGPH-5 — 5<sup>e</sup> Recensement général de la "
                   "population et de l'habitat, ANSD", s["cellule"]),
         Paragraph("Population résidente, structure par âge, taux "
                   "d'urbanisation, taille des ménages", s["cellule"]),
         "2023"],
        [Paragraph("EHCVM II — Enquête harmonisée sur les conditions de "
                   "vie des ménages, ANSD", s["cellule"]),
         Paragraph("Dépense de consommation annuelle par tête, "
                   "coefficients budgétaires par poste", s["cellule"]),
         "2021-2022"],
        [Paragraph("EAA / DAPSA — Enquête agricole annuelle", s["cellule"]),
         Paragraph("Production agricole régionale par culture", s["cellule"]),
         "Campagne de référence"],
    ]
    contenu.append(_tableau(lignes, [6.5 * cm, 8 * cm, 2.5 * cm]))
    contenu.append(Spacer(1, 0.3 * cm))

    contenu.append(Paragraph(
        f"Agrégats nationaux de référence : population résidente "
        f"{config.formater_nombre(config.POPULATION_NATIONALE)} habitants "
        f"(RGPH-5 2023) ; dépense de consommation annuelle par tête "
        f"{config.formater_fcfa(config.DEPENSE_ANNUELLE_TETE)} (EHCVM II "
        f"2021-2022) ; taux d'urbanisation "
        f"{config.TAUX_URBANISATION_NATIONAL} %.", s["corps"]))

    if resultat.avertissements:
        contenu.append(Paragraph("Avertissements sur ce calcul", s["h3"]))
        for avertissement in resultat.avertissements:
            contenu.append(Paragraph("• " + avertissement, s["corps"]))

    contenu.append(Paragraph("Limites méthodologiques", s["h3"]))
    for limite in [
        "Les dépenses par tête sont des moyennes régionales. Elles masquent "
        "des écarts de revenu importants à l'intérieur d'une même région, "
        "en particulier entre le centre urbain et sa périphérie rurale.",
        "Le taux de captation du commerce organisé est une hypothèse de "
        "modélisation et non une donnée mesurée. Il conditionne directement "
        "le niveau du TAM et doit être ajusté à la réalité observée sur le "
        "terrain.",
        "Le SOM ne tient pas compte de la concurrence existante à l'échelle "
        "de la rue ou du quartier, qui est le facteur déterminant du "
        "chiffre d'affaires réel d'un commerce de proximité.",
        "Les données EHCVM datent de 2021-2022 et ne reflètent pas "
        "l'inflation intervenue depuis. Les montants exprimés sont en francs "
        "courants de la période d'enquête.",
        "Cette étude est un outil de cadrage et de première décision. Elle "
        "ne se substitue pas à une étude terrain, à un plan de financement "
        "détaillé ni à un avis professionnel.",
    ]:
        contenu.append(Paragraph("• " + limite, s["corps"]))

    contenu.append(Spacer(1, 0.6 * cm))
    contenu.append(Filet(largeur_utile, VERT_CLAIR, 1))
    contenu.append(Spacer(1, 0.2 * cm))
    contenu.append(Paragraph(
        f"Rapport généré le {horodatage:%d/%m/%Y à %H:%M} par "
        f"DataMarket Sénégal.", s["centre"]))

    document.build(contenu, onFirstPage=_habillage, onLaterPages=_habillage)
    return chemin


if __name__ == "__main__":
    from pipeline import charger_donnees
    from market import calculer

    jeu = charger_donnees()
    r = calculer(jeu, "commerce_proximite", regions=["Thies"],
                 part_geographique=0.38, budget=15_000_000)
    sortie = generer_rapport(
        r, intention_brute="Je veux ouvrir une supérette à Mbour")
    print(f"Rapport généré : {sortie}")
