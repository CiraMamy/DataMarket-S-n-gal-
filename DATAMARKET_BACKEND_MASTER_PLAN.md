# DataMarket Backend Master Plan

## 0) Audit du repository existant

### État constaté

Le dépôt est actuellement un MVP Streamlit fonctionnel de DataMarket Sénégal, construit autour d'un moteur Python déterministe qui calcule TAM / SAM / SOM, parse des fiches ANSD, normalise les 14 régions, gère les villes et les territoires, et génère des PDF / cartes.

Ce qui est déjà solide :
- pipeline de données avec normalisation et surcharge par fichiers utilisateurs ;
- référentiel territorial chargé sur 14 régions ;
- moteur économique calculatoire avec preuves de provenance ;
- analyse NL locale / API Claude ;
- génération de rapports PDF ;
- tests de validation couvrant les données, cartographie, logique métier, PDF et robustesse.

Vérification faite au moment de l’audit :
- `pytest -q` : 161 tests passés, 0 échec ;
- application Streamlit fonctionnelle ;
- données de référence présentes (population, dépenses, production) ;
- fichiers de documentation métier existants : `README.md`, `DATA_INVENTORY.md`, `DATA_MAPPING.md`, `DEPLOIEMENT.md` ;
- absence des documents demandés par l’architecture cible (`AUDIT.md`, `ARCHITECTURE.md`, `ARCHITECTURE_DECISION.md`, `DATABASE.md`, `API.md`, `MIGRATION.md`, `SECURITY.md`, `DATA_PROVENANCE.md`, `DEPLOYMENT.md`) dans le dépôt.

### Ce qui doit être conservé

Le moteur existant est un point d’entrée utile pour le backend production-grade, car il contient déjà :
- les agrégats de référence du Sénégal ;
- les règles sectorielles ;
- la logique de calcul market sizing ;
- la gestion de la provenance dans les résultats ;
- le modèle de territorialisation ;
- le pattern de tests de vérification de la cohérence.

Le backend ne doit pas remplacer ce moteur ; il doit l’extraire proprement dans un domaine métier plus robuste.

### Ce qui doit être modernisé / séparé

- l’interface Streamlit reste un front d’usage, pas la source de vérité ;
- le calcul d’étude doit devenir un service applicatif versionné ;
- la provenance et les hypothèses doivent être stockées comme des objets de domaine, et non seulement dans des dictionnaires Python ;
- la source des données doit être traitée comme une entité de registre avec licence, version, checksum, statut et freshness ;
- la qualité de données doit passer d’un contrôle manuel dans les tests à un moteur explicite ;
- le territoire doit devenir un système de référence multi-niveaux (région, département, commune, localité) avec version administrative ;
- le backend doit exposer des endpoints versionnés et des preuves d’évidence plutôt qu’un unique résultat chiffré.

### Données actuellement présentes et utilisables

- `ref_population.csv` : population régionale calibrée sur RGPH-5 ;
- `ref_depenses.csv` : données de dépenses et coefficients budgétaires ;
- `ref_production.csv` : production agricole régionale ;
- `data/raw/` : zone d’import utilisateur ;
- `geo.py` : logique de frontières GeoJSON / fallback par cercles ;
- `territory.py` : résolution de ville / département / région.

### Dépendances actives

- Python 3.11 ;
- Streamlit ;
- Plotly ;
- Pandas / NumPy ;
- Folium / branca ;
- ReportLab ;
- requests ;
- anthropic (optionnel).

### Risques et incohérences architecturales

- absence de base de données persistante ;
- absence de schéma de données versionné ;
- absence d’API backend propre ;
- absence d’authentification / RBAC / multi-tenancy ;
- absence de gestion de licences, provenance et qualité au niveau du dataset ;
- absence de représentation explicite des versions de source / dataset / observation / calcul ;
- absence d’entity model structuré pour claims, evidence, conflict, scenario, decision passport ;
- absence de séparation nette entre `API`, `application`, `domain`, `infrastructure` ;
- absence d’ingestion structurée et de connecteurs dédiés.

Conclusion d’audit : le dépôt est un excellent MVP de démonstration, mais pas encore un backend production-grade de DataMarket.

---

## 1) Architecture cible proposée

### 1.1 Objectif

Construire une infrastructure de données économiques et territoriales, centrée sur la traceabilité complète d’une donnée jusqu’à sa conclusion.

### 1.2 Architecture logique

Couche 1 — Raw Data
- données brutes immuables ;
- fichiers ou API sources ;
- checksum et métadonnées brutes.

Couche 2 — Staged Data
- parsing et profilage ;
- détection de schéma ;
- validation structurelle initiale.

Couche 3 — Normalized Data
- colonnes normalisées ;
- libellés standardisés ;
- unités normalisées ;
- référentiel territorial harmonisé.

Couche 4 — Semantic Data
- définitions d’indicateurs ;
- dimensions et unités ;
- ontologie économique ;
- classifications et mappings.

Couche 5 — Analytical Data
- observations prêtes à l’analyse ;
- séries, agrégats, calculs déterministes ;
- données optimisées pour requêtes et comparaisons.

Couche 6 — Evidence Fabric
- relations source → dataset → version → observation → transformation → calcul → estimate → claim → report ;
- lineage graph dans PostgreSQL / graph abstraction.

Couche 7 — Decision Data
- scenario, evidence passport, market study, report final.

### 1.3 Pilier architectural

Le cœur de DataMarket est le `DMEF` : DataMarket Evidence Fabric.

Le DMEF représente les relations :
- source
- dataset
- dataset_version
- observation
- transformation
- calculation
- assumption
- estimate
- scenario
- claim
- evidence
- analysis
- report
- decision

Une conclusion sans chaîne de provenance n’est pas acceptable.

---

## 2) Stack de base recommandée

### 2.1 Technologies retenues

Backend :
- Python 3.11
- FastAPI
- Pydantic v2
- SQLAlchemy 2 / Alembic
- PostgreSQL + PostGIS
- Redis
- Object Storage S3-compatible
- Parquet + Apache Arrow
- DataFusion (ou équivalent) pour requêtes analytiques ciblées
- Celery / Dramatiq pour jobs d’ingestion
- OpenTelemetry pour observabilité

Frontend :
- Next.js + TypeScript seulement si une interface utilisateur est ajoutée ;
- pour cette phase backend, le moteur fonctionne sans front lourd.

### 2.2 Justification

- PostgreSQL + PostGIS répond aux besoins géospatiaux et transactionnels ;
- S3/Parquet répond aux besoins de données analytiques lourdes ;
- Redis donne du cache et des files de jobs ;
- FastAPI est adapté à des API versionnées et documentées ;
- DataFusion est utile sans introduire un sur-architcturing au départ ;
- Kafka/Redpanda n’est pas nécessaire tant que le besoin n’est pas réel.

Ne pas introduire Kafka, Neo4j, Spark, Kubernetes, vector DB au démarrage.

---

## 3) Modèle de données principal

### 3.1 Entités minimales

- organizations
- users
- memberships
- sources
- source_versions
- datasets
- dataset_versions
- dataset_files
- indicators
- indicator_versions
- indicator_definitions
- units
- dimensions
- dimension_values
- territories
- territory_versions
- territory_geometries
- territory_relationships
- territory_aliases
- observations
- observation_versions
- transformations
- transformation_runs
- quality_checks
- quality_results
- provenance_events
- lineage_nodes
- lineage_edges
- calculations
- calculation_inputs
- calculation_outputs
- assumptions
- estimates
- scenarios
- market_studies
- market_query_plans
- claims
- evidence
- conflicts
- reports
- report_versions
- ai_runs
- ai_evidence
- audit_logs

### 3.2 Entité Observation

Conceptuellement :
- id
- indicator_id
- dataset_version_id
- territory_id
- period
- period_type
- value_numeric
- value_text
- unit_id
- dimensions
- status
- quality_score
- missing_reason
- suppression_reason
- methodology_reference
- source_reference
- created_at

Important : l’observation est immutable ; toute correction passe par une nouvelle version.

### 3.3 Entité Source et Dataset

Chaque source et dataset doit avoir :
- id / slug
- provider / owner
- domain / country
- access_url / source_url / api_url
- format / license / access_level
- frequency / temporal_coverage / geographic_coverage
- schema / variables / dimensions / measures
- quality_profile / provenance_policy / ingestion_strategy / update_strategy
- status / checksum / version / last_checked_at / last_successful_ingestion

### 3.4 Entité Territory

- territory_id
- territory_type (region, department, commune, locality)
- canonical_name
- valid_from / valid_to
- administrative_version
- parent_id
- geom / geometry

Le territoire ne doit pas être une simple chaîne de caractères. Il doit être versionné et relié à son historique administratif.

---

## 4) Dataset Registry et catalogue initial

### 4.1 Rôle

Le dataset registry doit centraliser les fiches de métadonnées et organiser l’ingestion et la publication.

### 4.2 Priorité source

Priorité 1 et prioritaire pour la phase initiale :
- ANSD / ODP / ANADS / BADIS / RGPH / EHCVM / ENES / EERH / comptes nationaux / comptes régionaux / prix / agriculture / emploi / santé / éducation / énergie / telecom / tourisme / transport / environnement / culture / justice / cadre de vie / dette / finances publiques.

Priorité 2 :
- ARTP, BCEAO, BRVM, ministères et agences publiques ouvrant des données publiques et vérifiables.

Priorité 3 :
- World Bank, IMF, FAO, WHO, ILO, UNESCO, ITU, UN Comtrade, UNCTAD, IRENA.

Priorité 4 :
- OSM, WorldPop, données climatiques et géospatiales.

### 4.3 Source de vérité de la phase 1

Commencer par les jeux de données réellement accessibles / vérifiables du Sénégal, sans inventer de données ou contourner les autorisations.

### 4.4 Règles de catalogue

Chaque dataset doit posséder :
- fournisseur
- statut (DISCOVERED, VALIDATED, ACTIVE, STALE, DEPRECATED, BLOCKED, LICENSE_REQUIRED, PARTNERSHIP_REQUIRED, REJECTED)
- fréquence / date de dernière mise à jour
- public / licensed / restricted / internal / sensitive
- licence + obligations de redistribution / attribution
- qualité et metadata completeness
- checksum et version

Le système ne doit pas marquer un dataset ACTIVE si l’accès ou la validation n’ont pas été vérifiés.

---

## 5) Data provenance et Evidence Fabric

### 5.1 Objectif

Chaque donnée doit pouvoir remonter jusqu’à :
- sa source originelle ;
- le connecteur qui l’a récupérée ;
- la version du dataset ;
- le fichier brut ;
- le checksum ;
- la transformation appliquée ;
- la validation effectuée ;
- le calcul qui l’a utilisés ;
- les analyses / conclusions qui s’y appuient.

### 5.2 Éléments du graph

- Source
- Dataset
- DatasetVersion
- Observation
- Transformation
- Calculation
- Assumption
- Estimate
- Scenario
- Claim
- Evidence
- Analysis
- Report

### 5.3 Standards conceptuels

Compatibilité W3C PROV / OpenLineage, sans imposer un moteur graph spécialisé au démarrage.

Le graph peut être représenté d’abord dans PostgreSQL avec `nodes` et `edges`, puis abstrait pour permettre un éventuel moteur plus spécialisé ensuite.

---

## 6) Quality engine

### 6.1 Contrôles obligatoires

Validation structurelle
- colonnes
- types
- encodage
- duplication
- nulls
- format

Validation statistique
- valeurs négatives interdites là où le sens le demande
- bornes
- outliers
- incohérences de séries et de totaux

Validation sémantique
- unité
- définition
- population concernée
- territoire
- période

Validation relationnelle
- cohérence agrégats / sous-totaux / composés

Validation temporelle
- fréquence publiée
- trous de données
- doublons de période
- changement de définition

### 6.2 Score de qualité

Le `quality_score` doit être explicable, et non une note opaque. Il est produit par dimensions explicites :
- structural_quality
- statistical_quality
- semantic_quality
- temporal_quality
- geographic_quality
- metadata_coverage

---

## 7) Comparability kernel et conflict engine

### 7.1 Comparabilité

Deux observations ne sont comparables que si elles partagent :
- indicator definition
- unit
- population
- territory
- territory_version
- period
- methodology
- frequency
- sampling
- classification
- source
- revision status

Le moteur doit retourner :
- COMPARABLE
- CONDITIONALLY_COMPARABLE
- NOT_COMPARABLE
- INSUFFICIENT_METADATA

### 7.2 Conflict engine

Quand deux sources divergent :
- ne pas faire une moyenne automatique ;
- créer une ligne dans `conflicts` avec source A / source B / différence / analyse de résolution / statut ;
- exposer l’écart et les raisons de non-comparabilité.

Statuts : `UNRESOLVED`, `EXPLAINED`, `RECONCILED`, `NOT_COMPARABLE`.

---

## 8) Evidence Distance

Le système utilise un niveau d’evidence analytique :
- D0 : observation directe
- D1 : donnée nettoyée / harmonisée
- D2 : calcul déterministe
- D3 : estimation
- D4 : scénario / hypothèse

Cela n’indique pas une vérité absolue ; indique la distance analytique entre un résultat et la donnée source.

Tous les résultats importants doivent exposer leur `evidence_distance`.

---

## 9) Hypothesis engine et scenario engine

### 9.1 Assumptions

Les hypothèses ne sont pas des données officielles.

Structure :
- name
- description
- value
- unit
- origin
- user_defined
- system_defined
- source
- confidence
- created_at
- created_by

Types : `SOURCE_DERIVED`, `USER_DEFINED`, `MODEL_ASSUMPTION`, `SCENARIO_ASSUMPTION`

### 9.2 Scenarios

- BASE
- CONSERVATIVE
- OPTIMISTIC
- CUSTOM

Chaque scénario expose :
- inputs
- assumptions
- formula
- result
- evidence_distance

### 9.3 Régles importantes

- L’IA ne crée jamais une statistique ;
- l’IA ne transforme pas une hypothèse en fait ;
- l’IA ne transforme pas une estimation en statistique officielle ;
- l’IA garde les contradictions et affiche les limites.

---

## 10) Market Intelligence Engine

Le moteur déterministe doit être le cœur de la production numérique.

Fonctions initiales :
- market sizing
- TAM
- SAM
- SOM
- penetration
- growth rate / CAGR
- territorial comparison
- population segmentation
- customer segmentation
- density analysis
- location analysis
- sector analysis
- business demography
- price analysis
- income analysis
- employment analysis
- trend analysis
- scenario analysis

Toute formule de calcul doit stocker :
- formula
- inputs
- input_sources
- assumptions
- result
- unit
- timestamp
- engine_version

Le moteur existant de DataMarket Sénégal est un bon point d’entrée ; il doit être transformé en domaine métier versionné.

---

## 11) Question Compiler et MarketQueryPlan

### 11.1 Question Compiler

Le compiler transforme une question humaine en plan analytique structuré.

Exemple :
- question : “Je veux ouvrir un restaurant adapté aux personnes diabétiques à Dakar.”
- plan : market + target_population + territory + time_period + required_dimensions + required_indicators + available_data + missing_data + analysis_plan

### 11.2 MarketQueryPlan

Champs minimaux :
- question originale
- intention
- secteur
- produit / service
- territoire
- population cible
- période
- dimensions nécessaires
- indicateurs nécessaires
- datasets nécessaires
- filtres
- transformations
- calculs
- hypothèses
- données manquantes
- niveau de confiance
- contraintes
- engine_version

Le plan doit être reproductible et versionné.

---

## 12) Territory engine et géospatial

### 12.1 Territorial model

- regions
- departments
- arrondissements
- communes
- localities

Données sur :
- nom
- code administratif
- période de validité
- version administrative
- hiérarchie parent/enfant
- géométrie

### 12.2 Rôle de `territory.py`

Le moteur existant est précieux pour la résolution de ville → région et ambigüité locale. Il doit devenir un Territory Resolver formalisé avec :
- alias / synonyms
- confidence scoring
- territory_version
- canonical_territory_id
- territory_type

### 12.3 Géodonnées

- PostGIS pour géométries et relations administratives
- sources privilégiées : ANSD, OpenStreetMap, geoBoundaries, WorldPop, rasters climatiques conformément aux licences

---

## 13) Connecteurs et ingestion

### 13.1 Pattern

Chaque connecteur respecte :
- discover()
- fetch()
- validate_access()
- download()
- parse()
- extract_metadata()
- get_schema()
- get_version()
- get_license()
- get_update_time()

### 13.2 Connecteurs prioritaires

- ANSDConnector
- ANADSConnector
- ANSDODPConnector
- WorldBankConnector
- FAOConnector
- WHOConnector
- ILOSTATConnector
- ITUConnector
- ComtradeConnector
- OSMConnector
- WorldPopConnector

### 13.3 Pipeline d’ingestion

DISCOVER
↓
FETCH
↓
RAW STORE
↓
CHECKSUM
↓
PROFILE
↓
PARSE
↓
NORMALIZE
↓
VALIDATE
↓
MAP
↓
SEMANTIC HARMONIZATION
↓
PROVENANCE
↓
VERSION
↓
PUBLISH

Tout échec sur une étape bloque la publication du dataset.

---

## 14) API backend

### 14.1 Endpoints minimaux

- `/api/v1/datasets`
- `/api/v1/datasets/{id}`
- `/api/v1/datasets/{id}/versions`
- `/api/v1/indicators`
- `/api/v1/indicators/{id}`
- `/api/v1/observations`
- `/api/v1/observations/query`
- `/api/v1/territories`
- `/api/v1/territories/{id}`
- `/api/v1/markets`
- `/api/v1/markets/query`
- `/api/v1/analyses`
- `/api/v1/analyses/{id}`
- `/api/v1/evidence`
- `/api/v1/claims`
- `/api/v1/conflicts`
- `/api/v1/sources`
- `/api/v1/provenance`
- `/api/v1/lineage`
- `/api/v1/reports`
- `/api/v1/search`
- `/api/v1/ai`

### 14.2 API contract

- versionnée ;
- OpenAPI documentée ;
- filtres stricts sur indicators / territories / périodes ;
- retour de provenance et d’evidence sur les résultats reportés ;
- endpoint `reproducibility` pour remonter version des datasets, calculs, hypothèses et hashes ;
- aucun résultat sans provenance explicite.

---

## 15) Sécurité, multi-tenancy et gouvernance

### 15.1 Risques à corriger dès la première phase

- RBAC avec roles OWNER / ADMIN / ANALYST / MEMBER / VIEWER
- isolation par organization_id
- API keys hashées
- rate limiting IP / user / organization / API key
- sécurisation des uploads
- validation MIME / extension / archive bomb / path traversal / sandbox
- logging d’audit complet
- security headers / secure cookies / CORS contrôlé
- OWASP ASVS baseline

### 15.2 Licence governance

Avant publication :
- vérifier la licence ;
- bloquer la publication si la licence ne permet pas l’usage ;
- stocker `license_obligations` et obligations d’attribution ;
- ne pas exposer les données sensibles ou restreintes.

### 15.3 PII / privacy

- classification PUBLIC / INTERNAL / CONFIDENTIAL / PERSONAL / SENSITIVE ;
- détection de noms, emails, adresses, numéros, identifiants ;
- données microdonnées non exposées par défaut ;
- accès restreint selon niveau et organisation.

---

## 16) Tests requis

Le dépôt actuel a des tests métier utiles. La phase backend doit ajouter des tests de niveau plus haut :

- unit tests
- integration tests
- database tests
- API tests
- connector tests
- data quality tests
- security tests
- regression tests
- end-to-end tests
- property-based tests

Tests prioritaires :
- vérité d’une donnée source ;
- market sizing ;
- conflict detection ;
- comparability refusal ;
- provenance chain ;
- versioning ;
- multi-tenancy ;
- licence restrictions ;
- insufficient evidence AI response.

---

## 17) Roadmap implementation

### Phase 0 — Audit et plan
- documenter l’état du dépôt ;
- définir la cible backend et les garanties ;
- valider les sources ouvertes ;
- poser le master plan.

### Phase 1 — Database foundation
- créer le schéma principal ;
- migrations Alembic ;
- bases de données dev / test / prod.

### Phase 2 — Dataset Registry + Source Registry
- types d’entry ;
- gestion de statut ;
- enregistrement de métadonnées ;
- checksum et versioning.

### Phase 3 — Provenance + Versioning
- dataset versions ;
- observation versions ;
- calculation versions ;
- lineage graph ;
- audit logs.

### Phase 4 — Ingestion engine + connectors ANSD
- connecteurs ANSD, ODP, BADIS ;
- validation et publication.

### Phase 5 — Territory engine
- référentiel territorial ;
- résolution de ville / département / région ;
- relations hiérarchiques.

### Phase 6 — Quality + semantic layer
- definitions
- units
- dimension mapping
- quality score rationale

### Phase 7 — Comparability + conflicts
- comparability kernel
- conflict detection
- claims / evidence

### Phase 8 — Market intelligence + evidence graph
- TAM / SAM / SOM ;
- étude de marché ;
- decision evidence passport

### Phase 9 — API + admin console
- endpoints versionnés ;
- documentation OpenAPI ;
- liste des datasets / versions / quality / freshness.

### Phase 10 — AI layer + governance
- question compiler
- evidence-based response contract
- refus de l’insuffisance de preuve

### Phase 11 — Security, performance, deployment
- RBAC, headers, uploads, rate limiting
- health checks, metrics, logs
- deployment containerisé / infra as code

---

## 18) Priorités concrètes pour commencer

### Priorité 1 : ce qu’il faut construire avant toute autre fonction
1. Database foundation
2. Dataset Registry
3. Source Registry
4. Provenance
5. Versioning
6. Quality engine
7. ANSD connector
8. ANSD ODP connector
9. BADIS importer
10. Territory system
11. Observation engine
12. Comparability kernel
13. Conflict engine
14. Market calculation engine
15. Evidence graph
16. Claim ledger
17. Decision Evidence Passport
18. API
19. AI layer

### Priorité 2 : ne pas faire pour le moment
- Kafka
- Neo4j
- Spark
- vector DB non justifié
- nombre excessif d’index
- chargement de toutes les sources sans vérifier licence et accès

---

## 19) Règle de conception finale

Le backend DataMarket ne doit pas être une “IA qui connaît le Sénégal”. Il doit être une infrastructure qui répond à la question :

- Quelle est la donnée ?
- Quelle est sa source ?
- Quelle est sa version ?
- Comment a-t-elle été transformée ?
- Quel calcul l’a utilisée ?
- Quelles hypothèses ont été faites ?
- Quelles contradictions existent ?
- Que ne savons-nous pas ?
- Quel est le niveau d’évidence ?

Cette règle doit guider chaque décision d’architecture et chaque sprint de développement.

---

## 20) Conclusion de l’audit et du plan

Le dépôt actuel est un bon MVP démonstrateur, fondé sur des données publiques, des règles métier cohérentes et des tests robustes. Il n’est pas encore un backend DataMarket complet.

La bonne stratégie est de conserver ce moteur opérationnel comme base de domaine, puis de le faire évoluer progressivement vers :
- un registre de datasets fiable ;
- un moteur de provenance ;
- un système de versionnement ;
- un pipeline d’ingestion sécurisé ;
- un backend API multi-tenant ;
- un système d’évidence explicite ;
- un audio-analytique déterministe, non halluciné.

La prochaine étape de développement doit commencer par le schéma de donnée, les migrations, le registry, la provenance, puis l’API. Le code métier existant doit être réutilisé à bon escient, sans être écrasé par une migration technologique purement esthétique.
