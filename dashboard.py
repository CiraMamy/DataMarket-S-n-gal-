"""
MODULE 4 (partie visualisation) - Cartes et graphiques
======================================================

  carte_potentiel()        Carte choroplethe Leaflet des 14 regions,
                           coloree par score de potentiel de marche.
  graphique_tam_regions()  Barres horizontales du TAM par region.
  graphique_entonnoir()    Entonnoir TAM -> SAM -> SOM.
  graphique_secteurs()     Comparaison des trois secteurs.
  graphique_structure()    Population cible vs depense par tete.
  graphique_comparaison_territoires()  Deux regions cote a cote.
"""

from __future__ import annotations

import branca.colormap as cm
import folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import config
from geo import Geographie
from market import ResultatMarche


# ==========================================================================
# Carte
# ==========================================================================

def carte_potentiel(potentiel: pd.DataFrame, geo: Geographie,
                    titre_metrique: str = "Potentiel de marché") -> folium.Map:
    """
    Carte Leaflet (via folium) des 14 regions.

    - Si les polygones sont disponibles : choroplethe continue.
    - Sinon : pastilles proportionnelles sur les chefs-lieux.
    """
    carte = folium.Map(
        location=[14.45, -14.45],
        zoom_start=7,
        tiles="CartoDB positron",
        control_scale=True,
    )

    donnees = potentiel.set_index("region")
    scores = donnees["score_potentiel"]

    echelle = cm.LinearColormap(
        colors=["#F7FCF5", "#C7E9C0", "#74C476", "#31A354", "#00853F", "#00441B"],
        vmin=float(scores.min()),
        vmax=float(scores.max()),
        caption=f"{titre_metrique} (score 0-100)",
    )

    if geo.a_polygones:
        def style(entite):
            region = entite["properties"]["region"]
            score = scores.get(region)
            return {
                "fillColor": echelle(score) if score is not None else "#DDDDDD",
                "color": "#FFFFFF",
                "weight": 1.4,
                "fillOpacity": 0.85,
            }

        def surbrillance(_entite):
            return {"weight": 3, "color": "#1B2A32", "fillOpacity": 0.95}

        # Injection des donnees dans les proprietes pour l'infobulle
        geojson = {
            "type": "FeatureCollection",
            "features": [],
        }
        for entite in geo.geojson["features"]:
            entite = json_copie(entite)
            region = entite["properties"]["region"]
            if region in donnees.index:
                ligne = donnees.loc[region]
                entite["properties"].update({
                    "score": f"{ligne['score_potentiel']:.1f} / 100",
                    "rang": f"#{int(ligne['rang'])}",
                    "tam": config.formater_fcfa(ligne["tam_region"]),
                    "population": config.formater_nombre(ligne["population"]),
                    "tam_habitant": config.formater_fcfa(ligne["tam_par_habitant"]),
                })
            geojson["features"].append(entite)

        folium.GeoJson(
            geojson,
            name="Régions",
            style_function=style,
            highlight_function=surbrillance,
            tooltip=folium.GeoJsonTooltip(
                fields=["region_affichage", "rang", "score", "tam",
                        "population", "tam_habitant"],
                aliases=["Région", "Rang", "Score", "TAM annuel",
                         "Population", "TAM / habitant"],
                localize=True,
                sticky=True,
                style=(
                    "background-color: white; border: 1px solid #00853F; "
                    "border-radius: 4px; padding: 8px; font-family: sans-serif; "
                    "font-size: 12px;"
                ),
            ),
        ).add_to(carte)

    else:
        # Mode degrade : pastilles proportionnelles
        maxi = float(donnees["tam_region"].max()) or 1.0
        for region, ligne in donnees.iterrows():
            if region not in config.CENTROIDES:
                continue
            lat, lon = config.CENTROIDES[region]
            rayon = 8 + 32 * (ligne["tam_region"] / maxi) ** 0.5
            folium.CircleMarker(
                location=[lat, lon],
                radius=rayon,
                color="#FFFFFF",
                weight=1.5,
                fill=True,
                fill_color=echelle(ligne["score_potentiel"]),
                fill_opacity=0.85,
                tooltip=folium.Tooltip(
                    f"<b>{config.REGIONS_AFFICHAGE.get(region, region)}</b><br>"
                    f"Rang : #{int(ligne['rang'])}<br>"
                    f"Score : {ligne['score_potentiel']:.1f} / 100<br>"
                    f"TAM : {config.formater_fcfa(ligne['tam_region'])}<br>"
                    f"Population : {config.formater_nombre(ligne['population'])}"
                ),
            ).add_to(carte)

    echelle.add_to(carte)
    folium.LayerControl(collapsed=True).add_to(carte)
    return carte


def json_copie(objet):
    """Copie profonde legere d'une entite GeoJSON."""
    import copy

    return copy.deepcopy(objet)


# ==========================================================================
# Graphiques Plotly
# ==========================================================================

_MISE_EN_PAGE = dict(
    font=dict(family="Inter, Segoe UI, sans-serif", size=13),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=20, t=60, b=40),
    hoverlabel=dict(bgcolor="white", font_size=12),
)


def graphique_tam_regions(potentiel: pd.DataFrame, n: int = 14) -> go.Figure:
    """Barres horizontales du TAM annuel par region."""
    df = potentiel.nlargest(n, "tam_region").sort_values("tam_region")

    figure = go.Figure(
        go.Bar(
            x=df["tam_region"],
            y=df["region_affichage"],
            orientation="h",
            marker=dict(
                color=df["score_potentiel"],
                colorscale=[[0, "#C7E9C0"], [0.5, "#41AB5D"], [1, "#00441B"]],
                showscale=False,
                line=dict(color="rgba(255,255,255,0.6)", width=1),
            ),
            text=df["tam_region"].map(config.formater_fcfa),
            textposition="outside",
            textfont=dict(size=11),
            hovertemplate=(
                "<b>%{y}</b><br>TAM : %{text}<br>"
                "Score : %{marker.color:.1f}/100<extra></extra>"
            ),
        )
    )
    figure.update_layout(
        title="Marché total adressable (TAM) par région",
        xaxis_title="TAM annuel (FCFA)",
        yaxis_title=None,
        height=max(420, 32 * len(df)),
        **_MISE_EN_PAGE,
    )
    figure.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.06)")
    return figure


def graphique_entonnoir(resultat: ResultatMarche) -> go.Figure:
    """Entonnoir TAM -> SAM -> SOM."""
    figure = go.Figure(
        go.Funnel(
            y=["TAM<br><i>marché total</i>",
               "SAM<br><i>marché accessible</i>",
               "SOM<br><i>captable à 3 ans</i>"],
            x=[resultat.tam, resultat.sam, resultat.som],
            textposition="inside",
            textinfo="value+percent initial",
            texttemplate="%{value:,.0f} FCFA<br>%{percentInitial:.2%} du TAM",
            marker=dict(
                color=["#00441B", "#41AB5D", "#FDEF42"],
                line=dict(width=2, color="white"),
            ),
            connector=dict(line=dict(color="#CCCCCC", width=1)),
            hovertemplate="<b>%{y}</b><br>%{x:,.0f} FCFA<extra></extra>",
        )
    )
    figure.update_layout(
        title=f"Entonnoir de marché — {resultat.libelle}",
        height=430,
        **_MISE_EN_PAGE,
    )
    return figure


def graphique_secteurs(comparaison: pd.DataFrame) -> go.Figure:
    """Comparaison TAM / SAM / SOM des trois secteurs."""
    figure = go.Figure()
    couleurs = {"TAM (FCFA)": "#00441B", "SAM (FCFA)": "#41AB5D",
                "SOM (FCFA)": "#FDEF42"}

    for colonne, couleur in couleurs.items():
        figure.add_trace(
            go.Bar(
                name=colonne.replace(" (FCFA)", ""),
                x=comparaison["Secteur"],
                y=comparaison[colonne],
                marker_color=couleur,
                marker_line=dict(color="rgba(0,0,0,0.15)", width=1),
                hovertemplate="<b>%{x}</b><br>%{y:,.0f} FCFA<extra></extra>",
            )
        )

    figure.update_layout(
        title="Comparaison des trois secteurs sur le périmètre retenu",
        barmode="group",
        yaxis_title="FCFA par an",
        yaxis_type="log",
        height=460,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        **_MISE_EN_PAGE,
    )
    figure.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.06)")
    return figure


def graphique_structure(potentiel: pd.DataFrame) -> go.Figure:
    """
    Nuage de points : population cible (volume) contre depense par tete
    (intensite). Fait apparaitre les marches de volume et les marches de valeur.
    """
    df = potentiel.copy()
    figure = px.scatter(
        df,
        x="population_cible",
        y="depense_cible_tete",
        size="tam_region",
        color="score_potentiel",
        text="region_affichage",
        color_continuous_scale=[[0, "#C7E9C0"], [0.5, "#41AB5D"], [1, "#00441B"]],
        size_max=60,
        labels={
            "population_cible": "Population cible (habitants)",
            "depense_cible_tete": "Dépense annuelle par tête sur le poste (FCFA)",
            "score_potentiel": "Score",
        },
    )
    figure.update_traces(
        textposition="top center",
        textfont=dict(size=10),
        hovertemplate=(
            "<b>%{text}</b><br>Population cible : %{x:,.0f}<br>"
            "Dépense/tête : %{y:,.0f} FCFA<extra></extra>"
        ),
    )
    figure.update_layout(
        title="Volume contre valeur : structure du marché par région",
        height=520,
        **_MISE_EN_PAGE,
    )
    figure.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.06)")
    figure.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.06)")
    return figure


def graphique_comparaison_territoires(
    ligne_a: pd.Series, ligne_b: pd.Series,
    libelle_a: str, libelle_b: str, titre_secteur: str,
) -> go.Figure:
    """
    Barres groupees horizontales comparant deux territoires sur plusieurs
    indicateurs d'unites differentes (habitants, FCFA, score). Chaque
    indicateur est normalise a 100 = la valeur la plus elevee des deux
    territoires, pour rendre les echelles comparables sur un meme graphique.
    """
    indicateurs = [
        ("Population", "population", config.formater_nombre),
        ("TAM", "tam_region", config.formater_fcfa),
        ("TAM / habitant", "tam_par_habitant", config.formater_fcfa),
        ("Score de potentiel", "score_potentiel", lambda v: f"{v:.1f} / 100"),
    ]
    noms, valeurs_a, valeurs_b, texte_a, texte_b = [], [], [], [], []
    for label, cle, fmt in indicateurs:
        va = float(ligne_a[cle])
        vb = float(ligne_b[cle])
        maxi = max(va, vb) or 1.0
        noms.append(label)
        valeurs_a.append(100 * va / maxi)
        valeurs_b.append(100 * vb / maxi)
        texte_a.append(fmt(va))
        texte_b.append(fmt(vb))

    figure = go.Figure()
    figure.add_trace(go.Bar(
        name=libelle_a, y=noms, x=valeurs_a, orientation="h",
        marker_color="#00853F", text=texte_a, textposition="outside",
        hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
    ))
    figure.add_trace(go.Bar(
        name=libelle_b, y=noms, x=valeurs_b, orientation="h",
        marker_color="#E8A33D", text=texte_b, textposition="outside",
        hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
    ))
    figure.update_layout(
        title=f"{libelle_a} contre {libelle_b} — {titre_secteur}",
        barmode="group",
        xaxis_title="Indice relatif (100 = valeur la plus élevée des deux territoires)",
        height=380,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        **_MISE_EN_PAGE,
    )
    figure.update_xaxes(range=[0, 118], showgrid=True, gridcolor="rgba(0,0,0,0.06)")
    return figure


def graphique_production(production: pd.DataFrame) -> go.Figure:
    """Barres empilees de la production agricole par region et par culture."""
    cultures = {
        "arachide_t": "Arachide",
        "mil_sorgho_t": "Mil / sorgho",
        "riz_paddy_t": "Riz paddy",
        "mais_t": "Maïs",
        "horticulture_t": "Horticulture",
    }
    df = production.copy()
    df["region_affichage"] = df["region"].map(
        lambda r: config.REGIONS_AFFICHAGE.get(r, r))
    df = df.sort_values("production_totale_t", ascending=True)

    figure = go.Figure()
    palette = ["#00441B", "#238B45", "#41AB5D", "#74C476", "#A1D99B"]
    for (colonne, libelle), couleur in zip(cultures.items(), palette):
        if colonne not in df.columns:
            continue
        figure.add_trace(
            go.Bar(
                name=libelle,
                y=df["region_affichage"],
                x=df[colonne],
                orientation="h",
                marker_color=couleur,
                hovertemplate=f"<b>%{{y}}</b><br>{libelle} : "
                              "%{x:,.0f} t<extra></extra>",
            )
        )

    figure.update_layout(
        title="Production agricole par région et par culture (tonnes)",
        barmode="stack",
        xaxis_title="Production (tonnes)",
        height=max(420, 32 * len(df)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        **_MISE_EN_PAGE,
    )
    figure.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.06)")
    return figure
