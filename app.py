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
from i18n import LANGUES, t
from pipeline import charger_donnees
from report import generer_rapport

# ==========================================================================
# Langue
# ==========================================================================
# Lue depuis l'URL en tout premier, avant meme set_page_config (le titre de
# l'onglet navigateur en depend). Persistee dans st.session_state puis
# reportee dans st.query_params : un lien partage conserve donc la langue
# choisie par celui qui l'a genere.

_lang_url = st.query_params.get("lang", "fr")
if _lang_url not in LANGUES:
    _lang_url = "fr"
if "lang" not in st.session_state:
    st.session_state.lang = _lang_url
lang = st.session_state.lang

st.set_page_config(
    page_title=t("titre_page", lang),
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
    st.query_params["lang"] = lang
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
            if k not in {"libelle", "libelle_en", "description", "description_en",
                        "poste_depense"}
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
        st.session_state.synthese = nlp_agent.synthese_locale(*depuis_lien, lang=lang)


# ==========================================================================
# Etudes de cas pre-remplies (demo sans risque)
# ==========================================================================
# Calculees directement, sans passer par le moteur d'interpretation de
# phrase (module 3) : le resultat ne depend donc jamais de la reussite
# d'un parsing NLP. Utile en demonstration ou pour explorer l'outil sans
# rediger de phrase.

ETUDES_DE_CAS = {
    "cas_mbour": {
        "secteur": "commerce_proximite",
        "regions": ["Thies"],
        "ville": "Mbour",
        "budget": 15_000_000,
        "phrase_fr": "Je veux ouvrir une supérette à Mbour avec 15 millions de budget",
        "phrase_en": "I want to open a corner store in Mbour with a 15 million budget",
    },
    "cas_ziguinchor": {
        "secteur": "agrobusiness",
        "regions": ["Ziguinchor"],
        "ville": "Ziguinchor",
        "budget": 35_000_000,
        "phrase_fr": "Unité de transformation de mangue à Ziguinchor avec 35 millions de budget",
        "phrase_en": "Mango processing unit in Ziguinchor with a 35 million budget",
    },
    "cas_dakar": {
        "secteur": "restauration_sante",
        "regions": ["Dakar"],
        "ville": "Dakar",
        "budget": 25_000_000,
        "phrase_fr": "Restaurant pour diabétiques à Dakar avec 25 millions de budget",
        "phrase_en": "Diabetic-friendly restaurant in Dakar with a 25 million budget",
    },
}


def _charger_etude_cas(cle_cas: str) -> None:
    cas = ETUDES_DE_CAS[cle_cas]
    phrase = cas["phrase_fr"] if lang == "fr" else cas["phrase_en"]
    resultat = market.calculer(
        jeu, cas["secteur"], regions=cas["regions"], budget=cas["budget"])
    intention = nlp_agent.Intention(
        secteur=cas["secteur"], regions=cas["regions"], ville=cas["ville"],
        budget=cas["budget"], confiance=1.0, moteur="etude_cas",
        notes=[f"Étude de cas pré-remplie « {t(cle_cas, lang)} » — calcul "
               f"direct, sans passer par l'interprétation de phrase."])
    st.session_state.intention = intention
    st.session_state.resultat = resultat
    st.session_state.phrase = phrase
    st.session_state.synthese = nlp_agent.synthese_locale(intention, resultat, lang=lang)
    _maj_lien_partage(
        cas["secteur"], cas["regions"],
        resultat.hypotheses["part_geographique"],
        resultat.hypotheses["part_marche_visee_saisie"],
        cas["budget"], phrase)


# ==========================================================================
# Barre laterale
# ==========================================================================

with st.sidebar:
    col_titre, col_lang = st.columns([4, 2])
    col_titre.markdown(f"### 🇸🇳 {t('titre_page', lang)}")
    nouvelle_langue = col_lang.selectbox(
        "🌐", options=list(LANGUES), format_func=lambda l: LANGUES[l],
        index=list(LANGUES).index(lang), label_visibility="collapsed",
        key="selecteur_langue")
    if nouvelle_langue != lang:
        st.session_state.lang = nouvelle_langue
        st.query_params["lang"] = nouvelle_langue
        st.rerun()

    st.caption(t("sidebar_soustitre", lang))
    st.divider()

    cle_presente = bool(config.get_api_key())
    if cle_presente:
        st.success(t("api_connectee", lang), icon="✅")
    else:
        st.warning(t("api_non_configuree", lang), icon="⚠️")
        with st.expander(t("activer_ia", lang)):
            st.markdown(t("activer_ia_contenu", lang))

    forcer_local = st.toggle(
        t("forcer_local", lang), value=not cle_presente,
        help=t("forcer_local_aide", lang))

    st.divider()
    st.markdown(f"#### {t('qualite_donnees', lang)}")
    st.dataframe(jeu.controle_qualite(), hide_index=True,
                 width='stretch')

    with st.expander(t("journal_chargement", lang)):
        for ligne in jeu.journal:
            st.caption(ligne)
        st.caption(t("journal_depot", lang, chemin=config.RAW_DIR))

    if geographie.mode == "cercles":
        st.info(geographie.message, icon="🗺️")

    st.divider()
    st.markdown(
        t("population_nationale_sidebar", lang,
          pop=config.formater_nombre(config.POPULATION_NATIONALE))
        + f" {config.badge_html('OBS')}<br>"
        + t("depense_tete_sidebar", lang,
            dep=config.formater_fcfa(config.DEPENSE_ANNUELLE_TETE))
        + f" {config.badge_html('OBS')}"
        + '<div style="font-size:0.8rem;color:#666;margin-top:4px;">'
        + t("ventilation_region_sidebar", lang, badge=config.badge_html('EST'))
        + "</div>",
        unsafe_allow_html=True,
    )

    with st.expander(t("legende_badges", lang)):
        for code in ("OBS", "EST", "HYP"):
            info = config.PROVENANCE[code]
            st.markdown(f"{config.badge_html(code)}  {info['titre']}",
                        unsafe_allow_html=True)


# ==========================================================================
# En-tete
# ==========================================================================

st.markdown(
    f"""
    <div class="bandeau">
      <h1>{t('bandeau_titre', lang)}</h1>
      <p>{t('bandeau_sous_titre', lang)}</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================================================
# Impact & methode
# ==========================================================================

with st.expander(t("impact_methode_titre", lang)):
    imp_g, imp_d = st.columns(2)
    with imp_g:
        st.markdown(f"{t('impact_probleme_titre', lang)}\n\n"
                   f"{t('impact_probleme_texte', lang)}")
        st.markdown(f"{t('impact_donnees_titre', lang)}\n\n"
                   f"{t('impact_donnees_texte', lang)}")
    with imp_d:
        st.markdown(f"{t('impact_methode_titre2', lang)}\n\n"
                   f"{t('impact_methode_texte', lang)}")
        st.markdown(f"{t('impact_limites_titre', lang)}\n\n"
                   f"{t('impact_limites_texte', lang)}")


# ==========================================================================
# Etudes de cas pre-remplies
# ==========================================================================

st.markdown(f"### {t('cas_types_titre', lang)}")
st.caption(t("cas_types_caption", lang))

colonnes_cas = st.columns(len(ETUDES_DE_CAS))
for colonne, cle_cas in zip(colonnes_cas, ETUDES_DE_CAS):
    if colonne.button(t(cle_cas, lang), width='stretch', key=f"cas_{cle_cas}"):
        _charger_etude_cas(cle_cas)
        st.rerun()


# ==========================================================================
# Module 3 - Saisie conversationnelle
# ==========================================================================

st.markdown(f"### {t('decrivez_projet', lang)}")

exemples_cles = ["exemple_mbour", "exemple_dakar", "exemple_kaolack", "exemple_touba"]

colonnes = st.columns(len(exemples_cles))
for colonne, cle_exemple in zip(colonnes, exemples_cles):
    texte_exemple = t(cle_exemple, lang)
    if colonne.button(texte_exemple, width='stretch', key=f"ex_{cle_exemple}"):
        st.session_state.phrase = texte_exemple

phrase = st.text_input(
    t("phrase_label", lang),
    value=st.session_state.phrase,
    placeholder=t("phrase_placeholder", lang),
    label_visibility="collapsed",
)

gauche, droite = st.columns([1, 5])
lancer = gauche.button(t("analyser", lang), type="primary", width='stretch')

if lancer and phrase.strip():
    st.session_state.phrase = phrase
    with st.spinner(t("analyse_spinner", lang)):
        intention, resultat = nlp_agent.interroger(
            jeu, phrase, forcer_local=forcer_local)
        st.session_state.intention = intention
        st.session_state.resultat = resultat
        st.session_state.synthese = (
            nlp_agent.redaction_synthese(intention, resultat)
            if not forcer_local else None
        ) or nlp_agent.synthese_locale(intention, resultat, lang=lang)
        _maj_lien_partage(
            resultat.secteur, resultat.regions,
            resultat.hypotheses["part_geographique"],
            resultat.hypotheses["part_marche_visee_saisie"],
            intention.budget, phrase)
elif lancer:
    st.warning(t("saisir_description", lang))


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
        haut[0].markdown(f"**{t('interpretation', lang)}** — {intention.resume()}")
        haut[1].metric(t("moteur", lang), {
            "claude": t("moteur_claude", lang), "lien": t("moteur_lien", lang),
            "etude_cas": t("moteur_etude_cas", lang),
        }.get(intention.moteur, t("moteur_local", lang)))
        haut[2].metric(t("confiance", lang), f"{intention.confiance:.0%}")

        if intention.notes:
            with st.expander(t("detail_interpretation", lang)):
                for note in intention.notes:
                    st.caption("• " + note)

        st.caption(t("ajustez_ci_dessous", lang))

        ajuste = st.columns(4)
        secteur_choisi = ajuste[0].selectbox(
            t("secteur_label", lang),
            options=list(config.SECTEURS),
            index=list(config.SECTEURS).index(intention.secteur),
            format_func=lambda c: config.libelle_secteur(c, lang),
        )
        regions_choisies = ajuste[1].multiselect(
            t("regions_label", lang),
            options=config.REGIONS,
            default=intention.regions,
            format_func=lambda r: config.REGIONS_AFFICHAGE.get(r, r),
        )
        if not regions_choisies:
            st.caption(t("aucune_region_avertissement", lang))
        part_geo = ajuste[2].slider(
            t("zone_chalandise_label", lang),
            0.5, 100.0,
            value=float(100 * (intention.part_geographique
                               or config.SECTEURS[secteur_choisi]["sam_defaut"])),
            step=0.5,
        ) / 100
        part_som = ajuste[3].slider(
            t("part_marche_visee_label", lang),
            0.1, 50.0,
            value=float(100 * (intention.part_marche_visee
                               or config.SECTEURS[secteur_choisi]["som_defaut"])),
            step=0.1,
        ) / 100

        if st.button(t("recalculer", lang)):
            st.session_state.resultat = market.calculer(
                jeu, secteur_choisi, regions=regions_choisies,
                part_geographique=part_geo, part_marche_visee=part_som,
                budget=intention.budget)
            resultat = st.session_state.resultat
            st.session_state.synthese = nlp_agent.synthese_locale(
                intention, resultat, lang=lang)
            _maj_lien_partage(
                resultat.secteur, resultat.regions, part_geo, part_som,
                intention.budget, st.session_state.phrase)
            st.rerun()

    # ---- Indicateurs cles ----------------------------------------------
    st.markdown(
        f"### {t('resultat_titre', lang)} "
        f"{config.badge_html(resultat.provenance.get('tam', 'HYP'))}",
        unsafe_allow_html=True,
    )
    st.caption(t("resultat_caption", lang))
    st.caption(t("lien_partageable_caption", lang))
    mesures = st.columns(4)
    mesures[0].metric(t("tam_marche_total", lang), config.formater_fcfa(resultat.tam))
    mesures[1].metric(
        t("sam_accessible", lang), config.formater_fcfa(resultat.sam),
        t("pct_du_tam", lang, pct=f"{100 * resultat.sam / resultat.tam:.1f}")
        if resultat.tam else "—")
    mesures[2].metric(
        t("som_captable", lang), config.formater_fcfa(resultat.som),
        t("pct_du_tam", lang, pct=f"{100 * resultat.som / resultat.tam:.2f}")
        if resultat.tam else "—")
    mesures[3].metric(t("ca_mensuel_vise", lang),
                      config.formater_fcfa(resultat.ca_mensuel_som))

    for avertissement in resultat.avertissements:
        st.warning(avertissement, icon="⚠️")

    # ---- Analyse de sensibilite -----------------------------------------
    with st.expander(t("sensibilite_titre", lang), expanded=False):
        coefficients = market.coefficients_sensibles(resultat.secteur)
        st.caption(
            f"{config.badge_html('HYP')} "
            + t("sensibilite_caption", lang,
                coefs=', '.join(c.replace('_', ' ') for c in coefficients)),
            unsafe_allow_html=True)

        marge = st.slider(t("marge_incertitude_label", lang),
                          5, 50, 20, step=5) / 100

        intervalle = market.fourchette(
            jeu, resultat.secteur, regions=resultat.regions,
            part_geographique=resultat.hypotheses["part_geographique"],
            part_marche_visee=resultat.hypotheses["part_marche_visee_saisie"],
            budget=resultat.hypotheses.get("budget_fcfa"),
            marge=marge)

        st.plotly_chart(
            dashboard.graphique_fourchette(
                intervalle, config.libelle_secteur(resultat.secteur, lang), lang=lang),
            width='stretch')

        colonnes_fourchette = st.columns(3)
        colonnes_fourchette[0].metric(
            t("tam_bas", lang), config.formater_fcfa(intervalle["tam"]["bas"]))
        colonnes_fourchette[1].metric(
            t("tam_central", lang), config.formater_fcfa(intervalle["tam"]["central"]))
        colonnes_fourchette[2].metric(
            t("tam_haut", lang), config.formater_fcfa(intervalle["tam"]["haut"]))

        colonnes_fourchette_som = st.columns(3)
        colonnes_fourchette_som[0].metric(
            t("som_bas", lang), config.formater_fcfa(intervalle["som"]["bas"]))
        colonnes_fourchette_som[1].metric(
            t("som_central", lang), config.formater_fcfa(intervalle["som"]["central"]))
        colonnes_fourchette_som[2].metric(
            t("som_haut", lang), config.formater_fcfa(intervalle["som"]["haut"]))

        if intervalle["som"]["bas"] == intervalle["som"]["haut"]:
            st.caption(t("bas_egal_haut_caption", lang))

    # ---- Decision d'investissement ---------------------------------------
    with st.expander(t("decision_titre", lang), expanded=False):
        capex_min = resultat.hypotheses.get("capex_min_fcfa", 0)
        st.markdown(
            f"{config.badge_html('HYP')} "
            + t("capital_minimal_caption", lang,
                montant=f"**{config.formater_fcfa(capex_min)}**"),
            unsafe_allow_html=True)

        marge_nette = st.slider(
            t("marge_nette_label", lang), 1, 40, 10, step=1,
            help=t("marge_nette_aide", lang),
        ) / 100
        st.markdown(
            f"{config.badge_html('HYP')} {t('marge_nette_caption', lang)}",
            unsafe_allow_html=True)

        ca_mensuel = resultat.ca_mensuel_som
        profit_mensuel = ca_mensuel * marge_nette

        colonnes_decision = st.columns(3)
        colonnes_decision[0].metric(
            t("ca_mensuel_vise", lang), config.formater_fcfa(ca_mensuel))
        colonnes_decision[1].metric(
            t("profit_mensuel_estime", lang), config.formater_fcfa(profit_mensuel))

        if profit_mensuel > 0 and capex_min > 0:
            mois = capex_min / profit_mensuel
            if mois < 1:
                texte_delai = t("jours", lang, n=f"{mois * 30:.0f}")
            elif mois < 24:
                texte_delai = t("mois", lang, n=f"{mois:.0f}")
            else:
                texte_delai = t("ans", lang, n=f"{mois / 12:.1f}")
            colonnes_decision[2].metric(t("delai_amortissement", lang), texte_delai)
            if mois > 60:
                st.warning(t("delai_trop_long_avertissement", lang), icon="⚠️")
        else:
            colonnes_decision[2].metric(
                t("delai_amortissement", lang), t("delai_non_disponible", lang))
            st.warning(t("profit_nul_avertissement", lang), icon="⚠️")

        if intention.budget:
            ecart_budget = intention.budget - capex_min
            if ecart_budget < 0:
                st.caption(t(
                    "budget_insuffisant_caption", lang,
                    budget=config.formater_fcfa(intention.budget),
                    ecart=config.formater_fcfa(abs(ecart_budget))))
            else:
                st.caption(t(
                    "budget_suffisant_caption", lang,
                    budget=config.formater_fcfa(intention.budget),
                    ecart=config.formater_fcfa(ecart_budget)))

    # ---- Onglets --------------------------------------------------------
    onglets = st.tabs([
        t("onglet_synthese", lang), t("onglet_carte", lang), t("onglet_detail", lang),
        t("onglet_comparateur", lang), t("onglet_comparaison", lang),
        t("onglet_validation", lang), t("onglet_sources", lang), t("onglet_export", lang),
    ])

    # Synthese
    with onglets[0]:
        colg, cold = st.columns([3, 2])
        with colg:
            st.markdown(t("lecture_strategique", lang))
            if st.session_state.synthese:
                st.markdown(
                    f'<div class="encart">{st.session_state.synthese}</div>',
                    unsafe_allow_html=True)
        with cold:
            st.plotly_chart(dashboard.graphique_entonnoir(resultat, lang=lang),
                            width='stretch')

        st.markdown(
            f"{t('reperes', lang)} "
            f"{config.badge_html(resultat.provenance.get('population_cible', 'EST'))}",
            unsafe_allow_html=True,
        )
        reperes = st.columns(3)
        reperes[0].metric(t("population_cible", lang),
                          config.formater_nombre(resultat.population_cible))
        transactions = resultat.clients_potentiels()
        if transactions:
            reperes[1].metric(t("transactions_jour", lang),
                              config.formater_nombre(transactions / 365))
            reperes[2].metric(
                t("panier_moyen", lang),
                config.formater_fcfa(resultat.hypotheses["ticket_moyen_fcfa"]))
        else:
            reperes[1].metric(t("regions_couvertes", lang), len(resultat.regions))
            reperes[2].metric(
                t("capex_minimal_secteur", lang),
                config.formater_fcfa(resultat.hypotheses.get("capex_min_fcfa", 0)))

    # Carte
    with onglets[1]:
        st.markdown(t("potentiel_marche_region", lang))
        st.caption(t("score_composite_caption", lang))

        potentiel = _potentiel(resultat.secteur)

        try:
            from streamlit_folium import st_folium

            carte = dashboard.carte_potentiel(potentiel, geographie, lang=lang)
            st_folium(carte, height=560, use_container_width=True,
                      returned_objects=[])
        except ImportError:
            st.error(t("folium_absent", lang))

        if geographie.mode != "cercles":
            manquantes = geo_module.regions_manquantes(geographie)
            if manquantes:
                st.caption(t(
                    "regions_sans_polygone", lang,
                    regions=", ".join(config.REGIONS_AFFICHAGE.get(r, r)
                                     for r in manquantes)))

        st.plotly_chart(dashboard.graphique_tam_regions(potentiel, lang=lang),
                        width='stretch')
        st.plotly_chart(dashboard.graphique_structure(potentiel, lang=lang),
                        width='stretch')

    # Detail regional
    with onglets[2]:
        st.markdown(t("decomposition_marche", lang))
        st.markdown(
            f"{t('indicateur_population', lang)} "
            f"{config.badge_html(resultat.provenance.get('population_cible', 'EST'))}"
            f"&nbsp;&nbsp;·&nbsp;&nbsp;"
            f"TAM / SAM / SOM {config.badge_html(resultat.provenance.get('tam', 'HYP'))}",
            unsafe_allow_html=True,
        )
        detail = resultat.detail_regional.copy()
        detail["Région"] = detail["region"].map(
            lambda r: config.REGIONS_AFFICHAGE.get(r, r))

        affichage = pd.DataFrame({
            t("col_region", lang): detail["Région"],
            t("indicateur_population", lang): detail["population"].map(config.formater_nombre),
            t("population_cible", lang): detail["population_cible"].map(config.formater_nombre),
            t("chart_depense_tete_axis", lang): detail["depense_cible_tete"].map(config.formater_fcfa),
            "TAM": detail["tam_region"].map(config.formater_fcfa),
            "SAM": detail["sam_region"].map(config.formater_fcfa),
            "SOM": detail["som_region"].map(config.formater_fcfa),
            "% TAM": detail["part_tam_pct"].map(lambda v: f"{v:.1f} %"),
        })
        st.dataframe(affichage, hide_index=True, width='stretch')

        st.download_button(
            t("telecharger_csv", lang),
            detail.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"detail_{resultat.secteur}.csv",
            mime="text/csv",
        )

        with st.expander(t("hypotheses_calcul", lang)):
            st.markdown(
                f"{config.badge_html('HYP')} {t('hypotheses_calcul_caption', lang)}",
                unsafe_allow_html=True)
            lignes = []
            for cle, valeur in resultat.hypotheses.items():
                if cle in {"libelle", "libelle_en", "description", "description_en",
                           "poste_depense", "provenance_population_cible"} or valeur is None:
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
        st.markdown(t("comparer_territoires", lang))
        st.caption(t("comparer_territoires_caption", lang,
                    secteur=config.libelle_secteur(resultat.secteur, lang)))

        potentiel_cmp = _potentiel(resultat.secteur)
        options_regions = potentiel_cmp["region"].tolist()

        col_a, col_b = st.columns(2)
        region_a = col_a.selectbox(
            t("territoire_a", lang), options=options_regions, index=0,
            format_func=lambda r: config.REGIONS_AFFICHAGE.get(r, r),
            key="cmp_region_a")
        index_b = 1 if len(options_regions) > 1 else 0
        region_b = col_b.selectbox(
            t("territoire_b", lang), options=options_regions, index=index_b,
            format_func=lambda r: config.REGIONS_AFFICHAGE.get(r, r),
            key="cmp_region_b")

        if region_a == region_b:
            st.info(t("choisir_territoires_differents", lang))
        else:
            ligne_a = potentiel_cmp.loc[potentiel_cmp["region"] == region_a].iloc[0]
            ligne_b = potentiel_cmp.loc[potentiel_cmp["region"] == region_b].iloc[0]
            libelle_a = config.REGIONS_AFFICHAGE.get(region_a, region_a)
            libelle_b = config.REGIONS_AFFICHAGE.get(region_b, region_b)

            tableau_cmp = pd.DataFrame({
                t("col_indicateur", lang): [
                    t("indicateur_population", lang), t("col_tam", lang),
                    t("indicateur_tam_habitant", lang), t("indicateur_score", lang),
                    t("indicateur_rang", lang)],
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
                + t("ecart_tam_caption", lang, plus_grand=plus_grand,
                    ecart=config.formater_fcfa(abs(ecart_tam))),
                unsafe_allow_html=True)

            st.plotly_chart(
                dashboard.graphique_comparaison_territoires(
                    ligne_a, ligne_b, libelle_a, libelle_b,
                    config.libelle_secteur(resultat.secteur, lang), lang=lang),
                width='stretch')

    # Comparaison sectorielle
    with onglets[4]:
        st.markdown(t("trois_secteurs_perimetre", lang))
        comparaison = market.comparer_secteurs(jeu, regions=resultat.regions, lang=lang)
        st.plotly_chart(dashboard.graphique_secteurs(comparaison, lang=lang),
                        width='stretch')
        st.dataframe(
            comparaison[["Secteur", "TAM", "SAM", "SOM", "CA mensuel visé"]]
            .rename(columns={"CA mensuel visé": t("ca_mensuel_vise", lang)}),
            hide_index=True, width='stretch')
        st.caption(t("echelle_log_caption", lang))

    # Validation
    with onglets[5]:
        st.markdown(t("validation_titre", lang))
        st.caption(t("validation_caption", lang))

        validation = jeu.validation_externe()
        n_conformes = int(validation["Conforme"].sum())
        n_total = len(validation)

        if n_conformes == n_total:
            st.success(t("controles_conformes", lang, n=n_conformes, total=n_total),
                      icon="✅")
        else:
            st.warning(t("controles_partiels", lang, n=n_conformes, total=n_total),
                      icon="⚠️")

        affichage_validation = validation.copy()
        affichage_validation["Conforme"] = affichage_validation["Conforme"].map(
            lambda ok: "✅" if ok else "❌")
        st.dataframe(affichage_validation, hide_index=True, width='stretch')

        st.caption(
            t("validation_footer", lang, obs=config.badge_html('OBS'),
              calc=config.badge_html('CALC')),
            unsafe_allow_html=True)

    # Donnees sources
    with onglets[6]:
        st.markdown(t("donnees_normalisees", lang))
        sous = st.tabs([t("sous_onglet_population", lang),
                        t("sous_onglet_depenses", lang),
                        t("sous_onglet_production", lang)])

        with sous[0]:
            pop = jeu.population.copy()
            pop["Région"] = pop["region"].map(
                lambda r: config.REGIONS_AFFICHAGE.get(r, r))
            st.dataframe(
                pop[["Région", "population", "superficie_km2", "densite",
                     "part_nationale_pct", "taux_urbain_pct",
                     "population_urbaine", "nb_menages"]].round(1),
                hide_index=True, width='stretch')
            st.caption(t(
                "total_population_caption", lang,
                total=config.formater_nombre(pop['population'].sum()),
                ref=config.formater_nombre(config.POPULATION_NATIONALE)))

        with sous[1]:
            dep = jeu.depenses.copy()
            dep["Région"] = dep["region"].map(
                lambda r: config.REGIONS_AFFICHAGE.get(r, r))
            colonnes = ["Région", "depense_tete", "depense_totale_region"] + [
                c for c in dep.columns if c.startswith("part_")]
            st.dataframe(dep[colonnes].round(1), hide_index=True,
                         width='stretch')

        with sous[2]:
            st.plotly_chart(dashboard.graphique_production(jeu.production, lang=lang),
                            width='stretch')
            prod = jeu.production.copy()
            prod["Région"] = prod["region"].map(
                lambda r: config.REGIONS_AFFICHAGE.get(r, r))
            st.dataframe(
                prod[["Région"] + [c for c in prod.columns if c.endswith("_t")]],
                hide_index=True, width='stretch')

    # Export
    with onglets[7]:
        st.markdown(t("rapport_exportable", lang))
        st.caption(t("rapport_caption", lang))

        if st.button(t("generer_pdf", lang), type="primary"):
            with st.spinner(t("generation_spinner", lang)):
                try:
                    chemin = generer_rapport(
                        resultat,
                        synthese=st.session_state.synthese,
                        intention_brute=st.session_state.phrase,
                    )
                    st.session_state.pdf = chemin
                    st.success(t("rapport_genere", lang, nom=chemin.name))
                except Exception as erreur:
                    st.error(t("echec_generation", lang, erreur=erreur))

        if st.session_state.get("pdf") and st.session_state.pdf.exists():
            st.download_button(
                t("telecharger_pdf", lang),
                st.session_state.pdf.read_bytes(),
                file_name=st.session_state.pdf.name,
                mime="application/pdf",
                type="primary",
            )

        st.divider()
        st.markdown(t("export_json_titre", lang))
        st.caption(t("export_json_caption", lang))
        st.download_button(
            t("telecharger_json", lang),
            _export_json(resultat, st.session_state.phrase),
            file_name=f"etude_{resultat.secteur}.json",
            mime="application/json",
        )

else:
    # ---- Ecran d'accueil ------------------------------------------------
    st.divider()
    st.markdown(
        f"{t('panorama_national', lang)} {config.badge_html('HYP')}",
        unsafe_allow_html=True)
    st.caption(t("panorama_caption", lang))

    secteur_apercu = st.selectbox(
        t("secteur_explorer", lang),
        options=list(config.SECTEURS),
        format_func=lambda c: config.libelle_secteur(c, lang),
    )
    st.caption(config.description_secteur(secteur_apercu, lang))

    potentiel = _potentiel(secteur_apercu)
    national = market.calculer(jeu, secteur_apercu)

    mesures = st.columns(4)
    mesures[0].metric(t("tam_national", lang), config.formater_fcfa(national.tam))
    mesures[1].metric(t("population_cible", lang),
                      config.formater_nombre(national.population_cible))
    mesures[2].metric(t("region_n1", lang),
                      config.REGIONS_AFFICHAGE.get(potentiel.iloc[0]["region"], ""))
    mesures[3].metric(t("tam_region_n1", lang),
                      config.formater_fcfa(potentiel.iloc[0]["tam_region"]))

    colg, cold = st.columns([3, 2])
    with colg:
        try:
            from streamlit_folium import st_folium

            st_folium(dashboard.carte_potentiel(potentiel, geographie, lang=lang),
                      height=520, use_container_width=True,
                      returned_objects=[])
        except ImportError:
            st.info(t("folium_absent_court", lang))
    with cold:
        st.dataframe(
            potentiel[["rang", "region_affichage", "tam_lisible",
                       "score_potentiel"]].rename(columns={
                           "rang": t("col_rang", lang),
                           "region_affichage": t("col_region", lang),
                           "tam_lisible": t("col_tam", lang),
                           "score_potentiel": t("col_score", lang)}),
            hide_index=True, width='stretch', height=520)

    st.plotly_chart(dashboard.graphique_tam_regions(potentiel, lang=lang),
                    width='stretch')

st.divider()
st.caption(t("footer", lang))
