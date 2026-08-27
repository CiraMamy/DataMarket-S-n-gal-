# DataMarket Sénégal

Plateforme d'intelligence économique qui transforme les données statistiques
publiques de l'ANSD en études de marché chiffrées pour les entrepreneurs
sénégalais.

Un entrepreneur tape *« Je veux ouvrir une supérette à Mbour »* et obtient un
TAM, un SAM, un SOM, une carte du potentiel des 14 régions et un rapport PDF
exportable.

---

## Démarrage

```bash
pip install -r requirements.txt
streamlit run app.py
```

L'application démarre immédiatement : elle est livrée avec une couche de
données de référence calibrée sur les agrégats officiels. Aucun fichier
externe n'est requis, aucune clé API n'est obligatoire.

### Activer l'IA (optionnel)

Créez `.streamlit/secrets.toml` :

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

Sans clé, le module 3 bascule automatiquement sur un analyseur local
(lexiques + expressions régulières) : moins souple sur les formulations
libres, mais entièrement fonctionnel et gratuit.

---

## Les quatre modules

### Module 1 — Pipeline de données (`pipeline.py`)

Deux couches superposées :

| Couche | Source | Rôle |
|---|---|---|
| Référence | `ref_*.csv` livrés | Permet à l'app de tourner tout de suite |
| Utilisateur | `data/raw/*.csv` | **Écrase** la référence, région par région |

Déposez n'importe quel export ANSD dans `data/raw/` : le pipeline
auto-détecte son schéma par les noms de colonnes et l'intègre. Il tolère les
accents, la casse, les séparateurs `,` `;` `tab`, les encodages UTF-8 et
latin-1, les espaces insécables dans les nombres, la virgule décimale
française, une trentaine d'alias de colonnes, et agrège automatiquement des
données départementales au niveau régional.

Les lignes d'agrégat (`Sénégal`, `Total`, `Ensemble`) sont écartées.

Sortie : trois DataFrames Pandas indexés sur les 14 régions, plus un journal
de traçabilité consultable dans la barre latérale.

### Module 2 — Calculateur TAM/SAM/SOM (`market.py`)

```
TAM = population cible × dépense annuelle par tête sur le poste adressé
SAM = TAM × part géographique (zone de chalandise réelle)
SOM = SAM × part de marché visée × coefficient budgétaire
```

Trois secteurs modélisés, chacun avec sa propre logique de segmentation :

| Secteur | Population cible | Poste de dépense |
|---|---|---|
| **Commerce de proximité** | Toute la population, pondérée par un taux de captation du commerce organisé (55 % urbain / 30 % rural) | Alimentation + 12 % hygiène/entretien |
| **Restauration santé/diabète** | Adultes urbains de 25 ans et plus, touchés par le diabète (3,4 %) ou le prédiabète (8,0 %), solvables (45 %) | 16 % du budget alimentaire urbain |
| **Agrobusiness** | Demande interne en produits transformés, **bornée** par le gisement de matière première régionale non encore transformée | 30 % du budget alimentaire |

Chaque résultat expose son dictionnaire `hypotheses` complet : aucun chiffre
n'est une boîte noire.

`potentiel_par_region()` produit le score qui alimente la carte : 70 % volume
de marché, 30 % intensité par habitant.

### Module 3 — Interface conversationnelle (`nlp_agent.py`)

```python
intention, resultat = interroger(jeu, "Je veux ouvrir une supérette à Mbour")
```

Deux moteurs, avec bascule automatique :

1. **API Claude** — comprend les formulations libres, mappe les villes vers
   leur région, extrait les montants. Sortie JSON strictement validée et
   bornée côté Python : une valeur aberrante renvoyée par le modèle est
   corrigée, jamais propagée.
2. **Analyseur local** — ~150 mots-clés sectoriels, ~120 villes sénégalaises,
   extraction de budget (`15 millions`, `2,5 millions`, `500 mille`,
   `quinze millions`, `8 000 000 FCFA`).

`redaction_synthese()` fait commenter les chiffres par Claude — le modèle
commente, il ne recalcule rien. Sans clé API, `synthese_locale()` produit une
synthèse factuelle équivalente.

### Module 4 — Dashboard et export (`dashboard.py`, `geo.py`, `report.py`)

- **Carte choroplèthe** Leaflet des 14 régions colorées par potentiel, avec
  infobulles. Stratégie à trois niveaux : cache local → téléchargement
  geoBoundaries → repli en pastilles proportionnelles. Le niveau atteint est
  affiché honnêtement à l'utilisateur.
- **Graphiques Plotly** : barres TAM par région, entonnoir TAM→SAM→SOM,
  comparaison sectorielle, nuage volume/valeur, production agricole empilée.
- **Rapport PDF** de 4 pages via ReportLab : synthèse chiffrée, détail
  régional, méthodologie et hypothèses, sources et limites. Graphiques
  redessinés en vectoriel — pas de dépendance à un navigateur headless.

---

## Fichiers

```
app.py                  Application Streamlit
config.py               Référentiel 14 régions, secteurs, constantes
pipeline.py             MODULE 1
market.py               MODULE 2
nlp_agent.py            MODULE 3
dashboard.py            MODULE 4 — visualisations
geo.py                  MODULE 4 — frontières régionales
report.py               MODULE 4 — export PDF
test_datamarket.py      ~90 tests de validation
ref_population.csv      Données de référence — RGPH-5
ref_depenses.csv        Données de référence — EHCVM II
ref_production.csv      Données de référence — EAA
data/raw/               ← déposez vos exports ANSD ici
data/geo/               Cache GeoJSON
exports/                Rapports PDF générés
```

Chaque module est exécutable seul pour inspection :

```bash
python pipeline.py      # contrôle qualité + tableaux normalisés
python market.py        # comparaison des 3 secteurs + cas Mbour
python nlp_agent.py     # 5 phrases de test analysées
python geo.py           # état de la couche géographique
python report.py        # génère un PDF de démonstration
```

---

## Tests

```bash
pytest -v test_datamarket.py
```

Couvre notamment :

- le total des 14 régions retombe sur les 18 126 390 habitants du RGPH-5 ;
- la densité calculée de Dakar retombe sur les 7 277 hab/km² publiés ;
- la dépense moyenne pondérée retombe sur les 542 706 FCFA de l'EHCVM II ;
- les coefficients budgétaires somment à 100 % dans chaque région ;
- `TAM ≥ SAM ≥ SOM` et additivité géographique `TAM(A) + TAM(B) = TAM(A∪B)` ;
- le TAM ne dépasse jamais la dépense totale des ménages ;
- 9 formulations sectorielles, 7 villes, 6 formats de budget ;
- génération PDF pour les 3 secteurs ;
- robustesse : phrase vide, texte absurde, CSV illisible, région inexistante.

---

## Mode hors-ligne

Le calculateur TAM/SAM/SOM (modules 1 et 2) ne fait **aucun appel réseau** :
`ref_*.csv` est lu depuis le disque, sans dépendance externe. Vérifié en
simulant une coupure réseau totale (requêtes HTTP interceptées) :
l'application démarre et produit une étude complète sans exception.

Seule la carte (module 4) sollicite le réseau, à la marge, pour télécharger
les frontières régionales au premier lancement. Sa stratégie à trois niveaux
— cache local → téléchargement geoBoundaries → repli en pastilles
proportionnelles — a elle aussi été vérifiée hors-ligne : sans cache ni
réseau, l'application reste pleinement fonctionnelle, avec une carte
dégradée mais honnête sur son état (message affiché à l'utilisateur).

---

## Langue (FR/EN)

Sélecteur 🌐 en haut de la barre latérale. Le choix est encodé dans l'URL
(`?lang=en`), donc un lien partagé conserve la langue de celui qui l'a généré.

Couvert : l'intégralité de l'interface Streamlit (`app.py`), les libellés et
descriptions des trois secteurs (`config.SECTEURS`), les titres et légendes
des graphiques (`dashboard.py`), et la synthèse factuelle générée localement
(`nlp_agent.synthese_locale`). Vérifié via `streamlit.testing.v1.AppTest`
dans les deux langues : sélecteur, permalien, études de cas, tous les
onglets et tous les expanders (Impact & méthode, Sensibilité, Décision),
aucune exception.

**Limite assumée** : le commentaire généré par l'API Claude
(`nlp_agent.redaction_synthese`) reste en français quelle que soit la langue
choisie — le module bascule de toute façon sur la synthèse locale dès que
« Forcer l'analyse locale » est actif (comportement par défaut sans clé
API). Le rapport PDF (`report.py`) reste également en français uniquement.

---

## Sources et statut des données

| Source | Usage | Millésime |
|---|---|---|
| [RGPH-5, ANSD](https://www.ansd.sn/rapports/rgph-5-2023) | Population, urbanisation, ménages | 2023 |
| [EHCVM II, ANSD](https://www.ansd.sn/sites/default/files/2024-07/Rapport_Final_EHCVM_2021-2022_VF_0.pdf) | Dépense par tête, coefficients budgétaires | 2021-2022 |
| EAA / DAPSA | Production agricole régionale | Campagne de référence |

**Agrégats nationaux officiels** utilisés comme points d'ancrage :
population résidente **18 126 390** habitants ; dépense de consommation
annuelle par tête **542 706 FCFA** ; taux d'urbanisation **54,7 %** ;
concentration Dakar 22 % / Thiès 13 % / Diourbel 12 %.

> **Important — statut de la ventilation régionale.** Les totaux nationaux
> ci-dessus sont officiels. La ventilation région par région livrée dans les
> fichiers `ref_*.csv` est **dérivée** des parts publiées et calibrée sur les
> densités officielles (la densité reconstituée de Dakar, Diourbel, Thiès,
> Kaolack, Fatick, Tambacounda et Kédougou retombe à moins de 5 % des valeurs
> ANSD, ce qui valide la méthode). Elle reste une approximation : remplacez-la
> par vos propres exports ANSD dès que possible en les déposant dans
> `data/raw/`.

Les coefficients sectoriels (taux de captation, prévalence du diabète, part
de la restauration hors domicile, prix moyen à la tonne) sont des hypothèses
de modélisation explicites, toutes regroupées dans `config.SECTEURS` et
toutes affichées dans l'application et dans le rapport PDF. Ce sont les
premiers paramètres à ajuster avec vos observations terrain.

---

## Limites

Cet outil est un instrument de **cadrage**, pas une étude de faisabilité.

- Les dépenses par tête sont des moyennes régionales : elles masquent des
  écarts de revenu importants à l'intérieur d'une même région.
- Le SOM ne modélise pas la concurrence à l'échelle de la rue, qui est le
  premier déterminant du chiffre d'affaires réel d'un commerce de proximité.
- Les données EHCVM datent de 2021-2022 : les montants sont exprimés en
  francs courants de la période d'enquête, hors inflation ultérieure.
- La prévalence du diabète retenue (3,4 %) est une estimation nationale ;
  elle varie fortement entre milieu urbain et rural.

---

## Pistes d'extension

1. **Descendre au département** (46 départements) plutôt qu'à la région —
   c'est la maille qui compte pour un commerce de proximité, et le RGPH-5 la
   publie.
2. **Ajouter la densité concurrentielle** via OpenStreetMap (nombre de
   commerces existants par km²) pour transformer le SOM en estimation
   défendable.
3. **Injecter l'IHPC** (indice harmonisé des prix, base 2023) pour
   réactualiser les montants EHCVM en francs constants.
4. **Historiser les études** dans SQLite pour suivre l'évolution des marchés
   et permettre aux utilisateurs de retrouver leurs analyses.
