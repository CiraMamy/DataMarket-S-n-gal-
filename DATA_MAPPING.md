# DATA_MAPPING.md

**DataMarket Sénégal — Cartographie question entrepreneuriale → donnée → calcul**
Version 1.0 — 4 août 2026 — Hackathon ANSD 2026

Document complémentaire de `DATA_INVENTORY.md`. À valider conjointement
avant le début du développement (§52 du cahier des charges).

---

## 0. Grille de traçabilité

Conformément au §9, chaque valeur manipulée par DataMarket porte un
classement obligatoire. Ces étiquettes doivent apparaître **dans la base**,
**dans l'API** et **dans l'interface** — pas seulement dans cette
documentation.

| Étiquette | Signification | Rendu interface |
|---|---|---|
| `OBS` | **Donnée observée** — lue telle quelle dans une publication officielle | Fond blanc, source cliquable |
| `CALC` | **Indicateur calculé** — dérivé par opération sur des `OBS` | Fond blanc, formule dépliable |
| `EST` | **Estimation** — produite par une méthode statistique ou une transposition | **Fond ambré**, méthode affichée |
| `PROJ` | **Projection** — valeur estimée dans le futur | **Fond ambré**, horizon affiché |
| `HYP` | **Hypothèse utilisateur** — saisie ou modifiable par l'entrepreneur | **Fond bleu**, champ éditable |
| `EXT` | **Donnée externe** — hors ANSD | **Bordure grise**, producteur affiché |
| `N/D` | **Donnée non disponible** | Texte grisé : « Donnée non disponible dans les sources intégrées » |

**Règle de propagation.** Le classement d'un calcul est celui de son intrant
le plus faible, dans l'ordre `OBS` < `CALC` < `EST` < `PROJ` < `HYP`. Un TAM
qui combine une population `OBS` et une hypothèse de captation `HYP` est
classé `HYP` — jamais `OBS`.

---

## 1. Vue d'ensemble : les 10 questions du §2

| # | Question entrepreneuriale | Indicateur | Dataset | Faisabilité |
|---|---|---|---|---|
| Q1 | Combien de clients potentiels ? | Population cible du segment | D01, D02 | ✅ Complète |
| Q2 | Où sont-ils ? | Population par commune / village | D01 | ✅ Complète |
| Q3 | Quelle région a le meilleur potentiel ? | Opportunity Score | D01, D02, D04, D06 | ✅ Complète |
| Q4 | Quel profil démographique ? | Structure par âge et sexe | D02 | ⚠️ Région seulement |
| Q5 | Quel niveau de consommation ? | Dépense annuelle par tête | D04 | ⚠️ Région seulement |
| Q6 | Quel contexte économique ? | Pauvreté, emploi, tissu productif | D04, D06 | ✅ Complète |
| Q7 | Quel niveau de concurrence ? | Densité d'unités économiques | D08, D12 | ⛔ **Dégradée** |
| Q8 | Quelles données justifient l'hypothèse ? | Chaîne de traçabilité complète | Toutes | ✅ Complète |
| Q9 | Quelle différence entre deux régions ? | Comparateur territorial | D01, D02, D04, D06 | ✅ Complète |
| Q10 | Quelles hypothèses pour la taille de marché ? | Panneau d'hypothèses TAM/SAM/SOM | — | ✅ Complète |

**Lecture.** Huit questions sur dix sont traitables sur sources libres
vérifiées. Q4 et Q5 sont bloquées au niveau régional par l'absence de
microdonnées (D05 sous autorisation). Q7 est la seule réellement dégradée :
elle repose sur un recensement d'entreprises de 2016.

---

## 2. Cas d'usage principal — supérette à Mbour

> **Question posée :** « Je souhaite ouvrir une supérette à Mbour. Quel est le
> potentiel du marché ? »

### 2.1 Décomposition de l'intention

| Élément extrait | Valeur | Méthode | Classement |
|---|---|---|---|
| Type de projet | Commerce | LLM + lexique de repli | `CALC` |
| Secteur | Commerce de détail alimentaire | LLM + lexique | `CALC` |
| Territoire | Département de Mbour, région de Thiès | Référentiel territorial (D01, D11) | `CALC` |
| Budget | Saisi par l'utilisateur | Extraction ou formulaire | `HYP` |

> **Point d'attention.** « Mbour » désigne **trois entités distinctes** : la
> commune de Mbour, le département de Mbour, et l'arrondissement. Le
> référentiel territorial doit lever l'ambiguïté et **demander confirmation à
> l'utilisateur** plutôt que de choisir silencieusement. C'est exactement le
> genre de raccourci qui ruine la crédibilité d'un chiffre.

### 2.2 Chaîne de données

```
Question
   ↓
Référentiel territorial ────── D01 + D11 ─────→ code territoire
   ↓
Population              ────── D01 + D02 ─────→ effectif          [OBS]
Ménages                 ────── D01       ─────→ nombre            [OBS]
Structure par âge       ────── D02       ─────→ pyramide région   [OBS]
Consommation par tête   ────── D04       ─────→ FCFA/an région    [OBS]
Pauvreté                ────── D04       ─────→ % région          [OBS]
Tissu économique        ────── D06       ─────→ SES Thiès         [OBS]
Concurrence structurelle────── D08       ─────→ RGE 2016          [OBS obsolète]
Concurrence observable  ────── D12       ─────→ OSM               [EXT]
   ↓
Market Size Engine      ────── TAM / SAM / SOM                    [HYP]
Opportunity Engine      ────── Score composite                    [CALC]
   ↓
Étude de marché
```

### 2.3 Valeurs disponibles à ce jour

| Indicateur | Valeur | Source | Classement | Statut |
|---|---|---|---|---|
| Population du département de Mbour | **937 189** hab. | RGPH-5 2023 (D02/D03) | `OBS` | ✅ Vérifiée |
| Rang national du département | 3ᵉ | RGPH-5 2023 | `OBS` | ✅ Vérifiée |
| Population région de Thiès | ≈ 13 % du national | RGPH-5 2023 (D03) | `OBS` | ✅ Vérifiée |
| Densité région de Thiès | **375** hab/km² | RGPH-5 2023 (D03) | `OBS` | ✅ Vérifiée |
| Taux de pauvreté Thiès | **29,9 %** | EHCVM II (D04) | `OBS` | ✅ Vérifiée |
| Dépense annuelle par tête (national) | **542 706** FCFA | EHCVM II (D04) | `OBS` | ✅ Vérifiée |
| Dépense annuelle par tête (Thiès) | — | EHCVM II (D04) | `OBS` | ⬜ **À extraire du rapport** |
| Coefficients budgétaires Thiès | — | EHCVM II (D04) | `OBS` | ⬜ **À extraire du rapport** |
| Ménages du département de Mbour | — | Répertoire (D01) | `OBS` | ⬜ **À extraire** |
| Population par commune de Mbour | — | Répertoire (D01) | `OBS` | ⬜ **À extraire** |
| Unités économiques Thiès (2016) | **11,5 %** du total national | RGE 2016 (D08) | `OBS` | ⚠️ Obsolète |
| Commerces cartographiés à Mbour | — | OSM (D12) | `EXT` | ⬜ **À requêter** |

---

## 3. Fiches de mapping par indicateur

### M01 — Population cible

| Champ | Contenu |
|---|---|
| **Question** | Combien de clients potentiels ? |
| **Indicateur** | Population résidente du territoire, éventuellement segmentée |
| **Dataset** | D01 (commune/village) ou D02 (région/département) |
| **Variables** | `population_totale`, `population_par_groupe_age`, `population_par_sexe` |
| **Méthode** | Lecture directe. Pour un segment : `population × part_du_segment` |
| **Classement** | `OBS` si population totale ; `CALC` si segmentée sur une part `OBS` ; `EST` si la part vient d'une transposition régionale |
| **Niveau atteignable** | Village (D01), département (D02) |
| **Limites** | La structure par âge n'est publiée qu'au niveau régional. Segmenter Mbour sur la pyramide de Thiès est une **transposition** : classer `EST` et l'afficher. |
| **Message si indisponible** | « Structure par âge non disponible au niveau départemental. La segmentation utilise la pyramide régionale de Thiès, appliquée par hypothèse au département de Mbour. » |

---

### M02 — Ménages

| Champ | Contenu |
|---|---|
| **Question** | Combien de foyers, quelle taille ? |
| **Indicateur** | Nombre de ménages, taille moyenne |
| **Dataset** | D01 (**publie directement le nombre de ménages et de concessions**) |
| **Variables** | `nb_menages`, `nb_concessions`, `taille_moyenne_menage` |
| **Méthode** | Lecture directe depuis le Répertoire des localités |
| **Classement** | `OBS` |
| **Fallback** | Si D01 n'expose pas le champ : `nb_menages = population / taille_moyenne_régionale` → classer `CALC`, afficher la formule |
| **Limites** | La taille moyenne nationale est de 9 personnes, mais varie de 6 (Dakar) à 12 (Tambacounda, Sédhiou, Matam, Kaolack, Kaffrine). **Ne jamais appliquer la moyenne nationale à un territoire précis.** |

---

### M03 — Consommation

| Champ | Contenu |
|---|---|
| **Question** | Quel est le niveau de consommation ? |
| **Indicateur** | Dépense de consommation annuelle par tête, coefficients budgétaires |
| **Dataset** | D04 (EHCVM II) |
| **Variables** | `depense_annuelle_tete`, `coefficient_budgetaire_{poste}` |
| **Niveau publié** | **Région et milieu (urbain/rural) uniquement** |
| **Méthode pour un département** | Transposition de la valeur régionale, éventuellement pondérée par le taux d'urbanisation local |
| **Classement** | `OBS` au niveau régional ; **`EST` dès qu'on descend au département** |
| **Formule de transposition** | `dépense_Mbour = dépense_Thiès × (1 + δ)` où `δ` est un ajustement d'urbanisation, par défaut `δ = 0` |
| **Limites majeures** | 1. **Millésime 2021-2022 en francs courants.** Un TAM 2026 calculé sur ces montants est sous-évalué de l'inflation cumulée. **Correctif obligatoire :** redresser par l'IHPC base 2023 (D10) et afficher les deux valeurs. 2. La transposition région → département suppose que Mbour consomme comme la moyenne de Thiès, ce qui est discutable pour une zone touristique littorale. |
| **Message obligatoire** | « Dépense de consommation issue de l'EHCVM II 2021-2022 au niveau de la région de Thiès, transposée au département de Mbour. Montants en francs courants 2021-2022. » |

---

### M04 — Pouvoir d'achat

| Champ | Contenu |
|---|---|
| **Indicateur** | Taux de pauvreté monétaire, indice de pouvoir d'achat |
| **Dataset** | D04 |
| **Valeurs vérifiées** | National 37,5 % ; Dakar 9,3 % ; Thiès 29,9 % ; Saint-Louis 37,3 % ; Diourbel 37,4 % ; Kolda 62,5 % ; Tambacounda 62,8 % ; Sédhiou 64,4 % ; Kédougou 65,7 % ; urbain 20,0 % ; rural 53,3 % |
| **Méthode du score** | `PurchasingPowerScore = 100 × (1 − taux_pauvreté_normalisé)` en min-max sur les 14 régions |
| **Classement** | `OBS` pour le taux ; `CALC` pour le score |
| **Limites** | Cinq régions manquent encore à la liste vérifiée (Louga, Fatick, Matam, Kaffrine, Ziguinchor) — **à extraire du rapport D04 Jour 1**. Le taux de pauvreté est un indicateur de **privation**, pas de pouvoir d'achat disponible : deux territoires à pauvreté égale peuvent avoir des classes moyennes très différentes. |

---

### M05 — Concurrence ⛔ indicateur le plus fragile

| Champ | Contenu |
|---|---|
| **Question** | Quel est le niveau de concurrence ? |
| **Indicateur** | Market Saturation Score (§19) |
| **Dataset** | D08 (RGE 2016) et D12 (OSM) |
| **Formule §19** | `Saturation = nb_entreprises_secteur / population_cible` |
| **Problème méthodologique** | Le numérateur date de 2016, le dénominateur de 2023. **Le ratio est faux par construction.** |
| **Correctif imposé** | Calculer le ratio **entièrement en base 2016** (numérateur RGE 2016, dénominateur population 2016 projetée depuis le RGPH-4 2013), puis le présenter comme **structure historique**, jamais comme concurrence actuelle. |
| **Classement** | `OBS` pour le comptage 2016 ; `EST` pour le dénominateur projeté ; donc **`EST` pour le ratio** |
| **Complément OSM** | Comptage `shop=convenience`, `shop=supermarket`, `shop=grocery` dans un rayon paramétrable. Classement `EXT`. |
| **Piège à désamorcer explicitement** | Un faible comptage OSM peut signifier une faible concurrence **ou** une faible couverture cartographique. Ces deux causes sont indiscernables dans la donnée. **L'interface doit le dire à chaque affichage**, sans exception. |
| **Message obligatoire** | « Le dernier recensement des entreprises disponible date de 2016. Aucune source publique ne permet de mesurer la concurrence actuelle à Mbour. Le comptage OpenStreetMap est indicatif et dépend de la densité de contribution cartographique locale. Une visite terrain reste indispensable. » |
| **Recommandation produit** | Ne **pas** afficher de « score de concurrence » en chiffre unique. Afficher les deux comptages bruts avec leur date et leur limite. Un chiffre agrégé donnerait une fausse impression de mesure. |

---

### M06 — Environnement économique local

| Champ | Contenu |
|---|---|
| **Dataset** | D06 (SES régionales, détail départemental) |
| **Variables** | Infrastructures, transport, marchés, établissements de santé et d'éducation, activités économiques dominantes |
| **Classement** | `OBS` |
| **Utilité** | Risk Engine (§16) et contexte du rapport. Seule source libre à ce niveau de détail. |
| **Limites** | Format PDF hétérogène d'une région à l'autre. Extraction semi-manuelle assumée pour le MVP : **14 PDF, extraction ciblée des seuls tableaux utiles**, pas de parseur générique. |

---

## 4. Market Size Engine — calcul étape par étape

Le §17 impose d'afficher le calcul étape par étape et de rendre les hypothèses
modifiables. Voici le déroulé complet pour le cas Mbour, tel qu'il doit
apparaître à l'écran.

### Étape 1 — Population cible

```
Population du département de Mbour ............ 937 189       [OBS]
   Source : ANSD, RGPH-5 2023
```

### Étape 2 — Restriction au segment

```
Population cible = population × part du segment

Part du segment ............................... 100 %         [HYP]
   Une supérette s'adresse à l'ensemble des ménages.

Population cible .............................. 937 189       [CALC]
```

### Étape 3 — Dépense adressable par tête

```
Dépense annuelle par tête, région de Thiès .... à extraire    [OBS]
   Source : ANSD, EHCVM II 2021-2022
   ⚠ Valeur régionale transposée au département   → classe EST

Coefficient budgétaire « alimentation » ....... à extraire    [OBS]
   Source : ANSD, EHCVM II 2021-2022

Élargissement au panier d'une supérette ....... +12 %         [HYP]
   Produits d'hygiène et d'entretien, non alimentaires.

Part captée par le commerce organisé .......... à définir     [HYP]
   Le reste passe par les marchés, les boutiques informelles
   et l'autoconsommation. Paramètre le plus sensible du modèle.

Dépense adressable par tête ................... à calculer    [HYP]
```

### Étape 4 — TAM

```
TAM = population cible × dépense adressable par tête          [HYP]
```

### Étape 5 — SAM

```
SAM = TAM × zone de chalandise

Zone de chalandise ............................ à définir     [HYP]
   Part de la population du département réellement
   atteignable depuis l'emplacement envisagé.
   À calibrer sur la population de la commune (D01),
   et non sur celle du département.
```

### Étape 6 — SOM

```
SOM = SAM × part de marché visée

Part de marché visée .......................... à définir     [HYP]
   Ambition à 3 ans, fonction du capital engagé
   et de la concurrence locale — non mesurable (voir M05).
```

### Règles d'affichage obligatoires

1. Chaque ligne porte son étiquette de classement.
2. Chaque ligne `HYP` est un champ éditable, avec sa valeur par défaut visible.
3. Chaque ligne `OBS` porte un lien vers la source (document, page).
4. Le résultat final est étiqueté `HYP`, **jamais** `OBS` — car il dépend
   d'hypothèses.
5. Une mention permanente accompagne le TAM : *« Estimation construite à
   partir de données officielles et d'hypothèses modifiables. Ce n'est pas une
   statistique publiée par l'ANSD. »*

> **Pourquoi les valeurs ci-dessus sont laissées vides.** Le §50 interdit
> d'inventer des chiffres. Les coefficients budgétaires de la région de Thiès
> n'ont pas encore été extraits du rapport EHCVM II, et les taux de captation
> du commerce organisé ne font l'objet d'aucune publication officielle. Ces
> cases seront remplies Jour 1, après passage de D04 en V3 — les taux de
> captation restant, eux, des hypothèses assumées et affichées comme telles.

---

## 5. Opportunity Score — composition

Conformément au §18, le score doit être transparent et ses poids affichés.

```
Score = w₁·Population + w₂·PouvoirAchat + w₃·Croissance
      + w₄·Consommation − w₅·Concurrence
```

| Composante | Source | Normalisation | Poids par défaut | Classement |
|---|---|---|---|---|
| Population | D01, D02 | Min-max sur 14 régions | **0,30** | `CALC` |
| Pouvoir d'achat | D04 (pauvreté inversée) | Min-max | **0,25** | `CALC` |
| Croissance démographique | D02, D03 | Min-max | **0,15** | `CALC` |
| Consommation | D04 | Min-max | **0,30** | `EST` |
| Concurrence | D08 + D12 | Min-max, **soustraite** | **0,00** | ⛔ **Désactivée** |

> **Décision assumée : le poids de la concurrence est fixé à zéro dans le MVP.**
> Intégrer une composante concurrence calculée sur un recensement de 2016 et
> un comptage OSM à couverture inégale reviendrait à donner une précision
> illusoire au score. Le curseur est présent dans l'interface, réglé à zéro par
> défaut, avec l'explication affichée. L'utilisateur peut l'activer en
> connaissance de cause.

**Formulation de sortie imposée (§47).** Jamais « Mbour est la meilleure
région », mais :

> « Sur la base des quatre indicateurs retenus et de leurs poids affichés,
> le département de Mbour obtient un score de X sur 100, supérieur à N des M
> territoires comparés. Ce résultat s'explique principalement par sa
> population et son niveau de consommation. Les données disponibles ne
> permettent pas d'évaluer le niveau de concurrence actuel ni le pouvoir
> d'achat au niveau infrarégional. »

---

## 6. Autres cas d'usage — mapping résumé

### 6.1 Restauration santé / diabète

| Besoin | Source | Statut |
|---|---|---|
| Population adulte urbaine | D01, D02 | ✅ `OBS` |
| Prévalence du diabète | D16 (EDS, accès restreint) | ⛔ **`HYP` faute de source accessible** |
| Dépense de restauration hors domicile | D04 | ⚠️ Poste à vérifier dans la nomenclature EHCVM |

> **Décision.** Tant que la prévalence n'est pas sourcée, ce secteur doit
> afficher un bandeau : *« La prévalence du diabète utilisée est une hypothèse
> de modélisation. Aucune source officielle accessible ne la documente au
> niveau régional. »* Une alternative crédible est de sourcer la prévalence
> auprès de l'OMS (Global Health Observatory), en la classant `EXT`.

### 6.2 Agrobusiness ⛔

| Besoin | Source | Statut |
|---|---|---|
| Production agricole par région | D13 | ⛔ **V0 — source non identifiée** |
| Demande en produits transformés | D04 | ✅ `OBS` |

> **Décision.** Ce secteur ne peut pas être démontré tant que D13 n'est pas
> vérifié. Deux options, à trancher Jour 1 : identifier une source DAPSA libre
> et récente, ou **retirer le secteur de la démonstration**. Le maintenir avec
> des chiffres construits serait une violation directe du §50.

---

## 7. Ce que DataMarket doit répondre quand la donnée manque

Le §25 impose une formulation stricte. Voici les messages types à implémenter
comme constantes, et non à laisser à l'improvisation du LLM.

| Situation | Message |
|---|---|
| Indicateur absent des sources | « Donnée non disponible dans les sources intégrées. » |
| Donnée existante mais à un niveau plus agrégé | « Cette donnée n'est publiée qu'au niveau {niveau}. La valeur affichée pour {territoire} est une transposition, signalée comme estimation. » |
| Donnée existante mais sous autorisation | « Cette information figure dans les microdonnées {enquête}, dont l'accès est soumis à autorisation de l'ANSD. DataMarket n'y a pas accès. » |
| Donnée trop ancienne | « La source la plus récente disponible date de {année}. Cette valeur ne reflète pas nécessairement la situation actuelle. » |
| Aucune source, même externe | « Cette information n'est pas couverte par les sources statistiques publiques. Elle nécessiterait une enquête terrain. » |

---

## 8. Modèle de données — tables prioritaires MVP

Le §15 liste 20 tables. Pour un MVP de 72 heures, seules 8 sont nécessaires :

| Table | Alimentée par | Grain | Priorité |
|---|---|---|---|
| `territories` | D01, D11 | Village → région | **1** |
| `population` | D01, D02 | Territoire × année | **2** |
| `households` | D01 | Territoire × année | **3** |
| `consumption` | D04 | Région × poste | **4** |
| `poverty` | D04 | Région × année | **5** |
| `enterprises` | D08, D12 | Territoire × secteur × année | **6** |
| `sources` | Toutes | Dataset | **7** |
| `indicators` | Calculs | Territoire × indicateur | **8** |

**Colonnes obligatoires sur `indicators`** — sans elles, la traçabilité du §26
est impossible :

```sql
value              NUMERIC
classification     TEXT      -- OBS | CALC | EST | PROJ | HYP | EXT
source_id          INTEGER   -- FK vers sources
source_page        TEXT      -- « Chapitre 1, page 24 »
reference_year     INTEGER
computation        TEXT      -- formule lisible si CALC/EST
assumptions        JSONB     -- hypothèses si HYP
confidence         TEXT      -- élevée | moyenne | limitée
```

---

## 9. Data Confidence — règle de calcul (§33)

| Critère | Élevée | Moyenne | Limitée |
|---|---|---|---|
| Millésime de la source | ≤ 3 ans | 4 à 7 ans | > 7 ans |
| Niveau géographique | Correspond exactement | Un niveau au-dessus | Deux niveaux ou plus |
| Classement | `OBS` ou `CALC` | `EST` | `HYP` ou `PROJ` |
| Nombre d'hypothèses | 0 | 1 à 2 | ≥ 3 |

**Le niveau retenu est le plus faible des quatre critères.**

Application au TAM de Mbour : millésime EHCVM 2021-2022 (4 ans → moyenne),
niveau région transposé au département (un niveau → moyenne), classement `HYP`
(→ limitée), au moins 3 hypothèses (→ limitée). **Confiance : limitée.**

> C'est un résultat inconfortable, et c'est précisément pour cela qu'il faut
> l'afficher. Un TAM en confiance limitée, assumé et expliqué, vaut mieux
> qu'un TAM présenté comme une certitude. C'est aussi ce qui différencie
> DataMarket d'un générateur de business plans.

---

## 10. Validation

| Étape | Statut |
|---|---|
| Mapping des 10 questions du §2 | ✅ |
| Cas d'usage Mbour détaillé | ✅ |
| Chaîne de calcul TAM/SAM/SOM explicitée | ✅ |
| Composition de l'Opportunity Score arrêtée | ✅ |
| Messages d'indisponibilité normalisés | ✅ |
| **Extraction des valeurs EHCVM régionales** | ⬜ **Jour 1** |
| **Test d'export du Répertoire des localités** | ⬜ **Jour 1** |
| **Décision sur le secteur agrobusiness** | ⬜ **Jour 1** |
| Validation par l'équipe | ⬜ |

---

## 11. Trois arbitrages à valider avant de coder

1. **Le poids de la concurrence dans l'Opportunity Score est fixé à zéro.**
   Justifié par l'ancienneté du RGE. Si l'équipe préfère l'activer, il faut
   assumer un score bâti sur une donnée de 2016.

2. **Le secteur agrobusiness est suspendu** tant que la source de production
   agricole n'est pas identifiée. Alternative : le remplacer par un troisième
   secteur mieux documenté — le commerce de détail non alimentaire, par
   exemple, couvert par le RGE et l'EHCVM.

3. **Les montants EHCVM doivent-ils être redressés par l'IHPC ?** Redresser
   donne un TAM plus réaliste en 2026 mais ajoute une couche d'estimation. Ne
   pas redresser donne un TAM sous-évalué mais entièrement traçable. **La
   recommandation est d'afficher les deux**, avec le montant en francs
   courants comme valeur de référence et le montant redressé en valeur
   indicative.
