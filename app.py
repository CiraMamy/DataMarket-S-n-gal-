"""
DataMarket Senegal - Application Streamlit
==========================================
Assemble les quatre modules du MVP.

Lancement :
    streamlit run app.py
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

import config
import dashboard
import geo as geo_module
import market
import nlp_agent
from pipeline import charger_donnees
from report import generer_rapport

st.set_page_config(
    page_title="DataMarket Sénégal",
    page_icon="🇸🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container { padding-top: 2.2rem; max-width: 1400px; }
      h1, h2, h3 { color: #00441B; }
      div[data-testid="stMetricValue"] { font-size: 1.55rem; color: #00441B; }
      div[data-testid="stMetric"] {
          background: #F5F9F5; border: 1px solid #DCE8DC;
          border-radius: 10px; padding: 14px 16px;
      }
      .bandeau {
          background: linear-gradient(100deg, #00441B 0%, #00853F 55%, #41AB5D 100%);
          padding: 22px 28px; border-radius: 12px; color: white;
          margin-bottom: 22px;
      }
      .bandeau h1 { color: white !important; margin: 0; font-size: 1.9rem; }
      .bandeau p { color: rgba(255,255,255,0.9); margin: 6px 0 0 0;
                   font-size: 0.95rem; }
      .encart {
          background: #F5F9F5; border-left: 4px solid #00853F;
          padding: 14px 18px; border-radius: 6px; margin: 10px 0;
      }
      .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================================
# Chargement (mis en cache)
# ==========================================================================

@st.cache_data(show_spinner="Chargement des données ANSD…")
def _donnees():
    return charger_donnees()


@st.cache_data(show_spinner="Chargement des frontières régionales…")
def _geographie():
    return geo_module.charger_geographie()


@st.cache_data(show_spinner=False)
def _potentiel(secteur: str):
    return market.potentiel_par_region(_donnees(), secteur)


jeu = _donnees()
geographie = _geographie()

if "resultat" not in st.session_state:
    st.session_state.resultat = None
    st.session_state.intention = None
    st.session_state.phrase = ""
    st.session_state.synthese = None


# ==========================================================================
# Lien permanent partageable (reproductibilite)
# ==========================================================================
# Les parametres d'une etude sont encodes dans l'URL. Quiconque ouvre le
# lien retrouve exactement le meme calcul, sans avoir a re-decrire son
# projet ni a re-regler les curseurs.

def _maj_lien_partage(secteur: str, regions: list[str], part_geo: float,
                      part_som: float, budget: float | None,
                      phrase: str) -> None:
    st.query_params["secteur"] = secteur
    st.query_params["regions"] = ",".join(regions) if regions else ""
    st.query_params["zone"] = f"{part_geo:.4f}"
    st.query_params["part"] = f"{part_som:.4f}"
    if budget:
        st.query_params["budget"] = f"{budget:.0f}"
    if phrase:
        st.query_params["phrase"] = phrase


def _etude_depuis_lien() -> tuple[nlp_agent.Intention, market.ResultatMarche] | None:
    qp = st.query_params
    if "secteur" not in qp or qp["secteur"] not in config.SECTEURS:
        return None
    secteur = qp["secteur"]
    regions = [r for r in qp.get("regions", "").split(",") if r in config.REGIONS]
    try:
        part_geo = float(qp["zone"]) if qp.get("zone") else None
        part_som = float(qp["part"]) if qp.get("part") else None
        budget = float(qp["budget"]) if qp.get("budget") else None
    except ValueError:
        return None

    resultat = market.calculer(
        jeu, secteur, regions=regions or None,
        part_geographique=part_geo, part_marche_visee=part_som, budget=budget)
    intention = nlp_agent.Intention(
        secteur=secteur, regions=regions, budget=budget,
        part_geographique=part_geo, part_marche_visee=part_som,
        confiance=1.0, moteur="lien",
        notes=["Étude reconstituée depuis un lien partagé."])
    return intention, resultat


def _export_json(resultat: market.ResultatMarche, phrase: str) -> str:
    """Export complet et reproductible : entrees, hypotheses, sorties."""
    donnees = {
        "genere_le": datetime.now(timezone.utc).isoformat(),
        "entrees": {
            "phrase_saisie": phrase or None,
            "secteur": resultat.secteur,
            "regions": resultat.regions,
            "budget_fcfa": resultat.hypotheses.get("budget_fcfa"),
        },
        "hypotheses": {
            k: v for k, v in resultat.hypotheses.items()
            if k not in {"libelle", "description", "poste_depense"}
        },
        "provenance": resultat.provenance,
        "resultats": {
            "tam_fcfa": resultat.tam,
            "sam_fcfa": resultat.sam,
            "som_fcfa": resultat.som,
            "population_cible": resultat.population_cible,
            "ca_mensuel_som_fcfa": resultat.ca_mensuel_som,
        },
        "avertissements": resultat.avertissements,
        "detail_regional": resultat.detail_regional.to_dict(orient="records"),
        "lien_reproductible": {
            "secteur": resultat.secteur,
            "regions": ",".join(resultat.regions),
            "zone": resultat.hypotheses.get("part_geographique"),
            "part": resultat.hypotheses.get("part_marche_visee_saisie"),
            "budget": resultat.hypotheses.get("budget_fcfa"),
        },
    }
    return json.dumps(donnees, ensure_ascii=False, indent=2, default=str)


if st.session_state.resultat is None:
    depuis_lien = _etude_depuis_lien()
    if depuis_lien is not None:
        st.session_state.intention, st.session_state.resultat = depuis_lien
        st.session_state.phrase = st.query_params.get("phrase", "")
        st.session_state.synthese = nlp_agent.synthese_locale(*depuis_lien)


# ==========================================================================
# Etudes de cas pre-remplies (demo sans risque)
# ==========================================================================
# Calculees directement, sans passer par le moteur d'interpretation de
# phrase (module 3) : le resultat ne depend donc jamais de la reussite
# d'un parsing NLP. Utile en demonstration ou pour explorer l'outil sans
# rediger de phrase.

ETUDES_DE_CAS = {
    "Supérette à Mbour": {
        "secteur": "commerce_proximite",
        "regions": ["Thies"],
        "ville": "Mbour",
        "budget": 15_000_000,
        "phrase": "Je veux ouvrir une supérette à Mbour avec 15 millions de budget",
    },
    "Transformation de mangue à Ziguinchor": {
        "secteur": "agrobusiness",
        "regions": ["Ziguinchor"],
        "ville": "Ziguinchor",
        "budget": 35_000_000,
        "phrase": "Unité de transformation de mangue à Ziguinchor avec 35 millions de budget",
    },
    "Restauration santé à Dakar": {
        "secteur": "restauration_sante",
        "regions": ["Dakar"],
        "ville": "Dakar",
        "budget": 25_000_000,
        "phrase": "Restaurant pour diabétiques à Dakar avec 25 millions de budget",
    },
}


def _charger_etude_cas(nom: str) -> None:
    cas = ETUDES_DE_CAS[nom]
    resultat = market.calculer(
        jeu, cas["secteur"], regions=cas["regions"], budget=cas["budget"])
    intention = nlp_agent.Intention(
        secteur=cas["secteur"], regions=cas["regions"], ville=cas["ville"],
        budget=cas["budget"], confiance=1.0, moteur="etude_cas",
        notes=[f"Étude de cas pré-remplie « {nom} » — calcul direct, "
               f"sans passer par l'interprétation de phrase."])
    st.session_state.intention = intention
    st.session_state.resultat = resultat
    st.session_state.phrase = cas["phrase"]
    st.session_state.synthese = nlp_agent.synthese_locale(intention, resultat)
    _maj_lien_partage(
        cas["secteur"], cas["regions"],
        resultat.hypotheses["part_geographique"],
        resultat.hypotheses["part_marche_visee_saisie"],
        cas["budget"], cas["phrase"])


# ==========================================================================
# Barre laterale
# ==========================================================================

with st.sidebar:
    st.markdown("### 🇸🇳 DataMarket Sénégal")
    st.caption("Intelligence économique à partir des données ANSD")
    st.divider()

    cle_presente = bool(config.get_api_key())
    if cle_presente:
        st.success("API Claude connectée", icon="✅")
    else:
        st.warning("API Claude non configurée", icon="⚠️")
        with st.expander("Activer l'IA"):
            st.markdown(
                "Ajoutez votre clé dans `.streamlit/secrets.toml` :\n"
                "```toml\nANTHROPIC_API_KEY = \"sk-ant-...\"\n```\n"
                "ou dans la variable d'environnement `ANTHROPIC_API_KEY`.\n\n"
                "Sans clé, l'analyse des phrases se fait en local "
                "(lexiques et expressions régulières) : moins souple sur les "
                "formulations libres, mais entièrement fonctionnelle et gratuite."
            )

    forcer_local = st.toggle(
        "Forcer l'analyse locale", value=not cle_presente,
        help="Désactive tout appel à l'API Anthropic.")

    st.divider()
    st.markdown("#### Qualité des données")
    st.dataframe(jeu.controle_qualite(), hide_index=True,
                 width='stretch')

    with st.expander("Journal de chargement"):
        for ligne in jeu.journal:
            st.caption(ligne)
        st.caption(
            f"Déposez vos exports ANSD dans `{config.RAW_DIR}` : "
            "ils écrasent automatiquement les valeurs de référence.")

    if geographie.mode == "cercles":
        st.info(geographie.message, icon="🗺️")

    st.divider()
    st.markdown(
        f"Population nationale : "
        f"{config.formater_nombre(config.POPULATION_NATIONALE)} hab. "
        f"(RGPH-5 2023) {config.badge_html('OBS')}<br>"
        f"Dépense/tête : "
        f"{config.formater_fcfa(config.DEPENSE_ANNUELLE_TETE)}/an "
        f"(EHCVM II 2021-2022) {config.badge_html('OBS')}"
        f'<div style="font-size:0.8rem;color:#666;margin-top:4px;">'
        f"Ventilation par région {config.badge_html('EST')} dérivée des parts "
        f"publiées — remplaçable par vos exports ANSD.</div>",
        unsafe_allow_html=True,
    )

    with st.expander("Légende des badges"):
        for code in ("OBS", "EST", "HYP"):
            info = config.PROVENANCE[code]
            st.markdown(f"{config.badge_html(code)}  {info['titre']}",
                        unsafe_allow_html=True)


# ==========================================================================
# En-tete
# ==========================================================================

st.markdown(
    """
    <div class="bandeau">
      <h1>DataMarket Sénégal</h1>
      <p>Transformez les statistiques publiques de l'ANSD en études de marché
         chiffrées — TAM, SAM, SOM, carte du potentiel et rapport exportable.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================================================
# Impact & methode
# ==========================================================================

with st.expander("📋 Impact & méthode — à lire avant de commencer"):
    imp_g, imp_d = st.columns(2)
    with imp_g:
        st.markdown(
            "**Problème**\n\n"
            "Un entrepreneur sénégalais qui veut ouvrir une supérette, un "
            "restaurant ou une unité de transformation n'a aujourd'hui "
            "aucun moyen simple de chiffrer son marché : les données "
            "existent (ANSD) mais sont dispersées, techniques, et jamais "
            "reliées à une question concrète comme « combien de clients à "
            "Mbour ? ».")
        st.markdown(
            "**Données**\n\n"
            "RGPH-5 (2023), EHCVM II (2021-2022), EAA/DAPSA. Chaque valeur "
            "affichée porte un badge de provenance — OBS observé, EST "
            "estimé, HYP hypothèse — voir la légende dans la barre "
            "latérale.")
    with imp_d:
        st.markdown(
            "**Méthode**\n\n"
            "TAM = population cible × dépense annuelle sur le poste "
            "adressé. SAM = TAM × zone de chalandise réelle. SOM = SAM × "
            "part de marché visée à 3 ans, ajustée selon le budget "
            "disponible. Chaque coefficient est affiché et modifiable, "
            "jamais une boîte noire.")
        st.markdown(
            "**Limites assumées**\n\n"
            "Les dépenses par tête sont des moyennes régionales qui "
            "masquent des écarts de revenu. Le SOM ne modélise pas la "
            "concurrence de rue. Les données EHCVM datent de 2021-2022 "
            "(francs courants). Voir l'onglet *Validation* pour la "
            "calibration face à des chiffres publiés.")


# ==========================================================================
# Etudes de cas pre-remplies
# ==========================================================================

st.markdown("### Cas types")
st.caption(
    "Chargement immédiat, sans dépendre de l'interprétation d'une phrase — "
    "idéal pour explorer l'outil ou en démonstration.")

colonnes_cas = st.columns(len(ETUDES_DE_CAS))
for colonne, nom_cas in zip(colonnes_cas, ETUDES_DE_CAS):
    if colonne.button(nom_cas, width='stretch', key=f"cas_{nom_cas}"):
        _charger_etude_cas(nom_cas)
        st.rerun()


# ==========================================================================
# Module 3 - Saisie conversationnelle
# ==========================================================================

st.markdown("### Décrivez votre projet")

exemples = [
    "Je veux ouvrir une supérette à Mbour",
    "Restaurant pour diabétiques à Dakar avec 25 millions",
    "Unité de transformation d'arachide à Kaolack",
    "Une boutique de quartier à Touba, budget 3 millions",
]

colonnes = st.columns(len(exemples))
for colonne, exemple in zip(colonnes, exemples):
    if colonne.button(exemple, width='stretch', key=f"ex_{exemple}"):
        st.session_state.phrase = exemple

phrase = st.text_input(
    "Votre projet en une phrase",
    value=st.session_state.phrase,
    placeholder="Ex. : Je veux ouvrir une supérette à Mbour avec 15 millions de budget",
    label_visibility="collapsed",
)

gauche, droite = st.columns([1, 5])
lancer = gauche.button("Analyser", type="primary", width='stretch')

if lancer and phrase.strip():
    st.session_state.phrase = phrase
    with st.spinner("Analyse de votre projet…"):
        intention, resultat = nlp_agent.interroger(
            jeu, phrase, forcer_local=forcer_local)
        st.session_state.intention = intention
        st.session_state.resultat = resultat
        st.session_state.synthese = (
            nlp_agent.redaction_synthese(intention, resultat)
            if not forcer_local else None
        ) or nlp_agent.synthese_locale(intention, resultat)
        _maj_lien_partage(
            resultat.secteur, resultat.regions,
            resultat.hypotheses["part_geographique"],
            resultat.hypotheses["part_marche_visee_saisie"],
            intention.budget, phrase)
elif lancer:
    st.warning("Saisissez d'abord une description de votre projet.")


# ==========================================================================
# Resultats
# ==========================================================================

intention = st.session_state.intention
resultat = st.session_state.resultat

if resultat is not None:
    st.divider()

    # ---- Interpretation ------------------------------------------------
    with st.container(border=True):
        haut = st.columns([3, 1, 1])
        haut[0].markdown(f"**Interprétation** — {intention.resume()}")
        haut[1].metric("Moteur", {
            "claude": "Claude", "lien": "Lien partagé",
            "etude_cas": "Étude de cas",
        }.get(intention.moteur, "Local"))
        haut[2].metric("Confiance", f"{intention.confiance:.0%}")

        if intention.notes:
            with st.expander("Détail de l'interprétation"):
                for note in intention.notes:
                    st.caption("• " + note)

        st.caption(
            "Ajustez ci-dessous si l'interprétation ne correspond pas à votre projet.")

        ajuste = st.columns(4)
        secteur_choisi = ajuste[0].selectbox(
            "Secteur",
            options=list(config.SECTEURS),
            index=list(config.SECTEURS).index(intention.secteur),
            format_func=lambda c: config.SECTEURS[c]["libelle"],
        )
        regions_choisies = ajuste[1].multiselect(
            "Régions",
            options=config.REGIONS,
            default=intention.regions,
            format_func=lambda r: config.REGIONS_AFFICHAGE.get(r, r),
        )
        if not regions_choisies:
            st.caption(
                "⚠️ Aucune région sélectionnée : le recalcul portera sur "
                "les 14 régions (national).")
        part_geo = ajuste[2].slider(
            "Zone de chalandise (% de la région)",
            0.5, 100.0,
            value=float(100 * (intention.part_geographique
                               or config.SECTEURS[secteur_choisi]["sam_defaut"])),
            step=0.5,
        ) / 100
        part_som = ajuste[3].slider(
            "Part de marché visée à 3 ans (%)",
            0.1, 50.0,
            value=float(100 * (intention.part_marche_visee
                               or config.SECTEURS[secteur_choisi]["som_defaut"])),
            step=0.1,
        ) / 100

        if st.button("Recalculer avec ces paramètres"):
            st.session_state.resultat = market.calculer(
                jeu, secteur_choisi, regions=regions_choisies,
                part_geographique=part_geo, part_marche_visee=part_som,
                budget=intention.budget)
            resultat = st.session_state.resultat
            st.session_state.synthese = nlp_agent.synthese_locale(
                intention, resultat)
            _maj_lien_partage(
                resultat.secteur, resultat.regions, part_geo, part_som,
                intention.budget, st.session_state.phrase)
            st.rerun()

    # ---- Indicateurs cles ----------------------------------------------
    st.markdown(
        f"### Résultat {config.badge_html(resultat.provenance.get('tam', 'HYP'))}",
        unsafe_allow_html=True,
    )
    st.caption(
        "TAM, SAM et SOM combinent des données observées et des hypothèses "
        "sectorielles modifiables (captation, prévalence, part transformée) : "
        "ils héritent donc du classement Hypothèse — voir l'onglet "
        "« Détail régional » pour la liste complète.")
    st.caption(
        "🔗 L'adresse de cette page encode les paramètres de l'étude — "
        "copiez-la pour la partager ou la retrouver plus tard.")
    mesures = st.columns(4)
    mesures[0].metric("TAM — marché total", config.formater_fcfa(resultat.tam))
    mesures[1].metric(
        "SAM — accessible", config.formater_fcfa(resultat.sam),
        f"{100 * resultat.sam / resultat.tam:.1f} % du TAM" if resultat.tam else "—")
    mesures[2].metric(
        "SOM — captable à 3 ans", config.formater_fcfa(resultat.som),
        f"{100 * resultat.som / resultat.tam:.2f} % du TAM" if resultat.tam else "—")
    mesures[3].metric("CA mensuel visé",
                      config.formater_fcfa(resultat.ca_mensuel_som))

    for avertissement in resultat.avertissements:
        st.warning(avertissement, icon="⚠️")

    # ---- Analyse de sensibilite -----------------------------------------
    with st.expander("📐 Intervalle de confiance et analyse de sensibilité",
                     expanded=False):
        coefficients = market.coefficients_sensibles(resultat.secteur)
        st.caption(
            f"{config.badge_html('HYP')} Fait varier le(s) coefficient(s) de "
            f"modélisation les plus incertains du secteur — "
            f"**{', '.join(c.replace('_', ' ') for c in coefficients)}** — "
            "en laissant les autres hypothèses (zone de chalandise, part de "
            "marché visée, budget) fixées à la valeur choisie ci-dessus. Ce "
            "n'est pas une marge arbitraire appliquée au TAM.",
            unsafe_allow_html=True)

        marge = st.slider(
            "Marge d'incertitude sur les hypothèses clés (± %)",
            5, 50, 20, step=5) / 100

        intervalle = market.fourchette(
            jeu, resultat.secteur, regions=resultat.regions,
            part_geographique=resultat.hypotheses["part_geographique"],
            part_marche_visee=resultat.hypotheses["part_marche_visee_saisie"],
            budget=resultat.hypotheses.get("budget_fcfa"),
            marge=marge)

        st.plotly_chart(
            dashboard.graphique_fourchette(intervalle, resultat.libelle),
            width='stretch')

        colonnes_fourchette = st.columns(3)
        colonnes_fourchette[0].metric(
            "TAM bas", config.formater_fcfa(intervalle["tam"]["bas"]))
        colonnes_fourchette[1].metric(
            "TAM central", config.formater_fcfa(intervalle["tam"]["central"]))
        colonnes_fourchette[2].metric(
            "TAM haut", config.formater_fcfa(intervalle["tam"]["haut"]))

        colonnes_fourchette_som = st.columns(3)
        colonnes_fourchette_som[0].metric(
            "SOM bas", config.formater_fcfa(intervalle["som"]["bas"]))
        colonnes_fourchette_som[1].metric(
            "SOM central", config.formater_fcfa(intervalle["som"]["central"]))
        colonnes_fourchette_som[2].metric(
            "SOM haut", config.formater_fcfa(intervalle["som"]["haut"]))

        if intervalle["som"]["bas"] == intervalle["som"]["haut"]:
            st.caption(
                "Bas = haut ici : le gisement de matière première régionale "
                "est le facteur limitant sur ce périmètre, pas la demande — "
                "faire varier la part transformée n'a alors aucun effet.")

    # ---- Decision d'investissement ---------------------------------------
    with st.expander("💰 Décision d'investissement", expanded=False):
        capex_min = resultat.hypotheses.get("capex_min_fcfa", 0)
        st.markdown(
            f"{config.badge_html('HYP')} Capital minimal observé pour ce "
            f"secteur : **{config.formater_fcfa(capex_min)}**.",
            unsafe_allow_html=True)

        marge_nette = st.slider(
            "Marge nette estimée (%)",
            1, 40, 10, step=1,
            help="Hypothèse à régler vous-même selon votre connaissance du "
                 "secteur — ce n'est pas une donnée ANSD. Marge nette = "
                 "profit après toutes charges, en % du chiffre d'affaires.",
        ) / 100
        st.caption(
            f"{config.badge_html('HYP')} Hypothèse saisie par vous, "
            "non issue des données ANSD.", unsafe_allow_html=True)

        ca_mensuel = resultat.ca_mensuel_som
        profit_mensuel = ca_mensuel * marge_nette

        colonnes_decision = st.columns(3)
        colonnes_decision[0].metric(
            "CA mensuel visé", config.formater_fcfa(ca_mensuel))
        colonnes_decision[1].metric(
            "Profit mensuel estimé", config.formater_fcfa(profit_mensuel))

        if profit_mensuel > 0 and capex_min > 0:
            mois = capex_min / profit_mensuel
            if mois < 1:
                texte_delai = f"{mois * 30:.0f} jours"
            elif mois < 24:
                texte_delai = f"{mois:.0f} mois"
            else:
                texte_delai = f"{mois / 12:.1f} ans"
            colonnes_decision[2].metric("Délai d'amortissement", texte_delai)
            if mois > 60:
                st.warning(
                    "Délai d'amortissement supérieur à 5 ans : ce plan n'est "
                    "probablement pas viable en l'état — reconsidérez le "
                    "budget, la marge visée ou l'ambition de part de marché "
                    "(SOM).", icon="⚠️")
        else:
            colonnes_decision[2].metric("Délai d'amortissement", "n/d")
            st.warning(
                "Le chiffre d'affaires visé ne génère aucun profit positif "
                "avec cette marge : le capital ne serait jamais amorti selon "
                "ce plan.", icon="⚠️")

        if intention.budget:
            ecart_budget = intention.budget - capex_min
            if ecart_budget < 0:
                st.caption(
                    f"Votre budget ({config.formater_fcfa(intention.budget)}) "
                    f"est inférieur de {config.formater_fcfa(abs(ecart_budget))} "
                    "au capital minimal observé — le SOM a déjà été réduit en "
                    "conséquence (voir les avertissements ci-dessus).")
            else:
                st.caption(
                    f"Votre budget ({config.formater_fcfa(intention.budget)}) "
                    "couvre le capital minimal observé, avec une marge de "
                    f"{config.formater_fcfa(ecart_budget)}.")

    # ---- Onglets --------------------------------------------------------
    onglets = st.tabs([
        "Synthèse", "Carte du potentiel", "Détail régional",
        "Comparateur de territoires", "Comparaison sectorielle",
        "Validation", "Données sources", "Export",
    ])

    # Synthese
    with onglets[0]:
        colg, cold = st.columns([3, 2])
        with colg:
            st.markdown("#### Lecture stratégique")
            if st.session_state.synthese:
                st.markdown(
                    f'<div class="encart">{st.session_state.synthese}</div>',
                    unsafe_allow_html=True)
        with cold:
            st.plotly_chart(dashboard.graphique_entonnoir(resultat),
                            width='stretch')

        st.markdown(
            f"#### Repères "
            f"{config.badge_html(resultat.provenance.get('population_cible', 'EST'))}",
            unsafe_allow_html=True)
        reperes = st.columns(3)
        reperes[0].metric("Population cible",
                          config.formater_nombre(resultat.population_cible))
        transactions = resultat.clients_potentiels()
        if transactions:
            reperes[1].metric("Transactions / jour",
                              config.formater_nombre(transactions / 365))
            reperes[2].metric(
                "Panier moyen retenu",
                config.formater_fcfa(resultat.hypotheses["ticket_moyen_fcfa"]))
        else:
            reperes[1].metric("Régions couvertes", len(resultat.regions))
            reperes[2].metric(
                "Capex minimal du secteur",
                config.formater_fcfa(resultat.hypotheses.get("capex_min_fcfa", 0)))

    # Carte
    with onglets[1]:
        st.markdown("#### Potentiel de marché par région")
        st.caption(
            "Score composite : 70 % volume de marché (TAM absolu) et 30 % "
            "intensité (TAM par habitant). Calculé sur les 14 régions pour le "
            "secteur retenu, indépendamment du périmètre de votre projet.")

        potentiel = _potentiel(resultat.secteur)

        try:
            from streamlit_folium import st_folium

            carte = dashboard.carte_potentiel(potentiel, geographie)
            st_folium(carte, height=560, use_container_width=True,
                      returned_objects=[])
        except ImportError:
            st.error(
                "Le paquet `streamlit-folium` est absent. "
                "Installez-le avec `pip install streamlit-folium` pour afficher "
                "la carte.")

        if geographie.mode != "cercles":
            manquantes = geo_module.regions_manquantes(geographie)
            if manquantes:
                st.caption(
                    "Régions sans polygone dans le fond de carte : "
                    + ", ".join(config.REGIONS_AFFICHAGE.get(r, r)
                                for r in manquantes))

        st.plotly_chart(dashboard.graphique_tam_regions(potentiel),
                        width='stretch')
        st.plotly_chart(dashboard.graphique_structure(potentiel),
                        width='stretch')

    # Detail regional
    with onglets[2]:
        st.markdown("#### Décomposition du marché sur votre périmètre")
        st.markdown(
            f"Population {config.badge_html(resultat.provenance.get('population_cible', 'EST'))}"
            f"&nbsp;&nbsp;·&nbsp;&nbsp;"
            f"TAM / SAM / SOM {config.badge_html(resultat.provenance.get('tam', 'HYP'))}",
            unsafe_allow_html=True,
        )
        detail = resultat.detail_regional.copy()
        detail["Région"] = detail["region"].map(
            lambda r: config.REGIONS_AFFICHAGE.get(r, r))

        affichage = pd.DataFrame({
            "Région": detail["Région"],
            "Population": detail["population"].map(config.formater_nombre),
            "Population cible": detail["population_cible"].map(config.formater_nombre),
            "Dépense/tête": detail["depense_cible_tete"].map(config.formater_fcfa),
            "TAM": detail["tam_region"].map(config.formater_fcfa),
            "SAM": detail["sam_region"].map(config.formater_fcfa),
            "SOM": detail["som_region"].map(config.formater_fcfa),
            "% du TAM": detail["part_tam_pct"].map(lambda v: f"{v:.1f} %"),
        })
        st.dataframe(affichage, hide_index=True, width='stretch')

        st.download_button(
            "Télécharger ce tableau (CSV)",
            detail.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"detail_{resultat.secteur}.csv",
            mime="text/csv",
        )

        with st.expander("Hypothèses de calcul utilisées"):
            st.markdown(
                f"{config.badge_html('HYP')} Chaque ligne ci-dessous est un "
                f"paramètre de modélisation explicite — ajustez-le avec vos "
                f"observations terrain.",
                unsafe_allow_html=True)
            lignes = []
            for cle, valeur in resultat.hypotheses.items():
                if cle in {"libelle", "description", "poste_depense",
                           "provenance_population_cible"} or valeur is None:
                    continue
                lignes.append({
                    "Hypothèse": cle.replace("_", " ").capitalize(),
                    "Valeur": (f"{valeur:.1%}"
                               if isinstance(valeur, float) and 0 < abs(valeur) < 1
                               else config.formater_nombre(valeur)
                               if isinstance(valeur, (int, float))
                               else str(valeur)),
                })
            st.dataframe(pd.DataFrame(lignes), hide_index=True,
                         width='stretch')

    # Comparateur de territoires
    with onglets[3]:
        st.markdown("#### Comparer deux territoires")
        st.caption(
            "Comparaison sur les hypothèses par défaut du secteur "
            f"« {resultat.libelle} », indépendamment du périmètre de votre étude.")

        potentiel_cmp = _potentiel(resultat.secteur)
        options_regions = potentiel_cmp["region"].tolist()

        col_a, col_b = st.columns(2)
        region_a = col_a.selectbox(
            "Territoire A", options=options_regions, index=0,
            format_func=lambda r: config.REGIONS_AFFICHAGE.get(r, r),
            key="cmp_region_a")
        index_b = 1 if len(options_regions) > 1 else 0
        region_b = col_b.selectbox(
            "Territoire B", options=options_regions, index=index_b,
            format_func=lambda r: config.REGIONS_AFFICHAGE.get(r, r),
            key="cmp_region_b")

        if region_a == region_b:
            st.info("Choisissez deux territoires différents pour comparer.")
        else:
            ligne_a = potentiel_cmp.loc[potentiel_cmp["region"] == region_a].iloc[0]
            ligne_b = potentiel_cmp.loc[potentiel_cmp["region"] == region_b].iloc[0]
            libelle_a = config.REGIONS_AFFICHAGE.get(region_a, region_a)
            libelle_b = config.REGIONS_AFFICHAGE.get(region_b, region_b)

            tableau_cmp = pd.DataFrame({
                "Indicateur": ["Population", "TAM", "TAM / habitant",
                               "Score de potentiel", "Rang national"],
                libelle_a: [
                    config.formater_nombre(ligne_a["population"]),
                    config.formater_fcfa(ligne_a["tam_region"]),
                    config.formater_fcfa(ligne_a["tam_par_habitant"]),
                    f"{ligne_a['score_potentiel']:.1f} / 100",
                    f"{int(ligne_a['rang'])}ᵉ / 14",
                ],
                libelle_b: [
                    config.formater_nombre(ligne_b["population"]),
                    config.formater_fcfa(ligne_b["tam_region"]),
                    config.formater_fcfa(ligne_b["tam_par_habitant"]),
                    f"{ligne_b['score_potentiel']:.1f} / 100",
                    f"{int(ligne_b['rang'])}ᵉ / 14",
                ],
            })
            st.dataframe(tableau_cmp, hide_index=True, width='stretch')

            ecart_tam = float(ligne_a["tam_region"] - ligne_b["tam_region"])
            plus_grand = libelle_a if ecart_tam >= 0 else libelle_b
            st.markdown(
                f"{config.badge_html(resultat.provenance.get('tam', 'HYP'))} "
                f"Le TAM de **{plus_grand}** dépasse celui de son comparateur "
                f"de {config.formater_fcfa(abs(ecart_tam))}, sur les hypothèses "
                f"par défaut du secteur.",
                unsafe_allow_html=True)

            st.plotly_chart(
                dashboard.graphique_comparaison_territoires(
                    ligne_a, ligne_b, libelle_a, libelle_b, resultat.libelle),
                width='stretch')

    # Comparaison sectorielle
    with onglets[4]:
        st.markdown("#### Les trois secteurs sur le même périmètre")
        comparaison = market.comparer_secteurs(jeu, regions=resultat.regions)
        st.plotly_chart(dashboard.graphique_secteurs(comparaison),
                        width='stretch')
        st.dataframe(
            comparaison[["Secteur", "TAM", "SAM", "SOM", "CA mensuel visé"]],
            hide_index=True, width='stretch')
        st.caption(
            "Échelle logarithmique : les ordres de grandeur diffèrent fortement "
            "d'un secteur à l'autre. La restauration santé vise une niche "
            "étroite mais à forte valeur unitaire ; le commerce de proximité "
            "adresse un marché de masse.")

    # Validation
    with onglets[5]:
        st.markdown("#### Calibration face à des chiffres publiés indépendamment")
        st.caption(
            "Ce ne sont pas des sorties du modèle comparées à elles-mêmes : "
            "chaque ligne confronte une grandeur recalculée par le pipeline à "
            "un chiffre publié par l'ANSD, indépendamment de ce projet.")

        validation = jeu.validation_externe()
        n_conformes = int(validation["Conforme"].sum())
        n_total = len(validation)

        if n_conformes == n_total:
            st.success(
                f"{n_conformes}/{n_total} contrôles conformes aux seuils de "
                "tolérance.", icon="✅")
        else:
            st.warning(
                f"{n_conformes}/{n_total} contrôles conformes — voir le détail "
                "ci-dessous.", icon="⚠️")

        affichage_validation = validation.copy()
        affichage_validation["Conforme"] = affichage_validation["Conforme"].map(
            lambda ok: "✅" if ok else "❌")
        st.dataframe(affichage_validation, hide_index=True, width='stretch')

        st.caption(
            f"{config.badge_html('OBS')} Valeurs publiées = chiffres officiels "
            "RGPH-5 / EHCVM II cités dans `README.md`. "
            f"{config.badge_html('CALC')} Valeurs du modèle = recalculées à "
            "chaque chargement à partir des données de "
            "`ref_*.csv` (ou de vos exports dans `data/raw/` s'ils sont "
            "présents). Ces mêmes contrôles sont vérifiés automatiquement à "
            "chaque push par `test_datamarket.py::TestChargement` — cette "
            "page en est la version lisible pour un évaluateur.",
            unsafe_allow_html=True)

    # Donnees sources
    with onglets[6]:
        st.markdown("#### Données ANSD normalisées")
        sous = st.tabs(["Population (RGPH-5)", "Dépenses (EHCVM II)",
                        "Production agricole (EAA)"])

        with sous[0]:
            pop = jeu.population.copy()
            pop["Région"] = pop["region"].map(
                lambda r: config.REGIONS_AFFICHAGE.get(r, r))
            st.dataframe(
                pop[["Région", "population", "superficie_km2", "densite",
                     "part_nationale_pct", "taux_urbain_pct",
                     "population_urbaine", "nb_menages"]].round(1),
                hide_index=True, width='stretch')
            st.caption(
                f"Total : {config.formater_nombre(pop['population'].sum())} "
                f"habitants — à comparer au chiffre officiel RGPH-5 de "
                f"{config.formater_nombre(config.POPULATION_NATIONALE)}.")

        with sous[1]:
            dep = jeu.depenses.copy()
            dep["Région"] = dep["region"].map(
                lambda r: config.REGIONS_AFFICHAGE.get(r, r))
            colonnes = ["Région", "depense_tete", "depense_totale_region"] + [
                c for c in dep.columns if c.startswith("part_")]
            st.dataframe(dep[colonnes].round(1), hide_index=True,
                         width='stretch')

        with sous[2]:
            st.plotly_chart(dashboard.graphique_production(jeu.production),
                            width='stretch')
            prod = jeu.production.copy()
            prod["Région"] = prod["region"].map(
                lambda r: config.REGIONS_AFFICHAGE.get(r, r))
            st.dataframe(
                prod[["Région"] + [c for c in prod.columns if c.endswith("_t")]],
                hide_index=True, width='stretch')

    # Export
    with onglets[7]:
        st.markdown("#### Rapport d'étude exportable")
        st.caption(
            "Document de 4 pages : synthèse chiffrée, détail région par "
            "région, méthodologie complète, sources et limites.")

        if st.button("Générer le rapport PDF", type="primary"):
            with st.spinner("Génération du rapport…"):
                try:
                    chemin = generer_rapport(
                        resultat,
                        synthese=st.session_state.synthese,
                        intention_brute=st.session_state.phrase,
                    )
                    st.session_state.pdf = chemin
                    st.success(f"Rapport généré : {chemin.name}")
                except Exception as erreur:
                    st.error(f"Échec de la génération : {erreur}")

        if st.session_state.get("pdf") and st.session_state.pdf.exists():
            st.download_button(
                "Télécharger le PDF",
                st.session_state.pdf.read_bytes(),
                file_name=st.session_state.pdf.name,
                mime="application/pdf",
                type="primary",
            )

        st.divider()
        st.markdown("#### Export reproductible (JSON)")
        st.caption(
            "Entrées, hypothèses, provenance et sorties du calcul en un seul "
            "fichier — de quoi rejouer ou auditer les chiffres sans repasser "
            "par l'interface.")
        st.download_button(
            "Télécharger le calcul complet (JSON)",
            _export_json(resultat, st.session_state.phrase),
            file_name=f"etude_{resultat.secteur}.json",
            mime="application/json",
        )

else:
    # ---- Ecran d'accueil ------------------------------------------------
    st.divider()
    st.markdown(
        f"### Panorama national {config.badge_html('HYP')}",
        unsafe_allow_html=True)
    st.caption(
        "Le TAM combine des données observées et des hypothèses sectorielles "
        "modifiables — voir la légende des badges dans la barre latérale.")

    secteur_apercu = st.selectbox(
        "Secteur à explorer",
        options=list(config.SECTEURS),
        format_func=lambda c: config.SECTEURS[c]["libelle"],
    )
    st.caption(config.SECTEURS[secteur_apercu]["description"])

    potentiel = _potentiel(secteur_apercu)
    national = market.calculer(jeu, secteur_apercu)

    mesures = st.columns(4)
    mesures[0].metric("TAM national", config.formater_fcfa(national.tam))
    mesures[1].metric("Population cible",
                      config.formater_nombre(national.population_cible))
    mesures[2].metric("Région n°1",
                      config.REGIONS_AFFICHAGE.get(potentiel.iloc[0]["region"], ""))
    mesures[3].metric("TAM de la région n°1",
                      config.formater_fcfa(potentiel.iloc[0]["tam_region"]))

    colg, cold = st.columns([3, 2])
    with colg:
        try:
            from streamlit_folium import st_folium

            st_folium(dashboard.carte_potentiel(potentiel, geographie),
                      height=520, use_container_width=True,
                      returned_objects=[])
        except ImportError:
            st.info("Installez `streamlit-folium` pour afficher la carte.")
    with cold:
        st.dataframe(
            potentiel[["rang", "region_affichage", "tam_lisible",
                       "score_potentiel"]].rename(columns={
                           "rang": "Rang", "region_affichage": "Région",
                           "tam_lisible": "TAM", "score_potentiel": "Score"}),
            hide_index=True, width='stretch', height=520)

    st.plotly_chart(dashboard.graphique_tam_regions(potentiel),
                    width='stretch')

st.divider()
st.caption(
    "DataMarket Sénégal — sources : RGPH-5 2023 (ANSD), EHCVM II 2021-2022, "
    "EAA/DAPSA. Outil de cadrage : les montants sont des ordres de grandeur "
    "dérivés de moyennes régionales et ne remplacent pas une étude terrain."
)
