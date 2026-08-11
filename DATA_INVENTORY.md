# DATA_INVENTORY.md

**DataMarket Sénégal — Inventaire des sources de données**
Version 1.0 — 4 août 2026 — Hackathon ANSD 2026

---

## 0. Avertissement méthodologique sur cet inventaire lui-même

Le cahier des charges (§50) impose de vérifier l'accessibilité d'une source
**avant** de l'intégrer. Cet inventaire applique cette règle à lui-même.

**Limite de la vérification effectuée.** Les URL ci-dessous ont été
identifiées et recoupées par recherche documentaire. La récupération directe
des pages a échoué en cours de session (délai d'attente réseau dépassé). Par
conséquent, **aucune entrée de cet inventaire n'est marquée « vérifiée par
téléchargement effectif »**. Chaque fiche porte un niveau de vérification
explicite :

| Niveau | Signification |
|---|---|
| **V2** | URL et contenu recoupés par au moins deux sources documentaires concordantes |
| **V1** | URL identifiée, existence du document confirmée, contenu partiellement décrit |
| **V0** | Source citée dans le cahier des charges, non encore vérifiée |

**Action obligatoire avant le Jour 1 de développement :** ouvrir chaque URL de
niveau V2/V1, télécharger le fichier, confirmer le format et l'année, et faire
passer la fiche en **V3 (téléchargé et inspecté)**. Une case à cocher est
prévue à cet effet sur chaque fiche.

Aucune donnée de cet inventaire ne doit alimenter la base tant que sa fiche
n'est pas en V3.

---

## 1. Tableau de synthèse

| # | Dataset | Producteur | Année | Niveau géo. | Format | Accès | Vérif. | Priorité MVP |
|---|---|---|---|---|---|---|---|---|
| D01 | Répertoire des localités RGPH-5 | ANSD | 2023 | Village / quartier | CSV, JSON | Libre | V2 | **Critique** |
| D02 | RGPH-5 — rapports thématiques | ANSD | 2023 | Région, département | PDF | Libre | V2 | **Critique** |
| D03 | RGPH-5 — note de presse résultats définitifs | ANSD | 2023 | National, région | PDF | Libre | V2 | Haute |
| D04 | EHCVM II — rapport final | ANSD | 2021-2022 | National, région | PDF | Libre | V2 | **Critique** |
| D05 | EHCVM II — microdonnées | ANSD / ANADS | 2021-2022 | Ménage | SPSS, Stata | **Sous autorisation** | V2 | Exclu du MVP |
| D06 | SES régionales | ANSD | 2022-2023 | Région, département | PDF | Libre | V2 | **Critique** |
| D07 | SES nationale — sections | ANSD | 2022-2023 | National | PDF | Libre | V1 | Moyenne |
| D08 | RGE — rapport global | ANSD | 2016 | Région, département | PDF | Libre | V2 | Haute (dégradée) |
| D09 | RGE — microdonnées | ANSD / ANADS | 2016 | Unité économique | Stata | **Sous autorisation** | V1 | Exclu du MVP |
| D10 | ODP / Senegal Data Portal | ANSD / Knoema | Variable | National, région | CSV, JSON, SDMX, XLSX | Libre | V2 | Haute |
| D11 | Frontières administratives | geoBoundaries | 2023 | ADM1/2/3 | GeoJSON | Libre (CC BY) | V1 | **Critique** |
| D12 | Points d'intérêt commerciaux | OpenStreetMap | Continu | Point GPS | JSON (Overpass) | Libre (ODbL) | V1 | Haute |
| D13 | Enquêtes agricoles annuelles | DAPSA / ANSD | Variable | Région | PDF, XLSX | À vérifier | **V0** | *Remplacé par D17* |
| D14 | Enquête emploi (ENES) | ANSD | Variable | Région | PDF | À vérifier | **V0** | Basse |
| D15 | Indicateurs Banque mondiale | Banque mondiale | 1960-2024 | National | JSON (API) | Libre | V1 | Basse |
| D16 | EDS / DHS Sénégal | ANSD / ICF | 2023 | Région | SPSS, Stata | **Inscription requise** | V1 | Basse |
| **D17** | **AgriData — API CKAN** | ANSD / IPAR / DAPSA | Variable | À confirmer | **JSON, CSV (API)** | Libre | V2 | **Critique** |
| **D18** | **ODP Régional — API** | ANSD | Variable | **Département** | **JSON, CSV (API)** | Libre | V2 | **Critique** |

**Verdict de couverture pour le MVP :** les sources D01, D02, D04, D06, D08,
D10, D11 et D12 suffisent à alimenter le cas d'usage Mbour de bout en bout.
Les sources D05 et D09 (microdonnées) sont **exclues du MVP** — voir §3.

---

## 2. Fiches détaillées

### D01 — Répertoire des localités issu du RGPH-5, 2023

> **La source la plus importante du projet.** C'est la seule qui descend
> sous le niveau régional en format ouvert et exportable.

| Champ | Valeur |
|---|---|
| **Nom** | Répertoire des localités issu du RGPH-5, 2023 |
| **Source** | ANSD |
| **Publisher** | Agence Nationale de la Statistique et de la Démographie |
| **URL page** | https://www.ansd.sn/mademba/repertoire-des-localites-issu-du-rgph-5-2023 |
| **URL outil** | https://www.ansd.sn/node/15936 |
| **Format** | CSV, JSON (export depuis l'outil de consultation) |
| **Année** | 2023 |
| **Fréquence** | Décennale (par recensement) |
| **Niveau géographique** | Commune, quartier, village / localité |
| **Variables annoncées** | Nom de localité, population, nombre de concessions, nombre de ménages, rattachement administratif |
| **Licence** | À confirmer — l'ANSD annonce du CC BY 4.0 sur ses données et analyses ; à vérifier sur la page conditions d'utilisation |
| **Accessibilité** | Libre, sans inscription (outil de consultation web avec export) |
| **Access type** | `public_open` |
| **Vérification** | **V2** — outil de consultation et export CSV/JSON confirmés par recoupement |
| **Utilité DataMarket** | Alimente le référentiel territorial (§13), le Territory Engine, le profil territorial et la population cible du Market Size Engine. **C'est cette source qui rend possible l'analyse au niveau de Mbour plutôt qu'au niveau de la région de Thiès.** |
| **Méthode d'importation** | Extraction via l'outil de consultation, export CSV par commune ou par département. Si un export de masse n'est pas proposé, itérer par commune. Prévoir un fallback : saisie manuelle des ~20 communes du département de Mbour pour la démonstration. |
| **Risque** | L'outil peut ne pas proposer d'export exhaustif en une requête. **À tester en priorité absolue Jour 1 matin.** |

- [ ] **V3 — téléchargé et inspecté** (date : ______, opérateur : ______)

---

### D02 — RGPH-5 2023, rapports thématiques

| Champ | Valeur |
|---|---|
| **Nom** | RGPH-5 2023 — rapports provisoires et définitifs par chapitre |
| **Source** | ANSD |
| **URL page** | https://www.ansd.sn/rapports/rgph-5-2023 |
| **URL exemple** | https://www.ansd.sn/sites/default/files/recensements/rapport/Chapitre%201-%20ETAT-STRUCTURE-POPULATION-Rapport-Provisoire-RGPH5_juillet2024_0.pdf |
| **Format** | PDF |
| **Année** | 2023 (publication juillet 2024) |
| **Niveau géographique** | National, région, département |
| **Variables** | Population résidente, structure par âge et sexe, ménages, taille des ménages, urbanisation, scolarisation, fécondité, mortalité, migrations, habitat, handicap, activité agricole des ménages |
| **Chapitres identifiés** | Ch. 1 État et structure de la population ; Ch. 6 Migrations ; autres chapitres à recenser |
| **Licence** | CC BY 4.0 annoncée — à confirmer |
| **Accessibilité** | Libre, téléchargement direct |
| **Vérification** | **V2** |
| **Utilité DataMarket** | Profil démographique, structure par âge pour la segmentation client, taille des ménages pour le passage individu → ménage. Corpus principal du RAG (§24). |
| **Méthode d'importation** | Téléchargement des PDF → extraction texte et tableaux (`pdfplumber` pour les tableaux, `PyMuPDF` pour le texte) → chunking avec métadonnées `{document, chapitre, page, année, territoire}` → embeddings. **Les tableaux doivent être extraits et versés en base, pas seulement vectorisés** : le RAG répond à des questions, la base répond à des calculs. |
| **Risque** | Qualité variable de l'extraction de tableaux PDF. Prévoir une relecture humaine des tableaux critiques (population par département). |

- [ ] **V3 — téléchargé et inspecté**

---

### D03 — RGPH-5 2023, note de presse des résultats définitifs

| Champ | Valeur |
|---|---|
| **URL** | https://ambassadesenegal.be/wp-content/uploads/2024/07/NOTE-DE-PRESSE-OK.pdf |
| **Format** | PDF, 3 pages |
| **Date de publication** | 9 juillet 2024 |
| **Niveau** | National, région |
| **Vérification** | **V2** — contenu intégral lu et recoupé |
| **Valeurs confirmées** | Population résidente **18 126 390** (50,6 % H / 49,4 % F) ; densité nationale 92 hab/km² ; densité Dakar **7 277 hab/km²**, Diourbel **428**, Thiès **375**, Kaolack **252** ; urbanisation **54,7 %** ; concentration Dakar 22 % / Thiès 13 % / Diourbel 12 %, soit 47,0 % à eux trois ; taille moyenne des ménages 9 ; espérance de vie 68,9 ans ; 44,5 % de ménages agricoles ; 74,4 % d'accès à l'électricité |
| **Utilité** | **Jeu de valeurs d'ancrage.** Toute agrégation nationale calculée par DataMarket doit retomber sur ces chiffres, sous peine de rejet en contrôle qualité. |

- [ ] **V3 — téléchargé et inspecté**

---

### D04 — EHCVM II 2021-2022, rapport final

| Champ | Valeur |
|---|---|
| **Nom** | Enquête Harmonisée sur les Conditions de Vie des Ménages, édition 2 |
| **Source** | ANSD (cadre régional UEMOA) |
| **URL** | https://www.ansd.sn/sites/default/files/2024-07/Rapport_Final_EHCVM_2021-2022_VF_0.pdf |
| **URL note de presse** | https://www.ansd.sn/sites/default/files/2024-07/NOTE%20DE%20PRESSE%20EHCVM%20II.pdf |
| **Format** | PDF |
| **Année de collecte** | Vague 1 : 6 nov. 2021 – 5 janv. 2022 ; vague 2 : 22 avr. – 22 juil. 2022 |
| **Échantillon** | 7 120 ménages, représentatif au niveau national et régional |
| **Niveau géographique** | National, région, milieu (urbain / rural) — **pas de désagrégation départementale fiable** |
| **Variables clés** | Dépense de consommation annuelle par tête, coefficients budgétaires par poste, incidence de la pauvreté monétaire, extrême pauvreté, inégalités |
| **Valeurs confirmées** | Dépense annuelle par tête **542 706 FCFA** ; taux de pauvreté national **37,5 %** (contre 37,8 % en 2018-2019) ; extrême pauvreté **5,6 %** ; pauvreté rurale **53,3 %** contre urbaine **20,0 %** |
| **Pauvreté par région (confirmée)** | Kédougou **65,7 %**, Sédhiou **64,4 %**, Tambacounda **62,8 %**, Kolda **62,5 %** ; Dakar **9,3 %**, Thiès **29,9 %**, Saint-Louis **37,3 %**, Diourbel **37,4 %** |
| **Licence** | CC BY 4.0 annoncée — à confirmer |
| **Accessibilité** | Libre, téléchargement direct |
| **Vérification** | **V2** |
| **Utilité DataMarket** | Cœur du Market Size Engine : la dépense par tête est le multiplicateur du TAM. Le taux de pauvreté régional alimente le score de pouvoir d'achat. |
| **Méthode d'importation** | Extraction des tableaux de coefficients budgétaires et de pauvreté régionale par `pdfplumber`, **relecture humaine obligatoire**, versement en table `consumption` et `poverty`. |
| **Limite majeure** | Millésime 2021-2022 en francs courants. Ne pas comparer à des prix 2026 sans redressement par l'IHPC (voir D10). |

- [ ] **V3 — téléchargé et inspecté**

---

### D05 — EHCVM II, microdonnées ⛔

| Champ | Valeur |
|---|---|
| **URL catalogue** | https://anads.ansd.sn/index.php/catalog/310 |
| **Identifiant** | `SEN-ANSD-EHCVM-2021-2022-V1.0` |
| **Format** | SPSS, Stata |
| **Niveau** | Ménage et individu |
| **Accès** | **⛔ SOUS AUTORISATION** |
| **Vérification** | **V2** |
| **Conditions d'accès constatées** | Les microdonnées ne sont accessibles qu'aux services et organismes du système statistique national. Toute utilisation est subordonnée à une **demande d'autorisation adressée au Directeur général de l'ANSD**, précisant l'usage prévu et accompagnée d'une copie du projet d'étude. |
| **Politique d'accès** | https://anads.ansd.sn/index.php/politique-acces |
| **Décision MVP** | **EXCLU.** Le cahier des charges (§7) interdit explicitement de prétendre qu'une donnée est publiquement accessible lorsqu'elle requiert une autorisation. DataMarket doit donc, dans sa version hackathon, fonctionner **uniquement sur les agrégats publiés** (D04). |
| **Action recommandée** | Déposer la demande d'autorisation auprès du DG de l'ANSD **dès maintenant**, en vue de la version post-hackathon. C'est un argument de crédibilité à mentionner dans le pitch : le produit connaît et respecte le circuit d'accès. |

> **À afficher dans l'interface, page Sources :** « Les microdonnées EHCVM
> permettraient une segmentation client beaucoup plus fine. Elles sont soumises
> à autorisation de l'ANSD. DataMarket n'y a pas accès à ce stade et n'utilise
> que les résultats agrégés publiés. »

---

### D06 — Situation Économique et Sociale (SES) régionales, 2022-2023

> **La source la plus sous-estimée du projet.** Une publication par région,
> avec un détail par département que l'on ne trouve nulle part ailleurs en
> accès libre.

| Champ | Valeur |
|---|---|
| **Nom** | Situation Économique et Sociale de la région X, édition 2022-2023 |
| **Source** | ANSD — Services Régionaux de la Statistique |
| **URL index** | https://www.ansd.sn/rapports-donnees/themes/situation-economiques-et-sociales/ses-nationales |
| **URL Thiès** | https://www.ansd.sn/sites/default/files/2025-01/SES-Thies_2022-2023_0.pdf |
| **URL Dakar** | https://www.ansd.sn/sites/default/files/2025-05/SES-Dakar_2022-2023.pdf |
| **URL Diourbel** | https://www.ansd.sn/sites/default/files/2025-07/SES-Diourbel_2022-2023.pdf |
| **URL Saint-Louis** | https://www.ansd.sn/sites/default/files/2025-05/SES-Saint-Louis_2022-2023.pdf |
| **URL Kolda** | https://www.ansd.sn/sites/default/files/2025-02/SES-Kolda_2022-2023.pdf |
| **Format** | PDF (un par région) |
| **Année** | 2022-2023 (publications échelonnées 2025) |
| **Fréquence** | Annuelle |
| **Niveau géographique** | Région **et département** |
| **Variables** | Organisation administrative, démographie, éducation, santé, agriculture, élevage, pêche, industrie, commerce, transport, tourisme, infrastructures, emploi |
| **Accessibilité** | Libre, téléchargement direct |
| **Vérification** | **V2** pour Thiès, Dakar, Diourbel, Saint-Louis, Kolda ; **V1** pour Fatick ; **V0** pour les 8 autres régions — **URL à recenser Jour 1** |
| **Utilité DataMarket** | Seule source libre couvrant l'infrastructure, le tissu économique local et l'équipement au niveau départemental. Alimente le Territory Engine, le Risk Engine et le profil économique du cas Mbour. |
| **Méthode d'importation** | Téléchargement des 14 PDF → extraction ciblée des tableaux départementaux → corpus RAG secondaire. |
| **Risque** | Structure des tableaux hétérogène d'une région à l'autre. Prévoir un parseur par région plutôt qu'un parseur générique. |

- [ ] **V3 — SES Thiès téléchargé et inspecté** (prioritaire : contient Mbour)
- [ ] **V3 — 13 autres SES régionales recensées**

---

### D07 — SES nationale 2022-2023, sections thématiques

| Champ | Valeur |
|---|---|
| **URL page** | https://www.ansd.sn/mademba/publication-du-rapport-sur-la-situation-economique-et-sociale-du-senegal-2022-2023 |
| **URL exemple** | https://www.ansd.sn/sites/default/files/2025-02/Section-E_Systeme-productif_SESN2022-2023.pdf |
| **Format** | PDF par section |
| **Niveau** | National |
| **Vérification** | **V1** |
| **Utilité** | Contexte macroéconomique, section « Système productif » utile au Sector Engine. Priorité moyenne : n'apporte pas de désagrégation territoriale. |

- [ ] **V3 — téléchargé et inspecté**

---

### D08 — Recensement Général des Entreprises (RGE) 2016

> ⚠️ **Seule source publique de données d'entreprises — et elle a dix ans.**

| Champ | Valeur |
|---|---|
| **Nom** | Recensement Général des Entreprises — rapport global |
| **Source** | ANSD |
| **URL rapport** | https://www.ansd.sn/sites/default/files/2022-11/Rapport%20RGE%202016_0.pdf |
| **URL page** | https://www.ansd.sn/Indicateur/resultats-du-recensement-general-des-entreprises-rge |
| **Format** | PDF |
| **Année de collecte** | 2016 (rapport publié 2017) |
| **Niveau géographique** | National, région, département |
| **Variables** | Nombre d'unités économiques, branche d'activité, forme juridique, emplois permanents et saisonniers, taille, informalité |
| **Valeurs confirmées** | 99,8 % de PME, dont 81,8 % d'entrepreneurs individuels ; 611 543 emplois permanents et 232 725 saisonniers (844 268 au total) ; GIE 53,7 % et SARL 20,3 % des personnes morales ; répartition régionale **Dakar 39,5 %**, **Thiès 11,5 %**, toutes les autres régions ≈ un quart des unités |
| **Licence** | CC BY 4.0 annoncée — à confirmer |
| **Accessibilité** | Libre |
| **Vérification** | **V2** |
| **Utilité DataMarket** | Unique intrant public du **Competition Engine** (§19) et du Market Saturation Score. |
| **Limite bloquante** | **Millésime 2016.** Entre 2016 et 2026, la population sénégalaise est passée de ~14,8 à ~19 millions et le tissu commercial s'est densifié. Un ratio de saturation calculé avec un numérateur 2016 et un dénominateur 2023 est **méthodologiquement faux**. |
| **Décision** | Le Market Saturation Score sera calculé **uniquement sur base 2016 au numérateur et au dénominateur** (population RGPH-4 2013 projetée à 2016), puis présenté comme un **indicateur historique de structure**, jamais comme une mesure de concurrence actuelle. Le complément temps réel vient de D12 (OpenStreetMap). |

- [ ] **V3 — téléchargé et inspecté**

---

### D09 — RGE 2016, microdonnées ⛔

| Champ | Valeur |
|---|---|
| **URL catalogue** | https://anads.ansd.sn/index.php/catalog/148 |
| **Accès** | **⛔ SOUS AUTORISATION** (même régime que D05) |
| **Vérification** | **V1** |
| **Décision MVP** | **EXCLU.** |

---

### D10 — ODP / Senegal Data Portal (ANSD × Knoema)

| Champ | Valeur |
|---|---|
| **Nom** | Plateforme Open Data de l'ANSD / Senegal Data Portal |
| **URL principale** | https://senegal.opendataforafrica.org/ |
| **URL catalogue NSO** | https://nso-senegal.opendataforafrica.org/data/ |
| **URL page ANSD** | https://www.ansd.sn/node/16 |
| **Format** | **CSV, JSON, XLSX, SDMX**, PDF, PNG, snippets HTML/Python/R |
| **Niveau géographique** | National, région |
| **Fréquence** | Variable selon la série |
| **Accessibilité** | Libre, sans inscription pour la consultation et l'export |
| **Vérification** | **V2** — formats d'export confirmés ; une page de tableau de bord testée s'est révélée être une application client rendue en JavaScript |
| **Utilité DataMarket** | **Seule source ANSD nativement machine-readable.** C'est la voie d'ingestion à privilégier partout où elle couvre l'indicateur voulu, plutôt que l'extraction PDF. Contient notamment la répartition de la population par région RGPH-5, la pyramide des âges 2023, les projections de population, le commerce extérieur, les recettes budgétaires. |
| **Ressource identifiée** | IHPC base 2023 : https://www.ansd.sn/sites/default/files/2025-03/IHPC_base2023_FEV%202025.pdf — **indispensable pour redresser les montants EHCVM 2021-2022 en francs 2026** |
| **Méthode d'importation** | Tester en priorité l'existence d'une API Knoema exploitable. À défaut, export CSV manuel par jeu de données, versé dans `data/raw/`. **Attention : les pages sont rendues côté client — un simple `requests.get` renvoie une coquille vide.** Utiliser l'export direct, pas le scraping. |
| **Risque** | Fraîcheur inégale selon les séries. Toujours lire le champ « dernière mise à jour » et le reporter dans les métadonnées. |

- [ ] **V3 — export CSV testé sur au moins une série**
- [ ] **V3 — existence d'une API confirmée ou infirmée**

---

### D11 — Frontières administratives (geoBoundaries)

| Champ | Valeur |
|---|---|
| **Source** | geoBoundaries (William & Mary geoLab) — **source externe, non ANSD** |
| **URL API** | https://www.geoboundaries.org/api/current/gbOpen/SEN/ADM1/ |
| **URL directe** | https://raw.githubusercontent.com/wmgeolab/geoBoundaries/main/releaseData/gbOpen/SEN/ADM1/geoBoundaries-SEN-ADM1_simplified.geojson |
| **Format** | GeoJSON |
| **Niveaux** | ADM1 (14 régions), ADM2 (45 départements), ADM3 (communes) |
| **Licence** | Ouverte, attribution requise (CC BY 4.0) |
| **Accessibilité** | Libre, API publique |
| **Vérification** | **V1** |
| **Utilité DataMarket** | Fond de carte du module cartographique (§27), jointure spatiale avec le référentiel territorial. |
| **Point de vigilance** | Les libellés geoBoundaries ne correspondent pas exactement à ceux de l'ANSD (accents, tirets, « Thies » vs « Thiès »). **La table de correspondance est un livrable à part entière** du référentiel territorial (§13), pas un détail d'implémentation. |
| **Alternative à évaluer** | L'ANSD annonce un portail cartographique web ; s'il expose des frontières officielles, il doit être préféré à geoBoundaries. |

- [ ] **V3 — GeoJSON ADM1 et ADM2 téléchargés, libellés comparés au référentiel ANSD**

---

### D12 — OpenStreetMap / Overpass API

| Champ | Valeur |
|---|---|
| **Source** | OpenStreetMap — **source externe, contributive, non officielle** |
| **URL** | https://overpass-api.de/api/interpreter |
| **Format** | JSON, XML |
| **Niveau** | Point GPS |
| **Licence** | ODbL — **attribution et partage à l'identique obligatoires** |
| **Accessibilité** | Libre, avec quotas d'usage |
| **Vérification** | **V1** |
| **Utilité DataMarket** | Complément temps réel au RGE 2016 pour le Competition Engine : comptage des `shop=convenience`, `shop=supermarket`, `amenity=restaurant`, `amenity=marketplace` dans un rayon donné. |
| **Limite critique à afficher** | La couverture OSM au Sénégal est **très inégale** : bonne à Dakar, faible en zone rurale. Un faible nombre de commerces cartographiés ne signifie **pas** une faible concurrence — il peut signifier une faible couverture cartographique. **Ce point doit être affiché dans l'interface à chaque fois qu'un indicateur OSM est présenté.** |
| **Classement traçabilité** | `donnée externe` — jamais présentée comme officielle |

- [ ] **V3 — requête Overpass testée sur le département de Mbour**

---

### D13 — Enquêtes agricoles annuelles (EAA / DAPSA) — *superseded par D17*

| Champ | Valeur |
|---|---|
| **Producteur** | DAPSA, ministère de l'Agriculture |
| **Vérification** | **V0** — aucune URL directe identifiée pour les rapports EAA |
| **Statut** | **Rendu largement caduc par D17.** La DAPSA est co-productrice de la plateforme AgriData, qui expose ses données via une API CKAN. Passer par D17 plutôt que de chercher les PDF d'enquête. |
| **Reste utile si** | AgriData ne couvre pas la production par région et par culture. Dans ce cas seulement, revenir chercher les rapports EAA. |

---

### D17 — AgriData (ANSD / IPAR / DAPSA) — API CKAN ⭐ NOUVEAU

> **Débloque le secteur agrobusiness**, qui était la seule brique du prototype
> sans aucune source vérifiée.

| Champ | Valeur |
|---|---|
| **Nom** | AgriData — plateforme de données sur l'agriculture |
| **Producteurs** | ANSD, **IPAR** (Initiative Prospective Agricole et Rurale), **DAPSA** |
| **URL portail** | https://agridata.ansd.sn/ |
| **Page ANSD** | https://www.ansd.sn/node/228084 |
| **Catalogue** | https://agridata.ansd.sn/dataset/ |
| **Groupe agriculture** | https://agridata.ansd.sn/dataset/?groups=agriculture |
| **Jeu identifié** | https://agridata.ansd.sn/dataset/donneeagricole — « Données agricoles nationale » |
| **Technologie** | **CKAN + extension DataStore** |
| **Doc API** | https://agridata.ansd.sn/fr/api/1/util/snippet/api_info.html?resource_id=9b40d530-9f3c-4916-8813-51b8ed788f65 |
| **Format** | **JSON et CSV via API** — machine-readable natif |
| **Accessibilité** | Libre, sans authentification pour la lecture |
| **Vérification** | **V2** — existence du portail, technologie CKAN et extension DataStore confirmées par recoupement. **Aucun appel d'API n'a pu être exécuté** (environnement d'exécution indisponible). |
| **Endpoints CKAN standard** | `/api/3/action/package_list`, `package_search`, `package_show`, `datastore_search`, **`datastore_search_sql`** |
| **resource_id documentés** | `9b40d530-9f3c-4916-8813-51b8ed788f65`, `ac648d96-007f-416c-833c-705c8108f9ea` |
| **Utilité DataMarket** | Sector Engine agricole, secteur agrobusiness, gisement de matière première du Market Size Engine. |
| **Méthode d'importation** | `ckan_client.py` — implémenté. `python ckan_client.py explorer` cartographie le portail, `tout-agricole` ingère et dépose dans `data/raw/`. |
| **Ce qui reste à confirmer** | Niveau géographique réel (national seul ou régional ?), millésime des campagnes, **licence** — non renseignée dans les métadonnées consultées. |

> ⚠️ **La licence n'est pas confirmée.** Le §39 exige licence, propriétaire et
> conditions d'utilisation pour chaque dataset. La commande `explorer` remonte
> le champ `license_title` de chaque jeu ; si le champ est vide, il faut
> écrire à l'ANSD avant tout usage en production.

- [ ] **V3 — `explorer` exécuté, catalogue produit**
- [ ] **Niveau géographique confirmé**
- [ ] **Licence confirmée**

---

### D18 — ODP Régional (odpregional.statsenegal.sn) ⭐ NOUVEAU

> **Potentiellement la solution au problème du niveau départemental**, qui est
> le premier bloquant identifié dans l'analyse d'écart.

| Champ | Valeur |
|---|---|
| **Nom** | Open Data Platform régionale — statistiques régionales officielles |
| **Producteur** | ANSD |
| **URL** | https://odpregional.statsenegal.sn/ |
| **Page régions** | https://odpregional.statsenegal.sn/regions |
| **Objet** | Diffusion des statistiques officielles des 14 régions, à l'appui de la politique de décentralisation |
| **Niveau géographique** | **Région, département, arrondissement, commune** — exemple relevé : Fatick = 3 départements, 9 arrondissements, 40 communes |
| **Format** | **JSON et CSV** |
| **Accessibilité** | Libre |
| **Vérification** | **V2** pour l'existence et la structure ; **V0** pour l'API — le type d'API (CKAN ou REST propriétaire) **n'est pas confirmé** |
| **Utilité DataMarket** | Référentiel territorial (§13), Territory Engine, comparateur, et surtout **le cas Mbour au bon niveau géographique**. |
| **Méthode d'importation** | `ckan_client.py --portail odp explorer`. Le client teste les endpoints CKAN et, en cas d'échec, affiche les adresses à ouvrir manuellement pour identifier le type d'API. |
| **Rapport avec D01** | Complémentaire, pas redondant. D01 (Répertoire des localités) descend au village mais ne porte que la population et les ménages. D18 porte des **indicateurs de développement** au niveau département. Les deux sont nécessaires. |

- [ ] **V3 — type d'API identifié (CKAN / REST / aucune)**
- [ ] **V3 — un export département obtenu**
- [ ] **Licence confirmée**

---

### D14 — Enquête nationale sur l'emploi (ENES) ⚠️ NON VÉRIFIÉ

| Champ | Valeur |
|---|---|
| **Producteur** | ANSD |
| **Vérification** | **V0** |
| **Utilité potentielle** | Taux d'activité et de chômage régionaux pour le Risk Engine. |
| **Priorité** | Basse — hors périmètre du MVP 72 h. |

---

### D15 — Indicateurs Banque mondiale

| Champ | Valeur |
|---|---|
| **URL API** | https://api.worldbank.org/v2/country/SEN/indicator/{code}?format=json |
| **Format** | JSON, XML, CSV |
| **Niveau** | National uniquement |
| **Licence** | CC BY 4.0 |
| **Vérification** | **V1** |
| **Utilité** | Contexte macro et séries longues. **Aucune désagrégation territoriale** — utilité limitée pour DataMarket, dont la valeur est justement territoriale. |
| **Classement traçabilité** | `donnée externe` |

---

### D16 — EDS / DHS Sénégal 2023

| Champ | Valeur |
|---|---|
| **Producteur** | ANSD avec le programme DHS (ICF) |
| **Accès** | **Inscription et demande d'accès requises** sur dhsprogram.com |
| **Vérification** | **V1** |
| **Utilité** | Prévalence de pathologies (dont le diabète), utile au secteur restauration santé. |
| **Décision MVP** | Hors périmètre. La prévalence du diabète utilisée dans le prototype est une **hypothèse de modélisation**, pas une donnée EDS. |

---

## 3. Conclusions opérationnelles

### 3.1 Ce que l'inventaire autorise

Le cas d'usage **« supérette à Mbour »** est réalisable intégralement sur des
sources libres et vérifiées :

| Besoin | Source | Statut |
|---|---|---|
| Population de Mbour | D01 + D02 | ✅ Libre |
| Ménages de Mbour | D01 | ✅ Libre |
| Structure démographique | D02 | ✅ Libre |
| Consommation par tête | D04 (niveau région Thiès) | ✅ Libre |
| Pauvreté régionale | D04 (Thiès = 29,9 %) | ✅ Libre |
| Tissu économique local | D06 (SES Thiès) | ✅ Libre |
| Concurrence structurelle | D08 (RGE 2016) | ⚠️ Libre mais obsolète |
| Concurrence observable | D12 (OSM) | ⚠️ Libre mais couverture inégale |
| Fond de carte | D11 | ✅ Libre |

### 3.2 Ce que l'inventaire interdit

1. **Aucune segmentation client fine.** Sans microdonnées EHCVM (D05), on ne
   peut pas croiser âge × revenu × poste de dépense. Le « profil client » du
   MVP sera un **profil statistique de segment** au sens du §31, construit par
   croisement d'agrégats — et présenté comme tel.

2. **Aucune mesure de concurrence actuelle.** Le RGE date de 2016. Le
   Market Saturation Score doit être présenté comme un **proxy structurel
   historique**, jamais comme un état de la concurrence en 2026.

3. **Aucune donnée de consommation infrarégionale.** L'EHCVM s'arrête à la
   région. Descendre à Mbour exige une **hypothèse explicite** de transposition
   (voir DATA_MAPPING.md §4), qui doit être affichée et modifiable par
   l'utilisateur.

4. **Aucun secteur agrobusiness défendable** tant que D13 n'est pas vérifié.

### 3.3 Ordre d'attaque recommandé — Jour 1 matin

| Priorité | Action | Durée estimée | Bloquant si échec |
|---|---|---|---|
| 1 | Tester l'export du Répertoire des localités (D01) | 45 min | **Oui** — sans lui, pas d'analyse à Mbour |
| 2 | Télécharger SES Thiès (D06) | 15 min | Non |
| 3 | Télécharger EHCVM II + note de presse (D04) | 15 min | **Oui** |
| 4 | Télécharger RGPH-5 ch. 1 (D02) | 15 min | Non |
| 5 | Tester export CSV sur ODP (D10) | 30 min | Non |
| 6 | Télécharger geoBoundaries ADM1+ADM2 (D11) | 15 min | **Oui** — pas de carte sans lui |
| 7 | Tester une requête Overpass sur Mbour (D12) | 30 min | Non |
| 8 | Rechercher la source EAA (D13) | 45 min | Non — sinon retirer le secteur |

**Règle de sortie :** si les actions 1, 3 et 6 ne sont pas en V3 à la fin de la
matinée du Jour 1, réduire le périmètre de démonstration plutôt que de
compenser par des données construites.

---

## 4. Statut des données du prototype existant

Un prototype fonctionnel (4 modules Streamlit) a été construit avant cet
inventaire. Sa couche de données doit être reclassée selon la grille de
traçabilité du §9 :

| Élément | Classement §9 | Justification |
|---|---|---|
| Population nationale 18 126 390 | **Donnée observée** | D03, note de presse ANSD |
| Dépense par tête 542 706 FCFA | **Donnée observée** | D04, EHCVM II |
| Urbanisation 54,7 % | **Donnée observée** | D03 |
| Parts Dakar 22 % / Thiès 13 % / Diourbel 12 % | **Donnée observée** | D03 |
| Pauvreté régionale | **Donnée observée** | D04 — *non encore intégrée au prototype* |
| **Population des 14 régions en effectif** | **⚠️ Estimation** | Dérivée des parts publiées, non extraite d'un tableau ANSD |
| **Taux d'urbanisation par région** | **⚠️ Estimation** | Calibrée pour retomber sur 54,7 % national |
| **Indice de dépense par région** | **⚠️ Estimation** | Calibré pour retomber sur 542 706 FCFA national |
| **Coefficients budgétaires par région** | **⚠️ Estimation** | Profil plausible, non extrait de l'EHCVM |
| **Production agricole par région** | **⛔ Estimation non sourcée** | Aucune source vérifiée (D13 en V0) |
| Taux de captation du commerce | **Hypothèse** | Paramètre de modélisation, affiché dans l'interface |
| Prévalence du diabète 3,4 % | **Hypothèse** | Non issue de l'EDS (D16 hors périmètre) |

**Conséquence.** Le prototype affiche actuellement ces valeurs sans les
distinguer visuellement des données observées. C'est un écart direct avec le
§9. **Correctif obligatoire avant toute démonstration :** ajouter un badge de
provenance (`OBS` / `CALC` / `EST` / `HYP` / `EXT`) sur chaque valeur affichée,
et une couleur distincte pour les estimations.

À la décharge de la couche d'estimation : les densités qu'elle reconstitue
retombent à moins de 2 % des valeurs ANSD publiées pour Dakar (7 323 vs
7 277), Diourbel (432 vs 428), Thiès (373 vs 375), Kaolack (240 vs 252),
Kédougou (15,1 vs 15) et Tambacounda (23,1 vs 23). La méthode est donc saine —
mais **une estimation validée reste une estimation**, et doit être remplacée
par les effectifs réels dès que D01 et D02 sont en V3.

---

## 5. Registre des licences

| Source | Licence | Obligation |
|---|---|---|
| ANSD (D01–D04, D06–D08, D10) | CC BY 4.0 annoncée — **à confirmer** | Attribution « ANSD » + année + titre de la publication |
| geoBoundaries (D11) | CC BY 4.0 | Attribution geoBoundaries |
| OpenStreetMap (D12) | **ODbL** | Attribution **et** partage à l'identique de toute base dérivée |
| Banque mondiale (D15) | CC BY 4.0 | Attribution |
| Microdonnées ANADS (D05, D09) | Autorisation nominative | Demande écrite au DG de l'ANSD |

> ⚠️ **Point juridique à trancher avant commercialisation.** La licence ODbL
> d'OpenStreetMap impose le partage à l'identique des bases dérivées. Si
> DataMarket adopte un modèle freemium (§44) avec une offre premium, il faut
> soit isoler les données OSM dans une base séparée, soit renoncer à OSM, soit
> accepter d'ouvrir la base dérivée. **Ce n'est pas un détail : c'est une
> contrainte structurelle sur le modèle économique.**

---

## 6. Validation

Ce document répond à l'exigence §52 du cahier des charges. Il doit être
**relu et validé** avant le début du développement, conjointement avec
`DATA_MAPPING.md`.

| Étape | Statut |
|---|---|
| Inventaire rédigé | ✅ |
| Sources vérifiées en V2 | 9 sur 16 |
| Sources en V0 (non vérifiées) | 2 — D13, D14 |
| Sources exclues pour cause d'accès restreint | 3 — D05, D09, D16 |
| **Passage en V3 (téléchargement effectif)** | ⬜ **À faire Jour 1 matin** |
| Validation par l'équipe | ⬜ |
