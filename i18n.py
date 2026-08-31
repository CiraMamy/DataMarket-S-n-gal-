"""
Internationalisation (FR/EN)
============================
Dictionnaire de traduction statique + fonction d'acces t(cle, lang).

Perimetre couvert : l'integralite de l'interface Streamlit (app.py), les
libelles/descriptions sectoriels (config.SECTEURS) et les titres des
graphiques (dashboard.py). La synthese locale (nlp_agent.synthese_locale)
est traduite via son propre parametre `lang`.

Non couvert (limitation assumee) : le commentaire genere par l'API Claude
(nlp_agent.redaction_synthese) reste en francais quelle que soit la langue
choisie -- le module bascule de toute facon sur la synthese locale des que
"Forcer l'analyse locale" est actif (comportement par defaut sans cle API).
Le rapport PDF (report.py) reste egalement en francais uniquement.

Usage :
    from i18n import t
    st.markdown(t("bandeau_titre", lang))
"""

from __future__ import annotations

LANGUES = {"fr": "Français", "en": "English"}

TEXTES: dict[str, dict[str, str]] = {
    # -- Page / bandeau ----------------------------------------------------
    "titre_page": {"fr": "DataMarket Sénégal", "en": "DataMarket Senegal"},
    "bandeau_titre": {"fr": "DataMarket Sénégal", "en": "DataMarket Senegal"},
    "bandeau_sous_titre": {
        "fr": "Transformez les statistiques publiques de l'ANSD en études "
              "de marché chiffrées — TAM, SAM, SOM, carte du potentiel et "
              "rapport exportable.",
        "en": "Turn ANSD public statistics into quantified market studies "
              "— TAM, SAM, SOM, a potential map and an exportable report.",
    },

    # -- Sidebar -------------------------------------------------------------
    "sidebar_soustitre": {
        "fr": "Intelligence économique à partir des données ANSD",
        "en": "Economic intelligence built on ANSD data",
    },
    "api_connectee": {"fr": "API Claude connectée", "en": "Claude API connected"},
    "api_non_configuree": {"fr": "API Claude non configurée", "en": "Claude API not configured"},
    "activer_ia": {"fr": "Activer l'IA", "en": "Enable AI"},
    "activer_ia_contenu": {
        "fr": "Ajoutez votre clé dans `.streamlit/secrets.toml` :\n"
              "```toml\nANTHROPIC_API_KEY = \"sk-ant-...\"\n```\n"
              "ou dans la variable d'environnement `ANTHROPIC_API_KEY`.\n\n"
              "Sans clé, l'analyse des phrases se fait en local "
              "(lexiques et expressions régulières) : moins souple sur les "
              "formulations libres, mais entièrement fonctionnelle et gratuite.",
        "en": "Add your key in `.streamlit/secrets.toml`:\n"
              "```toml\nANTHROPIC_API_KEY = \"sk-ant-...\"\n```\n"
              "or in the `ANTHROPIC_API_KEY` environment variable.\n\n"
              "Without a key, sentence analysis runs locally (keyword "
              "lexicons and regular expressions): less flexible on free-form "
              "phrasing, but fully functional and free.",
    },
    "forcer_local": {"fr": "Forcer l'analyse locale", "en": "Force local analysis"},
    "forcer_local_aide": {
        "fr": "Désactive tout appel à l'API Anthropic.",
        "en": "Disables all calls to the Anthropic API.",
    },
    "qualite_donnees": {"fr": "Qualité des données", "en": "Data quality"},
    "journal_chargement": {"fr": "Journal de chargement", "en": "Loading log"},
    "journal_depot": {
        "fr": "Déposez vos exports ANSD dans `{chemin}` : ils écrasent "
              "automatiquement les valeurs de référence.",
        "en": "Drop your ANSD exports into `{chemin}`: they automatically "
              "override the reference values.",
    },
    "population_nationale_sidebar": {
        "fr": "Population nationale : {pop} hab. (RGPH-5 2023)",
        "en": "National population: {pop} people (RGPH-5 2023)",
    },
    "depense_tete_sidebar": {
        "fr": "Dépense/tête : {dep}/an (EHCVM II 2021-2022)",
        "en": "Spend/capita: {dep}/year (EHCVM II 2021-2022)",
    },
    "ventilation_region_sidebar": {
        "fr": "Ventilation par région {badge} dérivée des parts publiées — "
              "remplaçable par vos exports ANSD.",
        "en": "Regional breakdown {badge} derived from published shares — "
              "replaceable with your own ANSD exports.",
    },
    "legende_badges": {"fr": "Légende des badges", "en": "Badge legend"},

    # -- Impact & methode ------------------------------------------------
    "impact_methode_titre": {
        "fr": "📋 Impact & méthode — à lire avant de commencer",
        "en": "📋 Impact & method — read before you start",
    },
    "impact_probleme_titre": {"fr": "**Problème**", "en": "**Problem**"},
    "impact_probleme_texte": {
        "fr": "Un entrepreneur sénégalais qui veut ouvrir une supérette, un "
              "restaurant ou une unité de transformation n'a aujourd'hui "
              "aucun moyen simple de chiffrer son marché : les données "
              "existent (ANSD) mais sont dispersées, techniques, et jamais "
              "reliées à une question concrète comme « combien de clients à "
              "Mbour ? ».",
        "en": "A Senegalese entrepreneur who wants to open a corner store, a "
              "restaurant or a processing unit currently has no simple way "
              "to size their market: the data exists (ANSD) but is "
              "scattered, technical, and never connected to a concrete "
              "question like “how many customers in Mbour?”",
    },
    "impact_donnees_titre": {"fr": "**Données**", "en": "**Data**"},
    "impact_donnees_texte": {
        "fr": "RGPH-5 (2023), EHCVM II (2021-2022), EAA/DAPSA. Chaque valeur "
              "affichée porte un badge de provenance — OBS observé, EST "
              "estimé, HYP hypothèse — voir la légende dans la barre "
              "latérale.",
        "en": "RGPH-5 (2023), EHCVM II (2021-2022), EAA/DAPSA. Every value "
              "shown carries a provenance badge — OBS observed, EST "
              "estimated, HYP hypothesis — see the legend in the sidebar.",
    },
    "impact_methode_titre2": {"fr": "**Méthode**", "en": "**Method**"},
    "impact_methode_texte": {
        "fr": "TAM = population cible × dépense annuelle sur le poste "
              "adressé. SAM = TAM × zone de chalandise réelle. SOM = SAM × "
              "part de marché visée à 3 ans, ajustée selon le budget "
              "disponible. Chaque coefficient est affiché et modifiable, "
              "jamais une boîte noire.",
        "en": "TAM = target population × annual spend on the addressed "
              "category. SAM = TAM × real catchment area. SOM = SAM × "
              "market share targeted over 3 years, adjusted for available "
              "budget. Every coefficient is shown and editable, never a "
              "black box.",
    },
    "impact_limites_titre": {"fr": "**Limites assumées**", "en": "**Assumed limitations**"},
    "impact_limites_texte": {
        "fr": "Les dépenses par tête sont des moyennes régionales qui "
              "masquent des écarts de revenu. Le SOM ne modélise pas la "
              "concurrence de rue. Les données EHCVM datent de 2021-2022 "
              "(francs courants). Voir l'onglet *Validation* pour la "
              "calibration face à des chiffres publiés.",
        "en": "Per-capita spend figures are regional averages that mask "
              "income disparities. SOM does not model street-level "
              "competition. EHCVM data is from 2021-2022 (current francs). "
              "See the *Validation* tab for calibration against published "
              "figures.",
    },

    # -- Cas types -----------------------------------------------------------
    "cas_types_titre": {"fr": "Cas types", "en": "Sample cases"},
    "cas_types_caption": {
        "fr": "Chargement immédiat, sans dépendre de l'interprétation d'une "
              "phrase — idéal pour explorer l'outil ou en démonstration.",
        "en": "Loads instantly, without depending on sentence "
              "interpretation — ideal for exploring the tool or for a demo.",
    },
    "cas_mbour": {"fr": "Supérette à Mbour", "en": "Corner store in Mbour"},
    "cas_ziguinchor": {
        "fr": "Transformation de mangue à Ziguinchor",
        "en": "Mango processing in Ziguinchor",
    },
    "cas_dakar": {
        "fr": "Restauration santé à Dakar",
        "en": "Health-focused catering in Dakar",
    },

    # -- Module 3 : saisie ----------------------------------------------------
    "decrivez_projet": {"fr": "Décrivez votre projet", "en": "Describe your project"},
    "exemple_mbour": {
        "fr": "Je veux ouvrir une supérette à Mbour",
        "en": "I want to open a corner store in Mbour",
    },
    "exemple_dakar": {
        "fr": "Restaurant pour diabétiques à Dakar avec 25 millions",
        "en": "Diabetic-friendly restaurant in Dakar with 25 million",
    },
    "exemple_kaolack": {
        "fr": "Unité de transformation d'arachide à Kaolack",
        "en": "Peanut processing unit in Kaolack",
    },
    "exemple_touba": {
        "fr": "Une boutique de quartier à Touba, budget 3 millions",
        "en": "A neighborhood shop in Touba, 3 million budget",
    },
    "phrase_label": {"fr": "Votre projet en une phrase", "en": "Your project in one sentence"},
    "phrase_placeholder": {
        "fr": "Ex. : Je veux ouvrir une supérette à Mbour avec 15 millions de budget",
        "en": "E.g.: I want to open a corner store in Mbour with a 15 million budget",
    },
    "analyser": {"fr": "Analyser", "en": "Analyze"},
    "analyse_spinner": {"fr": "Analyse de votre projet…", "en": "Analyzing your project…"},
    "saisir_description": {
        "fr": "Saisissez d'abord une description de votre projet.",
        "en": "Please enter a description of your project first.",
    },

    # -- Interpretation --------------------------------------------------
    "interpretation": {"fr": "Interprétation", "en": "Interpretation"},
    "moteur": {"fr": "Moteur", "en": "Engine"},
    "moteur_claude": {"fr": "Claude", "en": "Claude"},
    "moteur_lien": {"fr": "Lien partagé", "en": "Shared link"},
    "moteur_etude_cas": {"fr": "Étude de cas", "en": "Sample case"},
    "moteur_local": {"fr": "Local", "en": "Local"},
    "confiance": {"fr": "Confiance", "en": "Confidence"},
    "detail_interpretation": {"fr": "Détail de l'interprétation", "en": "Interpretation detail"},
    "ajustez_ci_dessous": {
        "fr": "Ajustez ci-dessous si l'interprétation ne correspond pas à votre projet.",
        "en": "Adjust below if the interpretation doesn't match your project.",
    },
    "secteur_label": {"fr": "Secteur", "en": "Sector"},
    "regions_label": {"fr": "Régions", "en": "Regions"},
    "aucune_region_avertissement": {
        "fr": "⚠️ Aucune région sélectionnée : le recalcul portera sur les "
              "14 régions (national).",
        "en": "⚠️ No region selected: the recalculation will cover all 14 "
              "regions (national).",
    },
    "zone_chalandise_label": {
        "fr": "Zone de chalandise (% de la région)",
        "en": "Catchment area (% of the region)",
    },
    "part_marche_visee_label": {
        "fr": "Part de marché visée à 3 ans (%)",
        "en": "Market share targeted over 3 years (%)",
    },
    "recalculer": {"fr": "Recalculer avec ces paramètres", "en": "Recalculate with these settings"},

    # -- Resultat -------------------------------------------------------
    "resultat_titre": {"fr": "Résultat", "en": "Result"},
    "resultat_caption": {
        "fr": "TAM, SAM et SOM combinent des données observées et des "
              "hypothèses sectorielles modifiables (captation, prévalence, "
              "part transformée) : ils héritent donc du classement "
              "Hypothèse — voir l'onglet « Détail régional » pour la liste "
              "complète.",
        "en": "TAM, SAM and SOM combine observed data with editable "
              "sector-level assumptions (capture rate, prevalence, "
              "processed share): they therefore inherit the Hypothesis "
              "classification — see the “Regional detail” tab for "
              "the full list.",
    },
    "lien_partageable_caption": {
        "fr": "🔗 L'adresse de cette page encode les paramètres de l'étude "
              "— copiez-la pour la partager ou la retrouver plus tard.",
        "en": "🔗 This page's address encodes the study's parameters — "
              "copy it to share it or find it again later.",
    },
    "tam_marche_total": {"fr": "TAM — marché total", "en": "TAM — total market"},
    "sam_accessible": {"fr": "SAM — accessible", "en": "SAM — accessible"},
    "som_captable": {"fr": "SOM — captable à 3 ans", "en": "SOM — obtainable in 3 years"},
    "pct_du_tam": {"fr": "{pct} % du TAM", "en": "{pct}% of TAM"},
    "ca_mensuel_vise": {"fr": "CA mensuel visé", "en": "Monthly revenue target"},

    # -- Analyse de sensibilite -------------------------------------------
    "sensibilite_titre": {
        "fr": "📐 Intervalle de confiance et analyse de sensibilité",
        "en": "📐 Confidence interval and sensitivity analysis",
    },
    "sensibilite_caption": {
        "fr": "Fait varier le(s) coefficient(s) de modélisation les plus "
              "incertains du secteur — **{coefs}** — en laissant les "
              "autres hypothèses (zone de chalandise, part de marché "
              "visée, budget) fixées à la valeur choisie ci-dessus. Ce "
              "n'est pas une marge arbitraire appliquée au TAM.",
        "en": "Varies the sector's most uncertain modeling coefficient(s) "
              "— **{coefs}** — while keeping other assumptions (catchment "
              "area, targeted market share, budget) fixed at the value "
              "chosen above. This is not an arbitrary margin applied to "
              "TAM.",
    },
    "marge_incertitude_label": {
        "fr": "Marge d'incertitude sur les hypothèses clés (± %)",
        "en": "Uncertainty margin on key assumptions (± %)",
    },
    "tam_bas": {"fr": "TAM bas", "en": "TAM low"},
    "tam_central": {"fr": "TAM central", "en": "TAM central"},
    "tam_haut": {"fr": "TAM haut", "en": "TAM high"},
    "som_bas": {"fr": "SOM bas", "en": "SOM low"},
    "som_central": {"fr": "SOM central", "en": "SOM central"},
    "som_haut": {"fr": "SOM haut", "en": "SOM high"},
    "bas_egal_haut_caption": {
        "fr": "Bas = haut ici : le gisement de matière première régionale "
              "est le facteur limitant sur ce périmètre, pas la demande — "
              "faire varier la part transformée n'a alors aucun effet.",
        "en": "Low = high here: the regional raw-material pool is the "
              "limiting factor on this scope, not demand — varying the "
              "processed share has no effect in that case.",
    },

    # -- Decision d'investissement -----------------------------------------
    "decision_titre": {"fr": "💰 Décision d'investissement", "en": "💰 Investment decision"},
    "capital_minimal_caption": {
        "fr": "Capital minimal observé pour ce secteur : **{montant}**.",
        "en": "Minimum capital observed for this sector: **{montant}**.",
    },
    "marge_nette_label": {"fr": "Marge nette estimée (%)", "en": "Estimated net margin (%)"},
    "marge_nette_aide": {
        "fr": "Hypothèse à régler vous-même selon votre connaissance du "
              "secteur — ce n'est pas une donnée ANSD. Marge nette = profit "
              "après toutes charges, en % du chiffre d'affaires.",
        "en": "An assumption you set yourself based on your knowledge of "
              "the sector — this is not ANSD data. Net margin = profit "
              "after all expenses, as a % of revenue.",
    },
    "marge_nette_caption": {
        "fr": "Hypothèse saisie par vous, non issue des données ANSD.",
        "en": "Assumption entered by you, not sourced from ANSD data.",
    },
    "profit_mensuel_estime": {"fr": "Profit mensuel estimé", "en": "Estimated monthly profit"},
    "delai_amortissement": {"fr": "Délai d'amortissement", "en": "Payback period"},
    "jours": {"fr": "{n} jours", "en": "{n} days"},
    "mois": {"fr": "{n} mois", "en": "{n} months"},
    "ans": {"fr": "{n} ans", "en": "{n} years"},
    "delai_non_disponible": {"fr": "n/d", "en": "n/a"},
    "delai_trop_long_avertissement": {
        "fr": "Délai d'amortissement supérieur à 5 ans : ce plan n'est "
              "probablement pas viable en l'état — reconsidérez le budget, "
              "la marge visée ou l'ambition de part de marché (SOM).",
        "en": "Payback period over 5 years: this plan is probably not "
              "viable as-is — reconsider the budget, the targeted margin, "
              "or the market-share ambition (SOM).",
    },
    "profit_nul_avertissement": {
        "fr": "Le chiffre d'affaires visé ne génère aucun profit positif "
              "avec cette marge : le capital ne serait jamais amorti selon "
              "ce plan.",
        "en": "The targeted revenue generates no positive profit at this "
              "margin: the capital would never be paid back under this "
              "plan.",
    },
    "budget_insuffisant_caption": {
        "fr": "Votre budget ({budget}) est inférieur de {ecart} au capital "
              "minimal observé — le SOM a déjà été réduit en conséquence "
              "(voir les avertissements ci-dessus).",
        "en": "Your budget ({budget}) is {ecart} below the minimum capital "
              "observed — SOM has already been reduced accordingly (see "
              "the warnings above).",
    },
    "budget_suffisant_caption": {
        "fr": "Votre budget ({budget}) couvre le capital minimal observé, "
              "avec une marge de {ecart}.",
        "en": "Your budget ({budget}) covers the minimum capital observed, "
              "with a margin of {ecart}.",
    },

    # -- Scenario Engine ---------------------------------------------------
    "scenarios_titre": {"fr": "🎯 Scénarios (conservateur / réaliste / ambitieux)", "en": "🎯 Scenarios (conservative / realistic / ambitious)"},
    "scenarios_caption": {
        "fr": "Trois niveaux d'ambition commerciale sur la même modélisation "
              "— jamais un seul chiffre ne doit être lu comme une prédiction "
              "de l'avenir. Chaque scénario multiplie la part de marché "
              "visée ; le TAM ne change pas, seule l'ambition sur le SOM varie.",
        "en": "Three levels of commercial ambition on the same model — no "
              "single figure should ever be read as a prediction of the "
              "future. Each scenario multiplies the targeted market share; "
              "TAM stays the same, only the SOM ambition changes.",
    },
    "scenario_conservateur": {"fr": "Conservateur", "en": "Conservative"},
    "scenario_realiste": {"fr": "Réaliste", "en": "Realistic"},
    "scenario_ambitieux": {"fr": "Ambitieux", "en": "Ambitious"},
    "col_scenario": {"fr": "Scénario", "en": "Scenario"},
    "col_part_visee": {"fr": "Part visée", "en": "Targeted share"},
    "col_risque": {"fr": "Risque", "en": "Risk"},
    "risque_conservateur": {
        "fr": "Modéré — objectif prudent : sous-exploite le marché si la "
              "concurrence réelle est plus faible que redoutée.",
        "en": "Moderate — cautious target: under-exploits the market if "
              "actual competition is weaker than feared.",
    },
    "risque_realiste": {
        "fr": "Faible — correspond à l'hypothèse par défaut calibrée du secteur.",
        "en": "Low — matches the sector's calibrated default assumption.",
    },
    "risque_ambitieux": {
        "fr": "Élevé — suppose une exécution et une part de marché "
              "nettement supérieures à la référence sectorielle.",
        "en": "High — assumes execution and market share well above the "
              "sector's reference point.",
    },

    # -- Onglets ----------------------------------------------------------
    "onglet_synthese": {"fr": "Synthèse", "en": "Summary"},
    "onglet_carte": {"fr": "Carte du potentiel", "en": "Potential map"},
    "onglet_detail": {"fr": "Détail régional", "en": "Regional detail"},
    "onglet_comparateur": {"fr": "Comparateur de territoires", "en": "Territory comparator"},
    "onglet_comparaison": {"fr": "Comparaison sectorielle", "en": "Sector comparison"},
    "onglet_validation": {"fr": "Validation", "en": "Validation"},
    "onglet_sources": {"fr": "Données sources", "en": "Source data"},
    "onglet_export": {"fr": "Export", "en": "Export"},

    # -- Synthese -----------------------------------------------------------
    "lecture_strategique": {"fr": "#### Lecture stratégique", "en": "#### Strategic reading"},
    "reperes": {"fr": "#### Repères", "en": "#### Key figures"},
    "population_cible": {"fr": "Population cible", "en": "Target population"},
    "transactions_jour": {"fr": "Transactions / jour", "en": "Transactions / day"},
    "panier_moyen": {"fr": "Panier moyen retenu", "en": "Average basket used"},
    "regions_couvertes": {"fr": "Régions couvertes", "en": "Regions covered"},
    "capex_minimal_secteur": {"fr": "Capex minimal du secteur", "en": "Sector minimum capex"},

    # -- Carte --------------------------------------------------------------
    "potentiel_marche_region": {
        "fr": "#### Potentiel de marché par région",
        "en": "#### Market potential by region",
    },
    "score_composite_caption": {
        "fr": "Score composite : 70 % volume de marché (TAM absolu) et "
              "30 % intensité (TAM par habitant). Calculé sur les 14 "
              "régions pour le secteur retenu, indépendamment du périmètre "
              "de votre projet.",
        "en": "Composite score: 70% market volume (absolute TAM) and 30% "
              "intensity (TAM per capita). Computed across all 14 regions "
              "for the chosen sector, independently of your project's scope.",
    },
    "folium_absent": {
        "fr": "Le paquet `streamlit-folium` est absent. Installez-le avec "
              "`pip install streamlit-folium` pour afficher la carte.",
        "en": "The `streamlit-folium` package is missing. Install it with "
              "`pip install streamlit-folium` to display the map.",
    },
    "folium_absent_court": {
        "fr": "Installez `streamlit-folium` pour afficher la carte.",
        "en": "Install `streamlit-folium` to display the map.",
    },
    "regions_sans_polygone": {
        "fr": "Régions sans polygone dans le fond de carte : {regions}",
        "en": "Regions without a polygon on the basemap: {regions}",
    },

    # -- Detail regional ------------------------------------------------
    "decomposition_marche": {
        "fr": "#### Décomposition du marché sur votre périmètre",
        "en": "#### Market breakdown over your scope",
    },
    "telecharger_csv": {"fr": "Télécharger ce tableau (CSV)", "en": "Download this table (CSV)"},
    "hypotheses_calcul": {"fr": "Hypothèses de calcul utilisées", "en": "Calculation assumptions used"},
    "hypotheses_calcul_caption": {
        "fr": "Chaque ligne ci-dessous est un paramètre de modélisation "
              "explicite — ajustez-le avec vos observations terrain.",
        "en": "Each line below is an explicit modeling parameter — adjust "
              "it using your own field observations.",
    },

    # -- Comparateur de territoires ----------------------------------------
    "comparer_territoires": {"fr": "#### Comparer deux territoires", "en": "#### Compare two territories"},
    "comparer_territoires_caption": {
        "fr": "Comparaison sur les hypothèses par défaut du secteur "
              "« {secteur} », indépendamment du périmètre de votre étude.",
        "en": "Comparison using the default assumptions of the "
              "“{secteur}” sector, independently of your study's scope.",
    },
    "territoire_a": {"fr": "Territoire A", "en": "Territory A"},
    "territoire_b": {"fr": "Territoire B", "en": "Territory B"},
    "choisir_territoires_differents": {
        "fr": "Choisissez deux territoires différents pour comparer.",
        "en": "Choose two different territories to compare.",
    },
    "indicateur_population": {"fr": "Population", "en": "Population"},
    "indicateur_tam_habitant": {"fr": "TAM / habitant", "en": "TAM / capita"},
    "indicateur_score": {"fr": "Score de potentiel", "en": "Potential score"},
    "indicateur_rang": {"fr": "Rang national", "en": "National rank"},
    "ecart_tam_caption": {
        "fr": "Le TAM de **{plus_grand}** dépasse celui de son comparateur "
              "de {ecart}, sur les hypothèses par défaut du secteur.",
        "en": "**{plus_grand}**'s TAM exceeds its comparator's by {ecart}, "
              "under the sector's default assumptions.",
    },

    # -- Comparaison sectorielle ------------------------------------------
    "trois_secteurs_perimetre": {
        "fr": "#### Les trois secteurs sur le même périmètre",
        "en": "#### The three sectors on the same scope",
    },
    "echelle_log_caption": {
        "fr": "Échelle logarithmique : les ordres de grandeur diffèrent "
              "fortement d'un secteur à l'autre. La restauration santé vise "
              "une niche étroite mais à forte valeur unitaire ; le commerce "
              "de proximité adresse un marché de masse.",
        "en": "Logarithmic scale: orders of magnitude differ sharply "
              "between sectors. Health-focused catering targets a narrow "
              "but high-unit-value niche; the corner-store sector addresses "
              "a mass market.",
    },

    # -- Validation -----------------------------------------------------
    "validation_titre": {
        "fr": "#### Calibration face à des chiffres publiés indépendamment",
        "en": "#### Calibration against independently published figures",
    },
    "validation_caption": {
        "fr": "Ce ne sont pas des sorties du modèle comparées à "
              "elles-mêmes : chaque ligne confronte une grandeur "
              "recalculée par le pipeline à un chiffre publié par l'ANSD, "
              "indépendamment de ce projet.",
        "en": "These are not model outputs compared to themselves: each "
              "row checks a pipeline-recalculated figure against a number "
              "published by ANSD, independently of this project.",
    },
    "controles_conformes": {
        "fr": "{n}/{total} contrôles conformes aux seuils de tolérance.",
        "en": "{n}/{total} checks within tolerance thresholds.",
    },
    "controles_partiels": {
        "fr": "{n}/{total} contrôles conformes — voir le détail ci-dessous.",
        "en": "{n}/{total} checks within tolerance — see detail below.",
    },
    "validation_footer": {
        "fr": "{obs} Valeurs publiées = chiffres officiels RGPH-5 / EHCVM "
              "II cités dans `README.md`. {calc} Valeurs du modèle = "
              "recalculées à chaque chargement à partir des données de "
              "`ref_*.csv` (ou de vos exports dans `data/raw/` s'ils sont "
              "présents). Ces mêmes contrôles sont vérifiés automatiquement "
              "à chaque push par `test_datamarket.py::TestChargement` — "
              "cette page en est la version lisible pour un évaluateur.",
        "en": "{obs} Published values = official RGPH-5 / EHCVM II figures "
              "cited in `README.md`. {calc} Model values = recalculated on "
              "every load from `ref_*.csv` (or your own exports in "
              "`data/raw/` if present). These same checks run automatically "
              "on every push via `test_datamarket.py::TestChargement` — "
              "this page is the human-readable version for an evaluator.",
    },

    # -- Donnees sources --------------------------------------------------
    "donnees_normalisees": {"fr": "#### Données ANSD normalisées", "en": "#### Normalized ANSD data"},
    "sous_onglet_population": {"fr": "Population (RGPH-5)", "en": "Population (RGPH-5)"},
    "sous_onglet_depenses": {"fr": "Dépenses (EHCVM II)", "en": "Spending (EHCVM II)"},
    "sous_onglet_production": {"fr": "Production agricole (EAA)", "en": "Agricultural output (EAA)"},
    "total_population_caption": {
        "fr": "Total : {total} habitants — à comparer au chiffre officiel "
              "RGPH-5 de {ref}.",
        "en": "Total: {total} people — to compare against the official "
              "RGPH-5 figure of {ref}.",
    },

    # -- Export -------------------------------------------------------------
    "rapport_exportable": {"fr": "#### Rapport d'étude exportable", "en": "#### Exportable study report"},
    "rapport_caption": {
        "fr": "Document de 4 pages : synthèse chiffrée, détail région par "
              "région, méthodologie complète, sources et limites.",
        "en": "A 4-page document: quantified summary, region-by-region "
              "detail, full methodology, sources and limitations.",
    },
    "generer_pdf": {"fr": "Générer le rapport PDF", "en": "Generate PDF report"},
    "generation_spinner": {"fr": "Génération du rapport…", "en": "Generating the report…"},
    "rapport_genere": {"fr": "Rapport généré : {nom}", "en": "Report generated: {nom}"},
    "echec_generation": {"fr": "Échec de la génération : {erreur}", "en": "Generation failed: {erreur}"},
    "telecharger_pdf": {"fr": "Télécharger le PDF", "en": "Download the PDF"},
    "export_json_titre": {"fr": "#### Export reproductible (JSON)", "en": "#### Reproducible export (JSON)"},
    "export_json_caption": {
        "fr": "Entrées, hypothèses, provenance et sorties du calcul en un "
              "seul fichier — de quoi rejouer ou auditer les chiffres sans "
              "repasser par l'interface.",
        "en": "Inputs, assumptions, provenance and outputs of the "
              "calculation in one file — enough to replay or audit the "
              "figures without going through the interface.",
    },
    "telecharger_json": {
        "fr": "Télécharger le calcul complet (JSON)",
        "en": "Download the full calculation (JSON)",
    },

    # -- Ecran d'accueil ----------------------------------------------------
    "panorama_national": {"fr": "### Panorama national", "en": "### National overview"},
    "panorama_caption": {
        "fr": "Le TAM combine des données observées et des hypothèses "
              "sectorielles modifiables — voir la légende des badges dans "
              "la barre latérale.",
        "en": "TAM combines observed data with editable sector assumptions "
              "— see the badge legend in the sidebar.",
    },
    "secteur_explorer": {"fr": "Secteur à explorer", "en": "Sector to explore"},
    "tam_national": {"fr": "TAM national", "en": "National TAM"},
    "region_n1": {"fr": "Région n°1", "en": "Top region"},
    "tam_region_n1": {"fr": "TAM de la région n°1", "en": "Top region's TAM"},
    "col_rang": {"fr": "Rang", "en": "Rank"},
    "col_region": {"fr": "Région", "en": "Region"},
    "col_tam": {"fr": "TAM", "en": "TAM"},
    "col_score": {"fr": "Score", "en": "Score"},
    "col_indicateur": {"fr": "Indicateur", "en": "Indicator"},

    # -- Synthese locale (nlp_agent.synthese_locale) ------------------------
    "synth_ligne1": {
        "fr": "Sur le périmètre « {perimetre} », le marché total adressable "
              "pour l'activité « {secteur} » s'élève à {tam} par an, pour "
              "une population cible de {population} personnes.",
        "en": "Over the “{perimetre}” scope, the total addressable market "
              "for “{secteur}” amounts to {tam} per year, for a target "
              "population of {population} people.",
    },
    "synth_ligne2": {
        "fr": "Compte tenu de la zone de chalandise retenue, le marché "
              "réellement accessible (SAM) représente {sam}, soit "
              "{part_sam} % du TAM. L'objectif de capture à trois ans (SOM) "
              "est de {som} ({part_som} % du TAM), soit un chiffre "
              "d'affaires mensuel de {ca_mensuel}.",
        "en": "Given the chosen catchment area, the actually reachable "
              "market (SAM) is {sam}, or {part_sam}% of TAM. The 3-year "
              "capture target (SOM) is {som} ({part_som}% of TAM), i.e. a "
              "monthly revenue of {ca_mensuel}.",
    },
    "synth_transactions": {
        "fr": "À un panier moyen de {ticket}, cet objectif correspond à "
              "environ {transactions} transactions par jour.",
        "en": "At an average basket of {ticket}, this target corresponds "
              "to roughly {transactions} transactions per day.",
    },
    "synth_region_porteuse": {
        "fr": "La région la plus porteuse du périmètre est {region}, qui "
              "concentre {part} % du marché adressable.",
        "en": "The strongest region in scope is {region}, which "
              "accounts for {part}% of the addressable market.",
    },
    "synth_avertissement_final": {
        "fr": "Ces montants sont des ordres de grandeur dérivés de moyennes "
              "régionales publiées par l'ANSD. Ils ne remplacent pas une "
              "étude terrain sur la concurrence locale, l'emplacement et "
              "les prix pratiqués.",
        "en": "These figures are orders of magnitude derived from regional "
              "averages published by ANSD. They do not replace field "
              "research on local competition, location and pricing.",
    },

    # -- Graphiques (dashboard.py) ------------------------------------------
    "map_titre_potentiel": {"fr": "Potentiel de marché", "en": "Market potential"},
    "map_tam_annuel": {"fr": "TAM annuel", "en": "Annual TAM"},
    "chart_tam_region_titre": {
        "fr": "Marché total adressable (TAM) par région",
        "en": "Total addressable market (TAM) by region",
    },
    "chart_tam_annuel_axis": {"fr": "TAM annuel (FCFA)", "en": "Annual TAM (FCFA)"},
    "chart_entonnoir_titre": {
        "fr": "Entonnoir de marché — {secteur}",
        "en": "Market funnel — {secteur}",
    },
    "chart_tam_label": {"fr": "TAM<br><i>marché total</i>", "en": "TAM<br><i>total market</i>"},
    "chart_sam_label": {"fr": "SAM<br><i>marché accessible</i>", "en": "SAM<br><i>accessible market</i>"},
    "chart_som_label": {"fr": "SOM<br><i>captable à 3 ans</i>", "en": "SOM<br><i>obtainable in 3 years</i>"},
    "chart_comparaison_secteurs_titre": {
        "fr": "Comparaison des trois secteurs sur le périmètre retenu",
        "en": "Comparison of the three sectors over the chosen scope",
    },
    "chart_fcfa_an_axis": {"fr": "FCFA par an", "en": "FCFA per year"},
    "chart_structure_titre": {
        "fr": "Volume contre valeur : structure du marché par région",
        "en": "Volume vs. value: market structure by region",
    },
    "chart_population_cible_axis": {
        "fr": "Population cible (habitants)", "en": "Target population (people)",
    },
    "chart_depense_tete_axis": {
        "fr": "Dépense annuelle par tête sur le poste (FCFA)",
        "en": "Annual per-capita spend on the category (FCFA)",
    },
    "chart_score_label": {"fr": "Score", "en": "Score"},
    "chart_production_titre": {
        "fr": "Production agricole par région et par culture (tonnes)",
        "en": "Agricultural output by region and crop (metric tons)",
    },
    "chart_production_axis": {"fr": "Production (tonnes)", "en": "Output (metric tons)"},
    "chart_culture_arachide": {"fr": "Arachide", "en": "Peanut"},
    "chart_culture_mil_sorgho": {"fr": "Mil / sorgho", "en": "Millet / sorghum"},
    "chart_culture_riz": {"fr": "Riz paddy", "en": "Paddy rice"},
    "chart_culture_mais": {"fr": "Maïs", "en": "Maize"},
    "chart_culture_horticulture": {"fr": "Horticulture", "en": "Horticulture"},
    "chart_comparaison_territoires_titre": {
        "fr": "{a} contre {b} — {secteur}",
        "en": "{a} vs. {b} — {secteur}",
    },
    "chart_indice_relatif_axis": {
        "fr": "Indice relatif (100 = valeur la plus élevée des deux territoires)",
        "en": "Relative index (100 = higher of the two territories)",
    },
    "chart_fourchette_titre": {
        "fr": "Fourchette TAM / SOM — {secteur} (± {marge} sur les hypothèses clés)",
        "en": "TAM / SOM range — {secteur} (± {marge} on key assumptions)",
    },

    # -- Pied de page ---------------------------------------------------
    "footer": {
        "fr": "DataMarket Sénégal — sources : RGPH-5 2023 (ANSD), EHCVM II "
              "2021-2022, EAA/DAPSA. Outil de cadrage : les montants sont "
              "des ordres de grandeur dérivés de moyennes régionales et ne "
              "remplacent pas une étude terrain.",
        "en": "DataMarket Senegal — sources: RGPH-5 2023 (ANSD), EHCVM II "
              "2021-2022, EAA/DAPSA. A scoping tool: figures are orders of "
              "magnitude derived from regional averages and do not replace "
              "field research.",
    },
}


def t(cle: str, lang: str = "fr", **kwargs) -> str:
    """
    Traduit `cle` dans `lang` ("fr" ou "en"). Repli sur le francais si la
    langue est absente, puis sur la cle elle-meme si la cle est inconnue
    (evite un plantage plutot que de masquer un texte manquant).
    """
    entree = TEXTES.get(cle)
    if entree is None:
        return cle
    texte = entree.get(lang, entree.get("fr", cle))
    if kwargs:
        try:
            return texte.format(**kwargs)
        except (KeyError, IndexError):
            return texte
    return texte
