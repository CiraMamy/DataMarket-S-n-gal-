# Liste des données à télécharger

**DataMarket Sénégal** — liste de courses priorisée
Version 1.0 — 4 août 2026

---

## Règles générales

**Format.** Quand le choix existe, prendre dans cet ordre :
`CSV` > `XLSX` > `JSON` > `PDF`. Un tableau en CSV s'intègre en minutes ;
le même tableau en PDF demande une extraction et une relecture.

**Nommage.** Préfixer par la source et l'année :
`ANSD_RGPH5_2023_population_departements.csv`

**Où déposer.** Dans le dossier `DataMarket Sénégal` connecté, pas dans le
chat — les pièces jointes de la conversation ne me parviennent pas.

**Si un site propose « Exporter »**, toujours l'utiliser plutôt que de
copier-coller un tableau affiché à l'écran.

---

# PRIORITÉ 0 — bloque la démonstration

## P0-1 · Répertoire des localités RGPH-5 2023 ⭐ le plus important

> Sans ce fichier, « supérette à Mbour » reste une approximation. Avec lui,
> Mbour devient une analyse réelle. C'est le seul jeu de données ANSD en accès
> libre qui descend sous le niveau régional.

| | |
|---|---|
| **Page** | https://www.ansd.sn/mademba/repertoire-des-localites-issu-du-rgph-5-2023 |
| **Outil de consultation** | https://www.ansd.sn/node/15936 |
| **Format** | CSV ou JSON (l'outil propose un export) |

**Ce qu'il me faut, par ordre de préférence :**

1. **L'export national complet** — toutes les localités du Sénégal
2. À défaut : **un export par région** (14 fichiers)
3. Au minimum pour la démo : **le département de Mbour en entier** — toutes
   les communes, tous les villages

**Colonnes attendues** (vérifier qu'elles sont bien dans l'export) :

```
nom_localite · type (village/quartier) · commune · arrondissement
departement · region · population · nombre_menages · nombre_concessions
```

**Ce que ça débloque :** référentiel territorial (§13), cas Mbour réel,
comparateur de territoires, carte au niveau commune, et le passage de
« population estimée » à « population observée » sur toute la plateforme.

**Point de vigilance :** si l'outil ne permet qu'une recherche localité par
localité sans export de masse, dites-le-moi — on basculera sur une extraction
manuelle des seules communes du département de Mbour, ce qui suffit à la
démonstration.

---

## P0-2 · RGPH-5 2023 — population par département

| | |
|---|---|
| **Page** | https://www.ansd.sn/rapports/rgph-5-2023 |
| **Chapitre 1 (PDF)** | https://www.ansd.sn/sites/default/files/recensements/rapport/Chapitre%201-%20ETAT-STRUCTURE-POPULATION-Rapport-Provisoire-RGPH5_juillet2024_0.pdf |

**Ce qu'il me faut :**

- Le tableau **population résidente par région** (14 lignes) — pour remplacer
  mes estimations par les effectifs réels
- Le tableau **population par département** (45 lignes)
- Le tableau **structure par âge et sexe par région** — pour la segmentation
  client
- Le tableau **taille moyenne des ménages par région**
- Le tableau **taux d'urbanisation par région**

**Cherchez d'abord un fichier de tableaux en Excel.** L'ANSD publie parfois
les tableaux du recensement séparément du rapport rédigé. Si vous en trouvez
un, il vaut mieux que le PDF.

**Prenez aussi les autres chapitres** s'ils sont disponibles (ménages, habitat,
activité économique) — ils alimenteront le RAG.

---

## P0-3 · EHCVM II 2021-2022 — tableaux régionaux

| | |
|---|---|
| **Rapport final** | https://www.ansd.sn/sites/default/files/2024-07/Rapport_Final_EHCVM_2021-2022_VF_0.pdf |
| **Note de presse** | https://www.ansd.sn/sites/default/files/2024-07/NOTE%20DE%20PRESSE%20EHCVM%20II.pdf |

Vous me l'aviez déjà envoyé, mais je n'ai pas pu le lire.

**Les trois tableaux dont j'ai besoin, très précisément :**

1. **Dépense de consommation annuelle par tête, par région** — 14 valeurs en
   FCFA. Je n'ai que la valeur nationale (542 706 FCFA) et je reconstruis
   actuellement les 14 régions par un indice inventé. C'est la correction la
   plus importante à faire sur le modèle.

2. **Coefficients budgétaires par région** — la part du budget consacrée à
   chaque poste : alimentation, logement/énergie, transport, santé, éducation,
   habillement, communication, équipement du ménage, autres. C'est ce qui
   détermine directement le TAM.

3. **Incidence de la pauvreté par région** — j'ai 9 régions sur 14 par
   recoupement (Kédougou 65,7 % / Sédhiou 64,4 % / Tambacounda 62,8 % /
   Kolda 62,5 % / Diourbel 37,4 % / Saint-Louis 37,3 % / Thiès 29,9 % /
   Dakar 9,3 %, national 37,5 %). **Il me manque Louga, Fatick, Matam,
   Kaffrine et Ziguinchor.**

**Bonus très utile :** s'il existe un tableau de la dépense par **milieu**
(urbain / rural) croisé avec la région, il permettrait de transposer
correctement vers le département de Mbour au lieu de supposer.

---

# PRIORITÉ 1 — forte valeur

## P1-1 · SES régionales 2022-2023

> La seule source libre qui descend au **département** sur l'économie et les
> infrastructures.

**URL que j'ai déjà identifiées :**

| Région | URL |
|---|---|
| Thiès ⭐ | https://www.ansd.sn/sites/default/files/2025-01/SES-Thies_2022-2023_0.pdf |
| Dakar | https://www.ansd.sn/sites/default/files/2025-05/SES-Dakar_2022-2023.pdf |
| Diourbel | https://www.ansd.sn/sites/default/files/2025-07/SES-Diourbel_2022-2023.pdf |
| Saint-Louis | https://www.ansd.sn/sites/default/files/2025-05/SES-Saint-Louis_2022-2023.pdf |
| Kolda | https://www.ansd.sn/sites/default/files/2025-02/SES-Kolda_2022-2023.pdf |

**Page d'index à explorer pour les 9 autres :**
https://www.ansd.sn/rapports-donnees/themes/situation-economiques-et-sociales/ses-nationales

Manquent : Fatick, Louga, Kaolack, Kaffrine, Tambacounda, Matam, Ziguinchor,
Sédhiou, Kédougou.

**Si vous ne devez en prendre qu'une : Thiès** — c'est celle qui contient le
département de Mbour, donc celle de la démonstration.

---

## P1-2 · RGE 2016 — recensement des entreprises

| | |
|---|---|
| **Rapport global** | https://www.ansd.sn/sites/default/files/2022-11/Rapport%20RGE%202016_0.pdf |
| **Page** | https://www.ansd.sn/Indicateur/resultats-du-recensement-general-des-entreprises-rge |

**Ce qu'il me faut :**

- Nombre d'unités économiques **par région et par département**
- Répartition **par branche d'activité**, en isolant le **commerce de détail**
- Répartition formel / informel

**Vérifiez surtout s'il existe un RGE plus récent.** Le RGE 2016 a dix ans,
c'est la faiblesse la plus sérieuse de la plateforme. Un recensement des
entreprises postérieur à 2020, même partiel, changerait complètement la
qualité du moteur de concurrence. Cherchez aussi du côté de :

- L'**annuaire statistique** de l'ANSD (section entreprises)
- La **BDEF** (Banque de Données Économiques et Financières) :
  https://www.ansd.sn/Indicateur/banque-de-donnees-economiques-et-financieres-bdef
- Les statistiques d'entreprises :
  https://www.ansd.sn/Indicateur/autres-rapports-denquetes-sur-les-statistiques-dentreprise

---

## P1-3 · IHPC base 2023 — indice des prix

| | |
|---|---|
| **PDF identifié** | https://www.ansd.sn/sites/default/files/2025-03/IHPC_base2023_FEV%202025.pdf |

Les montants EHCVM sont en francs 2021-2022. Sans redressement, tout TAM
calculé pour 2026 est sous-évalué. Il me faut la **série de l'indice général**
de 2021 à aujourd'hui, et si possible l'indice du poste **alimentation**.

**Cherchez la version la plus récente** — celle-ci date de février 2025, il
doit y avoir des publications mensuelles depuis.

---

## P1-4 · Prévalence du diabète au Sénégal

Vous avez déjà envoyé des fichiers `RELAY_WHS` qui ressemblent à des exports
du Global Health Observatory de l'OMS. **Vérifiez s'ils contiennent la
prévalence du diabète pour le Sénégal** — si oui, c'est réglé.

Sinon, sources à essayer :

- OMS Global Health Observatory : https://www.who.int/data/gho
- Enquête **STEPS** Sénégal (OMS + ministère de la Santé) — la meilleure
  source pour les maladies non transmissibles
- **EDS-Continue** Sénégal, si un module NCD existe

**Ce que ça débloque :** aujourd'hui le secteur « restauration santé » repose
sur une prévalence de 3,4 % que **j'ai posée moi-même**, sans source. C'est le
type de chiffre que le §50 du cahier des charges interdit.

---

# PRIORITÉ 2 — utile mais non bloquant

## P2-1 · Production agricole

**Statut : je n'ai identifié aucune source vérifiée.** C'est pour cela que le
secteur agrobusiness est actuellement suspendu.

Pistes à explorer :

- **DAPSA** (Direction de l'Analyse, de la Prévision et des Statistiques
  Agricoles), ministère de l'Agriculture — chercher « Enquête Agricole
  Annuelle » ou « EAA »
- Section agriculture des **SES régionales** (P1-1) — elles contiennent des
  tableaux de production
- **FAOSTAT** : https://www.fao.org/faostat/ — production par culture, mais
  au niveau national uniquement

**Ce qu'il me faut :** production en tonnes **par région et par culture**
(arachide, mil/sorgho, riz, maïs, horticulture), campagne la plus récente.

**Si vous ne trouvez rien de récent et de régional, dites-le-moi** — on
remplacera l'agrobusiness par un secteur mieux documenté plutôt que de le
maintenir avec des chiffres construits.

---

## P2-2 · Frontières administratives

| | |
|---|---|
| **geoBoundaries ADM2 (départements)** | https://www.geoboundaries.org/api/current/gbOpen/SEN/ADM2/ |
| **geoBoundaries ADM3 (communes)** | https://www.geoboundaries.org/api/current/gbOpen/SEN/ADM3/ |

Il me faut le **GeoJSON des 45 départements** et si possible celui des
communes, pour la carte au bon niveau.

**Vérifiez d'abord si l'ANSD publie ses propres frontières** — l'agence
annonce un portail cartographique. Des frontières officielles ANSD seraient
préférables à geoBoundaries, dont les libellés ne correspondent pas exactement
(« Thies » vs « Thiès »).

---

## P2-3 · Plateforme Open Data ANSD (exports directs)

| | |
|---|---|
| **Portail** | https://senegal.opendataforafrica.org/ |
| **Catalogue** | https://nso-senegal.opendataforafrica.org/data/ |

C'est la **seule source ANSD nativement exploitable par machine** — export
CSV, JSON, XLSX, SDMX. Chaque fois qu'un indicateur y est disponible, il vaut
mieux le prendre là qu'extraire un PDF.

**Jeux de données repérés :**

- Répartition de la population par région (RGPH-5 2023)
- Pyramide des âges 2023
- Répartition de la population par région et par sexe
- Population du Sénégal — données de projection

**Ce qui m'aiderait le plus :** explorez le catalogue et dites-moi ce que vous
y trouvez sur la **consommation**, l'**emploi** et les **entreprises**. Si ces
thèmes y sont, on évite beaucoup d'extraction PDF.

**Question à trancher :** y a-t-il une **API** exploitable ? Le portail tourne
sur Knoema, qui en propose habituellement une. Si oui, l'ingestion devient
automatique et réactualisable — ce qui change la nature du produit.

---

## P2-4 · Enquête emploi et démographie

- **ENES** — enquête nationale sur l'emploi : taux d'activité et de chômage
  par région, pour le moteur de risque
- **EDS Sénégal 2023** : https://dhsprogram.com — attention, **inscription et
  demande d'accès requises**, donc à traiter comme source sous condition

---

# Récapitulatif

| Priorité | Item | Débloque | Effort |
|---|---|---|---|
| **P0-1** | Répertoire des localités | Référentiel territorial, cas Mbour | 30 min |
| **P0-2** | RGPH-5 tableaux départements | Population observée | 20 min |
| **P0-3** | EHCVM II tableaux régionaux | TAM réel | 20 min |
| P1-1 | SES Thiès (+ 13 autres) | Contexte économique local | 15 min – 1 h |
| P1-2 | RGE 2016 (+ chercher plus récent) | Moteur de concurrence | 30 min |
| P1-3 | IHPC base 2023 | Redressement inflation | 10 min |
| P1-4 | Prévalence diabète | Secteur restauration santé | 20 min |
| P2-1 | Production agricole | Secteur agrobusiness | 45 min |
| P2-2 | Frontières ADM2/ADM3 | Carte départementale | 15 min |
| P2-3 | Exploration ODP | Ingestion automatisable | 45 min |

**Si vous n'avez que deux heures :** faites P0-1, P0-2, P0-3 et P1-1 (Thiès).
Ces quatre-là transforment la plateforme d'un modèle d'estimations en un outil
adossé à des données observées.

---

# Ce que je ne vous demande pas, et pourquoi

**Les microdonnées ANADS** (EHCVM, RGE, EDS au niveau ménage). Elles
donneraient une segmentation client infiniment plus fine, mais leur accès est
soumis à **autorisation écrite du Directeur général de l'ANSD**, avec
description de l'usage et copie du projet d'étude.

Ne les téléchargez pas par un autre canal. En revanche, **déposer la demande
officielle dès maintenant** serait un excellent point de pitch : cela montre
au jury que le produit connaît le circuit d'accès aux données et le respecte,
au lieu de le contourner.

Page de la politique d'accès :
https://anads.ansd.sn/index.php/politique-acces
