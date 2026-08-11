# Déploiement — DataMarket Sénégal

Version 1.0 — 10 août 2026

---

## État de validation

Tout ce qui suit a été **exécuté**, pas seulement écrit :

| Vérification | Résultat |
|---|---|
| Suite de tests | **134 passés, 0 échec** |
| Démarrage de l'application | HTTP 200 |
| Point de santé `/_stcore/health` | `ok` |
| Exceptions au rendu (Streamlit AppTest) | **0** |
| Erreurs au rendu | **0** |
| Génération du rapport PDF | ✅ 10,7 Ko |
| Pipeline de données | ✅ 14 régions, complétude 100 % |
| Moteur conversationnel | ✅ 5 formulations testées |
| Versions des dépendances | Épinglées sur celles testées |

**Un bug a été trouvé et corrigé** au passage : une phrase vide renvoyait zéro
région au lieu du périmètre national. Il n'aurait pas été détecté sans cette
exécution.

**Une dépréciation a été corrigée** : 16 appels `use_container_width` migrés
vers `width='stretch'`. La date de retrait annoncée par Streamlit
(31 décembre 2025) est déjà dépassée — le code aurait cassé à la prochaine
montée de version.

---

## Ce que je ne peux pas faire à votre place

Je n'ai **pas** déployé la plateforme sur une URL publique, et je ne peux pas :

- aucun identifiant de votre part (GitHub, Streamlit Cloud, fournisseur cloud) ;
- le réseau de mon environnement d'exécution est restreint par liste blanche —
  il bloque aussi bien les fournisseurs cloud que `agridata.ansd.sn` ;
- un déploiement engage votre nom et vos coûts : c'est une décision qui vous
  revient.

Ce que j'ai fait : rendre le déploiement mécanique. Les commandes ci-dessous
sont à copier telles quelles.

---

## Option A — Streamlit Community Cloud

**Recommandée pour le hackathon.** Gratuit, HTTPS automatique, redéploiement à
chaque `git push`. Compter dix minutes.

### 1. Publier sur GitHub

```bash
cd /chemin/vers/datamarket-senegal

git init
git add .
git commit -m "DataMarket Sénégal — MVP, 134 tests"

git remote add origin https://github.com/VOTRE-COMPTE/datamarket-senegal.git
git branch -M main
git push -u origin main
```

> `.gitignore` exclut déjà `.streamlit/secrets.toml`. **Vérifiez avant de
> pousser** que votre clé API n'apparaît pas :
> `git log -p | grep -i "sk-ant"` doit ne rien retourner.

### 2. Déployer

1. Aller sur **share.streamlit.io**, se connecter avec GitHub
2. **New app** → sélectionner le dépôt, branche `main`, fichier `app.py`
3. **Advanced settings** → Python 3.11
4. **Secrets** → coller :

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

5. **Deploy**

L'URL obtenue est de la forme
`https://votre-compte-datamarket-senegal.streamlit.app`.

### Limites à connaître

| Point | Détail |
|---|---|
| Mémoire | 1 Go — suffisant ici, le jeu de données est petit |
| Mise en veille | L'app s'endort après inactivité, réveil en ~30 s |
| Stockage | **Éphémère** : les PDF générés disparaissent au redémarrage. Sans effet, l'utilisateur les télécharge immédiatement. |
| Données | `data/raw/` doit être versionné dans Git pour être présent en ligne |

---

## Option B — Docker

Correspond au §43 du cahier des charges. Portable, reproductible.

```bash
docker build -t datamarket-senegal .

docker run -d -p 8501:8501 \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -v "$(pwd)/data:/app/data" \
  --name datamarket \
  datamarket-senegal
```

Vérification :

```bash
curl http://localhost:8501/_stcore/health     # doit renvoyer : ok
docker logs datamarket
docker ps                                     # colonne STATUS : healthy
```

Le montage `-v` rend `data/` persistant : vos exports ANSD déposés dans
`data/raw/` survivent aux redémarrages du conteneur et sont détectés
automatiquement par le pipeline.

> **Le Dockerfile n'a pas pu être construit ici** — Docker n'est pas
> disponible dans mon environnement. Il suit les pratiques usuelles (couche de
> dépendances séparée, utilisateur non privilégié, healthcheck) mais la
> première construction est à faire chez vous. Comptez deux à trois minutes.

### docker-compose

Attendu au §51. Créez `docker-compose.yml` :

```yaml
services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./data:/app/data
      - ./exports:/app/exports
    restart: unless-stopped
```

Puis `echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env` et `docker compose up -d`.

---

## Option C — VPS avec nom de domaine

Pour une démonstration sur votre propre domaine.

```bash
# Sur le serveur
sudo apt update && sudo apt install -y docker.io docker-compose-plugin nginx certbot python3-certbot-nginx

git clone https://github.com/VOTRE-COMPTE/datamarket-senegal.git
cd datamarket-senegal
echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env
docker compose up -d
```

Reverse proxy — `/etc/nginx/sites-available/datamarket` :

```nginx
server {
    listen 80;
    server_name datamarket.votredomaine.sn;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/datamarket /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d datamarket.votredomaine.sn
```

> Les directives `Upgrade` et `Connection` sont **indispensables** : Streamlit
> communique par WebSocket. Sans elles la page s'affiche puis reste figée sur
> « Connecting… ».

---

## Vérification locale avant tout déploiement

```bash
pip install -r requirements.txt
pytest -q test_datamarket.py        # attendu : 134 passed
streamlit run app.py                # http://localhost:8501
```

Parcours de recette, deux minutes :

1. La page d'accueil affiche la carte et le classement des 14 régions
2. Cliquer « Je veux ouvrir une supérette à Mbour »
3. Cliquer « Analyser » → TAM, SAM, SOM s'affichent
4. Onglet **Carte du potentiel** → carte et graphiques
5. Onglet **Export PDF** → « Générer » puis « Télécharger »
6. Onglet **Données sources** → les trois blocs ANSD

---

## Sécurité — à contrôler avant publication

| Point | État |
|---|---|
| `secrets.toml` exclu de Git | ✅ dans `.gitignore` |
| Clé API absente du code | ✅ lue via `st.secrets` ou variable d'environnement |
| Conteneur non privilégié | ✅ utilisateur `datamarket` |
| Détails d'erreur masqués | ✅ `showErrorDetails = false` |
| Protection XSRF | ✅ activée |
| **Historique Git propre** | ⬜ **à vérifier** : `git log -p \| grep -i "sk-ant"` |

> Si une clé a déjà été poussée, la révoquer immédiatement sur
> console.anthropic.com. Retirer le fichier ne suffit pas : il reste dans
> l'historique.

---

## À afficher honnêtement le jour de la démonstration

La plateforme fonctionne, mais tourne encore sur une **couche d'estimations**.
Le §9 de votre cahier des charges impose de le dire.

| Élément | Statut |
|---|---|
| Population nationale, dépense par tête, urbanisation | **Données observées** ANSD |
| Ventilation régionale des effectifs | **Estimation** dérivée des parts publiées |
| Coefficients budgétaires régionaux | **Estimation** |
| Production agricole | **Non sourcée** — secteur à suspendre ou à alimenter via AgriData |
| Taux de captation, prévalence du diabète | **Hypothèses** de modélisation |

Les badges de provenance `OBS` / `CALC` / `EST` / `HYP` sont spécifiés dans
`DATA_MAPPING.md` mais **ne sont pas encore implémentés dans l'interface**.
C'est le premier correctif à apporter : c'est aussi ce qui différencie
DataMarket d'un générateur de chiffres (§46).

---

## Après le déploiement

Par ordre de valeur :

1. **Charger le Répertoire des localités** → Mbour devient réel, la démo cesse
   de reposer sur un coefficient de 38 % codé en dur
2. **Implémenter les badges de provenance** → la promesse de traçabilité
   devient visible
3. **Brancher AgriData** via `ckan_client.py` → remplace les estimations
   régionales par des données observées, et débloque l'agrobusiness
4. **Comparateur de territoires** (§30, §40.9) → peu coûteux une fois le
   référentiel en place
5. **Page Sources** (§40.10)
