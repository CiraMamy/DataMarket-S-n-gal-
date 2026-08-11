# DataMarket Sénégal — image de production
#
# Construction :  docker build -t datamarket-senegal .
# Lancement    :  docker run -p 8501:8501 datamarket-senegal
#
# Avec la clé API Claude (module 3) :
#   docker run -p 8501:8501 -e ANTHROPIC_API_KEY=sk-ant-... datamarket-senegal
#
# Avec vos propres données ANSD (montage du dossier data/) :
#   docker run -p 8501:8501 -v "$(pwd)/data:/app/data" datamarket-senegal

FROM python:3.11-slim

LABEL org.opencontainers.image.title="DataMarket Sénégal"
LABEL org.opencontainers.image.description="Plateforme d'intelligence économique \
fondée sur les données publiques de l'ANSD"
LABEL org.opencontainers.image.source="https://github.com/VOTRE-COMPTE/datamarket-senegal"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

# Dépendances système minimales.
# curl sert au HEALTHCHECK ; le reste des paquets Python est en roues
# précompilées, aucun compilateur n'est nécessaire.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Couche de dépendances séparée : le cache Docker n'est invalidé que si
# requirements.txt change, pas à chaque modification du code.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code applicatif
COPY *.py ./
COPY ref_*.csv ./

# Arborescence de travail. data/raw accueille vos exports ANSD :
# le pipeline les détecte automatiquement au démarrage.
RUN mkdir -p data/raw data/geo exports .streamlit

COPY .streamlit/ ./.streamlit/

# Exécution sans privilèges
RUN useradd --create-home --shell /bin/bash datamarket \
    && chown -R datamarket:datamarket /app
USER datamarket

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -fsS http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=8501", \
            "--server.address=0.0.0.0", \
            "--server.headless=true"]
